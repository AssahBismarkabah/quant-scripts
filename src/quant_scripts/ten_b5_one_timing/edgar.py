"""EDGAR 8-K harvest + classification for the 10b5-1 adoption-timing probe.

Detects the real-time **issuer** Rule 10b5-1 repurchase-plan adoption event
(the forward, non-lagged signal tested in IA/10b5-1-adoption-timing-research-spec.md).

This is deliberately distinct from buyback-timing/edgar.py, which classifies
broad repurchase *program authorizations*. Here the event is specifically a
company adopting a Rule 10b5-1 plan to repurchase its own shares, disclosed
via Form 8-K — a near-real-time, scheduleable signal (30-day issuer cooling-off).

The classifier must reject:
  - director / officer / 10b5-1 *sales* plans (not the issuer, and not a buyback),
  - general program authorizations that are NOT 10b5-1 plans,
  - citations of 10b5-1 in a legal-section recital without an adoption act.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path

import requests

HEADERS = {"User-Agent": "Research research@example.com"}
SEARCH = "https://efts.sec.gov/LATEST/search-index"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data"

# The plan/rule anchor: an explicit Rule 10b5-1 reference.
RULE_RE = re.compile(r"10b5-?1", flags=re.IGNORECASE)

# Adoption actions (issuer enters into / adopts / establishes a plan/program).
ADOPT_RE = re.compile(
    r"(adopt(?:ed|ing)?|enter(?:ed)?\s+into|establish(?:ed|ing)?|implement(?:ed|ing)?)"
    r".{0,80}?(?:" + RULE_RE.pattern + r")",
    flags=re.IGNORECASE | re.DOTALL,
)
# ...but the action must be attached to a repurchase-of-own-shares context.
BUYBACK_RE = re.compile(
    r"(repurchas(?:e|ed|ing|es)?|purchase\s+(?:of\s+)?(?:its|our|the\s+company's\s+)?"
    r"(?:common\s+)?shares?|repurchase\s+program|share\s+repurchase)",
    flags=re.IGNORECASE,
)

# Negative context: individual (director/officer) plans, sales/issuance, financing.
NEG_RE = re.compile(
    r"(director|officer|executive\s+officer|insider|for\s+sale|sales\s+plan|"
    r"sell(?:ing|s)?\s+(?:of|shares)|issu(e|ance|ing)|equity\s+compensation|"
    r"employee\s+(?:stock|share)|restricted\s+stock|grant\s+of|conversion|"
    r"underwriting|offering(?!/repurchase))",
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


def search_quarter(qs: date, qe: date, query: str = '"10b5-1" repurchase') -> list[dict]:
    """Return 8-K raw hits (metadata) in a quarter via EDGAR full-text search."""
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
    """Tiny HTML -> whitespace-joined text extractor (std-lib only)."""

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
    """Fetch the 8-K component containing the 10b5-1 repurchase narrative.

    The full-text search matched "10b5-1 repurchase", so we return the text of
    the first (smallest, then fallback largest) non-XBRL .htm document that
    actually contains "10b5-1". This is robust to the varying 8-K file naming
    (ticker-dated narrative vs CIK-dated cover vs EX-10/EX-99 exhibits).
    """
    idx = f"{ARCHIVE}/{int(cik)}/{adsh.replace('-', '')}/index.json"
    files = []
    for attempt in range(3):
        try:
            r = requests.get(idx, headers=HEADERS, timeout=40)
            r.raise_for_status()
            items = r.json()["directory"]["item"]
            files = sorted(
                (
                    (i["name"], int(i.get("size") or 0))
                    for i in items
                    if i["name"].endswith(".htm")
                    and not re.match(r"^R\d+\.htm$", i["name"], re.IGNORECASE)  # skip XBRL R-frames
                ),
                key=lambda x: x[1],
            )
            break
        except Exception:
            time.sleep(1.0)
    if not files:
        return ""

    def _fetch_text(fname: str) -> str:
        url = f"{ARCHIVE}/{int(cik)}/{adsh.replace('-', '')}/{fname}"
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

    # return the smallest doc containing "10b5-1" (the matched fragment);
    # if none, fall back to the largest (likely narrative).
    for fname, _size in files:
        txt = _fetch_text(fname)
        if RULE_RE.search(txt):
            return txt
    if files:
        return _fetch_text(files[-1][0])
    return ""


def classify(text: str) -> tuple[bool, str]:
    """Return (is_issuer_10b5-1_repurchase_adoption, reason)."""
    if not text:
        return False, "empty"
    if not RULE_RE.search(text):
        return False, "no-rule-reference"
    # The adoption action must be tied to a repurchase-of-own-shares context.
    if not ADOPT_RE.search(text):
        return False, "rule-cited-no-adoption"
    if not BUYBACK_RE.search(text):
        return False, "rule+adopt-no-buyback-context"
    # Reject individual / sales / financing contexts (must be issuer repurchase).
    neg = NEG_RE.search(text)
    if neg:
        return False, f"negative-context:{neg.group(0).strip()[:40]}"
    return True, "issuer-10b5-1-repurchase-adoption"


def harvest(
    start: date,
    end: date,
    *,
    classify_docs: bool = True,
    max_docs: int | None = None,
    sleep: float = 0.4,
    cache_path: str | None = None,
) -> list[dict]:
    """Harvest 8-K 10b5-1 filings, dedup by (cik,adsh), optionally classify.

    When `cache_path` is given, classifications are persisted to a JSON map
    keyed by adsh and reused across runs, so network-paced classification is
    resumable (survives timeout/interrupts).
    """
    cache: dict[str, dict] = {}
    if cache_path:
        try:
            cache = json.loads(Path(cache_path).read_text())
        except Exception:
            cache = {}
        done = set(cache)

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
            if r["adsh"] in done:
                r["is_adoption"] = cache[r["adsh"]]["is_adoption"]
                r["class_reason"] = cache[r["adsh"]]["class_reason"]
            else:
                txt = fetch_8k_text(r["cik"], r["adsh"])
                is_adopt, reason = classify(txt)
                r["is_adoption"] = is_adopt
                r["class_reason"] = reason
                cache[r["adsh"]] = {"is_adoption": is_adopt, "class_reason": reason}
                if cache_path:
                    Path(cache_path).write_text(json.dumps(cache))
            time.sleep(sleep)
            if (i + 1) % 25 == 0:
                print(f"  [classified {i + 1}/{len(rows)} docs ...]", flush=True)
            if max_docs and i + 1 >= max_docs:
                print(f"  [max_docs reached at {i + 1}]", flush=True)
                break
    return rows


def to_events(rows: list[dict], only_adoptions: bool = True) -> list[dict]:
    """Convert harvested + classified rows to event dicts (CIK, date, etc.)."""
    events = []
    for r in rows:
        if only_adoptions:
            if not r.get("class_reason"):
                continue
            if not r.get("is_adoption"):
                continue
        d = None
        if r.get("date"):
            d = date.fromisoformat(r["date"])
        events.append(
            {
                "cik": r["cik"],
                "adsh": r.get("adsh", ""),
                "company": (r.get("name") or "").split("(")[0].strip(),
                "event_date": d.isoformat() if d else "",
                "item_801": "8.01" in (r.get("items") or []),
                "class_reason": r.get("class_reason", ""),
            }
        )
    return events
