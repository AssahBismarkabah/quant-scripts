"""Merge Step-1 launch/graduation/trade pulls for one day and print analyst stats."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def ts(value: str | None) -> float | None:
    if not value:
        return None
    t = value.replace(" UTC", "").split(".")[0]
    return datetime.fromisoformat(t).replace(tzinfo=timezone.utc).timestamp()


def main() -> None:
    day_dir = Path(sys.argv[1])
    launches = json.loads((day_dir / "step1_launches.json").read_text())["result"]["rows"]
    grads = {r["mint"]: ts(r["first_graduation_time"]) for r in
             json.loads((day_dir / "step1_graduations.json").read_text())["result"]["rows"]}
    trades = {r["mint"]: r for r in
              json.loads((day_dir / "step1_trades.json").read_text())["result"]["rows"]}

    stats: dict[str, list] = {"graduated": [], "died_zero": [], "live_eod": []}
    for row in launches:
        mint = row["mint"]
        create_t = ts(row["call_block_time"])
        trade = trades.get(mint)
        grad_t = grads.get(mint)
        if grad_t:
            bucket = "graduated"
        elif trade and (trade.get("min_sol_reserves") or 0) < 0.1:
            bucket = "died_zero"
        else:
            bucket = "live_eod"
        rec = {
            "mint": mint,
            "creator": row["creator"],
            "schema_ver": row["schema_ver"],
            "is_mayhem": row["is_mayhem_mode"],
            "create_t": create_t,
            "grad_t": grad_t,
            "grad_minutes": (grad_t - create_t) / 60.0 if grad_t and create_t else None,
            "n_trades": (trade or {}).get("n_trades", 0),
            "n_traders": (trade or {}).get("n_traders", 0),
            "total_buy_sol": (trade or {}).get("total_buy_sol", 0.0),
            "total_sell_sol": (trade or {}).get("total_sell_sol", 0.0),
            "max_sol_reserves": (trade or {}).get("max_sol_reserves", 0.0),
            "min_sol_reserves": (trade or {}).get("min_sol_reserves"),
        }
        stats[bucket].append(rec)

    out = {"counts": {k: len(v) for k, v in stats.items()}, "tokens": stats}
    (day_dir / "step1_merged.json").write_text(json.dumps(out, indent=1))

    counts = {k: len(v) for k, v in stats.items()}
    total = sum(counts.values())
    print(f"total={total} {counts}")
    if counts["graduated"]:
        gm = sorted(r["grad_minutes"] for r in stats["graduated"] if r["grad_minutes"] is not None)
        med = gm[len(gm) // 2]
        print(f"graduation minutes: p50={med:.1f} p90={gm[int(0.9*len(gm))]:.1f} max={gm[-1]:.1f}")
    for name in ("graduated", "died_zero", "live_eod"):
        rows = stats[name]
        if not rows:
            continue
        buys = [r["total_buy_sol"] for r in rows]
        reserves = [r["max_sol_reserves"] or 0 for r in rows]
        ntr = [r["n_traders"] for r in rows]
        buys.sort(); reserves.sort(); ntr.sort()
        print(f"{name}: buy_sol p50={buys[len(buys)//2]:.2f} p90={buys[int(0.9*len(buys))]:.2f} "
              f"| max_reserve p50={reserves[len(reserves)//2]:.1f} p90={reserves[int(0.9*len(reserves))]:.1f} "
              f"| traders p50={ntr[len(ntr)//2]} p90={ntr[int(0.9*len(ntr))]}")

    all_recs = stats["graduated"] + stats["died_zero"] + stats["live_eod"]
    serial = Counter(r["creator"] for r in all_recs if r["creator"])
    multi = {c: n for c, n in serial.items() if n > 3}
    print(f"creators >3 launches/day: {len(multi)} covering {sum(multi.values())} tokens")
    for label, sel in [("mayhem", lambda r: r["is_mayhem"]), ("non_mayhem", lambda r: not r["is_mayhem"])]:
        rows = [r for r in all_recs if sel(r) and r["schema_ver"] == "v2"]
        if rows:
            g = sum(1 for r in rows if r["grad_t"])
            print(f"{label}: n={len(rows)} graduated={g} ({g/len(rows)*100:.1f}%)")


if __name__ == "__main__":
    main()
