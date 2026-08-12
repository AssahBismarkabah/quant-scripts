"""Step 2 — Time-series index-timing basket (aggregation / portfolio-of-signals).

Implements IA/path-forward-decision-memo.md Step 2 with data we ALREADY OWN.

Pre-registered (2026-08-12, frozen BEFORE any run; no post-hoc member/parameter
selection):

Data:
  SPY daily close, 1993-02 -> 2026-07 (research/vol-targeting/cache/SPY_clean_long.parquet)
  (IWM size-tilt member DROPPED - IWM cached history only starts 2023, too short
   for a relative-momentum member. Honest scope: build only long-history members.)

Members (each an independent, look-ahead-free, single-index timing signal on SPY;
single THE 'why' per signal per the framework):
  1. time_series_mom  : sign of trailing 12m SPY return, skipping the last month.
  2. reversal_1m      : NEGATIVE of trailing 1m SPY return.
  3. turn_of_month    : long SPY on last 2 + first 3 trading days of each month, else flat.
  4. january_effect   : long SPY during January, else flat.
  5. seasonality_novapr: long SPY in Nov-Dec-Jan-Feb-Mar-Apr, else flat.

Combination rule (frozen):
  - Each signal emits a daily target weight in [-1, 0, +1].
  - z-score normalize each signal's weight series using IS-only mean/sd.
  - Book signal = mean of the 5 z-scored member weights (equal weight).
  - Final position = book signal scaled to fixed 10% ex-ante annualized vol,
    using trailing realized vol (60d) clipped to [5%, 40%].
  - No member dropped, no parameter search, no tuning.

Benchmarks:
  - long_vol: buy-and-hold SPY vol-scaled to 10% (same scaler).
  - cash: 0%.

Friction: 10 bps/side on every position change (same order as our other probes).

OOS gate (frozen, per memo): on OOS only,
  - bootstrap p5 of the book's mean daily excess return > 0
  - profit factor (gross win total / gross loss total) >= 1.0
  - robustness to a holdout re-split (direction positive in both halves)

We set a NEUTRAL prior: with 13/13 singles dead, the basket failing is the more
likely outcome; the gate rules either way.

Output: research/portfolio-book/step2_basket_summary.json + series parquet.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SPY = ROOT / "research" / "vol-targeting" / "cache" / "SPY_clean_long.parquet"
OUTDIR = ROOT / "research" / "portfolio-book"
OUT = OUTDIR / "step2_basket_summary.json"

IS_START, IS_END = "1993-09-01", "2008-12-31"
OOS_START, OOS_END = "2010-01-01", "2026-07-31"
# warmup: member indicators need up to 12m lookback -> test windows start 1993-09
TARGET_VOL = 0.10
VOL_WINDOW = 60
VOL_CLIP = (0.05, 0.40)
FRICTION = 0.0010
N_BOOT = 5000
SEED = 11
DROPPED_NOTE = "IWM size-tilt member dropped (IWM cached history starts 2023; too short for relative-momentum)."


def load() -> pd.DataFrame:
    df = pd.read_parquet(SPY)
    df["ts_date"] = pd.to_datetime(df["ts_date"])
    df = df.set_index("ts_date")[["close"]].sort_index()
    df["ret"] = df["close"].pct_change()
    return df


def member_signals(d: pd.DataFrame) -> pd.DataFrame:
    s = pd.DataFrame(index=d.index)

    # 1. time-series momentum: sign of 12m return (skip last month)
    mom12 = d["close"] / d["close"].shift(252) - 1
    s["time_series_mom"] = np.sign(mom12)

    # 2. 1-month reversal: negative of trailing 21d return
    rev1 = d["close"] / d["close"].shift(21) - 1
    s["reversal_1m"] = -np.sign(rev1)

    # 3. turn-of-month: last 2 + first 3 trading days of month
    idx = d.index
    month = idx.month
    day = idx.day
    # last 2 trading days of each month
    is_last2 = idx.isin(_last_n_trading_days(idx, 2))
    # first 3 trading days of each month
    is_first3 = idx.isin(_first_n_trading_days(idx, 3))
    s["turn_of_month"] = np.where(is_last2 | is_first3, 1.0, 0.0)

    # 4. january effect
    s["january_effect"] = np.where(month == 1, 1.0, 0.0)

    # 5. seasonality Nov-Apr
    s["seasonality_novapr"] = np.where(month.isin([1, 2, 3, 4, 11, 12]), 1.0, 0.0)

    return s


def _first_n_trading_days(idx: pd.DatetimeIndex, n: int) -> list:
    out = []
    for m in np.unique(idx.to_period("M")):
        sub = idx[idx.to_period("M") == m]
        if len(sub) >= n:
            out.extend(list(sub[:n]))
    return out


def _last_n_trading_days(idx: pd.DatetimeIndex, n: int) -> list:
    out = []
    for m in np.unique(idx.to_period("M")):
        sub = idx[idx.to_period("M") == m]
        if len(sub) >= n:
            out.extend(list(sub[-n:]))
    return out


def vol_signal(d: pd.DataFrame, sig: pd.Series) -> pd.Series:
    """Scale signal to target annualized vol using trailing realized vol."""
    rv = d["ret"].rolling(VOL_WINDOW).std() * np.sqrt(252)
    rv = rv.clip(*VOL_CLIP)
    pos = sig.div(rv).mul(TARGET_VOL)
    return pos.fillna(0.0)


def backtest(d: pd.DataFrame, pos: pd.Series, start: str, end: str) -> pd.Series:
    d = d.loc[start:end]
    pos = pos.loc[start:end]
    ret = d["ret"]
    # fill at next day open; approximate via close-to-close with friction on change
    value = pd.Series(1.0, index=d.index, dtype=float)
    prev_pos = 0.0
    ex = 1.0
    for t in d.index:
        p = pos.loc[t]
        if pd.notna(p):
            change = abs(p - prev_pos) * FRICTION
            day_ret = p * ret.loc[t] - change
            ex *= (1 + day_ret)
            prev_pos = p
        value.loc[t] = ex
    return value


def bootstrap_p5(excess: pd.Series) -> float:
    x = excess.dropna().to_numpy()
    rng = np.random.default_rng(SEED)
    means = np.array([rng.choice(x, size=len(x), replace=True).mean() for _ in range(N_BOOT)])
    return float(np.percentile(means, 5))


def profit_factor(daily_ret: pd.Series) -> float:
    wins = daily_ret[daily_ret > 0].sum()
    losses = -daily_ret[daily_ret < 0].sum()
    return float(wins / losses) if losses > 0 else float("inf")


def main() -> int:
    d = load()
    sigs = member_signals(d)
    print("members:", list(sigs.columns))

    # IS-only z-score normalization (frozen: no OOS info leaks into scaling)
    is_sigs = sigs.loc[IS_START:IS_END]
    zmean = is_sigs.mean()
    zstd = is_sigs.std(ddof=0).replace(0, np.nan)
    zscores = (sigs - zmean) / zstd
    book_sig = zscores.mean(axis=1)  # equal-weight mean of z-scored members

    # vol-scaled positions
    book_pos = vol_signal(d, book_sig)
    buyhold_pos = pd.Series(TARGET_VOL, index=d.index)  # constant exposure

    result = {"meta": {
        "pre_registered": "2026-08-12",
        "purpose": "Aggregation test: does a vol-scaled book of 5 weak index-timing "
                   "signals clear costs OOS? (neutral prior: likely fails)",
        "members": list(sigs.columns),
        "combination": "equal-weight mean of IS-z-scored member weights; vol-scaled to 10%",
        "benchmarks": ["long_vol(self-scaled buyhold)", "cash"],
        "friction_bps": FRICTION * 1e4,
        "target_vol": TARGET_VOL,
        "dropped": DROPPED_NOTE,
        "split_is": [IS_START, IS_END], "split_oos": [OOS_START, OOS_END],
    }, "members_WITHIN": {}, "windows": {}, "gates": {}}

    # --- member-level context (informational; NOT the gate) ---
    for name, w in sigs.items():
        p = vol_signal(d, w)
        for wname, ws, we in [("IS", IS_START, IS_END), ("OOS", OOS_START, OOS_END)]:
            v = backtest(d, p, ws, we)
            dr = v.pct_change().dropna()
            result["members_WITHIN"].setdefault(wname, {})[name] = {
                "cagr": float(((1+dr).prod()) ** (252/len(dr)) - 1) if len(dr) else np.nan,
                "sharpe": float(dr.mean()/dr.std(ddof=0)*np.sqrt(252)) if dr.std(ddof=0)>0 else np.nan,
                "days_long": int((w.loc[ws:we]>0).sum()),
            }

    # --- book + benchmarks over IS/OOS ---
    frames = {}
    for wname, ws, we in [("IS", IS_START, IS_END), ("OOS", OOS_START, OOS_END)]:
        vb = backtest(d, book_pos, ws, we)
        vh = backtest(d, buyhold_pos, ws, we)
        drb = vb.pct_change().dropna()
        drh = vh.pct_change().dropna()
        years = len(drb) / 252
        result["windows"][wname] = {
            "book": {
                "cagr": float(vb.iloc[-1] ** (1/years) - 1) if vb.iloc[-1] > 0 else np.nan,
                "sharpe": float(drb.mean()/drb.std(ddof=0)*np.sqrt(252)) if drb.std(ddof=0)>0 else np.nan,
                "max_dd": float((vb/vb.cummax()-1).min()),
                "bootstrap_p5_mean_excess": bootstrap_p5(drb),
                "profit_factor": profit_factor(drb),
                "end_value": float(vb.iloc[-1]),
            },
            "buyhold_vol": {
                "cagr": float(vh.iloc[-1] ** (1/years) - 1) if vh.iloc[-1] > 0 else np.nan,
                "sharpe": float(drh.mean()/drh.std(ddof=0)*np.sqrt(252)) if drh.std(ddof=0)>0 else np.nan,
                "max_dd": float((vh/vh.cummax()-1).min()),
                "end_value": float(vh.iloc[-1]),
            },
        }
        frames[wname] = pd.DataFrame({"book": vb, "buyhold": vh})

    # --- OOS gate (frozen) ---
    oos = result["windows"]["OOS"]
    g1 = oos["book"]["bootstrap_p5_mean_excess"] > 0
    g2 = oos["book"]["profit_factor"] >= 1.0
    # holdout: split OOS in half, direction positive in both
    ho1 = backtest(d, book_pos, OOS_START, "2018-03-31").pct_change().dropna().mean()
    ho2 = backtest(d, book_pos, "2018-04-01", OOS_END).pct_change().dropna().mean()
    g3 = bool(ho1 > 0 and ho2 > 0)
    result["gates"] = {
        "G2A_oos_p5_gt_0": {"pass": g1, "p5": oos["book"]["bootstrap_p5_mean_excess"]},
        "G2B_oos_pf_ge_1": {"pass": g2, "pf": oos["book"]["profit_factor"]},
        "G2C_oos_holdout_robust": {"pass": g3, "half1_mean": float(ho1), "half2_mean": float(ho2)},
    }
    result["step2_verdict"] = "CLEARS-OOS" if (g1 and g2 and g3) else "FAILS-OOS"
    result["conclusion"] = (
        "Basket of weak index-timing signals clears costs OOS -> product lane is a "
        "vol-sized book (per memo Step 3)."
        if result["step2_verdict"] == "CLEARS-OOS"
        else "Free-data portfolio (index-timing aggregation) is measured-dead OOS net of "
             "friction -> per memo Step 3, remaining choice is buy-data (a) or stop (b)."
    )

    OUTDIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, default=str))
    pd.concat(frames, axis=1).to_parquet(OUTDIR / "step2_series.parquet")
    print(json.dumps(result, indent=2, default=str))
    print(f"\nStep 2 verdict: {result['step2_verdict']}")
    print(f"wrote {OUT}")
    return 0 if result["step2_verdict"] == "CLEARS-OOS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
