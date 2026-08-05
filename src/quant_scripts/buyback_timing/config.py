"""Pre-registered study parameters for the buyback-timing candidate.

Frozen before the study runs (see IA/buyback-timing-research-spec.md). Changing
these after results would invalidate the pre-registration, so treat this as
immutable during a run.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StudyParams:
    # --- data / window ---
    harvest_start: str = "2023-03-01"   # Rule 10b5-1 cooling-off + daily-disclosure regime live
    harvest_end: str = "2026-07-31"
    # universe cells
    cells: tuple[str, ...] = ("SP500", "SP600")
    # --- signal ---
    # Tier A: entry open of day t+1 after the 8-K repurchase-program announcement.
    # (Tier B cooling-off and Tier C post-decline are reported-only in this study.)
    tier: str = "A"
    entry_lag_days: int = 1
    # --- event windows (CAR) ; primary + others reported-not-selected ---
    primary_car: str = "(+1,+20)"
    report_cars: tuple[str, ...] = ("(0,+1)", "(+1,+5)", "(+1,+10)", "(+1,+20)")
    # --- friction (round trip, bps) : base per cell, stress add-on ---
    friction_base_cell1_bps: float = 10.0   # S&P 500
    friction_base_cell2_bps: float = 20.0   # S&P 600
    friction_stress_add_bps: float = 30.0
    # --- matched control / beta adjustment ---
    # control matched on market-cap (size) within each cell, plus plain excess vs cell index
    match_controls: bool = True
    # --- bootstrap ---
    n_sims: int = 10_000
    seed: int = 42
    # --- selection to avoid spurious matches ---
    min_events_per_year: int = 20
    min_events_total: int = 60
    # delisted must be included in bars (survivorship-bias control)
    include_delisted: bool = True

    # derived
    @property
    def friction_base_bps(self) -> dict:
        return {"SP500": self.friction_base_cell1_bps, "SP600": self.friction_base_cell2_bps}
