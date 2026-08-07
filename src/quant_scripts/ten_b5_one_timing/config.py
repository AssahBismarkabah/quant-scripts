"""Pre-registered study parameters for the 10b5-1 adoption-timing probe.

Frozen before the study runs (see IA/10b5-1-adoption-timing-research-spec.md).
Changing these after results would invalidate the pre-registration, so treat this
as immutable during a run.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StudyParams:
    # --- data / window ---
    # Regime: Rule 10b5-1 30-day issuer cooling-off (SEC 2022 amendments) live.
    # Bounded probe window matches the buyback-study comparability window (H1 2026).
    harvest_start: str = "2025-07-01"
    harvest_end: str = "2026-07-31"

    # --- signal / entry ---
    # Tier A: open of day t+1 after the 8-K 10b5-1 adoption (t).
    # Tier B (PRIMARY): enter ~30 sessions after adoption (cooling-off expiry), the
    # forward, non-lagged signal this probe isolates.
    # Tiers are independent pre-registered arms; the primary is Tier B.
    primary_tier: str = "B"
    entry_lag_days: int = 1          # Tier A
    cooling_off_sessions: int = 30   # Tier B

    # --- event windows (CAR) ; primary + others reported-not-selected ---
    primary_car: str = "(+1,+20)"
    report_cars: tuple[str, ...] = ("(+1,+5)", "(+1,+10)", "(+1,+20)")

    # --- friction (round trip, bps) ---
    friction_base_bps: float = 20.0   # conservative single-stock base
    friction_stress_add_bps: float = 20.0  # 40 bps stress

    # --- matched control / beta adjustment ---
    # control matched on market-cap (size) within the event universe, plus
    # plain excess vs SPY.
    match_controls: bool = True

    # --- bootstrap (the gate that failed buyback + vol-fade v2) ---
    n_sims: int = 10_000
    seed: int = 42

    # --- selection / sparsity gates ---
    min_events_total: int = 30
    min_liquid_events: int = 30       # price>=5, ADV filter
    price_min: float = 5.0
