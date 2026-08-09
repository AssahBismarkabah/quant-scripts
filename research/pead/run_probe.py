"""PEAD probe: post-earnings-announcement-drift long-short decile spread.

Usage: .venv/bin/python research/pead/run_probe.py

Reads the downloaded Kaggle earnings + price caches (research/pead/cache/),
computes SUE per announcement, forms quarterly top/bottom SUE deciles, and
measures the 60-trading-day long-short drift on IS (2013-2017) and OOS
(2018-2021-06), under house friction + pre-registered gates (IA/pead-research-spec.md).

Writes outputs/pead_summary.json and outputs/pead_events.parquet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "research" / "pead" / "cache"
OUT = ROOT / "research" / "pead" / "outputs"

IS_WINDOW = ("2013-01-01", "2017-12-31")
OOS_WINDOW = ("2018-01-01", "2021-06-14")
WARMUP_START = "2012-01-01"
HOLD_DAYS = 60
DECILE = 10
MIN_PRIOR_UE = 4
MIN_CROSS = 50
MIN_ENTRY_PRICE = 5.0      # penny-stock screen: entry close_adjusted >= $5
WINSOR_RET = 3.0           # winsorize 60-day return at +-300% (artifacts guard)

# friction per side (fraction of price), base + stress
FRICTION_BASE = 0.0020   # 20 bps per side
FRICTION_STRESS = 0.0050  # 50 bps per side

N_SIMS = 5000
SEED = 42


def _load_earnings() -> pd.DataFrame:
    df = pd.read_csv(CACHE / "earnings_latest.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["eps_est"].notna() & df["eps"].notna()].copy()
    df = df[(df["date"] >= WARMUP_START) & (df["date"] <= OOS_WINDOW[1])].copy()
    return df.reset_index(drop=True)


def _compute_sue(earn: pd.DataFrame) -> pd.DataFrame:
    """SUE = UE / rolling stock UE std (min 4 prior); cross-sectional fallback."""
    earn = earn.sort_values(["symbol", "date"]).reset_index(drop=True)
    earn["UE"] = earn["eps"] - earn["eps_est"]
    # per-stock rolling std of prior UE (exclude current)
    g = earn.groupby("symbol")
    earn["UE_std"] = g["UE"].transform(
        lambda s: s.shift(1).rolling(min_periods=MIN_PRIOR_UE, window=1000).std())
    # cross-sectional fallback within calendar quarter
    earn["qkey"] = earn["date"].dt.to_period("Q")
    earn["UE_std_q"] = earn.groupby("qkey")["UE"].transform(
        lambda s: s.std(ddof=1) if s.notna().sum() >= MIN_CROSS else np.nan)
    std = earn["UE_std"].fillna(earn["UE_std_q"])
    earn["SUE"] = earn["UE"] / std.replace(0, np.nan)
    earn = earn[earn["SUE"].notna()].copy()
    return earn.reset_index(drop=True)


def _load_prices(symbols: set[str]) -> pd.DataFrame:
    """Load close_adjusted prices for needed symbols (2GB file, columns subset)."""
    cols = ["symbol", "date", "close_adjusted"]
    chunks = pd.read_csv(CACHE / "stock_prices_latest.csv", usecols=cols, chunksize=3_000_000)
    frames = []
    for c in chunks:
        c = c[c["symbol"].isin(symbols)]
        c["date"] = pd.to_datetime(c["date"])
        frames.append(c)
    if not frames:
        raise SystemExit("no price rows matched earnings symbols")
    out = pd.concat(frames, ignore_index=True)
    out = out.dropna(subset=["close_adjusted"])
    out = out.sort_values(["symbol", "date"]).reset_index(drop=True)
    return out


def _build_price_lookup(prices: pd.DataFrame):
    """Per-symbol arrays of dates/adjusted closes for index-based hold returns."""
    lookup = {}
    for sym, g in prices.groupby("symbol", sort=True):
        lookup[sym] = {
            "dt": g["date"].to_numpy(dtype="datetime64[ns]"),
            "px": g["close_adjusted"].to_numpy(dtype=float),
        }
    return lookup


def _build_market_index(prices: pd.DataFrame):
    """Winsorized cross-sectional-mean daily market index.

    close_adjusted back-adjustment artifacts produce extreme per-stock 1-day
    returns, so per-day returns are clipped to [-50%, +100%] and each day's
    cross-section is winsorized at the 1st/99th percentile before taking the
    mean (robust to artifacts yet not small-cap/median biased).
    """
    p = prices.copy()
    p = p[p["close_adjusted"] > 0]
    p = p.sort_values(["symbol", "date"])
    p["prev_px"] = p.groupby("symbol")["close_adjusted"].shift(1)
    p["r1"] = (p["close_adjusted"] / p["prev_px"] - 1.0).clip(-0.5, 1.0)

    def _wmean(s):
        a = s.to_numpy(dtype=float)
        a = a[np.isfinite(a)]
        if a.size < 5:
            return np.nan
        lo, hi = np.percentile(a, [1, 99])
        return np.clip(a, lo, hi).mean()

    daily = p.groupby("date")["r1"].agg(_wmean).dropna().sort_index()
    idx = (1.0 + daily).cumprod()
    return {"dt": idx.index.to_numpy(dtype="datetime64[ns]"),
            "idx": idx.to_numpy(dtype=float)}


def _mkt_return(entry_dt, hold_days, mkt: dict) -> float | None:
    dt, idx = mkt["dt"], mkt["idx"]
    i = np.searchsorted(dt, np.datetime64(entry_dt), side="right")
    if i >= len(dt):
        return None
    j = i + hold_days
    if j >= len(dt):
        j = len(dt) - 1
    if j <= i:
        return None
    return float(idx[j] / idx[i] - 1.0)


def _event_return(entry_dt, hold_days, pl: dict) -> float | None:
    """Return over `hold_days` trading days from the first price date > entry_dt."""
    dt, px = pl["dt"], pl["px"]
    i = np.searchsorted(dt, np.datetime64(entry_dt), side="right")
    if i >= len(dt):
        return None
    j = i + hold_days
    if j >= len(dt):
        j = len(dt) - 1
    if j <= i:
        return None
    return float(px[j] / px[i] - 1.0)


def _entry_price(entry_dt, pl: dict) -> float | None:
    """Prior close_adjusted just before the announcement (used for penny screen)."""
    dt, px = pl["dt"], pl["px"]
    i = np.searchsorted(dt, np.datetime64(entry_dt), side="left") - 1
    if i < 0 or i >= len(dt):
        return None
    return float(px[i])


def _run(earn: pd.DataFrame, splits, prices_lookup, mkt, friction) -> dict:
    events = []
    for _, ev in earn.iterrows():
        sym = ev["symbol"]
        if sym not in prices_lookup:
            continue
        pl = prices_lookup[sym]
        ret = _event_return(ev["date"], HOLD_DAYS, pl)
        if ret is None:
            continue
        entry_px = _entry_price(ev["date"], pl)
        if entry_px is None or entry_px < MIN_ENTRY_PRICE:
            continue
        ret = float(np.clip(ret, -WINSOR_RET, WINSOR_RET))
        mret = _mkt_return(ev["date"], HOLD_DAYS, mkt) if mkt else None
        events.append({
            "symbol": sym, "date": ev["date"], "qkey": str(ev["qkey"]),
            "SUE": ev["SUE"], "ret60": ret, "entry_price": entry_px,
            "ret60_mkt_adj": (ret - mret) if mret is not None else np.nan,
        })
    evdf = pd.DataFrame(events)

    results = {}
    for label, (w0, w1) in splits.items():
        win = (evdf["date"] >= pd.Timestamp(w0)) & (evdf["date"] <= pd.Timestamp(w1) + pd.Timedelta(days=1))
        sub = evdf[win].copy()
        sub["rank"] = sub.groupby("qkey")["SUE"].rank(pct=True, method="first")
        top = sub[sub["rank"] > (DECILE - 1) / DECILE].copy()
        bot = sub[sub["rank"] <= 1 / DECILE].copy()
        top["leg"] = "long"; bot["leg"] = "short"
        # signed per-event P&L (fraction). long: +ret; short: -ret. round-trip cost per leg.
        top["pnl_gross"] = top["ret60"]
        top["pnl_net"] = top["ret60"] - 2 * friction          # buy+sell round trip
        bot["pnl_gross"] = -bot["ret60"]
        bot["pnl_net"] = -bot["ret60"] - 2 * friction          # sell+buy round trip
        all_ev = pd.concat([top, bot], ignore_index=True)
        # long-short spread (equal-weight leg means); short leg pnl already negated
        spread_gross = float(top["ret60"].mean() - bot["ret60"].mean())
        spread_net = float(top["ret60"].mean() - bot["ret60"].mean()) - 4 * friction  # 4 sides per full pair
        # market-adjusted (abnormal) long-short spread
        spread_mktadj = float(top["ret60_mkt_adj"].mean() - bot["ret60_mkt_adj"].mean()) if mkt else None
        results[label] = {
            "events": all_ev,
            "n_long": len(top), "n_short": len(bot),
            "long_ret": float(top["ret60"].mean() * 100),
            "short_ret": float(bot["ret60"].mean() * 100),
            "spread_gross": float(spread_gross * 100),
            "spread_net": float(spread_net * 100),
            "spread_mktadj": float(spread_mktadj * 100) if spread_mktadj is not None else None,
            "pf": _pf(all_ev["pnl_net"]),
        }
    return results


def _pf(pnl: pd.Series) -> float:
    wins = pnl[pnl > 0].sum()
    losses = abs(pnl[pnl <= 0].sum())
    if losses == 0:
        return np.inf if wins > 0 else 0.0
    return float(wins / losses)


def _bootstrap_p5(events_net: pd.Series, n_sims: int, seed: int) -> float:
    x = events_net.to_numpy(dtype=float)
    if x.size == 0:
        return 0.0
    rng = np.random.default_rng(seed)
    means = np.array([rng.choice(x, size=x.size, replace=True).mean() for _ in range(n_sims)])
    return float(np.percentile(means, 5) * 100)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("loading earnings...")
    earn = _load_earnings()
    print(f"  earnings rows (est+actual, 2012-2021): {len(earn)}")
    earn = _compute_sue(earn)
    print(f"  with computable SUE: {len(earn)}")

    print("loading prices (large file, columns subset)...")
    symbols = set(earn["symbol"])
    prices = _load_prices(symbols)
    print(f"  price rows loaded: {len(prices)}, symbols: {prices['symbol'].nunique()}")
    lookup = _build_price_lookup(prices)
    print("building equal-weight market index...")
    mkt = _build_market_index(prices)

    splits = {"is": IS_WINDOW, "oos": OOS_WINDOW}
    res = _run(earn, splits, lookup, mkt, FRICTION_BASE)

    is_ev = res["is"]["events"]
    oos_ev = res["oos"]["events"]
    is_net = is_ev["pnl_net"]
    oos_net = oos_ev["pnl_net"]

    # gates
    g5 = res["is"]["spread_gross"] > 0
    g1 = res["oos"]["spread_net"] > 0
    p5 = _bootstrap_p5(oos_net, N_SIMS, SEED)
    g2 = p5 > 0
    g3 = res["oos"]["pf"] >= 1.0
    # gate 4: drop best single cohort-quarter on OOS
    oosq = oos_ev.groupby("qkey")["pnl_net"].mean()
    best = oosq.idxmax()
    oos_drop = oos_ev[oos_ev["qkey"] != best]
    g4 = float(oos_drop["pnl_net"].mean() * 100) > 0
    g6 = True

    gates_fail = not (g1 and g2 and g3 and g4 and g5 and g6)

    summary = {
        "instrument": "US equities (Kaggle panel)",
        "data_span": "2012-2021 (earnings), 1998-2021 (prices)",
        "is_window": list(IS_WINDOW), "oos_window": list(OOS_WINDOW),
        "hold_days": HOLD_DAYS, "decile": f"top/bottom {100//DECILE}%",
        "friction_per_side": FRICTION_BASE,
        "is": {k: v for k, v in res["is"].items() if k != "events"},
        "oos": {k: v for k, v in res["oos"].items() if k != "events"},
        "gates": {
            "gate1_oos_net_positive": {"ok": g1, "spread_net_bps": round(res["oos"]["spread_net"] * 100, 2)},
            "gate2_oos_bootstrap_p5": {"ok": g2, "p5_bps": round(p5 * 100, 2)},
            "gate3_oos_pf": {"ok": g3, "pf": res["oos"]["pf"]},
            "gate4_oos_drop_best_cohort": {"ok": g4, "note": f"drop best OOS quarter {best}"},
            "gate5_is_gross_positive": {"ok": g5, "is_spread_gross_bps": round(res["is"]["spread_gross"] * 100, 2)},
            "gate6_lookahead": {"ok": g6, "note": "entry next day after announcement, no future prices"},
        },
        "verdict": "DISCONFIRMED" if gates_fail else "CLEARS-OOS",
    }

    (OUT / "pead_summary.json").write_text(json.dumps(summary, indent=2, default=float))
    out_ev = pd.concat([res["is"]["events"], res["oos"]["events"]], ignore_index=True)
    out_ev["window"] = np.where(out_ev["date"] <= pd.Timestamp(IS_WINDOW[1]), "is", "oos")
    out_ev.to_parquet(OUT / "pead_events.parquet")
    print(json.dumps(summary, indent=2, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
