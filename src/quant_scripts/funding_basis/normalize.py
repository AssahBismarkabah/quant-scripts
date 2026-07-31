from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from .models import MarketSnapshot, NormalizedDataset


def funding_rate_rows_to_dataset(
    rows: Iterable[dict[str, Any]],
    venue: str,
    symbol: str,
    source: str,
) -> NormalizedDataset:
    snapshots = tuple(
        MarketSnapshot(
            ts=_parse_ms(row["fundingTime"]),
            venue=venue,
            symbol=symbol,
            bid=None,
            ask=None,
            last=None,
            mark=None,
            index=None,
            funding_rate_bps=float(row["fundingRate"]) * 10_000.0,
            open_interest=None,
            source=source,
        )
        for row in rows
    )
    return NormalizedDataset(venue=venue, symbol=symbol, snapshots=snapshots)


def spot_klines_to_dataset(
    rows: Iterable[list[Any]],
    venue: str,
    symbol: str,
    source: str,
) -> NormalizedDataset:
    snapshots = tuple(
        MarketSnapshot(
            ts=_parse_ms(row[0]),
            venue=venue,
            symbol=symbol,
            bid=None,
            ask=None,
            last=float(row[4]),
            mark=None,
            index=None,
            funding_rate_bps=None,
            open_interest=None,
            source=source,
        )
        for row in rows
    )
    return NormalizedDataset(venue=venue, symbol=symbol, snapshots=snapshots)


def mark_price_klines_to_dataset(
    rows: Iterable[list[Any]],
    venue: str,
    symbol: str,
    source: str,
) -> NormalizedDataset:
    snapshots = tuple(
        MarketSnapshot(
            ts=_parse_ms(row[0]),
            venue=venue,
            symbol=symbol,
            bid=None,
            ask=None,
            last=float(row[4]),
            mark=float(row[4]),
            index=None,
            funding_rate_bps=None,
            open_interest=None,
            source=source,
        )
        for row in rows
    )
    return NormalizedDataset(venue=venue, symbol=symbol, snapshots=snapshots)


def _parse_ms(value: int | float | str) -> datetime:
    return datetime.fromtimestamp(int(value) / 1000.0, tz=timezone.utc)
