from __future__ import annotations

import html
import re
from datetime import date, datetime
from pathlib import Path

from .models import EventAction, ReasonCategory, Venue
from .utils import fetch_bytes

_ARCHIVE_URL = "https://press.spglobal.com/index.php?s=2429&l={page_size}&o={offset}"

# announcement date embedded in release URL slug: press.spglobal.com/YYYY-MM-DD-...
_URL_DATE_RE = re.compile(r"/20(\d{2})-(\d{2})-(\d{2})-")
_EFFECTIVE_DATE_PHRASES = [
    re.compile(r"effective prior to the opening of trading on (Monday|Tuesday|Wednesday|Thursday|Friday), (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})"),
    re.compile(r"effective prior to the open of trading on (Monday|Tuesday|Wednesday|Thursday|Friday), (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})"),
    re.compile(r"will be added to (?:the )?S&P [^\s]+ prior to the open of trading on (Monday|Tuesday|Wednesday|Thursday|Friday), (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})"),
    re.compile(r"effective (?:on|after) (Monday|Tuesday|Wednesday|Thursday|Friday), (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})"),
]
_MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}

# reason phrases in release body text
_MA_PHRASES = [
    r"acquiring", r"acquisition of", r"to be acquired", r"acquisition is expected",
    r"merger", r"merger of", r"tender offer", r"is acquiring", r"completed its acquisition",
]
_BANKRUPTCY_PHRASES = [r"bankruptcy", r"chapter 11", r"liquidation"]
_SPINOFF_PHRASES = [r"spin-off", r"spin off", r"spin-off of", r"separate its", r"distribution of .* shares"]


def sweep_archive(
    out_dir: Path,
    *,
    start_offset: int = 0,
    max_offset: int = 4000,
    page_size: int = 50,
    cache: bool = True,
) -> list[Path]:
    """Download archive listing pages. Stops at the first empty page.

    Note: the keyword parameter of the archive is ignored by the backend;
    pagination must use o=<offset> only.
    """
    pages: list[Path] = []
    offset = start_offset
    while offset <= max_offset:
        url = _ARCHIVE_URL.format(page_size=page_size, offset=offset)
        out_path = out_dir / f"page_{offset}.html"
        if cache:
            path = fetch_bytes(url, out_path)
        else:
            import requests

            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
            resp.raise_for_status()
            path = out_path
            path.write_bytes(resp.content)
        html = path.read_text(encoding="utf-8", errors="replace")
        links = _extract_links(html)
        if not links:
            break
        pages.append(path)
        offset += page_size
    return pages


def _extract_links(html: str) -> list[dict[str, object]]:
    """Extract release links: URL, announcement date (from slug), title."""
    out: list[dict[str, object]] = []
    for match in re.finditer(r'href="(https://press\.spglobal\.com/[^"]+)"[^>]*>([^<]{10,200})<', html):
        url = match.group(1)
        title = re.sub(r"\s+", " ", match.group(2)).strip()
        date_match = _URL_DATE_RE.search(url)
        ann_date = None
        if date_match:
            ann_date = date(2000 + int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)))
        out.append({"url": url, "title": title, "announcement_date": ann_date})
    return out


def parse_release_page(path: Path) -> list[dict[str, object]]:
    return _extract_links(path.read_text(encoding="utf-8", errors="replace"))


def parse_release_body(html_str: str) -> dict[str, object]:
    """Extract the event chain and effective dates from a release page.

    Primary source: the PRNewswire summary table
    (Effective Date | Index Name | Action | Company Name | Ticker | GICS
    Sector). Each row carries its own effective date, so a release with
    multiple effective dates (e.g. two separate rebalance dates) parses
    correctly. Falls back to the prose replacement-chain regex when the
    table is absent.
    """
    text = _strip_tags(html_str)
    text = html.unescape(text)
    effective_date = _find_effective_date(text)
    table_chain = _parse_summary_table(html_str)
    if table_chain:
        chain = table_chain
    else:
        lead = _extract_lead_paragraph(text)
        chain = _parse_chain(lead)
    reason = classify_reason(text)
    for link in chain:
        link["reason"] = reason
    return {"effective_date": effective_date, "chain": chain, "body": text}


def _parse_summary_table(html_str: str) -> list[dict[str, object]] | None:
    """Parse the PRNewswire summary table: rows of
    Effective Date | Index Name | Action | Company Name | Ticker | GICS Sector.
    Returns chain links carrying per-row effective_date, or None if the
    table is absent or has no data rows."""
    m = re.search(r"Effective\s*Date", html_str)
    if not m:
        return None
    table_start = html_str.rfind("<table", 0, m.start())
    table_end = html_str.find("</table>", m.start())
    if table_start == -1 or table_end == -1:
        return None
    table = html_str[table_start:table_end]
    links: list[dict[str, object]] = []
    last_date: date | None = None
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S):
        cells = []
        for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S):
            cell = re.sub(r"<[^>]+>", " ", td)
            cell = html.unescape(cell)
            cell = re.sub(r"\s+", " ", cell).strip()
            cells.append(cell)
        if len(cells) < 5:
            continue
        eff_date = _parse_table_date(cells[0])
        if eff_date is not None:
            last_date = eff_date  # date cell repeats only on the first row
        action_raw = cells[2].lower()
        ticker = cells[4].strip()
        if last_date is None or ticker == "Ticker":
            continue  # header row or no date yet
        action = EventAction.ADDITION if action_raw == "addition" else EventAction.DELETION
        links.append(
            {
                "effective_date": last_date,
                "venue": _venue_from_raw(cells[1]),
                "action": action.value,
                "ticker": ticker,
                "company_name": cells[3],
            }
        )
    return links or None


_MONTHS_ABBR = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def _parse_table_date(text: str) -> date | None:
    # formats seen in releases: 'November 26, 2024', 'Dec 22, 2025',
    # 'Sept. 19, 2022', 'Mar.18, 2024', '23-Sep-24'
    month_names = "|".join(_MONTHS) 
    month_abbrs = "|".join(_MONTHS_ABBR)
    match = re.match(
        rf"\s*(?:({month_names})\s+(\d{{1,2}}),\s*(\d{{4}})"
        rf"|({month_abbrs})\.?\s*(\d{{1,2}}),\s*(\d{{4}})"
        rf"|(\d{{1,2}})-({month_abbrs})-(\d{{2}}|\d{{4}}))",
        text,
    )
    if not match:
        return None
    if match.group(1):
        month, day, year = _MONTHS[match.group(1)], int(match.group(2)), int(match.group(3))
    elif match.group(4):
        month = _MONTHS_ABBR[match.group(4)]
        day, year = int(match.group(5)), int(match.group(6))
    else:
        month = _MONTHS_ABBR[match.group(8)]
        day = int(match.group(7))
        year = int(match.group(9))
        if year < 100:
            year += 2000
    return date(year, month, day)


def _extract_lead_paragraph(text: str) -> str:
    """Return the PRNewswire lead paragraph only (starts after '/ PRNewswire / --'
    and ends before 'Following is' or the effective-date sentence end).

    The rest of the page (nav menus, styles, tables) is excluded so the chain
    parser never matches menu text.
    """
    start = text.find("/ PRNewswire / --")
    if start == -1:
        start = text.find("PRNewswire / --")
    if start == -1:
        return text
    start += len("/ PRNewswire / --") if "/ PRNewswire / --" in text else len("PRNewswire / --")
    end = text.find("Following is", start)
    if end == -1:
        end = len(text)
    return text[start:end]


def _strip_tags(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text


def _find_effective_date(text: str) -> date | None:
    year = datetime.now().year
    for pattern in _EFFECTIVE_DATE_PHRASES:
        for match in pattern.finditer(text):
            weekday, month_name, day = match.group(1), match.group(2), int(match.group(3))
            month = _MONTHS[month_name]
            # try current year and up to 3 years back; pick the one where the weekday matches
            for y in range(year, year - 4, -1):
                try:
                    d = date(y, month, day)
                except ValueError:
                    continue
                if d.strftime("%A").lower() == weekday.lower():
                    return d
    return None


def _parse_chain(text: str) -> list[dict[str, object]]:
    """Parse 'X will replace Y in the S&P 500 ... effective ...' statements.

    Clause variants: the leading 'S&P <Index> constituent' phrase is optional
    (clauses after 'and' omit it), and the replaced company (Y) may or may not
    carry a ticker in parentheses. Ticker groups look like '(NYSE: TPL)'; the
    bare ticker is the last token.
    Returns links: {venue, action, ticker, company_name}.
    """
    chain: list[dict[str, object]] = []
    pattern = re.compile(
        r"(?:,\s*(?:and\s+)?|and\s+)?"
        r"(?:S&P\s+[A-Za-z0-9&]+(?:\s\d{3})?\s+constituent\s+)?"
        r"(?=[A-Za-z])"
        r"((?:(?!S&P|constituent)[^(])+?)\s*\(([^)]+)\)\s+will\s+replace\s+"
        r"(?=[A-Za-z])"
        r"((?:(?!S&P)[^(])+?)(?:\s*\(([^)]+)\))?\s+in\s+the\s+"
        r"(S&P\s+500|S&P\s+MidCap\s+400|S&P\s+SmallCap\s+600)"
    )
    for match in pattern.finditer(text):
        company_in = match.group(1).strip()
        ticker_in = _ticker_from_group(match.group(2))
        company_out = match.group(3).strip()
        ticker_out = _ticker_from_group(match.group(4)) if match.group(4) else ""
        venue = _venue_from_raw(match.group(5))
        chain.append({"ticker": ticker_out, "company_name": company_out, "action": "deletion", "venue": venue})
        chain.append({"ticker": ticker_in, "company_name": company_in, "action": "addition", "venue": venue})
    _resolve_missing_tickers(chain)
    return chain


def _ticker_from_group(group: str) -> str:
    """Extract the bare ticker from a group like 'NYSE: TPL' or 'TPL'."""
    return group.strip().split(":")[-1].strip()


def _resolve_missing_tickers(chain: list[dict[str, object]]) -> None:
    """Chain links sometimes omit the replaced company's ticker (no parens).

    The ticker usually appears elsewhere in the same release for the same
    company (e.g., Mueller Industries appears as an addition with (NYSE: MLI)
    in the previous link). Fill missing tickers by fuzzy company-name match.
    """
    by_company: dict[str, str] = {}
    for link in chain:
        ticker = str(link["ticker"])
        company = _norm_company(link["company_name"])
        if ticker and company:
            by_company.setdefault(company, ticker)
    for link in chain:
        if not link["ticker"]:
            company = _norm_company(link["company_name"])
            if company in by_company:
                link["ticker"] = by_company[company]
            else:
                # prefix match: 'texas pacific land' vs 'texas pacific land corp'
                for known, ticker in by_company.items():
                    if company and (known.startswith(company) or company.startswith(known)):
                        link["ticker"] = ticker
                        break


def _norm_company(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _ticker_from_group(group: str) -> str:
    """Extract the bare ticker from a group like 'NYSE: TPL' or 'TPL'."""
    return group.strip().split(":")[-1].strip()


def _venue_from_raw(raw: str) -> Venue:
    mapping = {
        "S&P 500": Venue.SP500,
        "S&P MidCap 400": Venue.SP400,
        "S&P SmallCap 600": Venue.SP600,
    }
    return mapping.get(raw, Venue.SP500)


def classify_reason(body_text: str) -> ReasonCategory:
    lower = body_text.lower()
    if any(re.search(p, lower) for p in _BANKRUPTCY_PHRASES):
        return ReasonCategory.BANKRUPTCY
    if any(re.search(p, lower) for p in _SPINOFF_PHRASES):
        return ReasonCategory.SPINOFF
    if any(re.search(p, lower) for p in _MA_PHRASES):
        return ReasonCategory.M_A
    return ReasonCategory.DISCRETIONARY


__all__ = [
    "sweep_archive",
    "parse_release_page",
    "parse_release_body",
    "classify_reason",
    "parse_release_page",
]
