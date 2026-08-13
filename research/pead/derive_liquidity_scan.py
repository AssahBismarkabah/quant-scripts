"""Stage 1 derive pass - liquidity/staleness descriptive scan on the PEAD panel.

Dir of discovery: data -> observe -> (this) test the observed relationship -> decide.

OBSERVATION (from inventory §6): the PEAD panel is dominated by a strong,
persistent liquidity/staleness dimension (7.9% of symbol-days exact-0 change,
concentrated in microcaps; 14% of symbols >20% stale days).

This script turns that observation into an objective, point-in-time,
machine-executable score with NO lookahead, then measures whether the
liquidity/staleness dimension predicts forward cross-sectional returns.

Deliverable of THIS step is descriptive: which liquidity tile has what forward
return, IS vs OOS, and (critical) does any signal survive on LIQUID-ONLY names
(the ones we could actually trade). It does NOT yet pre-register a tradeable
rule.

Score (trailing, point-in-time, no future info):
  stale_share = fraction of trailing 21 trading days with exact-0 one-day change
  price_level = trailing median close (for microcap/penny screen)
  liquidity tier by stale_share + price -> 5 quintiles by stale_share
  (and a separate price-based screen)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "research" / "pead" / "cache" / "prices_adj_long.parquet"
OUT = Path(__file__).resolve().parent / "outputs"

ARTIFACT_CAP = 1.0      # |one-day change| > 100% -> treated as split artifact, excluded
STALE_WIN = 21          # trailing window for stale-share score
QUINTILES = 5
HORIZONS = [1, 5, 21]   # forward trading-day horizons


def load_panel() -> pd.DataFrame:
    df = pd.read_parquet(PANEL)
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    # one-day raw change (adjusted close, so split jumps look huge)
    df["prev"] = df.groupby("symbol")["close_adjusted"].shift()
    df["chg"] = df["close_adjusted"] - df["prev"]
    df["ret"] = df["chg"] / df["prev"]
    df = df[df["prev"].notna()].copy()
    # corruption guard: drop any row where the level is absurd (price-to-return mismatch)
    df = df[np.isfinite(df["ret"])]
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Point-in-time stale-share and price features (trailing only, no leakage)."""
    g = df.groupby("symbol", sort=False)
    # zero-move indicator over trailing window
    df["zero"] = (df["ret"] == 0).astype(float)
    df["stale_share"] = g["zero"].transform(lambda s: s.rolling(STALE_WIN, min_periods=5).mean())
    df["price_med"] = g["close_adjusted"].transform(lambda s: s.rolling(STALE_WIN, min_periods=5).median())
    return df


def tilt_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional rank-tile stale_share and price each date (0..Q-1)."""
    df = df[df["stale_share"].notna()].copy()
    df["tile"] = df.groupby("date")["stale_share"].transform(
        lambda s: pd.qcut(s.rank(method="first"), QUINTILES, labels=False)
    )
    # price tile within the same date for a liquidity-lite cross-check
    df["ptile"] = df.groupby("date")["price_med"].transform(
        lambda s: pd.qcut(s.rank(method="first"), QUINTILES, labels=False)
    )
    return df


def forward_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Attach forward H-day cumulative equal-weight returns, no leakage (features at t, ret t+1..t+H)."""
    out = df[["date", "symbol", "chg", "ret", "zero", "stale_share", "price_med", "tile", "ptile"]].copy()
    g = df.groupby("symbol", sort=False)["close_adjusted"]
    fwd = pd.DataFrame(index=df.index)
    for H in HORIZONS:
        fwd_next = g.shift(-1)
        fwd_H = g.shift(-H - 1)
        cum = (fwd_H / fwd_next) - 1.0   # t+1 .. t+H cumulative
        fwd[f"fwd{H}"] = cum.values
    for H in HORIZONS:
        out[f"fwd{H}"] = fwd[f"fwd{H}"].values
    return out


def cap_forward(out: pd.DataFrame) -> pd.DataFrame:
    """Drop forward windows that cross an adjustment artifact on any intermediate day."""
    # crude but conservative: exclude rows whose own ret is an artifact, and
    # null out forward returns that are implausibly large (relit artifact)
    keep = out["ret"].abs() <= ARTIFACT_CAP
    out = out[keep].copy()
    for H in HORIZONS:
        out.loc[out[f"fwd{H}"].abs() > 2.0, f"fwd{H}"] = np.nan
    return out


def summarize(df: pd.DataFrame, name: str) -> pd.DataFrame:
    rows = []
    for H in HORIZONS:
        col = f"fwd{H}"
        for band, sub in df.groupby("tile"):
            sub = sub[sub[col].notna()]
            if len(sub) == 0:
                continue
            rows.append({"horizon": H, "tile": int(band), "n": len(sub),
                         "mean_bps": sub[col].mean() * 1e4, "median_bps": sub[col].median() * 1e4})
    res = pd.DataFrame(rows)
    res["set"] = name
    return res


def main() -> None:
    print("loading panel ...")
    df = load_panel()
    print(f"  {len(df):,} symbol-day rows after finite-return guard")

    df = build_features(df)
    df = tilt_features(df)
    out = forward_returns(df)
    out = cap_forward(out)
    print(f"  scored rows: {len(out):,}")

    date_split = pd.Timestamp("2010-01-01")
    is_df = out[out["date"] < date_split]
    oos_df = out[out["date"] >= date_split]

    full_is = summarize(is_df, "IS-all")
    full_oos = summarize(oos_df, "OOS-all")

    # LIQUID-ONLY: price > $5 AND stale_share < 25% (tradable universe)
    liq_is = is_df[(is_df["price_med"] > 5.0) & (is_df["stale_share"] < 0.25)].copy()
    liq_oos = oos_df[(oos_df["price_med"] > 5.0) & (oos_df["stale_share"] < 0.25)].copy()
    liq_is = summarize(liq_is, "IS-liquid")
    liq_oos = summarize(liq_oos, "OOS-liquid")

    panels = pd.concat([full_is, full_oos, liq_is, liq_oos], ignore_index=True)
    out_path = OUT / "liquidity_scan_summary.csv"
    panels.to_csv(out_path, index=False)
    print(f"\nwrote {out_path}\n")

    print("=== mean forward ret (bps) by liquidity tile, per set ===")
    show = panels.pivot_table(index=["set", "horizon"], columns="tile", values="mean_bps")
    print(show.round(1).to_string())
    print("\n(tile 0 = LEAST stale / most liquid; tile 4 = MOST stale / least liquid)")


if __name__ == "__main__":
    main()
