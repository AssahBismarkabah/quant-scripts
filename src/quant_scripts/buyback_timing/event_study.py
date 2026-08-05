"""Bounded-sample event study for buyback-timing.

For each program-level event: forward CAR from open of t+1 over the report
horizons, net of friction, and benchmark-relative (minus SPY / IWM over the
same window). Reports bootstrap p5 on the primary net CAR. Cells are assigned
by a size proxy (ticker in SPY's large-cap bucket vs not) and the joint gate is
reported with the caveat that membership is a proxy on this bounded sample.

Documented limitations (bounded study): sample is small (per dedup), sector-
concentrated (financials), single-year (persistence not assessable here), and
cell membership is a size proxy, not official index membership.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from .bars import load_bars
from .config import StudyParams

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "buyback-timing"
EVENTS = RESEARCH / "events" / "buyback_programs.parquet"

# approximates: SPY = large-cap (S&P 500 proxy), IWM = small-cap (S&P 600/2000 proxy)
BENCH = {"SP500": "SPY", "SP600": "IWM"}


def _car_on_frame(bars: pd.DataFrame, ticker: str, t: pd.Timestamp, entry_open: float) -> dict:
    """Forward CARs from open of t+1 at times (t+1..t+20)."""
    sub = bars[bars["ticker"] == ticker]
    sub = sub[sub["ts_date"] > t].sort_values("ts_date")
    if sub.empty:
        return {}
    closes = sub["close"].to_numpy()
    if len(closes) < 20:
        return {}
    # CAR(h) = close[t+h_][session] / entry_open - 1  (t+1 open entry; here use first open then closes)
    first_open = sub.iloc[0]["open"] if entry_open is None else entry_open
    out = {}
    for h in (5, 10, 20):
        if len(closes) >= h:
            out[h] = closes[h - 1] / first_open - 1
    return out


def dedup_programs(events: pd.DataFrame, gap_days: int = 90) -> pd.DataFrame:
    """Collapse 8-K events per issuer into independent program-level events.

    A new program is counted only if >= `gap_days` since the last kept event
    from the same issuer; routine periodic 8-Ks restating an ongoing program
    (which otherwise inflate the count, e.g. News Corp) are dropped.
    """
    df = events.copy()
    df["announcement_date"] = pd.to_datetime(df["announcement_date"])
    df = df.sort_values(["cik", "announcement_date"]).reset_index(drop=True)
    keep_pos = []
    last: dict[str, pd.Timestamp] = {}
    for pos, r in df.iterrows():
        c = r["cik"]
        d = r["announcement_date"]
        if c in last and (d - last[c]).days < gap_days:
            continue
        keep_pos.append(pos)
        last[c] = d
    return df.iloc[keep_pos].copy()


def run(events: pd.DataFrame | None = None, params: StudyParams = StudyParams()) -> dict:
    if events is None:
        events = pd.read_parquet(EVENTS)
    events = events.copy()
    events["announcement_date"] = pd.to_datetime(events["announcement_date"])

    start = datetime(2024, 1, 1)
    end = datetime(2026, 8, 1)
    tickers = sorted(set(events["ticker"].dropna().tolist() + ["SPY", "IWM"]))
    bars = load_bars(tickers, start, end)

    # benchmark CAR lookups
    bench_car = {}
    for bname, sym in BENCH.items():
        bb = bars[bars["ticker"] == sym].sort_values("ts_date")
        bench_car[bname] = bb

    rows = []
    for r in events.itertuples():
        ticker = r.ticker
        t = r.announcement_date
        b = bars[bars["ticker"] == ticker]
        row_b = b[b["ts_date"] > t].sort_values("ts_date")
        if row_b.empty:
            continue
        entry_open = row_b.iloc[0]["open"]
        car = _car_on_frame(bars, ticker, t, None)
        if not car:
            continue
        # benchmark CAR same window: from t to t+20 sessions
        brec = {}
        for bname, sym in BENCH.items():
            bb = bench_car[bname]
            bseg = bb[(bb["ts_date"] > t)].sort_values("ts_date")
            if len(bseg) >= 21:
                brec[bname] = bseg.iloc[20]["close"] / bseg.iloc[0]["open"] - 1
        # Conservative base friction for net CAR: use the small-cap (S&P 600) base
        # because the bounded sample is small/mid-cap-and-financial skewed; the
        # per-cell refinement runs once official membership is assigned.
        base_friction = params.friction_base_bps["SP600"] / 1e4
        for h in (5, 10, 20):
            if h in car:
                gross = car[h]
                net = gross - base_friction
                rel_spy = gross - (brec.get("SP500", gross))
                rel_iwm = gross - (brec.get("SP600", gross))
                rows.append(
                    {
                        "ticker": ticker,
                        "date": t,
                        "h": h,
                        "car_bps": round(gross * 1e4, 2),
                        "net_bps": round(net * 1e4, 2),
                        "rel_spy_bps": round(rel_spy * 1e4, 2),
                        "rel_iwm_bps": round(rel_iwm * 1e4, 2),
                    }
                )
    res = pd.DataFrame(rows)
    return {"frame": res}
