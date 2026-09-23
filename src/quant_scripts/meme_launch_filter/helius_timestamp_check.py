"""Helius block-level spot check of Dune timestamp truncation.

Dune reports all Sep-20 event/block times truncated to whole seconds
(:00.000). To verify whether sub-second ordering is recoverable (needed for
'creator graduated before anyone else could act' style claims), fetch the
actual graduation transactions for a few instant-grad tokens and compare
Helius blockTime against Dune's reported evt_block_time.

Usage: PYTHONPATH=src .venv/bin/python -m quant_scripts.meme_launch_filter.helius_timestamp_check
"""

from __future__ import annotations

import json
from pathlib import Path

from .config import PUMPSWAP_PROGRAM, helius_api_key
from .helius import HeliusClient

BASE = Path("research/meme_launch_filter/2026-09-20")

# Full graduation tx signatures are loaded from the Dune probe output
# (grad_tx_probe_full.json, written by a SELECT of evt_tx_id at full length).

def main() -> None:
    # Exact graduation tx ids for the 5 spot-check mints (from Dune probe
    # /tmp/grad_tx_probe.json, reproduced in-line for reproducibility).
    grad_txs = {
        "E4pWBbtuNbvjcRL2BGn8X9bA5wHAq2fX6FAVvxoupump": "7KhvJRwLaw7r2MUuKgGPgbuP",
        "2LVJ55ApwanmybLeD6oeAXsnLg7f3YPAkBSfdRsQpump": "4V8NsXMqe7hWGqjy5SDbF1k6",
        "AjHawC2nBLyzymfD3Z3tQf569dAZ74Xiujgid4wHpump": "37gKQvfhQjYrDSn23uwdBLJy",
        "HSrjfsmYnQcnM7MWBy8xx2871ZLtjZKFc6767Bwhpump": "sodQKmedk4N9XR9vNjwikwyL",
        "Dwz3ZkUeuZxuNWDjY6F5wS2VGafAFSM1zFLi9VZfpump": "4aNBTP93H1P9pxqvPaB5NkmV",
    }
    dune_times = {
        "E4pWBbtuNbvjcRL2BGn8X9bA5wHAq2fX6FAVvxoupump": "2026-09-20 01:20:00.000 UTC",
        "2LVJ55ApwanmybLeD6oeAXsnLg7f3YPAkBSfdRsQpump": "2026-09-20 03:15:00.000 UTC",
        "AjHawC2nBLyzymfD3Z3tQf569dAZ74Xiujgid4wHpump": "2026-09-20 05:17:00.000 UTC",
        "HSrjfsmYnQcnM7MWBy8xx2871ZLtjZKFc6767Bwhpump": "2026-09-20 05:30:00.000 UTC",
        "Dwz3ZkUeuZxuNWDjY6F5wS2VGafAFSM1zFLi9VZfpump": "2026-09-20 05:44:00.000 UTC",
    }

    client = HeliusClient(helius_api_key())
    full_sigs = json.loads((BASE / "grad_tx_full.json").read_text())
    out = []
    for mint, tx_prefix in grad_txs.items():
        dune_time = dune_times[mint]
        # Full tx ids from the Dune probe; getTransaction takes the signature
        # directly, so no history scan is needed.
        full_sig = full_sigs.get(mint)
        if not full_sig:
            out.append({"mint": mint, "error": "no full sig recorded"})
            continue
        tx = client.get_transaction(full_sig)
        if tx is None:
            out.append({"mint": mint, "error": "tx fetch returned None"})
            continue
        entries = {
            "helius_blockTime": tx.get("blockTime"),
            "helius_slot": tx.get("slot"),
            "dune_slot": None,
            "dune_time": dune_times[mint],
        }
        out.append(
            {
                "mint": mint,
                "dune_time": dune_time,
                "signatures": entries,
            }
        )

    dest = BASE / "helius_timestamp_check.json"
    dest.write_text(json.dumps(out, indent=1))
    print(f"wrote {dest} ({len(out)} mints checked)")


if __name__ == "__main__":
    main()
