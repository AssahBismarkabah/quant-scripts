from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Literal


class MarginMode(str, Enum):
    ISOLATED = "isolated"
    CROSS = "cross"
    PORTFOLIO = "portfolio"


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class SourceFormat(str, Enum):
    CSV = "csv"
    JSONL = "jsonl"


@dataclass(frozen=True)
class MarketSnapshot:
    ts: datetime
    venue: str
    symbol: str
    bid: float | None = None
    ask: float | None = None
    last: float | None = None
    mark: float | None = None
    index: float | None = None
    funding_rate_bps: float | None = None
    open_interest: float | None = None
    source: str | None = None


@dataclass(frozen=True)
class FundingEvent:
    funding_time: datetime
    entry_buffer: timedelta
    exit_buffer: timedelta

    def entry_window_end(self) -> datetime:
        return self.funding_time - self.entry_buffer

    def exit_window_start(self) -> datetime:
        return self.funding_time + self.exit_buffer

    def is_exact_timestamp_trade(self, entry_time: datetime, exit_time: datetime) -> bool:
        return entry_time == self.funding_time or exit_time == self.funding_time


@dataclass(frozen=True)
class MarginAssumptions:
    mode: MarginMode
    spot_can_collateralize_perp: bool

    def capital_multiplier(self) -> float:
        if self.mode is MarginMode.ISOLATED:
            return 2.0
        if self.mode is MarginMode.CROSS and self.spot_can_collateralize_perp:
            return 1.0
        return 1.5


@dataclass(frozen=True)
class WickStressResult:
    liquidation_hit: bool
    worst_mark_price: float


@dataclass(frozen=True)
class FundingBasisTrade:
    entry_time: datetime
    exit_time: datetime
    entry_spread_bps: float
    exit_spread_bps: float
    funding_received_bps: float
    basis_capture_bps: float
    fees_bps: float
    slippage_bps: float
    liquidation_risk_bps: float
    notional: float

    def net_edge_bps(self) -> float:
        return (
            self.funding_received_bps
            + self.basis_capture_bps
            - self.entry_spread_bps
            - self.exit_spread_bps
            - self.fees_bps
            - self.slippage_bps
            - self.liquidation_risk_bps
        )

    def net_pnl(self) -> float:
        return self.notional * self.net_edge_bps() / 10_000.0

    def gross_edge_bps(self) -> float:
        return self.funding_received_bps + self.basis_capture_bps

    def cost_bps(self) -> float:
        return self.entry_spread_bps + self.exit_spread_bps + self.fees_bps + self.slippage_bps + self.liquidation_risk_bps


@dataclass(frozen=True)
class TradeDecision:
    event: FundingEvent
    entry_time: datetime
    exit_time: datetime
    notional: float
    entry_spread_bps: float
    exit_spread_bps: float
    estimated_funding_bps: float
    basis_capture_bps: float
    fees_bps: float
    slippage_bps: float
    liquidation_risk_bps: float


@dataclass(frozen=True)
class NormalizedDataset:
    venue: str
    symbol: str
    snapshots: tuple[MarketSnapshot, ...] = field(default_factory=tuple)

    def sorted_snapshots(self) -> tuple[MarketSnapshot, ...]:
        return tuple(sorted(self.snapshots, key=lambda item: item.ts))


def build_funding_event(
    funding_time_utc: datetime,
    entry_buffer_minutes: int = 10,
    exit_buffer_minutes: int = 10,
) -> FundingEvent:
    if funding_time_utc.tzinfo is None:
        raise ValueError("funding_time_utc must be timezone-aware")
    if funding_time_utc.tzinfo != timezone.utc:
        funding_time_utc = funding_time_utc.astimezone(timezone.utc)
    return FundingEvent(
        funding_time=funding_time_utc,
        entry_buffer=timedelta(minutes=entry_buffer_minutes),
        exit_buffer=timedelta(minutes=exit_buffer_minutes),
    )


def wick_stress(
    long_liquidation_price: float,
    short_liquidation_price: float,
    observed_low: float,
    observed_high: float,
) -> WickStressResult:
    liquidation_hit = observed_low <= short_liquidation_price or observed_high >= long_liquidation_price
    worst_mark_price = observed_low if liquidation_hit else observed_high
    return WickStressResult(liquidation_hit=liquidation_hit, worst_mark_price=worst_mark_price)


def validate_trade_window(
    event: FundingEvent,
    entry_time: datetime,
    exit_time: datetime,
) -> None:
    if entry_time.tzinfo is None or exit_time.tzinfo is None:
        raise ValueError("entry_time and exit_time must be timezone-aware")
    if entry_time >= exit_time:
        raise ValueError("entry_time must be before exit_time")
    if event.is_exact_timestamp_trade(entry_time, exit_time):
        raise ValueError("trade may not assume fills at the exact funding timestamp")
    if entry_time > event.entry_window_end():
        raise ValueError("entry_time must be before the funding assessment buffer")
    if exit_time < event.exit_window_start():
        raise ValueError("exit_time must be after the funding assessment buffer")
