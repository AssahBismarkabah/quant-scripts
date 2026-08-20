"""Phase 0 census for Probe #24 (Rule of 4): bar coverage + volatility check.

Pre-registered gate (frozen in spec §5):
  - For each event day, the window T-120..T+180 must have C1..C5 bars present
    (the first five 5-min bars after T: [T, T+5) .. [T+20, T+25)).
  - Market-level gate: >= 90% of events in the period must have full C1..C5
    coverage. Any event with missing C1..C5 bars is EXCLUDED from the alpha
    run and counted in the census report.

Also reports per-event coverage stats and a volatility sanity check: median
5-min price range in C1..C5 vs the median of the prior 2h (should be higher on
event days; a spike confirms the calendar timezone conversion is correct).

Run: python3 research/rule-of-four/phase0_census.py
Writes outputs/phase0_census.json and prints a summary.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

C5_WINDOW_MIN = 25  # C1..C5 span [T, T+25)


def load_year_files(market: str) -> pd.DataFrame:
    d = DATA / market.lower()
    frames = [pd.read_parquet(p) for p in sorted(d.glob("*.parquet"))]
    df = pd.concat(frames, ignore_index=True)
    df["ts"] = pd.to_datetime(df["ts"]).dt.tz_localize(None)
    df["event_time_exch"] = pd.to_datetime(df["event_time_exch"])
    return df


def census(market: str) -> dict:
    df = load_year_files(market)
    events = (
        df.groupby(["event_date", "event_type", "event_time_exch"], as_index=False)
        .agg(n_bars=("ts", "count"))
    )
    events["event_time_exch"] = pd.to_datetime(events["event_time_exch"])

    rows = []
    for _, e in events.iterrows():
        t0 = e["event_time_exch"]
        day = e["event_date"]
        day_df = df[df["event_date"] == day]
        # C1..C5 bars: 5-min buckets whose start is in [T, T+25)
        bars = day_df[  # noqa: F841
            (day_df["ts"] >= t0) & (day_df["ts"] < t0 + pd.Timedelta(minutes=C5_WINDOW_MIN))
        ]
        n_c5 = int(bars["ts"].nunique())
        # prior 2h bars [T-120, T) for volatility baseline
        prior = day_df[
            (day_df["ts"] >= t0 - pd.Timedelta(minutes=120)) & (day_df["ts"] < t0)
        ]
        prior_ranges = (prior["high"] - prior["low"]).clip(lower=0)
        c5_ranges = (bars["high"] - bars["low"]).clip(lower=0)
        rows.append(
            {
                "event_date": day,
                "type": e["event_type"],
                "t0": t0.isoformat(),
                "n_c5_bars": n_c5,
                "c5_full": n_c5 == 5,
                "prior_median_range": float(prior_ranges.median()) if len(prior_ranges) else np.nan,
                "c5_median_range": float(c5_ranges.median()) if len(c5_ranges) else np.nan,
            }
        )
    res = pd.DataFrame(rows)
    return res


def main() -> None:
    report = {"markets": {}, "gate": "C1..C5 present (5/5 bars) for >=90% of events", "pass": True}
    for market in ("dax", "ftse"):
        res = census(market)
        n_total = len(res)
        n_full = int(res["c5_full"].sum())
        coverage = n_full / n_total if n_total else 0.0
        # volatility spike check: fraction of events where C1..C5 median range
        # exceeds the prior-2h median range
        ok = res.dropna(subset=["prior_median_range", "c5_median_range"])
        spike = float((ok["c5_median_range"] > ok["prior_median_range"]).mean()) if len(ok) else np.nan
        m = {
            "events_total": n_total,
            "events_full_c5": n_full,
            "coverage": round(coverage, 4),
            "pass_coverage_gate": coverage >= 0.90,
            "events_with_data": int(res["n_c5_bars"].gt(0).sum()),
            "c5_volatility_spike_frac": round(spike, 4) if spike == spike else None,
            "events_excluded": int(res[~res["c5_full"]]["n_c5_bars"].gt(0).sum()),
        }
        report["markets"][market] = m
        report["pass"] = report["pass"] and m["pass_coverage_gate"]
        print(f"=== {market.upper()} ===")
        for k, v in m.items():
            print(f"  {k}: {v}")
        print()
        res.to_csv(OUT / f"phase0_census_{market}.csv", index=False)
    with (OUT / "phase0_census.json").open("w") as f:
        json.dump(report, f, indent=2, default=str)
    print("phase0 gate PASS" if report["pass"] else "phase0 gate FAIL")


if __name__ == "__main__":
    main()