"""Run the free SEC EDGAR release-time audit on the fixed 100-row template.

Writes ``outputs/timing_audit.csv`` in the exact schema the Phase 0 evaluator
expects. This is the no-purchase path to unblock Phase 0 (see
IA/earnings-anchored-vwap-research-gate.md §10).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from quant_scripts.earnings_anchored_vwap.timing_audit import audit_sample  # noqa: E402

OUT = ROOT / "research" / "earnings-anchored-vwap" / "outputs"
TEMPLATE = OUT / "timing_audit_template.csv"
AUDIT = OUT / "timing_audit.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the free SEC EDGAR timing audit.")
    parser.add_argument("--limit", type=int, default=None, help="audit only the first N events")
    parser.add_argument("--start", type=int, default=1, help="1-based sample index to start at")
    args = parser.parse_args()

    template = pd.read_csv(TEMPLATE, dtype=str).fillna("")
    if args.limit is not None:
        template = template.iloc[args.start - 1 : args.start - 1 + args.limit]
    print(f"auditing {len(template)} events from {TEMPLATE.name} against SEC EDGAR (start={args.start})...")
    audit = audit_sample(template)

    # Merge with any existing audit rows (idempotent re-runs without re-hammering EDGAR)
    if AUDIT.exists() and args.limit is not None:
        existing = pd.read_csv(AUDIT, dtype=str).fillna("")
        audit = (
            pd.concat([existing[~existing["sample_id"].isin(audit["sample_id"])], audit], ignore_index=True)
            .drop_duplicates("sample_id", keep="last")
            .reset_index(drop=True)
        )

    AUDIT.write_bytes(
        audit.to_csv(index=False).encode("utf-8")
    )
    print(f"wrote {AUDIT.relative_to(ROOT)}")
    print("\nstatus breakdown:")
    print(audit["status"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    main()
