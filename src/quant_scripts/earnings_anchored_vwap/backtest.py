"""Pure daily-bar engine for the earnings-anchored VWAP proxy.

The engine intentionally operates on raw daily OHLCV. It never uses an
announcement-day close to decide an event, and reaction signals enter only at
the following session's open. Stop/target collisions are resolved adversely
(stop first), as frozen in IA/earnings-anchored-vwap-research-gate.md.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from .config import StudyParams

ReferenceKind = Literal["avwap", "unweighted"]
# anchor_mode controls which session an earnings event anchors to:
#   "label"       - frozen: pre -> first session on/after date, post -> session strictly after date
#   "next_open"   - free label-free fallback: always the first session on/after the release date.
#                   The stored release_time is ignored for anchoring but kept in output.
AnchorMode = Literal["label", "next_open"]

_REQUIRED_BAR_COLUMNS = {
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "split_coefficient",
}


@dataclass(frozen=True)
class EventSetup:
    """An earnings event that cleared the pre-signal eligibility screen."""

    symbol: str
    release_date: pd.Timestamp
    release_time: str
    anchor_idx: int
    side: int
    gap: float
    atr20: float
    median_dollar_volume20: float


def prepare_symbol_bars(raw: pd.DataFrame, params: StudyParams) -> pd.DataFrame:
    """Normalize one symbol's daily bars and attach strictly lagged features."""
    missing = _REQUIRED_BAR_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"daily bars missing columns: {sorted(missing)}")

    bars = raw.copy()
    bars["date"] = pd.to_datetime(bars["date"]).dt.normalize()
    for column in ("open", "high", "low", "close", "volume", "split_coefficient"):
        bars[column] = pd.to_numeric(bars[column], errors="coerce")
    bars = bars.sort_values("date").reset_index(drop=True)
    if bars["date"].duplicated().any():
        raise ValueError("daily bars contain duplicate sessions for a symbol")

    raw_values = bars[["open", "high", "low", "close", "volume", "split_coefficient"]].to_numpy(
        dtype=float
    )
    bars["valid_integrity_bar"] = (
        np.isfinite(raw_values).all(axis=1)
        & (bars["open"] > 0)
        & (bars["high"] > 0)
        & (bars["low"] > 0)
        & (bars["close"] > 0)
        & (bars["volume"] > 0)
        & (bars["high"] >= bars[["open", "low", "close"]].max(axis=1))
        & (bars["low"] <= bars[["open", "high", "close"]].min(axis=1))
        & np.isclose(bars["split_coefficient"], 1.0)
    )

    bars["typical_price"] = (bars["high"] + bars["low"] + bars["close"]) / 3.0
    bars["prev_close"] = bars["close"].shift(1)
    true_range = np.maximum(
        bars["high"] - bars["low"],
        np.maximum(
            (bars["high"] - bars["prev_close"]).abs(),
            (bars["low"] - bars["prev_close"]).abs(),
        ),
    )
    # The first observed session has no prior close; its intraday range is still
    # a valid true-range observation for the later, strictly lagged ATR window.
    true_range = true_range.fillna(bars["high"] - bars["low"])
    # Both filters use only sessions known before the anchor opens.
    bars["atr20"] = true_range.shift(1).rolling(
        params.atr_sessions, min_periods=params.atr_sessions
    ).mean()
    bars["median_dollar_volume20"] = (bars["close"] * bars["volume"]).shift(1).rolling(
        params.atr_sessions, min_periods=params.atr_sessions
    ).median()
    return bars


def resolve_anchor_index(
    bars: pd.DataFrame,
    release_date: object,
    release_time: str,
    anchor_mode: AnchorMode = "label",
) -> int | None:
    """Return the first executable session for an earnings event.

    In frozen ``label`` mode the stated pre/post session decides same-day vs
    strictly-after anchoring. In ``next_open`` (label-free) mode the event is
    always anchored at the first session on or after the release date, which is
    the safest date-only convention and does not depend on the disputed label.
    """
    if anchor_mode not in {"label", "next_open"}:
        return None
    if anchor_mode == "label" and release_time not in {"pre", "post"}:
        return None
    dates = bars["date"].to_numpy(dtype="datetime64[ns]")
    target = np.datetime64(pd.Timestamp(release_date).normalize())
    # label: pre -> left (same day if the release date is a session), post -> right (strictly after).
    # next_open: same-day open is the most conservative date-only anchor.
    side = "left" if (anchor_mode == "next_open" or release_time == "pre") else "right"
    idx = int(np.searchsorted(dates, target, side=side))
    return idx if idx < len(bars) else None


def event_integrity_reason(
    bars: pd.DataFrame, anchor_idx: int, params: StudyParams
) -> str | None:
    """Check the complete fixed window needed by any permitted daily trade."""
    start_idx = anchor_idx - params.atr_sessions
    end_idx = anchor_idx + params.reaction_search_sessions + params.max_holding_sessions
    if start_idx < 0 or end_idx >= len(bars):
        return "incomplete_integrity_window"
    if not bars.iloc[start_idx : end_idx + 1]["valid_integrity_bar"].all():
        return "invalid_raw_ohlcv_or_split_window"
    return None


def filter_events_by_price_integrity(
    events: pd.DataFrame,
    bars_by_symbol: dict[str, pd.DataFrame],
    params: StudyParams,
    anchor_mode: AnchorMode = "label",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Keep only events with an auditable full daily-bar study window."""
    retained_indexes: list[int] = []
    audit_rows: list[dict] = []
    for index, event in events.iterrows():
        symbol = str(event["symbol"])
        release_date = pd.Timestamp(event["release_date"]).normalize()
        release_time = str(event["release_time"]).strip().lower()
        bars = bars_by_symbol.get(symbol)
        if bars is None:
            reason = "missing_symbol_bars"
        else:
            anchor_idx = resolve_anchor_index(bars, release_date, release_time, anchor_mode)
            if anchor_idx is None:
                reason = "no_anchor_session"
            else:
                reason = event_integrity_reason(bars, anchor_idx, params) or "valid"
        if reason == "valid":
            retained_indexes.append(index)
        audit_rows.append(
            {
                "event_id": f"{symbol}|{release_date.date().isoformat()}|{release_time}",
                "symbol": symbol,
                "event_date": release_date,
                "release_time": release_time,
                "reason": reason,
            }
        )
    audit_columns = ["event_id", "symbol", "event_date", "release_time", "reason"]
    return (
        events.loc[retained_indexes].copy().reset_index(drop=True),
        pd.DataFrame(audit_rows, columns=audit_columns),
    )


def build_event_setup(
    event: pd.Series,
    bars: pd.DataFrame,
    params: StudyParams,
    anchor_mode: AnchorMode = "label",
) -> tuple[EventSetup | None, str]:
    """Apply the frozen, pre-signal event screen to one earnings record."""
    release_time = str(event["release_time"]).strip().lower()
    anchor_idx = resolve_anchor_index(bars, event["release_date"], release_time, anchor_mode)
    if anchor_idx is None:
        return None, "no_anchor_session"

    integrity_reason = event_integrity_reason(bars, anchor_idx, params)
    if integrity_reason is not None:
        return None, integrity_reason

    row = bars.iloc[anchor_idx]
    required = ("open", "prev_close", "atr20", "median_dollar_volume20")
    if any(not np.isfinite(float(row[column])) for column in required):
        return None, "missing_lagged_inputs"
    if row["prev_close"] < params.min_price:
        return None, "price_below_minimum"
    if row["median_dollar_volume20"] < params.min_median_dollar_volume:
        return None, "liquidity_below_minimum"
    if row["atr20"] <= 0 or row["prev_close"] <= 0:
        return None, "invalid_atr_or_price"

    eps = float(event["eps"])
    eps_est = float(event["eps_est"])
    gap = float(row["open"] / row["prev_close"] - 1.0)
    material_gap = float(row["atr20"] / row["prev_close"])
    if eps > eps_est and gap >= material_gap:
        side = 1
    elif eps < eps_est and gap <= -material_gap:
        side = -1
    else:
        return None, "direction_or_gap_not_eligible"

    return (
        EventSetup(
            symbol=str(event["symbol"]),
            release_date=pd.Timestamp(event["release_date"]).normalize(),
            release_time=release_time,
            anchor_idx=anchor_idx,
            side=side,
            gap=gap,
            atr20=float(row["atr20"]),
            median_dollar_volume20=float(row["median_dollar_volume20"]),
        ),
        "eligible",
    )


def _reference_values(
    bars: pd.DataFrame, anchor_idx: int, end_idx: int, kind: ReferenceKind
) -> np.ndarray:
    segment = bars.iloc[anchor_idx : end_idx + 1]
    typical = segment["typical_price"].to_numpy(dtype=float)
    if kind == "unweighted":
        return np.cumsum(typical) / np.arange(1, len(typical) + 1)

    volume = segment["volume"].to_numpy(dtype=float)
    cumulative_volume = np.cumsum(volume)
    numerator = np.cumsum(typical * volume)
    with np.errstate(divide="ignore", invalid="ignore"):
        return numerator / cumulative_volume


def find_reaction_signal(
    bars: pd.DataFrame, setup: EventSetup, params: StudyParams, kind: ReferenceKind
) -> int | None:
    """Return the first frozen daily reaction to the chosen anchored reference."""
    end_idx = setup.anchor_idx + params.reaction_search_sessions
    references = _reference_values(bars, setup.anchor_idx, end_idx, kind)
    for offset in range(1, len(references)):
        idx = setup.anchor_idx + offset
        row = bars.iloc[idx]
        reference = references[offset]
        if not np.isfinite(reference):
            continue
        touches = row["low"] <= reference <= row["high"]
        if setup.side == 1:
            qualifies = touches and row["close"] > reference and row["close"] > row["open"]
        else:
            qualifies = touches and row["close"] < reference and row["close"] < row["open"]
        if qualifies:
            return idx
    return None


def _has_corporate_action(bars: pd.DataFrame, start_idx: int, end_idx: int) -> bool:
    coefficients = bars.iloc[start_idx : end_idx + 1]["split_coefficient"].to_numpy(dtype=float)
    return bool((~np.isfinite(coefficients) | ~np.isclose(coefficients, 1.0)).any())


def _net_bps(gross_bps: float, params: StudyParams) -> tuple[float, float]:
    return (
        gross_bps - 2.0 * params.friction_base_bps_per_side,
        gross_bps - 2.0 * params.friction_stress_bps_per_side,
    )


def _trade_record(
    *,
    strategy: str,
    setup: EventSetup,
    bars: pd.DataFrame,
    signal_idx: int | None,
    entry_idx: int,
    exit_idx: int,
    entry: float,
    exit_price: float,
    exit_reason: str,
    stop: float | None,
    target: float | None,
    params: StudyParams,
) -> dict:
    gross_bps = setup.side * (exit_price / entry - 1.0) * 10_000.0
    net_base_bps, net_stress_bps = _net_bps(gross_bps, params)
    return {
        "strategy": strategy,
        "event_id": f"{setup.symbol}|{setup.release_date.date().isoformat()}|{setup.release_time}",
        "symbol": setup.symbol,
        "event_date": setup.release_date,
        "release_time": setup.release_time,
        "anchor_date": bars.iloc[setup.anchor_idx]["date"],
        "signal_date": bars.iloc[signal_idx]["date"] if signal_idx is not None else pd.NaT,
        "entry_date": bars.iloc[entry_idx]["date"],
        "exit_date": bars.iloc[exit_idx]["date"],
        "side": "long" if setup.side == 1 else "short",
        "entry": entry,
        "stop": stop,
        "target": target,
        "exit": exit_price,
        "exit_reason": exit_reason,
        "gross_bps": gross_bps,
        "net_base_bps": net_base_bps,
        "net_stress_bps": net_stress_bps,
        "risk_bps": (abs(entry - stop) / entry * 10_000.0) if stop is not None else np.nan,
        "gap_bps": setup.gap * 10_000.0,
        "atr20": setup.atr20,
        "median_dollar_volume20": setup.median_dollar_volume20,
    }


def simulate_reaction_trade(
    bars: pd.DataFrame, setup: EventSetup, params: StudyParams, kind: ReferenceKind
) -> tuple[dict | None, str]:
    """Simulate the specified anchored-reference reaction with conservative exits."""
    signal_idx = find_reaction_signal(bars, setup, params, kind)
    if signal_idx is None:
        return None, "no_reaction_signal"

    entry_idx = signal_idx + 1
    exit_limit_idx = entry_idx + params.max_holding_sessions - 1
    if exit_limit_idx >= len(bars):
        return None, "incomplete_holding_window"
    if _has_corporate_action(bars, setup.anchor_idx, exit_limit_idx):
        return None, "corporate_action_in_window"

    signal = bars.iloc[signal_idx]
    entry = float(bars.iloc[entry_idx]["open"])
    stop = float(signal["low"] if setup.side == 1 else signal["high"])
    risk = (entry - stop) if setup.side == 1 else (stop - entry)
    if not np.isfinite(risk) or risk <= 0:
        return None, "nonpositive_initial_risk"
    target = entry + risk if setup.side == 1 else entry - risk

    exit_idx = exit_limit_idx
    exit_price = float(bars.iloc[exit_limit_idx]["close"])
    exit_reason = "time"
    for idx in range(entry_idx, exit_limit_idx + 1):
        row = bars.iloc[idx]
        open_price = float(row["open"])
        high = float(row["high"])
        low = float(row["low"])
        if setup.side == 1:
            if open_price <= stop:
                exit_idx, exit_price, exit_reason = idx, open_price, "gap_stop"
                break
            if open_price >= target:
                exit_idx, exit_price, exit_reason = idx, open_price, "gap_target"
                break
            # If both levels lie in a daily bar, adverse stop-first ordering is frozen.
            if low <= stop:
                exit_idx, exit_price, exit_reason = idx, stop, "stop"
                break
            if high >= target:
                exit_idx, exit_price, exit_reason = idx, target, "target"
                break
        else:
            if open_price >= stop:
                exit_idx, exit_price, exit_reason = idx, open_price, "gap_stop"
                break
            if open_price <= target:
                exit_idx, exit_price, exit_reason = idx, open_price, "gap_target"
                break
            if high >= stop:
                exit_idx, exit_price, exit_reason = idx, stop, "stop"
                break
            if low <= target:
                exit_idx, exit_price, exit_reason = idx, target, "target"
                break

    return (
        _trade_record(
            strategy=kind,
            setup=setup,
            bars=bars,
            signal_idx=signal_idx,
            entry_idx=entry_idx,
            exit_idx=exit_idx,
            entry=entry,
            exit_price=exit_price,
            exit_reason=exit_reason,
            stop=stop,
            target=target,
            params=params,
        ),
        "trade",
    )


def simulate_gap_hold_baseline(
    bars: pd.DataFrame, setup: EventSetup, params: StudyParams
) -> tuple[dict | None, str]:
    """Hold the same earnings-gap direction without an anchored-reference rule."""
    entry_idx = setup.anchor_idx + 1
    exit_idx = entry_idx + params.max_holding_sessions - 1
    if exit_idx >= len(bars):
        return None, "incomplete_holding_window"
    if _has_corporate_action(bars, setup.anchor_idx, exit_idx):
        return None, "corporate_action_in_window"

    entry = float(bars.iloc[entry_idx]["open"])
    exit_price = float(bars.iloc[exit_idx]["close"])
    return (
        _trade_record(
            strategy="gap_hold",
            setup=setup,
            bars=bars,
            signal_idx=None,
            entry_idx=entry_idx,
            exit_idx=exit_idx,
            entry=entry,
            exit_price=exit_price,
            exit_reason="time",
            stop=None,
            target=None,
            params=params,
        ),
        "trade",
    )


def _event_log_row(event: pd.Series, strategy: str, reason: str) -> dict:
    return {
        "strategy": strategy,
        "symbol": str(event["symbol"]),
        "event_date": pd.Timestamp(event["release_date"]).normalize(),
        "release_time": str(event["release_time"]),
        "reason": reason,
    }


def run_strategy(
    events: pd.DataFrame,
    bars_by_symbol: dict[str, pd.DataFrame],
    params: StudyParams,
    strategy: Literal["avwap", "unweighted", "gap_hold"],
    anchor_mode: AnchorMode = "label",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run one frozen construction and return trades plus every event disposition."""
    if strategy not in {"avwap", "unweighted", "gap_hold"}:
        raise ValueError(f"unknown strategy: {strategy}")
    trades: list[dict] = []
    audit: list[dict] = []

    ordered = events.sort_values(["symbol", "release_date", "release_time"]).reset_index(drop=True)
    for symbol, symbol_events in ordered.groupby("symbol", sort=False):
        bars = bars_by_symbol.get(str(symbol))
        if bars is None:
            for _, event in symbol_events.iterrows():
                audit.append(_event_log_row(event, strategy, "missing_symbol_bars"))
            continue

        last_exit_date: pd.Timestamp | None = None
        for _, event in symbol_events.iterrows():
            setup, reason = build_event_setup(event, bars, params, anchor_mode)
            if setup is None:
                audit.append(_event_log_row(event, strategy, reason))
                continue
            if strategy == "gap_hold":
                trade, reason = simulate_gap_hold_baseline(bars, setup, params)
            else:
                trade, reason = simulate_reaction_trade(bars, setup, params, strategy)
            if trade is None:
                audit.append(_event_log_row(event, strategy, reason))
                continue

            entry_date = pd.Timestamp(trade["entry_date"])
            if last_exit_date is not None and entry_date <= last_exit_date:
                audit.append(_event_log_row(event, strategy, "symbol_position_overlap"))
                continue
            last_exit_date = pd.Timestamp(trade["exit_date"])
            trades.append(trade)
            audit.append(_event_log_row(event, strategy, "trade"))

    trade_columns = [
        "strategy", "event_id", "symbol", "event_date", "release_time", "anchor_date", "signal_date",
        "entry_date", "exit_date", "side", "entry", "stop", "target", "exit", "exit_reason",
        "gross_bps", "net_base_bps", "net_stress_bps", "risk_bps", "gap_bps", "atr20",
        "median_dollar_volume20",
    ]
    return pd.DataFrame(trades, columns=trade_columns), pd.DataFrame(audit)


def profit_factor(pnl_bps: pd.Series) -> float:
    """Return positive P/L divided by absolute negative P/L."""
    pnl = pnl_bps.dropna()
    wins = float(pnl[pnl > 0].sum())
    losses = float(abs(pnl[pnl <= 0].sum()))
    if losses == 0:
        return float("inf") if wins > 0 else 0.0
    return wins / losses


def clustered_bootstrap_p5(
    trades: pd.DataFrame, value_column: str, params: StudyParams, seed_offset: int = 0
) -> float:
    """5th percentile of an event-date cluster bootstrap mean, in basis points."""
    if trades.empty:
        return float("nan")
    grouped = trades.groupby("event_date", sort=False)[value_column].agg(["sum", "count"])
    sums = grouped["sum"].to_numpy(dtype=float)
    counts = grouped["count"].to_numpy(dtype=float)
    if not len(sums) or counts.sum() <= 0:
        return float("nan")
    rng = np.random.default_rng(params.bootstrap_seed + seed_offset)
    choices = rng.integers(0, len(sums), size=(params.bootstrap_simulations, len(sums)))
    sampled_sums = sums[choices].sum(axis=1)
    sampled_counts = counts[choices].sum(axis=1)
    means = sampled_sums / sampled_counts
    return float(np.percentile(means, 5))


def paired_control_comparison(
    primary: pd.DataFrame,
    control: pd.DataFrame,
    value_column: str,
    params: StudyParams,
    seed_offset: int = 100,
) -> dict:
    """Compare one construction against a control on exactly matched events.

    A positive AVWAP result cannot be attributed to volume weighting if one
    construction happened to trade a better collection of events. This function
    therefore forms a paired event intersection before calculating the mean and
    event-date clustered bootstrap lower bound.
    """
    empty = {"matched_trades": 0, "mean_difference_bps": None, "bootstrap_p5_bps": None}
    if primary.empty or control.empty:
        return empty

    keys = ["event_id", "event_date", "side"]
    left = primary[keys + [value_column]].rename(columns={value_column: "primary"})
    right = control[keys + [value_column]].rename(columns={value_column: "control"})
    paired = left.merge(right, on=keys, how="inner", validate="one_to_one")
    if paired.empty:
        return empty
    paired["difference"] = paired["primary"] - paired["control"]

    grouped = paired.groupby("event_date", sort=False)["difference"].agg(["sum", "count"])
    sums = grouped["sum"].to_numpy(dtype=float)
    counts = grouped["count"].to_numpy(dtype=float)
    rng = np.random.default_rng(params.bootstrap_seed + seed_offset)
    choices = rng.integers(0, len(sums), size=(params.bootstrap_simulations, len(sums)))
    means = sums[choices].sum(axis=1) / counts[choices].sum(axis=1)
    return {
        "matched_trades": int(len(paired)),
        "mean_difference_bps": float(paired["difference"].mean()),
        "bootstrap_p5_bps": float(np.percentile(means, 5)),
    }


def audit_reason_counts(audit: pd.DataFrame) -> dict[str, int]:
    """Stable JSON-ready event disposition counts."""
    if audit.empty:
        return {}
    return dict(sorted(Counter(audit["reason"].astype(str)).items()))
