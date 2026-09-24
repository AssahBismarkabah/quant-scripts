"""Step 10: post-migration retention study (Addendum P final test).

Population: graduates whose pool retains > 10% of its running peak
liquidity at t+60m (survivors; excludes the instant-grad lottery class).
Entry: first 1-min bar at or after t+60m. Exit: identical naive engine
on the bars slice. Fixed 8-split family (pre-registered in Addendum P).
Stats per split at the optimistic tier (0.5% slip, 0.02 fail) and the
mildest realistic tier (1% slip, 0.05 fail); regime split at mildest.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np

from quant_scripts.meme_launch_filter.step3_sim import (
    BASE, FEE, NOTIONAL_SOL, TP_FRAC, TP_GAIN, ATR_WINDOW, ATR_MULT,
    FILL_CAP, REGIME_SPLIT, load_day, pooled_stats,
)
from quant_scripts.meme_launch_filter.step6_cost_sensitivity import (
    FAILED_TX_COSTS, SLIPPAGES,
)

ENTRY_DELAY_S = 3600
SURVIVE_FRAC = 0.10
OPTIMISTIC = (0.005, 0.02)
MILDEST = (0.01, 0.05)
COMBOS = [OPTIMISTIC, MILDEST]


def to_epoch(s: str) -> float:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f %Z").replace(tzinfo=timezone.utc).timestamp()


def simulate_slice(bars: list[dict], slippage: float, failed_tx_cost: float) -> dict | None:
    if not bars:
        return None
    first = bars[0]
    entry = first["open"] * (1.0 + slippage)
    if entry <= 0:
        return None
    tokens = NOTIONAL_SOL * (1.0 - FEE) / entry
    proceeds = 0.0
    had_tp = False
    reason = "time_stop"
    peak = first["open"]
    trs: list[float] = []
    prev_close = first["open"]
    n = len(bars)
    for i, bar in enumerate(bars):
        h, l, c = bar["high"], bar["low"], bar["close"]
        tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        trs.append(tr)
        prev_close = c
        if h > peak:
            peak = h
        quote_res = bar.get("last_quote_reserves") or 0.0
        cap = FILL_CAP * quote_res
        if not had_tp and h >= entry * (1.0 + TP_GAIN):
            gross = tokens * TP_FRAC * entry * (1.0 + TP_GAIN) * (1.0 - slippage)
            if gross > cap:
                gross = cap
            proceeds += gross * (1.0 - FEE)
            tokens *= 1.0 - TP_FRAC
            had_tp = True
            reason = "tp_then_trail" if n > 1 else "tp_only"
        if i >= 1 and len(trs) >= 2:
            atr = float(np.mean(trs[-ATR_WINDOW:]))
            stop = peak - ATR_MULT * atr
            if l <= stop:
                gross = tokens * max(stop, l) * (1.0 - slippage)
                if gross > cap:
                    gross = cap
                proceeds += gross * (1.0 - FEE)
                tokens = 0.0
                reason = "trail_stop_after_tp" if had_tp else "trail_stop"
                break
        if i == n - 1:
            gross = tokens * c * (1.0 - slippage)
            if gross > cap:
                gross = cap
            proceeds += gross * (1.0 - FEE)
            tokens = 0.0
            reason = "time_stop_after_tp" if had_tp else "time_stop"
    return {"mint": first["mint"], "net_sol": proceeds - NOTIONAL_SOL - failed_tx_cost,
            "reason": reason, "had_tp": had_tp}


def main() -> None:
    days = sorted(p.name for p in BASE.iterdir() if p.name.startswith("2026-"))
    recs: list[dict] = []
    for day in days:
        by_mint, postgrad = load_day(day)
        grads = {r["mint"]: r for r in postgrad}
        day_n = 0
        for mint, bars in by_mint.items():
            if mint not in grads:
                continue
            gts = to_epoch(grads[mint]["grad_time"])
            for b in bars:
                b["_ts"] = to_epoch(b["minute_ts"])
            entry_idx = next((i for i, b in enumerate(bars) if b["_ts"] >= gts + ENTRY_DELAY_S), None)
            if not entry_idx:  # None or 0 (no history before entry)
                continue
            hist = bars[:entry_idx]
            peak = max(float(b["last_quote_reserves"] or 0.0) for b in hist)
            if peak <= 0:
                continue
            pool_now = float(hist[-1]["last_quote_reserves"] or 0.0)
            if pool_now <= SURVIVE_FRAC * peak:
                continue
            hour1 = [b for b in hist if b["_ts"] < gts + ENTRY_DELAY_S]
            net_flow = sum(b["buy_sol"] - b["sell_sol"] for b in hour1)
            n_trades = sum(b["n_trades"] for b in hour1)
            grad_price = hist[0]["open"]
            entry_price = bars[entry_idx]["open"]
            feats = {
                "pool_ge_85": pool_now >= 85.0,
                "pool_ge_200": pool_now >= 200.0,
                "netflow_pos": net_flow > 0,
                "netflow_pos_pool85": net_flow > 0 and pool_now >= 85.0,
                "price_up": grad_price > 0 and entry_price > grad_price,
                "trades_ge_40": n_trades >= 40,
                "netflow_pos_price_up": net_flow > 0 and grad_price > 0 and entry_price > grad_price,
                "pool200_netflow_pos": pool_now >= 200.0 and net_flow > 0,
            }
            regime = "pre" if day < REGIME_SPLIT else "post"
            for combo in COMBOS:
                out = simulate_slice(bars[entry_idx:], *combo)
                if out is None:
                    continue
                out["day"] = day
                out["regime"] = regime
                out["combo"] = combo
                out["feats"] = feats
                recs.append(out)
            day_n += 1
        print(f"{day}: survivors={day_n}", flush=True)

    pop_n = sum(1 for r in recs if r["combo"] == OPTIMISTIC)
    print(f"population: {pop_n}")
    splits = list(recs[0]["feats"].keys()) if recs else []
    summary: dict = {"population_n": pop_n, "splits": {}, "bonferroni_family": len(splits)}
    for split in splits:
        entry: dict = {}
        for label, combo in (("optimistic", OPTIMISTIC), ("mildest", MILDEST)):
            sel = [r["net_sol"] for r in recs if r["combo"] == combo and r["feats"][split]]
            entry[label] = pooled_stats(sel)
        for reg in ("pre", "post"):
            sub = [r["net_sol"] for r in recs if r["combo"] == MILDEST and r["feats"][split] and r["regime"] == reg]
            entry[reg] = pooled_stats(sub) if sub else {"n": 0}
        summary["splits"][split] = entry
        m, md = entry["optimistic"], entry["mildest"]
        print(f"{split}: opt n={m['n']} mean={m['mean_net_sol']:.4f} p5={m['boot_p5_mean']:.4f} | "
              f"mildest mean={md['mean_net_sol']:.4f} p5={md['boot_p5_mean']:.4f}", flush=True)

    out = BASE / "step10_retention_summary.json"
    out.write_text(json.dumps(summary, indent=2))
    with (BASE / "step10_retention_trades.jsonl").open("w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
