"""Databento intraday bars for the IVAMR probe.

Fetches 1-minute OHLCV for the continuous NQ contract, converts timestamps to
ET, filters to RTH (09:30..16:00 ET), caches as 1-min parquet, and resamples to
15-min (execution) bars. The 1-min base is what the volume-at-price histogram
(VAH/VAL/POC) and the previous-day ATR are built from.

Fetch is chunked (~30-day) and resumable, matching the NQ VWAP-pullback probe:
a dropped connection is retried, completed chunks are reused, and the final
concatenation is identical to a single get_range call.
"""

from __future__ import annotations

import os
import time as _time
from datetime import timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .config import StudyParams

ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = ROOT / "research" / "ivamr" / "cache"

# Fetch begins before the IS window so every IS/OOS trading day has the previous
# trading day's RTH profile available (profile & ATR are computed from D-1).
DATA_START = "2013-11-01"


def _et_tz():
    try:
        import zoneinfo

        return zoneinfo.ZoneInfo("America/New_York")
    except Exception:  # pragma: no cover - fallback fixed offset (EST)
        return timezone.utc


def _db_api_key() -> str:
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key.strip() == "DATABENTO_API_KEY":
                return value.strip()
    return os.environ.get("DATABENTO_API_KEY", "")


def fetch_1m(params: StudyParams) -> pd.DataFrame:
    """Fetch + cache 1-minute OHLCV for the probe window; return ET RTH 1-min bars.

    Columns: ts (ET tz-aware), date, open, high, low, close, volume.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / f"{params.symbol.replace('.', '_')}_1m.parquet"
    if cache.exists():
        return pd.read_parquet(cache)

    import databento as db

    client = db.Historical(key=_db_api_key())

    chunk_dir = CACHE_DIR / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    w0 = pd.Timestamp(DATA_START, tz=_et_tz())
    w1 = pd.Timestamp(params.oos_end, tz=_et_tz()) + pd.Timedelta(days=1)
    boundaries = list(pd.date_range(w0, w1 + pd.Timedelta(days=30), freq="30D"))
    rth_s = pd.Timestamp(params.rth_start + ":00").time()
    rth_e = pd.Timestamp(params.rth_end + ":00").time()

    def _clean(raw) -> pd.DataFrame:
        frame = raw.to_df()
        if isinstance(frame.index, pd.DatetimeIndex):
            frame = frame.reset_index()
        for col in ("ts_event", "ts"):
            if col in frame.columns:
                frame["ts"] = pd.to_datetime(frame[col], utc=True)
                break
        frame = frame[frame["ts"].notna()].copy()
        frame["ts"] = frame["ts"].dt.tz_convert(_et_tz())
        frame["open"] = frame["open"].astype(float)
        frame["high"] = frame["high"].astype(float)
        frame["low"] = frame["low"].astype(float)
        frame["close"] = frame["close"].astype(float)
        frame["volume"] = frame["volume"].fillna(0).astype(float)
        frame = frame[frame["ts"].dt.time.between(rth_s, rth_e)].copy()
        frame["date"] = frame["ts"].dt.date
        return frame[["ts", "date", "open", "high", "low", "close", "volume"]].sort_values("ts").reset_index(drop=True)

    chunks: list[Path] = []
    done = len(list(chunk_dir.glob("*.parquet")))
    total_chunks = max(1, len(boundaries) - 1)
    for lo, hi in zip(boundaries, boundaries[1:]):
        end = min(hi, w1)
        if end <= lo:
            continue
        cfile = chunk_dir / f"{lo.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.parquet"
        if cfile.exists():
            chunks.append(cfile)
            continue
        for attempt in range(params.fetch_retries):
            try:
                data = client.timeseries.get_range(
                    dataset=params.dataset,
                    schema="ohlcv-1m",
                    stype_in="continuous",
                    symbols=[params.symbol],
                    start=lo.strftime("%Y-%m-%d"),
                    end=end.strftime("%Y-%m-%d"),
                )
                out = _clean(data)
                out.to_parquet(cfile)
                chunks.append(cfile)
                done += 1
                print(f"  [{done}/{total_chunks}] {lo.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')} "
                      f"({len(out)} bars) -> {cfile.name}", flush=True)
                break
            except Exception as exc:  # noqa: BLE001 - retry transient 504/stream drops
                print(f"  retry {attempt+1}/{params.fetch_retries}: {lo.strftime('%Y-%m-%d')} ({str(exc)[:60]})", flush=True)
                if attempt == params.fetch_retries - 1:
                    raise
                _time.sleep(10 * (attempt + 1))

    print(f"concatenating {len(chunks)} cached chunks...", flush=True)
    frames = [pd.read_parquet(c) for c in chunks]
    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates(subset="ts", keep="last").sort_values("ts").reset_index(drop=True)
    out.to_parquet(cache)
    return out


def _resample(frame: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """Resample ET RTH 1-min bars to `minutes`-minute bars (aligned to 09:30 ET).

    Returns bar rows keyed by bar start `t` (ET). open=first 1m open, high=max,
    low=min, close=last, volume=sum.
    """
    f = frame.set_index("ts").sort_index()
    if minutes == 1:
        return frame.reset_index(drop=True)
    f = f.copy()
    secs = (f.index - f.index.normalize()).total_seconds()
    secs = np.asarray(secs, dtype=float)
    rth_off = 9 * 3600 + 30 * 60
    f["_bin"] = np.floor((secs - rth_off) / (minutes * 60)).astype(int)
    f["_bar_start"] = f.index.normalize() + pd.to_timedelta(rth_off + f["_bin"] * minutes * 60, unit="s")
    g = f.groupby(["_bar_start", "date"], sort=False)
    agg = g.agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).reset_index()
    agg = agg.sort_values("_bar_start").reset_index(drop=True)
    agg.rename(columns={"_bar_start": "t"}, inplace=True)
    return agg[["t", "date", "open", "high", "low", "close", "volume"]]


def load_intraday(params: StudyParams) -> dict[str, pd.DataFrame]:
    """Return {"1m": df, "15m": df} for the probe window (ET RTH bars)."""
    m1 = fetch_1m(params)
    one = m1[["ts", "date", "open", "high", "low", "close", "volume"]].rename(columns={"ts": "t"})
    fifteen = _resample(m1, params.exec_min)
    return {"1m": one, "15m": fifteen}
