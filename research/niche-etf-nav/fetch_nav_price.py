"""Fetch SSGA NAV history (navhist) and premium/discount history (pdhist)
XLSX files for every ticker in the frozen B5-01 universe, then build a
combined daily table with the official premium/discount.

This is a data-census step: it computes descriptive premium statistics only.
It computes no strategy returns and selects no trades.

Usage: fetch_nav_price.py UNIVERSE_CSV RAW_DIR OUT_PARQUET
"""
from __future__ import annotations

import argparse
import io
import time
from pathlib import Path

import pandas as pd
import requests


BASE = "https://www.ssga.com/library-content/products/fund-data/etfs/us/{kind}-us-en-{ticker}.xlsx"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def fetch_one(ticker: str, kind: str, raw_dir: Path) -> bytes | None:
    path = raw_dir / f"{kind}-{ticker}.xlsx"
    if path.exists() and path.stat().st_size > 5000:
        return path.read_bytes()
    url = BASE.format(kind=kind, ticker=ticker.lower())
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException:
        return None
    if r.status_code != 200 or len(r.content) < 5000 or r.content[:2] != b"PK":
        return None
    path.write_bytes(r.content)
    return r.content


def parse_hist(data: bytes, value_cols: list[str]) -> pd.DataFrame:
    xl = pd.ExcelFile(io.BytesIO(data))
    df = xl.parse(xl.sheet_names[0], header=None)
    for i in range(min(12, len(df))):
        vals = [str(v).strip() for v in df.iloc[i].tolist()]
        if "Date" in vals:
            for col in value_cols:
                if col in vals:
                    hdr = [str(v).strip() for v in df.iloc[i].tolist()]
                    body = df.iloc[i + 1:].copy()
                    body.columns = hdr
                    body = body[pd.to_datetime(body["Date"], errors="coerce").notna()]
                    body["Date"] = pd.to_datetime(body["Date"])
                    out = body[["Date", col]].copy()
                    out[col] = pd.to_numeric(out[col], errors="coerce")
                    return out.dropna().rename(columns={col: col.lower().replace(" ", "_").replace("/", "_")})
    raise ValueError("no Date/value header found")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("universe_csv")
    parser.add_argument("raw_dir")
    parser.add_argument("out_parquet")
    args = parser.parse_args()

    uni = pd.read_csv(args.universe_csv)
    uni = uni[uni["ticker"].notna()]
    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    failures = []
    for n, row in enumerate(uni.itertuples(index=False), 1):
        ticker = str(row.ticker).strip()
        nav_b = fetch_one(ticker, "navhist", raw_dir)
        px_b = fetch_one(ticker, "pdhist", raw_dir)
        if nav_b is None or px_b is None:
            failures.append(ticker)
            continue
        try:
            nav = parse_hist(nav_b, ["NAV"])
            pd_series = parse_hist(px_b, ["Premium/Discount"])
            merged = nav.merge(pd_series, on="Date", how="inner")
        except (ValueError, KeyError):
            failures.append(ticker)
            continue
        if merged.empty:
            failures.append(ticker)
            continue
        merged["ticker"] = ticker
        frames.append(merged)
        if n % 10 == 0:
            print(f"{n}/{len(uni)} fetched", flush=True)
        time.sleep(0.3)

    if frames:
        all_t = pd.concat(frames, ignore_index=True)
        all_t = all_t.rename(columns={"premium_discount": "premium_reported"})
        all_t.to_parquet(args.out_parquet, index=False)
        print(f"rows: {len(all_t)} across {all_t.ticker.nunique()} funds")
    else:
        print("no data fetched")
    print("failures:", ",".join(failures) if failures else "none")


if __name__ == "__main__":
    main()
