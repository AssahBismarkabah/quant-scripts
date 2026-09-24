"""Step 4: filtered entry sim - same exit engine as step3, filtered populations.

Variants (pre-registered from Addendum I):
- A base_clean: all grads with clean featbar rows (NaN-share artifact excluded)
- B net_gt0: noncreator_net > 0 (anti-moon exclusion)
- C attention: fb_traders >= 40 (moon-rate modifier, Q3/Q4)
- D combined: fb_traders >= 40 AND noncreator_net > 0
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from quant_scripts.meme_launch_filter.io_rows import load_rows
from quant_scripts.meme_launch_filter.step3_sim import (
    BASE, DAYS, FEE, FAILED_TX_COST, NOTIONAL_SOL, N_BOOT, SEED, SLIPPAGE,
    TP_FRAC, TP_GAIN, ATR_MULT, ATR_WINDOW, FILL_CAP, REGIME_SPLIT,
    load_day, simulate, pooled_stats,
)

VARIANTS = {
    "A_base_clean": lambda feat, share_nan: True,
    "B_net_gt0": lambda feat, share_nan: (feat.get("fb_noncreator_buy_sol") or 0) - (feat.get("fb_noncreator_sell_sol") or 0) > 0,
    "C_attention": lambda feat, share_nan: (feat.get("fb_traders") or 0) >= 40,
    "D_combined": lambda feat, share_nan: (feat.get("fb_traders") or 0) >= 40 and (feat.get("fb_noncreator_buy_sol") or 0) - (feat.get("fb_noncreator_sell_sol") or 0) > 0,
}


def main() -> None:
    # Simulate every clean graduate once; variant membership is just a subset.
    all_recs: list[dict] = []
    n_no_feat = 0
    n_share_nan = 0
    for day in DAYS:
        paths = load_rows(BASE / day, "step2_paths")
        postgrad = load_rows(BASE / day, "step1_postgrad")
        featbar = json.loads((BASE / day / "step2_featbar.json").read_text())["result"]["rows"]
        grads = {r["mint"] for r in postgrad}
        feat = {r["mint"]: r for r in featbar}
        by_mint: dict[str, list[dict]] = {}
        for r in paths:
            by_mint.setdefault(r["mint"], []).append(r)
        for bars in by_mint.values():
            bars.sort(key=lambda r: r["minute_ts"])
        day_recs = []
        for mint, bars in by_mint.items():
            if mint not in grads or mint not in feat:
                n_no_feat += mint not in feat and mint in grads
                continue
            frow = feat[mint]
            share = frow.get("fb_max_trader_share")
            share_nan = isinstance(share, str) and share == "NaN" or (isinstance(share, float) and math.isnan(share))
            if share_nan:
                n_share_nan += 1
                continue
            rec = simulate(bars)
            if rec is None:
                continue
            rec["day"] = day
            rec["regime"] = "pre" if day < REGIME_SPLIT else "post"
            for vname, pred in VARIANTS.items():
                rec[vname] = pred(frow, False)
            all_recs.append(rec)
            day_recs.append(rec)
        print(f"{day}: trades={len(day_recs)}", flush=True)
    print(f"skipped: no_featbar={n_no_feat} share_nan={n_share_nan}", flush=True)

    with (BASE / "step4_sim_trades.jsonl").open("w") as f:
        for t in all_recs:
            f.write(json.dumps(t) + "\n")

    summary = {
        "params": {
            "notional_sol": NOTIONAL_SOL, "fee": FEE, "slippage": SLIPPAGE,
            "failed_tx_cost": FAILED_TX_COST, "tp_gain": TP_GAIN, "tp_frac": TP_FRAC,
            "atr_window": ATR_WINDOW, "atr_mult": ATR_MULT, "fill_cap": FILL_CAP,
            "seed": SEED, "n_boot": N_BOOT, "regime_split": REGIME_SPLIT,
        },
        "variants": {},
    }
    for vname in VARIANTS:
        sub = [t for t in all_recs if t[vname]]
        nets = [t["net_sol"] for t in sub]
        vstats = pooled_stats(nets) if nets else {"n": 0}
        for reg in ("pre", "post"):
            rsub = [t["net_sol"] for t in sub if t["regime"] == reg]
            vstats[reg] = pooled_stats(rsub) if rsub else {"n": 0}
        reasons: dict[str, list[float]] = {}
        for t in sub:
            reasons.setdefault(t["reason"], []).append(t["net_sol"])
        vstats["exit_reasons"] = {k: {"n": len(v), "mean_net_sol": round(float(np.mean(v)), 4)} for k, v in reasons.items()}
        summary["variants"][vname] = vstats
        print(f"{vname}: {json.dumps({k: vstats[k] for k in ('n', 'mean_net_sol', 'boot_p5_mean', 'hit_rate') if k in vstats})}", flush=True)

    (BASE / "step4_sim_summary.json").write_text(json.dumps(summary, indent=2))
    print("wrote step4_sim_summary.json")


if __name__ == "__main__":
    main()
