"""Step 6: entry-cost sensitivity on the instant-grad class (Addendum N).

Pre-registered grid: slippage {0.01, 0.02, 0.03} x failed-tx cost {0.05, 0.1, 0.2}.
Population and exit engine identical to step5 (naive Step 3 engine, no filters).
Data is loaded once per day; the grid is looped inside per token.
"""

from __future__ import annotations

import json

import numpy as np

from quant_scripts.meme_launch_filter.step3_sim import (
    BASE, DAYS, FEE, NOTIONAL_SOL, TP_FRAC, TP_GAIN,
    ATR_WINDOW, ATR_MULT, FILL_CAP, REGIME_SPLIT, load_day, pooled_stats,
)

SLIPPAGES = [0.01, 0.02, 0.03]
FAILED_TX_COSTS = [0.05, 0.1, 0.2]


def simulate_cost(bars: list[dict], slippage: float, failed_tx_cost: float) -> dict | None:
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
        o, h, l, c = bar["open"], bar["high"], bar["low"], bar["close"]
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
    net = proceeds - NOTIONAL_SOL - failed_tx_cost
    return {"mint": first["mint"], "net_sol": net, "reason": reason, "had_tp": had_tp}


def main() -> None:
    combos = [(s, f) for s in SLIPPAGES for f in FAILED_TX_COSTS]
    trades: dict[tuple[float, float], list[dict]] = {c: [] for c in combos}
    day_counts: dict[str, int] = {}
    for day in DAYS:
        by_mint, postgrad = load_day(day)
        featbar = json.loads((BASE / day / "step2_featbar.json").read_text())["result"]["rows"]
        grads = {r["mint"] for r in postgrad}
        zero_class = {r["mint"] for r in featbar if (r.get("fb_trades") or 0) == 0}
        regime = "pre" if day < REGIME_SPLIT else "post"
        day_n = 0
        for mint, bars in by_mint.items():
            if mint not in grads or mint not in zero_class:
                continue
            for combo in combos:
                rec = simulate_cost(bars, *combo)
                if rec is not None:
                    rec["regime"] = regime
                    rec["day"] = day
                    trades[combo].append(rec)
            day_n += 1
        day_counts[day] = day_n
        print(f"{day}: tokens={day_n}", flush=True)

    summary: dict = {
        "params": {"slippages": SLIPPAGES, "failed_tx_costs": FAILED_TX_COSTS},
        "population": "instant_grad (fb_trades == 0), all September days",
        "day_counts_total": sum(day_counts.values()),
        "grid": {},
        "regimes": {},  # pre/post split per slippage at failed_tx = 0.1
    }
    print(f"total instant-grad tokens: {sum(day_counts.values())}")
    for combo in combos:
        nets = [t["net_sol"] for t in trades[combo]]
        s, f = combo
        key = f"slip_{s:.2f}_fail_{f:.2f}"
        stats = pooled_stats(nets)
        summary["grid"][key] = stats
        print(f"{key}: n={stats['n']} mean={stats['mean_net_sol']:.4f} "
              f"p5={stats['boot_p5_mean']:.4f} hit={stats['hit_rate']:.3f}", flush=True)
    for s in SLIPPAGES:
        combo = (s, 0.1)
        key = f"slip_{s:.2f}_fail_0.10"
        summary["regimes"][key] = {}
        for reg in ("pre", "post"):
            sub = [t["net_sol"] for t in trades[combo] if t["regime"] == reg]
            summary["regimes"][key][reg] = pooled_stats(sub) if sub else {"n": 0}

    (BASE / "step6_cost_sensitivity_summary.json").write_text(json.dumps(summary, indent=2))
    print("wrote step6_cost_sensitivity_summary.json")


if __name__ == "__main__":
    main()
