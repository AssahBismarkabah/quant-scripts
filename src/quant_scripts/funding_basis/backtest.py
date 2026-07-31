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

    def summary(self) -> dict[str, float | str | None]:
        return {
            "entry_time": self.trade.entry_time.isoformat(),
            "exit_time": self.trade.exit_time.isoformat(),
            "funding_bps": self.trade.funding_received_bps,
            "basis_bps": self.trade.basis_capture_bps,
            "gross_edge_bps": self.trade.gross_edge_bps(),
            "cost_bps": self.trade.cost_bps(),
            "net_edge_bps": self.trade.net_edge_bps(),
            "accepted": self.accepted,
            "rejection_reason": self.rejection_reason,
        }


@dataclass
class FundingBasisBacktest:
    minimum_net_edge_bps: float = 0.0
    minimum_basis_capture_bps: float = 0.0
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
            rejection_reason = None
            if not accepted:
                rejection_reason = _classify_rejection(trade, self.minimum_net_edge_bps, self.minimum_basis_capture_bps)
            self.results.append(
                FundingBasisTradeResult(
                    decision=decision,
                    trade=trade,
                    accepted=accepted,
                    rejection_reason=rejection_reason,
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


def _classify_rejection(
    trade: FundingBasisTrade,
    minimum_net_edge_bps: float,
    minimum_basis_capture_bps: float,
) -> str:
    if trade.funding_received_bps <= 0:
        return "funding not positive"
    if trade.basis_capture_bps < minimum_basis_capture_bps:
        return f"basis capture below threshold ({trade.basis_capture_bps:.6f} bps < {minimum_basis_capture_bps:.6f} bps)"
    if trade.gross_edge_bps() < trade.cost_bps():
        return "costs exceed gross edge"
    return f"net edge below threshold ({trade.net_edge_bps():.6f} bps < {minimum_net_edge_bps:.6f} bps)"
