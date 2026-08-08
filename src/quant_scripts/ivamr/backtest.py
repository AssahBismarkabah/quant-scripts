"""IVAMR backtest engine over NQ 15-min RTH bars.

Implements the frozen rule set from IA/ivamr-research-spec.md §2 (= IVAMR.md).
Key mechanics, faithful and look-ahead-free:

- The day's profile (POC/VAH/VAL) and ATR are computed from the PREVIOUS RTH
  day's 1-min/15-min bars (see profile.py), never the current day.
- Entries execute at the OPEN of the candle AFTER the signal/confirmation candle
  (market order):
    * Play 1/2 (3-candle pattern): signal completes at bar N+1 close -> fill at
      open of bar N+2 (per IVAMR 8.C).
    * Play 3/4 (single-candle signal): signal at bar N close -> fill at open of
      bar N+1.
- Single position (sequential intraday); per-day kill switch halts the day once
  cumulative equity-% loss reaches -3% (each trade risks 1%, full stop = -1%).
- Plays 1/2 exit via trailing stop with B/E move at +1.5 ATR, evaluated INTRA-BAR
  on the 15-min high/low, never close-only (IVAMR 8.D).
- Plays 3/4 exit at stop (trigger extreme +/- 0.5 ATR) or previous-day POC,
  stop-first. Pre-flight R:R abort (POC correct side; target >= 1.5*stop).
- Friction applied per round trip at exit; reported in index points, plus an
  equity-% per trade under the 1% risk rule.

Loop convention: at each bar i we (1) manage any open position using bar i's
intra-bar high/low, then (2) if flat, detect signals whose fill lands at the
open of a later bar. A Play1/2 fill at bar i+1 should have bar i+1 as its first
management bar, so when a fill is taken we advance i accordingly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import StudyParams
from .profile import compute_atr, compute_profile


def _hms(s: str) -> str:
    return s + ":00" if s.count(":") == 1 else s


def _prep_days(one: pd.DataFrame, fifteen: pd.DataFrame, params: StudyParams):
    """Build per-day 15m bars plus the PREVIOUS day's profile and ATR.

    Returns dict date -> {bars: DataFrame(15m), profile: dict, atr: float}.
    profile/atr for day D come from day D-1's RTH data.
    """
    one_by_date = {d: g for d, g in one.groupby("date", sort=True)}
    fifteen_by_date = {d: g for d, g in fifteen.groupby("date", sort=True)}
    all_dates = sorted(fifteen_by_date.keys())

    days = {}
    prev_prof = None
    prev_atr = np.nan
    for d in all_dates:
        d15 = fifteen_by_date[d].sort_values("t").reset_index(drop=True)
        days[d] = {"bars": d15, "profile": prev_prof, "atr": prev_atr}
        d1m = one_by_date.get(d)
        if d1m is not None:
            prev_prof = compute_profile(d1m, params)
            prev_atr = compute_atr(d15, params.atr_period)
    return days


def _resolve_rev_exit(row, entry, side, stop, target) -> tuple:
    hi = float(row["high"])
    lo = float(row["low"])
    if side == 1:  # long
        if lo <= stop:
            return stop, "stop"
        if hi >= target:
            return target, "target"
        return None, None
    else:
        if hi >= stop:
            return stop, "stop"
        if lo <= target:
            return target, "target"
        return None, None


def _manage_trend(row, idx, bars15, entry, side, atr, params, stop_raised, open_stop):
    """Return (exit_price, reason, stop_raised, open_stop) for Plays 1/2."""
    be_level = entry + params.trend_be_atr * atr if side == 1 else entry - params.trend_be_atr * atr
    stop = open_stop
    raised = stop_raised
    triggered_be = (row["high"] >= be_level) if side == 1 else (row["low"] <= be_level)

    if triggered_be:
        raised = True
    if raised:
        if side == 1:
            tr_low = bars15.iloc[max(0, idx - params.trend_trail_period + 1): idx + 1]["low"].min()
            stop = max(stop, tr_low)
        else:
            tr_high = bars15.iloc[max(0, idx - params.trend_trail_period + 1): idx + 1]["high"].max()
            stop = min(stop, tr_high)

    hit = (row["low"] <= stop) if side == 1 else (row["high"] >= stop)
    if hit:
        return stop, ("trail" if raised else "stop"), raised, stop
    return None, None, raised, stop


def run_backtest(bars: dict[str, pd.DataFrame], params: StudyParams,
                 window: tuple[str, str]) -> pd.DataFrame:
    """Run IVAMR over `window` (inclusive). bars={"1m":..., "15m":...}."""
    one = bars["1m"].copy()
    fifteen = bars["15m"].copy()

    tz = one["t"].iloc[0].tz
    w0 = pd.Timestamp(window[0], tz=tz)
    w1 = pd.Timestamp(window[1], tz=tz) + pd.Timedelta(days=1)

    # Profiles need the PREVIOUS trading day, which may be outside the window, so
    # compute profiles over the full frame and only EMIT trades for in-window dates.
    days = _prep_days(one, fifteen, params)

    entry_start_t = pd.Timestamp(_hms(params.entry_start)).time()
    signal_cutoff_t = pd.Timestamp(_hms(params.signal_cutoff)).time()
    entry_end_t = pd.Timestamp(_hms(params.entry_end)).time()
    hard_exit_t = pd.Timestamp(_hms(params.hard_exit)).time()

    trades: list[dict] = []

    for d, info in days.items():
        if not (w0.date() <= d <= w1.date()):
            continue
        bars15 = info["bars"]
        prof = info["profile"]
        atr = info["atr"]
        if prof is None or not np.isfinite(atr):
            continue
        vah, val, poc = prof["vah"], prof["val"], prof["poc"]
        if not (np.isfinite(vah) and np.isfinite(val) and np.isfinite(poc)):
            continue
        if not (val < poc < vah) or atr <= 0:
            continue

        open_side = 0
        open_entry = 0.0
        open_play = 0
        open_stop = 0.0
        open_target = None
        open_t = None
        stop_raised = False
        day_equity_pct = 0.0
        day_flat = False
        n = len(bars15)

        i = 0
        while i < n:
            row = bars15.iloc[i]
            tof = row["t"].time()

            # --- 1) manage an open position on this bar (intra-bar) ---
            if open_side != 0:
                exit_price = reason = None
                if open_play in (1, 2):
                    exit_price, reason, stop_raised, open_stop = _manage_trend(
                        row, i, bars15, open_entry, open_side, atr, params, stop_raised, open_stop)
                else:
                    exit_price, reason = _resolve_rev_exit(row, open_entry, open_side, open_stop, open_target)

                if exit_price is None and tof >= hard_exit_t:
                    exit_price = float(row["open"])
                    reason = "time"

                if exit_price is not None:
                    gross = open_side * (exit_price - open_entry)
                    net = gross - params.friction_base_pts
                    risk_pts = abs(open_stop - open_entry) if open_stop != open_entry else (abs(gross) if gross != 0 else 1.0)
                    equity_pct = (gross / risk_pts) if risk_pts > 0 else 0.0
                    trades.append({
                        "date": d, "play": open_play,
                        "side": "long" if open_side == 1 else "short",
                        "entry_t": open_t, "exit_t": row["t"],
                        "entry": open_entry, "exit": exit_price,
                        "exit_reason": reason,
                        "gross_pts": round(gross, 2), "net_pts": round(net, 2),
                        "win": bool(gross > 0), "equity_pct": round(equity_pct, 6),
                    })
                    day_equity_pct += equity_pct
                    open_side = 0
                    stop_raised = False
                    if day_equity_pct <= -params.daily_kill_loss_frac:
                        day_flat = True
                        break

            # --- 2) detect entry signals (only when flat and day not halted) ---
            if open_side == 0 and not day_flat:
                can_signal = entry_start_t <= tof <= signal_cutoff_t
                if can_signal:
                    filled = False
                    # Play 1/2: breakout at bar i-1 close, retest+confirm close at bar i -> fill i+1 open
                    if i >= 1:
                        prev = bars15.iloc[i - 1]
                        if prev["close"] > vah and row["low"] <= vah and row["low"] >= vah - params.rev_structural_atr * atr and row["close"] > vah:
                            if i + 1 < n and bars15.iloc[i + 1]["t"].time() <= entry_end_t:
                                fill = bars15.iloc[i + 1]
                                open_side, open_play, open_entry = 1, 1, float(fill["open"])
                                open_stop = open_entry - params.trend_stop_atr * atr
                                open_t, stop_raised = fill["t"], False
                                i += 1
                                filled = True
                        elif prev["close"] < val and row["high"] >= val and row["high"] <= val + params.rev_structural_atr * atr and row["close"] < val:
                            if i + 1 < n and bars15.iloc[i + 1]["t"].time() <= entry_end_t:
                                fill = bars15.iloc[i + 1]
                                open_side, open_play, open_entry = -1, 2, float(fill["open"])
                                open_stop = open_entry + params.trend_stop_atr * atr
                                open_t, stop_raised = fill["t"], False
                                i += 1
                                filled = True

                    # Play 3/4: single-candle signal at bar i -> fill i+1 open
                    if open_side == 0:
                        rng = row["high"] - row["low"]
                        side = 0
                        trigger_ext = None
                        if row["low"] < val and row["close"] > val and rng > 0 and (row["close"] - row["low"]) / rng >= params.retest_zone_close:
                            side, trigger_ext = 1, float(row["low"])
                        elif row["high"] > vah and row["close"] < vah and rng > 0 and (row["high"] - row["close"]) / rng >= params.retest_zone_close:
                            side, trigger_ext = -1, float(row["high"])
                        if side != 0:
                            if i + 1 < n and bars15.iloc[i + 1]["t"].time() <= entry_end_t:
                                fill = bars15.iloc[i + 1]
                                entry = float(fill["open"])
                                if side == 1:
                                    stop = trigger_ext - params.rev_stop_atr * atr
                                    ok = poc > entry and (poc - entry) >= params.rev_min_rr * (entry - stop)
                                else:
                                    stop = trigger_ext + params.rev_stop_atr * atr
                                    ok = poc < entry and (entry - poc) >= params.rev_min_rr * (stop - entry)
                                if ok and (entry - stop) > 0:
                                    open_side, open_play, open_entry = side, 3 if side == 1 else 4, entry
                                    open_stop, open_target = stop, poc
                                    open_t, stop_raised = fill["t"], False
                                    i += 1
                                    filled = True
                    if filled:
                        continue

            i += 1

        # any position still open at end of window/day -> flat at last available close
        if open_side != 0 and not day_flat:
            last = bars15.iloc[-1]
            exit_price = float(last["close"])
            gross = open_side * (exit_price - open_entry)
            net = gross - params.friction_base_pts
            trades.append({
                "date": d, "play": open_play,
                "side": "long" if open_side == 1 else "short",
                "entry_t": open_t, "exit_t": last["t"],
                "entry": open_entry, "exit": exit_price,
                "exit_reason": "endofday",
                "gross_pts": round(gross, 2), "net_pts": round(net, 2),
                "win": bool(gross > 0), "equity_pct": round(gross / (abs(open_stop - open_entry) if open_stop != open_entry else 1.0), 6),
            })

    if not trades:
        return pd.DataFrame()
    return pd.DataFrame(trades)
