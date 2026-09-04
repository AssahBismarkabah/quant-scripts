"""Bar-close volume profile proxy for the ES value-area study."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_profile(day_1m: pd.DataFrame, bin_size: float = 0.25,
                    value_area_pct: float = 0.70) -> dict[str, float]:
    """Compute POC/VAH/VAL using the frozen one-minute-close proxy.

    Each bar's full volume is assigned to the bin containing its close. This is
    deliberately not presented as true trade-level volume-at-price.
    """
    if day_1m.empty:
        return {"poc": np.nan, "vah": np.nan, "val": np.nan}
    close = day_1m["close"].to_numpy(dtype=float)
    volume = day_1m["volume"].to_numpy(dtype=float)
    bins = np.floor(close / bin_size) * bin_size
    profile = pd.DataFrame({"bin_low": bins, "volume": volume}).groupby(
        "bin_low", as_index=False)["volume"].sum().sort_values("bin_low").reset_index(drop=True)
    if profile.empty or profile["volume"].sum() <= 0:
        return {"poc": np.nan, "vah": np.nan, "val": np.nan}
    lows = profile["bin_low"].to_numpy(dtype=float)
    vols = profile["volume"].to_numpy(dtype=float)
    poc_idx = int(np.argmax(vols))
    lo = hi = poc_idx
    accumulated = vols[poc_idx]
    target = vols.sum() * value_area_pct
    while accumulated < target and (lo > 0 or hi < len(lows) - 1):
        if lo == 0:
            hi += 1
        elif hi == len(lows) - 1:
            lo -= 1
        elif vols[hi + 1] >= vols[lo - 1]:
            hi += 1
        else:
            lo -= 1
        accumulated = vols[lo:hi + 1].sum()
    return {
        "poc": float(lows[poc_idx] + bin_size / 2),
        "vah": float(lows[hi] + bin_size),
        "val": float(lows[lo]),
    }
