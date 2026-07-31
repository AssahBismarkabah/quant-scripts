from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .models import MarketSnapshot, NormalizedDataset


@dataclass(frozen=True)
class DatasetValidationReport:
    row_count: int
    sorted: bool
    duplicate_timestamps: int
    missing_bid_ask: int
    missing_funding: int

    @property
    def is_valid(self) -> bool:
        return self.sorted and self.duplicate_timestamps == 0 and self.missing_bid_ask == 0


def validate_dataset(dataset: NormalizedDataset) -> DatasetValidationReport:
    snapshots = list(dataset.snapshots)
    sorted_snapshots = sorted(snapshots, key=lambda item: item.ts)
    sorted_ok = snapshots == sorted_snapshots
    duplicate_timestamps = _count_duplicates(snapshot.ts for snapshot in snapshots)
    missing_bid_ask = sum(1 for snapshot in snapshots if snapshot.bid is None or snapshot.ask is None)
    missing_funding = sum(1 for snapshot in snapshots if snapshot.funding_rate_bps is None)
    return DatasetValidationReport(
        row_count=len(snapshots),
        sorted=sorted_ok,
        duplicate_timestamps=duplicate_timestamps,
        missing_bid_ask=missing_bid_ask,
        missing_funding=missing_funding,
    )


def _count_duplicates(values: list[datetime] | tuple[datetime, ...] | object) -> int:
    seen: set[datetime] = set()
    duplicates = 0
    for value in values:
        if value in seen:
            duplicates += 1
        else:
            seen.add(value)
    return duplicates

