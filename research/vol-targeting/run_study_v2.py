"""Target volatility flow fade - version 2 study (revisit).

Pre-registered in IA/vol-targeting-revisit-research-spec.md (v2.0, 2026-08-04).
Data: SPY_clean.parquet (Yahoo OHLC verified against FRED SP500; the cached
Databento bars were found corrupted on 35/839 days) + FRED VIXCLS.

Co-base cells (BOTH must pass - joint gate, no selection):
  Cell A (realized): exposure_t = min(cap, target / sigma60_t) * AUM
                     sigma60 = 60-day realized vol of SPY
  Cell B (implied):  exposure_t = min(cap, target / VIX_t) * AUM, VIX decimal

Base parameters (frozen): target 10%, cap 2.0x, AUM $1.0T constant,
bottom-decile flow threshold trained in-sample (IS <= 2024-12-31).
Entry: open of day t+1 after a bottom-decile sell-flow day t.
Primary horizon: 5 trading days (3 and 10 in the robustness grid).
H1: mean hold5 return > 0 after base friction (4 bps RT) in BOTH cells.
H2 (continuation) reported, not a fallback.
Friction: 4 bps RT base, 12 bps RT stress. Stop loss: -2% from entry (reported).

Gates (reject if ANY fails in EITHER cell): same-day diagnostic corr(flow,ret)>0;
episode check (Aug 5 2024 AND Apr 4 2025 in bottom decile of flow); H1 after base
friction; split sample same sign in both halves; bootstrap p5 > 0; drop-best
survives; events beat random-day control; result survives entry at t+1 close;
result does not depend on a single episode.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

CACHE = Path(__file__).resolve().parent / "cache"
BARS = CACHE / "SPY_clean.parquet"
VIXCSV = CACHE / "VIXCLS.csv"

BASE = {
    "target": 0.10,
    "cap": 2.0,
    "aum": 1.0e12,
    "decile": 0.10,
    "friction_base_bps": 4.0,
    "friction_stress_bps": 12.0,
    "n_sims": 10_000,
    "seed": 42,
    "horizon": 5,
}
IS_END = pd.Timestamp("2024-12-31")
EPISODE_DAYS = [pd.Timestamp("2024-08-05"), pd.Timestamp("2025-04-04")]
EPISODE_WINDOWS = [
    (pd.Timestamp("2024-08-02"), pd.Timestamp("2024-08-09")),   # Aug 2024 +-2 sessions
    (pd.Timestamp("2025-04-02"), pd.Timestamp("2025-04-09")),   # Apr 2025 +-2 sessions
]


def load_bars(path: Path | None = None) -> pd.DataFrame:
    df = pd.read_parquet(path or BARS)
    df["ts_date"] = pd.to_datetime(df["ts_date"])
    df = df.sort_values("ts_date").reset_index(drop=True)
    df["ret"] = df["close"].pct_change()
    return df


def load_vix() -> pd.Series:
    v = pd.read_csv(VIXCSV)
    v.columns = ["ts_date", "vix"]
    v["ts_date"] = pd.to_datetime(v["ts_date"])
    return v.set_index("ts_date")["vix"]


def ewma_vol(returns: pd.Series, lam: float = 0.94, warmup: int = 30) -> pd.Series:
    """RiskMetrics-style EWMA variance of daily returns, annualized."""
    r = returns.fillna(0.0).to_numpy()
    var = np.full(len(r), np.nan)
    v = np.var(r[:warmup])
    var[warmup - 1] = v
    for i in range(warmup, len(r)):
        v = lam * v + (1 - lam) * r[i] ** 2
        var[i] = v
    return pd.Series(np.sqrt(var) * np.sqrt(252), index=returns.index)


def build_cell(df: pd.DataFrame, vix: pd.Series, kind: str, target: float,
               cap: float, aum: float, window: int | None = None) -> pd.DataFrame:
    """Build exposure/flow/forward-return frame for one cell."""
    out = df.copy()
    if kind == "rv":
        out["vol"] = out["ret"].rolling(window).std() * np.sqrt(252)
    elif kind == "ewma":
        out["vol"] = ewma_vol(out["ret"])
    else:  # vix
        v = vix.reindex(out["ts_date"])
        if v.isna().any():
            raise ValueError(f"VIX missing on {int(v.isna().sum())} SPY sessions")
        out["vol"] = (v / 100.0).to_numpy()
    out["exposure"] = np.minimum(cap, target / out["vol"]) * aum
    out["flow"] = out["exposure"].diff()
    out["entry_open"] = out["open"].shift(-1)
    out["entry_close"] = out["close"].shift(-1)
    for h in (3, 5, 10):
        out[f"hold{h}"] = out["close"].shift(-h) / out["entry_open"] - 1
        out[f"ce_hold{h}"] = out["close"].shift(-h) / out["entry_close"] - 1  # t+1 close entry
    out["hold5_stop"] = _stop_adjusted(out, stop=0.02)
    return out


def _stop_adjusted(out: pd.DataFrame, stop: float) -> pd.Series:
    """Exit at first close at or below entry_open*(1-stop) within 5 sessions."""
    closes = out["close"].to_numpy()
    entry = out["entry_open"].to_numpy()
    n = len(out)
    res = np.full(n, np.nan)
    for i in range(n - 1):
        e = entry[i]
        if not np.isfinite(e):
            continue
        limit = e * (1 - stop)
        hit = None
        for j in range(i + 1, min(i + 6, n)):
            if closes[j] <= limit:
                hit = j
                break
        end = (i + 5) if (i + 5) < n else n - 1
        res[i] = (closes[hit if hit is not None else end] / e) - 1
    return pd.Series(res, index=out.index)


def mean_bps(x: pd.Series) -> float:
    return float(x.mean() * 1e4)


def tstat(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 2:
        return float("nan")
    return float(x.mean() / (x.std() / np.sqrt(len(x))))


def bootstrap(returns: pd.Series, n_sims: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    r = returns.dropna().to_numpy()
    if len(r) == 0:
        return {"p5_bps": None, "p95_bps": None, "p_negative": None}
    means = np.empty(n_sims)
    for i in range(n_sims):
        means[i] = rng.choice(r, size=len(r), replace=True).mean()
    return {
        "p5_bps": round(float(np.percentile(means, 5) * 1e4), 2),
        "p95_bps": round(float(np.percentile(means, 95) * 1e4), 2),
        "p_negative": round(float((means < 0).mean()), 4),
    }


def evaluate_cell(df: pd.DataFrame, label: str, horizon: int = 5) -> dict:
    """Full pre-registered evaluation for one cell. Returns results + gate flags."""
    h = f"hold{horizon}"
    is_mask = df["ts_date"] <= IS_END
    threshold = df.loc[is_mask, "flow"].quantile(BASE["decile"])
    events = df[df["flow"] < threshold].dropna(subset=[h]).reset_index(drop=True)

    rng = np.random.default_rng(BASE["seed"])
    all_h = df[h].dropna().to_numpy()
    control = pd.Series(rng.choice(all_h, size=len(events), replace=False))

    # episode check: flow percentile ranks + bottom-decile membership
    pct = df["flow"].rank(pct=True)
    episodes = {}
    for d in EPISODE_DAYS:
        row = df[df["ts_date"] == d]
        if row.empty:
            episodes[str(d.date())] = None
            continue
        r = row.iloc[0]
        episodes[str(d.date())] = {
            "flow_bn": round(r["flow"] / 1e9, 1),
            "ret_pct": round(r["ret"] * 100, 2),
            "pct_rank": round(pct.loc[r.name], 3),
            "in_bottom_decile": bool(r["flow"] < threshold),
        }

    # single-episode dependence: drop events inside episode windows
    keep = ~events["ts_date"].apply(lambda d: any(a <= d <= b for a, b in EPISODE_WINDOWS))
    no_ep = events[keep][h]

    split_is = events[events["ts_date"] <= IS_END][h]
    split_oos = events[events["ts_date"] > IS_END][h]

    res = {
        "cell": label,
        "n_events": int(len(events)),
        "n_events_is": int(len(split_is)),
        "n_events_oos": int(len(split_oos)),
        "threshold_bn": round(threshold / 1e9, 1),
        "same_day_corr": round(float(np.corrcoef(df["flow"], df["ret"])[0, 1]), 4),
        "episodes": episodes,
        "primary_hold5": {
            "raw_bps": round(mean_bps(events[h]), 2),
            "net_base_bps": round(mean_bps(events[h]) - BASE["friction_base_bps"], 2),
            "net_stress_bps": round(mean_bps(events[h]) - BASE["friction_stress_bps"], 2),
            "tstat": round(tstat(events[h]), 2),
            "stop_bps": round(mean_bps(events["hold5_stop"].dropna()), 2),
            "bootstrap": bootstrap(events[h], BASE["n_sims"], BASE["seed"]),
            "drop_best_bps": round(mean_bps(events[h].drop(events[h].idxmax())), 2),
            "control_bps": round(mean_bps(control), 2),
            "no_aug2024_bps": round(mean_bps(no_ep), 2),
        },
        "split": {
            "IS_bps": round(mean_bps(split_is), 2),
            "OOS_bps": round(mean_bps(split_oos), 2),
        },
        "horizons": {str(hh): round(mean_bps(events[f"hold{hh}"]), 2) for hh in (3, 5, 10)},
        "close_entry": {str(hh): round(mean_bps(events[f"ce_hold{hh}"]), 2) for hh in (3, 5, 10)},
        "top_sell_flow": [
            {"date": str(r.ts_date.date()), "flow_bn": round(r.flow / 1e9, 1), "ret_pct": round(r.ret * 100, 2)}
            for r in df.nsmallest(8, "flow").itertuples()
        ],
    }
    # gates
    g = {}
    g["same_day"] = res["same_day_corr"] > 0
    g["episode"] = all(v is not None and v["in_bottom_decile"] for v in episodes.values())
    g["h1_base_friction"] = res["primary_hold5"]["net_base_bps"] > 0
    g["split_same_sign"] = (res["split"]["IS_bps"] > 0) == (res["split"]["OOS_bps"] > 0)
    g["bootstrap_p5"] = res["primary_hold5"]["bootstrap"]["p5_bps"] > 0
    g["drop_best"] = res["primary_hold5"]["drop_best_bps"] > 0
    g["beats_random"] = res["primary_hold5"]["raw_bps"] > res["primary_hold5"]["control_bps"]
    g["close_entry"] = res["close_entry"]["5"] > 0
    g["single_episode"] = res["primary_hold5"]["no_aug2024_bps"] > 0
    res["gates"] = g
    res["gates_pass"] = all(g.values())
    return res


def robustness(df: pd.DataFrame, vix: pd.Series) -> pd.DataFrame:
    """Grid (reported, not selected). Returns hold means per cell config."""
    rows = []
    # Cell A: vol windows
    for kind, window in (("rv", 30), ("rv", 120), ("ewma", None)):
        for aum in (0.5e12, 2.0e12):
            for tgt in (0.08, 0.12):
                for cap in (1.5, 2.5):
                    f = build_cell(df, vix, kind, tgt, cap, aum, window)
                    f = f.dropna(subset=["flow"])
                    th = f.loc[f["ts_date"] <= IS_END, "flow"].quantile(BASE["decile"])
                    ev = f[f["flow"] < th]
                    rows.append({
                        "cell": "A", "kind": kind, "window": window, "aum": aum,
                        "tgt": tgt, "cap": cap,
                        "h3": round(mean_bps(ev["hold3"]), 2),
                        "h5": round(mean_bps(ev["hold5"]), 2),
                        "h10": round(mean_bps(ev["hold10"]), 2),
                        "n": int(len(ev)),
                    })
    # Cell B: caps
    for cap in (1.5, 2.5, float("inf")):
        for aum in (0.5e12, 2.0e12):
            for tgt in (0.08, 0.12):
                f = build_cell(df, vix, "vix", tgt, cap, aum)
                f = f.dropna(subset=["flow"])
                th = f.loc[f["ts_date"] <= IS_END, "flow"].quantile(BASE["decile"])
                ev = f[f["flow"] < th]
                rows.append({
                    "cell": "B", "kind": "vix", "window": None, "aum": aum,
                    "tgt": tgt, "cap": cap,
                    "h3": round(mean_bps(ev["hold3"]), 2),
                    "h5": round(mean_bps(ev["hold5"]), 2),
                    "h10": round(mean_bps(ev["hold10"]), 2),
                    "n": int(len(ev)),
                })
    return pd.DataFrame(rows)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bars", default=str(BARS))
    p.add_argument("--out", default=None)
    args = p.parse_args()

    df = load_bars(args.bars and Path(args.bars))
    vix = load_vix()

    cell_a = build_cell(df, vix, "rv", BASE["target"], BASE["cap"], BASE["aum"], window=60)
    cell_b = build_cell(df, vix, "vix", BASE["target"], BASE["cap"], BASE["aum"])
    cell_a = cell_a.dropna(subset=["flow"])
    cell_b = cell_b.dropna(subset=["flow"])

    res_a = evaluate_cell(cell_a, "A (60d RV)")
    res_b = evaluate_cell(cell_b, "B (VIX close)")

    print(json.dumps(res_a, indent=2, default=str))
    print(json.dumps(res_b, indent=2, default=str))

    grid = robustness(df, vix)
    pos5 = grid[grid["h5"] > 0]
    pos3 = grid[grid["h3"] > 0]
    pos10 = grid[grid["h10"] > 0]
    print(f"\nrobustness grid: {len(grid)} cells | h5 positive {len(pos5)} | h3 positive {len(pos3)} | h10 positive {len(pos10)}")
    print(grid.to_string(index=False))

    joint_pass = res_a["gates_pass"] and res_b["gates_pass"]
    print(f"\n=== JOINT GATE (both cells must pass) ===\nCell A: {res_a['gates_pass']} | Cell B: {res_b['gates_pass']} | JOINT: {joint_pass}")
    if not joint_pass:
        for lbl, r in (("A", res_a), ("B", res_b)):
            failed = [k for k, v in r["gates"].items() if not v]
            print(f"  {lbl} failed gates: {failed}")

    result = {"params": BASE, "cell_a": res_a, "cell_b": res_b, "joint_pass": joint_pass,
              "robustness": grid.to_dict("records")}
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2, default=str))
        print("\nreport written:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
