from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

from .config import DatabentoCredentials, FrictionSettings, StudySettings
from .models import EventStatus, ReasonCategory, Venue


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _research_dir() -> Path:
    return _repo_root() / "research" / "index-rebalancing"


def _load_dotenv() -> None:
    env_path = _repo_root() / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Index rebalancing price-pressure research helper")
    parser.add_argument(
        "--mode",
        choices=[
            "sweep-spdji",
            "parse-releases",
            "fetch-wikipedia",
            "fetch-tickerleague",
            "reconcile",
            "fetch-ftse",
            "derive-r2000",
            "fetch-bars",
            "run-study",
        ],
        default="run-study",
    )
    parser.add_argument("--min-announcement", type=str, default="2022-06-01")
    parser.add_argument("--venue", type=str, default=None, choices=["sp600", "sp400", "sp500", "r2000"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--stress", action="store_true")
    return parser


def _venues_from_arg(venue: str | None) -> list[Venue]:
    if venue:
        return [Venue(venue)]
    return [Venue.SP400, Venue.SP600]


def mode_sweep_spdji(args: argparse.Namespace) -> int:
    from .spdji import sweep_archive

    out_dir = _research_dir() / "raw" / "spdji" / "pages"
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = sweep_archive(out_dir, max_offset=4000)
    print(json.dumps({"pages": len(pages), "dir": str(out_dir)}, indent=2))
    return 0


def mode_parse_releases(args: argparse.Namespace) -> int:
    from .spdji import parse_release_body, parse_release_page
    from .utils import fetch_bytes, write_manifest

    pages_dir = _research_dir() / "raw" / "spdji" / "pages"
    releases_dir = _research_dir() / "raw" / "spdji" / "releases"
    releases_dir.mkdir(parents=True, exist_ok=True)
    min_ann = date.fromisoformat(args.min_announcement)
    links: dict[str, dict[str, object]] = {}
    for page in sorted(pages_dir.glob("page_*.html")):
        for link in parse_release_page(page):
            ann = link.get("announcement_date")
            title = str(link.get("title", ""))
            if ann is None or ann < min_ann:
                continue
            if not ("Set to Join" in title or "to Join" in title or "Index Changes" in title):
                continue
            links[str(link["url"])] = link
    if args.limit:
        links = dict(list(links.items())[: args.limit])
    releases: list[dict[str, object]] = []
    files: list[Path] = []
    for url, link in links.items():
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        out_path = releases_dir / f"{slug}.html"
        if out_path.exists():
            # press releases are immutable (URL embeds the date): keep cached copy
            files.append(out_path)
        else:
            try:
                files.append(fetch_bytes(str(url), out_path))
            except Exception:
                continue
        parsed = parse_release_body(out_path.read_text(encoding="utf-8", errors="replace"))
        parsed["announcement_date"] = link["announcement_date"]
        parsed["title"] = link["title"]
        parsed["url"] = url
        releases.append(parsed)
    out_json = _research_dir() / "raw" / "spdji" / "parsed_releases.jsonl"
    with out_json.open("w", encoding="utf-8") as fh:
        for rel in releases:
            slim = {k: v for k, v in rel.items() if k != "body"}
            fh.write(json.dumps(slim, default=str) + "\n")
    write_manifest(releases_dir, files)
    print(
        json.dumps(
            {"releases": len(releases), "output": str(out_json), "release_pages": len(files)},
            indent=2,
        )
    )
    return 0


def _load_releases() -> list[dict[str, object]]:
    path = _research_dir() / "raw" / "spdji" / "parsed_releases.jsonl"
    releases: list[dict[str, object]] = []
    if not path.exists():
        return releases
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            releases.append(json.loads(line))
    return releases


def mode_fetch_wikipedia(args: argparse.Namespace) -> int:
    from .crossvalidate import fetch_wikipedia_changes

    out_dir = _research_dir() / "raw" / "wikipedia"
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    for venue in _venues_from_arg(args.venue):
        rows = fetch_wikipedia_changes(venue, out_dir / f"{venue.value}.html")
        total += len(rows)
    print(json.dumps({"rows": total, "dir": str(out_dir)}, indent=2))
    return 0


def mode_fetch_tickerleague(args: argparse.Namespace) -> int:
    from .crossvalidate import fetch_tickerleague_changes

    out_dir = _research_dir() / "raw" / "tickerleague"
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    for venue in _venues_from_arg(args.venue):
        rows = fetch_tickerleague_changes(venue, out_dir / f"{venue.value}.html")
        total += len(rows)
    print(json.dumps({"rows": total, "dir": str(out_dir)}, indent=2))
    return 0


def mode_reconcile(args: argparse.Namespace) -> int:
    from .crossvalidate import parse_tickerleague_changes, parse_wikipedia_changes
    from .reconcile import agreement_report, reconcile, spdji_chain_to_events, write_events_parquet

    settings = StudySettings()
    releases = _load_releases()
    if not releases:
        raise SystemExit("no parsed releases; run parse-releases first")
    events = spdji_chain_to_events(
        releases,
        min_announcement=date.fromisoformat(args.min_announcement),
        max_effective=settings.data_end,
    )
    cross: list[dict[str, object]] = []
    wiki_dir = _research_dir() / "raw" / "wikipedia"
    tpl_dir = _research_dir() / "raw" / "tickerleague"
    for venue in (Venue.SP400, Venue.SP600):
        wiki_path = wiki_dir / f"{venue.value}.html"
        if wiki_path.exists():
            cross.extend(
                parse_wikipedia_changes(wiki_path.read_text(encoding="utf-8", errors="replace"), venue)
            )
        tpl_path = tpl_dir / f"{venue.value}.html"
        if tpl_path.exists():
            cross.extend(
                parse_tickerleague_changes(tpl_path.read_text(encoding="utf-8", errors="replace"), venue)
            )
    log_path = _research_dir() / "events" / "provenance" / "reconcile_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    reconciled = reconcile(events, cross, log_path=log_path)
    out_path = _research_dir() / "events" / "spdji_reconciled.parquet"
    write_events_parquet(reconciled, out_path)
    report = agreement_report(reconciled)
    report["cross_rows"] = len(cross)
    print(json.dumps(report, indent=2))
    return 0


def mode_fetch_ftse(args: argparse.Namespace) -> int:
    from .ftse import download_wayback_raw, find_snapshots, list_url
    from .utils import fetch_bytes, write_manifest

    out_dir = _research_dir() / "raw" / "ftse"
    out_dir.mkdir(parents=True, exist_ok=True)
    # live URL patterns by year/kind (preliminary lists are the primary source)
    live = {2025: {"additions": "additions-2025prelim", "deletions": "deletions-2025prelim"}}
    files: list[Path] = []
    missing: list[str] = []
    for year in (2023, 2024, 2025):
        for kind in ("additions", "deletions"):
            stamp = live.get(year, {}).get(kind)
            if stamp:
                url = list_url(year, kind, stamp)
                out_path = out_dir / f"ru3000-{kind}-{year}.pdf"
                try:
                    files.append(fetch_bytes(url, out_path))
                    continue
                except Exception:
                    pass
            snapshots = find_snapshots(year, kind, final_only=True)
            if not snapshots:
                missing.append(f"{year}-{kind}")
                continue
            out_path = out_dir / f"ru3000-{kind}-{year}.pdf"
            try:
                files.append(download_wayback_raw(snapshots[0], out_path))
            except Exception:
                missing.append(f"{year}-{kind}")
    write_manifest(out_dir, files)
    print(json.dumps({"downloaded": len(files), "missing": missing, "dir": str(out_dir)}, indent=2))
    return 0


def mode_derive_r2000(args: argparse.Namespace) -> int:
    from .ftse import derive_r2000, events_from_russell, parse_russell_pdf, validate_r2000_counts
    from .reconcile import write_events_parquet

    ftse_dir = _research_dir() / "raw" / "ftse"
    all_events: list[object] = []
    validation: list[dict[str, object]] = []
    for year in (2023, 2024, 2025):
        adds_path = ftse_dir / f"ru3000-additions-{year}.pdf"
        dels_path = ftse_dir / f"ru3000-deletions-{year}.pdf"
        if not (adds_path.exists() and dels_path.exists()):
            validation.append({"year": year, "skipped": "missing pdfs"})
            continue
        adds = parse_russell_pdf(adds_path)
        dels = parse_russell_pdf(dels_path)
        adds, dels = derive_r2000(adds, dels)
        validation.append(validate_r2000_counts(adds, dels, year))
        all_events.extend(events_from_russell(adds, dels, year))
    out_path = _research_dir() / "events" / "r2000_events.parquet"
    write_events_parquet(all_events, out_path)
    print(json.dumps({"events": len(all_events), "validation": validation, "output": str(out_path)}, indent=2))
    return 0


def _event_tickers() -> list[str]:
    """All study tickers (sp600/sp400/r2000, discretionary, confirmed/unverified)
    plus benchmark ETFs and calendar symbol."""
    settings = StudySettings()
    out: list[str] = []
    for path in (
        _research_dir() / "events" / "spdji_reconciled.parquet",
        _research_dir() / "events" / "r2000_events.parquet",
    ):
        if not path.exists():
            continue
        import pandas as pd

        df = pd.read_parquet(path)
        df = df[
            (df["venue"].isin(["sp600", "sp400", "r2000"]))
            & (df["reason_category"] == ReasonCategory.DISCRETIONARY.value)
            & (~df["status"].isin([EventStatus.RECONCILED.value, EventStatus.DROPPED.value]))
            & (pd.to_datetime(df["effective_date"]).dt.date >= settings.study_start)
        ]
        out.extend(sorted(df["ticker"].unique()))
    out.extend(sorted(set(settings.benchmark_by_venue.values())))
    out.append("SPY")
    return sorted(set(out))


def mode_fetch_bars(args: argparse.Namespace) -> int:
    from .databento import client_from_env, fetch_daily_bars, session_dates

    settings = StudySettings()
    bars_dir = _research_dir() / "cache" / "bars"
    bars_dir.mkdir(parents=True, exist_ok=True)
    client = client_from_env(_repo_root() / ".env")
    tickers = _event_tickers()
    if args.limit:
        tickers = tickers[: args.limit]
    paths = fetch_daily_bars(
        tickers,
        settings.study_start,
        settings.data_end,
        out_dir=bars_dir,
        client=client,
    )
    calendar = session_dates(
        settings.study_start,
        settings.data_end,
        client=client,
        out_dir=_research_dir() / "cache",
    )
    print(
        json.dumps(
            {"bars_written": len(paths), "calendar_sessions": len(calendar), "dir": str(bars_dir)},
            indent=2,
        )
    )
    return 0


def mode_run_study(args: argparse.Namespace) -> int:
    import pandas as pd

    from .event_study import run_study

    settings = StudySettings()
    friction = FrictionSettings()
    events_dir = _research_dir() / "events"
    frames = []
    for path in (events_dir / "spdji_reconciled.parquet", events_dir / "r2000_events.parquet"):
        if path.exists():
            frames.append(pd.read_parquet(path))
    if not frames:
        raise SystemExit("no event tables; run reconcile / derive-r2000 first")
    events = pd.concat(frames, ignore_index=True)
    events = events[
        (events["venue"].isin(["sp600", "sp400", "r2000"]))
        & (events["reason_category"] == ReasonCategory.DISCRETIONARY.value)
        & (~events["status"].isin([EventStatus.RECONCILED.value, EventStatus.DROPPED.value]))
        & (pd.to_datetime(events["effective_date"]).dt.date >= settings.study_start)
    ]
    study_events_path = events_dir / "study_events.parquet"
    events.to_parquet(study_events_path, index=False)
    cal_path = _research_dir() / "cache" / "calendar.parquet"
    if not cal_path.exists():
        raise SystemExit("no calendar cache; run fetch-bars first")
    calendar = [pd.Timestamp(d).date() for d in pd.read_parquet(cal_path)["ts_date"].tolist()]
    out_dir = _research_dir() / "outputs"
    result = run_study(
        study_events_path,
        _research_dir() / "cache" / "bars",
        calendar,
        out_dir,
        settings,
        friction,
        stress=args.stress,
    )
    agg = pd.read_parquet(result["aggregate"])
    summary = agg.to_dict(orient="records")
    print(json.dumps({"n_events": len(events), "aggregate": summary}, indent=2))
    return 0


_HANDLERS = {
    "sweep-spdji": mode_sweep_spdji,
    "parse-releases": mode_parse_releases,
    "fetch-wikipedia": mode_fetch_wikipedia,
    "fetch-tickerleague": mode_fetch_tickerleague,
    "reconcile": mode_reconcile,
    "fetch-ftse": mode_fetch_ftse,
    "derive-r2000": mode_derive_r2000,
    "fetch-bars": mode_fetch_bars,
    "run-study": mode_run_study,
}


def main() -> int:
    _load_dotenv()
    args = build_parser().parse_args()
    handler = _HANDLERS.get(args.mode)
    if handler is None:
        raise SystemExit(f"unknown mode: {args.mode}")
    return handler(args)


__all__ = ["build_parser", "main"]
