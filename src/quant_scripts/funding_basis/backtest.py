from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .models import FundingBasisTrade, NormalizedDataset, TradeDecision, validate_trade_window


@dataclass(frozen=True)
class FundingBasisTradeResult:
    decision: TradeDecision
    trade: FundingBasisTrade
    accepted: bool
    rejection_reason: str | None = None


@dataclass
class FundingBasisBacktest:
    minimum_net_edge_bps: float = 0.0
    results: list[FundingBasisTradeResult] = field(default_factory=list)

    def run(
        self,
        dataset: NormalizedDataset | None,
        decisions: Iterable[TradeDecision],
    ) -> list[FundingBasisTradeResult]:
        self.results = []
        for decision in decisions:
            try:
                validate_trade_window(decision.event, decision.entry_time, decision.exit_time)
            except ValueError as exc:
                result = FundingBasisTradeResult(
                    decision=decision,
                    trade=_build_trade(decision),
                    accepted=False,
                    rejection_reason=str(exc),
                )
                self.results.append(result)
                continue

            trade = _build_trade(decision)
            accepted = trade.net_edge_bps() >= self.minimum_net_edge_bps
            self.results.append(
                FundingBasisTradeResult(
                    decision=decision,
                    trade=trade,
                    accepted=accepted,
                    rejection_reason=None if accepted else "net edge below threshold",
                )
            )
        return self.results


def _build_trade(decision: TradeDecision) -> FundingBasisTrade:
    return FundingBasisTrade(
        entry_time=decision.entry_time,
        exit_time=decision.exit_time,
        entry_spread_bps=decision.entry_spread_bps,
        exit_spread_bps=decision.exit_spread_bps,
        funding_received_bps=decision.estimated_funding_bps,
        basis_capture_bps=decision.basis_capture_bps,
        fees_bps=decision.fees_bps,
        slippage_bps=decision.slippage_bps,
        liquidation_risk_bps=decision.liquidation_risk_bps,
        notional=decision.notional,
    )
