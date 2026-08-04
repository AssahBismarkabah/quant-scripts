"""Level-2 robustness and capacity analysis for the surviving candidate.

Covers the spec's robustness/capacity requirements using cached daily bars
(no new data):
- liquidity threshold sweep (spec: "test a reasonable range of ... liquidity
  thresholds") - reruns the study filters at several ADDV20 levels;
- year-by-year breakdown of the surviving cells (spec: "not dependent on one
  year" - with the caveat that 2023 is excluded by the data window);
- capacity at multiple notional sizes (spec: capacity validation), using the
  pre-registered depth_fraction (5% of ADDV20 executable per event);
- borrow break-even: the annual borrow fee that would zero out the short-side
  edge, and the edge at the pre-registered 300 bps hard-to-borrow cap.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from .config import StudySettings
from .databento import load_bars
from .event_study import apply_market_filters, compute_window_returns
from .models import EventAction, Venue

THRESHOLDS = (2_000_000, 5_000_000, 10_000_000, 20_000_000)
PARTICIPATIONS = (0.01, 0.05, 0.10)


def addv20_by_event(events: pd.DataFrame, bars_dir: Path) -> dict[str, float]:
    """ADDV20 per event_id, computed over the 20 sessions ending at the
    effective-date close (same definition as the study filter, no look-ahead)."""
    addv: dict[str, float] = {}
    for _, ev in events.iterrows():
        bars = load_bars(ev["ticker"], bars_dir)
        if bars.empty:
            continue
        hist = bars[bars.index < ev["effective_date"]]
        vol_window = hist.tail(20)
        if len(vol_window) < 20:
            continue
        addv[ev["event_id"]] = float((vol_window["close"] * vol_window["volume"]).mean())
    return addv


def threshold_sweep(
    events: pd.DataFrame,
    bars_dir: Path,
    calendar: list[date],
    *,
    base_settings: StudySettings,
    window_td: int = 10,
    action: EventAction = EventAction.ADDITION,
) -> pd.DataFrame:
    """Mean abnormal bps of the short-addition cell at several ADDV20 gates."""
    rows: list[dict[str, object]] = []
    for threshold in THRESHOLDS:
        settings = replace(base_settings, min_addv20_usd=threshold, windows_td=(window_td,))
        filtered = apply_market_filters(events, bars_dir, calendar, settings)
        filtered = filtered[filtered["action"] == action.value]
        if filtered.empty:
            rows.append({"threshold_usd": threshold, "n_events": 0})
            continue
        from .friction import FrictionSettings

        results = compute_window_returns(
            filtered, bars_dir, calendar, settings, FrictionSettings(), stress=False
        )
        abnormal = np.array([r.abnormal_bps for r in results])
        net = np.array([r.net_bps for r in results])
        n = len(abnormal)
        t = float(abnormal.mean() / (abnormal.std(ddof=1) / np.sqrt(n))) if n > 1 else 0.0
        rows.append(
            {
                "threshold_usd": threshold,
                "n_events": n,
                "mean_abnormal_bps": round(float(abnormal.mean()), 2),
                "mean_net_bps": round(float(net.mean()), 2),
                "t_stat": round(t, 2),
            }
        )
    return pd.DataFrame(rows)


def year_breakdown(
    results: pd.DataFrame,
    *,
    venues: tuple[Venue, ...] = (Venue.SP600, Venue.SP400),
    window_td: int = 10,
) -> pd.DataFrame:
    """Mean abnormal bps per entry year for the short-addition 10td cell."""
    rows: list[dict[str, object]] = []
    frame = results[
        (results["window_td"] == window_td)
        & (results["action"] == EventAction.ADDITION.value)
        & (results["venue"].isin([v.value for v in venues]))
    ]
    frame = frame.assign(year=frame["entry_date"].astype(str).str[:4])
    for (venue, year), group in frame.groupby(["venue", "year"]):
        abnormal = group["abnormal_bps"].to_numpy(dtype=float)
        n = len(abnormal)
        t = float(abnormal.mean() / (abnormal.std(ddof=1) / np.sqrt(n))) if n > 1 else 0.0
        rows.append(
            {
                "venue": venue,
                "year": year,
                "n_events": n,
                "mean_abnormal_bps": round(float(abnormal.mean()), 2),
                "t_stat": round(t, 2),
            }
        )
    return pd.DataFrame(rows)


def capacity_report(
    results: pd.DataFrame,
    addv: dict[str, float],
    *,
    venues: tuple[Venue, ...] = (Venue.SP600, Venue.SP400),
    window_td: int = 10,
) -> pd.DataFrame:
    """Capacity per tradeable batch at several participation levels.

    Uses the pre-registered depth_fraction (5% of ADDV20 executable per
    event) as the primary estimate, plus 1% and 10% for sensitivity. The
    batch is the set of events that actually traded at the same entry date
    (all additions of one reconstitution share the entry session).
    """
    frame = results[
        (results["window_td"] == window_td)
        & (results["action"] == EventAction.ADDITION.value)
        & (results["venue"].isin([v.value for v in venues]))
    ].copy()
    frame["addv20_usd"] = frame["event_id"].map(addv)
    frame = frame.dropna(subset=["addv20_usd"])
    frame["entry"] = pd.to_datetime(frame["entry_date"]).dt.date
    rows: list[dict[str, object]] = []
    for entry, group in frame.groupby("entry"):
        row: dict[str, object] = {"entry_date": str(entry), "n_events": len(group)}
        for frac in PARTICIPATIONS:
            notional = float((group["addv20_usd"].astype(float) * frac).sum())
            row[f"notional_{int(frac * 100)}pct_usd"] = notional
        rows.append(row)
    return pd.DataFrame(rows)


def borrow_breakeven(results: pd.DataFrame, *, window_td: int = 10) -> pd.DataFrame:
    """Annual borrow fee (bps) that zeroes the short-side edge, per cell.

    Current model charges 200 bps annual flat; at a 10td hold that is
    ~5.5 bps. The hard-to-borrow cap is 300 bps annual. Break-even = the fee
    at which mean net bps == 0, assuming the fee scales linearly with the
    holding period (hold_days = window_td trading days).
    """
    rows: list[dict[str, object]] = []
    frame = results[
        (results["window_td"] == window_td) & (results["action"] == EventAction.ADDITION.value)
    ]
    for (venue, action), group in frame.groupby(["venue", "action"]):
        net = group["net_bps"].to_numpy(dtype=float)
        hold_days = 10  # 10 trading days ~ 14 calendar days
        current_borrow_bps = 200.0 * hold_days / 365
        edge_after_current = float(net.mean())
        breakeven_annual = (edge_after_current + current_borrow_bps) * 365 / hold_days
        rows.append(
            {
                "venue": venue,
                "window_td": window_td,
                "n_events": len(group),
                "mean_net_bps": round(edge_after_current, 2),
                "current_borrow_bps": round(current_borrow_bps, 2),
                "edge_at_cap_bps": round(
                    edge_after_current + current_borrow_bps - 300.0 * hold_days / 365, 2
                ),
                "breakeven_annual_fee_bps": round(max(breakeven_annual, 0.0), 0),
            }
        )
    return pd.DataFrame(rows)


__all__ = [
    "addv20_by_event",
    "borrow_breakeven",
    "capacity_report",
    "threshold_sweep",
    "year_breakdown",
]
