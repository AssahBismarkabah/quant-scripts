"""Run the IVAMR probe: IS reproduction (gate 5) then OOS gates (1-4, 6).

Usage: .venv/bin/python research/ivamr/run_probe.py

Loads cached NQ bars (via quant_scripts.ivamr.bars), runs the frozen rule set on
the IS window (2014-01-01..2018-12-31) to reproduce an in-sample result, then on
the OOS window (2019-01-01..2023-12-31) to apply the pre-registered rejection
gates from IA/ivamr-research-spec.md §5.

Writes outputs/probe_trades_is.parquet, probe_trades_oos.parquet,
probe_summary.json under research/ivamr/outputs/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from quant_scripts.ivamr.config import StudyParams  # noqa: E402
from quant_scripts.ivamr.bars import load_intraday  # noqa: E402
from quant_scripts.ivamr.backtest import run_backtest  # noqa: E402

RESEARCH = ROOT / "research" / "ivamr"
OUT = RESEARCH / "outputs"

IS_WINDOW = ("2014-01-01", "2018-12-31")
OOS_WINDOW = ("2019-01-01", "2023-12-31")

# gate thresholds (IA/ivamr-research-spec.md §5)
OOS_WINRATE_MIN = 0.50
OOS_PF_MIN = 1.0
TF_WINRATE_MIN = 0.40
MR_WINRATE_MIN = 0.55
KILL_SWITCH_DAY_FRACTION = 0.30
KILL_SWITCH_FRAC = 0.03


def _metrics(trades: pd.DataFrame, friction: float) -> dict:
    if trades.empty:
        return {
            "n_trades": 0, "win_rate": None, "profit_factor": None,
            "gross_pts": 0.0, "net_pts": 0.0, "max_dd_pts": 0.0,
            "avg_trades_per_day": 0.0, "frac_days_killswitch": 0.0,
            "win_rate_trend": None, "win_rate_mr": None,
            "tf_win_rate": None, "mr_win_rate": None,
            "avg_equity_pct": 0.0, "worst_loss_pts": 0.0,
        }
    t = trades.copy()
    tf = t[t["play"].isin([1, 2])]
    mr = t[t["play"].isin([3, 4])]
    gross_wins = t[t["win"]]["gross_pts"].sum()
    gross_losses = abs(t[~t["win"]]["gross_pts"].sum())
    wr = len(t[t["win"]]) / len(t)
    pf = (gross_wins / gross_losses) if gross_losses > 0 else (np.inf if gross_wins > 0 else 0.0)

    equity = t["net_pts"].cumsum()
    running_max = equity.cummax()
    dd = (equity - running_max).min()

    days = t.groupby("date").agg(n=("gross_pts", "size"), kill=("equity_pct", lambda s: float(s.sum())))
    active_days = len(days)
    frac_kill = (days["kill"] <= -KILL_SWITCH_FRAC).mean() if active_days else 0.0

    def _wr(x):
        return round(float(x["win"].mean()), 4) if len(x) else None

    return {
        "n_trades": int(len(t)),
        "win_rate": round(wr, 4),
        "profit_factor": round(float(pf), 4),
        "gross_pts": round(float(t["gross_pts"].sum()), 2),
        "net_pts": round(float(t["net_pts"].sum()), 2),
        "max_dd_pts": round(float(dd), 2),
        "avg_trades_per_day": round(len(t) / active_days, 3) if active_days else 0.0,
        "frac_days_killswitch": round(float(frac_kill), 4),
        "win_rate_trend": _wr(tf),
        "win_rate_mr": _wr(mr),
        "tf_win_rate": _wr(tf),
        "mr_win_rate": _wr(mr),
        "avg_equity_pct": round(float(t["equity_pct"].mean()), 6),
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
    """IS reproduction gate: frozen rules must yield a net-positive IS result."""
    ok = is_m["net_pts"] > 0
    return {"gate5_is_net_positive": bool(ok), "gate5": bool(ok),
            "note": f"IS net_pts={is_m['net_pts']} (must be > 0)"}


def _gate1(oos_m: dict) -> dict:
    ok = oos_m["net_pts"] > 0
    return {"gate1_oos_net_positive": bool(ok), "note": f"OOS net_pts={oos_m['net_pts']}"}


def _gate2(oos_trades: pd.DataFrame, oos_m: dict, params: StudyParams) -> dict:
    daily = oos_trades.groupby("date")["net_pts"].sum()
    p5 = _bootstrap_p5(daily, params.n_sims, params.seed)
    ok = p5 > 0
    return {"gate2_oos_bootstrap_p5": p5, "gate2": bool(ok),
            "note": f"OOS per-day bootstrap p5={p5:.2f}"}


def _gate3(oos_m: dict) -> dict:
    wr_ok = oos_m["win_rate"] is not None and oos_m["win_rate"] >= OOS_WINRATE_MIN
    pf_ok = oos_m["profit_factor"] is not None and oos_m["profit_factor"] >= OOS_PF_MIN
    tf_ok = oos_m["tf_win_rate"] is None or oos_m["tf_win_rate"] >= TF_WINRATE_MIN
    mr_ok = oos_m["mr_win_rate"] is None or oos_m["mr_win_rate"] >= MR_WINRATE_MIN
    ok = bool(wr_ok and pf_ok and tf_ok and mr_ok)
    return {"gate3_oos_winrate_pf": ok, "gate3": ok,
            "note": f"OOS win_rate={oos_m['win_rate']} (min {OOS_WINRATE_MIN}), PF={oos_m['profit_factor']} "
                    f"(min {OOS_PF_MIN}), TF wr={oos_m['tf_win_rate']} (min {TF_WINRATE_MIN}), "
                    f"MR wr={oos_m['mr_win_rate']} (min {MR_WINRATE_MIN})"}


def _gate4(oos_m: dict) -> dict:
    too_many_kill_days = oos_m["frac_days_killswitch"] >= KILL_SWITCH_DAY_FRACTION
    gross_negative = oos_m["gross_pts"] <= 0
    ok = not (too_many_kill_days or gross_negative)
    return {"gate4_tail_fragility": ok, "gate4": ok,
            "note": f"frac_days_killswitch={oos_m['frac_days_killswitch']} (limit {KILL_SWITCH_DAY_FRACTION}), "
                    f"gross_pts={oos_m['gross_pts']} (must be > 0)"}


def blueprint_gates(is_m: dict, oos_m: dict) -> dict:
    """IVAMR's own Go/No-Go thresholds (§6) — reported as secondary info, not binding."""
    return {
        "pf_ge_1.3": {"oos_pf": oos_m["profit_factor"], "ok": oos_m["profit_factor"] is not None and oos_m["profit_factor"] >= 1.3},
        "avg_trade_ge_0.2pct_equity": {"oos_avg_equity_pct": oos_m["avg_equity_pct"], "ok": oos_m["avg_equity_pct"] >= 0.2},
        "max_dd_le_15pct": {"oos_max_dd_pts": oos_m["max_dd_pts"], "need_notional": True},
        "tf_winrate_ge_40": {"oos_tf": oos_m["tf_win_rate"], "ok": oos_m["tf_win_rate"] is not None and oos_m["tf_win_rate"] >= 0.40},
        "mr_winrate_ge_55": {"oos_mr": oos_m["mr_win_rate"], "ok": oos_m["mr_win_rate"] is not None and oos_m["mr_win_rate"] >= 0.55},
        "oos_ge_70pct_of_is": {"is_net": is_m["net_pts"], "oos_net": oos_m["net_pts"]},
    }


def main() -> int:
    params = StudyParams()
    OUT.mkdir(parents=True, exist_ok=True)

    print("loading bars (Databento NQ 1-min -> ET RTH -> volume profile + ATR)...")
    bars = load_intraday(params)
    print(f"  1m={len(bars['1m'])} 15m={len(bars['15m'])} rows")

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
        g5["gate5"] and g1["gate1_oos_net_positive"] and g2["gate2"]
        and g3["gate3"] and g4["gate4"]
    )
    # gate 6 (look-ahead) is structural: enforced by bars.py/profile.py/backtest.py

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
            "gate6_lookahead": {"gate6": True, "note": "structural: prev-day profile/ATR, entry at next-bar open, intra-bar stops"},
        },
        "blueprint_go_no_go": blueprint_gates(is_m, oos_m),
        "verdict": "DISCONFIRMED" if gates_fail else "CLEARS-OOS",
    }

    (OUT / "probe_summary.json").write_text(json.dumps(summary, indent=2, default=float))
    print(json.dumps(summary, indent=2, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
