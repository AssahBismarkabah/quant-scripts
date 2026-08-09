"""Acquire free daily OHLC for short/long-vol ETPs from Yahoo Finance.

Instruments (the "premium capture" test vehicle for the short-vol / VRP candidate):
    SVXY  ProShares Short VIX Short-Term Futures ETF (-1x short vol), inception 2011-10
    XIV   VelocityShares Daily Inverse VIX Short-Term ETN (-1x short vol), inception 2010-11,
          delisted 2018-02 after the volmageddon crush (~-80%+ single-day loss)  -> THE tail
    VXX   Barclays iPath S&P 500 VIX Short-Term Futures ETN (+1x long vol), inception 2009-01
    SVIX  Volatility Shares -1x Short VIX Futures ETF (-1x short vol), inception 2022-03

Yahoo's chart API collapses to monthly when a single request spans too much history at
interval=1d, so we fetch in ~8-year daily windows and concatenate (house pattern from
research/vol-targeting/acquire_long_spy.py). Output: cache/<SYM>.parquet
(columns ts_date, open, high, low, close). Cache is gitignored / re-fetchable.

Roadmap ref: IA/vol-risk-premium-research-spec.md section 4.D / 6.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

CACHE = Path(__file__).resolve().parent / "cache"
HEADERS = {"User-Agent": "Mozilla/5.0"}
URL = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
WINDOW_DAYS = 8 * 366

SYMBOLS = ["SVXY", "XIV", "VXX", "SVIX"]
START = datetime(2009, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 8, 5, tzinfo=timezone.utc)


def epoch(dt: datetime) -> int:
    return int(dt.timestamp())


def fetch_window(sym: str, p1: datetime, p2: datetime) -> list[dict]:
    params = {"period1": epoch(p1), "period2": epoch(p2), "interval": "1d", "events": "history"}
    r = requests.get(URL.format(sym=sym), params=params, headers=HEADERS, timeout=30)
    if r.status_code in (400, 404):
        return []  # delisted / range outside listing / no data (e.g. XIV after 2018 crush)
    r.raise_for_status()
    res = r.json()["chart"]["result"]
    if not res:
        return []
    ts = res[0]["timestamp"]
    q = res[0]["indicators"]["quote"][0]
    adj = (res[0].get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose")
    rows = []
    for i, t in enumerate(ts):
        rows.append({
            "ts_date": pd.Timestamp(datetime.fromtimestamp(t, timezone.utc).date()),
            "open": q["open"][i],
            "high": q["high"][i],
            "low": q["low"][i],
            "close": q["close"][i],
            "adj_close": (adj[i] if adj else q["close"][i]),
        })
    return rows


def fetch_symbol(sym: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    lo = START
    while lo < END:
        hi = min(lo + timedelta(days=WINDOW_DAYS), END)
        rows = fetch_window(sym, lo, hi)
        if rows:
            df = pd.DataFrame(rows).dropna(subset=["close"]).drop_duplicates(subset=["ts_date"])
            frames.append(df)
            print(f"[{sym}] fetched {lo.date()} -> {hi.date()}: {len(df)} rows")
        lo = hi + timedelta(days=1)
        time.sleep(0.4)
    if not frames:
        print(f"[{sym}] no data available (delisted or delayed quote); skipping")
        return pd.DataFrame()
    out = (
        pd.concat(frames)
        .sort_values("ts_date")
        .drop_duplicates(subset=["ts_date"], keep="first")
        .reset_index(drop=True)
    )
    CACHE.mkdir(parents=True, exist_ok=True)
    out.to_parquet(CACHE / f"{sym}.parquet")
    print(f"[{sym}] saved {len(out)} rows, {out['ts_date'].iloc[0].date()} -> {out['ts_date'].iloc[-1].date()}")
    return out


def main() -> int:
    for sym in SYMBOLS:
        fetch_symbol(sym)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
