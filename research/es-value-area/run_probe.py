"""Run the frozen ES value-area opening-state probe."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from quant_scripts.es_value_area.backtest import run_backtest  # noqa: E402

CACHE = ROOT / "research" / "relative-value" / "cache" / "ES_n_0_1m.parquet"
OUT = ROOT / "research" / "es-value-area" / "outputs"


def metrics(trades: pd.DataFrame, net_col: str) -> dict:
    if trades.empty:
        return {"n_trades": 0, "net_pts": 0.0, "win_rate": None, "profit_factor": None}
    x = trades[net_col]
    wins, losses = x[x > 0].sum(), abs(x[x < 0].sum())
    return {"n_trades": int(len(x)), "net_pts": round(float(x.sum()), 4),
            "win_rate": round(float((x > 0).mean()), 4),
            "profit_factor": round(float(wins / losses), 4) if losses else None,
            "max_drawdown_pts": round(float((x.cumsum() - x.cumsum().cummax()).min()), 4)}


def bootstrap_p5(trades: pd.DataFrame, net_col: str, seed: int = 20260904) -> float:
    daily = trades.groupby("date")[net_col].sum().to_numpy(dtype=float)
    if not len(daily):
        return 0.0
    rng = np.random.default_rng(seed)
    samples = np.array([rng.choice(daily, len(daily), replace=True).sum() for _ in range(5000)])
    return round(float(np.percentile(samples, 5)), 4)


def main() -> int:
    one = pd.read_parquet(CACHE)
    one["ts"] = pd.to_datetime(one["ts"])
    is_trades = run_backtest(one, "2020-09-01", "2023-12-29")
    oos_trades = run_backtest(one, "2024-01-02", "2026-08-06")
    OUT.mkdir(parents=True, exist_ok=True)
    is_trades.to_parquet(OUT / "probe_trades_is.parquet")
    oos_trades.to_parquet(OUT / "probe_trades_oos.parquet")
    oos_base = metrics(oos_trades, "base_net_pts")
    oos_stress = metrics(oos_trades, "stress_net_pts")
    concentration = float(oos_trades.groupby("date")["base_net_pts"].sum().max()) if not oos_trades.empty else 0.0
    total = float(oos_trades.base_net_pts.sum()) if not oos_trades.empty else 0.0
    gates = {"data_phase0": True,
             "oos_net_positive_base": bool(total > 0),
             "oos_net_positive_stress": bool(oos_trades.stress_net_pts.sum() > 0) if not oos_trades.empty else False,
             "sample_ge_100": bool(len(oos_trades) >= 100),
             "bootstrap_p5_base_positive": bootstrap_p5(oos_trades, "base_net_pts") > 0,
             "bootstrap_p5_stress_positive": bootstrap_p5(oos_trades, "stress_net_pts") > 0,
             "base_pf_ge_1_05": bool(oos_base["profit_factor"] is not None and oos_base["profit_factor"] >= 1.05),
             "stress_pf_gt_1": bool(oos_stress["profit_factor"] is not None and oos_stress["profit_factor"] > 1.0),
             "best_day_le_20pct": bool(total > 0 and concentration <= 0.20 * total),
             "is_base_positive": bool(not is_trades.empty and is_trades.base_net_pts.sum() > 0)}
    summary = {"instrument": "ES.n.0", "profile": "one-minute-close volume proxy",
               "is": {"base": metrics(is_trades, "base_net_pts"), "stress": metrics(is_trades, "stress_net_pts")},
               "oos": {"base": oos_base, "stress": oos_stress}, "gates": gates,
               "bootstrap_p5_base": bootstrap_p5(oos_trades, "base_net_pts"),
               "bootstrap_p5_stress": bootstrap_p5(oos_trades, "stress_net_pts"),
               "verdict": "CLEARS-OOS" if all(gates.values()) else "DISCONFIRMED"}
    (OUT / "probe_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
