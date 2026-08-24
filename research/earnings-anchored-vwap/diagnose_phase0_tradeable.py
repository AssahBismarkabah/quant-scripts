"""Diagnostic: intersect the fixed 100-row timing sample with frozen screens.

The Phase 0 timing audit failed on free data because 36 of 100 fixed rows have
no historical record in the free Yahoo earnings archive. This script answers a
bounded question without weakening any frozen gate:

    Of the 100 sampled rows, how many would actually survive the frozen
    tradeability screens (min price, median dollar volume, integrity window)?

It does not replace or relax the release-timing gate; it only reports the
overlap between 'verification status' and 'tradeable per frozen screens'.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from quant_scripts.earnings_anchored_vwap.backtest import (
    event_integrity_reason,
    prepare_symbol_bars,
    resolve_anchor_index,
)
from quant_scripts.earnings_anchored_vwap.config import StudyParams

OUT = ROOT / "research" / "earnings-anchored-vwap" / "outputs"
TEMPLATE = OUT / "timing_audit_template.csv"
YAHOO = OUT / "timing_crosscheck_yahoo.json"
EARNINGS = ROOT / "research" / "pead" / "cache" / "earnings_latest.csv"
PRICES = ROOT / "research" / "pead" / "cache" / "stock_prices_latest.csv"


def main() -> None:
    params = StudyParams()
    template = pd.read_csv(TEMPLATE, dtype=str).fillna("")
    yahoo = json.loads(YAHOO.read_text(encoding="utf-8"))

    status_by_sample: dict[int, str] = {}
    for row in yahoo["missing_ticker_rows"]:
        status_by_sample[int(row["sample_id"])] = "missing_ticker"
    for row in yahoo["missing_date_rows"]:
        status_by_sample[int(row["sample_id"])] = "missing_date"
    for row in yahoo["mismatch_rows"]:
        status_by_sample[int(row["sample_id"])] = "mismatch"
    matched = {
        int(row["sample_id"])
        for row in yahoo["missing_ticker_rows"]
        + yahoo["missing_date_rows"]
        + yahoo["mismatch_rows"]
    }
    for sample_id in range(1, 101):
        if sample_id not in status_by_sample:
            status_by_sample[sample_id] = "match"
    assert len(status_by_sample) == 100, f"classified {len(status_by_sample)} rows, expected 100"

    template["sample_id"] = pd.to_numeric(template["sample_id"])
    template["verify_status"] = template["sample_id"].map(status_by_sample)

    events = pd.read_csv(EARNINGS, usecols=["symbol", "date", "eps_est", "eps", "release_time"])
    events["release_date"] = pd.to_datetime(events.pop("date")).dt.normalize()
    events["eps"] = pd.to_numeric(events["eps"], errors="coerce")
    events["eps_est"] = pd.to_numeric(events["eps_est"], errors="coerce")
    events["release_time"] = events["release_time"].astype(str).str.strip().str.lower()
    events = events[
        events["eps"].notna()
        & events["eps_est"].notna()
        & events["release_time"].isin(["pre", "post"])
    ].copy()
    events = events.drop_duplicates(["symbol", "release_date", "release_time"], keep="last")
    events = events.set_index(["symbol", "release_date", "release_time"])

    symbols = set(template["symbol"].str.upper())
    columns = ["symbol", "date", "open", "high", "low", "close", "volume", "split_coefficient"]
    frames: list[pd.DataFrame] = []
    for chunk in pd.read_csv(PRICES, usecols=columns, chunksize=1_500_000):
        chunk = chunk[
            chunk["symbol"].isin(symbols)
            & (chunk["date"] >= params.warmup_start)
            & (chunk["date"] <= "2021-07-31")
        ]
        if not chunk.empty:
            frames.append(chunk)
    if not frames:
        raise SystemExit("no raw daily bars matched the sampled universe")
    prices = pd.concat(frames, ignore_index=True)
    prices["date"] = pd.to_datetime(prices["date"])
    bars_by_symbol = {
        symbol: prepare_symbol_bars(group, params)
        for symbol, group in prices.groupby("symbol", sort=False)
    }

    tradeable_reasons: Counter = Counter()
    rows: list[dict] = []
    for record in template.to_dict("records"):
        symbol = str(record["symbol"]).upper()
        release_date = pd.Timestamp(record["release_date"]).normalize()
        release_time = str(record["release_time"]).strip().lower()

        event_row = events.loc[(symbol, release_date, release_time)]
        key = (str(event_row["eps"]), str(event_row["eps_est"]))

        bars = bars_by_symbol.get(symbol)
        if bars is None:
            tradeable = False
            reason = "missing_symbol_bars"
        else:
            anchor_idx = resolve_anchor_index(bars, release_date, release_time)
            if anchor_idx is None:
                tradeable = False
                reason = "no_anchor_session"
            else:
                integrity = event_integrity_reason(bars, anchor_idx, params)
                if integrity is not None:
                    tradeable = False
                    reason = f"integrity:{integrity}"
                else:
                    prev = bars.iloc[anchor_idx - 1]
                    price_ok = bool(prev["close"] >= params.min_price)
                    dollar_vol = prev["median_dollar_volume20"]
                    dollar_ok = bool(pd.notna(dollar_vol) and dollar_vol >= params.min_median_dollar_volume)
                    if price_ok and dollar_ok:
                        tradeable = True
                        reason = "tradeable"
                    else:
                        tradeable = False
                        flags = []
                        if not price_ok:
                            flags.append("price_below_min")
                        if not dollar_ok:
                            flags.append("dollar_vol_below_min")
                        reason = "screen:" + "+".join(flags)

        rows.append(
            {
                "sample_id": int(record["sample_id"]),
                "symbol": symbol,
                "release_date": release_date.date().isoformat(),
                "release_time": release_time,
                "verify_status": status_by_sample[int(record["sample_id"])],
                "tradeable": tradeable,
                "screen_reason": reason,
                "eps_actual_est": key,
            }
        )
        tradeable_reasons[reason] += 1

    result = pd.DataFrame(rows)
    out_csv = OUT / "phase0_tradeable_intersection.csv"
    result.to_csv(out_csv, index=False)

    print(f"rows written: {len(result)} to {out_csv.relative_to(ROOT)}")
    print("\nverify_status x tradeable cross-tab (frozen screens):")
    print(pd.crosstab(result["verify_status"], result["tradeable"]).to_string())

    print("\nscreen reasons among the 36 unverifiable rows (missing_ticker + missing_date):")
    unverifiable = result[result["verify_status"].isin(["missing_ticker", "missing_date"])]
    print(unverifiable.groupby("screen_reason").size().sort_values(ascending=False).to_string())

    tradeable_all = result[result["tradeable"]]
    tradeable_unverifiable = unverifiable[unverifiable["tradeable"]]
    print(
        f"\ntradeable rows after all frozen screens: {len(tradeable_all)} / {len(result)} "
        f"({len(tradeable_unverifiable)} of them unverifiable on free data)"
    )

    matched_stratum = result[result["verify_status"] == "match"]
    matched_tradeable = result[(result["verify_status"] == "match") & result["tradeable"]]
    print(
        f"rows positively verified on free data AND tradeable: "
        f"{len(matched_tradeable)} (of {len(matched_stratum)} verified, of {len(result)} sampled)"
    )


if __name__ == "__main__":
    main()
