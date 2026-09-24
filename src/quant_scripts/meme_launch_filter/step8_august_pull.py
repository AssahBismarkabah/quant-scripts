"""Step 8: August 2026 out-of-sample pull (Addendum O).

Per day: step1_postgrad, step2_featbar, step2_paths - generated from the
2026-09-13 SQL templates with the date literal replaced. Skips days that
already have the files. featbar falls back to a v1-only launches CTE if
pump_call_create_v2 is unavailable for the target date.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from quant_scripts.meme_launch_filter.config import dune_api_key
from quant_scripts.meme_launch_filter.dune import DuneClient
from quant_scripts.meme_launch_filter.io_rows import convert_dune_json

BASE = Path("research/meme_launch_filter")
TEMPLATE_DAY = "2026-09-13"
QUERIES = {
    "step1_postgrad": ("step1_postgrad.sql", "medium"),
    "step2_featbar": ("step2_featbar.sql", "medium"),
    "step2_paths": ("step2_paths.sql", "medium"),
}


def day_sql(template_path: Path, day: str) -> str:
    sql = template_path.read_text()
    return sql.replace(TEMPLATE_DAY, day)


def v1_only_featbar(sql: str) -> str:
    """Replace the launches CTE with a v1-only variant (v2-table-missing fallback)."""
    start = sql.index("launches AS (")
    end = sql.index("curve_pre AS (")
    replacement = (
        "launches AS (\n"
        "    SELECT account_mint AS mint, call_block_time AS create_time, creator\n"
        "    FROM pumpdotfun_solana.pump_call_create\n"
        "    WHERE call_block_date = DATE '2026-09-13'\n"  # day_sql() replaces this
        "),\n"
    )
    return sql[:start] + replacement + sql[end:]


def main() -> None:
    days = sys.argv[1:]
    if not days:
        days = [f"2026-08-{i:02d}" for i in range(1, 32)]
    client = DuneClient(dune_api_key())
    for day in days:
        day_dir = BASE / day
        done = all((day_dir / f"{name}.json").exists() for name in QUERIES)
        if done:
            print(f"{day}: all outputs exist, skipping", flush=True)
            continue
        day_dir.mkdir(parents=True, exist_ok=True)
        for name, (fname, perf) in QUERIES.items():
            out = day_dir / f"{name}.json"
            if out.exists():
                continue
            try:
                sql = day_sql(BASE / TEMPLATE_DAY / fname, day)
                exec_id = client.execute_sql(sql, performance=perf)
                print(f"{day} {name}: exec_id={exec_id}", flush=True)
                results = client.get_results(exec_id)
                out.write_text(json.dumps(results, indent=2))
                convert_dune_json(out)
                rows = (results.get("result") or {}).get("rows") or []
                print(f"{day} {name}: state={results.get('state')} rows={len(rows)}", flush=True)
            except RuntimeError as exc:
                if name == "step2_featbar":
                    print(f"{day} {name}: retrying v1-only ({exc})", flush=True)
                    sql = v1_only_featbar(day_sql(BASE / TEMPLATE_DAY / fname, day))
                    try:
                        exec_id = client.execute_sql(sql, performance=perf)
                        print(f"{day} {name}: v1 exec_id={exec_id}", flush=True)
                        results = client.get_results(exec_id)
                        out.write_text(json.dumps(results, indent=2))
                        convert_dune_json(out)
                        rows = (results.get("result") or {}).get("rows") or []
                        print(f"{day} {name}: state={results.get('state')} rows={len(rows)}", flush=True)
                        continue
                    except RuntimeError as exc2:
                        print(f"{day} {name}: v1-only FAILED {exc2}", flush=True)
                        raise
                raise
        print(f"{day}: done", flush=True)


if __name__ == "__main__":
    main()
