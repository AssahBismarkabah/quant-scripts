from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import URLError

from .config import BinanceCredentials
from .client import BinanceRestClient
from .ingest import BinanceIngestionService
from .config import BinanceSettings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Binance funding-basis ingestion helper")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--dotenv", type=Path, default=None)
    parser.add_argument("--insecure-tls", action="store_true")
    parser.add_argument("--mode", choices=["smoke", "funding", "mark", "spot", "dump"], default="smoke")
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser


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
        dataset = service.load_funding_history(args.symbol, limit=10)
    elif args.mode == "mark":
        dataset = service.load_mark_price_klines(args.symbol, args.interval, limit=10)
    elif args.mode == "spot":
        dataset = service.load_spot_klines(args.symbol, args.interval, limit=10)
    else:
        output_dir = args.output_dir or Path("research/funding-basis/fixtures")
        output_dir.mkdir(parents=True, exist_ok=True)
        datasets = {
            "funding": service.load_funding_history(args.symbol, limit=10),
            "mark": service.load_mark_price_klines(args.symbol, args.interval, limit=10),
            "spot": service.load_spot_klines(args.symbol, args.interval, limit=10),
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
