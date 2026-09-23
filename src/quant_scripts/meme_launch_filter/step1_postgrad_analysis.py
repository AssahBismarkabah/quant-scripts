"""Step 1 post-graduation analysis: PumpSwap outcomes for graduates.

Merges step1_postgrad.json (post-migration AMM aggregates) with the
first-hour analysis joins. Key questions:
1. Of tokens that graduated, how many survive on the AMM vs drain?
2. Does the first-hour non-creator net demand signal predict post-grad survival?
"""

import json
import statistics
import sys
from pathlib import Path

BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("research/meme_launch_filter/2026-09-20")


def pct(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    idx = min(int(q * len(s)), len(s) - 1)
    return s[idx]


def dist(values: list[float]) -> dict:
    values = [v for v in values if v == v]
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "p10": round(pct(values, 0.10), 3),
        "p25": round(pct(values, 0.25), 3),
        "median": round(pct(values, 0.50), 3),
        "p75": round(pct(values, 0.75), 3),
        "p90": round(pct(values, 0.90), 3),
    }


def num(row: dict, key: str) -> float:
    v = row.get(key)
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def main() -> None:
    pg_raw = json.loads((BASE / "step1_postgrad.json").read_text())
    pg = {r["mint"]: r for r in pg_raw["result"]["rows"]}
    merged = json.loads((BASE / "step1_merged.json").read_text())
    fh_raw = json.loads((BASE / "step1_firsthour.json").read_text())
    fh = {r["mint"]: r for r in fh_raw["result"]["rows"]}

    graduates = merged["tokens"]["graduated"]

    # Post-grad outcome per graduate:
    # - drain: pool SOL ended < 1% of its max (liquidity effectively gone)
    # - alive: last observed pool SOL >= 10% of max
    # - partial: in between
    outcomes: dict[str, list[dict]] = {"drained": [], "partial": [], "alive": [], "no_postgrad": []}
    for t in graduates:
        mint = t["mint"]
        p = pg.get(mint)
        if p is None:
            outcomes["no_postgrad"].append(t)
            continue
        max_sol = num(p, "pg_max_pool_sol")
        last_sol = num(p, "pg_last_pool_sol") if "pg_last_pool_sol" in p else None
        # step1_postgrad has pg_min/max but not last; use sells vs buys + last trade as proxy
        sell_sol = num(p, "pg_sell_sol")
        buy_sol = num(p, "pg_buy_sol")
        net = buy_sol - sell_sol
        if max_sol <= 0:
            bucket = "no_postgrad"
        elif net <= -0.8 * max_sol or num(p, "pg_min_pool_sol") < 0.01 * max_sol:
            bucket = "drained"
        elif net >= -0.2 * max_sol:
            bucket = "alive"
        else:
            bucket = "partial"
        outcomes[bucket].append(
            {
                "mint": mint,
                "max_sol": max_sol,
                "min_sol": num(p, "pg_min_pool_sol"),
                "net_flow_sol": net,
                "pg_traders": num(p, "pg_traders"),
                "grad_minutes": t.get("grad_minutes"),
            }
        )

    report = {k: len(v) for k, v in outcomes.items()}

    # Join first-hour signal to outcome buckets (drained vs alive only).
    for bucket in ("drained", "alive"):
        rows = []
        for o in outcomes[bucket]:
            f = fh.get(o["mint"])
            if f is None:
                continue
            noncreator_net = num(f, "fh_noncreator_buy_sol") - num(f, "fh_noncreator_sell_sol")
            rows.append(
                {
                    "noncreator_net": noncreator_net,
                    "noncreator_traders": num(f, "fh_noncreator_traders"),
                    "instant_grad": o["grad_minutes"] is not None and o["grad_minutes"] < 1.0,
                }
            )
        report[f"{bucket}_fh"] = {
            "n": len(rows),
            "noncreator_net_sol": dist([r["noncreator_net"] for r in rows]),
            "noncreator_traders": dist([r["noncreator_traders"] for r in rows]),
            "share_instant_grad": round(sum(1 for r in rows if r["instant_grad"]) / len(rows), 4) if rows else None,
            "share_noncreator_net_gt_0": round(sum(1 for r in rows if r["noncreator_net"] > 0) / len(rows), 4) if rows else None,
        }

    out = BASE / "step1_postgrad_summary.json"
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
