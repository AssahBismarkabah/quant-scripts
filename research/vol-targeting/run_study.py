"""Target volatility fund rebalancing flow fade - first-pass study.

Pre-registered parameters (IA/vol-targeting-research-spec.md, 2026-08-04):
  - vol window: 20d realized vol of SPY daily returns
  - vol target: 10% annualized; leverage cap 1.5x
  - AUM: $1.0T constant (signal direction is AUM-scale-invariant)
  - flow_t = exposure_t - exposure_{t-1}, known at close of day t
  - events: bottom decile of flow (IS-trained threshold)
  - entry: open of day t+1; hold 1/2/5 trading days
  - primary H1: fade - positive mean return after friction (fade)
  - friction: 4 bps round trip base, 12 bps stress
  - split sample: IS 2023-03-28..2024-12-31 | OOS 2025-01-01..2026-08-01

Runs: same-day diagnostic, event stats, split sample, bootstrap, drop-best,
random-day control, robustness grid (vol window / AUM / target / cap / friction).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SPY_BARS = Path(__file__).resolve().parent.parent / "index-rebalancing" / "cache" / "bars" / "SPY.parquet"

BASE = {
    "vol_window": 20,
    "target": 0.10,
    "cap": 1.5,
    "aum": 1.0e12,
    "decile": 0.10,
    "friction_base_bps": 4.0,
    "friction_stress_bps": 12.0,
    "n_sims": 10_000,
    "seed": 42,
}


def load_spy(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["ts_date"] = pd.to_datetime(df["ts_date"])
    df = df.sort_values("ts_date").reset_index(drop=True)
    df["ret"] = df["close"].pct_change()
    return df


def build_flows(df: pd.DataFrame, vol_window: int, target: float, cap: float, aum: float) -> pd.DataFrame:
    """Return a frame with forecast vol, exposure, flow, returns."""
    out = df.copy()
    out["vol"] = out["ret"].rolling(vol_window).std() * np.sqrt(252)
    out["exposure"] = np.minimum(cap, target / out["vol"]) * aum
    out["flow"] = out["exposure"].diff()
    out["fwd_open"] = out["open"].shift(-1)
    out["fwd_close"] = out["close"].shift(-1)
    out["hold1"] = out["fwd_close"] / out["fwd_open"] - 1
    out["hold2"] = out["close"].shift(-2) / out["fwd_open"] - 1
    out["hold5"] = out["close"].shift(-5) / out["fwd_open"] - 1
    return out


def mean_bps(x: pd.Series) -> float:
    return float(x.mean() * 1e4)


def report(df: pd.DataFrame, label: str) -> dict:
    n = len(df)
    out = {"label": label, "n_events": n}
    for h in ("hold1", "hold2", "hold5"):
        s = df[h].dropna()
        out[f"{h}_mean_bps"] = round(mean_bps(s), 2)
        out[f"{h}_tstat"] = round(float(s.mean() / (s.std() / np.sqrt(len(s)))), 2) if len(s) > 1 else None
    return out


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


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bars", default=str(SPY_BARS))
    p.add_argument("--out", default=None, help="write JSON report to this path")
    args = p.parse_args()

    df = load_spy(Path(args.bars))
    flows = build_flows(df, BASE["vol_window"], BASE["target"], BASE["cap"], BASE["aum"])
    flows = flows.dropna(subset=["flow", "hold1", "hold2", "hold5"]).reset_index(drop=True)

    # sanity: the two in-window vol episodes must appear as large sell-flow days
    top_sell = flows.nsmallest(8, "flow")[["ts_date", "ret", "vol", "flow"]]
    print("=== largest sell-flow days (sanity) ===")
    print(top_sell.to_string(index=False, float_format=lambda v: f"{v:,.0f}"))

    # same-day diagnostic: flows must coincide with down days
    diag = np.corrcoef(flows["flow"], flows["ret"])[0, 1]
    print(f"\n=== same-day diagnostic ===\ncorr(flow, ret): {diag:.4f}")

    # IS-trained bottom-decile threshold (freeze before OOS)
    is_mask = flows["ts_date"] <= pd.Timestamp("2024-12-31")
    oos_mask = flows["ts_date"] >= pd.Timestamp("2025-01-01")
    threshold = flows.loc[is_mask, "flow"].quantile(BASE["decile"])
    print(f"\n=== threshold ===\nIS bottom-decile flow: {threshold:,.0f} USD (n IS={int(is_mask.sum())}, n OOS={int(oos_mask.sum())})")

    events = flows[flows["flow"] < threshold]
    print("\n=== fade events (flow < threshold) ===")
    for lbl, m in (("IS", is_mask), ("OOS", oos_mask), ("ALL", pd.Series(True, index=flows.index))):
        sub = events[m]
        if sub.empty:
            print(f"{lbl}: n=0")
            continue
        r = report(sub, lbl)
        print(json.dumps(r))

    # friction + controls on the primary cell (hold1, all events)
    ev_all = events
    primary = ev_all["hold1"].dropna()
    rng = np.random.default_rng(BASE["seed"])
    control = pd.Series(rng.choice(flows["hold1"].dropna().to_numpy(), size=len(primary), replace=False))
    drop_best = primary.drop(primary.idxmax()) if len(primary) > 1 else primary
    print("\n=== controls (hold1, all events) ===")
    print("raw mean bps:", round(mean_bps(primary), 2))
    print("net base  (4bps):", round(mean_bps(primary) - BASE["friction_base_bps"], 2))
    print("net stress (12bps):", round(mean_bps(primary) - BASE["friction_stress_bps"], 2))
    print("drop-best mean bps:", round(mean_bps(drop_best), 2))
    print("random-day control mean bps:", round(mean_bps(control), 2))
    print("bootstrap:", json.dumps(bootstrap(primary, BASE["n_sims"], BASE["seed"])))
    print("bootstrap (drop-best):", json.dumps(bootstrap(drop_best, BASE["n_sims"], BASE["seed"])))

    # split-sample direction on primary cell
    ev_is = events[is_mask]["hold1"].dropna()
    ev_oos = events[oos_mask]["hold1"].dropna()
    print("\n=== split sample (hold1) ===")
    print("IS mean bps:", round(mean_bps(ev_is), 2), "n:", len(ev_is))
    print("OOS mean bps:", round(mean_bps(ev_oos), 2), "n:", len(ev_oos))

    # robustness grid: vol window / AUM / target / cap / friction on primary cell
    print("\n=== robustness (hold1 mean bps, all events) ===")
    grid = []
    for vw in (10, 60):
        for aum in (0.5e12, 2.0e12):
            for tgt in (0.08, 0.12):
                for cap in (1.0, 2.0):
                    f2 = build_flows(df, vw, tgt, cap, aum).dropna(subset=["flow", "hold1"])
                    th = f2.loc[f2["ts_date"] <= pd.Timestamp("2024-12-31"), "flow"].quantile(BASE["decile"])
                    m = mean_bps(f2.loc[f2["flow"] < th, "hold1"])
                    grid.append({"vw": vw, "aum": aum, "tgt": tgt, "cap": cap, "hold1_mean_bps": round(m, 2)})
    g = pd.DataFrame(grid)
    print(g.to_string(index=False))
    print("positive cells:", int((g["hold1_mean_bps"] > 0).sum()), "of", len(g))

    result = {
        "params": BASE,
        "n_flow_days": len(flows),
        "n_events": len(events),
        "same_day_corr": diag,
        "threshold_usd": threshold,
        "primary_hold1": {
            "raw_bps": round(mean_bps(primary), 2),
            "net_base_bps": round(mean_bps(primary) - BASE["friction_base_bps"], 2),
            "net_stress_bps": round(mean_bps(primary) - BASE["friction_stress_bps"], 2),
            "drop_best_bps": round(mean_bps(drop_best), 2),
            "control_bps": round(mean_bps(control), 2),
            "bootstrap": bootstrap(primary, BASE["n_sims"], BASE["seed"]),
        },
        "split": {
            "IS_bps": round(mean_bps(ev_is), 2),
            "OOS_bps": round(mean_bps(ev_oos), 2),
            "IS_n": len(ev_is),
            "OOS_n": len(ev_oos),
        },
    }
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2))
        print("\nreport written:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
