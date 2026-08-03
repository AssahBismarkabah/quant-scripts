from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class Venue(str, Enum):
    SP600 = "sp600"
    SP400 = "sp400"
    R2000 = "r2000"
    SP500 = "sp500"  # control / cross-check only, excluded from study


class EventAction(str, Enum):
    ADDITION = "addition"
    DELETION = "deletion"


class ReasonCategory(str, Enum):
    DISCRETIONARY = "discretionary"
    M_A = "m_a"
    BANKRUPTCY = "bankruptcy"
    SPINOFF = "spinoff"
    IPO = "ipo"
    OTHER = "other"


class EventStatus(str, Enum):
    CONFIRMED = "confirmed"  # >=2 agreeing sources, discretionary
    UNVERIFIED = "unverified"  # single source
    RECONCILED = "reconciled"  # sources disagree; excluded until resolved
    DROPPED = "dropped"  # excluded (non-discretionary, insufficient history, etc.)


class ExitReason(str, Enum):
    WINDOW_END = "window_end"
    DELISTING = "delisting"
    STOP_LOSS = "stop_loss"
    DATA_END = "data_end"  # window extends past data_end; excluded from stats


@dataclass(frozen=True)
class IndexEvent:
    venue: Venue
    ticker: str
    company_name: str
    action: EventAction
    announcement_date: date
    effective_date: date
    reason_category: ReasonCategory
    reason_source: str
    source_primary: str
    sources: tuple[str, ...] = ()
    status: EventStatus = EventStatus.UNVERIFIED
    weight: float | None = None

    @property
    def event_id(self) -> str:
        return f"{self.venue.value}|{self.ticker}|{self.action.value}|{self.effective_date.isoformat()}"


@dataclass(frozen=True)
class DailyBar:
    ts_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class EventWindowResult:
    event_id: str
    venue: Venue
    ticker: str
    action: EventAction
    entry_date: date
    exit_date: date
    window_td: int
    gross_bps: float
    net_bps: float
    benchmark_bps: float
    abnormal_bps: float
    cost_bps: float
    exit_reason: ExitReason
    completed: bool


@dataclass(frozen=True)
class StudySummary:
    venue: Venue
    action: EventAction
    window_td: int
    n_events: int
    n_completed: int
    mean_abnormal_bps: float
    median_abnormal_bps: float
    t_stat: float
    win_rate: float
    cost_bps: float
    mean_net_bps: float


__all__ = [
    "Venue",
    "EventAction",
    "ReasonCategory",
    "EventStatus",
    "ExitReason",
    "IndexEvent",
    "DailyBar",
    "EventWindowResult",
    "StudySummary",
]
