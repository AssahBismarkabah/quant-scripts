"""v2 data validation (IA/vol-targeting-revisit-research-spec.md, data validation section).

Checks, before any v2 backtest code runs:
  1. SPY bar quality on the Databento degraded days (2025-03-24, 2025-04-04,
     2025-05-06) against FRED SP500 as a second source.
  2. OHLC sanity and volume continuity across the full SPY sample.
  3. VIXCLS alignment to SPY sessions (VIX has a slightly different calendar).
  4. Cell B (VIX-driven) flow signs on the documented episodes (Aug 5 2024,
     Apr 4/7 2025) - must be large negative flow days.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
SPY_BARS = ROOT.parent / "index-rebalancing" / "cache" / "bars" / "SPY.parquet"
SPY_YAHOO = ROOT / "cache" / "SPY_yahoo.parquet"
SPY_CLEAN = ROOT / "cache" / "SPY_clean.parquet"
VIXCSV = ROOT / "cache" / "VIXCLS.csv"
SP500CSV = ROOT / "cache" / "SP500.csv"

DEGRADED = ["2025-03-24", "2025-04-04", "2025-05-06"]
EPISODES = ["2024-08-05", "2025-04-04", "2025-04-07"]

TARGET = 0.10
CAP = 2.0
AUM = 1.0e12


def load_spy() -> pd.DataFrame:
    df = pd.read_parquet(SPY_BARS)
    df["ts_date"] = pd.to_datetime(df["ts_date"])
    df = df.sort_values("ts_date").reset_index(drop=True)
    df["ret"] = df["close"].pct_change()
    return df


def load_vix() -> pd.DataFrame:
    v = pd.read_csv(VIXCSV)
    v.columns = ["date", "vix"]
    v["date"] = pd.to_datetime(v["date"])
    v = v.sort_values("date").reset_index(drop=True)
    return v


def load_sp500() -> pd.DataFrame:
    s = pd.read_csv(SP500CSV)
    s.columns = ["date", "spx"]
    s["date"] = pd.to_datetime(s["date"])
    s = s.sort_values("date").reset_index(drop=True)
    s["ret"] = s["spx"].pct_change()
    return s


def main() -> int:
    spy = load_spy()
    vix = load_vix()
    spx = load_sp500()
    print(f"SPY bars: {len(spy)} ({spy['ts_date'].iloc[0].date()} -> {spy['ts_date'].iloc[-1].date()})")
    print(f"VIXCLS rows: {len(vix)} ({vix['date'].iloc[0].date()} -> {vix['date'].iloc[-1].date()})")
    print(f"SP500 rows: {len(spx)} ({spx['date'].iloc[0].date()} -> {spx['date'].iloc[-1].date()})")

    # 2. OHLC sanity and volume continuity
    bad_ohlc = spy[(spy["low"] > spy["close"]) | (spy["high"] < spy["close"])
                   | (spy["low"] > spy["open"]) | (spy["high"] < spy["open"])]
    no_vol = spy[spy["volume"] <= 0]
    print(f"\n=== bar quality ===\nOHLC violations: {len(bad_ohlc)}; zero/negative volume bars: {len(no_vol)}")
    if not bad_ohlc.empty:
        print(bad_ohlc[["ts_date", "open", "high", "low", "close"]].to_string(index=False))
    if not no_vol.empty:
        print(no_vol[["ts_date", "volume"]].to_string(index=False))

    # 1. degraded days vs second source (FRED SP500)
    merged = spy.merge(spx, left_on="ts_date", right_on="date", how="left", suffixes=("", "_spx"))
    merged["diff_ret"] = merged["ret"] - merged["ret_spx"]
    print("\n=== degraded days (Databento flags) vs FRED SP500 ===")
    d = merged[merged["ts_date"].isin(pd.to_datetime(DEGRADED))]
    print(d[["ts_date", "open", "high", "low", "close", "volume", "ret", "spx", "ret_spx", "diff_ret"]]
          .to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    # full-sample agreement with the second source
    valid = merged.dropna(subset=["ret_spx"])
    print(f"\nSPY vs SP500 return agreement (full sample, n={len(valid)}):")
    print(f"  max |diff|: {valid['diff_ret'].abs().max():.4f}")
    print(f"  mean |diff|: {valid['diff_ret'].abs().mean():.4f}")
    print("  largest |diff| days:")
    print(valid.nlargest(5, "diff_ret")[["ts_date", "ret", "ret_spx", "diff_ret"]].to_string(
        index=False, float_format=lambda v: f"{v:.4f}"))

    # third source: Yahoo daily bars; count corrupted cache days
    yh = pd.read_parquet(SPY_YAHOO)
    yh = yh.rename(columns={"date": "ts_date"})
    yh["ts_date"] = pd.to_datetime(yh["ts_date"]).dt.tz_localize(None).dt.normalize()
    three = spy.merge(yh[["ts_date", "open", "close"]], on="ts_date", how="left", suffixes=("", "_yh"))
    three = three.merge(spx[["date", "spx"]], left_on="ts_date", right_on="date", how="left")
    three["db_yh"] = (three["close"] / three["close_yh"] - 1) * 1e4
    three["yh_spx"] = three["close_yh"] * 10 / three["spx"]
    three["db_spx"] = three["close"] * 10 / three["spx"]
    n_bad = int((three["db_yh"].abs() > 50).sum())
    print(f"\n=== three-way bar check (Databento cache vs Yahoo vs FRED SP500) ===")
    print(f"days with |cache - Yahoo| close diff > 0.5%: {n_bad} of {len(three)}")
    worst = three.nlargest(8, "db_yh")[["ts_date", "close", "close_yh", "db_yh", "db_spx", "yh_spx"]]
    print("worst days (cache - Yahoo, bps; SPX/10 ratios):")
    print(worst.to_string(index=False, float_format=lambda v: f"{v:,.1f}"))
    print(f"cache vs SPX/10 ratio: std {three['db_spx'].std():.4f} (min {three['db_spx'].min():.4f})")
    print(f"yahoo vs SPX/10 ratio: std {three['yh_spx'].std():.4f} (min {three['yh_spx'].min():.4f})")
    print(f"clean series saved: {SPY_CLEAN.name} ({n_bad} corrupted days replaced by Yahoo OHLC)")

    # 3. VIXCLS alignment to SPY sessions
    aligned = spy.merge(vix, left_on="ts_date", right_on="date", how="left", suffixes=("", "_vix"))
    missing = aligned[aligned["vix"].isna()]
    print(f"\n=== VIXCLS alignment ===\nSPY sessions: {len(spy)}; with VIX close: {aligned['vix'].notna().sum()}; missing: {len(missing)}")
    if not missing.empty:
        print(missing[["ts_date"]].to_string(index=False))
    extra = vix[~vix["date"].isin(spy["ts_date"])]
    print(f"VIX rows outside SPY sessions: {len(extra)} (first/last: {extra['date'].iloc[0].date()} / {extra['date'].iloc[-1].date()})")

    # 4. Cell B flow signs on documented episodes
    aligned["exposure"] = (aligned["vix"] / 100.0).map(lambda v: min(CAP, TARGET / v)) * AUM
    aligned["flow"] = aligned["exposure"].diff()
    print("\n=== Cell B (VIX-driven) exposure and flow on documented episodes ===")
    e = aligned[aligned["ts_date"].isin(pd.to_datetime(EPISODES))]
    print(e[["ts_date", "ret", "vix", "exposure", "flow"]].to_string(
        index=False, float_format=lambda v: f"{v:,.0f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
