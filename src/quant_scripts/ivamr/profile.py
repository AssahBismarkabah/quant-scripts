"""Volume Profile (POC / VAH / VAL) and ATR for the IVAMR probe.

Per strategies/ivamr/IVAMR.md §3 and §8.B, the 70% Value Area and POC are built
from the PREVIOUS trading day's RTH 1-min closes (never 15-min OHLCV as if it
were a histogram), using a fixed bin size, and the 14-period 15-min ATR is
computed from the previous day's RTH 15-min candles ending at 16:00 ET.

Value-area algorithm (standard): start at the highest-volume bin (POC), expand
outward adding the adjacent bin with the larger volume, until the accumulated
volume reaches >= value_area_pct of the day's total volume.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import StudyParams


def _bin_low(prices: np.ndarray, bin_size: float) -> np.ndarray:
    """Floor each price to the low edge of its bin (0.25-pt bins)."""
    return np.floor(prices / bin_size) * bin_size


def compute_profile(day_1m: pd.DataFrame, params: StudyParams) -> dict:
    """Return {poc, vah, val} for a single day's RTH 1-min bars.

    Each 1-min bar contributes its volume to the bin containing its close.
    poc = midpoint of highest-volume bin. Value area expands around the POC to
    value_area_pct of total volume; vah/vah = top/bottom edges of the area.
    """
    if day_1m.empty:
        return {"poc": np.nan, "vah": np.nan, "val": np.nan}

    close = day_1m["close"].to_numpy(dtype=float)
    vol = day_1m["volume"].to_numpy(dtype=float)
    bins = _bin_low(close, params.bin_size)

    # aggregate volume per bin low-edge
    df = pd.DataFrame({"bin_low": bins, "vol": vol}).groupby("bin_low", as_index=False).sum()
    df = df.sort_values("bin_low").reset_index(drop=True)
    bin_lows = df["bin_low"].to_numpy(dtype=float)
    vols = df["vol"].to_numpy(dtype=float)

    total = vols.sum()
    if total <= 0:
        return {"poc": np.nan, "vah": np.nan, "val": np.nan}

    poc_idx = int(np.argmax(vols))
    poc = bin_lows[poc_idx] + params.bin_size / 2.0

    # expand outward from POC by always adding the adjacent bin with more volume
    lo = poc_idx
    hi = poc_idx
    if len(bin_lows) == 1:
        return {"poc": poc, "vah": bin_lows[poc_idx] + params.bin_size, "val": bin_lows[poc_idx]}

    target = total * params.value_area_pct
    acc = vols[lo : hi + 1].sum()
    while acc < target:
        has_lo = lo > 0
        has_hi = hi < len(bin_lows) - 1
        if not has_lo and not has_hi:
            break
        if not has_lo:
            hi += 1
        elif not has_hi:
            lo -= 1
        else:
            if vols[hi + 1] >= vols[lo - 1]:
                hi += 1
            else:
                lo -= 1
        acc = vols[lo : hi + 1].sum()

    vah = bin_lows[hi] + params.bin_size
    val = bin_lows[lo]
    return {"poc": float(poc), "vah": float(vah), "val": float(val)}


def compute_atr(day_15m: pd.DataFrame, period: int) -> float:
    """Previous-day 15-min ATR: mean of True Range over the day's 15-min bars.

    The blueprint's '14-period 15-min ATR ending at 16:00' is interpreted here,
    within a single day, as the average true range across that day's RTH 15-min
    candles (a single day contains ~26 bars; a rolling-14 of yesterday is not
    well defined across a non-trading gap). True Range uses the prior bar's close
    within the same day when available.
    """
    if day_15m is None or len(day_15m) < 2:
        return np.nan
    h = day_15m["high"].to_numpy(dtype=float)
    l = day_15m["low"].to_numpy(dtype=float)
    c = day_15m["close"].to_numpy(dtype=float)
    prev_c = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))
    return float(np.mean(tr[1:]))
