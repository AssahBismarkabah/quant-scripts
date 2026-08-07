"""Finalize the adoption event set from the classification cache (no re-fetch).

The EDGAR search step is fast; document re-fetching is the slow part and it is
already cached. This re-runs only the search, merges in the cached per-adsh
classifications, and writes the adoption events (with CIK->ticker mapping).

Sparsity read: the bounded probe classifies ~3 genuine issuer 10b5-1 repurchase-
plan adoptions out of ~730+ candidate 8-Ks — far below the pre-registered
>=30-event sparsity gate. This confirms sparsity is real (not a classifier bug):
the rejection reasons are dominated by officer/director 10b5-1 SALES plans,
financing/underwriting docs citing 10b5-1, and incidental rule mentions.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from quant_scripts.ten_b5_one_timing.edgar import search_quarter, _quarters, _cik_pad  # noqa: E402
from quant_scripts.ten_b5_one_timing.mapping import map_events  # noqa: E402

RESEARCH = ROOT / "research" / "10b5-1-timing"


def load_cache() -> dict:
    p = RESEARCH / "events" / "adoption_classify_cache.json"
    return json.loads(p.read_text()) if p.exists() else {}


def main() -> int:
    start = date.fromisoformat("2025-07-01")
    end = date.fromisoformat("2026-07-31")
    cache = load_cache()

    # fast search pass (no doc fetch)
    raw: dict[tuple, dict] = {}
    for qs, qe in _quarters(start, end):
        for r in search_quarter(qs, qe):
            raw[(r["cik"], r["adsh"])] = r
    print(f"search rows: {len(raw)} | cached docs: {len(cache)}")

    events = []
    for key, r in raw.items():
        cik, adsh = key
        rec = cache.get(adsh)
        if not rec or not rec.get("is_adoption"):
            continue
        d = r.get("date")
        events.append(
            {
                "cik": cik,
                "adsh": adsh,
                "company": (r.get("name") or "").split("(")[0].strip(),
                "event_date": d,
                "item_801": "8.01" in (r.get("items") or []),
                "class_reason": rec.get("class_reason", ""),
            }
        )

    df = pd.DataFrame(events)
    (RESEARCH / "events").mkdir(parents=True, exist_ok=True)
    if df.empty:
        print("no adoption events -> sparsity gate fails (0 >= 30: False)")
        df.to_parquet(RESEARCH / "events" / "adoption_events.parquet")
        return 0

    df["event_date"] = pd.to_datetime(df["event_date"])
    mapped = map_events(df)
    mapped.to_parquet(RESEARCH / "events" / "adoption_events.parquet")
    n_map = int(mapped["ticker"].notna().sum())
    print(f"\nadoption events: {len(mapped)} | ticker-mapped: {n_map}")
    print("saved:", RESEARCH / "events" / "adoption_events.parquet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
