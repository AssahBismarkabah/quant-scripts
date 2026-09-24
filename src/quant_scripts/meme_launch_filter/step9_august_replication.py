"""Step 9: August out-of-sample replication (Addendum O part 2).

1. Recount the featbar class split (fb_trades == 0 vs > 0) with canonical
   labels (classify from step2_analysis) pooled over all August days.
2. Age distribution of the zero class (instant-grad share).
3. Cost-sensitivity grid on the August instant-grad class with the same
   naive exit engine, plus the Addendum M optimistic config for reference.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from quant_scripts.meme_launch_filter.step2_analysis import classify, num
from quant_scripts.meme_launch_filter.step3_sim import (
    BASE, load_day, pooled_stats,
)
from quant_scripts.meme_launch_filter.step6_cost_sensitivity import (
    FAILED_TX_COSTS, SLIPPAGES, simulate_cost,
)

AUG_DAYS = sorted(p.name for p in BASE.iterdir() if p.name.startswith("2026-08-"))
COMBOS = [(0.005, 0.02)] + [(s, f) for s in SLIPPAGES for f in FAILED_TX_COSTS]


def main() -> None:
    classes: dict[str, list[str]] = {"zero": [], "clean": []}
    zero_ages: list[float] = []
    nets: dict[tuple[float, float], list[float]] = {c: [] for c in COMBOS}
    for day in AUG_DAYS:
        by_mint, postgrad = load_day(day)
        featbar = json.loads((BASE / day / "step2_featbar.json").read_text())["result"]["rows"]
        pg = {r["mint"]: r for r in postgrad}
        zero = {r["mint"] for r in featbar if (r.get("fb_trades") or 0) == 0}
        for mint, bars in by_mint.items():
            if mint not in pg:
                continue
            label = classify(pg[mint])
            if mint in zero:
                classes["zero"].append(label)
            else:
                classes["clean"].append(label)
        for r in featbar:
            if (r.get("fb_trades") or 0) == 0:
                age = num(r, "age_at_grad_s")
                if not np.isnan(age):
                    zero_ages.append(age)
        for mint, bars in by_mint.items():
            if mint not in pg or mint not in zero:
                continue
            for combo in COMBOS:
                rec = simulate_cost(bars, *combo)
                if rec is not None:
                    nets[combo].append(rec["net_sol"])
        print(f"{day}: done", flush=True)

    summary: dict = {"days": len(AUG_DAYS), "class_split": {}, "instant_grad_age": {}, "cost_grid": {}}
    for k, labels in classes.items():
        n = len(labels)
        counts = {lab: labels.count(lab) for lab in ("drained_small", "mooned", "retained")}
        summary["class_split"][k] = {
            "n": n,
            "counts": counts,
            "moon_rate": counts["mooned"] / n if n else None,
        }
    if zero_ages:
        arr = np.array(zero_ages)
        summary["instant_grad_age"] = {
            "n": len(arr),
            "share_le_60s": float((arr <= 60).mean()),
            "median_s": float(np.median(arr)),
        }
    print("class_split:", json.dumps(summary["class_split"], indent=2))
    print("instant_grad_age:", json.dumps(summary["instant_grad_age"]))
    for combo in COMBOS:
        s, f = combo
        key = "M_optimistic" if combo == (0.005, 0.02) else f"slip_{s:.2f}_fail_{f:.2f}"
        stats = pooled_stats(nets[combo])
        summary["cost_grid"][key] = stats
        print(f"{key}: n={stats['n']} mean={stats['mean_net_sol']:.4f} "
              f"p5={stats['boot_p5_mean']:.4f} hit={stats['hit_rate']:.3f}", flush=True)

    out = BASE / "step9_august_replication_summary.json"
    out.write_text(json.dumps(summary, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
