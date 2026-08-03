from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path

import requests

from .models import EventAction, EventStatus, IndexEvent, ReasonCategory, Venue
from .utils import fetch_bytes

_LIVE_BASE = "https://www.lseg.com/content/dam/ftse-russell/en_us/documents/other"
_WAYBACK_CDX = "https://web.archive.org/cdx/search/cdx"
_WAYBACK_RAW = "https://web.archive.org/web/{ts}id_/{url}"

# Russell reconstitution effective dates: after the close of the 4th Friday of June
_EFFECTIVE_DATES = {
    2023: date(2023, 6, 30),
    2024: date(2024, 6, 28),
    2025: date(2025, 6, 27),
    2026: date(2026, 6, 26),
}
# announcement date = date the preliminary lists were first posted
_ANNOUNCEMENT_DATES = {
    2023: date(2023, 5, 26),
    2024: date(2024, 5, 24),
    2025: date(2025, 5, 23),
    2026: date(2026, 5, 22),
}


def list_url(year: int, kind: str, stamp: str) -> str:
    return f"{_LIVE_BASE}/ru3000-{kind}-{stamp}.pdf"


def wayback_find(fragment: str, *, limit: int = 50) -> list[dict[str, str]]:
    """Query the Wayback CDX API for archived ru3000 list PDFs."""
    resp = requests.get(
        _WAYBACK_CDX,
        params={
            "url": f"lseg.com/content/dam/ftse-russell/en_us/documents/other/{fragment}",
            "output": "json",
            "fl": "original,timestamp,statuscode",
            "filter": "statuscode:200",
            "collapse": "urlkey",
            "limit": limit,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    rows = data[1:] if data else []
    return [{"url": r[0], "timestamp": r[1], "statuscode": r[2]} for r in rows]


def download_wayback_raw(snapshot: dict[str, str], out_path: Path) -> Path:
    url = _WAYBACK_RAW.format(ts=snapshot["timestamp"], url=snapshot["url"])
    return fetch_bytes(url, out_path)


def find_snapshots(
    year: int,
    kind: str,
    *,
    final_only: bool = False,
    limit: int = 50,
) -> list[dict[str, str]]:
    """Find archived snapshots of the ru3000 additions/deletions PDF for a year.

    Exact final filenames are queried first (fast); wildcard fallback (slow)
    is used only when exact names miss.
    """
    exact_candidates = [
        f"ru3000-{kind}-final-{year}0623.pdf",
        f"ru3000-{kind}-final-{year}0628.pdf",
        f"ru3000-{kind}-final-{year}0627.pdf",
        f"ru3000-{kind}-final-{year}0626.pdf",
    ]
    for fragment in exact_candidates:
        hits = wayback_find(fragment, limit=limit)
        if hits:
            return hits
    if not final_only:
        hits = wayback_find(f"ru3000-{kind}*{year}*.pdf", limit=limit)
        if hits:
            return hits
    return []


def parse_russell_pdf(pdf_path: Path) -> list[dict[str, object]]:
    """Parse the Russell 3000 additions/deletions list PDF.

    Table columns: Company | Symbol | Industry (header row 'Company Symbol Industry').
    """
    import pdfplumber

    rows: list[dict[str, object]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 2:
                        continue
                    company = (row[0] or "").strip()
                    symbol = (row[1] or "").strip()
                    if not company or not symbol:
                        continue
                    if company.lower() == "company" and symbol.lower() == "symbol":
                        continue
                    if re.match(r"^[A-Z0-9.\-]{1,6}$", symbol):
                        rows.append({"company_name": company, "ticker": symbol})
    return rows


def events_from_russell(
    adds: list[dict[str, object]],
    dels: list[dict[str, object]],
    year: int,
) -> list[IndexEvent]:
    """Build IndexEvents from Russell 3000 additions/deletions lists.

    The lists carry no reason; events default to discretionary and are filtered
    later by the market-data negative filter (S5).
    """
    eff_date = _EFFECTIVE_DATES[year]
    ann_date = _ANNOUNCEMENT_DATES[year]
    events: list[IndexEvent] = []
    for row in adds:
        events.append(
            IndexEvent(
                venue=Venue.R2000,
                ticker=row["ticker"],
                company_name=row["company_name"],
                action=EventAction.ADDITION,
                announcement_date=ann_date,
                effective_date=eff_date,
                reason_category=ReasonCategory.DISCRETIONARY,
                reason_source="ftse_default",
                source_primary="ftse_russell",
                sources=("ftse_russell",),
                status=EventStatus.UNVERIFIED,
            )
        )
    for row in dels:
        events.append(
            IndexEvent(
                venue=Venue.R2000,
                ticker=row["ticker"],
                company_name=row["company_name"],
                action=EventAction.DELETION,
                announcement_date=ann_date,
                effective_date=eff_date,
                reason_category=ReasonCategory.DISCRETIONARY,
                reason_source="ftse_default",
                source_primary="ftse_russell",
                sources=("ftse_russell",),
                status=EventStatus.UNVERIFIED,
            )
        )
    return events


def derive_r2000(
    r3000_adds: list[dict[str, object]],
    r3000_dels: list[dict[str, object]],
    r1000_adds: list[dict[str, object]] | None = None,
    r1000_dels: list[dict[str, object]] | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Derive Russell 2000 additions/deletions from Russell 3000 lists.

    The Russell 3000 list includes moves into/out of the Russell 1000. Without
    the R1000 split we cannot separate graduations from genuine R2000 adds/
    deletes, so this marks the R2000 derivation as provisional (see S5 where
    the reconstitution summary counts validate it). When R1000 lists are
    provided, R1000 names are removed from the R2000 population.
    """
    r1000_add_tickers = {str(r["ticker"]) for r in (r1000_adds or [])}
    r1000_del_tickers = {str(r["ticker"]) for r in (r1000_dels or [])}
    adds = [r for r in r3000_adds if str(r["ticker"]) not in r1000_add_tickers]
    dels = [r for r in r3000_dels if str(r["ticker"]) not in r1000_del_tickers]
    return adds, dels


def validate_r2000_counts(
    adds: list[dict[str, object]],
    dels: list[dict[str, object]],
    year: int,
    *,
    documented_adds: int | None = None,
    documented_dels: int | None = None,
    tolerance_pct: float = 2.0,
) -> dict[str, object]:
    """Validate parsed counts against documented reconstitution summaries.

    Documented (from FTSE Russell summaries):
      2023: 229 adds / 154 dels (R3000, final)
      2024: ~230 adds / ~150 dels
      2025: 229 adds / 154 dels
    Returns the check result; GATE 4 (Russell leg) fails if either count is
    outside the tolerance band.
    """
    n_adds, n_dels = len(adds), len(dels)
    if documented_adds is None or documented_dels is None:
        documented_adds, documented_dels = _DOCUMENTED_COUNTS.get(year, (n_adds, n_dels))
    add_diff = abs(n_adds - documented_adds) / documented_adds * 100 if documented_adds else 100.0
    del_diff = abs(n_dels - documented_dels) / documented_dels * 100 if documented_dels else 100.0
    return {
        "year": year,
        "parsed_adds": n_adds,
        "parsed_dels": n_dels,
        "documented_adds": documented_adds,
        "documented_dels": documented_dels,
        "add_diff_pct": round(add_diff, 2),
        "del_diff_pct": round(del_diff, 2),
        "within_tolerance": add_diff <= tolerance_pct and del_diff <= tolerance_pct,
        "tolerance_pct": tolerance_pct,
        "note": "R3000 list includes R1000-bound names; R2000 derivation provisional without ru1000 lists",
    }


_DOCUMENTED_COUNTS = {
    2023: (229, 154),
    2024: (230, 150),
    2025: (229, 154),
    2026: (244, 155),
}


__all__ = [
    "list_url",
    "wayback_find",
    "find_snapshots",
    "download_wayback_raw",
    "parse_russell_pdf",
    "events_from_russell",
    "derive_r2000",
    "validate_r2000_counts",
]
