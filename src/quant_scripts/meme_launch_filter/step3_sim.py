"""Step 3: naive baseline exit sim on per-graduate 1-min price paths (Addendum J).

Population: every graduate of the pulled September days (no entry filters).
Entry at first post-grad 1-min bar open; frozen exit rules per spec Section 5.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

BASE = Path("research/meme_launch_filter")
DAYS = sorted(p.name for p in BASE.iterdir() if p.name.startswith("2026-09-"))

# Frozen sim params (spec Section 5, pre-registered).
NOTIONAL_SOL = 1.0
FEE = 0.0025
SLIPPAGE = 0.005
FAILED_TX_COST = 0.02
TP_FRAC = 0.5
TP_GAIN = 0.5
ATR_WINDOW = 15
ATR_MULT = 2.0
FILL_CAP = 0.9
SEED = 20260923
N_BOOT = 10_000
REGIME_SPLIT = "2026-09-09"


def load_day(day: str) -> tuple[dict[str, list[dict]], list[dict]]:
    paths = json.loads((BASE / day / "step2_paths.json").read_text())["result"]["rows"]
    postgrad = json.loads((BASE / day / "step1_postgrad.json").read_text())["result"]["rows"]
    by_mint: dict[str, list[dict]] = {}
    for r in paths:
        by_mint.setdefault(r["mint"], []).append(r)
    for bars in by_mint.values():
        bars.sort(key=lambda r: r["minute_ts"])
    return by_mint, postgrad


def simulate(bars: list[dict]) -> dict | None:
    """Simulate one buy-and-manage trade over the 24h path. Returns record or None."""
    if not bars:
        return None
    first = bars[0]
    entry = first["open"] * (1.0 + SLIPPAGE)
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
        o, h, l, c = bar["open"], bar["high"], bar["low"], bar["close"]
        tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        trs.append(tr)
        prev_close = c
        if h > peak:
            peak = h
        if not had_tp and h >= entry * (1.0 + TP_GAIN):
            sell_price = entry * (1.0 + TP_GAIN) * (1.0 - SLIPPAGE)
            quote_res = bar.get("last_quote_reserves") or 0.0
            cap = FILL_CAP * quote_res
            gross = tokens * TP_FRAC * sell_price
            if gross > cap:
                gross = cap
            proceeds += gross * (1.0 - FEE)
            tokens *= 1.0 - TP_FRAC
            had_tp = True
            reason = "tp_then_trail" if n > 1 else "tp_only"
        if i >= 1 and len(trs) >= 2:
            window = trs[-ATR_WINDOW:]
            atr = float(np.mean(window))
            stop = peak - ATR_MULT * atr
            if l <= stop:
                sell_price = max(stop, l) * (1.0 - SLIPPAGE)
                quote_res = bar.get("last_quote_reserves") or 0.0
                cap = FILL_CAP * quote_res
                gross = tokens * sell_price
                if gross > cap:
                    gross = cap
                proceeds += gross * (1.0 - FEE)
                tokens = 0.0
                reason = "trail_stop_after_tp" if had_tp else "trail_stop"
                break
        if i == n - 1:
            quote_res = bar.get("last_quote_reserves") or 0.0
            cap = FILL_CAP * quote_res
            gross = tokens * c * (1.0 - SLIPPAGE)
            if gross > cap:
                gross = cap
            proceeds += gross * (1.0 - FEE)
            tokens = 0.0
            reason = "time_stop_after_tp" if had_tp else "time_stop"
    net = proceeds - NOTIONAL_SOL - FAILED_TX_COST
    return {"mint": first["mint"], "net_sol": net, "reason": reason, "had_tp": had_tp}


def pooled_stats(nets: list[float]) -> dict:
    arr = np.array(nets)
    rng = np.random.default_rng(SEED)
    boot = [float(rng.choice(arr, size=len(arr), replace=True).mean()) for _ in range(N_BOOT)]
    drop_k = max(1, int(0.01 * len(arr)))
    sorted_arr = np.sort(arr)
    return {
        "n": len(arr),
        "mean_net_sol": float(arr.mean()),
        "median_net_sol": float(np.median(arr)),
        "boot_p5_mean": float(np.percentile(boot, 5)),
        "hit_rate": float((arr > 0).mean()),
        "mean_excl_top1pct": float(sorted_arr[:-drop_k].mean()),
    }


def main() -> None:
    all_trades: list[dict] = []
    skipped = 0
    for day in DAYS:
        by_mint, postgrad = load_day(day)
        grads = {r["mint"] for r in postgrad}
        day_trades = []
        for mint, bars in by_mint.items():
            if mint not in grads:
                continue
            rec = simulate(bars)
            if rec is None:
                skipped += 1
                continue
            rec["day"] = day
            rec["regime"] = "pre" if day < REGIME_SPLIT else "post"
            all_trades.append(rec)
            day_trades.append(rec)
        print(f"{day}: trades={len(day_trades)}", flush=True)

    out_trades = BASE / "step3_sim_trades.jsonl"
    with out_trades.open("w") as f:
        for t in all_trades:
            f.write(json.dumps(t) + "\n")

    nets = [t["net_sol"] for t in all_trades]
    summary = {
        "params": {
            "notional_sol": NOTIONAL_SOL, "fee": FEE, "slippage": SLIPPAGE,
            "failed_tx_cost": FAILED_TX_COST, "tp_gain": TP_GAIN, "tp_frac": TP_FRAC,
            "atr_window": ATR_WINDOW, "atr_mult": ATR_MULT, "fill_cap": FILL_CAP,
            "seed": SEED, "n_boot": N_BOOT, "regime_split": REGIME_SPLIT,
        },
        "skipped_tokens": skipped,
        "pooled": pooled_stats(nets),
        "exit_reasons": {},
        "regimes": {},
        "per_day": {},
    }
    reasons: dict[str, list[float]] = {}
    for t in all_trades:
        reasons.setdefault(t["reason"], []).append(t["net_sol"])
    for k, v in reasons.items():
        summary["exit_reasons"][k] = {"n": len(v), "mean_net_sol": float(np.mean(v))}
    for reg in ("pre", "post"):
        sub = [t["net_sol"] for t in all_trades if t["regime"] == reg]
        summary["regimes"][reg] = pooled_stats(sub) if sub else {"n": 0}
    for day in DAYS:
        sub = [t["net_sol"] for t in all_trades if t["day"] == day]
        summary["per_day"][day] = {"n": len(sub), "mean_net_sol": float(np.mean(sub)) if sub else None}

    (BASE / "step3_sim_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary["pooled"], indent=2))
    print("exit_reasons:", json.dumps(summary["exit_reasons"]))
    print("regimes:", json.dumps(summary["regimes"]))


if __name__ == "__main__":
    main()
