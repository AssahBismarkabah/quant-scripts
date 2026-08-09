"""Acquire free inputs for the V3 (tail-overlay short-vol) probe.

CBOE publishes daily history for its volatility indices on a fast public CDN
(no key, no paywall). We use these to build the term-structure / stress signal
for the short-vol tail overlay:
  - VIX    (30-day implied vol)
  - VIX3M  (3-month implied vol)  -> term-structure slope  VIX - VIX3M
  - VIX9D  (9-day implied vol)    -> short-term tension     VIX9D / VIX
All from https://cdn.cboe.com/api/global/us_indices/daily_prices/<ID>_History.csv

Short-vol instrument: SVXY (Yahoo, already cached).
Realized underlying / drawdown: SPY (Yahoo, already cached).

Outputs (raw, gitignored): cache/VIX.csv, cache/VIX3M.csv, cache/VIX9D.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

CACHE = Path(__file__).resolve().parent / "cache"
BASE = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{id}_History.csv"
IDS = ["VIX", "VIX3M", "VIX9D"]
HEADERS = {"User-Agent": "Mozilla/5.0"}


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    for sid in IDS:
        r = requests.get(BASE.format(id=sid), headers=HEADERS, timeout=40)
        r.raise_for_status()
        path = CACHE / f"{sid}.csv"
        path.write_text(r.text, encoding="utf-8")
        df = pd.read_csv(path)
        print(f"{sid}: {len(df)} rows, cols {list(df.columns)}, "
              f"first date {df['DATE'].iloc[0]}, last {df['DATE'].iloc[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
