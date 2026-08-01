from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class GEXRegime(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    FLAT = "flat"


@dataclass(frozen=True)
class GEXContract:
    option_type: str
    strike: float
    expiration: datetime
    open_interest: float
    gamma: float
    contract_multiplier: float = 100.0

    def contract_gex(self, underlying_price: float) -> float:
        return self.gamma * self.open_interest * self.contract_multiplier * (underlying_price**2) * 0.01


@dataclass(frozen=True)
class GEXDataPoint:
    snapshot_time: datetime
    underlying_symbol: str
    underlying_price: float
    contracts: tuple[GEXContract, ...] = field(default_factory=tuple)
    exclude_0dte: bool = True

    def sorted_contracts(self) -> tuple[GEXContract, ...]:
        return tuple(sorted(self.contracts, key=lambda item: (item.expiration, item.strike, item.option_type)))


@dataclass(frozen=True)
class IntradayBar:
    ts: datetime
    open: float
    high: float
    low: float
    close: float

    def range(self) -> float:
        return self.high - self.low


@dataclass(frozen=True)
class SPXGEXTradeDecision:
    regime: GEXRegime
    entry_time: datetime
    exit_time: datetime
    lookback_return_bps: float
    direction: int
    entry_price: float
    exit_price: float
    notional: float
    slippage_bps: float
    commission_bps: float
    sec_fee_bps: float

    def gross_edge_bps(self) -> float:
        return self.direction * (self.exit_price - self.entry_price) / self.entry_price * 10_000

    def cost_bps(self) -> float:
        return self.slippage_bps + self.commission_bps + self.sec_fee_bps

    def net_edge_bps(self) -> float:
        return self.gross_edge_bps() - self.cost_bps()


def calculate_dealer_gex(point: GEXDataPoint) -> float:
    aggregate = 0.0
    for contract in point.contracts:
        if point.exclude_0dte and contract.expiration.date() == point.snapshot_time.date():
            continue
        aggregate += contract.contract_gex(point.underlying_price)
    return -1.0 * aggregate


def classify_regime(dealer_gex: float, flat_threshold: float = 0.0) -> GEXRegime:
    if dealer_gex > flat_threshold:
        return GEXRegime.POSITIVE
    if dealer_gex < -flat_threshold:
        return GEXRegime.NEGATIVE
    return GEXRegime.FLAT


def build_gex_data_point(
    snapshot_time: datetime,
    underlying_symbol: str,
    underlying_price: float,
    contracts: list[GEXContract],
    exclude_0dte: bool = True,
) -> GEXDataPoint:
    return GEXDataPoint(
        snapshot_time=snapshot_time,
        underlying_symbol=underlying_symbol,
        underlying_price=underlying_price,
        contracts=tuple(contracts),
        exclude_0dte=exclude_0dte,
    )


def summarize_contracts(point: GEXDataPoint) -> dict[str, float]:
    aggregate = sum(
        contract.contract_gex(point.underlying_price)
        for contract in point.contracts
        if not (point.exclude_0dte and contract.expiration.date() == point.snapshot_time.date())
    )
    dealer = -1.0 * aggregate
    return {"aggregate_gex": aggregate, "dealer_gex": dealer}


def validate_gex_data_point(point: GEXDataPoint) -> None:
    if point.underlying_symbol != "SPX":
        raise ValueError("underlying_symbol must be SPX")
    if point.underlying_price <= 0:
        raise ValueError("underlying_price must be positive")
    if not point.contracts:
        raise ValueError("contracts must not be empty")
