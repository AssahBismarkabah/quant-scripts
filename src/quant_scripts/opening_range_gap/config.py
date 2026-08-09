"""Pre-registered study parameters for the opening-range / gap trio.

Frozen before the study runs (see IA/opening-range-gap-strategies-research-spec.md
§8). These implement the rule set extracted verbatim from the transcript's three
named strategies. Changing any value after results would invalidate the
pre-registration, so treat this module as immutable during a run.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StudyParams:
    # --- instrument / data ---
    symbol: str = "NQ.n.0"        # Databento continuous symbol, lead contract
    dataset: str = "GLBX.MDP3"
    tz: str = "America/New_York"

    # --- RTH session (ET) ---
    rth_start: str = "09:30"
    rth_end: str = "16:00"

    # --- bars ---
    base_min: int = 1     # 1-min base (levels/range built from 1-min)
    exec_min: int = 5     # 5-min execution bars (entry confirmation + fill)

    # --- ORB (frozen) ---
    orb_range_min: int = 15        # first 15-min RTH range
    orb_target_rr: float = 2.0     # target = stop distance * 2  (1:2 RR)
    orb_no_entry_before: str = "09:50"   # earliest 5-min bar fill (range complete at 09:45)

    # --- Gap Fill (frozen) ---
    gap_fill_no_entry_before: str = "09:50"
    gap_fill_exit: str = "15:55"   # flat at session close if not filled

    # --- Oops (frozen) ---
    oops_min_gap_pts: float = 20.0
    oops_no_entry_before: str = "09:50"
    oops_target_rr: float = 1.0    # 1:1 RR
    oops_stop_buffer_pts: float = 2.0  # stop just beyond the level

    # --- shared timing ---
    no_new_entries_after: str = "15:00"
    force_flat: str = "15:55"

    # --- guard rails ---
    max_positions: int = 1

    # --- friction (futures, pts round trip) ---
    friction_base_pts: float = 0.5
    friction_stress_pts: float = 1.0

    # --- split (immutable) ---
    is_start: str = "2014-01-01"
    is_end: str = "2018-12-31"
    oos_start: str = "2019-01-01"
    oos_end: str = "2026-08-07"

    # --- bootstrap ---
    n_sims: int = 5000
    seed: int = 42
