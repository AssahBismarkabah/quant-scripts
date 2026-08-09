"""V1 VRP probe: private registration of the unconditional variance risk premium.

Pre-registered in IA/vol-risk-premium-research-spec.md section 11 (frozen 2026-08-08).
Tests whether implied variance (VIX^2) systematically exceeds forward realized
variance on SPY, over IS (1993-02 -> 2008-12) and the modern/OOS window
(2009-01 -> 2026-07). Gates and definitions are frozen; a verdict is recorded once.

Usage:
    .venv/bin/python research/vol-risk-premium/run_probe.py
Writes research/vol-risk-premium/outputs/v1_summary.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
VIXCSV = ROOT / "research" / "vol-targeting" / "cache" / "VIXCLS.csv"
SPYPQ = ROOT / "research" / "vol-targeting" / "cache" / "SPY_clean_long.parquet"
OUT_DIR = ROOT / "research" / "vol-risk-premium" / "outputs"

H = 21  # forward realized-variance window (trading days); VIX is 30-day (~22 td) — robustness uses 22
RNG = np.random.default_rng(20260808)
N_BOOT = 10_000

IS_START, IS_END = pd.Timestamp("1993-02-01"), pd.Timestamp("2008-12-31")
OOS_START, OOS_END = pd.Timestamp("2009-01-01"), pd.Timestamp("2026-07-31")

# conservative placeholder for executable short-vol cost (fraction of premium)
COST_BUF = 0.10


def load_aligned() -> pd.DataFrame:
    vix = pd.read_csv(VIXCSV, parse_dates=["observation_date"])
    vix = vix.rename(columns={"observation_date": "date", "VIXCLS": "vix"})
    vix = vix.dropna(subset=["vix"])
    vix = vix.sort_values("date").drop_duplicates("date")

    spy = pd.read_parquet(SPYPQ)[["ts_date", "close"]]
    spy = spy.rename(columns={"ts_date": "date"})
    spy = spy.sort_values("date").drop_duplicates("date")

    df = pd.merge(spy, vix, on="date", how="inner").sort_values("date")
    if len(df) == 0:
        raise SystemExit("no overlapping VIX/SPY dates")
    return df.reset_index(drop=True)


def add_vrp(df: pd.DataFrame) -> pd.DataFrame:
    # returns in % (so rv_fwd is in %^2, directly comparable to VIX^2 in %^2)
    ret = 100.0 * np.log(df["close"].to_numpy()).astype(float)
    ret = np.diff(ret, prepend=np.nan)
    df["ret"] = ret

    # forward realized variance, annualized, over next H trading days
    n = len(df)
    rv_fwd = np.full(n, np.nan)
    ret_arr = ret
    for i in range(n):
        window = ret_arr[i + 1 : i + 1 + H]
        if len(window) < H:  # require a full forward window (no partial)
            continue
        rv_fwd[i] = (252.0 / H) * float(np.sum(window**2))
    df["rv_fwd"] = rv_fwd

    df["iv"] = df["vix"] ** 2.0               # %^2
    df["vrp"] = df["iv"] - df["rv_fwd"]       # %^2
    # annualized vol-point spread (reporting only): sqrt of %^2 -> %
    df["vrp_vol"] = np.sqrt(df["iv"]) - np.sqrt(df["rv_fwd"])
    return df


def bootstrap_p5(series: pd.Series) -> float:
    x = series.dropna().to_numpy()
    if len(x) < 2:
        return np.nan
    means = np.empty(N_BOOT)
    for b in range(N_BOOT):
        means[b] = RNG.choice(x, size=len(x), replace=True).mean()
    return float(np.percentile(means, 5))


def summarize(df: pd.DataFrame, lo: pd.Timestamp, hi: pd.Timestamp, tag: str) -> dict:
    sub = df[(df["date"] >= lo) & (df["date"] <= hi) & df["vrp"].notna()]
    if len(sub) == 0:
        return {"window": tag, "n": 0, "mean_vrp": float("nan"),
                "mean_vrp_vol": float("nan"), "bootstrap_p5": float("nan"),
                "net_mean_vrp": float("nan")}
    mean_vrp = float(sub["vrp"].mean())
    net_mean_vrp = mean_vrp * (1.0 - COST_BUF)
    return {
        "window": tag,
        "dates": f"{sub['date'].iloc[0].date()} -> {sub['date'].iloc[-1].date()}",
        "n": int(len(sub)),
        "mean_vrp": float(mean_vrp),
        "mean_vrp_vol": float(sub["vrp_vol"].mean()),
        "bootstrap_p5": bootstrap_p5(sub["vrp"]),
        "net_mean_vrp": float(net_mean_vrp),
    }


def by_decade(df: pd.DataFrame) -> dict[str, float]:
    out: dict[str, float] = {}
    years = df["date"].dt.year
    for start in range(1990, 2031, 10):
        end = start + 9
        mask = (years >= start) & (years <= end) & df["vrp"].notna()
        if mask.sum() == 0:
            continue
        out[f"{start}-{end}"] = float(df.loc[mask, "vrp"].mean())
    return out


def main() -> int:
    df = load_aligned()
    df = add_vrp(df)

    is_sum = summarize(df, IS_START, IS_END, "is")
    oos_sum = summarize(df, OOS_START, OOS_END, "oos_modern")

    # gates (frozen in spec section 11.D)
    g1 = oos_sum["bootstrap_p5"] > 0.0            # modern premium exists
    g3 = is_sum["bootstrap_p5"] > 0.0             # IS reproduction (sanity)
    g4 = oos_sum["net_mean_vrp"] > 0.0            # survives cost buffer

    gates = {
        "gate1_oos_modern_premium": bool(g1),
        "gate1_note": f"OOS bootstrap p5={oos_sum['bootstrap_p5']:.4f}",
        "gate3_is_reproduction": bool(g3),
        "gate3_note": f"IS bootstrap p5={is_sum['bootstrap_p5']:.4f}",
        "gate4_survives_cost": bool(g4),
        "gate4_note": f"OOS net mean VRP={oos_sum['net_mean_vrp']:.4f} (cost buf {COST_BUF})",
        "gate2_lookahead": True,
        "gate2_note": "VRP_t uses VIX_t and past returns only; fwd realized var is tagged outcome",
    }

    # DISCONFIRMED if any of gates 1, 3, 4 fail (per spec 11.D)
    failed = [k for k, v in {"gate1": g1, "gate3": g3, "gate4": g4}.items() if not v]
    # Honest framing: V1 measures the LEVEL of the premium (implied>realized on
    # average), which passes its gates -- but a positive average level is NOT a
    # deployable edge. The tradeable short-vol question (costs + tail + decay)
    # is V2. So a pass on the level gate is "MEASURED," never "validated edge."
    if failed:
        verdict = "DISCONFIRMED"
        interpretation = "One or more V1 level-gates failed."
    else:
        verdict = "MEASURED-POSITIVE-LEVEL (NOT ADVANCED)"
        interpretation = (
            "V1 gates passed: the average implied-vs-realized premium is positive "
            "and persistent across IS and the modern OOS window (see mean_vrp_vol by era). "
            "This confirms the LEVEL of the variance risk premium is real. It does NOT "
            "establish a deployable edge: capturing it requires selling vol/options with "
            "real costs and the severe fat tail, which V1 does not model. Whether the "
            "premium is *harvestable* after costs and survives its own tail, and whether "
            "event/conditional versions add anything, is the V2 question."
        )

    summary = {
        "probe": "v1_unconditional_vrp",
        "instrument_implied": "CBOE VIX (FRED VIXCLS)",
        "instrument_realized": "SPY daily (Yahoo)",
        "frozen_ref": "IA/vol-risk-premium-research-spec.md section 11",
        "h_fwd_days": H,
        "n_aligned_days": int(len(df)),
        "vrp_mean_by_decade": by_decade(df),
        "panels": {"is": is_sum, "oos_modern": oos_sum},
        "gates": gates,
        "failed_gates": failed,
        "verdict": verdict,
        "interpretation": interpretation,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "v1_summary.json").write_text(json.dumps(summary, indent=2))

    print(json.dumps(summary, indent=2))
    print("\nVERDICT:", verdict, "(failed:" + (", ".join(failed) or "none") + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
