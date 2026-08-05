"""CLI for the buyback-timing research pipeline (mirrors other candidate CLIs)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from .config import StudyParams
from .edgar import harvest, to_events
from .event_study import run as run_study

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "buyback-timing"


def _out_dir() -> Path:
    (RESEARCH / "events").mkdir(parents=True, exist_ok=True)
    return RESEARCH / "events"


def cmd_harvest(args: argparse.Namespace) -> int:
    p = StudyParams()
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    print(f"harvesting 8-K repurchase-program filings {start}..{end} (classify={args.classify_docs}, max_docs={args.max_docs})")
    rows = harvest(start, end, classify_docs=args.classify_docs, max_docs=args.max_docs, sleep=args.sleep)
    events = to_events(rows, only_new=True)

    out = _out_dir() / "buyback_events.parquet"
    df = pd.DataFrame([e.__dict__ for e in events])
    df.to_parquet(out)
    print(f"\nclassified summary")
    n_ev = len(events)
    n_new = sum(1 for r in rows if r.get("is_new_program"))
    from collections import Counter
    by_year = Counter((e.announcement_date.year for e in events if e.announcement_date))
    print(f"rows: {len(rows)} | classified-new: {n_new} | events: {n_ev}")
    print("events by year:", dict(sorted(by_year.items())))
    print("saved:", out)
    return 0


def cmd_study(args: argparse.Namespace) -> int:
    p = StudyParams()
    events = pd.read_parquet(str(RESEARCH / "events" / "buyback_programs.parquet"))
    out = run_study(events, p)
    frame = out["frame"]
    (RESEARCH / "outputs").mkdir(parents=True, exist_ok=True)
    frame.to_parquet(RESEARCH / "outputs" / "study_frame.parquet")
    summary = summarize(frame)
    (RESEARCH / "outputs" / "study_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
    return 0


def summarize(frame: pd.DataFrame) -> dict:
    summary = {"n_events": int(frame["ticker"].nunique())}
    for h in (5, 10, 20):
        sub = frame[frame["h"] == h]
        if sub.empty:
            continue
        net = sub["net_bps"].dropna()
        rel_spy = sub["rel_spy_bps"].dropna()
        rel_iwm = sub["rel_iwm_bps"].dropna()
        summary[f"h{h}"] = {
            "n": int(len(sub)),
            "net_mean_bps": round(float(net.mean()), 1),
            "net_tstat": round(float(net.mean() / (net.std() / np.sqrt(len(net)))), 2) if len(net) > 1 else None,
            "net_p5_bps": round(float(np.percentile(_boot(net), 5)), 1),
            "rel_spy_mean_bps": round(float(rel_spy.mean()), 1),
            "rel_spy_p5_bps": round(float(np.percentile(_boot(rel_spy), 5)), 1),
            "rel_iwm_mean_bps": round(float(rel_iwm.mean()), 1),
            "pos_frac": round(float((net > 0).mean()), 3),
        }
    return summary


def _boot(x: pd.Series, n: int = 10_000, seed: int = 42) -> np.ndarray:
    x = x.dropna().to_numpy()
    rng = np.random.default_rng(seed)
    if len(x) == 0:
        return np.array([0.0])
    return np.array([rng.choice(x, size=len(x), replace=True).mean() for _ in range(n)])


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="buyback-timing research CLI")
    sub = p.add_subparsers(dest="mode", required=True)

    h = sub.add_parser("harvest", help="harvest + classify 8-K repurchase-program events")
    h.add_argument("--start", default="2025-07-01")
    h.add_argument("--end", default="2026-07-31")
    h.add_argument("--no-classify", dest="classify_docs", action="store_false", default=True)
    h.add_argument("--max-docs", type=int, default=None)
    h.add_argument("--sleep", type=float, default=0.4)
    h.set_defaults(func=cmd_harvest)

    s = sub.add_parser("study", help="run bounded event study on the program events")
    s.set_defaults(func=cmd_study)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_argparser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
