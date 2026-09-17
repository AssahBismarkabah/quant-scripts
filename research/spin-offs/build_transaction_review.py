"""Create a provisional transaction review queue from classified SEC filings."""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


def issuer_key(company: str) -> str:
    """Strip tickers/CIK so amendments from one issuer cluster together."""
    value = re.sub(r"\s*\(.*?CIK.*?\)", "", company, flags=re.I)
    value = re.sub(r"\s*\([^)]*\)", "", value)
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--output", default="outputs/transaction_review_queue.csv")
    args = parser.parse_args()
    with Path(args.input).open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    groups = defaultdict(list)
    for row in rows:
        if row.get("classification", "").startswith("UNRELATED"):
            continue
        groups[(row.get("cik", ""), issuer_key(row.get("company", "")))].append(row)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["provisional_transaction_id", "issuer_key", "cik", "filing_count", "filing_dates", "filing_urls", "status"]
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for number, ((cik, key), filings) in enumerate(sorted(groups.items()), 1):
            writer.writerow({
                "provisional_transaction_id": f"SPIN-REVIEW-{number:03d}",
                "issuer_key": key,
                "cik": cik,
                "filing_count": len(filings),
                "filing_dates": ";".join(sorted({r.get("filing_date", "") for r in filings})),
                "filing_urls": ";".join(r.get("document_url", "") for r in filings),
                "status": "PROVISIONAL — VERIFY PARENT/SPINCO AND GOVERNING DOCUMENT",
            })
    print(f"wrote {len(groups)} provisional transaction groups to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
