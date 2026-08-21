import datetime as dt
import os
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import cpu_count

import pandas as pd
import requests

PAIRS = ["BTCUSDT", "ETHUSDT"]
SCHEMAS = ["aggTrades", "bookDepth"]
START = dt.date(2023, 1, 1)
END = dt.date(2026, 6, 30)
BASE = "https://data.binance.vision/data/futures/um/daily"
CACHE = "research/microstructure/cache"
ZIPS = os.path.join(CACHE, "zips")


def dates():
    d = START
    while d <= END:
        yield d
        d += dt.timedelta(days=1)


def download_zip(pair, schema, day):
    os.makedirs(ZIPS, exist_ok=True)
    out = os.path.join(ZIPS, f"{pair}-{schema}-{day.isoformat()}.zip")
    if os.path.exists(out):
        return out
    url = f"{BASE}/{schema}/{pair}/{pair}-{schema}-{day.isoformat()}.zip"
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        return f"MISSING {day} {pair} {schema} HTTP {r.status_code}"
    with open(out, "wb") as f:
        f.write(r.content)
    return out


def unzip_to_parquet(pair, schema, day):
    zip_path = os.path.join(ZIPS, f"{pair}-{schema}-{day.isoformat()}.zip")
    out = os.path.join(CACHE, f"{pair}-{schema}-{day.isoformat()}.parquet")
    if os.path.exists(out):
        return out
    try:
        with zipfile.ZipFile(zip_path) as z:
            name = z.namelist()[0]
            df = pd.read_csv(z.open(name))
    except Exception as e:
        return f"ERR {day} {pair} {schema}: {e}"
    if schema == "aggTrades":
        df = df[["agg_trade_id", "price", "quantity", "transact_time", "is_buyer_maker"]]
        df["ts"] = pd.to_datetime(df["transact_time"], unit="ms", utc=True)
    else:
        df["ts"] = pd.to_datetime(df["timestamp"], utc=True)
    df.to_parquet(out)
    return out


def main():
    os.makedirs(ZIPS, exist_ok=True)
    jobs = [(p, s, d) for p in PAIRS for s in SCHEMAS for d in dates()]
    print(f"Phase A: downloading {len(jobs)} zips...")
    missing = 0
    with ThreadPoolExecutor(max_workers=24) as ex:
        for i, res in enumerate(ex.map(lambda j: download_zip(*j), jobs)):
            if isinstance(res, str) and res.startswith("MISSING"):
                missing += 1
                print(res)
            if (i + 1) % 200 == 0:
                print(f"  {i+1}/{len(jobs)}", flush=True)
    print(f"Phase A done, missing={missing}")

    print(f"Phase B: unzip+parquet ({len(jobs)} files, {cpu_count()} workers)...")
    failed = 0
    with ProcessPoolExecutor(max_workers=max(4, cpu_count() // 2)) as ex:
        for i, res in enumerate(ex.map(lambda j: unzip_to_parquet(*j), jobs)):
            if isinstance(res, str) and res.startswith("ERR"):
                failed += 1
                print(res)
            if (i + 1) % 200 == 0:
                print(f"  {i+1}/{len(jobs)}", flush=True)
    print(f"Phase B done, failed={failed}")


if __name__ == "__main__":
    main()