from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from .config import FrictionSettings, StudySettings
from .databento import first_session_after, load_bars
from .friction import is_hard_to_borrow, total_cost_bps
from .models import EventAction, EventWindowResult, ExitReason, Venue


def apply_market_filters(
    events: pd.DataFrame,
    bars_dir: Path,
    calendar: list[date],
    settings: StudySettings,
) -> pd.DataFrame:
    """Apply the pre-registered market filters.

    - min price history: >= min_price_history_td sessions with bars before the
      effective date (window ends at effective-date close; no look-ahead)
    - min liquidity: ADDV20 >= threshold, computed over the 20 sessions ending
      at the effective-date close
    Returns the filtered frame plus exclusion-count columns.
    """
    kept: list[bool] = []
    excl_history = 0
    excl_liquidity = 0
    excl_no_bars = 0
    for _, ev in events.iterrows():
        bars = load_bars(ev["ticker"], bars_dir)
        if bars.empty:
            kept.append(False)
            excl_no_bars += 1
            continue
        hist = bars[bars.index < ev["effective_date"]]
        if len(hist) < settings.min_price_history_td:
            kept.append(False)
            excl_history += 1
            continue
        vol_window = hist.tail(20)
        if len(vol_window) < 20:
            kept.append(False)
            excl_liquidity += 1
            continue
        addv = (vol_window["close"] * vol_window["volume"]).mean()
        if addv < settings.min_addv20_usd:
            kept.append(False)
            excl_liquidity += 1
            continue
        kept.append(True)
    out = events.assign(_kept=kept).loc[kept].drop(columns=["_kept"]).reset_index(drop=True)
    out.attrs["exclusions"] = {
        "no_bars": excl_no_bars,
        "insufficient_history": excl_history,
        "below_addv_threshold": excl_liquidity,
    }
    return out


def benchmark_daily_returns(venue: Venue, bars_dir: Path) -> pd.Series:
    """Daily close-to-close returns of the venue benchmark ETF (IJR/IJH/IWM)."""
    settings = StudySettings()
    ticker = settings.benchmark_by_venue[venue]
    bars = load_bars(ticker, bars_dir)
    if bars.empty or "close" not in bars.columns:
        return pd.Series(dtype=float)
    return bars["close"].pct_change().dropna()


def compute_window_returns(
    events: pd.DataFrame,
    bars_dir: Path,
    calendar: list[date],
    settings: StudySettings,
    friction: FrictionSettings,
    *,
    stress: bool = False,
) -> list[EventWindowResult]:
    """Run the event study for all events x windows.

    Entry: open of the first session strictly after the effective date.
    Exit: close of the window's final session; force-close at the last
    available close (exit_reason=delisting) or when data ends (data_end).
    Benchmark: size-matched venue ETF buy-and-hold over the same span.
    """
    results: list[EventWindowResult] = []
    for _, ev in events.iterrows():
        ticker = ev["ticker"]
        venue = Venue(ev["venue"])
        action = EventAction(ev["action"])
        bars = load_bars(ticker, bars_dir)
        if bars.empty:
            continue
        entry_date = first_session_after(pd.Timestamp(ev["effective_date"]).date(), calendar)
        if entry_date is None:
            continue
        assert entry_date > pd.Timestamp(ev["effective_date"]).date()  # no entry on effective date
        entry_bars = bars[bars.index == entry_date]
        if entry_bars.empty:
            continue
        entry_price = float(entry_bars["open"].iloc[0])
        bench = benchmark_daily_returns(venue, bars_dir)
        for window_td in settings.windows_td:
            exit_sessions = [s for s in calendar if s >= entry_date]
            if len(exit_sessions) < window_td:
                continue
            exit_date = exit_sessions[window_td - 1]
            exit_bars = bars[bars.index <= exit_date]
            if exit_bars.empty:
                continue
            exit_reason = ExitReason.WINDOW_END
            completed = True
            if exit_date >= settings.data_end:
                completed = False
            last_close = float(exit_bars["close"].iloc[-1])
            exit_price = last_close
            if exit_date not in exit_bars.index:
                # bars stopped before the window end: force close at last bar
                exit_reason = ExitReason.DELISTING
            hold_days = len(exit_sessions[:window_td])
            gross_bps = (exit_price / entry_price - 1) * 10_000
            if action is EventAction.ADDITION:
                gross_bps = -gross_bps  # short additions: profit when price falls
            cost = total_cost_bps(
                action, entry_price, exit_price, hold_days,
                stress=stress, settings=friction,
            )
            net_bps = gross_bps - cost
            # benchmark abnormal return over the same span
            span = [s for s in calendar if entry_date <= s <= exit_date]
            bench_cum = 0.0
            if bench is not None and not bench.empty and len(span) > 1:
                # bench index holds datetime.date objects; isin must compare
                # like-for-like (DatetimeIndex() would never match dates)
                bench_slice = bench.loc[bench.index.isin(span)]
                bench_cum = float((1 + bench_slice).prod() - 1) * 10_000
            abnormal_bps = net_bps - bench_cum
            results.append(
                EventWindowResult(
                    event_id=str(ev["event_id"]),
                    venue=venue,
                    ticker=ticker,
                    action=action,
                    entry_date=entry_date,
                    exit_date=exit_date,
                    window_td=window_td,
                    gross_bps=round(gross_bps, 2),
                    net_bps=round(net_bps, 2),
                    benchmark_bps=round(bench_cum, 2),
                    abnormal_bps=round(abnormal_bps, 2),
                    cost_bps=round(cost, 2),
                    exit_reason=exit_reason,
                    completed=completed,
                )
            )
    return results


def aggregate(results: list[EventWindowResult], *, completed_only: bool = True) -> pd.DataFrame:
    """Aggregate per venue x action x window: n, mean/median abnormal bps,
    t-stat, win rate, cost, mean net."""
    rows = []
    completed = [r for r in results if r.completed or not completed_only]
    for venue in sorted({r.venue for r in completed}):
        for action in sorted({r.action for r in completed}):
            for window_td in sorted({r.window_td for r in completed}):
                group = [r for r in completed if r.venue == venue and r.action == action and r.window_td == window_td]
                if not group:
                    continue
                abnormal = np.array([r.abnormal_bps for r in group])
                net = np.array([r.net_bps for r in group])
                n = len(group)
                mean = float(abnormal.mean())
                std = float(abnormal.std(ddof=1)) if n > 1 else 0.0
                t_stat = float(mean / (std / np.sqrt(n))) if std > 0 else 0.0
                rows.append(
                    {
                        "venue": venue.value,
                        "action": action.value,
                        "window_td": window_td,
                        "n_events": n,
                        "mean_abnormal_bps": round(mean, 2),
                        "median_abnormal_bps": round(float(np.median(abnormal)), 2),
                        "t_stat": round(t_stat, 2),
                        "win_rate": round(float((abnormal > 0).mean()), 3),
                        "mean_net_bps": round(float(net.mean()), 2),
                        "mean_cost_bps": round(float(np.mean([r.cost_bps for r in group])), 2),
                    }
                )
    return pd.DataFrame(rows)


def run_study(
    events_path: Path,
    bars_dir: Path,
    calendar: list[date],
    out_dir: Path,
    settings: StudySettings,
    friction: FrictionSettings,
    *,
    stress: bool = False,
) -> dict[str, Path]:
    """Full pipeline: load events, filter, compute window returns, aggregate."""
    events = pd.read_parquet(events_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    filtered = apply_market_filters(events, bars_dir, calendar, settings)
    results = compute_window_returns(filtered, bars_dir, calendar, settings, friction, stress=stress)
    agg = aggregate(results)
    suffix = "stress" if stress else "base"
    agg_path = out_dir / f"aggregate_{suffix}.parquet"
    agg.to_parquet(agg_path, index=False)
    return {"aggregate": agg_path}


__all__ = [
    "apply_market_filters",
    "benchmark_daily_returns",
    "compute_window_returns",
    "aggregate",
    "run_study",
]
