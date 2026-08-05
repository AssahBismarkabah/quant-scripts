"""EDGAR 8-K repurchase-program harvest and event classification.

Retrieves Form 8-K filings whose text mentions a share repurchase program,
dedups them, and classifies each as a *new buyback-program authorization*
(the Tier A event) vs a follow-on / miscellaneous mention, using explicit
keyword rules so the classification is auditable.

Signal feed for the buyback-timing candidate (IA/buyback-timing-research-spec.md).
"""

from __future__ import annotations

import re
import time
import urllib.parse
from datetime import date, timedelta
from html.parser import HTMLParser

import requests

from .models import BuybackEvent

HEADERS = {"User-Agent": "Research research@example.com"}
SEARCH = "https://efts.sec.gov/LATEST/search-index"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data"

# Keywords that indicate a NEW authorization of a repurchase program, vs a
# mention. Authorization blocks contain a dollar cap and an "authoriz"/"program"
# construction. (Auditable; refine on inspection, not post hoc to pass.)
AUTH_RE = re.compile(
    r"(authoriz(?:e|ed|ing|ation)?|approved?|adopt(?:ed|ing)?)\b"
    r".{0,40}?"
    r"(repurchas(?:e|ed|ing|es)?|buy.?back|share repurchase|stock repurchase)\b",
    flags=re.IGNORECASE | re.DOTALL,
)
CAP_RE = re.compile(r"(?:up to|of|approximately|)\s*[$]\s*[\d,.]+\s*(?:million|billion|m|b|M|B)", flags=re.IGNORECASE)
# negative signals (repurchase mentioned but not a new program): credit/borrowing plans, employee plans, etc.
NEG_RE = re.compile(
    r"(credit agreement|borrowing|loan|indenture|note offering|convertible|employee (?:stock|share) purchase|"
    r"dividend reinvestment|earnings? call|results|financial results)",
    flags=re.IGNORECASE,
)


def _cik_pad(cik: str | int | None) -> str:
    if cik is None:
        return ""
    return str(cik).zfill(10)


def _quarters(start: date, end: date):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        qs = date(y, m, 1)
        qe = (date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)) - timedelta(days=1)
        yield (max(start, qs), min(end, qe))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def search_quarter(qs: date, qe: date, query: str = '"repurchase program"') -> list[dict]:
    """Return 8-K raw hits (metadata) in a calendar quarter via EDGAR full-text search."""
    params = {
        "q": query,
        "dateRange": "custom",
        "startdt": qs.isoformat(),
        "enddt": qe.isoformat(),
        "forms": "8-K",
    }
    url = SEARCH + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(6):
        try:
            r = requests.get(url, headers=HEADERS, timeout=40)
            if r.status_code == 200:
                break
            last = r
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(2.0 * (attempt + 1))
    else:
        raise RuntimeError(f"search_quarter failed after retries: {last}")
    out = []
    for h in r.json().get("hits", {}).get("hits", []):
        s = h.get("_source", {})
        if s.get("form") == "8-K":
            out.append(
                {
                    "adsh": s.get("adsh"),
                    "cik": _cik_pad(s.get("ciks", [None])[0] if s.get("ciks") else None),
                    "date": s.get("file_date"),
                    "name": (s.get("display_names") or [""])[0],
                    "items": s.get("items") or [],
                }
            )
    return out


class _TextParser(HTMLParser):
    """Tiny HTML -> whitespace-joined text extractor (no external deps)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self._chunks.append(data.strip())

    def text(self) -> str:
        return " ".join(self._chunks)


def fetch_8k_text(cik: str, adsh: str) -> str:
    """Fetch and strip the primary 8-K document text (std-lib only)."""
    idx = f"{ARCHIVE}/{int(cik)}/{adsh.replace('-', '')}/index.json"
    files = []
    for attempt in range(3):
        try:
            r = requests.get(idx, headers=HEADERS, timeout=40)
            r.raise_for_status()
            files = [i["name"] for i in r.json()["directory"]["item"] if i["name"].endswith(".htm")]
            break
        except Exception:
            time.sleep(1.0)
    if not files:
        return ""
    basename = adsh.split("-")[0] + ".htm"
    primary = next((f for f in files if f == basename), None) or next(
        (f for f in files if f != "FilingSummary.xml"), None
    )
    if not primary:
        return ""
    url = f"{ARCHIVE}/{int(cik)}/{adsh.replace('-', '')}/{primary}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        if r.status_code != 200:
            return ""
        parser = _TextParser()
        parser.feed(r.text)
        parser.close()
        return parser.text()
    except Exception:
        return ""


def classify(text: str) -> tuple[bool, str]:
    """Return (is_new_program, reason)."""
    if not text:
        return False, "empty"
    if NEG_RE.search(text):
        return False, "negative-context"
    auth = AUTH_RE.search(text)
    cap = CAP_RE.search(text)
    if auth and cap:
        return True, "auth+cap"
    if auth:
        return True, "auth"
    return False, "no-auth"


def harvest(
    start: date,
    end: date,
    *,
    classify_docs: bool = True,
    max_docs: int | None = None,
    sleep: float = 0.4,
) -> list[dict]:
    """Harvest 8-K repurchase-program filings, dedup by (cik,adsh), optionally classify."""
    raw: dict[tuple, dict] = {}
    for qs, qe in _quarters(start, end):
        rows = search_quarter(qs, qe)
        for r in rows:
            raw[(r["cik"], r["adsh"])] = r
        print(f"  {qs}..{qe}: {len(rows)} hits (cumulative unique {len(raw)})")
        time.sleep(sleep)

    rows = list(raw.values())
    if classify_docs:
        for i, r in enumerate(rows):
            txt = fetch_8k_text(r["cik"], r["adsh"])
            is_new, reason = classify(txt)
            r["is_new_program"] = is_new
            r["class_reason"] = reason
            time.sleep(sleep)  # pace doc fetches to respect EDGAR rate limits
            if max_docs and i + 1 >= max_docs:
                break
    return rows


def to_events(rows: list[dict], only_new: bool = True) -> list[BuybackEvent]:
    """Convert harvested + optionally classified rows to BuybackEvent objects.

    When `only_new=True`, a row counts as an event only if it was explicitly
    classified as a new program (has a class_reason); unclassified rows are
    excluded so a truncated/max_docs run does not inflate the event count.
    """
    events = []
    for r in rows:
        if only_new:
            if not r.get("class_reason"):
                continue  # not classified -> do not count
            if not r.get("is_new_program"):
                continue  # classified but not a new program
        d = None
        if r.get("date"):
            d = date.fromisoformat(r["date"])
        events.append(
            BuybackEvent(
                cik=r["cik"],
                adsh=r.get("adsh", ""),
                company=(r.get("name") or "").split("(")[0].strip(),
                announcement_date=d,
                item_801="8.01" in (r.get("items") or []),
            )
        )
    return events
