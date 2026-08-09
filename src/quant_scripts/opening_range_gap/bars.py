"""Combined NQ RTH 1-min bars for the opening-range / gap trio.

Loads the two owned Databento NQ RTH 1-min caches and concatenates them into
one series spanning 2013-11 .. 2026-08:

- research/ivamr/cache/NQ_n_0_1m.parquet          (2013-11 .. 2023-12)
- research/nq-vwap-pullback/cache/NQ_n_0_1m.parquet (2020-08 .. 2026-08)

The overlap (~339K rows) is byte-identical across both caches, so a concat with
drop_duplicates(subset="ts", keep="last") is lossless. No new Databento fetch is
required (see spec §6/§8). 1-min bars are then resampled to 5-min execution bars.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import StudyParams

ROOT = Path(__file__).resolve().parents[3]
ivi_cache = ROOT / "research" / "ivamr" / "cache" / "NQ_n_0_1m.parquet"
vwap_cache = ROOT / "research" / "nq-vwap-pullback" / "cache" / "NQ_n_0_1m.parquet"


def _et_tz():
    import zoneinfo

    return zoneinfo.ZoneInfo("America/New_York")


def load_combined(params: StudyParams) -> pd.DataFrame:
    """Return ET RTH 1-min bars (columns: ts, date, open, high, low, close, volume)
    combined from the two owned caches, deduped on ts and sorted."""
    if not (ivi_cache.exists() and vwap_cache.exists()):
        raise FileNotFoundError(
            f"owned 1-min caches not found:\n  {ivi_cache}\n  {vwap_cache}\n"
            f"Run make fetch under research/ivamr and research/nq-vwap-pullback first."
        )
    a = pd.read_parquet(ivi_cache)
    b = pd.read_parquet(vwap_cache)
    out = pd.concat([a, b], ignore_index=True)
    out = out.drop_duplicates(subset="ts", keep="last").sort_values("ts").reset_index(drop=True)
    out["ts"] = pd.to_datetime(out["ts"])
    return out


def _resample(frame: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """Resample ET RTH 1-min bars to `minutes`-minute bars aligned to 09:30 ET.

    Returns bar rows keyed by bar start `t` (ET): open=first 1m open, high=max,
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
    """Return {"1m": df, "5m": df} for the combined window (ET RTH bars)."""
    m1 = load_combined(params)
    one = m1[["ts", "date", "open", "high", "low", "close", "volume"]].rename(columns={"ts": "t"})
    five = _resample(m1, params.exec_min)
    return {"1m": one, "5m": five}
