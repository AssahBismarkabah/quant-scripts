"""CLI helper: run a Dune SQL string and save results as JSON.

Usage: PYTHONPATH=src python -m quant_scripts.meme_launch_filter.dune_cli \
    --sql-file query.sql --out results.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import dune_api_key
from .dune import DuneClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--performance", default="medium", choices=["medium", "large"])
    args = parser.parse_args()

    sql = Path(args.sql_file).read_text()
    client = DuneClient(dune_api_key())
    execution_id = client.execute_sql(sql, performance=args.performance)
    print(f"execution_id={execution_id}", flush=True)
    results = client.get_results(execution_id)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    meta = results.get("result", {}).get("metadata") or {}
    rows = results.get("result", {}).get("rows") or []
    print(f"state={results.get('state')} rows={len(rows)} total={meta.get('total_row_count')}")


if __name__ == "__main__":
    main()
