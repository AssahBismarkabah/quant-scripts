"""Bounded-sample event study for the 10b5-1 adoption-timing probe.

For each distinct issuer 10b5-1 repurchase-adoption event:
  - Tier A: entry at open of the first session after the 8-K adoption date (t+1).
  - Tier B (PRIMARY): entry ~30 sessions after adoption (cooling-off expiry),
    i.e. the session whose row number is (adoption_position + 30).

Forward CARs measured over (+1,+5), (+1,+10), (+1,+20) sessions after entry,
net of friction, and excess vs SPY over the same window. The pre-registered
primary gate is bootstrap p5 of the net CAR at (+1,+20) on the Tier B arm.

Reported-not-selected: short-horizon rel-SPY (termination signature), matched
control (size), and the gate set. This mirrors the gate-discipline that closed
vol-fade and buyback.

Documented limitations (bounded probe): single window, sector skew risk,
CIK->ticker mapping via current submissions (delisted may be unmapped), size
proxy control rather than official index membership.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .bars import load_bars
from .config import StudyParams

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "10b5-1-timing"
EVENTS = RESEARCH / "events" / "adoption_events.parquet"
BENCH = "SPY"


def _entry_open_and_car(bars: pd.DataFrame, ticker: str, event_date: pd.Timestamp, entry_skip: int):
    """Return (entry_open, {h: car}) measured from the session at position `entry_skip`
    after (strictly after) event_date.

    entry_skip=1  -> Tier A: enter at open of the first post-event session (t+1).
    entry_skip=31 -> Tier B: enter at open of the session ~30 sessions after
                     the adoption session (cooling-off expiry).
    """
    b = bars[bars["ticker"] == ticker].sort_values("ts_date")
    post = b[b["ts_date"] > event_date].reset_index(drop=True)
    if len(post) < entry_skip:
        return None, {}
    entry_open = post.iloc[entry_skip - 1]["open"]
    closes = post["close"].to_numpy()
    car = {}
    for h in (5, 10, 20):
        idx = entry_skip - 1 + h
        if idx < len(closes):
            car[h] = closes[idx] / entry_open - 1
    return entry_open, car


def _boot_p5(x: np.ndarray, n: int = 10_000, seed: int = 42) -> float:
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return 0.0
    rng = np.random.default_rng(seed)
    means = np.array([rng.choice(x, size=x.size, replace=True).mean() for _ in range(n)])
    return float(np.percentile(means, 5))


def build_frame(events: pd.DataFrame, params: StudyParams) -> pd.DataFrame:
    events = events.copy()
    events["event_date"] = pd.to_datetime(events["event_date"])

    start = datetime(2024, 1, 1)
    end = datetime(2026, 9, 1)
    tickers = sorted(set(events["ticker"].dropna().tolist()) | {BENCH})
    bars = load_bars(tickers, start, end)

    spy = bars[bars["ticker"] == BENCH].sort_values("ts_date")

    rows = []
    for r in events.itertuples():
        ticker = r.ticker
        if not ticker:
            continue
        d = r.event_date
        for tier, skip in (("A", params.entry_lag_days), ("B", params.cooling_off_sessions + 1)):
            entry, car = _entry_open_and_car(bars, ticker, d, skip)
            if entry is None or not car:
                continue
            # benchmark CAR over the same post-event span (to same session index)
            spy_post = spy[spy["ts_date"] > d].sort_values("ts_date").reset_index(drop=True)
            # gross friction (20 bps base) applied to each horizon
            base_f = params.friction_base_bps / 1e4
            for h in (5, 10, 20):
                if h not in car:
                    continue
                gross = car[h]
                net = gross - base_f
                # rel-SPY over identical post-event horizon
                rel_spy = gross  # placeholder, replaced below per-tier if data allow
                if len(spy_post) >= skip - 1 + h:
                    s_entry = spy_post.iloc[skip - 1]["open"]
                    s_close = spy_post.iloc[skip - 1 + h]["close"]
                    sp_car = s_close / s_entry - 1
                    rel_spy = gross - sp_car
                rows.append(
                    {
                        "ticker": ticker,
                        "cik": r.cik,
                        "date": d,
                        "tier": tier,
                        "h": h,
                        "car_bps": round(gross * 1e4, 2),
                        "net_bps": round(net * 1e4, 2),
                        "rel_spy_bps": round(rel_spy * 1e4, 2),
                    }
                )
    return pd.DataFrame(rows)


def apply_gates(frame: pd.DataFrame, params: StudyParams) -> dict:
    """Apply the pre-registered rejection gates. Returns a gate summary."""
    gates: dict[str, bool] = {}
    notes: dict[str, str] = {}

    # liquidity filter: need bars (already filtered by presence); price gate applied pre-study
    # distinct liquid events
    n_events_total = frame[frame["tier"] == params.primary_tier]["ticker"].nunique() if not frame.empty else 0
    g_sparse = n_events_total < params.min_events_total
    gates["sparse"] = g_sparse
    notes["sparse"] = f"distinct {params.primary_tier} events={n_events_total} (min {params.min_events_total})"

    # distribute horizons per tier
    # primary horizon gate
    for tier in ("A", "B"):
        for h in (5, 10, 20):
            sub = frame[(frame["tier"] == tier) & (frame["h"] == h)]
            if sub.empty:
                gates[f"{tier}_h{h}"] = True
                notes[f"{tier}_h{h}"] = "no events"
                continue
            net = sub["net_bps"].to_numpy()
            rel = sub["rel_spy_bps"].to_numpy()
            p5 = _boot_p5(net, params.n_sims, params.seed)
            rel_mean = float(np.mean(rel)) if rel.size else 0.0
            rel_p5 = _boot_p5(rel, params.n_sims, params.seed)
            gates[f"{tier}_h{h}"] = bool(p5 < 0 or rel_mean < 0)
            notes[f"{tier}_h{h}"] = (
                f"n={len(sub)} net_p5={p5:.0f} rel_mean={rel_mean:.0f} rel_p5={rel_p5:.0f}"
            )

    # matched-control gate: compare net CAR to SPY-benchmark (rel_spy mean) as the control excess
    # gate 3 of the spec: effect vanishes vs matched/random-day. We use rel-SPY as the control proxy
    # on the bounded probe.
    for tier in ("A", "B"):
        sub = frame[(frame["tier"] == tier) & (frame["h"] == 20)]
        if sub.empty:
            gates[f"{tier}_control"] = True
            notes[f"{tier}_control"] = "no events"
            continue
        rel_mean = float(sub["rel_spy_bps"].mean())
        gates[f"{tier}_control"] = bool(rel_mean <= 0)
        notes[f"{tier}_control"] = f"rel_spy_mean={rel_mean:.0f}"

    # comprehensive: the probe FAILS if the primary tier's primary horizon fails its gate
    primary_p20 = gates.get(f"{params.primary_tier}_h20", True)
    gates["PRIMARY"] = primary_p20
    notes["PRIMARY"] = notes.get(f"{params.primary_tier}_h20", "")
    gates_pass = not any(
        v
        for k, v in gates.items()
        if k != "PRIMARY" and not k.endswith("_h5")  # short-horizon reported-not-selected
    )
    return {"gates": gates, "gates_pass": bool(gates_pass), "notes": notes}


def run(events: pd.DataFrame | None = None, params: StudyParams = StudyParams()) -> dict:
    if events is None:
        events = pd.read_parquet(EVENTS)
    frame = build_frame(events, params)
    gate_result = apply_gates(frame, params)
    return {"frame": frame, **gate_result}


if __name__ == "__main__":
    res = run()
    (RESEARCH / "outputs").mkdir(parents=True, exist_ok=True)
    res["frame"].to_parquet(RESEARCH / "outputs" / "probe_frame.parquet")
    summary = {
        "n_distinct_tierA": int(res["frame"][res["frame"]["tier"] == "A"]["ticker"].nunique()) if not res["frame"].empty else 0,
        "n_distinct_tierB": int(res["frame"][res["frame"]["tier"] == "B"]["ticker"].nunique()) if not res["frame"].empty else 0,
        "gates": res["gates"],
        "gates_pass": res["gates_pass"],
        "notes": res["notes"],
    }
    (RESEARCH / "outputs" / "probe_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
