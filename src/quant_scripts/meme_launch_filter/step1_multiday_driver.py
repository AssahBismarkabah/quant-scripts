"""Run the full Step 1 pull + analysis sequence for each day in a window.

Per day: launches, graduations, trades, firsthour, postgrad pulls via the
Dune CLI, then the three merge/analysis scripts. Skips pulls whose output
JSON already exists (resumable after interruptions).

Usage: PYTHONPATH=src .venv/bin/python -m quant_scripts.meme_launch_filter.step1_multiday_driver 2026-09-13 2026-09-19
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

from quant_scripts.meme_launch_filter.io_rows import PARQUET_KINDS, convert_dune_json, has_rows

SRC = Path("research/meme_launch_filter/2026-09-20")

PULLS = [
    ("step1_launches", "large"),
    ("step1_graduations", "medium"),
    ("step1_trades", "large"),
    ("step1_firsthour", "large"),
    ("step1_postgrad", "large"),
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = (result.stdout + result.stderr).strip()
    if out:
        print(out[-2000:], flush=True)
    if result.returncode != 0:
        print(f"FAILED rc={result.returncode}", flush=True)


def main() -> None:
    start = date.fromisoformat(sys.argv[1])
    end = date.fromisoformat(sys.argv[2])
    day = start
    while day <= end:
        day_dir = SRC.parent / day.isoformat()
        print(f"===== {day} =====", flush=True)
        for kind, perf in PULLS:
            out_json = day_dir / f"{kind}.json"
            # Re-pull if neither parquet nor JSON has rows — catches
            # stale/broken windows across all pull kinds.
            needs_pull = not has_rows(day_dir, kind)
            if not needs_pull:
                print(f"{kind}: exists, skip", flush=True)
                continue
            run([
                ".venv/bin/python", "-m", "quant_scripts.meme_launch_filter.dune_cli",
                "--sql-file", str(day_dir / f"{kind}.sql"),
                "--out", str(out_json),
                "--performance", perf,
            ])
            if kind in PARQUET_KINDS:
                convert_dune_json(out_json)
        run([".venv/bin/python", "-m", "quant_scripts.meme_launch_filter.step1_summary", str(day_dir)])
        run([".venv/bin/python", "-m", "quant_scripts.meme_launch_filter.step1_firsthour_analysis", str(day_dir)])
        run([".venv/bin/python", "-m", "quant_scripts.meme_launch_filter.step1_postgrad_analysis", str(day_dir)])
        day += timedelta(days=1)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
