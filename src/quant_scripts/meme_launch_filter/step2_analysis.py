"""Step 2 monthly analysis: entry-bar features vs post-grad outcomes.

Joins per-day step2_featbar.json (pre-graduation trade features, no
lookahead) with step1_postgrad.json (AMM outcome aggregates).

Outcome label is the REFINED version from Addendum H:
- drained_small: min_pool < 10% of max AND max_pool_sol < MOON_THRESH
  (a rug: liquidity gone, pool was never big)
- mooned: min_pool < 10% of max AND max_pool_sol >= MOON_THRESH
  (drawdown of a big pool - the lottery prize, NOT a failure)
- retained: min_pool >= 10% of max

Regime split: pre/post Sep 9 (died_zero regime shift, Addendum G).
"""

import json
import math
import sys
from pathlib import Path

BASE_DIR = Path("research/meme_launch_filter")
MOON_THRESH = 200.0  # SOL; ~2.4x the ~85 SOL migration seed, top ~7% of graduates


def num(row: dict, key: str) -> float:
    v = row.get(key)
    try:
        x = float(v)
        if math.isnan(x):
            return float("nan")
        return x
    except (TypeError, ValueError):
        return float("nan")


def pct(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    return s[min(int(q * len(s)), len(s) - 1)]


def classify(pg_row: dict | None) -> str:
    if pg_row is None:
        return "no_postgrad"
    max_sol = num(pg_row, "pg_max_pool_sol")
    min_sol = num(pg_row, "pg_min_pool_sol")
    if max_sol <= 0:
        return "no_postgrad"
    if min_sol < 0.10 * max_sol:
        return "mooned" if max_sol >= MOON_THRESH else "drained_small"
    return "retained"


def rate(groups: dict[str, list[str]]) -> dict:
    out = {}
    for k, outs in groups.items():
        n = len(outs)
        if n == 0:
            continue
        out[k] = {
            "n": n,
            "drain_rate": round(outs.count("drained_small") / n, 4),
            "moon_rate": round(outs.count("mooned") / n, 4),
            "retained_rate": round(outs.count("retained") / n, 4),
        }
    return out


def main() -> None:
    start = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    end = sys.argv[2] if len(sys.argv) > 2 else "2026-09-22"
    days = sorted(d.name for d in BASE_DIR.iterdir() if d.name[:2] == "20" and start <= d.name <= end)

    # Moon-threshold scan on pooled outcome data.
    all_max: list[float] = []
    rows: list[tuple[str, dict, str]] = []  # (day, featrow, outcome)
    per_day: dict[str, dict] = {}
    caches: dict[str, tuple[dict, dict]] = {}
    for day in days:
        ddir = BASE_DIR / day
        fb = {r["mint"]: r for r in json.loads((ddir / "step2_featbar.json").read_text())["result"]["rows"]}
        pg = {r["mint"]: r for r in json.loads((ddir / "step1_postgrad.json").read_text())["result"]["rows"]}
        caches[day] = (fb, pg)
        grads = [r for r in fb.values() if not math.isnan(num(r, "fb_trades"))]
        outs = [classify(pg.get(r["mint"])) for r in grads]
        per_day[day] = {
            "grad_rows": len(fb),
            "with_history": len(grads),
            "with_history_share": round(len(grads) / len(fb), 4) if fb else None,
            "outcome_counts": {k: outs.count(k) for k in ("drained_small", "mooned", "retained", "no_postgrad")},
        }
        for r in grads:
            v = num(pg.get(r["mint"], {}), "pg_max_pool_sol")
            if v == v:
                all_max.append(v)
            rows.append((day, r, classify(pg.get(r["mint"]))))

    scan = {}
    for t in (10, 20, 50, 100, 200, 500):
        scan[f">{t}_sol"] = {
            "n": sum(1 for v in all_max if v > t),
            "share": round(sum(1 for v in all_max if v > t) / len(all_max), 4),
        }

    # Signal scan on pooled with-history graduates.
    trader_vals = sorted(num(r, "fb_traders") for _, r, _ in rows if num(r, "fb_traders") == num(r, "fb_traders"))
    q1, q2, q3 = pct(trader_vals, 0.25), pct(trader_vals, 0.50), pct(trader_vals, 0.75)

    def bucket_traders(v: float) -> str:
        if v != v:
            return "missing"
        if v <= q1:
            return "Q1"
        if v <= q2:
            return "Q2"
        if v <= q3:
            return "Q3"
        return "Q4"

    def share_bucket(v: float) -> str:
        if v != v:
            return "missing"
        if v <= 0.05:
            return "le0.05"
        if v <= 0.15:
            return "0.05-0.15"
        return "gt0.15"

    for regime, day_pred in (
        ("pre_sep9", lambda d: d < "2026-09-09"),
        ("post_sep9", lambda d: d >= "2026-09-09"),
        ("all", lambda d: True),
    ):
        groups: dict[str, list[str]] = {}
        for d, r, o in rows:
            if not day_pred(d):
                continue
            groups.setdefault(f"traders_{bucket_traders(num(r, 'fb_traders'))}", []).append(o)
            groups.setdefault(f"share_{share_bucket(num(r, 'fb_max_trader_share'))}", []).append(o)
            net = num(r, "fb_noncreator_buy_sol") - num(r, "fb_noncreator_sell_sol")
            groups.setdefault("noncreator_net_gt0" if net == net and net > 0 else "noncreator_net_le0", []).append(o)
            groups.setdefault("all", []).append(o)
        per_day[f"signal_scan_{regime}"] = rate(groups)
        per_day[f"trader_quartiles_{regime}"] = {"q1": q1, "q2": q2, "q3": q3}

    # Moon tail: top tokens by max pool across the whole month.
    tops = sorted(((num(p, "pg_max_pool_sol"), m) for m, p in
                   ((m, caches[day][1].get(m)) for day in days for m in caches[day][1]) if p and num(p, "pg_max_pool_sol") == num(p, "pg_max_pool_sol")), reverse=True)

    report = {
        "moon_threshold": MOON_THRESH,
        "threshold_scan": scan,
        "per_day": per_day,
        "top_pools_month": [{"mint": m, "max_sol": round(v, 2)} for v, m in tops[:10]],
    }
    out = BASE_DIR / "step2_monthly_summary.json"
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps({
        "threshold_scan": scan,
        "signal_scan_all": per_day.get("signal_scan_all"),
        "signal_scan_pre_sep9": per_day.get("signal_scan_pre_sep9"),
        "signal_scan_post_sep9": per_day.get("signal_scan_post_sep9"),
        "top_pools_month": report["top_pools_month"],
    }, indent=1))


if __name__ == "__main__":
    main()
