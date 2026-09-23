"""Step 7: Helius raw-log fill-feasibility probe (Addendum N part 2).

For 3 of the largest instant-grad tokens: page signatures back to the token's
first ~2 minutes, count them and the failed share, then fetch a few raw
transactions (jsonParsed) and inspect what the data actually contains.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from quant_scripts.meme_launch_filter.config import helius_api_key
from quant_scripts.meme_launch_filter.helius import HeliusClient

# (mint, day) for the top pg_max_pool_sol instant-grad tokens.
TOKENS = [
    ("F2reRYPQUPkagQy7t5VaZgtiHqXNFQ91ej15GRypump", "2026-09-13"),
    ("VEY71Uj9G6oZiVHR3dDjhMVrVAXfaTNatTjt226pump", "2026-09-12"),
    ("QTw25puRZ6dDMgw2TbAJJ31kKNdrvEmtmWCixvTpump", "2026-09-01"),
]
WINDOW_S = 120  # collect signatures within create_time .. create_time + window
MAX_PAGES = 200
N_TX_SAMPLE = 4


def parse_dune_ts(s: str) -> float:
    """Parse '2026-09-13 09:29:01.000 UTC' to epoch seconds."""
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f %Z").replace(tzinfo=timezone.utc).timestamp()


def page_back_to_first_minute(client: HeliusClient, mint: str, create_time: float) -> tuple[list[dict], bool]:
    """Return (earliest-window signatures oldest-first, hit_cap bool)."""
    pages: list[list[dict]] = []
    before: str | None = None
    hit_cap = True
    for _ in range(MAX_PAGES):
        batch = client.get_signatures_for_address(mint, before=before, limit=1000)
        if not batch:
            hit_cap = False
            break
        pages.append(batch)
        oldest = batch[-1]
        bt = oldest.get("blockTime")
        if bt is not None and bt <= create_time + WINDOW_S:
            hit_cap = False
            break
        before = oldest["signature"]
    # Signatures across pages are strictly newest->oldest; flatten.
    all_sigs: list[dict] = []
    for page in pages:
        all_sigs.extend(page)
    early = [s for s in all_sigs if s.get("blockTime") is not None and s["blockTime"] <= create_time + WINDOW_S]
    early.sort(key=lambda s: s["blockTime"])
    return early, hit_cap


def summarize_tx(tx: dict) -> dict:
    meta = tx.get("meta") or {}
    ixs = tx.get("transaction", {}).get("message", {}).get("instructions", [])
    names: list[str] = []
    programs: set[str] = set()
    for ix in ixs:
        p = (ix.get("programIdName") or ix.get("program") or "")[:40]
        programs.add(p)
        name = ix.get("programIdName")
        if not name and "parsed" in ix:
            name = (ix["parsed"].get("type") or "")[:40]
        names.append(name or "?")
    logs = meta.get("logMessages") or []
    return {
        "sig": tx.get("transaction", {}).get("signatures", ["?"])[0],
        "err": meta.get("err"),
        "fee_lamports": meta.get("fee"),
        "n_inner": len(meta.get("innerInstructions") or []),
        "ix_names": names[:8],
        "programs": sorted(programs)[:5],
        "log_head": logs[:6],
        "log_tail": logs[-6:],
    }


def main() -> None:
    client = HeliusClient(helius_api_key())
    out: dict = {}
    for mint, day in TOKENS:
        fb = json.loads((Path("research/meme_launch_filter") / day / "step2_featbar.json").read_text())["result"]["rows"]
        row = next(r for r in fb if r["mint"] == mint)
        create_time = parse_dune_ts(row["create_time"])
        print(f"{mint[:8]} day={day} create_time={create_time}", flush=True)
        early, hit_cap = page_back_to_first_minute(client, mint, create_time)
        if not early:
            out[mint] = {"error": "no signatures in window", "hit_cap": hit_cap}
            print("  no early sigs", flush=True)
            continue
        span = early[-1]["blockTime"] - early[0]["blockTime"]
        n_err = sum(1 for s in early if s.get("err"))
        print(f"  first-minute sigs={len(early)} span={span:.0f}s failed={n_err}", flush=True)
        samples = []
        picks = [0, len(early) // 3, 2 * len(early) // 3, len(early) - 1][:N_TX_SAMPLE]
        for idx in sorted(set(picks)):
            tx = client.get_transaction(early[idx]["signature"])
            if tx is None:
                samples.append({"idx": idx, "error": "getTransaction null"})
                continue
            s = summarize_tx(tx)
            s["idx"] = idx
            s["blockTime"] = early[idx]["blockTime"] - create_time
            samples.append(s)
        out[mint] = {
            "day": day,
            "create_time": create_time,
            "sigs_in_window": len(early),
            "span_s": span,
            "failed_count": n_err,
            "hit_page_cap": hit_cap,
            "samples": samples,
        }
    (Path("research/meme_launch_filter/step7_helius_probe.json")).write_text(json.dumps(out, indent=2))
    print("wrote step7_helius_probe.json")


if __name__ == "__main__":
    main()
