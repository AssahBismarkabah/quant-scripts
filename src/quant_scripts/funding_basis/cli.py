from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import BinanceCredentials
from .client import BinanceRestClient
from .ingest import BinanceIngestionService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Binance funding-basis ingestion helper")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--dotenv", type=Path, default=None)
    parser.add_argument("--mode", choices=["funding", "mark", "spot"], default="funding")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    credentials = BinanceCredentials.from_env(args.dotenv)
    client = BinanceRestClient(credentials=credentials)
    service = BinanceIngestionService(client=client)

    if args.mode == "funding":
        dataset = service.load_funding_history(args.symbol, limit=10)
    elif args.mode == "mark":
        dataset = service.load_mark_price_klines(args.symbol, args.interval, limit=10)
    else:
        dataset = service.load_spot_klines(args.symbol, args.interval, limit=10)

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

