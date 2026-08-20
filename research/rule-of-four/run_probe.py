"""Probe #24 alpha run: Rule of Four (frozen protocol).

Pre-registered method (frozen in research-specs/rule-of-four-probe24-spec.md):

  For each event day x market (DAX, FTSE):
    T = release time in exchange-local time (Europe/Berlin for DAX,
        Europe/London for FTSE), via IANA zoneinfo conversion.
    C1..C4 = four 5-min candles starting at T; H4=max(high), L4=min(low).
    Entry: C5 = [T+20, T+25). Close > H4 -> long at C5 close; close < L4 ->
           short at C5 close. Only C5 may trigger (primary). V2 variant:
           any of C5..C12 (60-min window) may trigger.
    Stop: long -> L4, short -> H4 (no buffer).
    Targets: TP at 1:1, 1:2, 1:3 x risk; primary = 1:2.
    Time exit: +120 min after entry (T+140 absolute). No overnight.
    Friction (frozen, brutal): 4 pts round-trip GER30, 3 pts UK100.
    One trade per event per market; 1 unit flat.

  Gates (frozen): per market then pooled.
    G1 >=30 IS events/market (long+short combined).
    G2 IS net ROI > 0 at 1:2, n>=30 (per market).
    G3 gross win rate at 1:2 > breakeven 1/(1+R_avg) net.
    G4 IS net ROI > 0 in both halves at 1:2.
    G5 OOS net ROI > 0, n>=30 (per market).

  Verdict: CERTIFIED (all gates) / DEAD (any of G2-G5 fail) / UNVERIFIABLE.

Run: python3 research/rule-of-four/run_probe.py
Writes outputs/rule_of_four_summary.json and outputs/rule_of_four_trades.parquet.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

IS_START = "2010-01-01"
IS_END = "2017-12-31"
OOS_START = "2018-01-01"
OOS_END = "2025-12-31"
FRICTION = {"dax": 4.0, "ftse": 3.0}
TARGETS = (1.0, 2.0, 3.0)  # multiples of risk; primary = 2.0
TARGET_PRIMARY = 2.0
TIME_EXIT_MIN = 120  # after entry
V2_MAX_C = 12  # V2 trigger window C5..C12 (60 min)

SEED = 42
N_SIMS = 5000


def load_events() -> pd.DataFrame:
    frames = []
    for fname in ("fomc.csv", "nfp.csv"):
        frames.append(pd.read_csv(ROOT / "events" / fname))
    return pd.concat(frames, ignore_index=True)


def load_bars(market: str) -> pd.DataFrame:
    d = DATA / market
    frames = [pd.read_parquet(p) for p in sorted(d.glob("*.parquet"))]
    df = pd.concat(frames, ignore_index=True)
    df["ts"] = pd.to_datetime(df["ts"]).dt.tz_localize(None)
    df["event_time_exch"] = pd.to_datetime(df["event_time_exch"])
    return df


def per_event_data(df: pd.DataFrame, market: str) -> pd.DataFrame:
    """Assemble per-event rows: C1..C5 OHLC, ranges, and trigger close."""
    out = []
    for (edate, etype, etime), g in df.groupby(["event_date", "event_type", "event_time_exch"]):
        t0 = pd.Timestamp(etime)
        g = g.sort_values("ts")
        def bars(start_min, end_min):
            s = t0 + pd.Timedelta(minutes=start_min)
            e = t0 + pd.Timedelta(minutes=end_min)
            return g[(g["ts"] >= s) & (g["ts"] < e)]
        c = {}
        for i in range(1, 13):
            b = bars((i - 1) * 5, i * 5)
            if len(b) == 0:
                continue
            c[i] = b.iloc[0]
        if 1 not in c or 2 not in c or 3 not in c or 4 not in c:
            continue  # need C1..C4 for the range; no trade possible
        h4 = max(c[i]["high"] for i in (1, 2, 3, 4))
        l4 = min(c[i]["low"] for i in (1, 2, 3, 4))
        risk = h4 - l4
        rec = {
            "event_date": edate, "type": etype, "t0": t0,
            "h4": h4, "l4": l4, "risk": risk,
        }
        # primary trigger: C5 close vs range
        if 5 in c:
            rec["c5_close"] = c[5]["close"]
            rec["c5_high"] = c[5]["high"]
            rec["c5_low"] = c[5]["low"]
            if c[5]["close"] > h4:
                rec["dir"] = 1
                rec["entry"] = c[5]["close"]
            elif c[5]["close"] < l4:
                rec["dir"] = -1
                rec["entry"] = c[5]["close"]
            else:
                rec["dir"] = 0
                rec["entry"] = np.nan
        else:
            rec["c5_close"] = np.nan
            rec["c5_high"] = np.nan
            rec["c5_low"] = np.nan
            rec["dir"] = 0
            rec["entry"] = np.nan
        # V2 trigger: any C5..C12 close beyond range
        v2_dir, v2_entry = 0, np.nan
        for i in range(5, V2_MAX_C + 1):
            if i in c:
                if v2_dir == 0 and c[i]["close"] > h4:
                    v2_dir, v2_entry = 1, c[i]["close"]
                    break
                if v2_dir == 0 and c[i]["close"] < l4:
                    v2_dir, v2_entry = -1, c[i]["close"]
                    break
        rec["v2_dir"] = v2_dir
        rec["v2_entry"] = v2_entry
        out.append(rec)
    return pd.DataFrame(out)


def simulate(event: pd.Series, variant: str, target_mult: float, friction: float, df: pd.DataFrame) -> dict:
    """Run the exit logic for one event given an entry price/direction."""
    if variant == "v2":
        dirn = int(event["v2_dir"])
        entry = float(event["v2_entry"])
        entry_min_off = None  # set below from actual trigger bar
    else:
        dirn = int(event["dir"])
        entry = float(event["entry"])
        entry_min_off = 20  # C5 starts at T+20
    if dirn == 0 or pd.isna(entry):
        return None
    h4, l4 = event["h4"], event["l4"]
    risk = event["risk"]
    stop = l4 if dirn == 1 else h4
    tp = entry + dirn * target_mult * risk

    # find the trigger bar for v2 (first C5..C12 with a close beyond range)
    if variant == "v2":
        g = df[(df["event_date"] == event["event_date"])]
        for i in range(5, V2_MAX_C + 1):
            s = event["t0"] + pd.Timedelta(minutes=(i - 1) * 5)
            e = event["t0"] + pd.Timedelta(minutes=i * 5)
            b = g[(g["ts"] >= s) & (g["ts"] < e)]
            if len(b) == 0:
                continue
            c = b.iloc[0]["close"]
            if (dirn == 1 and c > h4) or (dirn == -1 and c < l4):
                entry_min_off = (i - 1) * 5  # start of trigger bar
                break
        if entry_min_off is None:
            return None
    else:
        g = df[(df["event_date"] == event["event_date"])]

    t_entry = event["t0"] + pd.Timedelta(minutes=entry_min_off)
    t_exit = t_entry + pd.Timedelta(minutes=TIME_EXIT_MIN)
    g = g[(g["ts"] >= t_entry)]
    if g.empty:
        return None
    px = None
    for _, b in g.iterrows():
        if b["ts"] >= t_exit:
            px = b["open"]
            break
        if dirn == 1:
            if b["high"] >= tp:
                px = tp
                break
            if b["low"] <= stop:
                px = stop
                break
        else:
            if b["low"] <= tp:
                px = tp
                break
            if b["high"] >= stop:
                px = stop
                break
        px = b["close"]  # candle close as fallback each bar
    if px is None:
        px = g.iloc[-1]["close"]
    gross = (px - entry) * dirn
    net = gross - friction
    return {"dir": dirn, "entry": entry, "exit": px, "gross": gross, "net": net,
            "risk": risk, "target": tp, "stop": stop, "variant": variant,
            "target_mult": target_mult}


def compute(events: pd.DataFrame, df: pd.DataFrame, market: str) -> pd.DataFrame:
    friction = FRICTION[market]
    rows = []
    for _, e in events.iterrows():
        for target_mult in TARGETS:
            for variant in ("primary", "v2"):
                res = simulate(e, variant, target_mult, friction, df)
                if res is None:
                    continue
                rows.append({**e.to_dict(), **res})
    return pd.DataFrame(rows)


def boot_p5(x, n=N_SIMS, seed=SEED):
    rng = np.random.default_rng(seed)
    arr = np.asarray(x, dtype=float)
    means = np.array([rng.choice(arr, size=arr.size, replace=True).mean() for _ in range(n)])
    return float(np.percentile(means, 5))


def gate_report(trades: pd.DataFrame, market: str, variant: str = "primary") -> dict:
    friction = FRICTION[market]
    trades = trades[(trades["target_mult"] == TARGET_PRIMARY) & (trades["variant"] == variant)].copy()
    if trades.empty:
        return {"market": market, "variant": variant, "is_n": 0, "oos_n": 0,
                "is_net_roi_pts": np.nan, "oos_net_roi_pts": np.nan,
                "gates": {"g1_existence": False, "g2_realization": False,
                          "g3_breakeven": False, "g4_persistence": False,
                          "g5_oos": False},
                "all_pass": False, "verdict": "UNVERIFIABLE"}
    trades["day"] = pd.to_datetime(trades["event_date"])
    isd = trades[(trades["day"] >= pd.Timestamp(IS_START)) & (trades["day"] <= pd.Timestamp(IS_END))]
    oosd = trades[(trades["day"] >= pd.Timestamp(OOS_START)) & (trades["day"] <= pd.Timestamp(OOS_END))]
    is_net = isd["net"]
    oos_net = oosd["net"]
    is_half = len(isd) // 2
    is_first = isd.iloc[:is_half]["net"]
    is_second = isd.iloc[is_half:]["net"]

    def wr(x):
        return float((x > 0).mean()) if len(x) else np.nan

    r_avg = float((is_net.abs() / isd["risk"]).mean()) if len(is_net) else np.nan
    r = {
        "market": market, "variant": variant,
        "is_n": int(len(isd)), "oos_n": int(len(oosd)),
        "is_net_roi_pts": float(is_net.mean()) if len(is_net) else np.nan,
        "oos_net_roi_pts": float(oos_net.mean()) if len(oos_net) else np.nan,
        "is_win_rate": wr(is_net),
        "is_avg_r": r_avg,
        "oos_win_rate": wr(oos_net),
        "is_first_half": float(is_first.mean()) if len(is_first) else np.nan,
        "is_second_half": float(is_second.mean()) if len(is_second) else np.nan,
        "is_long": int((isd["dir"] == 1).sum()), "is_short": int((isd["dir"] == -1).sum()),
        "oos_long": int((oosd["dir"] == 1).sum()), "oos_short": int((oosd["dir"] == -1).sum()),
        "friction": friction,
    }
    g1 = len(isd) >= 30
    g2 = r["is_net_roi_pts"] > 0 and len(isd) >= 30
    be = 1.0 / (1.0 + r_avg) if r_avg and r_avg > 0 else 1.0
    g3 = wr(is_net) > be and len(isd) >= 30
    g4 = (r["is_first_half"] > 0 and r["is_second_half"] > 0) and len(isd) >= 30
    g5 = r["oos_net_roi_pts"] > 0 and len(oosd) >= 30
    r["gates"] = {"g1_existence": g1, "g2_realization": g2, "g3_breakeven": g3,
                  "g4_persistence": g4, "g5_oos": g5}
    r["all_pass"] = all(r["gates"].values())
    r["verdict"] = "CERTIFIED" if r["all_pass"] else ("DEAD" if g1 else "UNVERIFIABLE")
    return r


def main() -> int:
    events = load_events()
    summary = {"markets": {}, "pooled": {}}
    all_trades = []
    for market in ("dax", "ftse"):
        print(f"=== {market.upper()} ===", flush=True)
        bars = load_bars(market)
        ev = per_event_data(bars, market)
        print(f"  events with C1..C4: {len(ev)}", flush=True)
        trades = compute(ev, bars, market)
        print(f"  trades (primary+v2): {len(trades)}", flush=True)
        for variant in ("primary", "v2"):
            rep = gate_report(trades, market, variant)
            summary["markets"].setdefault(market, {})[variant] = rep
            print(f"  [{variant}] {rep['verdict']}: IS n={rep['is_n']} "
                  f"net={rep['is_net_roi_pts']:+.2f} | OOS n={rep['oos_n']} "
                  f"net={rep['oos_net_roi_pts']:+.2f}", flush=True)
        all_trades.append(trades)

    allt = pd.concat(all_trades, ignore_index=True)
    allt.to_parquet(OUT / "rule_of_four_trades.parquet")
    for variant in ("primary", "v2"):
        t = allt[(allt["target_mult"] == TARGET_PRIMARY) & (allt["variant"] == variant)].copy()
        t["net_r"] = t["net"] / t["risk"]
        t["day"] = pd.to_datetime(t["event_date"])
        isd = t[(t["day"] >= pd.Timestamp(IS_START)) & (t["day"] <= pd.Timestamp(IS_END))]
        oosd = t[(t["day"] >= pd.Timestamp(OOS_START)) & (t["day"] <= pd.Timestamp(OOS_END))]
        ih = len(isd) // 2
        pooled = {
            "variant": variant,
            "is_n": int(len(isd)), "oos_n": int(len(oosd)),
            "is_net_roi_r": float(isd["net_r"].mean()) if len(isd) else np.nan,
            "oos_net_roi_r": float(oosd["net_r"].mean()) if len(oosd) else np.nan,
            "is_first_half_r": float(isd.iloc[:ih]["net_r"].mean()) if len(isd) else np.nan,
            "is_second_half_r": float(isd.iloc[ih:]["net_r"].mean()) if len(isd) else np.nan,
            "is_win_rate": float((isd["net"] > 0).mean()) if len(isd) else np.nan,
            "oos_win_rate": float((oosd["net"] > 0).mean()) if len(oosd) else np.nan,
        }
        be = 1.0 / (1.0 + pooled["is_net_roi_r"]) if pooled["is_net_roi_r"] and pooled["is_net_roi_r"] > 0 else 1.0
        gates = {
            "g1": len(isd) >= 30,
            "g2": pooled["is_net_roi_r"] > 0 and len(isd) >= 30,
            "g3": pooled["is_win_rate"] > be and len(isd) >= 30,
            "g4": pooled["is_first_half_r"] > 0 and pooled["is_second_half_r"] > 0 and len(isd) >= 30,
            "g5": pooled["oos_net_roi_r"] > 0 and len(oosd) >= 30,
        }
        pooled["gates"] = gates
        pooled["all_pass"] = all(gates.values())
        pooled["verdict"] = "CERTIFIED" if pooled["all_pass"] else ("DEAD" if gates["g1"] else "UNVERIFIABLE")
        summary["pooled"][variant] = pooled
        print(f"=== POOLED [{variant}] === {pooled['verdict']}: "
              f"IS n={pooled['is_n']} netR={pooled['is_net_roi_r']:+.3f} | "
              f"OOS n={pooled['oos_n']} netR={pooled['oos_net_roi_r']:+.3f}")
    (OUT / "rule_of_four_summary.json").write_text(
        json.dumps(summary, indent=2, default=str))
    print("saved outputs/rule_of_four_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())