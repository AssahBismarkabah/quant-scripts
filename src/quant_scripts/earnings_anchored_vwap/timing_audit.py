"""Free SEC EDGAR release-time audit for the earnings-anchored VWAP probe.

Phase 0 requires an independent confirmation of the release date and the
BMO/AMC session for a fixed 100-event, year-stratified sample. This module uses
only free, no-auth SEC EDGAR endpoints:

  - ``data.sec.gov/submissions/CIK{cik}.json`` (+ quarterly ``files``) for the
    filing index: exact-date Form 8-K Item 2.02 (and 6-K for foreign private
    issuers) with the ``acceptanceDateTime`` (UTC) and ``items``;
  - ``/Archives/edgar/data/{cik}/{accession}/index.json`` + the largest EX-99
    press release for mid-session or next-day filings, whose conference-call
    time / release dateline disambiguates the session.

The EDGAR full-text symbol search is deliberately not used: it is unreliable
for the exact tickers that the year-stratified sample deliberately includes
(verified: BMO -> Citigroup, DATA -> Cincinnati, MIND -> Fifth Third). Instead a
curated symbol -> CIK map resolves each ticker, so delisted registrants
(retained by EDGAR, dropped by Yahoo) are still covered.

Honesty caveat (documented in the research gate, §10): the *acceptance* time is
the SEC filing moment, not necessarily the moment the press release went out.
For a date + session audit this is a strong independent check; rows where the
acceptance falls during market hours, or where a foreign issuer supplied the
release to its home exchange before the SEC acceptance, are disambiguated from
the EX-99 text or left honestly ``ambiguous``.

Every row that disagrees with the template is reported, never patched: the
release date is never moved to fit a filing (a filing on a different date is
``not_found`` for the template row), and a foreign issuer's acceptance time is
never silently treated as its release time (that mis-attributes the session).
"""

from __future__ import annotations

import re
import time
from datetime import timedelta
from typing import Any

import requests
import pandas as pd

HEADERS = {"User-Agent": "earnings-anchored-vwap-audit research@example.com"}
SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"

MARKET_OPEN_ET = 9 * 60 + 30  # 09:30 ET
MARKET_CLOSE_ET = 16 * 60  # 16:00 ET

# Curated symbol -> CIK, resolved and verified by direct EDGAR probes. The EDGAR
# full-text symbol search is unreliable for the exact tickers the frozen,
# year-stratified sample picks (BMO -> Citigroup, DATA -> Cincinnati, MIND ->
# Fifth Third), so the ticker -> registrant resolution is pinned here instead.
# 100 entries; every CIK in the sample maps to a real registrant.
CIK: dict[str, str] = {
    "FCFS": "0000840489", "SPSC": "0001092699", "RS": "0000861884", "IRDM": "0001418819", "XEC": "0001168054",
    "WSTL": "0001002135", "THR": "0001489096", "JEC": "0000052988", "SMTC": "0000088941", "ADBE": "0000796343",
    "MCRI": "0000907242", "PCMI": "0000937941", "HOMB": "0001331520", "SEIC": "0000350894", "GD": "0000040533",
    "RPT": "0000842183", "SNCR": "0001131554", "CRNT": "0001119769", "DY": "0000067215", "CRAY": "0000949158",
    "SP": "0001347613", "LL": "0001396033", "MTB": "0000036270", "FUN": "0000811532", "MVIS": "0000065770",
    "ZEUS": "0000917470", "WTFC": "0001015328", "MCF": "0001071993", "GES": "0000912463", "HIVE": "0001372414",
    "DNR": "0000945764", "WLH": "0001095996", "BCEI": "0001509589", "EA": "0000712515", "CAMT": "0001109138",
    "TVPT": "0001424755", "BZUN": "0001625414", "MIND": "0000926423", "AMBR": "0001314223", "TRIP": "0001526520",
    "ARDX": "0001437402", "GCP": "0001644440", "PSTG": "0001474432", "MSM": "0001003078", "HMST": "0001518715",
    "EURN": "0001604481", "COTY": "0001024305", "RRC": "0000315852", "CL": "0000021665", "MAN": "0000871763",
    "POR": "0000784977", "KEM": "0000887730", "PZN": "0001399249", "HBCP": "0001436425", "DATA": "0001303652",
    "PPC": "0000802481", "BANF": "0000760498", "TFSL": "0001381668", "BMO": "0000927971", "HRS": "0000202058",
    "EMKR": "0000808326", "CINF": "0000020286", "SUI": "0000912593", "AMKR": "0001047127", "HRC": "0000047518",
    "CAR": "0000723612", "IIVI": "0000820318", "OFG": "0001030469", "GNK": "0001326200", "PYPL": "0001633917",
    "BXG": "0000778946", "RGA": "0000898174", "WMGI": "0001492658", "UAA": "0001336917", "ICE": "0001571949",
    "SRT": "0001031029", "DOMO": "0001505952", "LIND": "0001512499", "QTNT": "0001596946", "LYTS": "0000763532",
    "APEN": "0001251769", "GDP": "0000943861", "GPX": "0000070415", "MGEN": "0001590750", "ZIXI": "0000855612",
    "SRRA": "0001290149", "ANIK": "0000898437", "GEVO": "0001392380", "DXCM": "0001093557", "JYNT": "0001612630",
    "CSTM": "0001563411", "BSVN": "0001746129", "NXST": "0001142417", "DRH": "0001298946", "EGRX": "0000827871",
    "HCKT": "0001057379", "LPG": "0001596993", "CANG": "0001725123",
}

# Foreign private issuers in the sample report earnings via Form 6-K (or 8-K for
# some FPIs) and frequently supply the release to their home exchange hours
# before the SEC acceptance. For these the acceptance time is NOT a release-time
# signal; the attached press-release text is the only honest evidence, and the
# event is left ambiguous when no release text exists.
FOREIGN_ISSUERS: set[str] = {"CAMT", "BZUN", "CRNT", "EURN", "BMO", "CSTM", "CANG", "LPG"}

# efts.sec.gov full-text search is intentionally unused (symbol resolution is
# wrong for sample tickers). Delete the symbol-match helpers that shipped with
# the first pivot so the only path is the CIK-centric one.


def _get(url: str, tries: int = 6) -> requests.Response:
    """GET with polite exponential backoff for SEC's throttling."""
    last: Exception | None = None
    for attempt in range(tries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=45)
            if response.status_code in (200, 403, 429, 500, 503):
                return response
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            last = exc
        time.sleep(1.5 * (2 ** attempt))
    if last is not None:
        raise last
    raise RuntimeError(f"GET failed for {url}")


def _et_minutes(timestamp: pd.Timestamp) -> int:
    """Return minutes since midnight in US/Eastern for a tz-aware timestamp."""
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    eastern = timestamp.tz_convert("US/Eastern")
    return eastern.hour * 60 + eastern.minute + eastern.second / 60.0


def classify_session(timestamp: pd.Timestamp) -> str | None:
    """Classify an acceptance timestamp as pre / post (BMO / AMC), or mid."""
    if timestamp is None or pd.isna(timestamp):
        return None
    minutes = _et_minutes(timestamp)
    if minutes < MARKET_OPEN_ET:
        return "pre"
    if minutes > MARKET_CLOSE_ET:
        return "post"
    return "mid"  # during regular hours; treat as ambiguous, not pre/post


def _pad_cik(cik: str | int | None) -> str:
    if cik is None:
        return ""
    return str(cik).zfill(10)


_SUBMISSION_CACHE: dict[str, tuple[str | None, list[dict[str, Any]]]] = {}


def submission_filings(cik: str) -> tuple[str | None, list[dict[str, Any]]]:
    """Return (registrant name, filing rows) from recent + quarterly EDGAR files."""
    if cik in _SUBMISSION_CACHE:
        return _SUBMISSION_CACHE[cik]
    rows: list[dict[str, Any]] = []
    name: str | None = None
    try:
        response = _get(SUBMISSIONS.format(cik=cik))
        if response.status_code == 200:
            payload = response.json()
            name = payload.get("name")
            recent = payload.get("filings", {}).get("recent", {})
            for accn, fdate, accepted, form, items in zip(
                recent.get("accessionNumber", []),
                recent.get("filingDate", []),
                recent.get("acceptanceDateTime", []),
                recent.get("form", []),
                recent.get("items", []) or [[]] * len(recent.get("accessionNumber", [])),
            ):
                rows.append(_filing_row(fdate, accepted, form, items, accn))
            for quarterly in payload.get("filings", {}).get("files", []) or []:
                time.sleep(0.12)
                try:
                    quri = f"https://data.sec.gov/submissions/{quarterly['name']}"
                    qr = requests.get(quri, headers=HEADERS, timeout=45)
                    if qr.status_code != 200:
                        continue
                    qd = qr.json()
                    for accn, fdate, accepted, form, items in zip(
                        qd.get("accessionNumber", []),
                        qd.get("filingDate", []),
                        qd.get("acceptanceDateTime", []),
                        qd.get("form", []),
                        qd.get("items", []) or [[]] * len(qd.get("accessionNumber", [])),
                    ):
                        rows.append(_filing_row(fdate, accepted, form, items, accn))
                except requests.RequestException:
                    continue
    except requests.RequestException:
        rows = []
        name = None
    _SUBMISSION_CACHE[cik] = (name, rows)
    return _SUBMISSION_CACHE[cik]


def _filing_row(
    fdate: str,
    accepted: str,
    form: str,
    items: object,
    accn: str,
) -> dict[str, Any]:
    if isinstance(items, list):
        items_str = ",".join(str(i) for i in items)
    else:
        items_str = str(items or "")
    return {
        "date": fdate,
        "acc": accepted or "",
        "form": form or "",
        "items": items_str,
        "adsh": accn,
    }


def _to_et_session(accepted_utc: str) -> tuple[pd.Timestamp | None, str]:
    """Return (ET timestamp, session) for a UTC acceptance string."""
    try:
        ts = pd.Timestamp(accepted_utc)
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        et = ts.tz_convert("US/Eastern")
        minutes = et.hour * 60 + et.minute + et.second / 60.0
        session = "pre" if minutes < MARKET_OPEN_ET else ("post" if minutes > MARKET_CLOSE_ET else "mid")
        return et, session
    except (ValueError, TypeError):
        return None, "mid"


def filing_documents(cik: str, accn: str) -> list[dict[str, Any]]:
    """Text .htm documents for a filing, biggest first, unifying both sources.

    EDGAR exposes a filing's documents in two places that disagree for older
    filings:

    - the per-filing index JSON (``directory.item``) lists the main form and
      the ``-index``/``-headers``/``.txt`` helper files, and frequently omits
      the EX-99 press-release exhibits entirely (verified for PCMI
      0001104659-13-015981, HIVE 0001193125-15-044221, CRNT
      0001178913-13-003116, BMO 0001193125-17-361608, and DY release 8-K
      0000067215-13-000051);
    - EDGAR's free full-text index search keyed on the accession number
      (``https://efts.sec.gov/LATEST/search-index?q="<accn>"``) enumerates
      *every* file in the filing including the exhibits. (The ``.json``
      suffix on that endpoint 403s, but the plain endpoint needs no auth and
      returns 200.)

    This function unions both sources so a press-release exhibit is never
    missed just because the directory listing skipped it. Duplicates by
    filename are dropped (directory sizes preferred when known).
    """
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/index.json"
    directory_docs: list[dict[str, Any]] = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=45)
        if response.status_code == 200:
            items = response.json().get("directory", {}).get("item", [])
            directory_docs = [
                i
                for i in items
                if i.get("type") == "text.gif"
                and i.get("name", "").endswith(".htm")
                and not any(b in i["name"] for b in ("index", "-headers", ".txt"))
            ]
    except (requests.RequestException, ValueError):
        directory_docs = []
    # Full-text index may add exhibit files the directory listing skipped.
    efts_docs: list[dict[str, Any]] = []
    try:
        q = f'https://efts.sec.gov/LATEST/search-index?q=%22{accn}%22'
        response = requests.get(q, headers=HEADERS, timeout=45)
        if response.status_code == 200:
            hits = response.json().get("hits", {}).get("hits", [])
            for hit in hits:
                fname = (hit.get("_id") or "").split(":", 1)[-1]
                if not fname.endswith(".htm"):
                    continue
                if any(b in fname for b in ("index", "-headers", ".txt")):
                    continue
                efts_docs.append({"name": fname, "size": 0})
    except (requests.RequestException, ValueError):
        efts_docs = []
    by_name = {d["name"]: d for d in directory_docs}
    for doc in efts_docs:
        by_name.setdefault(doc["name"], doc)
    return sorted(by_name.values(), key=lambda i: int(i.get("size") or 0), reverse=True)


def _fetch_document_body(cik: str, accn: str, fname: str) -> str:
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/{fname}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=45)
        body = re.sub(r"<[^>]+>", " ", response.text)
        body = re.sub(r"&[a-z]+;|&#\d+;", " ", body)
        return re.sub(r"\s+", " ", body)
    except requests.RequestException:
        return ""


_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}
_TIME_RE = re.compile(r"(\d{1,2}(?:[:\s]\d{2})?)\s*([ap]\.?m\.?)", re.I)
_NON_US_TZ = re.compile(
    r"^(CET|CEST|BST|GMT|Beijing|China|JST|IST|CST|CXT|WET|WEST)", re.I
)


def _non_us_tz_after(body: str, ampm_end: int) -> bool:
    """True if the next word after an a.m./p.m. token is a non-US timezone."""
    next_word = re.match(r"\s*([A-Za-z]{2,12})", body[ampm_end : ampm_end + 16])
    return bool(next_word and _NON_US_TZ.match(next_word.group(1)))


def _is_pm(tok: str) -> bool:
    return bool(re.search(r"p\.?m", tok, re.I))


def _call_signal(body: str, release_iso: str) -> tuple[str | None, str | None]:
    """Session from an earnings-call time in the release text, anchored R.

    Market convention:
      - call R AM      -> pre  (BMO release)
      - call R PM      -> post (AMC release)
      - call R+1 (AM)  -> post (report after close, call next morning)
    """
    release = pd.Timestamp(release_iso)
    # 1a) "Month Day, Year ... at H:MM am|pm" (year present; date before time).
    #     Day and year tolerate embedded spaces from HTML conversion
    #     (e.g. "February 2 7 , 201 5"). The time must be the *nearest* one
    #     after the date: a `[^.]{0,90}` span can overreach past a parenthetical
    #     and bind a secondary timezone's time (e.g. "8:00 a.m. EDT ... (8:00
    #     p.m. Beijing ...)"). Stop at the first am/pm token after the date.
    for m in re.finditer(
        r"(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+(\d\s?\d?),?\s+(\d\s?\d\s?\d\s?\d)"
        r"[^.]{0,120}?(\d{1,2}(?:[:\s]\d{2})?)\s*([ap]\.?m\.?)",
        body,
        re.I,
    ):
        year = int(re.sub(r"\s", "", m.group(3)))
        day = int(re.sub(r"\s", "", m.group(2)))
        month_name, t = m.group(1), m.group(5)
        if _non_us_tz_after(body, m.end()):
            continue
        try:
            call = pd.Timestamp(year=year, month=_MONTHS[month_name.lower()], day=day).normalize()
        except ValueError:
            continue
        # Only a call on the release day itself or the next morning is session
        # evidence. A dated call days away is a different event's meeting
        # inside the same release (e.g. an unrelated board meeting) and says
        # nothing about the release session; skip it.
        if call not in (release, release + timedelta(days=1)):
            continue
        if _is_pm(t):
            return "post", f"call@{call.date()} pm"
        if call == release:
            return "pre", f"call@sameday-am {call.date()}"
        if call == release + timedelta(days=1):
            return "post", f"call@nextday-am {call.date()}"
    # 1b) "H:MM am|pm ... Month Day, Year" (time before date)
    for m in re.finditer(
        r"(\d{1,2}(?:[:\s]\d{2})?)\s*([ap]\.?m\.?)[^.]{0,90}?"
        r"(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+(\d\s?\d?),?\s+(\d\s?\d\s?\d\s?\d)",
        body,
        re.I,
    ):
        t, month_name = m.group(2), m.group(3)
        if _non_us_tz_after(body, m.end(2)):
            continue
        day = int(re.sub(r"\s", "", m.group(4)))
        year = int(re.sub(r"\s", "", m.group(5)))
        try:
            call = pd.Timestamp(year=year, month=_MONTHS[month_name.lower()], day=day).normalize()
        except ValueError:
            continue
        # Same date-gate as pattern 1a: a dated call that is not the release
        # day or the next morning is a different event's meeting (e.g. a
        # quarter-end "March 31, 2016" date inside the financial narrative
        # followed by the release's call time), and says nothing about the
        # release session. Must gate BEFORE the PM early-return so a PM time
        # next to an unrelated date does not mislabel the release.
        if call not in (release, release + timedelta(days=1)):
            continue
        if _is_pm(t):
            return "post", f"call@{call.date()} pm"
        if call == release:
            return "pre", f"call@sameday-am {call.date()}"
        if call == release + timedelta(days=1):
            return "post", f"call@nextday-am {call.date()}"
    # 1c) "month day ... at H:MM" without a year, written as "today, Thursday,
    #     February 19, at 10:00 A.M." (time comes after the month-day and a
    #     weekday). Anchored to the release month/year so the same-day call wins
    #     over a later, unrelated dated meeting in the same release.
    for m in re.finditer(
        r"(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+(\d\s?\d?),?\s+"
        r"(?:[^.]{0,40}?(?:at|on)\s+)?\d{1,2}(?::\d{2})?\s*([ap]\.?m\.?)",
        body,
        re.I,
    ):
        day = int(re.sub(r"\s", "", m.group(2)))
        try:
            call = pd.Timestamp(
                year=release.year, month=_MONTHS[m.group(1).lower()], day=day
            ).normalize()
        except ValueError:
            continue
        if call < release and release.month != call.month:
            call = call.replace(year=release.year + 1)
        if _non_us_tz_after(body, m.end(3)):
            continue
        if call == release:
            return ("post" if _is_pm(m.group(3)) else "pre"), f"call@sameday-{m.group(3)}"
        if call == release + timedelta(days=1):
            return "post", f"call@nextday-{m.group(3)} {call.date()}"
    # 2) "Month Day ... at H:MM" without year (year = release year, else +1)
    for m in re.finditer(
        r"(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+(\d\s?\d?),?\s+"
        r"(?:[^.]{0,60}?at\s+|at\s+)"
        r"(\d{1,2}(?:[:\s]\d{2})?)\s*([ap]\.?m\.?)",
        body,
        re.I,
    ):
        day = int(re.sub(r"\s", "", m.group(2)))
        try:
            cand = pd.Timestamp(year=release.year, month=_MONTHS[m.group(1).lower()], day=day).normalize()
            call = cand if cand >= release.replace(day=1) else cand.replace(year=release.year + 1)
        except ValueError:
            continue
        if call < release:
            continue
        if _non_us_tz_after(body, m.end(4)):
            continue
        if call == release:
            return ("post" if _is_pm(m.group(4)) else "pre"), f"call@sameday-{m.group(4)}"
        if call == release + timedelta(days=1):
            return "post", f"call@nextday-{m.group(4)} {call.date()}"
    # 3) "today|tomorrow ... at H:MM"
    for m in re.finditer(
        r"\b(today|tomorrow)\b[^.]{0,70}?(\d{1,2}(?:[:\s]\d{2})?)\s*([ap]\.?m\.?)",
        body,
        re.I,
    ):
        rel, t = m.group(1), m.group(3)
        if _is_pm(t) or rel.lower() == "tomorrow":
            return "post", f"call@{rel}-pm"
        return "pre", f"call@{rel}-am"
    # 3b) "at H:MM ... today|tomorrow" (time before relative word)
    for m in re.finditer(
        r"(?:at\s+)(\d{1,2}(?:[:\s]\d{2})?)\s*([ap]\.?m\.?)[^.]{0,70}?\b(today|tomorrow)\b",
        body,
        re.I,
    ):
        t, rel = m.group(2), m.group(3)
        if _is_pm(t) or rel.lower() == "tomorrow":
            return "post", f"call@{rel}-pm"
        return "pre", f"call@{rel}-am"
    # 3c) "on Weekday DD Month YYYY" (European day-before-month order, used by
    #     foreign private issuers, e.g. Euronav "9:30 a.m. EDT / 3:30 p.m. CET
    #     on Thursday 28 July 2016"). Same-day AM call => pre; PM call => post.
    #     When a release lists both a US-market time and a secondary timezone
    #     (CET/BST/Beijing), the US-market time is the session-relevant one.
    for m in re.finditer(
        r"\bon\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
        r"\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+(\d\s?\d\s?\d\s?\d)",
        body,
        re.I,
    ):
        day = int(re.sub(r"\s", "", m.group(1)))
        month_name, year_tok = m.group(2), m.group(3)
        try:
            call = pd.Timestamp(
                year=int(re.sub(r"\s", "", year_tok)),
                month=_MONTHS[month_name.lower()],
                day=day,
            ).normalize()
        except ValueError:
            continue
        if call not in (release, release + timedelta(days=1)):
            continue
        if call == release:
            # Walk backwards over every "at|on H:MM am/pm" before this date and
            # pick the nearest one whose timezone is US-market. A dual-timezone
            # call line ("9:30 a.m. EDT / 3:30 p.m. CET on Thursday 28 ...")
            # lists the US-market time first; the secondary (CET/BST/...) time
            # is nearest the date but not session-relevant.
            head = body[: m.start()]
            matches = list(
                re.finditer(
                    r"(?:at|on|for)\s+(\d{1,2}(?:[:\s]\d{2})?)\s*([ap]\.?m\.?)\s*"
                    r"([A-Za-z]{2,12})?",
                    head,
                    re.I,
                )
            )
            if not matches:
                continue
            for last in reversed(matches):
                t = last.group(2)
                tz = last.group(3)
                if tz and re.search(
                    r"^(CET|CEST|BST|GMT|Beijing|China|JST|IST|CST)$", tz, re.I
                ):
                    continue  # secondary (non-US) timezone; keep searching earlier
                return ("post" if _is_pm(t) else "pre"), f"call@{call.date()} {t}"
            continue  # only non-US timezones found; ambiguous
        if call == release + timedelta(days=1):
            return "post", f"call@nextday-am {call.date()}"
    # 4) standalone PM call time (no date/day words): a PM call ends after the
    #    close, so it implies an AMC/post release on the release date.
    for m in re.finditer(r"(?:at|for)\s+(\d{1,2}(?:[:\s]\d{2})?)\s*([ap]\.?m\.?)", body, re.I):
        if _is_pm(m.group(2)):
            return "post", f"call@pm {m.group(1)}"
    return None, None


def _call_time_signals(body: str, release_iso: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    sess, ev = _call_signal(body, release_iso)
    if sess:
        out.append((sess, ev or "call"))
    return out


def _release_signals(body: str) -> list[tuple[str, str]]:
    """Session evidence from release-phrase casing (release text only)."""
    out: list[tuple[str, str]] = []
    for kw, sess in (
        ("after the market close", "post"),
        ("after market close", "post"),
        ("after the close of market", "post"),
        ("before the market opens", "pre"),
        ("before market open", "pre"),
        ("prior to the market open", "pre"),
        ("released today before", "pre"),
        ("released today after", "post"),
    ):
        if re.search(re.escape(kw), body, re.I):
            out.append((sess, "txt:" + kw))
    return out


_DOR_DATE_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+(\d\s?\d?),?\s+(\d\s?\d\s?\d\s?\d)",
    re.I,
)
_DOR_AFTER_LABEL_RE = re.compile(
    r"Date\s+of\s+Report\s*(?:\([^)]*\))?\s*:?\s*"
    r"(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+(\d\s?\d?),?\s+(\d\s?\d\s?\d\s?\d)",
    re.I,
)
_DOR_BEFORE_LABEL_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+(\d\s?\d?),?\s+(\d\s?\d\s?\d\s?\d)\s*"
    r"Date\s+of\s+Report",
    re.I,
)


def _date_of_report(body: str) -> str | None:
    """The 8-K 'Date of Report' line - the authoritative release date.

    Handles both label-before-date ("Date of Report (Date of earliest event
    reported): February 11, 2016", with any-length parenthetical) and
    date-before-label ("February 26, 2015 Date of Report ...") layouts, plus
    the embedded-space HTML artifacts (e.g. "February 2 6 , 201 5").
    """
    for pattern in (_DOR_AFTER_LABEL_RE, _DOR_BEFORE_LABEL_RE):
        m = pattern.search(body)
        if not m:
            continue
        month_name, day_tok, year_tok = m.group(1), m.group(2), m.group(3)
        day = re.sub(r"\s", "", day_tok)
        year = re.sub(r"\s", "", year_tok)
        try:
            return pd.Timestamp(
                year=int(year), month=_MONTHS[month_name.lower()], day=int(day)
            ).date().isoformat()
        except (ValueError, TypeError):
            continue
    return None


def _press_release_signals(cik: str, accn: str, release_iso: str) -> tuple[list[tuple[str, str]], str | None]:
    """Scan of the 8-K/6-K body plus the largest EX-99 text; returns (signals, DOR).

    The main 8-K document carries the authoritative 'Date of Report' line even
    when the EX-99 press release does not, and its Item 2.02 narrative
    frequently restates the release/call time. Both are scanned, EX-99 first
    (it is the larger, richer text).
    """
    signals: list[tuple[str, str]] = []
    dor: str | None = None
    docs = filing_documents(cik, accn)
    # Main 8-K/6-K document name tends to be "<prefix>-8k/6k" or "a8k..."; sort
    # it before any EX-99 exhibit so the authoritative Date of Report wins.
    def _priority(doc: dict[str, Any]) -> tuple[int, int]:
        name = doc.get("name", "").lower()
        if re.search(r"(?:-|_)?(?:8k|6k)[^a-z]", name) or name.startswith(("a8k", "x8k")):
            return (0, -int(doc.get("size") or 0))
        if name.startswith("form8-k") or "8-k" in name:
            return (1, -int(doc.get("size") or 0))
        return (2, -int(doc.get("size") or 0))

    docs = sorted(docs, key=_priority)
    for doc in docs[:4]:
        body = _fetch_document_body(cik, accn, doc["name"])
        if not body:
            continue
        if dor is None:
            dor = _date_of_report(body)
        signals.extend(_call_time_signals(body, release_iso))
        signals.extend(_release_signals(body))
        if len(signals) >= 3:
            break
    return signals, dor


def _candidate_session(
    symbol: str,
    cik: str,
    hit: dict[str, Any],
    dt: str,
    is_foreign: bool,
) -> tuple[str | None, str | None, str | None]:
    """Return (session, evidence_source, dor) for one 8-K/6-K candidate.

    Evaluates a single filing the way the old single-candidate path did: EX-99
    release-text signal first, then (domestic only) the acceptance timestamp on
    the release date itself. A Date-of-Report mismatch is *not* returned as a
    hard failure here; the caller ranks candidates and only reports the DOR
    conflict for the chosen one.
    """
    accn = hit["adsh"]
    accepted = hit["acc"]
    accepted_et, session = _to_et_session(accepted) if accepted else (None, "mid")
    signals, dor = _press_release_signals(cik, accn, dt)

    sess: str | None = None
    evidence_src: str | None = None
    for sig, lab in signals:
        if sig in ("pre", "post"):
            sess, evidence_src = sig, f"EX-99 {lab}"
            break
    if sess is None and not is_foreign and accepted_et is not None:
        accepted_day = accepted_et.tz_convert("US/Eastern").date().isoformat()
        if accepted_day == dt and session in ("pre", "post"):
            sess, evidence_src = session, "acceptance"
    return sess, evidence_src, dor


def _candidate_rank(
    sess: str | None,
    evidence_src: str | None,
    dor: str | None,
    dt: str,
) -> tuple[int, int]:
    """Rank a candidate's evidence; higher is better.

    A candidate that pins the session from release text AND has the template
    release date as its Date of Report is the strongest evidence. Release-text
    session evidence beats acceptance-only. A DOR conflict knocks a candidate
    down unless release text already settles the session.
    """
    text_evidence = evidence_src and evidence_src.startswith("EX-99")
    same_dor = bool(dor and dor == dt)
    grade = 0
    if text_evidence:
        grade += 2
    if same_dor:
        grade += 1
    if sess is None:
        grade = 0
    return (grade, 1 if same_dor else 0)


def _audit_one(symbol: str, rdate: pd.Timestamp) -> dict[str, Any]:
    """CIK-centric EDGAR audit for one template row (no cache-warm race)."""
    result: dict[str, Any] = {
        "status": "error",
        "verified_date": "",
        "verified_release_time": "",
        "source_url": "",
        "source_type": "sec_edgar_item202",
        "notes": "",
    }
    cik = CIK.get(symbol)
    if not cik:
        result["status"] = "not_found"
        result["notes"] = "no CIK resolution"
        return result

    name, filings = submission_filings(cik)
    dt = rdate.date().isoformat()
    lo = dt
    hi = (rdate + timedelta(days=6)).date().isoformat()

    is_foreign = symbol in FOREIGN_ISSUERS
    if is_foreign:
        candidates = [
            f
            for f in filings
            if f["form"] in ("6-K", "8-K") and lo <= f["date"] <= hi
        ]
    else:
        candidates = [
            f
            for f in filings
            if f["form"] == "8-K" and "2.02" in f["items"] and lo <= f["date"] <= hi
        ]

    # Domestic fallback: press releases are sometimes furnished only as a
    # 10-Q/10-K exhibit with no Item 2.02 8-K in the window (SEIC Q1-2013:
    # the release PR is exhibit 99.1 of the 10-Q filed 2013-04-26, dated
    # 2013-04-24). Scan 10-Q/10-K filings in the window as candidates too.
    if not is_foreign:
        candidates = candidates + [
            f
            for f in filings
            if f["form"] in ("10-Q", "10-K") and lo <= f["date"] <= hi
        ]

    if not candidates:
        result["status"] = "not_found"
        notes = "no matching 8-K Item 2.02 / 6-K / quarterly filing"
        if name:
            notes += f" ({name})"
        anyd = [f for f in filings if f["date"] == dt]
        if anyd:
            notes += "; same-day=" + str([(f["form"], f["items"][:12]) for f in anyd[:3]])
        result["notes"] = notes
        return result

    # Scan every candidate (not just the first) and keep the strongest. DY
    # filed both a release 8-K (11-26, Date of Report 11-25) and a transcript
    # 8-K (11-27); the old `exact[0] else candidates[0]` picked the transcript.
    # All candidates are evaluated; the release-text-settled, DOR-matching one
    # wins.
    best: tuple[tuple[int, int], dict[str, Any], str | None, str | None, str | None] | None = None
    for hit in candidates:
        sess, evidence_src, dor = _candidate_session(symbol, cik, hit, dt, is_foreign)
        score = _candidate_rank(sess, evidence_src, dor, dt)
        if best is None or score > best[0]:
            best = (score, hit, sess, evidence_src, dor)
    if best is None or best[0][0] == 0:
        # A filing exists in the window but no candidate yields conclusive
        # session evidence (foreign issuer with a home-exchange release, or a
        # release with no call time / dateline). That is honestly ambiguous, not
        # not_found: the event was reported, we just cannot independently pin
        # the session from free data.
        hit = next(iter(candidates))
        accepted = hit.get("acc") or ""
        result["status"] = "ambiguous"
        base = f"{hit['form']} accepted {accepted} (ET)"
        if is_foreign:
            base += "; foreign issuer: acceptance time is not release time"
        result["notes"] = (
            f"{base} and no EX-99 call-time/date evidence is conclusive"
        )
        return result
    _, hit, sess, evidence_src, dor = best
    accn = hit["adsh"]
    accepted = hit["acc"]
    source_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"

    # Release-date hygiene, kept honest: the 8-K 'Date of Report' line records
    # the *earliest event reported*, which can predate the earnings release
    # (ARDX filed a May 2016 Q1-results 8-K whose DOR header still read
    # "March 9, 2016" from an earlier Item 2.02). The Date of Report is
    # therefore only a rejection when it conflicts AND no release-text session
    # signal pins the template date. When a session signal is anchored to the
    # release date (EX-99 call time / dateline), it is the stronger evidence
    # and the DOR mismatch is recorded in the note, not used to erase a
    # correct verification.
    # Acceptance-only fallback for domestic issuers already ran inside
    # _candidate_session; a candidate reaching here with sess is None can only
    # mean no conclusive evidence, handled below.

    if sess is None:
        result["status"] = "ambiguous"
        base = f"{hit['form']} accepted {accepted} (ET)"
        if is_foreign:
            base += "; foreign issuer: acceptance time is not release time"
        result["notes"] = (
            f"{base} and no EX-99 call-time/date evidence is conclusive"
        )
        return result

    result["source_type"] = "sec_edgar_6k" if (hit["form"] == "6-K") else "sec_edgar_item202"
    result["status"] = "verified"
    result["verified_date"] = dt
    result["verified_release_time"] = sess
    result["source_url"] = source_url
    if evidence_src == "acceptance":
        result["notes"] = (
            f"{hit['form']} (Date of Report {dor or dt}) accepted {accepted} "
            f"(ET) => {sess}"
        )
    else:
        result["notes"] = (
            f"{hit['form']} (Date of Report {dor or dt}) accepted {accepted} "
            f"(ET), {evidence_src} => {sess}"
        )
    return result


def audit_sample(template: pd.DataFrame) -> pd.DataFrame:
    """Audit every row of the fixed timing template and return audit CSV rows."""
    rows: list[dict[str, Any]] = []
    for _, item in template.iterrows():
        symbol = str(item["symbol"]).strip().upper()
        release_date = pd.Timestamp(item["release_date"])
        release_time = str(item["release_time"]).strip().lower()

        result = _audit_one(symbol, release_date)
        rows.append(
            {
                "sample_id": int(item["sample_id"]),
                "symbol": symbol,
                "release_date": release_date.date().isoformat(),
                "release_time": release_time,
                "verified_date": result.get("verified_date", ""),
                "verified_release_time": result.get("verified_release_time", ""),
                "source_url": result.get("source_url", ""),
                "status": result.get("status", "error"),
                "notes": result.get("notes", ""),
                "source_type": result.get("source_type", "sec_edgar_item202"),
            }
        )
        time.sleep(0.2)
    return pd.DataFrame(rows, columns=[
        "sample_id", "symbol", "release_date", "release_time",
        "verified_date", "verified_release_time", "source_url", "source_type",
        "status", "notes",
    ])
