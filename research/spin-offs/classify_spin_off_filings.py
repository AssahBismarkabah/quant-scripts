"""Conservatively classify SEC spin-off search hits by reading primary filings."""
from __future__ import annotations

import argparse
import csv
import re
import time
from pathlib import Path

import requests

HEADERS = {"User-Agent": "quant-scripts research contact@example.com"}
ARCHIVE = "https://www.sec.gov/Archives/edgar/data"
SPIN = re.compile(r"\b(spin[- ]off|spinoff|distribution of .* shares)\b", re.I)
DATES = re.compile(r"\b(record date|distribution date|ex[- ]date|first trade)\b", re.I)


def classify(row: dict, session: requests.Session) -> dict:
    accession = (row.get("accession") or "").replace("-", "")
    cik = (row.get("cik") or "").lstrip("0")
    base = f"{ARCHIVE}/{cik}/{accession}"
    result = {**row, "document_url": "", "classification": "REVIEW"}
    try:
        index = session.get(base + "/index.json", headers=HEADERS, timeout=40)
        index.raise_for_status()
        files = index.json().get("directory", {}).get("item", [])
        names = [x["name"] for x in files if x.get("name", "").lower().endswith((".htm", ".html"))]
        primary = next((x for x in names if "index" not in x.lower()), None)
        if not primary:
            result["classification"] = "UNVERIFIABLE — NO PRIMARY HTML"
            return result
        url = f"{base}/{primary}"
        response = session.get(url, headers=HEADERS, timeout=40)
        response.raise_for_status()
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", response.text))
        result["document_url"] = url
        result["classification"] = (
            "LIKELY SPIN-OFF — PRIMARY REVIEW REQUIRED" if SPIN.search(text) and DATES.search(text)
            else "SPIN-OFF MENTION — PRIMARY REVIEW REQUIRED" if SPIN.search(text)
            else "UNRELATED OR NOT CONFIRMED"
        )
    except requests.RequestException:
        result["classification"] = "UNVERIFIABLE — FETCH ERROR"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--output", default="outputs/filing_review_queue.csv")
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()
    with Path(args.input).open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    results = []
    with requests.Session() as session:
        for number, row in enumerate(rows, 1):
            results.append(classify(row, session))
            print(f"{number}/{len(rows)} {results[-1]['classification']}")
            time.sleep(args.sleep)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(results[0]) if results else []
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    print(f"wrote {len(results)} review rows to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
