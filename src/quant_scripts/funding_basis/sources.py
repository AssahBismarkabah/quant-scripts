from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Protocol

from .models import MarketSnapshot, NormalizedDataset, SourceFormat


class MarketDataSource(Protocol):
    def load(self) -> NormalizedDataset: ...


@dataclass(frozen=True)
class FileMarketDataSource:
    path: Path
    venue: str
    symbol: str
    source: str
    format: SourceFormat = SourceFormat.CSV

    def load(self) -> NormalizedDataset:
        if self.format is SourceFormat.CSV:
            snapshots = tuple(_load_csv_rows(self.path, self.venue, self.symbol, self.source))
        elif self.format is SourceFormat.JSONL:
            snapshots = tuple(_load_jsonl_rows(self.path, self.venue, self.symbol, self.source))
        else:
            raise ValueError(f"unsupported format: {self.format}")
        return NormalizedDataset(venue=self.venue, symbol=self.symbol, snapshots=snapshots)


def _load_csv_rows(path: Path, venue: str, symbol: str, source: str) -> Iterable[MarketSnapshot]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield _row_to_snapshot(row, venue, symbol, source)


def _load_jsonl_rows(path: Path, venue: str, symbol: str, source: str) -> Iterable[MarketSnapshot]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            yield _row_to_snapshot(json.loads(line), venue, symbol, source)


def _row_to_snapshot(row: dict[str, object], venue: str, symbol: str, source: str) -> MarketSnapshot:
    ts = _parse_timestamp(str(row["ts"]))
    return MarketSnapshot(
        ts=ts,
        venue=str(row.get("venue", venue)),
        symbol=str(row.get("symbol", symbol)),
        bid=_maybe_float(row.get("bid")),
        ask=_maybe_float(row.get("ask")),
        last=_maybe_float(row.get("last")),
        mark=_maybe_float(row.get("mark")),
        index=_maybe_float(row.get("index")),
        funding_rate_bps=_maybe_float(row.get("funding_rate_bps")),
        open_interest=_maybe_float(row.get("open_interest")),
        source=str(row.get("source", source)),
    )


def _maybe_float(value: object | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

