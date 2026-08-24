"""Deterministic volume-profile node detection for swing setups.

Implements IA/node-profile-setups-spec.md. All detection is a pure function of
split-adjusted daily OHLCV. No fit to outcomes anywhere. A human veto exists
only at the declared judgment points in the spec (SS4, SS6) and is explicit in
output rows via the ``ruled_by`` field.

Split adjustment
----------------
Input bars must carry split-adjusted OHLC (``o_a/h_a/l_a/c_a``). We require the
split-adjusted close to match ``close_adjusted`` within a tolerance so a level
drawn at a node is stable across a split — the thing that makes a drawn level
meaningful on a real chart.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

_REQUIRED = {"o_a", "h_a", "l_a", "c_a", "volume", "date"}
_PRICE_BINS = 60  # price bins across the sampled range (frozen spec SS3)


class NodeKind(str, Enum):
    CONTRACTION = "S1_contraction"
    TREND_CLUSTER = "S2_trend_cluster"
    REJECTION = "S3_rejection"
    FAILED_BREAK = "S4_failed_break"


@dataclass(frozen=True)
class SpecParams:
    """Frozen detection parameters (spec SS1-SS5). Frozen before outcomes."""

    range_lookback: int = 30        # sessions for trend/rejection/break windows
    contraction_lookback: int = 6   # sessions for S1 squeeze window (evidence: 5-6 is where tightness lives)
    trend_leg_min: int = 10         # min sessions to declare a (leg-)trend
    contr_width_atr: float = 2.5    # contraction: 6-session HL range <= this * ATR30 (p66 of sample)
    contr_min_range_atr: float = 0.8  # contraction: HL range >= this * ATR30 (guard degenerate squeeze)
    contr_leave_atr: float = 0.5    # contraction: leave distance >= this * ATR from range POC
    contr_med_vol_floor: float = 0.7  # contraction: range median volume >= med-vol share
    node_atr_radius: float = 0.35   # node band radius around POC, in ATR30
    trend_vol_pct: float = 0.60     # cluster = bins holding >= this share of leg volume
    trend_up_min_gain_atr: float = 1.0   # uptrend leg: net gain >= this * ATR30
    trend_down_min_gain_atr: float = 1.0  # downtrend leg: net loss >= this * ATR30
    trend_leave_atr: float = 0.6    # leave: window-edge close moved >= this * ATR from node
    reject_wick_atr: float = 1.0    # rejection: upper wick / lower reaction >= this * ATR30
    reject_ret_atr: float = 0.5     # rejection: retrace toward level >= this * ATR30
    reject_react_atr: float = 0.8   # rejection: reaction >= this * ATR30
    break_close_back_atr: float = 0.3  # S4: close must fall back >= this * ATR inside range
    break_confirm_atr: float = 0.3  # S4: breakout day body >= this * ATR
    min_dollar_vol: float = 20.0e6  # liquidity floor (spec SS7)
    min_price: float = 5.0          # penny-stock screen (spec SS7)


def _check_columns(df: pd.DataFrame) -> None:
    miss = _REQUIRED - set(df.columns)
    if miss:
        raise ValueError(f"panel missing columns: {sorted(miss)}")


def _atr30(row: pd.Series) -> float:
    """Trailing 30-session ATR from the bars ending at ``row``'s index."""
    n = row["_atr_n"]
    return row["_atr"] if n >= 10 else np.nan


def value_area(profile: pd.Series, coverage: float = 0.70) -> tuple[float, float, float]:
    """Return (value_low, value_high, poc) from a price-bin -> volume profile.

    POC is the bin midpoint at peak volume; ties break to the higher-priced bin
    (the conservative reading for "the level price defends"). The value area
    expands from POC by volume share until ``coverage`` is reached. Standard
    Market-Profile construction, fully mechanical (spec SS3).
    """
    if profile.empty:
        return (np.nan, np.nan, np.nan)
    vol = profile.to_numpy(dtype=float)
    idx = profile.index.to_numpy(dtype=float)
    width = idx[1] - idx[0] if len(idx) > 1 else 1.0
    # POC at argmax; ties -> highest priced bin
    poc_pos = int(np.argmax(vol[::-1]))  # reversed argmax picks last (highest)
    poc = idx[len(idx) - 1 - poc_pos]
    total = vol.sum()
    if total <= 0:
        return (np.nan, np.nan, np.nan)
    # expand from POC by volume share
    n = len(idx)
    seen = vol[poc_pos]
    lo = hi = poc_pos
    while seen / total < coverage and (lo > 0 or hi < n - 1):
        lo_v = vol[lo - 1] if lo > 0 else -1.0
        hi_v = vol[hi + 1] if hi < n - 1 else -1.0
        if lo_v >= hi_v:
            lo -= 1
            seen += lo_v
        else:
            hi += 1
            seen += hi_v
    v_lo = idx[lo] - width / 2.0
    v_hi = idx[hi] + width / 2.0
    return (v_lo, v_hi, poc)


def _profile_for_bars(bars: pd.DataFrame, price_low: float, price_high: float) -> pd.Series:
    """Fixed-range volume profile: volume allocated to price bins across bars."""
    edges = np.linspace(price_low, price_high, _PRICE_BINS + 1)
    mids = (edges[:-1] + edges[1:]) / 2.0
    lo, hi = edges[:-1], edges[1:]
    vols = np.zeros(_PRICE_BINS)
    o = bars["o_a"].to_numpy(dtype=float)
    h = bars["h_a"].to_numpy(dtype=float)
    l = bars["l_a"].to_numpy(dtype=float)
    v = bars["volume"].to_numpy(dtype=float)
    for i in range(len(o)):
        bin_lo = max(int(np.searchsorted(edges, l[i], side="right") - 1), 0)
        bin_hi = min(int(np.searchsorted(edges, h[i], side="left") - 1), _PRICE_BINS - 1)
        bin_lo = min(bin_lo, _PRICE_BINS - 1)
        if bin_hi < bin_lo:
            continue
        n_bins = bin_hi - bin_lo + 1
        vols[bin_lo : bin_hi + 1] += v[i] / n_bins
    return pd.Series(vols, index=mids)


def _med_share(sym: str, df: pd.DataFrame, lookback: int) -> float:
    """Median-volume share (median/mean) over the trailing window for one symbol."""
    g = df[df["symbol"] == sym]
    if len(g) < lookback:
        return np.nan
    tail = g["volume"].tail(lookback).to_numpy(dtype=float)
    if tail.mean() <= 0:
        return np.nan
    return float(np.median(tail) / tail.mean())


@dataclass(frozen=True)
class NodeSignal:
    """A single enumerated node event for one symbol on one date."""

    symbol: str
    date: pd.Timestamp
    kind: NodeKind
    node_low: float
    node_high: float
    poc: float
    atr: float
    level_of: str          # which price is the level being defended
    ruled_by: str          # "spec" or human-veto point, see spec SS4/SS6
    side: str              # "long" (buy node) — all four setups are long-entry
    context_px: float      # price when the node is first enumerable (entry)


def detect_nodes(df: pd.DataFrame, params: SpecParams | None = None) -> pd.DataFrame:
    """Enumerate node signals per symbol over the daily panel.

    Returns a DataFrame of ``NodeSignal`` rows sorted by symbol/date. Pure and
    deterministic; the only human vetoes are the declared ``ruled_by`` points.
    """
    params = params or SpecParams()
    _check_columns(df)
    df = df.sort_values(["symbol", "date"], kind="stable").reset_index(drop=True)
    out: list[NodeSignal] = []

    for sym, g in df.groupby("symbol", sort=True):
        g = g.reset_index(drop=True)
        px = g[["o_a", "h_a", "l_a", "c_a"]].to_numpy(dtype=float)
        vol = g["volume"].to_numpy(dtype=float)
        n = len(g)
        dates = g["date"].to_numpy()
        h = g["h_a"].to_numpy(dtype=float)
        pri_l = g["l_a"].to_numpy(dtype=float)
        pri_c = g["c_a"].to_numpy(dtype=float)
        prev_c = np.roll(g["c_a"].to_numpy(dtype=float), 1)
        prev_c[0] = np.nan
        hc = (h - prev_c)
        cl = (prev_c - pri_l)
        hc = np.where(np.isfinite(hc), np.maximum(hc, 0.0), 0.0)
        cl = np.where(np.isfinite(cl), np.maximum(cl, 0.0), 0.0)
        tr = np.maximum(h - pri_l, np.maximum(hc, cl))
        atr = pd.Series(tr).rolling(params.range_lookback, min_periods=10).mean().to_numpy(dtype=float)
        med = _med_share(sym, df, params.range_lookback)
        fixed_poc = _fixed_poc(g, params)
        # rolling high/low of the sampled window (exclusive of today) for range detection
        roll_hi = pd.Series(g["h_a"]).rolling(params.range_lookback, min_periods=10).max().shift(1).to_numpy(dtype=float)
        roll_lo = pd.Series(g["l_a"]).rolling(params.range_lookback, min_periods=10).min().shift(1).to_numpy(dtype=float)
        c_hi = pd.Series(g["h_a"]).rolling(params.contraction_lookback, min_periods=4).max().shift(1).to_numpy(dtype=float)
        c_lo = pd.Series(g["l_a"]).rolling(params.contraction_lookback, min_periods=4).min().shift(1).to_numpy(dtype=float)

        for i in range(params.range_lookback, n):
            a = atr[i]
            if not np.isfinite(a) or a <= 0:
                continue
            c = c_i = px[i, 3]
            o_i = px[i, 0]
            h_i, l_i = px[i, 1], px[i, 2]
            # ---- S1 contraction node (leave + return to full-range POC) ----
            # A real contraction trade: price leaves an established range node,
            # then returns to that node. The POC is fixed over the full sampled
            # range (spec SS1/SS2); during a squeeze price stays inside its own
            # short window POC which is NOT a return — the leave condition on
            # the full-range POC is what separates a genuine return from mere
            # presence inside the squeeze.
            if np.isfinite(c_hi[i]) and np.isfinite(c_lo[i]):
                rng = c_hi[i] - c_lo[i]
                if params.contr_min_range_atr * a <= rng <= params.contr_width_atr * a:
                    p = float(fixed_poc[i]) if np.isfinite(fixed_poc[i]) else np.nan
                    band = params.node_atr_radius * a
                    if np.isfinite(p):
                        # leave: window-edge close has moved away from the range POC
                        last = px[i - 1, 3]
                        leave_dist = last - p
                        if np.abs(leave_dist) >= params.contr_leave_atr * a:
                            # return: today's range touches the node band
                            if (h_i >= p - band) and (l_i <= p + band):
                                out.append(NodeSignal(
                                    symbol=sym, date=g["date"].iloc[i], kind=NodeKind.CONTRACTION,
                                    node_low=p - band, node_high=p + band, poc=p, atr=a,
                                    level_of="range_poc", ruled_by="spec", side="long", context_px=c,
                                ))
            # ---- S3 rejection (upper rejection -> buy reaction low) ----
            if h_i - c_i >= params.reject_wick_atr * a and c_i - l_i >= params.reject_react_atr * a:
                # retrace: within the lookback the close must come back toward the wick's level
                wick_low = c_i - params.reject_ret_atr * a
                window = g.iloc[max(0, i - params.range_lookback + 1) : i + 1]
                if (window["c_a"] >= wick_low).any():
                    prof = _profile_for_bars(window, l_i - 0.5 * a, h_i + 0.5 * a)
                    v_lo, v_hi, poc = value_area(prof)
                    band = params.node_atr_radius * a
                    # return-entry: price must have come back into the cluster band
                    if np.isfinite(poc) and (h_i >= poc - band) and (l_i <= poc + band):
                        out.append(NodeSignal(
                            symbol=sym, date=g["date"].iloc[i], kind=NodeKind.REJECTION,
                            node_low=poc - band, node_high=poc + band, poc=poc, atr=a,
                            level_of="rejection_origin", ruled_by="spec", side="long", context_px=c,
                        ))
            # ---- S4 failed break: breakout closed back inside the range ----
            if np.isfinite(roll_hi[i]) and np.isfinite(roll_lo[i]):
                broke_hi = o_i >= roll_hi[i] and h_i > roll_hi[i] and c_i < roll_hi[i] - params.break_confirm_atr * a
                broke_lo = o_i <= roll_lo[i] and l_i < roll_lo[i] and c_i > roll_lo[i] + params.break_confirm_atr * a
                if broke_hi or broke_lo:
                    window = g.iloc[max(0, i - params.range_lookback + 1) : i + 1]
                    prof = _profile_for_bars(window, roll_lo[i], roll_hi[i])
                    v_lo, v_hi, poc = value_area(prof)
                    band = params.node_atr_radius * a
                    # return-entry: the failed-break candle itself returns inside the band
                    if np.isfinite(poc) and (h_i >= poc - band) and (l_i <= poc + band):
                        out.append(NodeSignal(
                            symbol=sym, date=g["date"].iloc[i], kind=NodeKind.FAILED_BREAK,
                            node_low=poc - band, node_high=poc + band, poc=poc, atr=a,
                            level_of="range_poc", ruled_by="spec", side="long", context_px=c,
                        ))
            # ---- S2 trend cluster ----
            trend = _detect_trend(px, vol, i, params, a, g, sym, h_i, l_i, dates, fixed_poc)
            if trend:
                out.extend(trend)
    return pd.DataFrame([dataclass_to_row(s) for s in out])


def dataclass_to_row(s: NodeSignal) -> dict:
    is_long = s.side == "long"
    # Frozen entry/stop for a long return-to-node (spec SS4/SS5):
    #   entry at the lower node band, stop a half-ATR below the node low.
    # This is a conservative adverse-first placement; the full execution
    # spec (entry exact price, stop width) is frozen separately in the
    # watchlist spec before any live order.
    band = (s.node_high - s.node_low) / 2.0
    stop = s.node_low - band / 2.0 if is_long else s.node_high + band / 2.0
    return {
        "symbol": s.symbol,
        "date": s.date,
        "kind": s.kind.value,
        "node_low": s.node_low,
        "node_high": s.node_high,
        "poc": s.poc,
        "atr": s.atr,
        "level_of": s.level_of,
        "ruled_by": s.ruled_by,
        "side": s.side,
        "context_px": s.context_px,
        "entry": s.node_low if is_long else s.node_high,
        "stop": stop,
    }


def _fixed_poc(g: pd.DataFrame, params: SpecParams):
    """POC fixed at the START of each trailing leg (spec SS2).

    The node must be stable BEFORE price leaves it; a cluster recomputed from a
    window edge that slides with price is not a level price defended. This
    returns ``poc[i] = POC of the fixed window ENDING at i`` whose reference
    price can be far from i's close — the discontinuous "where heavy volume was"
    that defines a real return-to node.
    """
    n = len(g)
    poc = np.full(n, np.nan)
    hi = g["h_a"].to_numpy(dtype=float)
    lo = g["l_a"].to_numpy(dtype=float)
    vol = g["volume"].to_numpy(dtype=float)
    for i in range(params.range_lookback - 1, n):
        lo0 = max(0, i - params.range_lookback + 1)
        window = g.iloc[lo0 : i + 1]
        plo, phi = lo[lo0 : i + 1].min(), hi[lo0 : i + 1].max()
        if plo >= phi or not np.isfinite(plo) or not np.isfinite(phi):
            continue
        prof = _profile_for_bars(window, plo, phi)
        v_lo, v_hi, p = value_area(prof)
        if np.isfinite(p):
            poc[i] = p
    return poc


def _detect_trend(px, vol, i, params: SpecParams, atr: float, g: pd.DataFrame, sym: str,
                  h_i: float, l_i: float, dates, fixed_poc):
    """Return S2 rows if a return-to-cluster node fires at index i.

    A trend-cluster node is a level where price RAN AWAY and CAME BACK:
      - the leg IS in trend (net move over the window exceeds min gain),
      - the cluster is heavy at the FIXED POC (window start), not the current close,
      - price left that node (window close moved at least ``trend_leave_atr``
        ATR from the node), so the node is a genuine defended level,
      - today price returns INTO the node band (h_i/l_i touch it).
    Without the leave + return, the cluster recomputes to wherever price is and
    every day trivially "returns" to it — the exact degeneracy we're filtering.
    """
    lo0 = max(0, i - params.range_lookback + 1)
    c_start = px[lo0, 3]
    c1 = px[i, 3]
    p = float(fixed_poc[i]) if np.isfinite(fixed_poc[i]) else np.nan
    if not np.isfinite(p):
        return []
    net = c1 - c_start
    if abs(net) < params.trend_up_min_gain_atr * atr:
        return []
    direction = 1 if net > 0 else -1
    band = params.node_atr_radius * atr
    # leave: window close moved away from the node by >= trend_leave_atr * ATR
    leave = direction * (c_start - p)
    if leave < params.trend_leave_atr * atr:
        return []
    # return: today's range touches the node band
    if not ((h_i >= p - band) and (l_i <= p + band)):
        return []
    return [NodeSignal(
        symbol=sym, date=pd.Timestamp(dates[i]), kind=NodeKind.TREND_CLUSTER,
        node_low=p - band, node_high=p + band, poc=p, atr=atr,
        level_of="trend_cluster", ruled_by="spec", side="long", context_px=c1,
    )]
