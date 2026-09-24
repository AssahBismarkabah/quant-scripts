"""Step 1 first-hour analysis: merge first-hour aggregates with outcome buckets.

Reads step1_firsthour.json and step1_merged.json, tests the hypotheses
recorded in the research spec, writes a summary JSON next to the data.
"""

import json
import statistics
import sys
from pathlib import Path

from quant_scripts.meme_launch_filter.io_rows import load_merged, load_rows

BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("research/meme_launch_filter/2026-09-20")


def load_firsthour() -> dict[str, dict]:
    rows = load_rows(BASE, "step1_firsthour")
    return {r["mint"]: r for r in rows}


def load_merged_tokens() -> dict[str, list[dict]]:
    return load_merged(BASE)["tokens"]


def pct(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    idx = min(int(q * len(s)), len(s) - 1)
    return s[idx]


def dist_summary(values: list[float]) -> dict:
    values = [v for v in values if v == v]  # drop NaN
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "p10": round(pct(values, 0.10), 3),
        "p25": round(pct(values, 0.25), 3),
        "median": round(pct(values, 0.50), 3),
        "p75": round(pct(values, 0.75), 3),
        "p90": round(pct(values, 0.90), 3),
        "mean": round(statistics.fmean(values), 3),
    }


def num(row: dict, key: str) -> float:
    v = row.get(key)
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def main() -> None:
    fh = load_firsthour()
    merged = load_merged_tokens()

    report: dict = {"fh_rows": len(fh), "buckets": {}}

    for bucket, tokens in merged.items():
        joined = []
        for t in tokens:
            f = fh.get(t["mint"])
            if f is None:
                continue
            joined.append(
                {
                    "mint": t["mint"],
                    "grad_minutes": t.get("grad_minutes"),
                    "fh_trades": num(f, "fh_trades"),
                    "fh_noncreator_traders": num(f, "fh_noncreator_traders"),
                    "creator_net": num(f, "fh_creator_buy_sol") - num(f, "fh_creator_sell_sol"),
                    "noncreator_net": num(f, "fh_noncreator_buy_sol") - num(f, "fh_noncreator_sell_sol"),
                    "creator_first_sell_min": num(f, "creator_first_sell_min"),
                    "creator_buy_sol": num(f, "fh_creator_buy_sol"),
                    "creator_sell_sol": num(f, "fh_creator_sell_sol"),
                }
            )

        stats = {
            "tokens_with_fh": len(joined),
            "fh_noncreator_traders": dist_summary([j["fh_noncreator_traders"] for j in joined]),
            "noncreator_net_sol": dist_summary([j["noncreator_net"] for j in joined]),
            "creator_net_sol": dist_summary([j["creator_net"] for j in joined]),
        }

        instant = [j for j in joined if j["grad_minutes"] is not None and j["grad_minutes"] < 1.0]
        stats["instant_grad"] = {
            "n": len(instant),
            "creator_sold_within_hour": sum(1 for j in instant if j["creator_sell_sol"] > 0),
            "creator_net_sol": dist_summary([j["creator_net"] for j in instant]),
            "single_trade_instant": sum(1 for j in instant if j["fh_trades"] <= 2),
        }

        for thresh in (5, 10, 20):
            stats[f"share_noncreator_traders_ge_{thresh}"] = (
                round(sum(1 for j in joined if j["fh_noncreator_traders"] >= thresh) / len(joined), 4)
                if joined else None
            )

        with_sell = [j for j in joined if j["creator_first_sell_min"] > 0]
        stats["creator_first_sell"] = {
            "n_with_sell_in_hour": len(with_sell),
            "share_sell_le_1min": (
                round(sum(1 for j in with_sell if j["creator_first_sell_min"] <= 1.0) / len(with_sell), 4)
                if with_sell else None
            ),
        }

        # Key conditional: positive non-creator net demand in first hour.
        stats["share_noncreator_net_gt_0"] = (
            round(sum(1 for j in joined if j["noncreator_net"] > 0) / len(joined), 4)
            if joined else None
        )

        # Graduated-only: split self-grad (single trade, instant) vs organic.
        if bucket == "graduated":
            organic = [j for j in joined if j["grad_minutes"] >= 1.0 or j["fh_trades"] > 2]
            stats["organic_grad"] = {
                "n": len(organic),
                "noncreator_net_sol": dist_summary([j["noncreator_net"] for j in organic]),
                "share_noncreator_net_gt_0": (
                    round(sum(1 for j in organic if j["noncreator_net"] > 0) / len(organic), 4)
                    if organic else None
                ),
                "fh_noncreator_traders": dist_summary(
                    [j["fh_noncreator_traders"] for j in organic]
                ),
            }

        report["buckets"][bucket] = stats

    out = BASE / "step1_firsthour_summary.json"
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
