from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from .models import EventAction, EventStatus, IndexEvent, ReasonCategory, Venue
from .utils import append_log


def _as_date(value) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def spdji_chain_to_events(
    releases: list[dict[str, object]],
    *,
    min_announcement: date | None = None,
    max_effective: date | None = None,
) -> list[IndexEvent]:
    """Expand parsed S&P DJI releases into IndexEvents.

    Each release has announcement_date (from the URL slug) and a chain of
    (venue, action, ticker, company) links with one effective_date per release.
    """
    events: list[IndexEvent] = []
    for release in releases:
        ann_date = _as_date(release.get("announcement_date"))
        if ann_date is None:
            continue
        if min_announcement is not None and ann_date < min_announcement:
            continue
        for link in release.get("chain", []):
            ticker = str(link.get("ticker", "")).strip()
            venue = link.get("venue")
            if isinstance(venue, str):
                venue = Venue(venue)
            action = link.get("action")
            # table rows carry their own effective date; prose releases share
            # one effective date per release
            eff_date = _as_date(link.get("effective_date") or release.get("effective_date"))
            if not ticker or venue is None or action not in ("addition", "deletion"):
                continue
            if eff_date is None:
                continue
            if max_effective is not None and eff_date > max_effective:
                continue
            reason = link.get("reason") or ReasonCategory.DISCRETIONARY
            if isinstance(reason, str):
                reason = ReasonCategory(reason)
            events.append(
                IndexEvent(
                    venue=venue,
                    ticker=ticker,
                    company_name=str(link.get("company_name", "")),
                    action=EventAction(action),
                    announcement_date=ann_date,
                    effective_date=eff_date,
                    reason_category=reason,
                    reason_source="spdji_text",
                    source_primary="spdji_press",
                    sources=("spdji_press",),
                    status=EventStatus.UNVERIFIED,
                )
            )
    return events


def reconcile(
    spdji_events: list[IndexEvent],
    cross_rows: list[dict[str, object]],
    *,
    log_path: Path,
) -> list[IndexEvent]:
    """Stamp each S&P DJI event with cross-source agreement.

    Match key: (ticker, action, effective_date) against the cross rows
    (Wikipedia / tickerleague). Cross rows use 'date' as the effective date.

    status:
      - confirmed: matched by >=1 cross source (>=2 sources total, one is
        always spdji_press)
      - unverified: no cross match
      - reconciled: cross source disagrees on reason; excluded until resolved
    """
    cross_keys: dict[tuple[str, str, date], list[dict[str, object]]] = {}
    for row in cross_rows:
        key = (
            str(row.get("ticker", "")).strip().upper(),
            str(row.get("action", "")),
            row.get("date"),
        )
        if isinstance(key[2], date):
            cross_keys.setdefault(key, []).append(row)

    result: list[IndexEvent] = []
    hard_exclude = {ReasonCategory.M_A, ReasonCategory.BANKRUPTCY, ReasonCategory.SPINOFF}
    for ev in spdji_events:
        key = (ev.ticker.upper(), ev.action.value, ev.effective_date)
        matches = cross_keys.get(key, [])
        if matches:
            reasons = {m.get("reason") for m in matches if m.get("reason") is not None}
            # reasons may be ReasonCategory or str; normalize
            reasons = {r if isinstance(r, ReasonCategory) else ReasonCategory(r) for r in reasons}
            cross_exclude = bool(reasons & hard_exclude)
            spdji_exclude = ev.reason_category in hard_exclude
            if cross_exclude != spdji_exclude and reasons:
                # sources disagree on whether the event is study-eligible
                # (M&A/bankruptcy/spin-off vs discretionary) -> exclude until
                # resolved; agreement on 'other' does not trigger exclusion
                cross_reason = next(iter(reasons & hard_exclude)) if cross_exclude else next(iter(reasons))
                append_log(
                    log_path,
                    {
                        "event_id": ev.event_id,
                        "decision": "reason_conflict",
                        "spdji_reason": ev.reason_category.value,
                        "cross_reason": cross_reason.value,
                        "source": "reconcile",
                    },
                )
                ev = IndexEvent(
                    venue=ev.venue,
                    ticker=ev.ticker,
                    company_name=ev.company_name,
                    action=ev.action,
                    announcement_date=ev.announcement_date,
                    effective_date=ev.effective_date,
                    reason_category=cross_reason if cross_exclude else ev.reason_category,
                    reason_source="cross_sources" if cross_exclude else ev.reason_source,
                    source_primary=ev.source_primary,
                    sources=ev.sources + ("cross_sources",),
                    status=EventStatus.RECONCILED,
                )
            else:
                ev = IndexEvent(
                    venue=ev.venue,
                    ticker=ev.ticker,
                    company_name=ev.company_name,
                    action=ev.action,
                    announcement_date=ev.announcement_date,
                    effective_date=ev.effective_date,
                    reason_category=ev.reason_category,
                    reason_source=ev.reason_source,
                    source_primary=ev.source_primary,
                    sources=ev.sources + ("cross_sources",),
                    status=EventStatus.CONFIRMED,
                )
        else:
            ev = IndexEvent(
                venue=ev.venue,
                ticker=ev.ticker,
                company_name=ev.company_name,
                action=ev.action,
                announcement_date=ev.announcement_date,
                effective_date=ev.effective_date,
                reason_category=ev.reason_category,
                reason_source=ev.reason_source,
                source_primary=ev.source_primary,
                sources=ev.sources,
                status=EventStatus.UNVERIFIED,
            )
        result.append(ev)
    return result


def write_events_parquet(events: list[IndexEvent], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "event_id": ev.event_id,
            "venue": ev.venue.value,
            "ticker": ev.ticker,
            "company_name": ev.company_name,
            "action": ev.action.value,
            "announcement_date": ev.announcement_date,
            "effective_date": ev.effective_date,
            "reason_category": ev.reason_category.value,
            "reason_source": ev.reason_source,
            "source_primary": ev.source_primary,
            "sources": list(ev.sources),
            "status": ev.status.value,
            "weight": ev.weight,
        }
        for ev in events
    ]
    df = pd.DataFrame(rows)
    df.to_parquet(out_path, index=False)
    return out_path


def load_events_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def agreement_report(events: list[IndexEvent]) -> dict[str, object]:
    from collections import Counter

    total = len(events)
    status_counts = Counter(ev.status for ev in events)
    confirmed = status_counts.get(EventStatus.CONFIRMED, 0)
    return {
        "total_events": total,
        "status": {k.value: v for k, v in status_counts.items()},
        "confirmed_pct": round(100.0 * confirmed / total, 2) if total else 0.0,
        "by_venue": {
            venue.value: Counter(ev.status for ev in events if ev.venue == venue).get(EventStatus.CONFIRMED, 0)
            for venue in Venue
        },
    }


__all__ = [
    "spdji_chain_to_events",
    "reconcile",
    "write_events_parquet",
    "load_events_parquet",
    "agreement_report",
]
