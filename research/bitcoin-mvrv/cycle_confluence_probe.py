"""Bitcoin Cycle x MVRV-Z Confluence — pre-registered probe.

Surfaces the question we decided to test: does combining (a) the "Bitcoin Cycle"
indicator (1Y-MA x2 vs 116D for cycle tops; 232D vs 2Y-MA for cycle bottoms) with
(b) the MVRV Z-score low/high bands give a UNAIDED buy-at-bottom / sell-at-top
signal that beats (i) buy-and-hold BTC and (ii) the MVRV-Z band signal alone?

Frozen rules (IA/bitcoin-mvrv-cycle-confluence-research-spec.md §2/§3):
  - MVRV Z (Pine "rescaled" form, faithful to the indicator we are testing):
      rawZ = (CapMrktCurUSD - CapRealUSD) / stdev(CapMrktCurUSD, 730)
      Z    = rescale(rawZ, -0.57, 9.40, 0, 100)   (clamped, Pine rescale)
      lowB  = EMA(lowest(Z,1500),900) + 5     (low/value band line)
      highB = EMA(highest(Z,1200),900) - 20   (high/euphoria band line)
  - Cycle (Pine, crossunder only):
      CycleTop    = crossunder(2*SMA365, SMA116)
      CycleBottom = crossunder(SMA232, SMA2Y)
  - Signal families (both variants tested, pre-registered):
      CONFLUENCE : buy  = CycleBottom AND Z < lowB
                   sell = CycleTop    AND Z > highB
      EITHER     : buy  = CycleBottom OR  Z < lowB
                   sell = CycleTop    OR  Z > highB
  - MVRV-only benchmark: buy = Z < lowB, sell = Z > highB  (no cycle).
  - Positions (both tested): long-only ; long+short (short = opposite of long).
  - Friction: 10 bps/side + 25 bps flat on each round turn, applied per position change.
  - Split: IS 2013-01-01..2020-12-31 ; OOS 2021-01-01..2026-08-09 (same as prior probe).

Output: outputs/bitcoin_cycle_confluence_summary.json + series parquet.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "research" / "bitcoin-mvrv" / "cache"
OUTDIR = ROOT / "research" / "bitcoin-mvrv" / "outputs"
OUT = OUTDIR / "bitcoin_cycle_confluence_summary.json"

# Pine parameters (faithful to the indicator being tested)
RAW_MIN, RAW_MAX = -0.57, 9.40
Z_LOW_LOOKBACK = 1500
Z_HIGH_LOOKBACK = 1200
EMA_LEN = 900
LOW_OFFSET = 5.0
HIGH_OFFSET = 20.0
SMA116, SMA365 = 116, 365
SMA232, SMA2Y = 232, 730

FRICTION_SIDE = 0.0010
FRICTION_FLAT = 0.0025
TOTAL_BUDGET = 100_000_000.0
IS_START, IS_END = "2013-01-01", "2020-12-31"
OOS_START, OOS_END = "2021-01-01", "2026-08-09"


def load() -> pd.DataFrame:
    df = pd.read_parquet(CACHE / "mvrv.parquet")
    df = df[["CapMrktCurUSD", "CapRealUSD", "price"]].loc["2009-01-01":].copy()
    df["MC"] = df["CapMrktCurUSD"]
    df["RC"] = df["CapRealUSD"]
    return df


def _ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def build_signals(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    # --- MVRV Z (rescaled, Pine) ---
    d["rawZ"] = (d["MC"] - d["RC"]) / d["MC"].rolling(730, min_periods=730).std(ddof=0)
    raw = d["rawZ"].clip(lower=RAW_MIN, upper=RAW_MAX)
    d["Z"] = (raw - RAW_MIN) / (RAW_MAX - RAW_MIN) * 100.0
    d["lowestZ"] = d["Z"].rolling(Z_LOW_LOOKBACK, min_periods=Z_LOW_LOOKBACK).min()
    d["highestZ"] = d["Z"].rolling(Z_HIGH_LOOKBACK, min_periods=Z_HIGH_LOOKBACK).max()
    d["lowB"] = _ema(d["lowestZ"], EMA_LEN) + LOW_OFFSET
    d["highB"] = _ema(d["highestZ"], EMA_LEN) - HIGH_OFFSET

    # --- Cycle (Pine, crossunder only) ---
    p = d["price"]
    ma116 = p.rolling(SMA116, min_periods=SMA116).mean()
    ma365 = p.rolling(SMA365, min_periods=SMA365).mean()
    ma232 = p.rolling(SMA232, min_periods=SMA232).mean()
    ma2y = p.rolling(SMA2Y, min_periods=SMA2Y).mean()
    d["CycleTop"] = ((2 * ma365).shift(1) > ma116.shift(1)) & (2 * ma365 <= ma116)
    d["CycleBottom"] = (ma232.shift(1) > ma2y.shift(1)) & (ma232 <= ma2y)

    # --- event flags (forward-usable at close t) ---
    d["z_low"] = d["Z"] < d["lowB"]
    d["z_high"] = d["Z"] > d["highB"]
    return d


def make_signals(d: pd.DataFrame, family: str) -> pd.DataFrame:
    """Return per-day 'buy'/'sell' boolean event signals for a signal family."""
    s = pd.DataFrame(index=d.index)
    if family == "confluence":
        s["buy"] = d["CycleBottom"] & d["z_low"]
        s["sell"] = d["CycleTop"] & d["z_high"]
    elif family == "either":
        s["buy"] = d["CycleBottom"] | d["z_low"]
        s["sell"] = d["CycleTop"] | d["z_high"]
    elif family == "mvrv":
        s["buy"] = d["z_low"]
        s["sell"] = d["z_high"]
    else:
        raise ValueError(family)
    return s


def simulate(d: pd.DataFrame, sig: pd.DataFrame, start: str, end: str,
             allow_short: bool) -> pd.Series:
    d = d.loc[start:end]
    sig = sig.loc[start:end]
    price = d["price"]
    cash = TOTAL_BUDGET
    pos = 0.0  # +1 long, -1 short, 0 flat
    btc = 0.0  # signed BTC holding
    value = pd.Series(np.nan, index=d.index, dtype=float)

    for t in d.index:
        p = price.at[t]
        ev = sig.loc[t]
        if ev["buy"] and btc <= 0:
            if btc < 0:  # cover short -> flat
                cash += -btc * p * (1 - FRICTION_SIDE) * (1 - FRICTION_FLAT)
                btc = 0.0
            spend = cash * (1 - FRICTION_SIDE) * (1 - FRICTION_FLAT)
            btc = spend / p
            cash -= spend
        elif ev["sell"] and allow_short and btc >= 0:
            if btc > 0:  # flatten long
                cash += btc * p * (1 - FRICTION_SIDE) * (1 - FRICTION_FLAT)
                btc = 0.0
            # go short: sell notional worth of BTC; proceeds held in cash (margin, earns 0)
            notional = cash * (1 - FRICTION_SIDE) * (1 - FRICTION_FLAT)
            cash += notional
            btc = -notional / p
        elif ev["sell"] and not allow_short and btc > 0:
            cash += btc * p * (1 - FRICTION_SIDE) * (1 - FRICTION_FLAT)
            btc = 0.0
        value.at[t] = cash + btc * p
    return value.ffill().fillna(TOTAL_BUDGET)


def metrics(v: pd.Series) -> dict:
    if len(v) < 2:
        return {}
    rets = v.pct_change().dropna()
    days = (v.index[-1] - v.index[0]).days
    years = days / 365.25
    cagr = (v.iloc[-1] / v.iloc[0]) ** (1 / years) - 1 if years > 0 and v.iloc[0] > 0 else np.nan
    vol = rets.std(ddof=0) * np.sqrt(365.25)
    sharpe = (rets.mean() / rets.std(ddof=0)) * np.sqrt(365.25) if rets.std(ddof=0) > 0 else np.nan
    peak = v.cummax()
    dd = v / peak - 1
    max_dd = dd.min()
    trough_t = dd.idxmin()
    peak_before = v.loc[:trough_t].idxmax()
    rec = v.loc[trough_t:]
    recovered = rec[rec >= v.loc[peak_before]]
    ttr = np.nan
    if len(recovered) > 0:
        ttr = (recovered.index[0] - trough_t).days
    return {
        "cagr": float(cagr), "sharpe": float(sharpe), "vol": float(vol),
        "max_drawdown": float(max_dd),
        "ttr_days": None if pd.isna(ttr) else int(ttr),
        "end_value": float(v.iloc[-1]), "start_value": float(v.iloc[0]),
    }


def main() -> int:
    df = load()
    d = build_signals(df)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    print(f"data: {len(d):,} rows  {d.index.min().date()} .. {d.index.max().date()}")
    print(f"cycle events: CycleTop={int(d['CycleTop'].sum())}, "
          f"CycleBottom={int(d['CycleBottom'].sum())}; "
          f"Z low days={int(d['z_low'].sum())}, Z high days={int(d['z_high'].sum())}")

    result = {"meta": {
        "pre_registered": "2026-08-11",
        "purpose": "Does Bitcoin-Cycle x MVRV-Z confluence beat buy-hold and MVRV-Z alone?",
        "rules": {
            "mvrv_z": "rawZ=(MC-RC)/std(MC,730); Z=rescale(rawZ,-0.57,9.4,0,100)",
            "lowB": "ema(lowest(Z,1500),900)+5", "highB": "ema(highest(Z,1200),900)-20",
            "cycle_top": "crossunder(2*SMA365,SMA116)",
            "cycle_bottom": "crossunder(SMA232,SMA2Y)",
            "friction_side": FRICTION_SIDE, "friction_flat": FRICTION_FLAT,
        },
        "split": {"IS": [IS_START, IS_END], "OOS": [OOS_START, OOS_END]},
    }, "windows": {}, "gate_summary": {}}

    families = ["confluence", "either", "mvrv"]
    sides = [False, True]  # long-only, long+short
    sigs = {f: make_signals(d, f) for f in families}

    # buy-and-hold (no short) computed once
    bh_vals = {}
    for wname, (ws, we) in {"IS": (IS_START, IS_END), "OOS": (OOS_START, OOS_END)}.items():
        dd = d.loc[ws:we]
        bh = pd.Series(index=dd.index, dtype=float)
        p0 = dd["price"].iloc[0]
        btc = TOTAL_BUDGET * (1 - FRICTION_SIDE) * (1 - FRICTION_FLAT) / p0
        bh_vals[wname] = pd.Series(btc * dd["price"].values, index=dd.index)
        result["windows"].setdefault(wname, {})["buyhold"] = metrics(bh_vals[wname])

    for family in families:
        for allow_short in sides:
            label = f"{family}_longonly" if not allow_short else f"{family}_longshort"
            for wname, (ws, we) in {"IS": (IS_START, IS_END), "OOS": (OOS_START, OOS_END)}.items():
                v = simulate(d, sigs[family], ws, we, allow_short)
                result["windows"].setdefault(wname, {})[label] = metrics(v)

    # Save series for the key variants (trace)
    for variant in ["confluence_longonly", "confluence_longshort"]:
        frames = {}
        for allow_short in sides:
            sig = sigs["confluence"]
            nm = variant if (allow_short == ("_longshort" in variant)) else None
        # simpler: save confluence long-only + long-short + mvrv + buyhold traces
        out = {}
        for fam in families:
            for as_ in sides:
                nm = f"{fam}_{'longonly' if not as_ else 'longshort'}"
                out[nm] = simulate(d, sigs[fam], OOS_START, OOS_END, as_)
        out["buyhold"] = bh_vals["OOS"]
        pd.DataFrame(out).to_parquet(OUTDIR / "cycle_confluence_oos_series.parquet")

    # ---- Gate summary (confluence long-only adds value over buy-hold?) ----
    is_ = result["windows"]["IS"]
    oos = result["windows"]["OOS"]
    g = {}
    for wname, W in [("IS", is_), ("OOS", oos)]:
        bh_c = W["buyhold"]["cagr"]
        cf_c = W["confluence_longonly"]["cagr"]
        cf_dd = W["confluence_longonly"]["max_drawdown"]
        bh_dd = W["buyhold"]["max_drawdown"]
        g[f"{wname}_conflongonly_vs_bh"] = {
            "cagr": cf_c, "bh_cagr": bh_c,
            "delta_cagr": cf_c - bh_c,
            "max_dd": cf_dd, "bh_max_dd": bh_dd,
            "dd_pp_shallower": (bh_dd - cf_dd) * 100,
            "sharpe": W["confluence_longonly"]["sharpe"],
            "bh_sharpe": W["buyhold"]["sharpe"],
        }
    # confluence vs mvrv-only
    for wname, W in [("IS", is_), ("OOS", oos)]:
        cf = W["confluence_longonly"]["cagr"]
        mv = W["mvrv_longonly"]["cagr"]
        g[f"{wname}_conflongonly_vs_mvrv"] = {
            "delta_cagr": cf - mv,
            "confluence_cagr": cf, "mvrv_cagr": mv,
        }
    result["gate_summary"] = g
    result["verdict"] = "SEE DATA — reviewer decision pending (no pre-judged outcome)."

    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2, default=str))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
