"""Moon-tail harvest variants on the D population (Addendum K step 2).

Pre-registered wider-stop / run-winners variants, no grid search:
- W1 wide_trail: trail with ATR_MULT 4.0 (2x wider), TP +50%, post-TP trail
- W2 wide_bev: fixed -35% stop pre-TP, TP +50%, then breakeven stop
- W3 wide_run: fixed -35% stop pre-TP, TP +100%, then breakeven stop
"""

from __future__ import annotations

import json

import numpy as np

from quant_scripts.meme_launch_filter.step3_sim import (
    BASE, DAYS, FEE, FAILED_TX_COST, NOTIONAL_SOL, SLIPPAGE,
    TP_FRAC, ATR_WINDOW, FILL_CAP, REGIME_SPLIT, load_day, pooled_stats,
)

VARIANTS = {
    "W1_wide_trail": {"pre_stop": "trail4", "tp_gain": 0.5, "post": "trail4"},
    "W2_wide_bev": {"pre_stop": "fixed35", "tp_gain": 0.5, "post": "bev"},
    "W3_wide_run": {"pre_stop": "fixed35", "tp_gain": 1.0, "post": "bev"},
}
FIXED_STOP = 0.35


def simulate_variant(bars: list[dict], v: dict) -> float | None:
    if not bars:
        return None
    first = bars[0]
    entry = first["open"] * (1.0 + SLIPPAGE)
    if entry <= 0:
        return None
    tokens = NOTIONAL_SOL * (1.0 - FEE) / entry
    proceeds = 0.0
    had_tp = False
    peak = first["open"]
    trs: list[float] = []
    prev_close = first["open"]
    n = len(bars)

    def sell(remaining: float, price: float, quote_res: float) -> float:
        cap = FILL_CAP * quote_res
        gross = remaining * price
        if gross > cap:
            gross = cap
        return gross * (1.0 - FEE)

    def stop_hit(mode: str) -> bool:
        if mode == "trail4":
            if i < 1:
                return False
            atr = float(np.mean(trs[-ATR_WINDOW:]))
            stop = peak - 4.0 * atr
            return l <= stop
        if mode == "fixed35":
            return l <= entry * (1.0 - FIXED_STOP)
        return False

    for i, bar in enumerate(bars):
        h, l, c = bar["high"], bar["low"], bar["close"]
        tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        trs.append(tr)
        prev_close = c
        if h > peak:
            peak = h
        quote_res = bar.get("last_quote_reserves") or 0.0
        if not had_tp:
            if h >= entry * (1.0 + v["tp_gain"]):
                proceeds += sell(tokens * TP_FRAC, entry * (1.0 + v["tp_gain"]) * (1.0 - SLIPPAGE), quote_res)
                tokens *= 1.0 - TP_FRAC
                had_tp = True
            elif stop_hit(v["pre_stop"]):
                px = entry * (1.0 - FIXED_STOP) if v["pre_stop"] == "fixed35" else max(peak - 4.0 * float(np.mean(trs[-ATR_WINDOW:])), l)
                proceeds += sell(tokens, px * (1.0 - SLIPPAGE), quote_res)
                tokens = 0.0
                break
        else:
            if v["post"] == "trail4":
                atr = float(np.mean(trs[-ATR_WINDOW:]))
                stop = peak - 4.0 * atr
                if l <= stop:
                    proceeds += sell(tokens, max(stop, l) * (1.0 - SLIPPAGE), quote_res)
                    tokens = 0.0
                    break
            elif l <= entry:
                proceeds += sell(tokens, entry * (1.0 - SLIPPAGE), quote_res)
                tokens = 0.0
                break
        if i == n - 1 and tokens > 0:
            proceeds += sell(tokens, c * (1.0 - SLIPPAGE), quote_res)
            tokens = 0.0
    return proceeds - NOTIONAL_SOL - FAILED_TX_COST


def main() -> None:
    trades: list[dict] = []
    for day in DAYS:
        by_mint, postgrad = load_day(day)
        featbar = json.loads((BASE / day / "step2_featbar.json").read_text())["result"]["rows"]
        grads = {r["mint"] for r in postgrad}
        feat = {r["mint"]: r for r in featbar}
        for mint, bars in by_mint.items():
            if mint not in grads or mint not in feat:
                continue
            f = feat[mint]
            share = f.get("fb_max_trader_share")
            if isinstance(share, str) and share == "NaN":
                continue
            traders = f.get("fb_traders") or 0
            net = (f.get("fb_noncreator_buy_sol") or 0) - (f.get("fb_noncreator_sell_sol") or 0)
            if traders < 40 or net <= 0:
                continue
            regime = "pre" if day < REGIME_SPLIT else "post"
            for vname, v in VARIANTS.items():
                n = simulate_variant(bars, v)
                if n is None:
                    continue
                trades.append({"day": day, "regime": regime, "variant": vname, "net_sol": n})
        print(f"{day}: done", flush=True)

    (BASE / "step4_harvest.jsonl").open("w").write("".join(json.dumps(t) + "\n" for t in trades))
    summary: dict = {"variants": {}}
    for vname in VARIANTS:
        nets = [t["net_sol"] for t in trades if t["variant"] == vname]
        st = pooled_stats(nets)
        for reg in ("pre", "post"):
            rsub = [t["net_sol"] for t in trades if t["variant"] == vname and t["regime"] == reg]
            st[reg] = pooled_stats(rsub) if rsub else {"n": 0}
        summary["variants"][vname] = st
        print(f"{vname}: n={st['n']} mean={st['mean_net_sol']:.3f} p5={st['boot_p5_mean']:.3f} hit={st['hit_rate']:.3f}", flush=True)

    (BASE / "step4_harvest_summary.json").write_text(json.dumps(summary, indent=2))
    print("wrote step4_harvest_summary.json")


if __name__ == "__main__":
    main()
