"""Run the daily earnings-anchored VWAP falsification only after Phase 0.

The frozen design is in IA/earnings-anchored-vwap-research-gate.md. This script
creates a deterministic 100-event timing-audit template if needed, then refuses
to load outcomes until independently verified timing labels meet that gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from quant_scripts.earnings_anchored_vwap.backtest import (
    audit_reason_counts,
    clustered_bootstrap_p5,
    filter_events_by_price_integrity,
    paired_control_comparison,
    prepare_symbol_bars,
    profit_factor,
    run_strategy,
)
from quant_scripts.earnings_anchored_vwap.config import StudyParams

PEAD_CACHE = ROOT / "research" / "pead" / "cache"
OUT = ROOT / "research" / "earnings-anchored-vwap" / "outputs"
EARNINGS_PATH = PEAD_CACHE / "earnings_latest.csv"
PRICES_PATH = PEAD_CACHE / "stock_prices_latest.csv"
TEMPLATE_PATH = OUT / "timing_audit_template.csv"
AUDIT_PATH = OUT / "timing_audit.csv"
PHASE0_PATH = OUT / "phase0_summary.json"
SUMMARY_PATH = OUT / "probe_summary.json"
TRADES_PATH = OUT / "probe_trades.parquet"
EVENT_AUDIT_PATH = OUT / "event_audit.parquet"
PRICE_INTEGRITY_PATH = OUT / "price_integrity_audit.parquet"


def _load_events(params: StudyParams) -> tuple[pd.DataFrame, int]:
    events = pd.read_csv(EARNINGS_PATH, usecols=["symbol", "date", "eps_est", "eps", "release_time"])
    events["release_date"] = pd.to_datetime(events.pop("date")).dt.normalize()
    events["eps"] = pd.to_numeric(events["eps"], errors="coerce")
    events["eps_est"] = pd.to_numeric(events["eps_est"], errors="coerce")
    events["release_time"] = events["release_time"].astype(str).str.strip().str.lower()
    events = events[
        events["eps"].notna()
        & events["eps_est"].notna()
        & events["release_time"].isin(["pre", "post"])
        & (events["release_date"] >= pd.Timestamp(params.warmup_start))
        & (events["release_date"] <= pd.Timestamp(params.oos_end))
    ].copy()
    before_dedup = len(events)
    events = events.drop_duplicates(["symbol", "release_date", "release_time"], keep="last")
    return events.sort_values(["symbol", "release_date", "release_time"]).reset_index(drop=True), before_dedup - len(events)


def _timing_sample(events: pd.DataFrame, params: StudyParams) -> pd.DataFrame:
    """Build 5 reproducible rows for each year × pre/post stratum (20 × 5)."""
    sample_rows: list[pd.DataFrame] = []
    events = events.copy()
    events["year"] = events["release_date"].dt.year
    strata = sorted(events.groupby(["year", "release_time"], sort=True), key=lambda item: item[0])
    if len(strata) != 20 or params.timing_audit_size % len(strata) != 0:
        raise ValueError("timing sample must split evenly across available year/session strata")
    per_stratum = params.timing_audit_size // len(strata)
    for (year, release_time), group in strata:
        if len(group) < per_stratum:
            raise ValueError(f"insufficient events for timing stratum {year}/{release_time}")
        sample_rows.append(group.sample(per_stratum, random_state=params.bootstrap_seed + year + (1 if release_time == "post" else 0)))
    sample = pd.concat(sample_rows, ignore_index=True).sort_values(["release_date", "release_time", "symbol"])
    sample.insert(0, "sample_id", range(1, len(sample) + 1))
    return sample[["sample_id", "symbol", "release_date", "release_time"]].reset_index(drop=True)


def _write_timing_template(sample: pd.DataFrame) -> None:
    if TEMPLATE_PATH.exists():
        return
    template = sample.copy()
    template["verified_date"] = ""
    template["verified_release_time"] = ""
    template["source_url"] = ""
    template["source_type"] = ""
    template["status"] = "pending"
    template["notes"] = ""
    template.to_csv(TEMPLATE_PATH, index=False)


def _normalize_verified_time(value: object) -> str | None:
    normalized = str(value).strip().lower()
    mapping = {
        "pre": "pre",
        "premarket": "pre",
        "pre-market": "pre",
        "bmo": "pre",
        "before market open": "pre",
        "post": "post",
        "postmarket": "post",
        "post-market": "post",
        "amc": "post",
        "after market close": "post",
    }
    return mapping.get(normalized)


def evaluate_timing_audit(sample: pd.DataFrame, params: StudyParams) -> dict:
    """Evaluate independently verified date/session evidence against the template."""
    base = {
        "required_rows": params.timing_audit_size,
        "template_path": str(TEMPLATE_PATH.relative_to(ROOT)),
        "audit_path": str(AUDIT_PATH.relative_to(ROOT)),
        "minimum_agreement": params.timing_min_agreement,
    }
    if not AUDIT_PATH.exists():
        return {**base, "status": "PENDING", "audited_rows": 0, "agreement": None}

    audit = pd.read_csv(AUDIT_PATH, dtype=str).fillna("")
    required = {
        "sample_id", "symbol", "release_date", "release_time", "verified_date",
        "verified_release_time", "source_url", "status",
    }
    missing = sorted(required.difference(audit.columns))
    if missing:
        return {**base, "status": "INVALID", "reason": f"missing columns: {missing}"}

    audit["sample_id"] = pd.to_numeric(audit["sample_id"], errors="coerce")
    audit = audit.dropna(subset=["sample_id"]).copy()
    audit["sample_id"] = audit["sample_id"].astype(int)
    expected = sample.set_index("sample_id")
    supplied = audit.drop_duplicates("sample_id", keep="last").set_index("sample_id")
    checks: list[bool] = []
    verified_rows = 0
    for sample_id, expected_row in expected.iterrows():
        if sample_id not in supplied.index:
            continue
        row = supplied.loc[sample_id]
        if str(row["status"]).strip().lower() != "verified":
            continue
        verified_rows += 1
        try:
            same_identity = (
                str(row["symbol"]).strip().upper() == str(expected_row["symbol"]).strip().upper()
                and pd.Timestamp(row["release_date"]).normalize() == expected_row["release_date"]
                and str(row["release_time"]).strip().lower() == expected_row["release_time"]
            )
            same_date = pd.Timestamp(row["verified_date"]).normalize() == expected_row["release_date"]
        except (TypeError, ValueError):
            same_identity = False
            same_date = False
        verified_time = _normalize_verified_time(row["verified_release_time"])
        same_evidence = (
            same_date
            and verified_time == expected_row["release_time"]
            and bool(str(row["source_url"]).strip())
        )
        checks.append(bool(same_identity and same_evidence))

    agreement = float(np.mean(checks)) if checks else 0.0
    passed = verified_rows >= params.timing_audit_size and agreement >= params.timing_min_agreement
    return {
        **base,
        "status": "PASS" if passed else "FAIL",
        "audited_rows": verified_rows,
        "matching_rows": int(sum(checks)),
        "agreement": agreement,
    }


def _load_prices(symbols: set[str], params: StudyParams) -> pd.DataFrame:
    """Read only relevant raw OHLCV rows and only the frozen study span."""
    columns = ["symbol", "date", "open", "high", "low", "close", "volume", "split_coefficient"]
    frames: list[pd.DataFrame] = []
    for chunk in pd.read_csv(PRICES_PATH, usecols=columns, chunksize=1_500_000):
        chunk = chunk[
            chunk["symbol"].isin(symbols)
            & (chunk["date"] >= params.warmup_start)
            & (chunk["date"] <= "2021-07-31")
        ]
        if not chunk.empty:
            frames.append(chunk)
    if not frames:
        raise SystemExit("no raw daily bars matched the earnings universe")
    prices = pd.concat(frames, ignore_index=True)
    prices["date"] = pd.to_datetime(prices["date"])
    return prices


def _window(frame: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    return frame[(frame["event_date"] >= pd.Timestamp(start)) & (frame["event_date"] <= pd.Timestamp(end))].copy()


def _side_metrics(trades: pd.DataFrame, params: StudyParams) -> dict:
    if trades.empty:
        return {
            "trades": 0,
            "gross_mean_bps": None,
            "net_base_mean_bps": None,
            "net_stress_mean_bps": None,
            "net_base_pf": None,
            "net_base_bootstrap_p5_bps": None,
            "gap_stop_loss_fraction": None,
            "positive_complete_oos_years": [],
        }
    losses = trades[trades["net_base_bps"] <= 0]
    gap_stop_fraction = (
        float((losses["exit_reason"] == "gap_stop").mean()) if not losses.empty else 0.0
    )
    yearly = trades.assign(year=trades["event_date"].dt.year).groupby("year")["net_base_bps"].mean()
    return {
        "trades": int(len(trades)),
        "gross_mean_bps": float(trades["gross_bps"].mean()),
        "net_base_mean_bps": float(trades["net_base_bps"].mean()),
        "net_stress_mean_bps": float(trades["net_stress_bps"].mean()),
        "net_base_pf": float(profit_factor(trades["net_base_bps"])),
        "net_base_bootstrap_p5_bps": clustered_bootstrap_p5(trades, "net_base_bps", params),
        "gap_stop_loss_fraction": gap_stop_fraction,
        "positive_complete_oos_years": [
            int(year) for year in params.complete_oos_years if yearly.get(year, float("-inf")) > 0
        ],
    }


def _incremental_metrics(
    primary: pd.DataFrame, control: pd.DataFrame, params: StudyParams, seed_offset: int
) -> dict:
    return paired_control_comparison(primary, control, "net_base_bps", params, seed_offset=seed_offset)


def _side_gates(
    is_primary: pd.DataFrame,
    oos_primary: pd.DataFrame,
    oos_gap_hold: pd.DataFrame,
    oos_unweighted: pd.DataFrame,
    params: StudyParams,
) -> dict:
    oos = _side_metrics(oos_primary, params)
    is_metrics = _side_metrics(is_primary, params)
    gap_compare = _incremental_metrics(oos_primary, oos_gap_hold, params, 200)
    unweighted_compare = _incremental_metrics(oos_primary, oos_unweighted, params, 300)
    enough = oos["trades"] >= params.min_oos_trades_per_side
    gate1 = enough and oos["net_base_mean_bps"] > 0 and oos["net_stress_mean_bps"] > 0
    gate2 = enough and oos["net_base_bootstrap_p5_bps"] > 0
    gate3 = (
        enough
        and oos["net_base_pf"] >= 1.0
        and oos["gap_stop_loss_fraction"] <= params.max_gap_stop_loss_fraction
    )
    gate4 = enough and len(oos["positive_complete_oos_years"]) >= params.min_positive_complete_oos_years
    gate5 = all(
        value is not None and value > 0
        for value in (
            gap_compare["mean_difference_bps"],
            gap_compare["bootstrap_p5_bps"],
            unweighted_compare["mean_difference_bps"],
            unweighted_compare["bootstrap_p5_bps"],
        )
    ) and all(
        comparison["matched_trades"] >= params.min_oos_trades_per_side
        for comparison in (gap_compare, unweighted_compare)
    )
    gate6 = is_metrics["trades"] > 0 and is_metrics["gross_mean_bps"] > 0
    return {
        "is": is_metrics,
        "oos": oos,
        "incremental_vs_gap_hold": gap_compare,
        "incremental_vs_unweighted": unweighted_compare,
        "gates": {
            "gate1_oos_net_positive_base_and_stress": gate1,
            "gate2_oos_cluster_bootstrap_p5_positive": gate2,
            "gate3_oos_pf_and_gap_stop_limit": gate3,
            "gate4_oos_year_persistence": gate4,
            "gate5_incremental_value_over_controls": gate5,
            "gate6_is_gross_positive": gate6,
        },
    }


def _json_default(value: object):
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    raise TypeError(f"not JSON serializable: {type(value)!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase0", action="store_true", help="only generate/evaluate timing evidence")
    parser.add_argument(
        "--anchor-mode",
        default="label",
        choices=["label", "next_open"],
        help="session used to anchor the daily reconstruction; 'next_open' is the label-free fallback",
    )
    parser.add_argument(
        "--allow-free-outcomes",
        action="store_true",
        help=(
            "intentionally run the outcome study while Phase 0 is FAIL, using only the "
            "anchor mode selected; recorded for audit, not a silent gate lift"
        ),
    )
    args = parser.parse_args()

    params = StudyParams()
    anchor_mode = args.anchor_mode
    OUT.mkdir(parents=True, exist_ok=True)
    events, duplicates_dropped = _load_events(params)
    sample = _timing_sample(events, params)
    _write_timing_template(sample)
    timing = evaluate_timing_audit(sample, params)
    phase0 = {
        "status": "PASS" if timing["status"] == "PASS" else "PENDING_OR_FAILED",
        "event_source": str(EARNINGS_PATH.relative_to(ROOT)),
        "events_after_source_filters": int(len(events)),
        "symbols": int(events["symbol"].nunique()),
        "date_min": events["release_date"].min().date().isoformat(),
        "date_max": events["release_date"].max().date().isoformat(),
        "duplicate_events_dropped": int(duplicates_dropped),
        "timing_audit": timing,
    }
    PHASE0_PATH.write_text(json.dumps(phase0, indent=2, default=_json_default), encoding="utf-8")
    if args.phase0 or (timing["status"] != "PASS" and not args.allow_free_outcomes):
        print(json.dumps(phase0, indent=2, default=_json_default))
        if timing["status"] != "PASS" and not args.allow_free_outcomes:
            print(f"\nNo outcome data loaded. Complete {AUDIT_PATH.relative_to(ROOT)} from {TEMPLATE_PATH.relative_to(ROOT)}.")
        return 0

    if timing["status"] != "PASS" and args.allow_free_outcomes:
        print(
            "\nNOTE: running outcomes under a deliberately recorded free-data allowance "
            f"(anchor_mode={anchor_mode}). Phase 0 audit is FAIL; this is an explicit "
            "decision, not a gate pass. Results remain a bounded historical falsification.\n"
        )

    print("Phase 0 passed. Loading raw daily OHLCV...")
    prices = _load_prices(set(events["symbol"]), params)
    bars_by_symbol = {
        symbol: prepare_symbol_bars(group, params)
        for symbol, group in prices.groupby("symbol", sort=False)
    }
    print(f"Prepared {len(bars_by_symbol):,} symbol histories from {len(prices):,} bars.")

    valid_events, price_integrity_audit = filter_events_by_price_integrity(
        events, bars_by_symbol, params, anchor_mode
    )
    price_integrity_audit.to_parquet(PRICE_INTEGRITY_PATH, index=False)
    price_integrity = {
        "candidate_events": int(len(events)),
        "retained_events": int(len(valid_events)),
        "retained_fraction": float(len(valid_events) / len(events)) if len(events) else 0.0,
        "minimum_retained_fraction": 0.90,
        "reason_counts": audit_reason_counts(price_integrity_audit),
    }
    price_integrity["gate_passed"] = (
        price_integrity["retained_fraction"] >= price_integrity["minimum_retained_fraction"]
    )
    if not price_integrity["gate_passed"]:
        summary = {
            "status": "COMPLETED",
            "spec": "IA/earnings-anchored-vwap-research-gate.md",
            "phase0": phase0,
            "params": vars(params),
            "data_integrity": price_integrity,
            "verdict": "UNVERIFIABLE_DATA_INTEGRITY",
            "deployment": "NOT AUTHORIZED — the frozen daily data-integrity gate failed.",
        }
        SUMMARY_PATH.write_text(json.dumps(summary, indent=2, default=_json_default), encoding="utf-8")
        print(json.dumps(summary, indent=2, default=_json_default))
        return 0

    all_trades: list[pd.DataFrame] = []
    all_audits: list[pd.DataFrame] = []
    results: dict[str, pd.DataFrame] = {}
    for strategy in ("avwap", "unweighted", "gap_hold"):
        trades, audit = run_strategy(valid_events, bars_by_symbol, params, strategy, anchor_mode)
        results[strategy] = trades
        all_trades.append(trades)
        all_audits.append(audit)
        print(f"{strategy}: {len(trades):,} trades")

    combined_trades = pd.concat(all_trades, ignore_index=True)
    combined_audit = pd.concat(all_audits, ignore_index=True)
    combined_trades.to_parquet(TRADES_PATH, index=False)
    combined_audit.to_parquet(EVENT_AUDIT_PATH, index=False)

    side_results: dict[str, dict] = {}
    for side in ("long", "short"):
        avwap = results["avwap"]
        gap_hold = results["gap_hold"]
        unweighted = results["unweighted"]
        is_primary = _window(avwap[avwap["side"] == side], params.is_start, params.is_end)
        oos_primary = _window(avwap[avwap["side"] == side], params.oos_start, params.oos_end)
        oos_gap = _window(gap_hold[gap_hold["side"] == side], params.oos_start, params.oos_end)
        oos_unweighted = _window(unweighted[unweighted["side"] == side], params.oos_start, params.oos_end)
        side_results[side] = _side_gates(is_primary, oos_primary, oos_gap, oos_unweighted, params)

    all_gates = [
        price_integrity["gate_passed"],
        *(value for side in side_results.values() for value in side["gates"].values()),
    ]
    summary = {
        "status": "COMPLETED",
        "spec": "IA/earnings-anchored-vwap-research-gate.md",
        "phase0": phase0,
        "params": vars(params),
        "data_integrity": price_integrity,
        "trade_counts": {name: int(len(frame)) for name, frame in results.items()},
        "event_audit_reasons": {
            name: audit_reason_counts(combined_audit[combined_audit["strategy"] == name])
            for name in ("avwap", "unweighted", "gap_hold")
        },
        "sides": side_results,
        "verdict": "CLEARS-OOS" if all(all_gates) else "DISCONFIRMED",
        "deployment": "NOT AUTHORIZED — all data ends in 2021; a pass only earns a current-data stage.",
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
