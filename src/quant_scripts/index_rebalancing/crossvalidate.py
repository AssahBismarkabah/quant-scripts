from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from .models import EventAction, ReasonCategory, Venue
from .utils import fetch_bytes

_WIKIPEDIA_URLS = {
    Venue.SP400: "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies",
    Venue.SP600: "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies",
    Venue.SP500: "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
}
_TICKERLEAGUE_URLS = {
    Venue.SP500: "https://tickerleague.com/indices/stock/sp-500/additions-and-removals",
    Venue.SP400: "https://tickerleague.com/indices/stock/sp-400/additions-and-removals",
    Venue.SP600: "https://tickerleague.com/indices/stock/sp-600/additions-and-removals",
}

_MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}
_DATE_RE = re.compile(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})")

_REASON_MAP = {
    "acquisition": ReasonCategory.M_A,
    "acquired": ReasonCategory.M_A,
    "merger": ReasonCategory.M_A,
    "bankruptcy": ReasonCategory.BANKRUPTCY,
    "bankrupt": ReasonCategory.BANKRUPTCY,
    "spin-off": ReasonCategory.SPINOFF,
    "spin off": ReasonCategory.SPINOFF,
    "spinoff": ReasonCategory.SPINOFF,
    "resignation": ReasonCategory.OTHER,
    "market cap": ReasonCategory.DISCRETIONARY,
}


def fetch_wikipedia_changes(venue: Venue, out_path: Path) -> list[dict[str, object]]:
    """Fetch and parse the Wikipedia constituent-change table for a venue.

    Table columns: Date | Added (Ticker, Security) | Removed (Ticker, Security) | Reason.
    Returns rows: {date, ticker, company_name, action, reason, venue}.
    """
    url = _WIKIPEDIA_URLS.get(venue)
    if url is None:
        return []
    path = fetch_bytes(url, out_path)
    return parse_wikipedia_changes(path.read_text(encoding="utf-8", errors="replace"), venue)


def parse_wikipedia_changes(html: str, venue: Venue) -> list[dict[str, object]]:
    """Parse the Wikipedia change table. Not expected to be complete for
    400/600 (coverage stats recorded separately); used for cross-validation
    of dates, tickers, and reasons."""
    rows: list[dict[str, object]] = []
    # locate the table whose header contains Added/Removed/Reason
    header_idx = -1
    for match in re.finditer(r"<th[^>]*>\s*(Added)\s*</th>", html):
        header_idx = match.start()
        break
    if header_idx == -1:
        return rows
    seg = html[header_idx : header_idx + 500_000]
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", seg, re.S):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
        if len(cells) < 4:
            continue
        clean = [re.sub(r"<[^>]+>", " ", c) for c in cells]
        clean = [re.sub(r"\s+", " ", c).strip() for c in clean]
        date_str = clean[0]
        if date_str == "Date" or date_str == "":
            continue
        event_date = _parse_date(date_str)
        if event_date is None:
            continue
        if len(clean) >= 6:
            # 6-cell layout: Date | Added Ticker | Added Security | Removed Ticker | Removed Security | Reason
            added_ticker, added_security = clean[1], clean[2]
            removed_ticker, removed_security = clean[3], clean[4]
            reason_raw = clean[5]
        else:
            # 4-cell layout: Date | Added (Ticker+Security) | Removed (Ticker+Security) | Reason
            added = _parse_company(clean[1])
            removed = _parse_company(clean[2])
            added_ticker, added_security = (added["ticker"], added["security"]) if added else ("", "")
            removed_ticker, removed_security = (removed["ticker"], removed["security"]) if removed else ("", "")
            reason_raw = clean[3]
        reason = _classify_reason(reason_raw)
        if added_ticker:
            rows.append(
                {
                    "date": event_date,
                    "ticker": added_ticker,
                    "company_name": added_security,
                    "action": EventAction.ADDITION.value,
                    "reason": reason,
                    "venue": venue,
                }
            )
        if removed_ticker:
            rows.append(
                {
                    "date": event_date,
                    "ticker": removed_ticker,
                    "company_name": removed_security,
                    "action": EventAction.DELETION.value,
                    "reason": reason,
                    "venue": venue,
                }
            )
    return rows


def fetch_tickerleague_changes(venue: Venue, out_path: Path) -> list[dict[str, object]]:
    url = _TICKERLEAGUE_URLS.get(venue)
    if url is None:
        return []
    path = fetch_bytes(url, out_path)
    return parse_tickerleague_changes(path.read_text(encoding="utf-8", errors="replace"), venue)


def parse_tickerleague_changes(html: str, venue: Venue) -> list[dict[str, object]]:
    """Parse tickerleague additions/removals. Table format varies by page;
    rows contain company/ticker/date/type columns. If the page cannot be
    parsed, return [] and record the gap at reconcile time."""
    rows: list[dict[str, object]] = []
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    # tickerleague renders rows like: 'CompanyName (TICKER) Jan 05, 2024 Added'
    pattern = re.compile(
        r"([A-Z][A-Za-z0-9 .&'-]{2,60}?)\s*\(([A-Z0-9.\-]{1,5})\)\s+"
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})\s+(Added|Removed)"
    )
    for match in pattern.finditer(text):
        company = match.group(1).strip()
        ticker = match.group(2).strip()
        event_date = date(int(match.group(5)), _MONTHS[match.group(3)], int(match.group(4)))
        action = EventAction.ADDITION if match.group(6) == "Added" else EventAction.DELETION
        rows.append(
            {
                "date": event_date,
                "ticker": ticker,
                "company_name": company,
                "action": action.value,
                "reason": None,
                "venue": venue,
            }
        )
    return rows


def _parse_date(text: str) -> date | None:
    match = _DATE_RE.search(text)
    if not match:
        return None
    return date(int(match.group(3)), _MONTHS[match.group(1)], int(match.group(2)))


def _parse_company(cell: str) -> dict[str, str] | None:
    # cell: 'TICKER\nSecurity' or 'TICKER Security'
    parts = re.split(r"\s{2,}|\n", cell)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return None
    ticker = parts[0]
    security = " ".join(parts[1:]) if len(parts) > 1 else ""
    if not re.match(r"^[A-Z0-9.\-]{1,6}$", ticker):
        return None
    return {"ticker": ticker, "security": security}


def _classify_reason(text: str) -> ReasonCategory:
    lower = text.lower()
    for key, category in _REASON_MAP.items():
        if key in lower:
            return category
    return ReasonCategory.OTHER


__all__ = [
    "fetch_wikipedia_changes",
    "parse_wikipedia_changes",
    "fetch_tickerleague_changes",
    "parse_tickerleague_changes",
]
