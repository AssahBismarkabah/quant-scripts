"""Generate per-day SQL variants for the 7-day pilot window and print commands.

The Step 1 SQL files are single-day (DATE '2026-09-20'). This writes one SQL
per day per pull type (launches, graduations, trades, firsthour, postgrad)
with the date substituted, so each day can be pulled and analyzed exactly
like the pilot day.

Usage: PYTHONPATH=src .venv/bin/python -m quant_scripts.meme_launch_filter.step1_multiday 2026-09-13 2026-09-19
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

SRC = Path("research/meme_launch_filter/2026-09-20")


def main() -> None:
    start = date.fromisoformat(sys.argv[1])
    end = date.fromisoformat(sys.argv[2])
    day = start
    while day <= end:
        day_dir = SRC.parent / day.isoformat()
        day_dir.mkdir(parents=True, exist_ok=True)
        for kind in ("step1_launches", "step1_graduations", "step1_trades", "step1_firsthour", "step1_postgrad", "step2_featbar", "step2_paths"):
            sql = (SRC / f"{kind}.sql").read_text()
            day_sql = sql.replace("2026-09-20", day.isoformat())
            (day_dir / f"{kind}.sql").write_text(day_sql)
        # step1_postgrad.sql references the grad day in two places plus a
        # date-range guard '>= DATE 2026-09-20'; check substitution count.
        pg = (day_dir / "step1_postgrad.sql").read_text()
        n = pg.count(day.isoformat())
        print(f"{day}: postgrad date refs={n} (expect 2)")
        day += timedelta(days=1)


if __name__ == "__main__":
    main()
