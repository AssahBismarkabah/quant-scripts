"""Harvest + classify 10b5-1 repurchase-adoption 8-K events for the probe.

Usage:
  .venv/bin/python research/10b5-1-timing/harvest_adoptions.py --start 2025-07-01 --end 2026-07-31

Writes classified events to events/adoption_events.parquet with CIK->ticker mapping.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from quant_scripts.ten_b5_one_timing.edgar import harvest, to_events  # noqa: E402
from quant_scripts.ten_b5_one_timing.mapping import map_events  # noqa: E402

RESEARCH = ROOT / "research" / "10b5-1-timing"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2025-07-01")
    ap.add_argument("--end", default="2026-07-31")
    ap.add_argument("--max-docs", type=int, default=None)
    ap.add_argument("--sleep", type=float, default=0.4)
    ap.add_argument("--no-classify", dest="classify", action="store_false", default=True)
    ap.add_argument("--dry-run", action="store_true", help="harvest+classify, print, do not save")
    args = ap.parse_args()

    (RESEARCH / "events").mkdir(parents=True, exist_ok=True)
    cache_path = str(RESEARCH / "events" / "adoption_classify_cache.json")

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    print(f"harvesting 8-K '10b5-1' repurchase filings {start}..{end} (classify={args.classify}, cache={cache_path})")
    rows = harvest(
        start,
        end,
        classify_docs=args.classify,
        max_docs=args.max_docs,
        sleep=args.sleep,
        cache_path=cache_path,
    )

    n_adopt = sum(1 for r in rows if r.get("is_adoption"))
    print(f"\nraw rows: {len(rows)} | classified-adoptions: {n_adopt}")
    for r in rows:
        if r.get("is_adoption"):
            print(f"  ADOPT {r['date']} {r['cik']} {(r.get('name') or '')[:50]} [{r.get('class_reason')}]")

    if args.dry_run:
        return 0

    events = to_events(rows, only_adoptions=True)
    df = pd.DataFrame(events)
    (RESEARCH / "events").mkdir(parents=True, exist_ok=True)
    if df.empty:
        print("no adoption events found; writing empty frame (nothing to map)")
        df.to_parquet(RESEARCH / "events" / "adoption_events.parquet")
        return 0
    # map CIK -> ticker
    mapped = map_events(df)
    mapped.to_parquet(RESEARCH / "events" / "adoption_events.parquet")
    n_mapped = int(mapped["ticker"].notna().sum())
    print(f"\nevents: {len(mapped)} | ticker-mapped: {n_mapped}")
    print("saved:", RESEARCH / "events" / "adoption_events.parquet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
