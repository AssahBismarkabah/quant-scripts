from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .models import FundingBasisTrade, FundingEvent, MarketSnapshot, NormalizedDataset, TradeDecision
from .backtest import FundingBasisBacktest, FundingBasisTradeResult


@dataclass(frozen=True)
class FixtureReplayResult:
    funding: NormalizedDataset
    mark: NormalizedDataset
    spot: NormalizedDataset
    decisions: tuple[TradeDecision, ...]
    results: tuple[FundingBasisTradeResult, ...]


@dataclass(frozen=True)
class ReplayRegimeSummary:
    label: str
    decisions: int
    accepted: int
    rejected: int
    avg_net_edge_bps: float


def load_fixture_dataset(path: Path) -> NormalizedDataset:
    payload = json.loads(path.read_text(encoding="utf-8"))
    snapshots = tuple(
        MarketSnapshot(
            ts=datetime.fromisoformat(snapshot["ts"]),
            venue=snapshot["venue"],
            symbol=snapshot["symbol"],
            bid=snapshot.get("bid"),
            ask=snapshot.get("ask"),
            last=snapshot.get("last"),
            mark=snapshot.get("mark"),
            index=snapshot.get("index"),
            funding_rate_bps=snapshot.get("funding_rate_bps"),
            open_interest=snapshot.get("open_interest"),
            source=snapshot.get("source"),
        )
        for snapshot in payload["snapshots"]
    )
    return NormalizedDataset(venue=payload["venue"], symbol=payload["symbol"], snapshots=snapshots)


def nearest_snapshot(dataset: NormalizedDataset, target: datetime) -> MarketSnapshot:
    eligible = [snapshot for snapshot in dataset.snapshots if snapshot.ts <= target]
    if not eligible:
        raise ValueError(f"no snapshot available before {target.isoformat()}")
    return max(eligible, key=lambda snapshot: snapshot.ts)


def build_replay_decision(
    funding: NormalizedDataset,
    mark: NormalizedDataset,
    spot: NormalizedDataset,
    *,
    entry_buffer_minutes: int = 10,
    exit_buffer_minutes: int = 10,
    notional: float = 10_000.0,
) -> TradeDecision:
    funding_snapshot = funding.snapshots[-1]
    event = FundingEvent(
        funding_time=funding_snapshot.ts,
        entry_buffer=_minutes(entry_buffer_minutes),
        exit_buffer=_minutes(exit_buffer_minutes),
    )
    entry_time = event.entry_window_end()
    exit_time = event.exit_window_start()
    entry_mark = nearest_snapshot(mark, entry_time)
    exit_mark = nearest_snapshot(mark, exit_time)
    entry_spot = nearest_snapshot(spot, entry_time)
    exit_spot = nearest_snapshot(spot, exit_time)
    funding_rate_bps = funding_snapshot.funding_rate_bps or 0.0
    basis_capture_bps = ((exit_mark.mark or exit_mark.last or 0.0) - (entry_mark.mark or entry_mark.last or 0.0))
    spot_move_bps = ((exit_spot.last or 0.0) - (entry_spot.last or 0.0))
    return TradeDecision(
        event=event,
        entry_time=entry_time,
        exit_time=exit_time,
        notional=notional,
        entry_spread_bps=0.5,
        exit_spread_bps=0.5,
        estimated_funding_bps=funding_rate_bps,
        basis_capture_bps=basis_capture_bps - spot_move_bps,
        fees_bps=0.2,
        slippage_bps=0.3,
        liquidation_risk_bps=0.0,
    )


def build_replay_decisions(
    funding: NormalizedDataset,
    mark: NormalizedDataset,
    spot: NormalizedDataset,
    *,
    entry_buffer_minutes: int = 10,
    exit_buffer_minutes: int = 10,
    notional: float = 10_000.0,
) -> tuple[TradeDecision, ...]:
    decisions: list[TradeDecision] = []
    for funding_snapshot in funding.snapshots:
        event = FundingEvent(
            funding_time=funding_snapshot.ts,
            entry_buffer=_minutes(entry_buffer_minutes),
            exit_buffer=_minutes(exit_buffer_minutes),
        )
        entry_time = event.entry_window_end()
        exit_time = event.exit_window_start()
        try:
            entry_mark = nearest_snapshot(mark, entry_time)
            exit_mark = nearest_snapshot(mark, exit_time)
            entry_spot = nearest_snapshot(spot, entry_time)
            exit_spot = nearest_snapshot(spot, exit_time)
        except ValueError:
            continue

        funding_rate_bps = funding_snapshot.funding_rate_bps or 0.0
        basis_capture_bps = ((exit_mark.mark or exit_mark.last or 0.0) - (entry_mark.mark or entry_mark.last or 0.0))
        spot_move_bps = ((exit_spot.last or 0.0) - (entry_spot.last or 0.0))
        decisions.append(
            TradeDecision(
                event=event,
                entry_time=entry_time,
                exit_time=exit_time,
                notional=notional,
                entry_spread_bps=0.5,
                exit_spread_bps=0.5,
                estimated_funding_bps=funding_rate_bps,
                basis_capture_bps=basis_capture_bps - spot_move_bps,
                fees_bps=0.2,
                slippage_bps=0.3,
                liquidation_risk_bps=0.0,
            )
        )
    return tuple(decisions)


def replay_fixture_set_many(
    funding_path: Path,
    mark_path: Path,
    spot_path: Path,
    *,
    minimum_net_edge_bps: float = 0.0,
    minimum_basis_capture_bps: float = 0.0,
) -> FixtureReplayResult:
    funding = load_fixture_dataset(funding_path)
    mark = load_fixture_dataset(mark_path)
    spot = load_fixture_dataset(spot_path)
    decisions = build_replay_decisions(funding, mark, spot)
    results = tuple(
        FundingBasisBacktest(
            minimum_net_edge_bps=minimum_net_edge_bps,
            minimum_basis_capture_bps=minimum_basis_capture_bps,
        ).run(dataset=funding, decisions=decisions)
    )
    return FixtureReplayResult(
        funding=funding,
        mark=mark,
        spot=spot,
        decisions=decisions,
        results=results,
    )


def summarize_regimes(
    replay: FixtureReplayResult,
) -> tuple[ReplayRegimeSummary, ReplayRegimeSummary]:
    if not replay.decisions:
        empty = ReplayRegimeSummary(label="empty", decisions=0, accepted=0, rejected=0, avg_net_edge_bps=0.0)
        return empty, empty

    midpoint = replay.decisions[len(replay.decisions) // 2].event.funding_time
    first_results = [result for result in replay.results if result.decision.event.funding_time <= midpoint]
    second_results = [result for result in replay.results if result.decision.event.funding_time > midpoint]
    return _summarize_bucket("first_half", first_results), _summarize_bucket("second_half", second_results)


def replay_fixture_set(
    funding_path: Path,
    mark_path: Path,
    spot_path: Path,
) -> FixtureReplayResult:
    replay_many = replay_fixture_set_many(funding_path, mark_path, spot_path)
    first_decision = replay_many.decisions[0]
    first_result = replay_many.results[0]
    return FixtureReplayResult(
        funding=replay_many.funding,
        mark=replay_many.mark,
        spot=replay_many.spot,
        decisions=(first_decision,),
        results=(first_result,),
    )


def _minutes(value: int):
    from datetime import timedelta

    return timedelta(minutes=value)


def _summarize_bucket(label: str, results: list[FundingBasisTradeResult]) -> ReplayRegimeSummary:
    accepted = sum(1 for result in results if result.accepted)
    return ReplayRegimeSummary(
        label=label,
        decisions=len(results),
        accepted=accepted,
        rejected=len(results) - accepted,
        avg_net_edge_bps=sum(result.trade.net_edge_bps() for result in results) / len(results) if results else 0.0,
    )
