"""Census: full-panel eligibility under the frozen screens and gates.

Loads every eligible earnings event in the owned panel, applies the frozen
pre-signal screens (price, liquidity, direction-gap agreement), and reports how
many would reach the OOS sample-size gate per side. It produces no trade or
P&L outcome: it only counts candidates, so it does not violate the frozen
'no outcome loaded' state.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from quant_scripts.earnings_anchored_vwap.backtest import (
    build_event_setup,
    filter_events_by_price_integrity,
    find_reaction_signal,
    prepare_symbol_bars,
)
from quant_scripts.earnings_anchored_vwap.config import StudyParams

EARNINGS = ROOT / "research" / "pead" / "cache" / "earnings_latest.csv"
PRICES = ROOT / "research" / "pead" / "cache" / "stock_prices_latest.csv"
OUT = ROOT / "research" / "earnings-anchored-vwap" / "outputs"


def main() -> None:
    params = StudyParams()
    events = pd.read_csv(EARNINGS, usecols=["symbol", "date", "eps_est", "eps", "release_time"])
    events["release_date"] = pd.to_datetime(events.pop("date")).dt.normalize()
    for column in ("eps", "eps_est"):
        events[column] = pd.to_numeric(events[column], errors="coerce")
    events["release_time"] = events["release_time"].astype(str).str.strip().str.lower()
    events = events[
        events["eps"].notna()
        & events["eps_est"].notna()
        & events["release_time"].isin(["pre", "post"])
    ].copy()
    events = events.drop_duplicates(["symbol", "release_date", "release_time"], keep="last")
    events = events[
        (events["release_date"] >= pd.Timestamp(params.warmup_start))
        & (events["release_date"] <= pd.Timestamp(params.oos_end))
    ].copy()

    columns = ["symbol", "date", "open", "high", "low", "close", "volume", "split_coefficient"]
    frames: list[pd.DataFrame] = []
    all_symbols = set(events["symbol"])
    for chunk in pd.read_csv(PRICES, usecols=columns, chunksize=1_500_000):
        chunk = chunk[
            chunk["symbol"].isin(all_symbols)
            & (chunk["date"] >= params.warmup_start)
            & (chunk["date"] <= "2021-07-31")
        ]
        if not chunk.empty:
            frames.append(chunk)
    prices = pd.concat(frames, ignore_index=True)
    prices["date"] = pd.to_datetime(prices["date"])
    bars_by_symbol = {
        symbol: prepare_symbol_bars(group, params)
        for symbol, group in prices.groupby("symbol", sort=False)
    }

    valid, _ = filter_events_by_price_integrity(events, bars_by_symbol, params)
    print(f"price-integrity gate: {len(valid):,} of {len(events):,} events retained ({len(valid) / len(events):.3f})")

    screen_counts: Counter = Counter()
    eligible_rows: list[dict] = []
    for _, event in valid.iterrows():
        bars = bars_by_symbol.get(str(event["symbol"]))
        setup, reason = build_event_setup(event, bars, params)
        screen_counts[reason] += 1
        if setup is None:
            continue
        side = "long" if setup.side == 1 else "short"
        if event["release_date"] <= pd.Timestamp(params.is_end):
            period = "IS"
        elif event["release_date"] >= pd.Timestamp(params.oos_start):
            period = "OOS"
        else:
            period = "other"
        eligible_rows.append(
            {
                "symbol": setup.symbol,
                "release_date": event["release_date"].date().isoformat(),
                "release_time": event["release_time"],
                "side": side,
                "period": period,
            }
        )

    print("frozen screen reasons (full panel):")
    for reason, count in screen_counts.most_common():
        print(f"  {reason}: {count:,}")

    eligible = pd.DataFrame(eligible_rows)
    print("\neligible candidates by side x period:")
    print(pd.crosstab(eligible["side"], eligible["period"]).to_string())

    oos_eligible = eligible[eligible["period"] == "OOS"]
    signal_counts: Counter = Counter()
    for _, row in oos_eligible.iterrows():
        event = valid[(valid["symbol"] == row["symbol"]) & (valid["release_date"] == pd.Timestamp(row["release_date"]))].iloc[0]
        bars = bars_by_symbol.get(row["symbol"])
        anchor_idx = None
        from quant_scripts.earnings_anchored_vwap.backtest import resolve_anchor_index
        anchor_idx = resolve_anchor_index(bars, event["release_date"], str(event["release_time"]).strip().lower())
        if anchor_idx is None:
            signal_counts["no_anchor"] += 1
            continue
        setup, _ = build_event_setup(event, bars, params)
        if setup is None:
            signal_counts["setup_none"] += 1
            continue
        signal_idx = find_reaction_signal(bars, setup, params, "avwap")
        signal_counts[(row["side"], "signal" if signal_idx is not None else "no_signal")] += 1

    print("\nOOS candidate -> AVWAP reaction-signal counts per side (no P&L):")
    for (side, outcome), count in sorted(signal_counts.items()):
        print(f"  {side} {outcome}: {count:,}")
    print(f"\nfrozen minimum OOS trades per side: {params.min_oos_trades_per_side:,}")

    out_csv = OUT / "eligible_census.csv"
    eligible.to_csv(out_csv, index=False)
    print(f"census written: {out_csv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
