"""CLI: dry-run launch reconstruction for one UTC day (spec step 1 half-step).

Usage: python -m quant_scripts.meme_launch_filter dry-run --date 2026-09-14 [--sample 300]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import time

from .config import OUTPUT_DIR, PUMP_PROGRAM, DEFAULT_SAMPLE
from .helius import HeliusClient
from .launches import parse_create


def day_bounds_utc(date_str: str) -> tuple[int, int]:
    day = dt.date.fromisoformat(date_str)
    start = int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp())
    return start, start + 86_400

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["dry-run"])
    parser.add_argument("--date", required=True, help="UTC date, YYYY-MM-DD")
    parser.add_argument("--sample", type=int, default=DEFAULT_SAMPLE)
    args = parser.parse_args()

    from .config import helius_api_key

    client = HeliusClient(api_key=helius_api_key())
    start, end = day_bounds_utc(args.date)
    out_dir = OUTPUT_DIR / args.date
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[dry-run] scanning {PUMP_PROGRAM} signatures for UTC {args.date} ...")
    signatures: list[dict] = []
    before = None
    while True:
        batch = client.get_signatures_for_address(PUMP_PROGRAM, before=before, limit=1000)
        if not batch:
            break
        signatures.extend(batch)
        oldest = batch[-1]
        before = oldest.get("signature")
        block_time = oldest.get("blockTime")
        print(f"  signatures so far: {len(signatures)} (oldest blockTime {block_time})")
        if block_time is not None and block_time < start:
            break
        if len(batch) < 1000:
            break

    in_day = [
        s for s in signatures
        if s.get("blockTime") is not None and start <= s["blockTime"] < end
    ]
    print(f"  total signatures in window: {len(in_day)}")

    sample = random.Random(42).sample(in_day, min(args.sample, len(in_day)))
    print(f"  classifying sample of {len(sample)} transactions ...")
    counts = {"create": 0, "other_or_unparsed": 0}
    create_records = []
    raw_create_examples = []
    for i, sig_info in enumerate(sample):
        signature = sig_info["signature"]
        tx = client.get_transaction(signature)
        record = parse_create(tx, signature) if tx else None
        if record is not None:
            counts["create"] += 1
            create_records.append(record.__dict__)
            if len(raw_create_examples) < 5:
                accounts = (((tx.get("transaction") or {}).get("message") or {}).get("instructions") or [])
                for ins in accounts:
                    if ins.get("programId") == PUMP_PROGRAM:
                        raw_create_examples.append(
                            {"signature": signature, "instruction_keys": list(ins.keys()),
                             "accounts": ins.get("accounts")}
                        )
                        break
        else:
            counts["other_or_unparsed"] += 1
        if (i + 1) % 25 == 0:
            print(f"    {i + 1}/{len(sample)} classified (calls so far: {client.calls})")

    create_ratio = counts["create"] / max(1, sum(counts.values()))
    estimated_creates = round(create_ratio * len(in_day))
    result = {
        "date_utc": args.date,
        "window": [start, end],
        "signatures_in_day": len(in_day),
        "sample_size": len(sample),
        "counts": counts,
        "create_ratio_estimated": round(create_ratio, 4),
        "estimated_creates_in_day": estimated_creates,
        "rpc_calls_made": client.calls,
        "create_records_sample": create_records[:50],
        "raw_create_examples": raw_create_examples,
    }
    out_file = out_dir / "dry_run.json"
    out_file.write_text(json.dumps(result, indent=2))
    print(f"[dry-run] done: {json.dumps({k: result[k] for k in ('signatures_in_day','counts','estimated_creates_in_day','rpc_calls_made')})}")
    print(f"[dry-run] output written to {out_file}")


if __name__ == "__main__":
    main()
