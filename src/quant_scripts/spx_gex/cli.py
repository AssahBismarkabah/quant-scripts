from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .backtest import SPXGEXBacktest, run_walk_forward, write_backtest_report
from .databento import DatabentoBarRequest, fetch_spy_intraday_bars, write_spy_intraday_bars_json
from .io import (
    load_gex_files,
    load_gex_point,
    normalize_cboe_input,
    load_session_list,
    sample_csv_payload,
    sample_bars_payload,
    sample_input_payload,
    sample_point_payload,
    sample_sessions_payload,
    summarize_input,
)
from .models import GEXContract, build_gex_data_point, classify_regime, calculate_dealer_gex


def _load_dotenv(dotenv_path: Path | None = None) -> None:
    env_path = dotenv_path if dotenv_path is not None else Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SPX dealer gamma exposure research helper")
    parser.add_argument(
        "--mode",
        choices=[
            "smoke",
            "calc",
            "backtest",
            "walk-forward",
            "template",
            "validate",
            "point-template",
            "bars-template",
            "sessions-template",
            "csv-template",
            "normalize-cboe",
            "fetch-spy-bars",
        ],
        default="smoke",
    )
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--point", type=Path, default=None)
    parser.add_argument("--bars", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dataset", type=str, default="EQUS.MINI")
    parser.add_argument("--symbol", type=str, default="SPY")
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    return parser


def main() -> int:
    _load_dotenv()
    args = build_parser().parse_args()
    if args.mode == "smoke":
        sample = build_gex_data_point(
            snapshot_time=datetime(2026, 8, 1, 15, 45, tzinfo=timezone.utc),
            underlying_symbol="SPX",
            underlying_price=5000.0,
            contracts=[
                GEXContract("call", 5000.0, datetime(2026, 8, 2, tzinfo=timezone.utc), 1000.0, 0.02),
                GEXContract("put", 4950.0, datetime(2026, 8, 2, tzinfo=timezone.utc), 800.0, 0.018),
            ],
        )
        dealer_gex = calculate_dealer_gex(sample)
        print(json.dumps({"dealer_gex": dealer_gex, "regime": classify_regime(dealer_gex).value}, indent=2))
        return 0

    if args.mode == "template":
        print(json.dumps(sample_input_payload(), indent=2))
        return 0

    if args.mode == "point-template":
        print(json.dumps(sample_point_payload(), indent=2))
        return 0

    if args.mode == "bars-template":
        print(json.dumps(sample_bars_payload(), indent=2))
        return 0

    if args.mode == "sessions-template":
        print(json.dumps(sample_sessions_payload(), indent=2))
        return 0

    if args.mode == "csv-template":
        print(sample_csv_payload())
        return 0

    if args.mode == "normalize-cboe":
        if args.input is None:
            raise SystemExit("--input is required for normalize-cboe mode")
        print(json.dumps(normalize_cboe_input(args.input), indent=2))
        return 0

    if args.mode == "fetch-spy-bars":
        if args.start is None or args.end is None:
            raise SystemExit("--start and --end are required for fetch-spy-bars mode")
        if args.output is None:
            raise SystemExit("--output is required for fetch-spy-bars mode")
        request = DatabentoBarRequest(
            dataset=args.dataset,
            symbol=args.symbol,
            start=datetime.fromisoformat(args.start),
            end=datetime.fromisoformat(args.end),
        )
        bars = fetch_spy_intraday_bars(request)
        write_spy_intraday_bars_json(args.output, bars)
        print(json.dumps({"bars": len(bars), "output": str(args.output)}, indent=2))
        return 0

    if args.mode == "validate":
        if args.input is None:
            raise SystemExit("--input is required for validate mode")
        print(json.dumps(summarize_input(args.input), indent=2))
        return 0

    if args.mode == "calc":
        if args.input is None:
            raise SystemExit("--input is required for calc mode")
        point, _ = load_gex_files(args.input, args.bars)
    elif args.mode == "walk-forward":
        if args.input is None:
            raise SystemExit("--input is required for walk-forward mode")
        sessions = load_session_list(args.input)
        wf_sessions = []
        for point, bars in sessions:
            ordered = sorted(bars, key=lambda bar: bar.ts)
            evaluation = next((bar.ts for bar in ordered if bar.ts.hour == 13 and bar.ts.minute == 30), None)
            entry = evaluation
            exit_time = next((bar.ts for bar in ordered if bar.ts.hour == 15 and bar.ts.minute == 0), None)
            lookback = next((bar.ts for bar in ordered if bar.ts.hour == 11 and bar.ts.minute == 30), None)
            if evaluation is None or entry is None or exit_time is None or lookback is None:
                continue
            wf_sessions.append((point, bars, lookback, evaluation, entry, exit_time))
        backtest, summary = run_walk_forward(wf_sessions)
        if args.output is not None:
            write_backtest_report(args.output, backtest, summary)
        print(json.dumps(summary.as_dict(), indent=2))
        return 0
    elif args.mode == "backtest":
        if args.point is None or args.bars is None:
            raise SystemExit("--point and --bars are required for backtest mode")
        point, bars = load_gex_files(args.point, args.bars)
    else:
        if args.input is None:
            raise SystemExit("--input is required for calc/backtest mode")
        point, bars = load_gex_point(args.input)

    dealer_gex = calculate_dealer_gex(point)
    output = {"dealer_gex": dealer_gex, "regime": classify_regime(dealer_gex).value}
    if args.mode == "backtest":
        if not bars:
            raise SystemExit("backtest mode requires bars in the input file")
        backtest = SPXGEXBacktest()
        ordered = sorted(bars, key=lambda bar: bar.ts)
        evaluation = next((bar.ts for bar in ordered if bar.ts.hour == 13 and bar.ts.minute == 30), None)
        entry = evaluation
        exit_time = next((bar.ts for bar in ordered if bar.ts.hour == 15 and bar.ts.minute == 0), None)
        lookback = next((bar.ts for bar in ordered if bar.ts.hour == 11 and bar.ts.minute == 30), None)
        if evaluation is None or entry is None or exit_time is None or lookback is None:
            raise SystemExit("backtest mode requires 11:30, 13:30, and 15:00 bars")
        results = backtest.run(
            point=point,
            bars=bars,
            lookback_start_time=lookback,
            evaluation_time=evaluation,
            entry_time=entry,
            exit_time=exit_time,
        )
        output["backtest"] = [result.summary() for result in results]
        output["summary"] = backtest.summarize().as_dict()
        if args.output is not None:
            write_backtest_report(args.output, backtest, backtest.summarize())
    print(json.dumps(output, indent=2))
    return 0
