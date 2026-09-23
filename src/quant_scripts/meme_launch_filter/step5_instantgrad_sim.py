"""Step 5: instant-grad class sim (Addendum M candidate).

Population: graduates with fb_trades = 0 (decode-gap class, ~all with
age_at_grad_s <= 60s). Naive Step 3 exit engine, no filters.
"""

from __future__ import annotations

import json

from quant_scripts.meme_launch_filter.step3_sim import (
    BASE, DAYS, REGIME_SPLIT, load_day, simulate, pooled_stats,
)


def main() -> None:
    trades: list[dict] = []
    for day in DAYS:
        by_mint, postgrad = load_day(day)
        featbar = json.loads((BASE / day / "step2_featbar.json").read_text())["result"]["rows"]
        grads = {r["mint"] for r in postgrad}
        zero_class = {r["mint"] for r in featbar if (r.get("fb_trades") or 0) == 0}
        day_n = 0
        for mint, bars in by_mint.items():
            if mint not in grads or mint not in zero_class:
                continue
            rec = simulate(bars)
            if rec is None:
                continue
            rec["day"] = day
            rec["regime"] = "pre" if day < REGIME_SPLIT else "post"
            trades.append(rec)
            day_n += 1
        print(f"{day}: trades={day_n}", flush=True)

    (BASE / "step5_instantgrad_trades.jsonl").open("w").write("".join(json.dumps(t) + "\n" for t in trades))
    nets = [t["net_sol"] for t in trades]
    summary: dict = {"pooled": pooled_stats(nets), "regimes": {}}
    for reg in ("pre", "post"):
        sub = [t["net_sol"] for t in trades if t["regime"] == reg]
        summary["regimes"][reg] = pooled_stats(sub) if sub else {"n": 0}
    reasons: dict[str, list[float]] = {}
    for t in trades:
        reasons.setdefault(t["reason"], []).append(t["net_sol"])
    summary["exit_reasons"] = {k: {"n": len(v), "mean": round(sum(v) / len(v), 4)} for k, v in reasons.items()}
    (BASE / "step5_instantgrad_summary.json").write_text(json.dumps(summary, indent=2))
    print("pooled:", json.dumps(summary["pooled"]))
    print("regimes:", json.dumps({k: {"n": v.get("n"), "mean": v.get("mean_net_sol")} for k, v in summary["regimes"].items()}))
    print("exits:", json.dumps(summary["exit_reasons"]))


if __name__ == "__main__":
    main()
