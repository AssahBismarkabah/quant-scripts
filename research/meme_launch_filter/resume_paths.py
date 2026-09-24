"""Resume polling of already-submitted Dune executions and save results."""

import json
import sys
from pathlib import Path

from quant_scripts.meme_launch_filter.config import dune_api_key
from quant_scripts.meme_launch_filter.dune import DuneClient
from quant_scripts.meme_launch_filter.io_rows import convert_dune_json, has_rows

JOBS = {
    "2026-09-18": "01M36TSBK0AR2FY2BMSKSYT2ZF",
    "2026-09-19": "01M36TN6CPBAW6D62NXGK68G4W",
    "2026-09-20": "01M36TPAJ3TXMCMQDR3GZ05S8K",
    "2026-09-21": "01M36TQEKM2F3NYASTN0S30ERH",
}

def main() -> None:
    client = DuneClient(dune_api_key())
    base = Path("research/meme_launch_filter")
    only = sys.argv[1:] or list(JOBS)
    for day in only:
        exec_id = JOBS[day]
        day_dir = base / day
        out = day_dir / "step2_paths.json"
        if has_rows(day_dir, "step2_paths"):
            print(f"{day}: already exists, skipping", flush=True)
            continue
        print(f"{day}: polling {exec_id}", flush=True)
        results = client.get_results(exec_id)
        out.write_text(json.dumps(results, indent=2))
        convert_dune_json(out)
        rows = results.get("result", {}).get("rows") or []
        meta = results.get("result", {}).get("metadata") or {}
        state = results.get('state')
        total = meta.get('total_row_count')
        print(f"{day}: state={state} rows={len(rows)} total={total}", flush=True)

if __name__ == "__main__":
    main()
