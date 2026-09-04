"""Event-driven backtest for the frozen ES value-area opening-state study."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .profile import compute_profile


def rth_15m(one: pd.DataFrame) -> pd.DataFrame:
    """Aggregate ET RTH one-minute bars into bars anchored at 09:30."""
    frame = one.sort_values("ts").copy()
    frame["date"] = frame["ts"].dt.date
    frame["slot"] = frame.groupby("date").cumcount() // 15
    out = frame.groupby(["date", "slot"], sort=True).agg(
        ts=("ts", "first"), open=("open", "first"), high=("high", "max"),
        low=("low", "min"), close=("close", "last"), volume=("volume", "sum"),
        n_1m=("ts", "size"),
    ).reset_index()
    return out


def classify_opening(closes: list[float], val: float, vah: float) -> str:
    if len(closes) != 4:
        return "UNCLASSIFIED"
    if sum(val <= x <= vah for x in closes) >= 3:
        return "IN_VALUE"
    if sum(x > vah for x in closes) >= 3:
        return "OUT_ABOVE"
    if sum(x < val for x in closes) >= 3:
        return "OUT_BELOW"
    return "UNCLASSIFIED"


def _wick_ratio(row: pd.Series, side: str) -> float:
    rng = float(row.high - row.low)
    if rng <= 0:
        return 0.0
    if side == "long":
        return float((min(row.open, row.close) - row.low) / rng)
    return float((row.high - max(row.open, row.close)) / rng)


def run_backtest(one: pd.DataFrame, start: str, end: str,
                 base_friction: float = 0.50, stress_friction: float = 1.00) -> pd.DataFrame:
    """Run the frozen strategy; returns one row per completed position."""
    one = one.copy()
    one["ts"] = pd.to_datetime(one["ts"])
    one["date"] = one["ts"].dt.date
    one = one.sort_values("ts")
    fifteen = rth_15m(one)
    days = {d: g.reset_index(drop=True) for d, g in fifteen.groupby("date", sort=True)}
    one_days = {d: g.reset_index(drop=True) for d, g in one.groupby("date", sort=True)}
    dates = sorted(days)
    start_d, end_d = pd.Timestamp(start).date(), pd.Timestamp(end).date()
    trades = []
    prior_profile = None
    for d in dates:
        bars = days[d]
        current_1m = one_days[d]
        profile = prior_profile
        prior_profile = compute_profile(current_1m)
        if d < start_d or d > end_d or profile is None:
            continue
        val, vah, poc = profile["val"], profile["vah"], profile["poc"]
        if not all(np.isfinite(x) for x in (val, vah, poc)) or not val < poc < vah:
            continue
        if len(bars) < 5:
            continue
        state = classify_opening(bars.iloc[:4]["close"].tolist(), val, vah)
        if state == "UNCLASSIFIED":
            continue
        entries = 0
        position = None
        for i in range(4, len(bars)):
            bar = bars.iloc[i]
            bar_time = bar.ts.time()
            if position is not None:
                exit_price = reason = None
                exit_qty = position["qty"]
                if position["side"] == 1:
                    if bar.low <= position["stop"]:
                        exit_price, reason = position["stop"], "stop"
                    elif position["target1"] is not None and bar.high >= position["target1"]:
                        exit_price, reason, exit_qty = position["target1"], "target1", position["qty"] / 2
                    elif position["target2"] is not None and bar.high >= position["target2"]:
                        exit_price, reason = position["target2"], "target2"
                else:
                    if bar.high >= position["stop"]:
                        exit_price, reason = position["stop"], "stop"
                    elif position["target1"] is not None and bar.low <= position["target1"]:
                        exit_price, reason, exit_qty = position["target1"], "target1", position["qty"] / 2
                    elif position["target2"] is not None and bar.low <= position["target2"]:
                        exit_price, reason = position["target2"], "target2"
                if exit_price is None and bar_time >= pd.Timestamp("15:55").time():
                    minute = current_1m[current_1m.ts.dt.time >= pd.Timestamp("15:55").time()]
                    exit_price, reason = (float(minute.iloc[0].open), "time") if len(minute) else (float(bar.open), "time")
                if exit_price is not None:
                    side, entry = position["side"], position["entry"]
                    gross = side * (float(exit_price) - entry) * exit_qty
                    trades.append({"date": d, "state": state, "side": "long" if side == 1 else "short",
                                   "setup": position["setup"], "entry_t": position["entry_t"],
                                   "exit_t": bar.ts, "entry": entry, "exit": float(exit_price),
                                   "exit_reason": reason, "quantity": exit_qty, "gross_pts": gross,
                                   "base_net_pts": gross - base_friction,
                                   "stress_net_pts": gross - stress_friction})
                    if reason == "target1" and position["qty"] > 0.5:
                        position["qty"] = 0.5
                        position["target1"] = None
                    else:
                        position = None
                    if reason != "time":
                        continue
            if position is not None or entries >= 2 or not (bar_time <= pd.Timestamp("15:00").time()):
                continue
            side = setup = None
            stop = target1 = target2 = None
            if state == "IN_VALUE":
                if bar.low < val <= bar.close and _wick_ratio(bar, "long") >= 0.40:
                    side, setup = 1, "value_long"; stop = bar.low - 2.0; target1, target2 = poc, vah
                elif bar.high > vah >= bar.close and _wick_ratio(bar, "short") >= 0.40:
                    side, setup = -1, "value_short"; stop = bar.high + 2.0; target1, target2 = poc, val
            elif state == "OUT_ABOVE" and bar.low <= vah + 1.0 and bar.close > vah and bar.close > bar.open:
                side, setup = 1, "trend_long"; stop = vah - 2.5; target1, target2 = bar.close + 10.0, bar.close + 20.0
            elif state == "OUT_BELOW" and bar.high >= val - 1.0 and bar.close < val and bar.close < bar.open:
                side, setup = -1, "trend_short"; stop = val + 2.5; target1, target2 = bar.close - 10.0, bar.close - 20.0
            if side is None:
                continue
            fill_i = i + 1
            if fill_i >= len(bars) or bars.iloc[fill_i].ts.time() > pd.Timestamp("15:00").time() or entries >= 2:
                continue
            entry = float(bars.iloc[fill_i].open)
            if (side == 1 and not stop < entry < target1 < target2) or (side == -1 and not stop > entry > target1 > target2):
                continue
            position = {"side": side, "setup": setup, "entry": entry, "entry_t": bars.iloc[fill_i].ts,
                        "stop": float(stop), "target1": float(target1), "target2": float(target2), "qty": 1.0}
            entries += 1
        if position is not None:
            bar = bars.iloc[-1]
            exit_price = float(bar.close)
            side, entry = position["side"], position["entry"]
            gross = side * (exit_price - entry) * position["qty"]
            trades.append({"date": d, "state": state, "side": "long" if side == 1 else "short",
                           "setup": position["setup"], "entry_t": position["entry_t"], "exit_t": bar.ts,
                           "entry": entry, "exit": exit_price, "exit_reason": "session_end", "quantity": position["qty"], "gross_pts": gross,
                           "base_net_pts": gross - base_friction, "stress_net_pts": gross - stress_friction})
    return pd.DataFrame(trades)
