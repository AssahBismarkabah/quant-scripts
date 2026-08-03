"""SPX GEX Level-1 daily regime study runner.

For each trade day T in the window:

    regime(T) = merge(OptionsDX EOD chain snapshot T-1,
                      Databento open interest as-of T-1),
                0DTE excluded per spec version one
    trade(T)  = SPY intraday playbook on day T:
                11:30-13:30 ET lookback, 13:30 ET entry, 15:00 ET exit

The regime for day T uses only information from T-1, so no look-ahead.
Results are reported per regime (positive / negative / flat) as the spec
requires regimes not to be pooled.

Usage:
    PYTHONPATH=src python research/spx-gex/run_study.py \
        --chain-dir spx_eod_extract \
        --oi research/spx-gex/data/spx_oi_2023_full.csv \
        --oi research/spx-gex/data/spxw_oi_2023_full.csv \
        --bars research/spx-gex/data/spy_bars_2023.json \
        [--start 2023-04-04 --end 2023-04-17]

    Open interest may span multiple option roots (SPX monthlies and SPXW
    weeklies are the same economic contract with volume split across the
    two listings), so pass --oi once per root; open interest is summed
    across roots per (option type, strike, expiration, trade date).
"""

from __future__ import annotations

import argparse
import csv
import glob
import sys
from collections import defaultdict
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")


def _ny_time(day: date, hour: int, minute: int) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=NY)


def _load_bars_by_day(path: Path) -> dict[date, list]:
    from quant_scripts.spx_gex.io import load_intraday_bars

    bars = load_intraday_bars(path)
    by_day: dict[date, list] = defaultdict(list)
    for bar in bars:
        by_day[bar.ts.astimezone(NY).date()].append(bar)
    return dict(by_day)


def _oi_trade_dates(oi_paths: list[Path]) -> list[date]:
    dates: set[date] = set()
    for path in oi_paths:
        with path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            dates.update(
                date.fromisoformat(row["trade_date"])
                for row in reader
                if row.get("trade_date")
            )
    return sorted(dates)


def _chain_file_for(chain_dir: Path, day: date) -> Path:
    matches = glob.glob(str(chain_dir / "**" / f"spx_eod_{day:%Y%m}.txt"), recursive=True)
    if not matches:
        raise FileNotFoundError(f"no chain file for {day:%Y-%m} in {chain_dir}")
    return Path(matches[0])


def _previous_trade_date(oi_dates: list[date], day: date) -> date | None:
    for candidate in reversed(oi_dates):
        if candidate < day:
            return candidate
    return None


def _oi_by_trade_date(oi_paths: list[Path]) -> dict[date, list]:
    from quant_scripts.spx_gex.databento_options import OpenInterestRow, normalize_oi_row

    # Within a root file, repeated rows for the same contract are duplicate
    # snapshots: keep the max. Across roots, the same economic contract can be
    # listed in both SPX and SPXW: sum the open interest.
    root_best: dict[tuple, OpenInterestRow] = {}
    for path in oi_paths:
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        per_root: dict[tuple, OpenInterestRow] = {}
        for raw in rows:
            row = normalize_oi_row(raw)
            if row.as_of is None:
                continue
            key = (row.option_type, round(row.strike, 6), row.expiration.date().isoformat(), row.as_of)
            existing = per_root.get(key)
            if existing is None or row.open_interest > existing.open_interest:
                per_root[key] = row
        for key, row in per_root.items():
            merged = root_best.get(key)
            if merged is None:
                root_best[key] = row
            else:
                root_best[key] = replace(merged, open_interest=merged.open_interest + row.open_interest)
    by_day: dict[date, list] = defaultdict(list)
    for row in root_best.values():
        by_day[row.as_of].append(row)
    return dict(by_day)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chain-dir", type=Path, required=True)
    parser.add_argument("--oi", type=Path, action="append", required=True, help="OI csv, one per option root")
    parser.add_argument("--bars", type=Path, required=True)
    parser.add_argument("--start", type=date.fromisoformat, default=None)
    parser.add_argument("--end", type=date.fromisoformat, default=None)
    parser.add_argument("--slippage-bps", type=float, default=2.0, help="1 bps per side")
    parser.add_argument("--commission-bps", type=float, default=0.1)
    parser.add_argument("--sec-fee-bps", type=float, default=0.08)
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

    from quant_scripts.spx_gex.backtest import SPXGEXBacktest
    from quant_scripts.spx_gex.databento_options import load_optionsdx_rows, merge_optionsdx_with_open_interest

    bars_by_day = _load_bars_by_day(args.bars)
    oi_dates = _oi_trade_dates(args.oi)
    oi_by_day = _oi_by_trade_date(args.oi)

    trade_days = [day for day in sorted(bars_by_day) if (args.start is None or day >= args.start) and (args.end is None or day <= args.end)]
    if not trade_days:
        print("no trade days in the window", file=sys.stderr)
        return 1

    # each monthly chain file and the OI snapshot per date are parsed once
    chain_cache: dict[Path, list] = {}

    def merged_point(prev: date):
        chain_file = _chain_file_for(args.chain_dir, prev)
        if chain_file not in chain_cache:
            chain_cache[chain_file] = load_optionsdx_rows(chain_file)
        return merge_optionsdx_with_open_interest(
            chain_file,
            args.oi[0],
            snapshot_date=prev,
            oi_as_of=prev,
            exclude_0dte=True,
            chain_rows=chain_cache[chain_file],
            oi_rows=oi_by_day.get(prev, []),
        )

    backtest = SPXGEXBacktest(
        slippage_bps=args.slippage_bps,
        commission_bps=args.commission_bps,
        sec_fee_bps=args.sec_fee_bps,
    )

    print("day,regime,accepted,lookback_bps,net_edge_bps,dealer_gex_billions")
    outcomes: list[tuple[str, float]] = []
    skipped = 0
    for day in trade_days:
        prev = _previous_trade_date(oi_dates, day)
        if prev is None:
            print(f"{day}: skipped (no T-1 open interest)", file=sys.stderr)
            skipped += 1
            continue

        point = merged_point(prev)

        results = backtest.run(
            point=point,
            bars=bars_by_day[day],
            lookback_start_time=_ny_time(day, 11, 30).astimezone(UTC),
            evaluation_time=_ny_time(day, 13, 30).astimezone(UTC),
            entry_time=_ny_time(day, 13, 30).astimezone(UTC),
            exit_time=_ny_time(day, 15, 0).astimezone(UTC),
        )
        for result in results:
            decision = result.decision
            edge = decision.net_edge_bps() if result.accepted else 0.0
            outcomes.append((decision.regime.value, edge))
            print(
                f"{day},{decision.regime.value},{int(result.accepted)},"
                f"{decision.lookback_return_bps:.2f},{edge:.2f},"
                f"{-1 * sum(c.contract_gex(point.underlying_price) for c in point.contracts) / 1e9:.1f}"
            )

    print("\nper-regime summary (spec: regimes are not pooled)")
    print("regime,sessions,accepted,avg_net_edge_bps,win_rate")
    for regime in ("positive", "negative", "flat"):
        edges = [edge for name, edge in outcomes if name == regime]
        avg = sum(edges) / len(edges) if edges else 0.0
        win = sum(1 for e in edges if e > 0) / len(edges) if edges else 0.0
        print(f"{regime},{len(edges)},{len(edges)},{avg:.2f},{win:.2%}")
    print(f"\nskipped sessions (no T-1 OI): {skipped}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
