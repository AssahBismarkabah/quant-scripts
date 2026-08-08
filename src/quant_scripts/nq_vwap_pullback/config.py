"""Pre-registered study parameters for the NQ VWAP-pullback probe.

Frozen before the study runs (see IA/nq-vwap-pullback-research-spec.md).
These implement the rule set extracted verbatim from the source interview.
Changing any value after results would invalidate the pre-registration, so
treat this module as immutable during a run.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StudyParams:
    # --- instrument / data ---
    symbol: str = "NQ.n.0"        # Databento continuous symbol, lead contract
    dataset: str = "GLBX.MDP3"
    tz: str = "America/New_York"  # strategy is defined on ET (09:30..16:00)

    # --- time windows (ET) ---
    rth_start: str = "09:30"
    rth_end: str = "16:00"
    no_trade_until: str = "10:30"   # no trades 09:30..10:30
    no_new_trades_after: str = "15:30"
    force_flat: str = "15:55"

    # --- bars / VWAP ---
    exec_min: int = 5       # execution bars
    trend_min: int = 15     # trend bars
    vwap_min: int = 1       # VWAP base (correctness requirement: 1-min base)

    # --- frozen rule parameters ---
    drift_return_bps: float = 10.0      # +0.10% over past 1h (LONG) / -0.10% (SHORT)
    vwap_lookback_min: int = 15         # VWAP rising/falling over past 15 min
    long_risk_pts: float = 80.0
    long_target_pts: float = 40.0
    short_risk_pts: float = 80.0
    short_target_pts: float = 50.0

    # --- guard rails ---
    max_positions: int = 1
    max_trades_per_day: int = 4
    max_losses_per_day: int = 2

    # --- friction (futures, pts round trip) ---
    friction_base_pts: float = 0.5
    friction_stress_pts: float = 1.0

    # --- split (immutable) ---
    is_start: str = "2020-08-01"
    is_end: str = "2024-12-31"
    oos_start: str = "2025-01-01"
    oos_end: str = "2026-08-07"

    # --- bootstrap ---
    n_sims: int = 5000
    seed: int = 42

    # --- fetch robustness ---
    fetch_retries: int = 3   # per-chunk retries on transient Databento 504/stream drops
