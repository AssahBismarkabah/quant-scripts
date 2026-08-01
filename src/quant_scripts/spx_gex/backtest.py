from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import GEXDataPoint, GEXRegime, IntradayBar, SPXGEXTradeDecision, calculate_dealer_gex, classify_regime


@dataclass(frozen=True)
class SPXGEXTradeResult:
    decision: SPXGEXTradeDecision
    accepted: bool
    rejection_reason: str | None = None

    def summary(self) -> dict[str, object]:
        return {
            "entry_time": self.decision.entry_time.isoformat(),
            "exit_time": self.decision.exit_time.isoformat(),
            "regime": self.decision.regime.value,
            "lookback_return_bps": self.decision.lookback_return_bps,
            "gross_edge_bps": self.decision.gross_edge_bps(),
            "cost_bps": self.decision.cost_bps(),
            "net_edge_bps": self.decision.net_edge_bps(),
            "accepted": self.accepted,
            "rejection_reason": self.rejection_reason,
        }


@dataclass(frozen=True)
class SPXGEXBacktestSummary:
    sessions: int
    trades: int
    accepted: int
    rejected: int
    avg_gross_edge_bps: float
    avg_cost_bps: float
    avg_net_edge_bps: float
    positive_sessions: int
    negative_sessions: int
    flat_sessions: int

    def as_dict(self) -> dict[str, float | int]:
        return {
            "sessions": self.sessions,
            "trades": self.trades,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "avg_gross_edge_bps": self.avg_gross_edge_bps,
            "avg_cost_bps": self.avg_cost_bps,
            "avg_net_edge_bps": self.avg_net_edge_bps,
            "positive_sessions": self.positive_sessions,
            "negative_sessions": self.negative_sessions,
            "flat_sessions": self.flat_sessions,
        }


@dataclass
class SPXGEXBacktest:
    results: list[SPXGEXTradeResult] = field(default_factory=list)
    flat_threshold: float = 0.0
    slippage_bps: float = 1.0
    commission_bps: float = 0.0
    sec_fee_bps: float = 0.0

    def classify(self, point: GEXDataPoint) -> GEXRegime:
        return classify_regime(calculate_dealer_gex(point), flat_threshold=self.flat_threshold)

    def run(
        self,
        point: GEXDataPoint,
        bars: Iterable[IntradayBar],
        lookback_start_time: datetime,
        evaluation_time: datetime,
        entry_time: datetime,
        exit_time: datetime,
    ) -> list[SPXGEXTradeResult]:
        self.results = []
        regime = self.classify(point)
        if regime is GEXRegime.FLAT:
            return self.results

        ordered_bars = list(sorted(bars, key=lambda bar: bar.ts))
        entry_bar = next((bar for bar in ordered_bars if bar.ts == entry_time), None)
        exit_bar = next((bar for bar in ordered_bars if bar.ts == exit_time), None)
        lookback_start_bar = next((bar for bar in ordered_bars if bar.ts == lookback_start_time), None)
        lookback_bar = next((bar for bar in ordered_bars if bar.ts == evaluation_time), None)

        if entry_bar is None or exit_bar is None or lookback_bar is None or lookback_start_bar is None:
            self.results.append(
                SPXGEXTradeResult(
                    decision=_build_decision(
                        regime,
                        evaluation_time,
                        entry_time,
                        exit_time,
                        0.0,
                        0,
                        0.0,
                        0.0,
                        self.slippage_bps,
                        self.commission_bps,
                        self.sec_fee_bps,
                    ),
                    accepted=False,
                    rejection_reason="missing evaluation, entry, or exit bar",
                )
            )
            return self.results

        lookback_return_bps = (lookback_bar.close - lookback_start_bar.close) / lookback_start_bar.close * 10_000
        direction = _direction_from_regime(regime, lookback_return_bps)
        decision = _build_decision(
            regime,
            evaluation_time,
            entry_time,
            exit_time,
            lookback_return_bps,
            direction,
            entry_bar.close,
            exit_bar.close,
            self.slippage_bps,
            self.commission_bps,
            self.sec_fee_bps,
        )
        self.results.append(SPXGEXTradeResult(decision=decision, accepted=True))
        return self.results

    def summarize(self) -> SPXGEXBacktestSummary:
        if not self.results:
            return SPXGEXBacktestSummary(
                sessions=0,
                trades=0,
                accepted=0,
                rejected=0,
                avg_gross_edge_bps=0.0,
                avg_cost_bps=0.0,
                avg_net_edge_bps=0.0,
                positive_sessions=0,
                negative_sessions=0,
                flat_sessions=0,
            )
        accepted = sum(1 for result in self.results if result.accepted)
        return SPXGEXBacktestSummary(
            sessions=len(self.results),
            trades=len(self.results),
            accepted=accepted,
            rejected=len(self.results) - accepted,
            avg_gross_edge_bps=sum(result.decision.gross_edge_bps() for result in self.results) / len(self.results),
            avg_cost_bps=sum(result.decision.cost_bps() for result in self.results) / len(self.results),
            avg_net_edge_bps=sum(result.decision.net_edge_bps() for result in self.results) / len(self.results),
            positive_sessions=sum(1 for result in self.results if result.decision.regime is GEXRegime.POSITIVE),
            negative_sessions=sum(1 for result in self.results if result.decision.regime is GEXRegime.NEGATIVE),
            flat_sessions=sum(1 for result in self.results if result.decision.regime is GEXRegime.FLAT),
        )


def run_walk_forward(
    sessions: Iterable[tuple[GEXDataPoint, list[IntradayBar], datetime, datetime, datetime, datetime]],
    flat_threshold: float = 0.0,
    slippage_bps: float = 1.0,
    commission_bps: float = 0.0,
    sec_fee_bps: float = 0.0,
) -> tuple[SPXGEXBacktest, SPXGEXBacktestSummary]:
    backtest = SPXGEXBacktest(
        flat_threshold=flat_threshold,
        slippage_bps=slippage_bps,
        commission_bps=commission_bps,
        sec_fee_bps=sec_fee_bps,
    )
    for point, bars, lookback_start_time, evaluation_time, entry_time, exit_time in sessions:
        backtest.run(
            point=point,
            bars=bars,
            lookback_start_time=lookback_start_time,
            evaluation_time=evaluation_time,
            entry_time=entry_time,
            exit_time=exit_time,
    )
    return backtest, backtest.summarize()


def write_backtest_report(path: Path, backtest: SPXGEXBacktest, summary: SPXGEXBacktestSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "summary": summary.as_dict(),
                "results": [result.summary() for result in backtest.results],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _direction_from_regime(regime: GEXRegime, lookback_return_bps: float) -> int:
    if regime is GEXRegime.POSITIVE:
        return -1 if lookback_return_bps > 0 else 1
    if regime is GEXRegime.NEGATIVE:
        return 1 if lookback_return_bps > 0 else -1
    return 0


def _build_decision(
    regime: GEXRegime,
    evaluation_time: datetime,
    entry_time: datetime,
    exit_time: datetime,
    lookback_return_bps: float,
    direction: int,
    entry_price: float,
    exit_price: float,
    slippage_bps: float,
    commission_bps: float,
    sec_fee_bps: float,
) -> SPXGEXTradeDecision:
    return SPXGEXTradeDecision(
        regime=regime,
        entry_time=entry_time,
        exit_time=exit_time,
        lookback_return_bps=lookback_return_bps,
        direction=direction,
        entry_price=entry_price,
        exit_price=exit_price,
        notional=0.0,
        slippage_bps=slippage_bps,
        commission_bps=commission_bps,
        sec_fee_bps=sec_fee_bps,
    )
