from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable

from .models import MarketSnapshot, NormalizedDataset, SourceFormat


class BinanceRecordType(str, Enum):
    AGG_TRADE = "agg_trade"
    KLINE = "kline"
    DEPTH_SNAPSHOT = "depth_snapshot"
    BOOK_TICKER = "book_ticker"


@dataclass(frozen=True)
class BinanceFileMarketDataSource:
    path: Path
    venue: str
    symbol: str
    record_type: BinanceRecordType
    source: str
    format: SourceFormat = SourceFormat.JSONL

    def load(self) -> NormalizedDataset:
        if self.format is SourceFormat.JSONL:
            rows = _load_jsonl_rows(self.path)
        elif self.format is SourceFormat.CSV:
            rows = _load_csv_rows(self.path)
        else:
            raise ValueError(f"unsupported format: {self.format}")

        snapshots = tuple(
            _row_to_snapshot(row, venue=self.venue, symbol=self.symbol, source=self.source, record_type=self.record_type)
            for row in rows
        )
        return NormalizedDataset(venue=self.venue, symbol=self.symbol, snapshots=snapshots)


def _load_jsonl_rows(path: Path) -> Iterable[dict[str, object]]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def _load_csv_rows(path: Path) -> Iterable[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def _row_to_snapshot(
    row: dict[str, object],
    venue: str,
    symbol: str,
    source: str,
    record_type: BinanceRecordType,
) -> MarketSnapshot:
    if record_type is BinanceRecordType.AGG_TRADE:
        return MarketSnapshot(
            ts=_parse_timestamp(_get(row, "T", "ts", "time", "timestamp")),
            venue=venue,
            symbol=_get_str(row, symbol, "s", "symbol"),
            bid=None,
            ask=None,
            last=_maybe_float(_get(row, "p", "price")),
            mark=None,
            index=None,
            funding_rate_bps=None,
            open_interest=None,
            source=source,
        )
    if record_type is BinanceRecordType.KLINE:
        return MarketSnapshot(
            ts=_parse_timestamp(_get(row, "open_time", "openTime", "t", "ts", "time")),
            venue=venue,
            symbol=_get_str(row, symbol, "s", "symbol"),
            bid=None,
            ask=None,
            last=_maybe_float(_get(row, "c", "close", "closePrice")),
            mark=None,
            index=None,
            funding_rate_bps=None,
            open_interest=None,
            source=source,
        )
    if record_type is BinanceRecordType.DEPTH_SNAPSHOT:
        return MarketSnapshot(
            ts=_parse_timestamp(_get(row, "E", "ts", "time", "timestamp")),
            venue=venue,
            symbol=_get_str(row, symbol, "s", "symbol"),
            bid=_best_price_from_levels(row.get("bids"), row.get("bid"), side="bid"),
            ask=_best_price_from_levels(row.get("asks"), row.get("ask"), side="ask"),
            last=None,
            mark=None,
            index=None,
            funding_rate_bps=None,
            open_interest=None,
            source=source,
        )
    if record_type is BinanceRecordType.BOOK_TICKER:
        return MarketSnapshot(
            ts=_parse_timestamp(_get(row, "E", "ts", "time", "timestamp")),
            venue=venue,
            symbol=_get_str(row, symbol, "s", "symbol"),
            bid=_maybe_float(_get(row, "b", "bidPrice")),
            ask=_maybe_float(_get(row, "a", "askPrice")),
            last=None,
            mark=None,
            index=None,
            funding_rate_bps=None,
            open_interest=None,
            source=source,
        )
    raise ValueError(f"unsupported Binance record type: {record_type}")


def _get(row: dict[str, object], *keys: str) -> object:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    raise KeyError(f"missing keys: {', '.join(keys)}")


def _get_str(row: dict[str, object], default: str, *keys: str) -> str:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return str(row[key])
    return default


def _maybe_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _best_price_from_levels(value: object, fallback: object, side: str) -> float | None:
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, (list, tuple)) and first:
            return float(first[0])
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, list) and parsed:
            first = parsed[0]
            if isinstance(first, (list, tuple)) and first:
                return float(first[0])
    if fallback not in (None, ""):
        return float(fallback)
    return None


def _parse_timestamp(value: object) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value) / 1000.0, tz=timezone.utc)
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

