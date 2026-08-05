"""CIK -> ticker and S&P 500/600 membership mapping for the event set.

Uses EDGAR company submissions (free) for the current ticker, and an index
membership approach via the tickers' index attribution. Survivorship-bias note:
CIKs that no longer map to a current ticker (delisted/acquired/bankrupt) are
marked unmapped and excluded from the return computation; this is a documented
limitation of the bounded free-data study (see IA/buyback-timing-research-spec.md).
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

HEADERS = {"User-Agent": "Research research@example.com"}
SUBMISSIONS = "https://data.sec.gov/submissions/CIK{}.json"
CACHE: dict[str, dict] = {}


def _cik_pad(cik: str) -> str:
    return str(cik).zfill(10)


def company_ticker(cik: str) -> str | None:
    """Return the current ticker for a CIK, or None if not mapped."""
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
                ticker = tickers[0] if tickers else None
                out = {"name": d.get("name"), "ticker": ticker or None}
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
    """Add `ticker` column to the event frame via EDGAR company mapping."""
    df = events.copy()
    tickers = []
    for cik in df["cik"]:
        tk = company_ticker(cik)
        tickers.append(tk)
        # pace politely
        if len(tickers) % 20 == 0:
            print(f"  mapped {len(tickers)}/{len(df)}")
    df["ticker"] = tickers
    return df
