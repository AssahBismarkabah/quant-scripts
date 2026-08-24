"""Frozen parameters for the daily earnings-anchored VWAP proxy.

These values implement IA/earnings-anchored-vwap-research-gate.md §§5-7.
They are researcher-authored design assumptions, frozen before any outcome is
loaded. Changing one creates a separate hypothesis.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StudyParams:
    # Data and timing audit
    warmup_start: str = "2012-01-01"
    is_start: str = "2013-01-01"
    is_end: str = "2016-12-31"
    oos_start: str = "2017-01-01"
    oos_end: str = "2021-06-14"
    timing_audit_size: int = 100
    timing_min_agreement: float = 0.95

    # Event eligibility
    atr_sessions: int = 20
    min_price: float = 5.0
    min_median_dollar_volume: float = 10_000_000.0
    reaction_search_sessions: int = 10
    max_holding_sessions: int = 10

    # Execution economics
    friction_base_bps_per_side: float = 20.0
    friction_stress_bps_per_side: float = 50.0

    # Decision gates
    min_oos_trades_per_side: int = 300
    max_gap_stop_loss_fraction: float = 0.40
    min_positive_complete_oos_years: int = 3
    complete_oos_years: tuple[int, ...] = (2017, 2018, 2019, 2020)

    # Inference
    bootstrap_simulations: int = 5_000
    bootstrap_seed: int = 42
