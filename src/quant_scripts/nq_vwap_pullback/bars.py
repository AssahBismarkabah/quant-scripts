"""Databento intraday bars for the NQ VWAP-pullback probe.

Fetches 1-minute OHLCV for the continuous NQ contract, converts timestamps to
ET, filters to RTH (09:30..16:00 ET), computes the session-anchored VWAP from
the 1-minute base, and resamples to 5-min (execution) and 15-min (trend) bars.
Caches to research/nq-vwap-pullback/cache/ (parquet, resumable).

VWAP correctness (spec gate 6): VWAP is computed strictly from bars whose
session-relative timestamp <= the bar in question (running within the day),
anchored to the 09:30 ET open. It is defined on the 1-min base and carried
onto the resampled bars at the bar's close, so no future information leaks.
"""

from __future__ import annotations

from datetime import datetime, time, timezone
from pathlib import Path

import os

import numpy as np
import pandas as pd

from .config import StudyParams

ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = ROOT / "research" / "nq-vwap-pullback" / "cache"


def _db_api_key() -> str:
    """Read DATABENTO_API_KEY from the repo ROOT .env (matches repo convention)."""
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


def _et_tz():
    try:
        import zoneinfo

        return zoneinfo.ZoneInfo("America/New_York")
    except Exception:  # pragma: no cover - fallback fixed offset (EDT)
        return timezone.utc


def fetch_1m(params: StudyParams) -> pd.DataFrame:
    """Fetch + cache 1-minute OHLCV for the full window; return ET RTH 1-min bars.

    Returns columns: ts (ET, tz-aware), date, open, high, low, close, volume.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / f"{params.symbol.replace('.', '_')}_1m.parquet"
    if cache.exists():
        return pd.read_parquet(cache)

    import databento as db

    client = db.Historical(key=_db_api_key())

    # Fetch in ~30-day chunks so each request completes within Databento's
    # server gateway timeout (90-day chunks kept 504ing on high-volume NQ
    # periods). Chunked fetch is resumable and a failed chunk does not discard
    # earlier work; per-chunk retry tolerates transient 504/streaming drops.
    # The final concatenation is identical to a single get_range call.
    import time as _time

    chunk_dir = CACHE_DIR / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    w0 = pd.Timestamp(params.is_start, tz=_et_tz())
    w1 = pd.Timestamp(params.oos_end, tz=_et_tz())
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
    for lo, hi in zip(boundaries, boundaries[1:]):
        # clamp query end to the study window (dataset may end before w1+30D)
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
                break
            except Exception as exc:  # noqa: BLE001 - retry transient 504/stream drops
                if attempt == params.fetch_retries - 1:
                    raise
                _time.sleep(10 * (attempt + 1))

    frames = [pd.read_parquet(c) for c in chunks]
    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates(subset="ts", keep="last").sort_values("ts").reset_index(drop=True)
    out.to_parquet(cache)
    return out


def _running_vwap(day_rows: pd.DataFrame) -> np.ndarray:
    """Session-anchored running VWAP over 1-min bars of one day (in time order).

    VWAP at bar i = sum(typical*vol)[0..i] / sum(vol)[0..i], anchored at the
    session open (first RTH bar of the day).
    """
    typp = (day_rows["high"] + day_rows["low"] + day_rows["close"]) / 3.0
    pv = typp * day_rows["volume"]
    cv = day_rows["volume"].cumsum()
    cpv = pv.cumsum()
    vwap = np.where(cv > 0, cpv / np.maximum(cv, 1e-12), np.nan)
    # forward-fill early bars where no volume yet
    out = pd.Series(vwap).ffill().to_numpy()
    return out


def _resample(frame: pd.DataFrame, minutes: int, cols) -> pd.DataFrame:
    """Resample ET RTH 1-min bars to `minutes`-minute bars (aligned to RTH open).

    Returns bar rows keyed by bar start time `t` (ET). `open`=first 1m open,
    high=max, low=min, close=last, volume=sum, vwap=value at bar close.
    """
    f = frame.set_index("ts").sort_index()
    if minutes == 1:
        return frame.reset_index(drop=True)
    # create RTH-anchored bins: bar k starts at 09:30 + k*minutes
    f = f.copy()
    secs = (f.index - f.index.normalize()).total_seconds()
    # RTH start offset in seconds (09:30)
    rth_off = 9 * 3600 + 30 * 60
    f["_bin"] = (np.floor((secs - rth_off) / (minutes * 60))).astype(int)
    f["_bar_start"] = f.index.normalize() + pd.to_timedelta(rth_off + f["_bin"] * minutes * 60, unit="s")
    g = f.groupby(["_bar_start", "date"], sort=False)
    agg = g.agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
        vwap=("vwap", "last"),
    ).reset_index()
    agg = agg.sort_values("_bar_start").reset_index(drop=True)
    agg.rename(columns={"_bar_start": "t"}, inplace=True)
    return agg[["t", "date", "open", "high", "low", "close", "volume", "vwap"]]


def load_intraday(params: StudyParams) -> dict[str, pd.DataFrame]:
    """Return {"1m": df, "5m": df, "15m": df} with session-anchored VWAP attached.

    VWAP is computed once on the 1-min base, then carried onto the 5m and 15m
    bars (as of each bar's close). 1m rows include the running vwap too.
    """
    m1 = fetch_1m(params)
    # attach running vwap per day
    m1["vwap"] = np.nan
    for d, grp in m1.groupby("date", sort=True):
        m1.loc[grp.index, "vwap"] = _running_vwap(grp.sort_values("ts"))
    m1 = m1[m1["vwap"].notna()].reset_index(drop=True)

    one = m1[["ts", "date", "open", "high", "low", "close", "volume", "vwap"]].rename(columns={"ts": "t"})
    five = _resample(m1, params.exec_min, None)
    fifteen = _resample(m1, params.trend_min, None)
    return {"1m": one, "5m": five, "15m": fifteen}
