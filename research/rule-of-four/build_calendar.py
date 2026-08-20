"""Build the pre-registered event calendar for Probe #24 (Rule of 4).

Frozen inclusion rule (decided before any alpha run):
  FOMC  = days the Federal Reserve issued an FOMC monetary policy statement
          following a regular or unscheduled meeting.
          EXCLUDED: joint multi-central-bank announcements (2010-05-09 swap
          facilities) and implementation-only statements (2019-10-11), which
          are not FOMC policy statements.
  NFP   = official BLS Employment Situation releases, 8:30 AM ET, from the
          BLS yearly news-release schedules.

Release times (ET):
  FOMC standard: 2:15 PM (2010-2018), 2:00 PM (2019+). Emergency 2020
  meetings have page-embedded times: 03-03 10:00 AM, 03-15 5:00 PM,
  03-23 8:00 AM.
  NFP: 8:30 AM ET (all releases; confirmed on every schedule row).

Sources (committed under sources/):
  - fomc_data.csv / fomc_cur.csv: marcburri/ScrapeFOMC datasets; Statement
    field -> statement date. Statement days after 2022-03-16 verified
    directly against Federal Reserve statement pages (HTTP 200), listed
    in FOMC_VERIFIED_DAYS.
  - sched_YYYY.txt: BLS yearly news-release schedules (www.bls.gov blocks
    direct scraping; fetched via jina.ai text proxy, committed as text).

Writes events/fomc.csv and events/nfp.csv with columns:
  date (YYYY-MM-DD), time_et (HH:MM), tz (America/New_York), type, note.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "sources"
OUT = ROOT / "events"
OUT.mkdir(exist_ok=True)

FOMC_VERIFIED_DAYS = [
    "2022-05-04", "2022-06-15", "2022-07-27", "2022-09-21", "2022-11-02",
    "2022-12-14",
    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26",
    "2023-09-20", "2023-11-01", "2023-12-13",
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31",
    "2024-09-18", "2024-11-07", "2024-12-18",
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30",
    "2025-09-17", "2025-10-29", "2025-12-10",
]

# Pre-registered exclusions (not FOMC policy statements).
EXCLUDED = {
    "2010-05-09": "joint central-bank swap-facility announcement, not a policy statement",
    "2019-10-11": "implementation-only statement (T-bill purchases), not an FOMC policy statement",
}

# Emergency meetings with page-embedded times.
EMERGENCY_TIMES = {
    "2020-03-03": "10:00",
    "2020-03-15": "17:00",
    "2020-03-23": "08:00",
}

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}


def fomc_time(day: str) -> str:
    if day in EMERGENCY_TIMES:
        return EMERGENCY_TIMES[day]
    return "14:15" if day < "2019-01-01" else "14:00"


def parse_fomc() -> list[tuple]:
    days = []
    for fname in ("fomc_data.csv", "fomc_cur.csv"):
        with (SRC / fname).open() as f:
            for row in csv.DictReader(f):
                if not row["Statement"].strip():
                    continue
                m = re.search(r"(\d{4})(\d{2})(\d{2})", row["Statement"])
                if m and "2010-01-01" <= f"{m.group(1)}-{m.group(2)}-{m.group(3)}" <= "2022-03-16":
                    days.append(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
    days += FOMC_VERIFIED_DAYS
    out = []
    for d in sorted(set(days)):
        if d in EXCLUDED:
            continue
        out.append((d, fomc_time(d), "America/New_York", "FOMC", EXCLUDED.get(d, "fomc")))
    assert len(out) == len(set(x[0] for x in out)), "duplicate FOMC days"
    return out


def parse_nfp() -> list[tuple]:
    out = []
    for y in range(2010, 2026):
        fname = SRC / f"sched_{y}.txt" if y != 2025 else SRC / "sched_2025b.txt"
        text = fname.read_text()
        pat = re.compile(
            r"\|\s*([A-Z][a-z]+day), ([A-Z][a-z]+) (\d{1,2}), (\d{4}) \|\s*"
            r"(\d{1,2}:\d{2} [AP]M) \|\s*\*\*Employment Situation\*\*")
        for m in pat.finditer(text):
            wd, mo, d, yr, t = m.groups()
            assert yr == str(y), (yr, y)
            date = f"{yr}-{MONTHS[mo]:02d}-{int(d):02d}"
            hh, mm, _ = re.split(r"[: ]", t)
            out.append((date, f"{hh}:{mm}", "America/New_York", "NFP", "bls_schedule"))
    out.sort()
    assert len(out) == len(set(x[0] for x in out)), "duplicate NFP days"
    return out


def main() -> None:
    fomc = parse_fomc()
    nfp = parse_nfp()
    with (OUT / "fomc.csv").open("w") as f:
        f.write("date,time_et,tz,type,note\n")
        for day, t, tz, typ, note in fomc:
            f.write(f"{day},{t},{tz},{typ},{note}\n")
    with (OUT / "nfp.csv").open("w") as f:
        f.write("date,time_et,tz,type,note\n")
        for day, t, tz, typ, note in nfp:
            f.write(f"{day},{t},{tz},{typ},{note}\n")
    print(f"FOMC events: {len(fomc)}  (2010-2025)")
    print(f"NFP events:  {len(nfp)}  (2010-2025)")


if __name__ == "__main__":
    main()