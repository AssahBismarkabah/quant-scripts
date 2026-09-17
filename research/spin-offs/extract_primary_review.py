"""Extract primary-document evidence snippets for likely spin-off filings."""
from __future__ import annotations
import argparse, csv, re
from pathlib import Path
import requests

HEADERS = {"User-Agent": "quant-scripts research contact@example.com"}
TERMS = re.compile(r".{0,180}(?:spin[- ]off|spinoff|distribution|record date|ex[- ]date|first trad).{0,220}", re.I)

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--output", default="outputs/primary_evidence_review.csv")
    args = p.parse_args()
    with Path(args.input).open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("classification", "").startswith("LIKELY")]
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["company", "cik", "form", "filing_date", "document_url", "snippet", "review_status"]
    with requests.Session() as session, out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for row in rows:
            url = row.get("document_url", "")
            try:
                html = session.get(url, headers=HEADERS, timeout=40).text
                text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
                snippets = " || ".join(TERMS.findall(text)[:8])
                status = "PRIMARY REVIEW REQUIRED" if snippets else "NO RELEVANT PRIMARY TEXT"
            except requests.RequestException as exc:
                snippets, status = str(exc), "UNVERIFIABLE — FETCH ERROR"
            writer.writerow({"company": row.get("company"), "cik": row.get("cik"), "form": row.get("form"), "filing_date": row.get("filing_date"), "document_url": url, "snippet": snippets, "review_status": status})
    print(f"wrote {len(rows)} primary-document review rows to {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
