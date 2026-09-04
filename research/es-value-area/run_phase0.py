"""Phase 0 data audit for the pre-registered ES value-area study."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

CACHE = ROOT / "research" / "relative-value" / "cache" / "ES_n_0_1m.parquet"
OUT = ROOT / "research" / "es-value-area" / "outputs"
RTH_START = "09:30"
RTH_END = "16:00"


def audit(path: Path = CACHE) -> dict:
    if not path.exists():
        return {"status": "UNVERIFIABLE", "reason": f"missing cache: {path}"}
    frame = pd.read_parquet(path)
    required = {"ts", "open", "high", "low", "close", "volume"}
    missing = sorted(required - set(frame.columns))
    if missing:
        return {"status": "UNVERIFIABLE", "reason": f"missing columns: {missing}"}
    ts = pd.to_datetime(frame["ts"], utc=True).dt.tz_convert("America/New_York")
    rth = frame.loc[(ts.dt.time >= pd.Timestamp(RTH_START).time()) &
                    (ts.dt.time < pd.Timestamp(RTH_END).time())].copy()
    rth["et"] = ts.loc[rth.index]
    rth["date"] = rth["et"].dt.date
    counts = rth.groupby("date")["et"].nunique()
    duplicates = int(rth.duplicated(subset=["et"]).sum())
    invalid_ohlc = int(((rth["high"] < rth[["open", "close"]].max(axis=1)) |
                        (rth["low"] > rth[["open", "close"]].min(axis=1))).sum())
    nonpositive_volume = int((rth["volume"] <= 0).sum())
    dates = sorted(counts.index)
    complete = counts[counts >= 390]
    result = {
        "status": "PASS" if dates and duplicates == 0 and invalid_ohlc == 0 and nonpositive_volume == 0 else "FAIL",
        "source": str(path),
        "columns": sorted(frame.columns.tolist()),
        "source_rows": int(len(frame)),
        "rth_rows": int(len(rth)),
        "first_rth_date": str(dates[0]) if dates else None,
        "last_rth_date": str(dates[-1]) if dates else None,
        "rth_sessions": int(len(dates)),
        "sessions_with_390_bars": int(len(complete)),
        "bar_count_min": int(counts.min()) if len(counts) else None,
        "bar_count_max": int(counts.max()) if len(counts) else None,
        "duplicate_rth_timestamps": duplicates,
        "invalid_ohlc_rows": invalid_ohlc,
        "nonpositive_volume_rows": nonpositive_volume,
        "sessions_under_390_bars": [str(x) for x in counts[counts < 390].index],
        "is_window": ["2020-09-01", "2023-12-29"],
        "oos_start": "2024-01-02",
        "oos_end": str(complete.index[-1]) if len(complete) else None,
        "note": "390 bars is the normal 09:30-16:00 RTH count; early closes are reported, not silently discarded.",
    }
    return result


def main() -> int:
    result = audit()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "phase0_coverage.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
