"""Look-ahead-free backtest engines for the opening-range / gap trio.

Each strategy runs over 5-min RTH bars, one day at a time, and is independent.
One entry per day per strategy (transcript-confirmed single setup). All inputs
that must be known in advance come from prior bars only:

- ORB:      first 15-min RTH range built from 1-min bars in [09:30, 09:45),
            complete before any trigger; a 5-min close beyond it is the signal.
- Gap Fill: the gap (open vs PREVIOUS day's close) is known at 09:30; enter in
            the fill direction on a 5-min close showing a move toward the fill.
- Oops:     prev-day high/low known from D-1; gap >= 20 pts beyond; enter on a
            5-min close breaking back through the level.

Common, look-ahead-free conventions:
- A signal is confirmed by a 5-min bar CLOSE; the fill is the OPEN of the NEXT
  5-min bar (market order), so the signal bar's close is never used at entry.
- Stops/targets are expressed as LEVELS set by the signal, but the target's RR
  distance is computed from the ACTUAL fill price and the stop level, so the
  risk:reward is exact and independent of the signal-bar open (gate-6 fix).
- Open positions are managed intra-bar (bar high/low), stop-first. Time exit at
  force_flat; Oops exits at the next 5-min bar close (transcript wording).

Trade rows: date, strategy, side, entry_t, exit_t, entry, exit, exit_reason,
gross_pts, net_pts, win, equity_pct.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import StudyParams


def _hms(s: str):
    return pd.Timestamp(s).time()


def _prev_day_stats(one_by_date) -> dict:
    """date(D) -> {hi, lo, close} of the immediately preceding available day."""
    dates = sorted(one_by_date.keys())
    stats = {}
    for i, d in enumerate(dates):
        if i == 0:
            stats[d] = None
        else:
            p = one_by_date[dates[i - 1]]
            stats[d] = {
                "hi": float(p["high"].max()),
                "lo": float(p["low"].min()),
                "close": float(p["close"].iloc[-1]),
            }
    return stats


def _open_range(day1m: pd.DataFrame, minutes: int) -> dict | None:
    """First `minutes`-minute RTH range from 1-min bars in [09:30, 09:30+minutes)."""
    t0 = pd.Timestamp("09:30").time()
    t1 = (pd.Timestamp("09:30") + pd.Timedelta(minutes=minutes)).time()
    sub = day1m[(day1m["t"].dt.time >= t0) & (day1m["t"].dt.time < t1)]
    if sub.empty:
        return None
    return {"hi": float(sub["high"].max()), "lo": float(sub["low"].min())}


def _make_trade(d, which, side, entry_t, exit_t, entry, exit_price, reason, stop, friction):
    gross = side * (exit_price - entry)
    net = gross - friction
    risk = abs(stop - entry) if abs(stop - entry) > 0 else 1.0
    return {
        "date": d, "strategy": which,
        "side": "long" if side == 1 else "short",
        "entry_t": entry_t, "exit_t": exit_t,
        "entry": round(entry, 2), "exit": round(exit_price, 2),
        "exit_reason": reason,
        "gross_pts": round(gross, 2), "net_pts": round(net, 2),
        "win": bool(gross > 0), "equity_pct": round(gross / risk, 6),
    }


def run_orb(bars: dict[str, pd.DataFrame], params: StudyParams,
            window: tuple[str, str]) -> pd.DataFrame:
    """Opening Range Breakout, 5-min close entry, stop at range-other-side, 1:2."""
    return _run_trio(bars, params, window, "orb")


def run_gap_fill(bars: dict[str, pd.DataFrame], params: StudyParams,
                 window: tuple[str, str]) -> pd.DataFrame:
    """Gap Fill: enter in fill direction, target = prev-day close, flat at close."""
    return _run_trio(bars, params, window, "gap_fill")


def run_oops(bars: dict[str, pd.DataFrame], params: StudyParams,
             window: tuple[str, str]) -> pd.DataFrame:
    """Oops: gap >=20 pts beyond prev-day high/low, break-back entry, next-close exit."""
    return _run_trio(bars, params, window, "oops")


def _run_trio(bars: dict[str, pd.DataFrame], params: StudyParams,
              window: tuple[str, str], which: str) -> pd.DataFrame:
    one = bars["1m"].copy()
    five = bars["5m"].copy()
    tz = one["t"].iloc[0].tz
    w0 = pd.Timestamp(window[0], tz=tz)
    w1 = pd.Timestamp(window[1], tz=tz) + pd.Timedelta(days=1)

    one_by_date = {d: g for d, g in one.groupby("date", sort=True)}
    five_by_date = {d: g for d, g in five.groupby("date", sort=True)}
    prev = _prev_day_stats(one_by_date)

    no_entry_t = _hms(params.no_new_entries_after)
    flat_t = _hms(params.force_flat)
    earliest_t = _hms(getattr(params, {
        "orb": "orb_no_entry_before", "gap_fill": "gap_fill_no_entry_before",
        "oops": "oops_no_entry_before"}[which]))

    trades: list[dict] = []

    for d, d5 in five_by_date.items():
        if not (w0.date() <= d <= w1.date()):
            continue
        p = prev.get(d)
        if p is None:
            continue
        d5 = d5.sort_values("t").reset_index(drop=True)
        d1m = one_by_date.get(d)
        orb_rng = _open_range(d1m, params.orb_range_min) if d1m is not None else None

        side = 0            # 0 flat, +1 long, -1 short
        entry = stop = 0.0
        target = None
        entry_t = None
        traded_today = False
        first_manage_idx = None       # bar index at which we fill (its open is entry)
        n = len(d5)

        i = 0
        while i < n:
            row = d5.iloc[i]
            tof = row["t"].time()
            o, h, l, c = float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"])

            # --- 1) manage an open position (intra-bar, stop-first) ---
            if side != 0 and i >= first_manage_idx:
                exit_price, reason = None, None
                if side == 1:
                    if l <= stop:
                        exit_price, reason = stop, "stop"
                    elif target is not None and h >= target:
                        exit_price, reason = target, "target"
                    elif which == "oops" and i >= first_manage_idx:
                        exit_price, reason = c, "next_close"
                else:
                    if h >= stop:
                        exit_price, reason = stop, "stop"
                    elif target is not None and l <= target:
                        exit_price, reason = target, "target"
                    elif which == "oops" and i >= first_manage_idx:
                        exit_price, reason = c, "next_close"
                if exit_price is None and tof >= flat_t:
                    exit_price, reason = o, "time"
                if exit_price is not None:
                    trades.append(_make_trade(d, which, side, entry_t, row["t"],
                                              entry, exit_price, reason, stop,
                                              params.friction_base_pts))
                    side = 0
                    target = None

            # --- 2) single daily entry (only when flat and not yet traded) ---
            if side == 0 and not traded_today and earliest_t <= tof <= no_entry_t:
                sig_side, sig_stop, sig_target = 0, None, None
                if which == "orb" and orb_rng is not None and orb_rng["hi"] > orb_rng["lo"]:
                    if i >= 1:
                        pb = d5.iloc[i - 1]
                        if c > orb_rng["hi"] and pb["close"] <= orb_rng["hi"]:
                            sig_side, sig_stop = 1, float(orb_rng["lo"])
                        elif c < orb_rng["lo"] and pb["close"] >= orb_rng["lo"]:
                            sig_side, sig_stop = -1, float(orb_rng["hi"])
                elif which == "gap_fill":
                    gap_up = o > p["close"]
                    gap_down = o < p["close"]
                    if gap_up or gap_down:
                        if i >= 1:
                            pb = d5.iloc[i - 1]
                            if gap_down and c > o and pb["close"] <= pb["open"]:
                                sig_side, sig_target = 1, float(p["close"])
                            elif gap_up and c < o and pb["close"] >= pb["open"]:
                                sig_side, sig_target = -1, float(p["close"])
                        if sig_side != 0:
                            sig_stop = float(p["lo"] - params.oops_stop_buffer_pts) if sig_side == 1 else float(p["hi"] + params.oops_stop_buffer_pts)
                elif which == "oops":
                    if o > p["hi"] + params.oops_min_gap_pts:
                        if i >= 1 and c < p["hi"] <= d5.iloc[i - 1]["close"]:
                            sig_side, sig_stop = -1, float(p["hi"] + params.oops_stop_buffer_pts)
                    elif o < p["lo"] - params.oops_min_gap_pts:
                        if i >= 1 and c > p["lo"] >= d5.iloc[i - 1]["close"]:
                            sig_side, sig_stop = 1, float(p["lo"] - params.oops_stop_buffer_pts)

                if sig_side != 0 and i + 1 < n:
                    fill = d5.iloc[i + 1]
                    entry = float(fill["open"])
                    stop = sig_stop
                    if sig_target is not None:
                        target = sig_target
                    elif which in ("orb",):
                        # RR target computed from the ACTUAL fill and stop level
                        dist = abs(entry - stop) if abs(entry - stop) > 0 else 1.0
                        target = entry + params.orb_target_rr * dist if sig_side == 1 else entry - params.orb_target_rr * dist
                    entry_t = fill["t"]
                    side = sig_side
                    traded_today = True
                    first_manage_idx = i + 1
                    i += 1  # consume the fill bar as its own first management bar
                    continue

            i += 1

        if side != 0:
            last = d5.iloc[-1]
            trades.append(_make_trade(d, which, side, entry_t, last["t"],
                                      entry, float(last["close"]), "endofday",
                                      stop, params.friction_base_pts))

    if not trades:
        return pd.DataFrame()
    return pd.DataFrame(trades)


def gap_fill_rate(bars: dict[str, pd.DataFrame], params: StudyParams,
                  window: tuple[str, str]) -> dict:
    """Pure statistical claim: fraction of gap-open days whose gap fills by 16:00.

    Direction-agnostic: for a gap-down day, a fill is any intraday high >= prev
    close; for a gap-up day, any intraday low <= prev close.
    """
    one = bars["1m"].copy()
    tz = one["t"].iloc[0].tz
    w0 = pd.Timestamp(window[0], tz=tz)
    w1 = pd.Timestamp(window[1], tz=tz) + pd.Timedelta(days=1)
    by_date = {d: g for d, g in one.groupby("date", sort=True)}
    prev = _prev_day_stats(by_date)

    filled = gapped = total_days = 0
    for d, g in by_date.items():
        if not (w0.date() <= d <= w1.date()):
            continue
        p = prev.get(d)
        if p is None:
            continue
        total_days += 1
        o = float(g["open"].iloc[0])
        if o > p["close"]:
            gapped += 1
            if float(g["low"].min()) <= p["close"]:
                filled += 1
        elif o < p["close"]:
            gapped += 1
            if float(g["high"].max()) >= p["close"]:
                filled += 1
    rate = (filled / gapped) if gapped else None
    return {"total_days": total_days, "gapped_days": gapped,
            "filled_days": filled, "fill_rate": round(rate, 4) if rate is not None else None}
