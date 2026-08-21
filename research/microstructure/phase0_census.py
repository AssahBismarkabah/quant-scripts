import glob
import os

import numpy as np
import pandas as pd

CACHE = "research/microstructure/cache"
OUT = "research/microstructure/outputs"
PAIRS = ["BTCUSDT", "ETHUSDT"]


def load_day(path):
    return pd.read_parquet(path)


def census_pair(pair):
    bd_files = sorted(glob.glob(os.path.join(CACHE, f"{pair}-bookDepth-*.parquet")))
    at_files = sorted(glob.glob(os.path.join(CACHE, f"{pair}-aggTrades-*.parquet")))
    rows = []
    bd_snap_gaps = []
    bd_valid_min_fracs = []
    at_day_counts = []
    vwap_gaps = 0
    vwap_minutes = 0
    prev_min = None
    for bd, at in zip(bd_files, at_files):
        day = os.path.basename(bd).split("-")[2]
        bdf = load_day(bd)
        atf = load_day(at)
        if bdf.empty or atf.empty:
            rows.append((day, "EMPTY", 0, 0, 0))
            continue
        bdf = bdf.sort_values("ts")
        snaps = bdf.groupby("ts").size()
        valid_snaps = snaps[(snaps == 10) & (bdf.groupby("ts")["depth"].min() >= 0)]
        bd_valid_min_fracs.append(len(valid_snaps) / max(len(snaps), 1))
        gaps = bdf["ts"].diff().dropna().dt.total_seconds()
        bd_snap_gaps.append((gaps > 30).mean())
        atf["min"] = atf["ts"].dt.floor("min")
        agg = atf.groupby("min").agg(
            n=("agg_trade_id", "count"),
            buy_vol=("quantity", lambda s: s[~atf.loc[s.index, "is_buyer_maker"]].sum()),
            sell_vol=("quantity", lambda s: s[atf.loc[s.index, "is_buyer_maker"]].sum()),
        )
        agg["vwap"] = atf.groupby("min").apply(
            lambda g: (g["price"] * g["quantity"]).sum() / g["quantity"].sum(), include_groups=False
        )
        at_day_counts.append(int(agg["n"].sum()))
        cur = agg["vwap"].dropna()
        for ts, v in cur.items():
            if prev_min is not None and (ts - prev_min).total_seconds() <= 90:
                vwap_minutes += 1
                if abs(v / prev_v - 1) > 0.10:
                    vwap_gaps += 1
            prev_min, prev_v = ts, v
        rows.append((day, "OK", len(valid_snaps), len(snaps), int(agg["n"].sum())))
    bd_frac = np.mean(bd_valid_min_fracs)
    gap_frac = np.mean(bd_snap_gaps)
    counts = np.array(at_day_counts)
    dow = pd.Series(counts).groupby(np.arange(len(counts)) % 7)
    dow_med = pd.Series(counts).groupby(np.arange(len(counts)) % 7).transform("median")
    dow_std = pd.Series(counts).groupby(np.arange(len(counts)) % 7).transform("std")
    outlier_days = int(((counts - dow_med).abs() > 3 * dow_std).sum())
    vwap_gap_frac = vwap_gaps / max(vwap_minutes, 1)
    result = {
        "pair": pair,
        "days": len(rows),
        "bd_minute_coverage": round(bd_frac, 4),
        "bd_snapshot_gap30s_frac": round(gap_frac, 4),
        "aggTrades_days_outside_3sigma": outlier_days,
        "vwap_gap10pct_frac": round(vwap_gap_frac, 5),
    }
    return result, pd.DataFrame(rows, columns=["day", "status", "valid_snaps", "snaps", "trades"])


def main():
    os.makedirs(OUT, exist_ok=True)
    summary = []
    for pair in PAIRS:
        res, df = census_pair(pair)
        summary.append(res)
        df.to_csv(os.path.join(OUT, f"phase0_census_{pair}.csv"), index=False)
        print(pair, res)
    pd.DataFrame(summary).to_csv(os.path.join(OUT, "phase0_census_summary.csv"), index=False)
    for r in summary:
        g = {
            "bd_minute_coverage": r["bd_minute_coverage"] >= 0.95,
            "bd_snapshot_gap30s_frac": r["bd_snapshot_gap30s_frac"] <= 0.05,
            "aggTrades_days_outside_3sigma": r["aggTrades_days_outside_3sigma"] == 0,
            "vwap_gap10pct_frac": r["vwap_gap10pct_frac"] == 0,
        }
        print("gates:", g, "PASS" if all(g.values()) else "FAIL")


if __name__ == "__main__":
    main()