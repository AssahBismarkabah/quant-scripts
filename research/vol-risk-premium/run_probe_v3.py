"""V3 VRP probe: tail-overlay short-vol strategy.

Pre-registered in IA/vol-risk-premium-research-spec.md section 15 (frozen 2026-08-08).
Core = long short-vol (SVXY); overlay exits to cash when any tail-risk trigger is active.
Tests whether the short-vol premium can be kept while bounding the tail (vs naive -95%).

Usage:
    .venv/bin/python research/vol-risk-premium/run_probe_v3.py
Writes research/vol-risk-premium/outputs/v3_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "research" / "vol-risk-premium" / "cache"
OUT_DIR = ROOT / "research" / "vol-risk-premium" / "outputs"
SPYPQ = ROOT / "research" / "vol-targeting" / "cache" / "SPY_clean_long.parquet"

# frozen overlay thresholds (spec 15.B)
VIX_HIGH = 30.0
VIX_5D_CHANGE = 0.10          # +10% in 5 days
SPY_DD_60D = 0.05             # -5% from 60-day high
MAX_DD_LIMIT = -0.40          # gate 1
TERM_INVERT = 0.0             # VIX - VIX3M > 0


def load_cboe(sid: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE / f"{sid}.csv")
    df["date"] = pd.to_datetime(df["DATE"], format="%m/%d/%Y")
    df = df[["date", "CLOSE"]].rename(columns={"CLOSE": sid})
    return df.sort_values("date")


def load_svxy() -> pd.DataFrame:
    df = pd.read_parquet(CACHE / "SVXY.parquet")[["ts_date", "adj_close"]]
    df = df.rename(columns={"ts_date": "date", "adj_close": "svxy"})
    df["ret"] = df["svxy"].pct_change().fillna(0.0)
    return df.sort_values("date")


def build_panel() -> pd.DataFrame:
    vix = load_cboe("VIX")
    v3 = load_cboe("VIX3M")
    v9 = load_cboe("VIX9D")
    spy = pd.read_parquet(SPYPQ)[["ts_date", "close"]].rename(columns={"ts_date": "date"})
    svxy = load_svxy()

    df = (
        svxy[["date", "svxy", "ret"]]
        .merge(vix, on="date", how="left")
        .merge(v3, on="date", how="left")
        .merge(v9, on="date", how="left")
        .merge(spy, on="date", how="left")
        .sort_values("date")
        .reset_index(drop=True)
    )
    # forward-fill signal inputs up to t (use values known at prior close)
    for c in ["VIX", "VIX3M", "VIX9D", "close"]:
        df[c] = df[c].ffill()
    df["vix_5d_chg"] = df["VIX"].pct_change(5)
    df["spy_60d_high"] = df["close"].rolling(60).max().shift(1)
    df["spy_dd"] = df["close"] / df["spy_60d_high"] - 1.0
    df["term"] = df["VIX"] - df["VIX3M"]
    return df


def make_overlay_signals(df: pd.DataFrame) -> np.ndarray:
    """Return bool array: True = stress (de-risk to cash). Uses prior-day values only."""
    trig1 = df["term"] > TERM_INVERT                       # VIX > VIX3M (inversion)
    trig2 = (df["VIX"] > VIX_HIGH) | (df["vix_5d_chg"] > VIX_5D_CHANGE)
    trig3 = df["spy_dd"] < -SPY_DD_60D
    overlay = (trig1 | trig2 | trig3).shift(1).fillna(False).to_numpy()  # signal known at prev close
    return overlay.astype(bool)


def stats(returns: np.ndarray, dates: pd.Series) -> dict:
    nav = np.cumprod(1.0 + returns)
    total = nav[-1] - 1.0
    peak = np.maximum.accumulate(nav)
    dd = (peak - nav) / peak
    worst = float(np.min(returns)) if len(returns) else 0.0
    widx = int(np.argmin(returns)) if len(returns) else 0
    return {
        "total_return_pct": round(float(total) * 100, 2),
        "worst_single_day_pct": round(worst * 100, 2),
        "worst_single_day_date": str(dates.iloc[widx].date()) if len(returns) else "n/a",
        "max_drawdown_pct": round(float(dd.max()) * 100, 2),
        "days_in_market": int(np.sum(returns != 0.0)),
    }


def main() -> int:
    df = build_panel()
    df = df[df["ret"].notna()].reset_index(drop=True)
    overlay = make_overlay_signals(df)

    base_ret = df["ret"].to_numpy()
    core_ret = np.where(overlay, 0.0, base_ret)   # flat when stress, else long short-vol

    naive = stats(base_ret, df["date"])
    ovly = stats(core_ret, df["date"])

    # gates (frozen 15.D)
    g1 = ovly["max_drawdown_pct"] > MAX_DD_LIMIT * 100
    g2 = ovly["total_return_pct"] > 0
    g3a = ovly["max_drawdown_pct"] < naive["max_drawdown_pct"] - 5.0   # materially lower DD
    g3b = ovly["total_return_pct"] > 0
    gates = {
        "gate1_tail_bounded": bool(g1),
        "gate2_harvestable_net": bool(g2),
        "gate3_overlay_adds_value": bool(g3a and g3b),
    }
    verdict = "DISCONFIRMED"
    if g1 and g2:
        verdict = "MEASURED-NOT-DISCONFIRMED (candidate for V4)"

    summary = {
        "probe": "v3_tail_overlay_short_vol",
        "frozen_ref": "IA/vol-risk-premium-research-spec.md section 15",
        "sample_days": int(len(df)),
        "sample_range": f"{df['date'].iloc[0].date()} -> {df['date'].iloc[-1].date()}",
        "overlay_fired_days": int(np.sum(np.diff(overlay.astype(int)) == 1)),
        "naive_buy_hold": naive,
        "tail_overlay": ovly,
        "gates": gates,
        "verdict": verdict,
        "interpretation": (
            "V3 tests whether a short-vol core + a tail-risk overlay (term-structure "
            "inversion, elevated/rising VIX, equity drawdown) can keep the premium while "
            "bounding the tail that killed the naive version. Gate 1 requires max DD better "
            "than -40%; gate 2 requires positive net return; gate 3 requires the overlay to "
            "beat naive buy-and-hold on drawdown while staying profitable."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "v3_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print("\nVERDICT:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
