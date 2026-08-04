"""Acquire long SPY daily OHLC from Yahoo Finance (free) in ~8-year windows.

Extends the short verified series (SPY_clean.parquet, 2023-2026) back to SPY
launch (Feb 1993). Yahoo's chart API collapses to monthly bars when a single
request spans too much history at interval=1d, so we fetch overlapping daily
windows via period1/period2 and concatenate, keeping the trusted clean bars
for the 2023-2026 overlap.

Output: cache/SPY_long.parquet (columns ts_date, open, high, low, close, volume)
This is a raw re-fetchable download (cache is gitignored), not a tracked artefact.

Roadmap ref: IA/data-and-portfolio-roadmap.md section 3.2.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

CACHE = Path(__file__).resolve().parent / "cache"
OUT = CACHE / "SPY_long.parquet"
HEADERS = {"User-Agent": "Mozilla/5.0"}
URL = "https://query1.finance.yahoo.com/v8/finance/chart/SPY"

START = datetime(1993, 2, 1, tzinfo=timezone.utc)
END = datetime(2026, 8, 3, tzinfo=timezone.utc)
WINDOW_DAYS = 8 * 366  # keep well under Yahoo's ~2500-row daily cap


def epoch(dt: datetime) -> int:
    return int(dt.timestamp())


def fetch_window(p1: datetime, p2: datetime) -> tuple[list[int], list[dict]]:
    params = {
        "period1": epoch(p1),
        "period2": epoch(p2),
        "interval": "1d",
        "events": "history",
    }
    r = requests.get(URL, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    rows = []
    for i, t in enumerate(ts):
        rows.append({
            "ts_date": pd.Timestamp(datetime.fromtimestamp(t, timezone.utc).date()),
            "open": q["open"][i],
            "high": q["high"][i],
            "low": q["low"][i],
            "close": q["close"][i],
            "volume": q["volume"][i],
        })
    return ts, rows


def main() -> int:
    frames: list[pd.DataFrame] = []
    lo = START
    while lo < END:
        hi = min(lo + timedelta(days=WINDOW_DAYS), END)
        _, rows = fetch_window(lo, hi)
        df = pd.DataFrame(rows)
        df = df.dropna(subset=["close"]).drop_duplicates(subset=["ts_date"])
        frames.append(df)
        print(f"fetched {lo.date()} -> {hi.date()}: {len(df)} daily rows")
        lo = hi + timedelta(days=1)
        time.sleep(0.4)  # be polite to Yahoo

    long = pd.concat(frames).sort_values("ts_date").reset_index(drop=True)
    long = long.drop_duplicates(subset=["ts_date"], keep="first")
    CACHE.mkdir(parents=True, exist_ok=True)
    long.to_parquet(OUT)
    print(f"\nSPY_long.parquet: {len(long)} rows, "
          f"{long['ts_date'].iloc[0].date()} -> {long['ts_date'].iloc[-1].date()}")
    # sanity: daily-granularity check
    gaps = long["ts_date"].diff().dt.days
    print(f"daily-gap stats: median {gaps.median():.0f} days, max {gaps.max():.0f} days")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
