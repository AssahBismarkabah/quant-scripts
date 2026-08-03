"""Fetch per-day SPX open interest from Databento OPRA statistics.

Unlike the single-day CLI fetch, this script:
  - patches the databento client read timeout (large month streams exceed 100s)
  - skips the definitions join (a point-in-time full-history download per call)
    and parses the option symbol directly, e.g. "SPX 231215C04300000"
    -> (expiry 2023-12-15, call, strike 4300.0)
  - fetches month by month so each stream fits comfortably in one request

Output CSV: option_type,strike,expiration,open_interest,trade_date
One row per contract per trade date (duplicates within a day are collapsed
to the max open interest by the loader).

Usage:
    PYTHONPATH=src python research/spx-gex/fetch_oi.py \
        --output research/spx-gex/data/spx_oi_2023_full.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_SYMBOL_RE = re.compile(r"(\d{2})(\d{2})(\d{2})([CP])(\d{8})$")

_MONTH_WINDOWS = [
    ("2023-01-01", "2023-02-01"),
    ("2023-02-01", "2023-03-01"),
    ("2023-03-01", "2023-04-01"),
    ("2023-04-01", "2023-05-01"),
    ("2023-05-01", "2023-06-01"),
    ("2023-06-01", "2023-07-01"),
    ("2023-07-01", "2023-08-01"),
    ("2023-08-01", "2023-09-01"),
    ("2023-09-01", "2023-10-01"),
    ("2023-10-01", "2023-11-01"),
    ("2023-11-01", "2023-12-01"),
    ("2023-12-01", "2024-01-01"),
]


def _load_env() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _parse_symbol(symbol: str) -> tuple[str, float, datetime] | None:
    match = _SYMBOL_RE.search(symbol)
    if match is None:
        return None
    yy, mm, dd, option_type, strike = match.groups()
    expiration = datetime(2000 + int(yy), int(mm), int(dd))
    return (option_type.lower(), int(strike) / 1000.0, expiration)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", type=str, default="OPRA.PILLAR")
    parser.add_argument("--symbol", type=str, default="SPX.OPT")
    args = parser.parse_args()

    _load_env()

    # month streams can exceed the client's 100s read timeout
    import databento.common.http as db_http

    db_http.BentoHttpAPI.TIMEOUT = 900

    import databento as db

    client = db.Historical()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        handle.write("option_type,strike,expiration,open_interest,trade_date\n")

    total = 0
    for index, (start, end) in enumerate(_MONTH_WINDOWS, 1):
        stats = client.timeseries.get_range(
            dataset=args.dataset,
            symbols=args.symbol,
            schema="statistics",
            stype_in="parent",
            start=datetime.fromisoformat(f"{start}T00:00:00+00:00"),
            end=datetime.fromisoformat(f"{end}T00:00:00+00:00"),
        ).to_df().reset_index()

        oi = stats[stats["stat_type"].isin((9, "9", "open_interest", "OPEN_INTEREST"))]
        with out.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            for _, row in oi.iterrows():
                parsed = _parse_symbol(str(row["symbol"]))
                if parsed is None:
                    continue
                option_type, strike, expiration = parsed
                as_of = row["ts_event"].date() if hasattr(row["ts_event"], "date") else None
                writer.writerow(
                    [option_type, strike, expiration.isoformat(), row["quantity"], as_of]
                )
        total += len(oi)
        print(f"month {index}/{len(_MONTH_WINDOWS)} ({start}..{end}): {len(oi)} OI rows")
        sys.stdout.flush()

    print(f"done, {total} raw OI rows -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
