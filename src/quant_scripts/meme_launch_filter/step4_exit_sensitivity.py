"""Exit-structure sensitivity on the D population (Addendum K follow-up).

Pre-registered three variants, no grid search:
- V1 trail: current (pre-TP trail, TP +50%, post-TP trail) - equals step4 D
- V2 tp_time: no stops, TP +50%, ride to 24h close
- V3 tp_bev: pre-TP trail, TP +50%, then breakeven stop, else 24h close
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from quant_scripts.meme_launch_filter.step3_sim import (
    BASE, DAYS, FEE, FAILED_TX_COST, NOTIONAL_SOL, SLIPPAGE,
    TP_FRAC, TP_GAIN, ATR_MULT, ATR_WINDOW, FILL_CAP, REGIME_SPLIT,
    load_day, pooled_stats,
)


def simulate_mode(bars: list[dict], mode: str) -> float | None:
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

    for i, bar in enumerate(bars):
        h, l, c = bar["high"], bar["low"], bar["close"]
        tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        trs.append(tr)
        prev_close = c
        if h > peak:
            peak = h
        quote_res = bar.get("last_quote_reserves") or 0.0

        if not had_tp:
            # Take-profit leg is common to all variants.
            if h >= entry * (1.0 + TP_GAIN):
                proceeds += sell(tokens * TP_FRAC, entry * (1.0 + TP_GAIN) * (1.0 - SLIPPAGE), quote_res)
                tokens *= 1.0 - TP_FRAC
                had_tp = True
            elif mode != "tp_time" and i >= 1:
                # V1/V3: pre-TP trail stop active.
                atr = float(np.mean(trs[-ATR_WINDOW:]))
                stop = peak - ATR_MULT * atr
                if l <= stop:
                    proceeds += sell(tokens, max(stop, l) * (1.0 - SLIPPAGE), quote_res)
                    tokens = 0.0
                    break
        else:
            if mode == "trail":
                atr = float(np.mean(trs[-ATR_WINDOW:]))
                stop = peak - ATR_MULT * atr
                if l <= stop:
                    proceeds += sell(tokens, max(stop, l) * (1.0 - SLIPPAGE), quote_res)
                    tokens = 0.0
                    break
            elif mode == "tp_bev":
                if l <= entry:
                    proceeds += sell(tokens, entry * (1.0 - SLIPPAGE), quote_res)
                    tokens = 0.0
                    break
            # tp_time: no post-TP stop, ride to the end.
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
        day_n = 0
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
            for mode in ("trail", "tp_time", "tp_bev"):
                n = simulate_mode(bars, mode)
                if n is None:
                    continue
                trades.append({"day": day, "regime": regime, "mode": mode, "net_sol": n})
            day_n += 1
        print(f"{day}: tokens={day_n}", flush=True)

    (BASE / "step4_exit_sensitivity.jsonl").open("w").write("".join(json.dumps(t) + "\n" for t in trades))
    summary: dict = {"modes": {}}
    for mode in ("trail", "tp_time", "tp_bev"):
        nets = [t["net_sol"] for t in trades if t["mode"] == mode]
        mstats = pooled_stats(nets)
        for reg in ("pre", "post"):
            rsub = [t["net_sol"] for t in trades if t["mode"] == mode and t["regime"] == reg]
            mstats[reg] = pooled_stats(rsub) if rsub else {"n": 0}
        summary["modes"][mode] = mstats
        print(f"{mode}: n={mstats['n']} mean={mstats['mean_net_sol']:.3f} p5={mstats['boot_p5_mean']:.3f} hit={mstats['hit_rate']:.3f}", flush=True)

    (BASE / "step4_exit_sensitivity_summary.json").write_text(json.dumps(summary, indent=2))
    print("wrote step4_exit_sensitivity_summary.json")


if __name__ == "__main__":
    main()
