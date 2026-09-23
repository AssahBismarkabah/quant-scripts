"""Aggregate per-day Step 1 summaries into a cross-day stability view.

Reads step1_firsthour_summary.json and step1_postgrad_summary.json from each
day directory under research/meme_launch_filter/ and prints one compact row
per day plus pooled totals, so pilot-day signals can be checked for stability.

Usage: PYTHONPATH=src .venv/bin/python -m quant_scripts.meme_launch_filter.step1_crossday 2026-09-13 2026-09-20
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

RESEARCH = Path("research/meme_launch_filter")


def load(day: str) -> dict:
    day_dir = RESEARCH / day
    merged = json.loads((day_dir / "step1_merged.json").read_text())["counts"]
    fh = json.loads((day_dir / "step1_firsthour_summary.json").read_text())
    pg = json.loads((day_dir / "step1_postgrad_summary.json").read_text())
    buckets = fh["buckets"]
    grads = pg["drained"] + pg["partial"] + pg["alive"]
    return {
        "day": day,
        "launches": merged["graduated"] + merged["died_zero"] + merged["live_eod"],
        "graduated": merged["graduated"],
        "died_zero": merged["died_zero"],
        "live_eod": merged["live_eod"],
        "grad_rate": merged["graduated"] / max(merged["graduated"] + merged["died_zero"] + merged["live_eod"], 1),
        "instant_grad": buckets["graduated"]["instant_grad"]["n"],
        "instant_grad_share": buckets["graduated"]["instant_grad"]["n"] / max(merged["graduated"], 1),
        "organic_grads": buckets["graduated"].get("organic_grad", {}).get("n", 0),
        "died_net_pos": buckets["died_zero"]["share_noncreator_net_gt_0"],
        "live_net_pos": buckets["live_eod"]["share_noncreator_net_gt_0"],
        "organic_net_pos": buckets["graduated"].get("organic_grad", {}).get("share_noncreator_net_gt_0", 0.0),
        "died_creator_sell1m": buckets["died_zero"]["creator_first_sell"]["share_sell_le_1min"],
        "drained": pg["drained"],
        "partial": pg["partial"],
        "alive": pg["alive"],
        "drain_rate": pg["drained"] / max(grads, 1),
        "drained_instant_share": (pg["drained_fh"] or {}).get("share_instant_grad"),
        "alive_noncreator_net_pos": (pg["alive_fh"] or {}).get("share_noncreator_net_gt_0"),
        "alive_traders_median": (pg["alive_fh"] or {}).get("noncreator_traders", {}).get("median"),
    }


def main() -> None:
    start = date.fromisoformat(sys.argv[1])
    end = date.fromisoformat(sys.argv[2])
    days = []
    d = start
    while d <= end:
        days.append(load(d.isoformat()))
        d += timedelta(days=1)

    hdr = (
        "day        launches  grads  died   live   grad%  inst%  "
        "died+net  live+net  org+net  drain%  alive_tr_p50"
    )
    print(hdr)
    for r in days:
        print(
            f"{r['day']}  {r['launches']:>7} {r['graduated']:>6} {r['died_zero']:>6} "
            f"{r['live_eod']:>6} {100*r['grad_rate']:>5.1f} {100*r['instant_grad_share']:>5.1f} "
            f"{100*r['died_net_pos']:>8.1f} {100*r['live_net_pos']:>8.1f} "
            f"{100*r['organic_net_pos']:>7.1f} {100*r['drain_rate']:>6.1f} "
            f"{str(r['alive_traders_median']):>12}"
        )

    n = len(days)
    pooled = {
        "launches": sum(r["launches"] for r in days),
        "graduated": sum(r["graduated"] for r in days),
        "drained": sum(r["drained"] for r in days),
        "alive": sum(r["alive"] for r in days),
    }
    print()
    print(f"pooled over {n} days: launches={pooled['launches']} "
          f"graduated={pooled['graduated']} postgrad_drained={pooled['drained']} "
          f"postgrad_alive={pooled['alive']}")

    def spread(key: str) -> tuple[float, float, float]:
        vals = [r[key] for r in days if r[key] is not None]
        return min(vals), max(vals), sum(vals) / len(vals)

    for key, label in [
        ("grad_rate", "graduation rate"),
        ("instant_grad_share", "instant-grad share"),
        ("died_net_pos", "died_zero share noncreator_net>0"),
        ("live_net_pos", "live_eod share noncreator_net>0"),
        ("organic_net_pos", "organic grads share noncreator_net>0"),
        ("drain_rate", "postgrad drain rate"),
        ("drained_instant_share", "drained share that were instant grads"),
        ("alive_noncreator_net_pos", "alive share noncreator_net>0"),
    ]:
        lo, hi, mean = spread(key)
        print(f"{label}: min={100*lo:.1f}% max={100*hi:.1f}% mean={100*mean:.1f}%")

    out = RESEARCH / "step1_crossday_summary.json"
    out.write_text(json.dumps(days, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
