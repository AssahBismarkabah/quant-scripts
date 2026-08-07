"""CIK -> ticker mapping for the 10b5-1 event set (via EDGAR company submissions)."""

from __future__ import annotations

import time

import pandas as pd
import requests

HEADERS = {"User-Agent": "Research research@example.com"}
SUBMISSIONS = "https://data.sec.gov/submissions/CIK{}.json"
CACHE: dict[str, dict] = {}


def _cik_pad(cik: str) -> str:
    return str(cik).zfill(10)


def company_ticker(cik: str) -> str | None:
    key = _cik_pad(cik)
    if key in CACHE:
        return CACHE[key].get("ticker")
    out = {}
    for attempt in range(3):
        try:
            r = requests.get(SUBMISSIONS.format(key), headers=HEADERS, timeout=40)
            if r.status_code == 200:
                d = r.json()
                tickers = d.get("tickers") or []
                out = {"name": d.get("name"), "ticker": tickers[0] if tickers else None}
                break
            elif r.status_code == 404:
                out = {"name": None, "ticker": None}
                break
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1.0 + attempt)
    CACHE[key] = out
    return out.get("ticker")


def map_events(events: pd.DataFrame) -> pd.DataFrame:
    df = events.copy()
    tickers = []
    for cik in df["cik"]:
        tickers.append(company_ticker(cik))
        if len(tickers) % 20 == 0:
            print(f"  mapped {len(tickers)}/{len(df)}")
    df["ticker"] = tickers
    return df
