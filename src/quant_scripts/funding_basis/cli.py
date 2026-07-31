from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError

from .config import BinanceCredentials, BinanceSettings
from .client import BinanceRestClient
from .fixture_replay import replay_fixture_set_many
from .ingest import BinanceIngestionService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Binance funding-basis ingestion helper")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--dotenv", type=Path, default=None)
    parser.add_argument("--insecure-tls", action="store_true")
    parser.add_argument("--mode", choices=["smoke", "funding", "mark", "spot", "dump", "replay"], default="smoke")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--start-time", type=_parse_timestamp, default=None)
    parser.add_argument("--end-time", type=_parse_timestamp, default=None)
    return parser


def _parse_timestamp(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.astimezone(timezone.utc).timestamp() * 1000)


def main() -> int:
    args = build_parser().parse_args()
    credentials = BinanceCredentials.from_env(args.dotenv)
    client = BinanceRestClient(credentials=credentials, settings=BinanceSettings(insecure_tls=args.insecure_tls))
    service = BinanceIngestionService(client=client)

    if args.mode == "smoke":
        try:
            output = {
                "server_time": client.get_server_time(),
                "exchange_info_symbols": len(client.get_futures_exchange_info().get("symbols", [])),
            }
            try:
                output["futures_account"] = client.get_futures_account()
            except Exception as exc:  # pragma: no cover - only used for live smoke checks
                output["futures_account_error"] = str(exc)
        except URLError as exc:  # pragma: no cover - only used for live smoke checks
            output = {"network_error": str(exc)}
        print(json.dumps(output, indent=2))
        return 0

    if args.mode == "funding":
        dataset = service.load_funding_history(
            args.symbol,
            start_time=args.start_time,
            end_time=args.end_time,
            limit=args.limit,
        )
    elif args.mode == "mark":
        dataset = service.load_mark_price_klines(
            args.symbol,
            args.interval,
            start_time=args.start_time,
            end_time=args.end_time,
            limit=args.limit,
        )
    elif args.mode == "spot":
        dataset = service.load_spot_klines(
            args.symbol,
            args.interval,
            start_time=args.start_time,
            end_time=args.end_time,
            limit=args.limit,
        )
    elif args.mode == "replay":
        output_dir = args.output_dir or Path("research/funding-basis/fixtures")
        replay = replay_fixture_set_many(
            output_dir / f"{args.symbol.lower()}_funding.json",
            output_dir / f"{args.symbol.lower()}_mark.json",
            output_dir / f"{args.symbol.lower()}_spot.json",
        )
        accepted = sum(1 for result in replay.results if result.accepted)
        print(
            json.dumps(
                {
                    "decisions": len(replay.decisions),
                    "accepted": accepted,
                    "rejected": len(replay.results) - accepted,
                    "avg_net_edge_bps": sum(result.trade.net_edge_bps() for result in replay.results) / len(replay.results)
                    if replay.results
                    else 0.0,
                    "avg_net_pnl": sum(result.trade.net_pnl() for result in replay.results) / len(replay.results)
                    if replay.results
                    else 0.0,
                    "first_rejection_reason": next((result.rejection_reason for result in replay.results if not result.accepted), None),
                    "first_entry_time": replay.decisions[0].entry_time.isoformat() if replay.decisions else None,
                    "first_exit_time": replay.decisions[0].exit_time.isoformat() if replay.decisions else None,
                    "funding_rows": len(replay.funding.snapshots),
                    "mark_rows": len(replay.mark.snapshots),
                    "spot_rows": len(replay.spot.snapshots),
                },
                indent=2,
            )
        )
        return 0
    else:
        output_dir = args.output_dir or Path("research/funding-basis/fixtures")
        output_dir.mkdir(parents=True, exist_ok=True)
        datasets = {
            "funding": service.load_funding_history(
                args.symbol,
                start_time=args.start_time,
                end_time=args.end_time,
                limit=args.limit,
            ),
            "mark": service.load_mark_price_klines(
                args.symbol,
                args.interval,
                start_time=args.start_time,
                end_time=args.end_time,
                limit=args.limit,
            ),
            "spot": service.load_spot_klines(
                args.symbol,
                args.interval,
                start_time=args.start_time,
                end_time=args.end_time,
                limit=args.limit,
            ),
        }
        output = {}
        for name, dataset in datasets.items():
            path = output_dir / f"{args.symbol.lower()}_{name}.json"
            path.write_text(
                json.dumps(
                    {
                        "venue": dataset.venue,
                        "symbol": dataset.symbol,
                        "snapshots": [
                            {
                                "ts": snapshot.ts.isoformat(),
                                "venue": snapshot.venue,
                                "symbol": snapshot.symbol,
                                "bid": snapshot.bid,
                                "ask": snapshot.ask,
                                "last": snapshot.last,
                                "mark": snapshot.mark,
                                "index": snapshot.index,
                                "funding_rate_bps": snapshot.funding_rate_bps,
                                "open_interest": snapshot.open_interest,
                                "source": snapshot.source,
                            }
                            for snapshot in dataset.snapshots
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            output[name] = {"rows": len(dataset.snapshots), "path": str(path)}
        print(json.dumps(output, indent=2))
        return 0

    print(
        json.dumps(
            {
                "venue": dataset.venue,
                "symbol": dataset.symbol,
                "rows": len(dataset.snapshots),
                "first_ts": dataset.snapshots[0].ts.isoformat() if dataset.snapshots else None,
                "last_ts": dataset.snapshots[-1].ts.isoformat() if dataset.snapshots else None,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
