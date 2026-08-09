"""Run the opening-range / gap trio probe: IS reproduction then OOS gates, per strategy.

Usage: .venv/bin/python research/opening-range-gap/run_probe.py

Loads the combined owned NQ 1-min caches (via quant_scripts.opening_range_gap.bars)
and runs each of the trio --- ORB, Gap Fill, Oops --- on the IS window
(2014-01-01..2018-12-31) to check reproduction (gate 5), then the OOS window
(2019-01-01..2026-08-07) to apply the pre-registered rejection gates (1-4,6).

Each strategy is falsified independently (spec §8): DISCONFIRMED if any of its
gates fail. Gap Fill additionally reports the raw 65-70% gap-fill-rate stat.

Writes outputs/{orb,gap_fill,oops}_trades_is.parquet, _oos.parquet, and
outputs/probe_summary.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from quant_scripts.opening_range_gap.config import StudyParams  # noqa: E402
from quant_scripts.opening_range_gap.bars import load_intraday  # noqa: E402
from quant_scripts.opening_range_gap.backtest import (  # noqa: E402
    run_orb, run_gap_fill, run_oops, gap_fill_rate,
)

RESEARCH = ROOT / "research" / "opening-range-gap"
OUT = RESEARCH / "outputs"

IS_WINDOW = ("2014-01-01", "2018-12-31")
OOS_WINDOW = ("2019-01-01", "2026-08-07")

# pre-registered gate thresholds (spec §8), per strategy
THRESH = {
    "orb":      {"oos_winrate": 0.40, "oos_pf": 1.0, "fill_rate": None},
    "gap_fill": {"oos_winrate": 0.40, "oos_pf": 1.0, "fill_rate": 0.60},
    "oops":     {"oos_winrate": 0.50, "oos_pf": 1.0, "fill_rate": None},
}
KILL_DAY_FRACTION = 0.30      # gate 4: fraction of active days losing >=3% equity cap
KILL_FRAC = 0.03


def _metrics(trades: pd.DataFrame, friction: float) -> dict:
    if trades.empty:
        return {
            "n_trades": 0, "win_rate": None, "profit_factor": None,
            "gross_pts": 0.0, "net_pts": 0.0, "max_dd_pts": 0.0,
            "avg_trades_per_day": 0.0, "frac_days_killswitch": 0.0,
            "avg_equity_pct": 0.0, "worst_loss_pts": 0.0,
        }
    t = trades.copy()
    gross_wins = t[t["win"]]["gross_pts"].sum()
    gross_losses = abs(t[~t["win"]]["gross_pts"].sum())
    wr = len(t[t["win"]]) / len(t)
    pf = (gross_wins / gross_losses) if gross_losses > 0 else (np.inf if gross_wins > 0 else 0.0)

    equity = t["net_pts"].cumsum()
    dd = (equity - equity.cummax()).min()

    days = t.groupby("date").agg(n=("gross_pts", "size"), eqpct=("equity_pct", lambda s: float(s.sum())))
    active_days = len(days)
    frac_kill = (days["eqpct"] <= -KILL_FRAC).mean() if active_days else 0.0

    return {
        "n_trades": int(len(t)),
        "win_rate": round(float(wr), 4),
        "profit_factor": round(float(pf), 4),
        "gross_pts": round(float(t["gross_pts"].sum()), 2),
        "net_pts": round(float(t["net_pts"].sum()), 2),
        "max_dd_pts": round(float(dd), 2),
        "avg_trades_per_day": round(len(t) / active_days, 3) if active_days else 0.0,
        "frac_days_killswitch": round(float(frac_kill), 4),
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


def _gates(name: str, is_trades, oos_trades, params: StudyParams) -> dict:
    is_m = _metrics(is_trades, params.friction_base_pts)
    oos_m = _metrics(oos_trades, params.friction_base_pts)
    th = THRESH[name]

    # gate 5: IS reproduction = net positive
    g5 = is_m["net_pts"] > 0
    # gate 1: OOS net positive
    g1 = oos_m["net_pts"] > 0
    # gate 2: OOS per-day bootstrap p5 > 0
    daily = oos_trades.groupby("date")["net_pts"].sum()
    p5 = _bootstrap_p5(daily, params.n_sims, params.seed)
    g2 = p5 > 0
    # gate 3: OOS winrate & PF
    wr_ok = oos_m["win_rate"] is not None and oos_m["win_rate"] >= th["oos_winrate"]
    pf_ok = oos_m["profit_factor"] is not None and oos_m["profit_factor"] >= th["oos_pf"]
    g3 = bool(wr_ok and pf_ok)
    # gate 4: tail fragility
    g4 = not (oos_m["frac_days_killswitch"] >= KILL_DAY_FRACTION or oos_m["gross_pts"] <= 0)
    # gate 6: structural, by construction
    g6 = True

    gates_fail = not (g1 and g2 and g3 and g4 and g5 and g6)
    return {
        "is": is_m,
        "oos": oos_m,
        "gates": {
            "gate1_oos_net_positive": {"ok": g1, "net_pts": oos_m["net_pts"]},
            "gate2_oos_bootstrap_p5": {"ok": g2, "p5": p5},
            "gate3_oos_winrate_pf": {"ok": g3, "win_rate": oos_m["win_rate"],
                                     "pf": oos_m["profit_factor"],
                                     "min_winrate": th["oos_winrate"], "min_pf": th["oos_pf"]},
            "gate4_tail_fragility": {"ok": g4, "frac_days_killswitch": oos_m["frac_days_killswitch"],
                                     "gross_pts": oos_m["gross_pts"]},
            "gate5_is_reproduction": {"ok": g5, "is_net_pts": is_m["net_pts"]},
            "gate6_lookahead": {"ok": g6, "note": "structural: prev-day levels/range complete before trigger, fill at next-bar open, intra-bar stops"},
        },
        "verdict": "DISCONFIRMED" if gates_fail else "CLEARS-OOS",
    }


def main() -> int:
    params = StudyParams()
    OUT.mkdir(parents=True, exist_ok=True)

    print("loading combined NQ RTH bars (2013-11 .. 2026-08)...")
    bars = load_intraday(params)
    print(f"  1m={len(bars['1m'])} 5m={len(bars['5m'])} rows")

    runs = {
        "orb": run_orb,
        "gap_fill": run_gap_fill,
        "oops": run_oops,
    }

    summary = {
        "instrument": params.symbol,
        "is_window": list(IS_WINDOW),
        "oos_window": list(OOS_WINDOW),
        "friction_base_pts": params.friction_base_pts,
        "strategies": {},
    }

    for name, fn in runs.items():
        print(f"--- {name} ---")
        is_trades = fn(bars, params, IS_WINDOW)
        oos_trades = fn(bars, params, OOS_WINDOW)
        is_trades.to_parquet(OUT / f"{name}_trades_is.parquet")
        oos_trades.to_parquet(OUT / f"{name}_trades_oos.parquet")
        print(f"  IS trades={len(is_trades)} OOS trades={len(oos_trades)}")

        res = _gates(name, is_trades, oos_trades, params)
        entry = {"is": res["is"], "oos": res["oos"], "gates": res["gates"],
                 "verdict": res["verdict"]}

        if name == "gap_fill":
            is_rate = gap_fill_rate(bars, params, IS_WINDOW)
            oos_rate = gap_fill_rate(bars, params, OOS_WINDOW)
            entry["is_gap_fill_rate"] = is_rate
            entry["oos_gap_fill_rate"] = oos_rate
            fr_ok = is_rate["fill_rate"] is not None and is_rate["fill_rate"] >= THRESH["gap_fill"]["fill_rate"]
            entry["gap_fill_rate_gate"] = {"ok": fr_ok, "min": THRESH["gap_fill"]["fill_rate"],
                                           "note": "raw fill-rate stat (dir-agnostic), not a P&L gate"}
            summary["strategies"][name] = entry
        else:
            summary["strategies"][name] = entry

    # overall: any strategy clears -> report independently (no single portfolio verdict)
    (OUT / "probe_summary.json").write_text(json.dumps(summary, indent=2, default=float))
    print(json.dumps(summary, indent=2, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
