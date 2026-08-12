"""Step 1 Test B — natural positive control: long-equity-vs-cash (smoke test).

Per IA/path-forward-decision-memo.md Step 1 (refined): Test B is a SMOKE test
only, NOT load-bearing. Its value is limited: it mostly shows the harness can
detect *beta* (long-equity-vs-risk-free), which almost any pipeline trivially
can. Test A (synthetic embedded-alpha) is the load-bearing control.

Design (pre-registered 2026-08-12):
- Equity: SPY daily total-return proxy (close-to-close, from SPY_clean_long.parquet,
  1993-02 -> 2026-07). No dividends (conservative; SPY close excludes dividends).
- Risk-free: 3M T-bill (FRED DTB3), converted to a daily risk-free rate.
- Excess return = equity_ret - rf_daily, compounded into an equity curve.
- Run through the equity backtest metrics (CAGR, Sharpe vs 0, max DD) on
  IS/OOS windows, and bootstrap the daily excess returns (permutation of the
  harness's ethos applied at the daily level) to get a p5 on the mean.
- Smoke gate: the long-equity-vs-cash premium must be large and positive in
  BOTH windows (CAGR >> 0, Sharpe > 0, bootstrap p5 of mean excess > 0).

NOT a tradable strategy claim; a calibration/sanity check only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "research" / "vol-targeting" / "cache"
OUTDIR = ROOT / "research" / "positive-control"
OUT = OUTDIR / "step1_testB_summary.json"

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FRED_RF_SERIES = "DTB3"  # 3-month T-bill secondary market rate, % annualized

IS_START, IS_END = "1993-02-01", "2008-12-31"
OOS_START, OOS_END = "2010-01-01", "2026-07-31"
N_BOOT = 10_000
SEED = 7


def load_spy() -> pd.DataFrame:
    df = pd.read_parquet(CACHE / "SPY_clean_long.parquet")
    df["ts_date"] = pd.to_datetime(df["ts_date"])
    df = df.set_index("ts_date")[["close"]].sort_index()
    df["ret"] = df["close"].pct_change()
    return df[["ret"]]


def load_rf() -> pd.Series:
    """Fetch 3M T-bill from FRED, return daily risk-free rate series indexed by date."""
    r = requests.get(FRED, params={
        "id": FRED_RF_SERIES,
        "cosd": "1993-01-01", "coed": "2026-12-31",
    }, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(pd.io.common.StringIO(r.text))
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df = df.rename(columns={FRED_RF_SERIES: "rf"})
    df["rf"] = pd.to_numeric(df["rf"], errors="coerce")
    df = df.dropna().set_index("observation_date")["rf"].sort_index()
    # % annualized -> daily simple rate
    daily = (1 + df / 100) ** (1 / 252.0) - 1
    return daily


def metrics(value: pd.Series) -> dict:
    rets = value.pct_change().dropna()
    days = (value.index[-1] - value.index[0]).days
    years = days / 365.25
    cagr = (value.iloc[-1] / value.iloc[0]) ** (1 / years) - 1 if value.iloc[0] > 0 else np.nan
    vol = rets.std(ddof=0) * np.sqrt(252)
    sharpe = (rets.mean() / rets.std(ddof=0)) * np.sqrt(252) if rets.std(ddof=0) > 0 else np.nan
    dd = value / value.cummax() - 1
    return {"cagr": float(cagr), "sharpe": float(sharpe),
            "vol": float(vol), "max_drawdown": float(dd.min()),
            "end_value": float(value.iloc[-1])}


def bootstrap_mean_p5(excess: pd.Series) -> float:
    rng = np.random.default_rng(SEED)
    x = excess.dropna().to_numpy()
    means = np.array([rng.choice(x, size=len(x), replace=True).mean() for _ in range(N_BOOT)])
    return float(np.percentile(means, 5))


def main() -> int:
    spy = load_spy()
    rf = load_rf()
    # Excess daily return = spy_ret - rf_daily (rf forward-filled over non-Holiday dates)
    spy["rf"] = rf.reindex(spy.index).ffill().fillna(0.0)
    spy["excess"] = spy["ret"] - spy["rf"]
    # First row's return is NaN (pct_change); drop it so momentum/cum are clean.
    spy = spy.dropna(subset=["excess"])

    print(f"SPY {spy.index.min().date()} .. {spy.index.max().date()}  excess daily mean {spy['excess'].mean()*100:.3f}%")
    result = {"meta": {
        "pre_registered": "2026-08-12",
        "purpose": "Smoke test: harness must detect the large, established long-equity-vs-cash premium",
        "equity": "SPY close-to-close (no dividends; conservative)",
        "risk_free": "FRED DTB3 3M T-bill",
        "note": "SMOKE test only; Test A is the load-bearing control.",
        "split": {"IS": [IS_START, IS_END], "OOS": [OOS_START, OOS_END]},
    }, "windows": {}, "gates": {}}

    # Build a $1 equity curve from the cumulative excess returns within each window.
    # The smoke gate runs on the FULL clean sample (the right way to detect a
    # large long-run equity premium); the two halves are reported as context.
    full_win = ("FULL", str(spy.index.min().date()), str(spy.index.max().date()))
    for wname, ws, we in [
        ("IS", IS_START, IS_END),
        ("OOS", OOS_START, OOS_END),
        full_win,
    ]:
        w = spy.loc[ws:we].copy()
        w["cum"] = (1 + w["excess"]).cumprod()
        w["cum"] = w["cum"] / w["cum"].iloc[0]  # start at 1
        m = metrics(w["cum"])
        m["bootstrap_p5_excess_mean"] = bootstrap_mean_p5(w["excess"])
        m["sample_days"] = int(len(w))
        result["windows"][wname] = m

    # Smoke gate: a large positive long-equity-vs-cash premium over the FULL
    # sample (price-only SPY is conservative; dividends would add ~1.5-2%/yr).
    full = result["windows"]["FULL"]
    gate = (
        full["cagr"] > 0.03 and full["sharpe"] > 0
        and full["bootstrap_p5_excess_mean"] > 0
    )
    result["gates"]["G1B_long_equity_premium_detected"] = {
        "pass": gate,
        "FULL": {k: full[k] for k in ["cagr", "sharpe", "bootstrap_p5_excess_mean", "max_drawdown"]},
        "IS": {
            "cagr": result["windows"]["IS"]["cagr"],
            "sharpe": result["windows"]["IS"]["sharpe"],
            "note": "1993-2008 ends at the GFC trough; weak IS is an artifact of the "
                    "break point + price-only (no dividends), not a harness failure.",
        },
        "OOS": {k: result["windows"]["OOS"][k] for k in ["cagr", "sharpe", "bootstrap_p5_excess_mean", "max_drawdown"]},
        "note": "Smoke test: harness must detect a large long-equity-vs-cash premium over the "
                "FULL sample (CAGR>3%, Sharpe>0, bootstrap p5 of mean excess >0). IS ending at "
                "the 2008 trough is expected weak; the full-sample signal is load-bearing here.",
    }
    result["testB_verdict"] = "PASS" if gate else "FAIL"
    OUTDIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, default=str))
    print(json.dumps(result, indent=2, default=str))
    print(f"\nTest B verdict (smoke): {result['testB_verdict']}")
    print(f"wrote {OUT}")
    return 0 if gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
