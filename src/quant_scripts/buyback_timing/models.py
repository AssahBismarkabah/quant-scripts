"""Data models for the buyback-timing event study."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class BuybackEvent:
    """A distinct issuer repurchase-program announcement (the Tier A signal)."""

    cik: str
    ticker: str | None = None
    company: str = ""
    announcement_date: date | None = None   # filing date (t)
    adsh: str = ""                            # EDGAR accession (provenance)
    item_801: bool = False                    # disclosed via item 8.01
    cell: str = ""                            # SP500 | SP600 (assigned later)

    @property
    def entry_date(self) -> date | None:
        # open of day t+1 (signal known at close of t); see entry_lag in study
        return self.announcement_date


@dataclass
class EventStudyResult:
    cell: str = ""
    n_events: int = 0
    n_events_by_year: dict = field(default_factory=dict)
    primary_car: str = ""
    cars: dict = field(default_factory=dict)          # horizon -> {raw_bps, net_bps, tstat}
    control_excess_bps: float = 0.0                   # raw CAR - matched-control CAR
    beats_control: bool = False
    beta_adjusted_excess_bps: float = 0.0
    split_same_sign: bool = False
    is_bps: float = 0.0
    oos_bps: float = 0.0
    persistence: bool = False                          # positive in X-of-years
    drop_best_bps: float = 0.0
    bootstrap_p5_bps: float = 0.0
    bootstrap_p_negative: float = 0.0
    gates: dict = field(default_factory=dict)
    gates_pass: bool = False
