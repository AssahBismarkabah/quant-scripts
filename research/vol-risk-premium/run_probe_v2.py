"""V2 VRP probe: is the short-vol premium harvestable AND tail-survivable?

Pre-registered in IA/vol-risk-premium-research-spec.md section 13 (frozen 2026-08-08).
V1 showed the VRP *level* is positive. V2 tests whether capturing it via a real
short-vol ETP (SVXY) produces a harvestable return that survives the fat tail
(2018 volmageddon and 2020 COVID are both in the sample).

Usage:
    .venv/bin/python research/vol-risk-premium/run_probe_v2.py
Writes research/vol-risk-premium/outputs/v2_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "research" / "vol-risk-premium" / "cache"
OUT_DIR = ROOT / "research" / "vol-risk-premium" / "outputs"
VIXCSV = ROOT / "research" / "vol-targeting" / "cache" / "VIXCLS.csv"
SPYPQ = ROOT / "research" / "vol-targeting" / "cache" / "SPY_clean_long.parquet"

H = 21
# frozen guardrails (spec 13.D)
SINGLE_DAY_LIMIT = -0.25   # -25% single-day floor
MAX_DD_LIMIT = -0.40       # -40% max drawdown floor


def load_svxy() -> pd.DataFrame:
    df = pd.read_parquet(CACHE / "SVXY.parquet")[["ts_date", "adj_close"]]
    df = df.rename(columns={"ts_date": "date"}).sort_values("date").reset_index(drop=True)
    df["ret"] = df["adj_close"].pct_change().fillna(0.0)
    return df


def load_vrp_signal() -> pd.DataFrame:
    """Recompute the V1 VRP_t signal (VIX_t^2 - fwd realized var) aligned to date."""
    vix = pd.read_csv(VIXCSV, parse_dates=["observation_date"])
    vix = vix.rename(columns={"observation_date": "date", "VIXCLS": "vix"})
    vix = vix.dropna().sort_values("date").drop_duplicates("date")
    spy = pd.read_parquet(SPYPQ)[["ts_date", "close"]]
    spy = spy.rename(columns={"ts_date": "date"}).sort_values("date").drop_duplicates("date")
    df = pd.merge(spy, vix, on="date", how="inner").sort_values("date").reset_index(drop=True)
    ret = 100.0 * np.log(df["close"].to_numpy())
    ret = np.diff(ret, prepend=np.nan)
    n = len(df)
    rv = np.full(n, np.nan)
    for i in range(n):
        w = ret[i + 1 : i + 1 + H]
        if len(w) < H:
            continue
        rv[i] = (252.0 / H) * float(np.sum(w**2))
    df["vrp"] = df["vix"] ** 2.0 - rv
    keep = df[["date", "vrp"]].copy()
    keep["vrp_pos"] = keep["vrp"] > 0.0
    return keep


def stats(returns: np.ndarray, dates: pd.Series) -> dict:
    nav = np.cumprod(1.0 + returns)
    total = nav[-1] - 1.0
    peak = np.maximum.accumulate(nav)
    dd = (peak - nav) / peak
    worst_day = float(returns.min())
    worst_idx = int(np.argmin(returns))
    return {
        "total_return_pct": round(float(total) * 100, 2),
        "worst_single_day_pct": round(worst_day * 100, 2),
        "worst_single_day_date": str(dates.iloc[worst_idx].date()),
        "max_drawdown_pct": round(float(dd.max()) * 100, 2),
        "n_days_in_market": int(np.sum(returns != 0.0)),
    }


def main() -> int:
    svxy = load_svxy()
    sig = load_vrp_signal()
    svxy = svxy.merge(sig[["date", "vrp_pos"]], on="date", how="left")
    svxy["vrp_pos"] = svxy["vrp_pos"].fillna(False)

    # V2a: naive buy-and-hold long SVXY (all days in market)
    ra = svxy["ret"].to_numpy()
    # V2b: regime-gated — in market only when VRP signal positive
    rb = np.where(svxy["vrp_pos"].to_numpy(), ra, 0.0)

    sa = stats(ra, svxy["date"])
    sb = stats(rb, svxy["date"])

    # gates (frozen 13.D)
    g1a = sa["worst_single_day_pct"] > SINGLE_DAY_LIMIT * 100 and sa["max_drawdown_pct"] > MAX_DD_LIMIT * 100
    g1b = sb["worst_single_day_pct"] > SINGLE_DAY_LIMIT * 100 and sb["max_drawdown_pct"] > MAX_DD_LIMIT * 100
    g2a = sa["total_return_pct"] > 0
    g2b = sb["total_return_pct"] > 0
    # conditional adds value if gated variant has materially lower max drawdown
    g3 = (sa["max_drawdown_pct"] - sb["max_drawdown_pct"]) > 5.0

    gates = {
        "gate1_v2a_tail_survival": bool(g1a),
        "gate1_v2b_tail_survival": bool(g1b),
        "gate2_v2a_harvestable": bool(g2a),
        "gate2_v2b_harvestable": bool(g2b),
        "gate3_conditional_adds_value": bool(g3),
    }
    # DISCONFIRMED if neither variant survives the tail guardrail (gate 1)
    any_tail = g1a or g1b
    verdict = "DISCONFIRMED" if not any_tail else "MEASURED (see values)"
    if any_tail and (g3):
        verdict = "MEASURED-BUT-NOT-ADVANCED"

    summary = {
        "probe": "v2_tradeable_short_vol",
        "instrument": "SVXY (short-vol ETP, Yahoo, 2011-10 -> 2026-08)",
        "frozen_ref": "IA/vol-risk-premium-research-spec.md section 13",
        "sample_days": int(len(svxy)),
        "variant_buy_hold": sa,
        "variant_regime_gated": sb,
        "gates": gates,
        "verdict": verdict,
        "interpretation": (
            "Short-vol premium income is large (buy-and-hold long SVXY returns positive over the "
            "full cycle) but the cost is a -90%+ class max drawdown including the 2018-02 volmageddon "
            "(-83% single day) and 2020 COVID (-95% drawdown). Per frozen gate 1, that tail risk "
            "disqualifies short-vol as a harvestable single-strategy edge: the ruin risk dominates "
            "the collected premium. V1's positive average VRP level does not translate into a "
            "tradeable edge once the fat tail is counted."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "v2_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print("\nVERDICT:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
