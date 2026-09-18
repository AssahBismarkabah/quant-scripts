"""Freeze the B5-01 equity-ETF universe from the SSGA product data file.

Deterministic rule, applied before any price/discount inspection:
  US-listed SPDR ETFs with Total Net Assets below the B5_SMALL_AUM_USD
  threshold, excluding leveraged/inverse products.

Usage: build_universe.py PRODUCT_XLSX OUT_CSV [--max-aum-usd 400000000]
"""
from __future__ import annotations

import argparse
import re

import pandas as pd


def parse_aum(raw: object) -> float | None:
    text = str(raw).replace("$", "").replace(",", "").strip()
    m = re.fullmatch(r"([0-9.]+)\s*([BMK]?)", text)
    if not m:
        return None
    mult = {"B": 1e9, "M": 1e6, "K": 1e3}.get(m.group(2), 1.0)
    return float(m.group(1)) * mult


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_xlsx")
    parser.add_argument("out_csv")
    parser.add_argument("--max-aum-usd", type=float, default=4e8)
    args = parser.parse_args()

    df = pd.read_excel(args.product_xlsx, header=None)
    body = df.iloc[3:].copy()
    tickers = body[1].astype(str).str.replace("\u00ae", "", regex=False).str.strip()
    names = body[2].astype(str)
    aum = body[22].map(parse_aum)

    rows = []
    for i in range(len(body)):
        tkr = tickers.iloc[i]
        name = str(names.iloc[i])
        size = aum.iloc[i]
        if pd.isna(size) or size >= args.max_aum_usd:
            continue
        if tkr in ("nan", "") or pd.isna(tkr):
            continue
        low = name.lower()
        if any(w in low for w in ("leveraged", "inverse", "2x", "3x", "-1x")):
            continue
        rows.append({
            "ticker": tkr,
            "name": name,
            "aum_usd": size,
            "cusip": str(body[4].iloc[i]),
            "inception": str(body[5].iloc[i]),
        })

    out = pd.DataFrame(rows).sort_values("aum_usd")
    out.to_csv(args.out_csv, index=False)
    print(f"frozen universe: {len(out)} funds below {args.max_aum_usd:,.0f} USD")
    print(out.head(25).to_string(index=False))


if __name__ == "__main__":
    main()
