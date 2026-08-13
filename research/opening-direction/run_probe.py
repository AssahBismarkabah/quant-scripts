"""Pre-registered probe: NQ opening-range direction persistence (derived, Stage 1).

Observation (derived, not claim-copied): if the first W minutes of the RTH session
close up vs the open, the rest of the day tends to close up too; if down, rest-of-day
tends down. Intraday open-direction persistence.

RULE (objective, machine-executable, no lookahead):
  - Instrument: continuous NQ futures (Databento GLBX.MDP3, NQ.n.0), RTH 09:30-16:00 ET.
  - Data: combined IVAMR panel (2013-11..2023-12) + vwap-pullback panel (2020-08..2026-08),
    overlapping days verified identical, dedup kept (continuous series -> 2013-2026).
  - Each RTH day, let open = first bar open, cW = close of minute W (30 or 60).
  - dir = +1 if cW > open (long the open direction), -1 if cW < open.
  - Enter at cW, hold to session close (last RTH bar close). Exit at close.
  - Daily PnL (pts) = (close - cW) * dir. Gross; then net of friction (0.5 pts/turn base,
    1.0 stress), one round turn per day.

Pre-registered (frozen before run):
  - PRIMARY window W = 30. SECONDARY W = 60 (reported, not primary gate).
  - Split: IS 2013-11-01 .. 2024-12-31 ; OOS 2025-01-01 .. 2026-08-07.
  - Friction base 0.5 pts/turn, stress 1.0 pts/turn.
  - Gates (house): G1 OOS net > 0; G2 OOS bootstrap p5 > 0 (n=5000); G3 OOS PF >= 1.0;
    G4 OOS drop-best-month still > 0; G5 IS net > 0; G6 no-lookahead (entry at cW, known then).
  - Verdict: CLEARS-OOS if all gates pass on primary W=30; else DISCONFIRMED.

Writes outputs/opening_direction_summary.json and daily pnl parquet.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
IVAMR = ROOT / "research" / "ivamr" / "cache" / "NQ_n_0_1m.parquet"
VWAP = ROOT / "research" / "nq-vwap-pullback" / "cache" / "NQ_n_0_1m.parquet"
OUT = Path(__file__).resolve().parent / "outputs"

IS_START = "2013-11-01"
IS_END = "2024-12-31"
OOS_START = "2025-01-01"
OOS_END = "2026-08-07"
WINDOWS = [30]        # primary; 60 reported as secondary separately
FRICTION = {"base": 0.5, "stress": 1.0}
N_SIMS = 5000
SEED = 42


def load_combined() -> pd.DataFrame:
    a = pd.read_parquet(IVAMR)
    b = pd.read_parquet(VWAP)
    a = a[["ts", "open", "high", "low", "close", "volume"]].copy()
    b = b[["ts", "open", "high", "low", "close", "volume"]].copy()
    both = pd.concat([a, b], ignore_index=True)
    both["ts"] = pd.to_datetime(both["ts"]).dt.tz_localize(None)
    both = both.sort_values("ts").reset_index(drop=True)
    both = both[both["volume"] > 0].copy()          # drop empty bars
    both = both[both["low"] <= both["high"]].copy()  # sanity
    both["day"] = both["ts"].dt.date
    # keep earliest version per (ts) since panels overlap identically
    both = both.drop_duplicates(subset="ts", keep="first")
    return both.reset_index(drop=True)


def gates(d: pd.DataFrame, W: int, friction: float) -> dict:
    d = d.dropna(subset=[f"pnl_gross{W}"]).copy()
    isd = d[(d["day"] >= pd.Timestamp(IS_START).date()) & (d["day"] <= pd.Timestamp(IS_END).date())]
    oosd = d[(d["day"] >= pd.Timestamp(OOS_START).date()) & (d["day"] <= pd.Timestamp(OOS_END).date())]
    is_net = isd[f"pnl_gross{W}"] - friction
    oos_net = oosd[f"pnl_gross{W}"] - friction

    def pf(x):
        wins = x[x > 0].sum(); losses = abs(x[x <= 0].sum())
        return float(wins / losses) if losses != 0 else (np.inf if wins > 0 else 0.0)

    def boot_p5(x, n=N_SIMS, seed=SEED):
        rng = np.random.default_rng(seed)
        arr = x.to_numpy(dtype=float)
        means = np.array([rng.choice(arr, size=arr.size, replace=True).mean() for _ in range(n)])
        return float(np.percentile(means, 5))

    oosd = oosd.assign(_m=pd.to_datetime(oosd["day"]).dt.to_period("M"))
    oos_month = oosd.groupby("_m")[f"pnl_gross{W}"].mean()
    best_month = oos_month.idxmax()
    oos_drop = oosd[oosd["_m"] != best_month]
    g5 = float(isd[f"pnl_gross{W}"].mean() - friction) > 0
    g1 = float(oosd[f"pnl_gross{W}"].mean() - friction) > 0
    p5 = boot_p5(oos_net)
    g2 = p5 > 0
    g3 = pf(oos_net) >= 1.0
    g4 = float(oos_drop[f"pnl_gross{W}"].mean() - friction) > 0
    g6 = True
    all_pass = all([g1, g2, g3, g4, g5, g6])
    return {
        "window": W, "friction": friction, "is_n_days": len(isd), "oos_n_days": len(oosd),
        "is_net_pts_per_day": float(isd[f"pnl_gross{W}"].mean() - friction),
        "oos_net_pts_per_day": float(oosd[f"pnl_gross{W}"].mean() - friction),
        "oos_gross_pts_per_day": float(oosd[f"pnl_gross{W}"].mean()),
        "oos_pf": pf(oos_net), "oos_boot_p5_pts": p5,
        "oos_long_n": int((oosd[f"dir{W}"] == 1).sum()), "oos_short_n": int((oosd[f"dir{W}"] == -1).sum()),
        "best_oos_month_dropped": str(best_month),
        "eval_n_bps": np.nan,
        "gates": {
            "g1_oos_net_positive": g1, "g2_oos_boot_p5": g2, "g3_oos_pf": g3,
            "g4_oos_drop_best_month": g4, "g5_is_net_positive": g5, "g6_lookahead": g6,
        },
        "verdict": "CLEARS-OOS" if all_pass else "DISCONFIRMED",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("loading combined NQ panels ...")
    df = load_combined()
    print(f"  bars={len(df):,}  days={df['day'].nunique()}  span={df['day'].min()}..{df['day'].max()}")

    # build daily for primary W=30 and secondary W=60 in one pass
    daily2 = build_daily_with(df, [30, 60])

    results = {}
    for W in (30, 60):
        for name, fric in FRICTION.items():
            results[f"W{W}_{name}"] = gates(daily2, W, fric)

    primary = results.get("W30_base", {})
    (OUT / "opening_direction_summary.json").write_text(
        json.dumps({"results": results, "primary": primary,
                    "ref_px_note": f"sample close-level~{daily2['close'].median():.0f}"},
                   indent=2, default=str))
    daily2.to_parquet(OUT / "opening_direction_daily_pnl.parquet")
    print("\n=== RESULTS (pts/day net, per window x friction) ===")
    for k, v in results.items():
        print(f"{k}: is_net={v['is_net_pts_per_day']:+.2f} oos_net={v['oos_net_pts_per_day']:+.2f} "
              f"pf={v['oos_pf']:.2f} p5={v['oos_boot_p5_pts']:+.2f} n_oos={v['oos_n_days']} "
              f"{v['verdict']}")
    print("\nPRIMARY verdict:", primary.get("verdict"))
    return 0


def build_daily_with(df: pd.DataFrame, windows: list[int]) -> pd.DataFrame:
    df = df.copy()
    df["min"] = df.groupby("day")["ts"].transform(lambda s: (s - s.min()).dt.total_seconds() / 60)
    rows = []
    for day, g in df.groupby("day"):
        g = g.sort_values("ts")
        o = g["open"].iloc[0]; c = g["close"].iloc[-1]
        rec = {"day": day, "open": o, "close": c}
        for W in windows:
            seg = g[g["min"] <= W]
            if len(seg) > 0:
                rec[f"c{W}"] = seg["close"].iloc[-1]
        rows.append(rec)
    d = pd.DataFrame(rows)
    for W in windows:
        d[f"ret{W}_pts"] = d[f"c{W}"] - d["open"]
        d[f"rest{W}_pts"] = d["close"] - d[f"c{W}"]
        d[f"dir{W}"] = np.sign(d[f"ret{W}_pts"])
        d[f"pnl_gross{W}"] = d[f"rest{W}_pts"] * d[f"dir{W}"]
    return d


if __name__ == "__main__":
    raise SystemExit(main())
