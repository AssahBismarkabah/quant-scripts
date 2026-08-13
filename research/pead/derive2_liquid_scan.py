"""Stage 1 derive pass - second scan on the PEAD panel (liquid-only universe).

Builds on the liquidity/staleness scan (first pass = dead end on the illiquid
artifact). This scan tests TWO derived observations, restricted from the start
to the LIQUID-ONLY universe (median price > $5 AND stale_share < 25%) so we do
not repeat the microcap ghost:

  Observation A - SHORT-HORIZON REVERSAL:
    Within the liquid cross-section, do prior-1d (and prior-5d) losers beat
    winners over the next 1/5/21d? (reversal) or lose (momentum)?
    Tiles by prior-return; forward equal-weight returns per tile, IS & OOS.

  Observation B - CONDITIONAL LIQUIDITY:
    Liquidity tile x prior-return-state interaction. Is there a conditional
    cell whose forward spread is persistent and economically meaningful on
    liquid names?

All features are point-in-time (trailing window only, no lookahead). This is a
descriptive scan, not a tradeable rule. Outputs to outputs/.

NOTE: panel has only daily CLOSE (no o/h/l), so "overnight vs intraday" is not
measurable here; short-horizon means 1/5/21 trading days on closes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "research" / "pead" / "cache" / "prices_adj_long.parquet"
OUT = Path(__file__).resolve().parent / "outputs"

ARTIFACT_CAP = 1.0
STALE_WIN = 21          # trailing window for stale-share (liquidity proxy)
QUINTILES = 5
HORIZONS = [1, 5, 21]

# liquidity screen (tradable universe) — set from first-pass finding
LIQ_PRICE = 5.0
LIQ_STALE = 0.25


def load_and_clean() -> pd.DataFrame:
    df = pd.read_parquet(PANEL)
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    df["prev"] = df.groupby("symbol")["close_adjusted"].shift()
    df["ret"] = df["close_adjusted"] / df["prev"] - 1.0
    df = df[df["prev"].notna() & np.isfinite(df["ret"])].copy()
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("symbol", sort=False)
    df["zero"] = (df["ret"] == 0).astype(float)
    df["stale_share"] = g["zero"].transform(lambda s: s.rolling(STALE_WIN, min_periods=5).mean())
    df["price_med"] = g["close_adjusted"].transform(lambda s: s.rolling(STALE_WIN, min_periods=5).median())
    # prior-1d and prior-5d return (pure lag, per-symbol, no leakage)
    df["r1_lag"] = g["ret"].shift(1)
    df["r5"] = g["close_adjusted"].transform(
        lambda s: (s / s.shift(5) - 1.0).shift(1))  # prior 5d
    return df


def liquid_universe(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["price_med"] > LIQ_PRICE) & (df["stale_share"] < LIQ_STALE)].copy()


def attach_forward(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("symbol", sort=False)["close_adjusted"]
    base = df[["date", "symbol", "ret", "zero", "stale_share", "price_med", "r1_lag", "r5"]].copy()
    for H in HORIZONS:
        cum = (g.shift(-H - 1) / g.shift(-1)) - 1.0  # t+1..t+H
        base[f"fwd{H}"] = cum.values
        base.loc[base[f"fwd{H}"].abs() > 2.0, f"fwd{H}"] = np.nan  # artifact guard on fwd
    return base


def tile_by(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df[df[col].notna()].copy()
    df["tile"] = df.groupby("date")[col].transform(
        lambda s: pd.qcut(s.rank(method="first"), QUINTILES, labels=False))
    return df


def tabulate(df: pd.DataFrame, key: str, setname: str) -> pd.DataFrame:
    rows = []
    for H in HORIZONS:
        col = f"fwd{H}"
        for tile, sub in df.groupby("tile"):
            sub = sub[sub[col].notna()]
            if len(sub) == 0:
                continue
            rows.append({"set": setname, "key": key, "tile": int(tile), "horizon": H,
                         "n": len(sub), "mean_bps": sub[col].mean() * 1e4})
    return pd.DataFrame(rows)


def interaction_table(df: pd.DataFrame, setname: str) -> pd.DataFrame:
    """B) liquidity tile x prior-5d-return-sign interaction, 5/21d forward."""
    df = tile_by(df, "stale_share").copy()   # liquidity tile (0=most liquid)
    df["sig"] = np.sign(df["r5"])
    rows = []
    for H in (5, 21):
        col = f"fwd{H}"
        for lt, lg in df.groupby("tile"):
            for sg, sg2 in lg.groupby("sig"):
                sub = sg2[sg2[col].notna()]
                if len(sub) == 0:
                    continue
                rows.append({"set": setname, "horizon": H, "ltile": int(lt),
                             "sig": int(sg), "n": len(sub),
                             "mean_bps": sub[col].mean() * 1e4})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("loading + cleaning panel ...")
    df = load_and_clean()
    df = build_features(df)
    liq = liquid_universe(df)
    print(f"  rows total={len(df):,}  liquid rows={len(liq):,} "
          f"({len(liq)/len(df)*100:.1f}%)  symbols={liq['symbol'].nunique():,}")

    out = attach_forward(liq)
    split = pd.Timestamp("2010-01-01")
    is_df = out[out["date"] < split]
    oos_df = out[out["date"] >= split]

    # A) reversal / momentum by prior 1d and prior 5d
    a1_is = tabulate(tile_by(is_df, "r1_lag"), "A:prior1d", "IS")
    a1_oos = tabulate(tile_by(oos_df, "r1_lag"), "A:prior1d", "OOS")
    a5_is = tabulate(tile_by(is_df, "r5"), "A:prior5d", "IS")
    a5_oos = tabulate(tile_by(oos_df, "r5"), "A:prior5d", "OOS")

    # B) conditional liquidity x prior-5d-sign
    b_is = interaction_table(is_df, "IS")
    b_oos = interaction_table(oos_df, "OOS")

    resA = pd.concat([a1_is, a1_oos, a5_is, a5_oos], ignore_index=True)
    resB = pd.concat([b_is, b_oos], ignore_index=True)
    resA.to_csv(OUT / "derive2_reversal_summary.csv", index=False)
    resB.to_csv(OUT / "derive2_conditional_summary.csv", index=False)
    print(f"\nwrote {OUT / 'derive2_reversal_summary.csv'}")
    print(f"wrote {OUT / 'derive2_conditional_summary.csv'}")

    print("\n========== OBSERVATION A: prior1d tiles, mean fwd bps ==========")
    p = resA[resA["key"] == "A:prior1d"].pivot_table(index=["set", "horizon"], columns="tile", values="mean_bps")
    print(p.round(1).to_string())

    print("\n========== OBSERVATION A: prior5d tiles, mean fwd bps ==========")
    p = resA[resA["key"] == "A:prior5d"].pivot_table(index=["set", "horizon"], columns="tile", values="mean_bps")
    print(p.round(1).to_string())

    print("\n========== OBSERVATION B: liquidity-tile x prior5d-sign, 21d fwd ==========")
    b21 = resB[resB["horizon"] == 21].pivot_table(index=["set", "ltile"], columns="sig", values="mean_bps")
    print(b21.round(1).to_string())

    print("\n(tile 0 = most liquid; tile 4 = least liquid of the liquid universe;")
    print(" sig -1 = prior5d negative, +1 = prior5d positive)")


if __name__ == "__main__":
    main()
