"""Daily OHLCV bars from Yahoo Finance for event tickers + benchmark.

Reuses the free Yahoo chart API approach from buyback-timing/bars.py; caches to
the 10b5-1-timing research cache dir so this probe is self-contained.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}
URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}"
CACHE_DIR = Path(__file__).resolve().parents[3] / "research" / "10b5-1-timing" / "cache"


def _epoch(dt: datetime) -> int:
    return int(dt.timestamp())


def fetch_daily(ticker: str, start: datetime, end: datetime) -> pd.DataFrame:
    frames = []
    lo = start
    WINDOW = 6 * 366
    while lo < end:
        hi = min(lo + timedelta(days=WINDOW), end)
        params = {
            "period1": _epoch(lo),
            "period2": _epoch(hi),
            "interval": "1d",
            "events": "history",
        }
        last = None
        for attempt in range(4):
            try:
                r = requests.get(URL.format(ticker), params=params, headers=HEADERS, timeout=30)
                if r.status_code == 200:
                    break
                last = r
            except Exception as e:  # noqa: BLE001
                last = e
            time.sleep(1.5 * (attempt + 1))
        else:
            raise RuntimeError(f"yf {ticker}: {last}")
        res = r.json()["chart"]["result"]
        if not res:
            lo = hi + timedelta(days=1)
            continue
        ts = res[0]["timestamp"]
        q = res[0]["indicators"]["quote"][0]
        rows = [
            {
                "ts_date": pd.Timestamp(datetime.fromtimestamp(t, timezone.utc).date()),
                "open": q["open"][i],
                "high": q["high"][i],
                "low": q["low"][i],
                "close": q["close"][i],
                "volume": q["volume"][i],
            }
            for i, t in enumerate(ts)
        ]
        frames.append(pd.DataFrame(rows).dropna(subset=["close"]))
        lo = hi + timedelta(days=1)
        time.sleep(0.3)
    if not frames:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    out = pd.concat(frames).sort_values("ts_date").drop_duplicates("ts_date").reset_index(drop=True)
    out["ticker"] = ticker
    return out


def load_bars(tickers: list[str], start: datetime, end: datetime) -> pd.DataFrame:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for tk in sorted(set(tickers)):
        cache = CACHE_DIR / f"{tk}.parquet"
        if cache.exists():
            df = pd.read_parquet(cache)
        else:
            df = fetch_daily(tk, start, end)
            df.to_parquet(cache)
        frames.append(df)
        print(f"  bars {tk}: {len(df)}")
    return pd.concat(frames, ignore_index=True)
