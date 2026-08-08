"""Pre-registered study parameters for the IVAMR probe.

Frozen before the study runs (see IA/ivamr-research-spec.md). These implement
the rule set extracted verbatim from strategies/ivamr/IVAMR.md. Changing any
value after results would invalidate the pre-registration, so treat this module
as immutable during a run.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StudyParams:
    # --- instrument / data ---
    symbol: str = "NQ.n.0"          # Databento continuous symbol, lead contract
    dataset: str = "GLBX.MDP3"
    tz: str = "America/New_York"

    # --- RTH session (ET) ---
    rth_start: str = "09:30"
    rth_end: str = "16:00"

    # --- bars ---
    exec_min: int = 15              # entry bars (15-min)
    vwap_min: int = 1               # granularity for volume-at-price histogram base

    # --- volume profile (frozen, IVAMR spec) ---
    value_area_pct: float = 0.70    # 70% Value Area
    bin_size: float = 0.25          # index points per volume-at-price bin (1 tick ES/NQ)

    # --- time / risk filters (IVAMR 4.A) ---
    entry_start: str = "09:45"      # no entries before
    signal_cutoff: str = "14:15"    # stop evaluating new setups
    entry_end: str = "14:30"        # no new entries after
    hard_exit: str = "15:30"        # hard market-order time exit
    daily_kill_loss_frac: float = 0.03  # halt day if realized loss reaches 3% of equity
    max_positions: int = 1

    # --- play parameters (IVAMR 4.C) ---
    atr_period: int = 14            # 14-period 15-min ATR
    trend_stop_atr: float = 2.0     # Plays 1/2 stop = entry +/- 2.0 * ATR
    trend_be_atr: float = 1.5       # move to breakeven when +1.5 * ATR intra-bar
    trend_trail_period: int = 2     # trail at 2-period 15-min low/high
    rev_stop_atr: float = 0.5       # Plays 3/4 stop = trigger extreme +/- 0.5 * ATR
    rev_structural_atr: float = 0.5 # Plays 1/2 retest structural integrity buffer
    rev_min_rr: float = 1.5         # Play 3/4: target distance must be >= 1.5 * stop distance
    retest_zone_close: float = 0.60 # Play 3/4 close-in-zone threshold ((c-l)/(h-l) or (h-c)/(h-l))

    # --- friction (NQ futures, index points round trip) ---
    friction_base_pts: float = 0.5
    friction_stress_pts: float = 1.0

    # --- split (immutable; see spec 4) ---
    is_start: str = "2014-01-01"
    is_end: str = "2018-12-31"
    oos_start: str = "2019-01-01"
    oos_end: str = "2023-12-31"

    # --- bootstrap ---
    n_sims: int = 5000
    seed: int = 42

    # --- fetch robustness ---
    fetch_retries: int = 3
