"""Fetch Bitcoin MVRV + market-cap data from the Coin Metrics Community API.

Free, keyless, non-commercial. Downloads the daily BTC series for
CapMVRVCur (MVRV ratio) and CapMrktCurUSD (market cap) from 2010 to present,
writes a single parquet to research/bitcoin-mvrv/cache/mvrv.parquet, and a
manifest.json describing source + coverage so a re-run can skip if present.

Usage: .venv/bin/python research/bitcoin-mvrv/fetch_mvrv_data.py
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "research" / "bitcoin-mvrv" / "cache"
OUT = CACHE / "mvrv.parquet"
MANIFEST = CACHE / "manifest.json"

BASE = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
METRICS = "CapMVRVCur,CapMrktCurUSD"
SUPPLY_URL = "https://api.blockchain.info/charts/total-bitcoins?timespan=all&format=json"
ASSET = "btc"
FREQ = "1d"
START = "2009-01-01"
PAGE_SIZE = 10000


def fetch_series() -> list[dict]:
    rows: list[dict] = []
    url = (
        f"{BASE}?assets={ASSET}&metrics={METRICS}&frequency={FREQ}"
        f"&start_time={START}&page_size={PAGE_SIZE}"
    )
    page = 0
    while True:
        r = requests.get(url, timeout=120)
        if r.status_code != 200:
            raise SystemExit(f"Coin Metrics error {r.status_code}: {r.text[:300]}")
        payload = r.json()
        data = payload.get("data", [])
        rows = data + rows  # pages go backwards in time as token advances
        nxt = payload.get("next_page_token")
        page += 1
        if not nxt:
            break
        url = (
            f"{BASE}?assets={ASSET}&metrics={METRICS}&frequency={FREQ}"
            f"&start_time={START}&page_size={PAGE_SIZE}&next_page_token={nxt}"
        )
        time.sleep(0.4)
        if page % 25 == 0:
            print(f"  fetched {len(rows):,} rows after {page} pages")
    return rows


def fetch_supply() -> pd.Series:
    """Circulating BTC supply from Blockchain.info (keyless). Indexed by day."""
    r = requests.get(SUPPLY_URL, timeout=120)
    if r.status_code != 200:
        raise SystemExit(f"Blockchain.info supply error {r.status_code}: {r.text[:200]}")
    vals = r.json()["values"]
    idx = pd.to_datetime([v["x"] for v in vals], unit="s")
    ser = pd.Series([v["y"] for v in vals], index=idx)
    # forward-fill to daily grid
    ser = ser.resample("1D").ffill()
    return ser


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and MANIFEST.exists():
        print(f"cache already present: {OUT}")
        return 0

    print(f"fetching {ASSET} {METRICS} {FREQ} from {START} ...")
    rows = fetch_series()
    if not rows:
        raise SystemExit("no data returned")
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time").sort_index()
    for col in [m for m in METRICS.split(",") if m in df.columns]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # recover realized cap for integrity/sanity only (not used in the DCA)
    df["CapRealUSD"] = df["CapMrktCurUSD"] / df["CapMVRVCur"]
    # USD price = market cap / circulating supply (supply from Blockchain.info)
    supply = fetch_supply()
    if supply.index.tz is None:
        supply.index = supply.index.tz_localize("UTC")
    df["supply"] = supply.reindex(df.index).ffill()
    df["price"] = df["CapMrktCurUSD"] / df["supply"]
    df.to_parquet(OUT)
    manifest = {
        "source": "Coin Metrics Community API (free, keyless) + Blockchain.info (supply)",
        "endpoint": BASE,
        "asset": ASSET,
        "metrics": METRICS.split(","),
        "frequency": FREQ,
        "start_time": START,
        "coverage": {
            "first": df.index.min().isoformat(),
            "last": df.index.max().isoformat(),
            "rows": int(len(df)),
            "nan_price": int(df["price"].isna().sum()),
        },
        "fetched_utc": datetime.now(timezone.utc).isoformat(),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"rows: {len(df):,}  first={manifest['coverage']['first']}  "
          f"last={manifest['coverage']['last']}  nan_price={manifest['coverage']['nan_price']}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
