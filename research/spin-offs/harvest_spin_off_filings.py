"""Harvest timestamped SEC filing candidates for the spin-off feasibility audit.

This is an event-inventory tool only. It does not infer event dates, identify
forced sellers, calculate returns, or select trades.
"""

from __future__ import annotations

import argparse
import csv
import time
import urllib.parse
from datetime import date
from pathlib import Path

import requests

BASE = "https://efts.sec.gov/LATEST/search-index"
HEADERS = {"User-Agent": "quant-scripts research contact@example.com"}
FORMS = "8-K,10-12B,10"


def quarters(start: date, end: date):
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        qs = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        from datetime import timedelta

        qe = next_month - timedelta(days=1)
        if qe >= start and qs <= end:
            yield max(start, qs), min(end, qe)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def fetch(qs: date, qe: date, page_size: int = 100) -> list[dict]:
    params = {
        "q": '"spin-off" OR "spinoff"',
        "dateRange": "custom",
        "startdt": qs.isoformat(),
        "enddt": qe.isoformat(),
        "forms": FORMS,
        "from": 0,
        "size": page_size,
    }
    response = requests.get(
        BASE + "?" + urllib.parse.urlencode(params), headers=HEADERS, timeout=40
    )
    response.raise_for_status()
    hits = response.json().get("hits", {}).get("hits", [])
    rows = []
    for hit in hits:
        source = hit.get("_source", {})
        ciks = source.get("ciks") or []
        rows.append(
            {
                "accession": source.get("adsh"),
                "cik": ciks[0] if ciks else None,
                "form": source.get("form"),
                "filing_date": source.get("file_date"),
                "acceptance_datetime": source.get("acceptance_datetime"),
                "company": (source.get("display_names") or [""])[0],
                "description": source.get("file_description") or "",
                "items": ";".join(source.get("items") or []),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2010-01-01")
    parser.add_argument("--end", default="2026-09-17")
    parser.add_argument("--sleep", type=float, default=0.25)
    parser.add_argument("--output", default="outputs/filing_candidates.csv")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for qs, qe in quarters(date.fromisoformat(args.start), date.fromisoformat(args.end)):
        batch = fetch(qs, qe)
        rows.extend(batch)
        print(f"{qs}..{qe}: {len(batch)} filing hits")
        time.sleep(args.sleep)

    unique = {(row["cik"], row["accession"]): row for row in rows}
    fields = [
        "accession", "cik", "form", "filing_date", "acceptance_datetime",
        "company", "description", "items",
    ]
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(unique.values(), key=lambda row: (row["filing_date"] or "", row["company"])))
    print(f"wrote {len(unique)} unique filing candidates to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
