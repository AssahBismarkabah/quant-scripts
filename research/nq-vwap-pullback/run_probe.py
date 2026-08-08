"""Run the NQ VWAP-pullback probe: IS reproduction (gate 5) then OOS gates (1-4,6).

Usage: .venv/bin/python research/nq-vwap-pullback/run_probe.py

Loads cached bars (via quant_scripts.nq_vwap_pullback.bars), runs the frozen
strategy on the IS window (2020-08-01..2024-12-31) to check reproduction of the
claimed ~64% win rate / net-positive, then on the OOS window (2025-01-01..
2026-08-07) to apply the pre-registered rejection gates.

Writes outputs/probe_trades_is.parquet, probe_trades_oos.parquet and
probe_summary.json under research/nq-vwap-pullback/outputs/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from quant_scripts.nq_vwap_pullback.config import StudyParams  # noqa: E402
from quant_scripts.nq_vwap_pullback.bars import load_intraday  # noqa: E402
from quant_scripts.nq_vwap_pullback.backtest import run_backtest  # noqa: E402

RESEARCH = ROOT / "research" / "nq-vwap-pullback"
OUT = RESEARCH / "outputs"

IS_WINDOW = ("2020-08-01", "2024-12-31")
OOS_WINDOW = ("2025-01-01", "2026-08-07")

# gate thresholds (from IA/nq-vwap-pullback-research-spec.md §5)
OOS_WINRATE_MIN = 0.55
OOS_PF_MIN = 1.0
TWO_LOSS_CAP_FRACTION = 0.30  # gate 4: fraction of active days hitting the 2-loss cap
FOUR_TRADE_REACH_FRACTION = 0.30  # gate 4: fraction of active days reaching 4 trades


def _metrics(trades: pd.DataFrame, friction: float) -> dict:
    if trades.empty:
        return {
            "n_trades": 0, "win_rate": None, "avg_win": 0.0, "avg_loss": 0.0,
            "profit_factor": None, "gross_pts": 0.0, "net_pts": 0.0,
            "max_dd_pts": 0.0, "avg_trades_per_day": 0.0,
            "frac_days_2loss": 0.0, "frac_days_4trades": 0.0, "worst_loss_pts": 0.0,
        }
    t = trades.copy()
    wins = t[t["win"]]
    losses = t[~t["win"]]
    gross_wins = wins["gross_pts"].sum()
    gross_losses = abs(losses["gross_pts"].sum())
    wr = len(wins) / len(t)
    pf = (gross_wins / gross_losses) if gross_losses > 0 else (np.inf if gross_wins > 0 else 0.0)

    # cumulative net equity for max drawdown
    equity = t["net_pts"].cumsum()
    running_max = equity.cummax()
    dd = (equity - running_max).min()

    days = t.groupby("date").agg(n=("gross_pts", "size"), losses=("win", lambda s: int((~s).sum())))
    active_days = len(days)
    frac_2loss = (days["losses"] >= 2).mean() if active_days else 0.0
    frac_4 = (days["n"] >= 4).mean() if active_days else 0.0

    return {
        "n_trades": int(len(t)),
        "win_rate": round(wr, 4),
        "avg_win": round(float(wins["gross_pts"].mean()), 2) if len(wins) else 0.0,
        "avg_loss": round(float(losses["gross_pts"].mean()), 2) if len(losses) else 0.0,
        "profit_factor": round(float(pf), 4),
        "gross_pts": round(float(t["gross_pts"].sum()), 2),
        "net_pts": round(float(t["net_pts"].sum()), 2),
        "max_dd_pts": round(float(dd), 2),
        "avg_trades_per_day": round(len(t) / active_days, 3) if active_days else 0.0,
        "frac_days_2loss": round(float(frac_2loss), 4),
        "frac_days_4trades": round(float(frac_4), 4),
        "worst_loss_pts": round(float(t["gross_pts"].min()), 2),
    }


def _bootstrap_p5(daily_net: pd.Series, n_sims: int, seed: int) -> float:
    x = daily_net.to_numpy(dtype=float)
    if x.size == 0:
        return 0.0
    rng = np.random.default_rng(seed)
    means = np.array([rng.choice(x, size=x.size, replace=True).mean() for _ in range(n_sims)])
    return float(np.percentile(means, 5))


def _gate5(is_m: dict) -> dict:
    """IS reproduction gate: claimed ~64% win rate & net-positive should reproduce."""
    wr = is_m["win_rate"]
    ok_wr = wr is not None and wr >= 0.58  # tolerant: 64% claim, allow reasonable slack
    ok_net = is_m["net_pts"] > 0
    ok = bool(ok_wr and ok_net)
    return {
        "gate5_is_winrate_reproduced": bool(ok_wr),
        "gate5_is_net_positive": bool(ok_net),
        "gate5": ok,
        "note": f"IS win_rate={wr}, net_pts={is_m['net_pts']} (expect ~0.64 and >0)",
    }


def _gate1(oos_m: dict) -> dict:
    ok = oos_m["net_pts"] > 0
    return {"gate1_oos_net_positive": ok, "note": f"OOS net_pts={oos_m['net_pts']}"}


def _gate2(oos_trades: pd.DataFrame, oos_m: dict, params: StudyParams) -> dict:
    daily = oos_trades.groupby("date")["net_pts"].sum()
    p5 = _bootstrap_p5(daily, params.n_sims, params.seed)
    ok = p5 > 0
    return {"gate2_oos_bootstrap_p5": p5, "gate2": ok,
            "note": f"OOS per-day bootstrap p5={p5:.2f}"}


def _gate3(oos_m: dict) -> dict:
    wr_ok = oos_m["win_rate"] is not None and oos_m["win_rate"] >= OOS_WINRATE_MIN
    pf_ok = oos_m["profit_factor"] is not None and oos_m["profit_factor"] >= OOS_PF_MIN
    ok = bool(wr_ok and pf_ok)
    return {"gate3_oos_winrate": oos_m["win_rate"], "gate3_oos_pf": oos_m["profit_factor"],
            "gate3": ok,
            "note": f"OOS win_rate={oos_m['win_rate']} (min {OOS_WINRATE_MIN}), PF={oos_m['profit_factor']} (min {OOS_PF_MIN})"}


def _gate4(oos_m: dict) -> dict:
    """Tail fragility: if a large fraction of active days hit the 2-loss cap or fail
    to reach 4 trades, the negative-RR win-rate engine can't sustain its pass math."""
    fragile_loss = oos_m["frac_days_2loss"] >= TWO_LOSS_CAP_FRACTION
    low_reach = oos_m["frac_days_4trades"] < FOUR_TRADE_REACH_FRACTION
    ok = not (fragile_loss or low_reach)
    return {
        "gate4": bool(ok),
        "note": f"frac_days_2loss={oos_m['frac_days_2loss']} (limit {TWO_LOSS_CAP_FRACTION}), "
                f"frac_days_4trades={oos_m['frac_days_4trades']} (need >= {FOUR_TRADE_REACH_FRACTION})",
    }


def main() -> int:
    params = StudyParams()
    OUT.mkdir(parents=True, exist_ok=True)

    print("loading bars (Databento NQ 1-min -> ET RTH -> VWAP -> 5m/15m)...")
    bars = load_intraday(params)
    print(f"  1m={len(bars['1m'])} 5m={len(bars['5m'])} 15m={len(bars['15m'])} rows")

    is_trades = run_backtest(bars, params, IS_WINDOW)
    oos_trades = run_backtest(bars, params, OOS_WINDOW)
    is_trades.to_parquet(OUT / "probe_trades_is.parquet")
    oos_trades.to_parquet(OUT / "probe_trades_oos.parquet")

    is_m = _metrics(is_trades, params.friction_base_pts)
    oos_m = _metrics(oos_trades, params.friction_base_pts)

    g5 = _gate5(is_m)
    g1 = _gate1(oos_m)
    g2 = _gate2(oos_trades, oos_m, params)
    g3 = _gate3(oos_m)
    g4 = _gate4(oos_m)

    gates_fail = not (
        g1["gate1_oos_net_positive"]
        and g2["gate2"]
        and g3["gate3"]
        and g4["gate4"]
        and g5["gate5"]
    )
    # gate 6 (look-ahead) is structural and enforced by construction in bars.py/backtest.py

    summary = {
        "instrument": params.symbol,
        "is_window": list(IS_WINDOW),
        "oos_window": list(OOS_WINDOW),
        "friction_base_pts": params.friction_base_pts,
        "is": is_m,
        "oos": oos_m,
        "gates": {
            "gate1_oos_net_positive": g1,
            "gate2_oos_bootstrap_p5": g2,
            "gate3_oos_winrate_pf": g3,
            "gate4_tail_fragility": g4,
            "gate5_is_reproduction": g5,
            "gate6_lookahead": {"gate6": True, "note": "structural: VWAP anchored on 1m base, entry at next-bar open, no future leak"},
        },
        "verdict": "DISCONFIRMED" if gates_fail else "CLEARS-OOS",
    }

    (OUT / "probe_summary.json").write_text(json.dumps(summary, indent=2, default=float))
    print(json.dumps(summary, indent=2, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
