"""Sparsity test: harvest + count 8-K repurchase-program announcements from EDGAR.

Counts independent buyback-authorization events across a multi-year window to
assess whether the Tier A signal is dense enough to pass the "too few events"
gate. Uses EDGAR full-text search paginated by calendar quarter, filtered to
Form 8-K, deduped by (CIK, accession).

Roadmap/spec ref: IA/buyback-timing-research-spec.md (feasibility / sparsity item).
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
from collections import Counter
from datetime import datetime, date

import requests

HEADERS = {"User-Agent": "Research research@example.com"}
BASE = "https://efts.sec.gov/LATEST/search-index"
QUERY = '"repurchase program"'


def quarters(start: date, end: date):
    """Yield (start, end) date pairs bounding each calendar quarter in range."""
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        qs = date(y, m, 1)
        if m == 12:
            qe = date(y + 1, 1, 1)
        else:
            qe = date(y, m + 1, 1)
        from datetime import timedelta
        qend = qe - timedelta(days=1)
        if qend >= start and qs <= end:
            yield (max(start, qs), min(end, qend))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def fetch_quarter(qs: date, qe: date) -> list[dict]:
    """Return 8-K repurchase-program hits in a quarter (single page)."""
    params = {
        "q": QUERY,
        "dateRange": "custom",
        "startdt": qs.isoformat(),
        "enddt": qe.isoformat(),
        "forms": "8-K",
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    r = requests.get(url, headers=HEADERS, timeout=40)
    r.raise_for_status()
    hits = r.json().get("hits", {}).get("hits", [])
    out = []
    for h in hits:
        s = h.get("_source", {})
        if s.get("form") == "8-K":
            out.append({
                "adsh": s.get("adsh"),
                "cik": s.get("ciks", [None])[0] if s.get("ciks") else None,
                "date": s.get("file_date"),
                "name": (s.get("display_names") or [""])[0],
                "items": s.get("items") or [],
                "desc": s.get("file_description") or "",
            })
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2023-01-01")
    p.add_argument("--end", default="2026-07-31")
    p.add_argument("--sleep", type=float, default=0.3)
    args = p.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    all_rows = []
    qmap = {}
    for qs, qe in quarters(start, end):
        try:
            rows = fetch_quarter(qs, qe)
        except Exception as e:
            print(f"quarter {qs}..{qe}: ERROR {e}")
            continue
        all_rows.extend(rows)
        qmap[qs.strftime("%Y-%m")] = len(rows)
        print(f"{qs}..{qe}: {len(rows)} 8-K repurchase-program hits")
        time.sleep(args.sleep)

    # dedup by (cik, adsh)
    seen = {}
    for r in all_rows:
        seen.setdefault((r["cik"], r["adsh"]), r)
    rows = list(seen.values())

    by_year = Counter((r["date"] or "")[:4] for r in rows if r.get("date"))
    by_items8101 = sum(1 for r in rows if "8.01" in (r["items"] or []))
    print("\n=== TOTAL unique 8-K repurchase-program filings ===")
    print(f"unique (cik,adsh): {len(rows)} (from {len(all_rows)} raw page hits)")
    print("by year:", dict(sorted(by_year.items())))

    # 8-K item 8.01 = new registrant event (often new buyback authorization/action)
    has_item = sum(1 for r in rows if r.get("items"))
    print(f"with item codes: {has_item}; with item 8.01: {by_items8101}")

    print("\nmonthly counts:")
    for m in sorted(qmap):
        print(f"  {m}: {qmap[m]}")

    # uniqueness within a CIK over time (one 8-K usually = one discrete authorization)
    cik_counts = Counter(r["cik"] for r in rows if r.get("cik"))
    multi = sum(1 for c, n in cik_counts.items() if n > 1)
    print(f"\ndistinct issuers: {len(cik_counts)} | issuers with >1 filing: {multi}")
    print(f"filings per issuer (top): {dict(cik_counts.most_common(8))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
