"""Backtest engine for the NQ VWAP-pullback ("Drift VWOP Pullback") probe.

Implements the frozen rule set from IA/nq-vwap-pullback-research-spec.md §2 over
Databento NQ 5-min/15-min RTH bars with a session-anchored VWAP.

Mechanics (faithful to the frozen spec, reproducible, no look-ahead):
  - Trend regime evaluated once per 15-min bucket and held for the 5-min bars
    inside that bucket.
    LONG active : close > VWAP AND VWAP rising (VWAP > prior 15min VWAP)
                  AND 1h return (close vs close 4 x 15min ago) >= +0.10%.
    SHORT active: close < VWAP AND VWAP falling AND 1h return <= -0.10%.
  - No entries 09:30..10:30 ET; no new entries after 15:30 ET; flat at 15:55.
  - Entry (LONG): while LONG active, the FIRST red (close<open) 5-min pullback
    candle triggers; a market order fills at the OPEN of the following 5-min bar.
    SHORT mirrors (first green candle).
  - Exits: LONG stop 80 pts below entry / target 40 pts above; SHORT 80/50.
    Resolved bar-by-bar (stop if low<=stop; else target if high>=target).
  - Guard rails: 1 position at a time; max 4 trades/day; max 2 losses/day (stop
    after 2 losses in a session).
  - Friction applied per round trip (pts) at the decision window.

Returns a per-trade frame plus per-day summaries so the gate functions in
run_probe can decide IS reproduction and OOS advance/disconfirm.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import StudyParams


def _hms(s: str) -> str:
    return s + ":00" if s.count(":") == 1 else s


def _build_regime(fifteen: pd.DataFrame, params: StudyParams) -> pd.DataFrame:
    """Assign long_active/short_active to each 15-min bucket (in bucket time)."""
    f = fifteen.sort_values("t").reset_index(drop=True)
    prev_vwap = f["vwap"].shift(1)
    close4 = f["close"].shift(4)
    ret_1h = f["close"] / close4 - 1.0
    vwap_up = f["vwap"] > prev_vwap
    price_above = f["close"] > f["vwap"]
    thr = params.drift_return_bps / 1e4
    long_active = price_above & vwap_up & (ret_1h >= thr) & close4.notna()
    short_active = (~price_above) & (~vwap_up) & (ret_1h <= -thr) & close4.notna()
    f["long_active"] = long_active.fillna(False)
    f["short_active"] = short_active.fillna(False)
    return f


def _attach_regime(five: pd.DataFrame, regime: pd.DataFrame, params: StudyParams) -> pd.DataFrame:
    """Map each 5-min bar to the 15-min bucket that contains it and join regime flags."""
    f = five.sort_values("t").reset_index(drop=True)
    ref = f["t"].dt.normalize() + pd.Timedelta(hours=9, minutes=30)
    f["_bucket"] = np.floor(((f["t"] - ref).dt.total_seconds()) / (params.trend_min * 60)).astype(int)
    r = regime[["t", "long_active", "short_active"]].copy()
    rref = r["t"].dt.normalize() + pd.Timedelta(hours=9, minutes=30)
    r["_bucket"] = np.floor(((r["t"] - rref).dt.total_seconds()) / (params.trend_min * 60)).astype(int)
    r = r[["_bucket", "long_active", "short_active"]].drop_duplicates("_bucket")
    f = f.merge(r, on="_bucket", how="left")
    f["long_active"] = f["long_active"].fillna(False)
    f["short_active"] = f["short_active"].fillna(False)
    return f


def _resolve_exit_bar(row: pd.DataFrame, entry_side: int, entry_price: float, params: StudyParams) -> tuple:
    """Return (exit_price, exit_reason) resolved for a single 5-min bar given an open position.

    Conservative: stop (adverse) checked before target if the bar spans both.
    """
    hi = float(row["high"])
    lo = float(row["low"])
    if entry_side == 1:
        stop = entry_price - params.long_risk_pts
        tgt = entry_price + params.long_target_pts
        if lo <= stop:
            return stop, "stop"
        if hi >= tgt:
            return tgt, "target"
        return None, None
    else:
        stop = entry_price + params.short_risk_pts
        tgt = entry_price - params.short_target_pts
        if hi >= stop:
            return stop, "stop"
        if lo <= tgt:
            return tgt, "target"
        return None, None


def run_backtest(bars: dict[str, pd.DataFrame], params: StudyParams,
                 window: tuple[str, str]) -> pd.DataFrame:
    """Run the frozen strategy over `window` (inclusive) on the given bars.

    bars = {"1m":..., "5m":..., "15m":...} as returned by load_intraday.
    Returns a per-trade DataFrame with friction already applied (net) and px P/L
    columns plus gross P/L and win flag.
    """
    five = bars["5m"].copy()
    fifteen = bars["15m"].copy()

    # time window filter (ET-aware)
    w0 = pd.Timestamp(window[0], tz=five["t"].iloc[0].tz)
    w1 = pd.Timestamp(window[1], tz=five["t"].iloc[0].tz) + pd.Timedelta(days=1)
    five = five[(five["t"] >= w0) & (five["t"] < w1)].sort_values("t").reset_index(drop=True)

    regime = _build_regime(fifteen, params)
    five = _attach_regime(five, regime, params)

    no_trade_until = pd.Timestamp(_hms(params.no_trade_until)).time()
    no_new_after = pd.Timestamp(_hms(params.no_new_trades_after)).time()
    force_flat = pd.Timestamp(_hms(params.force_flat)).time()

    trades: list[dict] = []
    open_side = 0
    open_entry = 0.0
    open_entry_t = None
    trades_today = 0
    losses_today = 0
    current_date = None
    pending_side = 0  # armed by a pullback trigger candle; executed at next bar open

    for i in range(len(five)):
        row = five.iloc[i]
        t = row["t"]
        d = t.date()
        tof = t.time()

        # day boundary: reset daily counters
        if d != current_date:
            current_date = d
            trades_today = 0
            losses_today = 0

        # --- resolve an existing position on this bar's OHLC ---
        if open_side != 0:
            exit_price, reason = _resolve_exit_bar(row, open_side, open_entry, params)
            if exit_price is None and tof >= force_flat:
                # force flat at 15:55 ET at this bar's open
                exit_price = float(row["open"])
                reason = "flat"
            if exit_price is not None:
                gross = open_side * (exit_price - open_entry)
                net = gross - params.friction_base_pts
                is_win = open_side * (exit_price - open_entry) > 0
                trades.append(
                    {
                        "date": d,
                        "entry_t": open_entry_t,
                        "exit_t": t,
                        "side": "long" if open_side == 1 else "short",
                        "entry": open_entry,
                        "exit": exit_price,
                        "exit_reason": reason,
                        "gross_pts": round(gross, 2),
                        "net_pts": round(net, 2),
                        "win": bool(is_win),
                    }
                )
                trades_today += 1
                if not is_win:
                    losses_today += 1
                open_side = 0
                pending_side = 0

        # --- entry logic (only when flat) ---
        if open_side == 0:
            can_enter = (
                tof >= no_trade_until
                and tof <= no_new_after
                and trades_today < params.max_trades_per_day
                and losses_today < params.max_losses_per_day
            )
            # refresh pending from the previous bar as trigger only if regime active at trigger
            # trigger candle = previous 5-min bar; enter at this bar's open
            if i >= 1 and can_enter:
                prev = five.iloc[i - 1]
                prev_t = prev["t"]
                # no-trade window / after-limit check on prev too for correctness
                prev_ok = prev_t.time() >= no_trade_until and prev_t.time() <= no_new_after
                if prev_ok:
                    if prev["long_active"] and prev["close"] < prev["open"]:
                        pending_side = 1
                    elif prev["short_active"] and prev["close"] > prev["open"]:
                        pending_side = -1
            # if pending armed, enter at this bar's open (position taken / arm clear)
            if pending_side != 0 and can_enter:
                open_side = pending_side
                open_entry = float(row["open"])
                open_entry_t = t
                pending_side = 0

    # any position still open at end of window -> close at last bar close (non-ideal; flat rule should prevent)
    if open_side != 0:
        last = five.iloc[-1]
        exit_price = float(last["close"])
        gross = open_side * (exit_price - open_entry)
        net = gross - params.friction_base_pts
        is_win = open_side * (exit_price - open_entry) > 0
        trades.append(
            {
                "date": open_entry_t.date() if open_entry_t is not None else last["t"].date(),
                "entry_t": open_entry_t,
                "exit_t": last["t"],
                "side": "long" if open_side == 1 else "short",
                "entry": open_entry,
                "exit": exit_price,
                "exit_reason": "endoflist",
                "gross_pts": round(gross, 2),
                "net_pts": round(net, 2),
                "win": bool(is_win),
            }
        )

    if not trades:
        return pd.DataFrame()
    return pd.DataFrame(trades)
