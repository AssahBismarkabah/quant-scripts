"""Fetch + cache NQ 1-min bars (Databento) for the probe window.

Usage: .venv/bin/python research/nq-vwap-pullback/fetch_bars.py

Downloads the full 2020-08-01..2026-08-07 window once and caches to
cache/NQ_n_0_1m.parquet. Subsequent runs reuse the cache (resumable), so the
IS and OOS windows in run_probe.py are both computed from the same fetched base.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from quant_scripts.nq_vwap_pullback.config import StudyParams  # noqa: E402
from quant_scripts.nq_vwap_pullback.bars import load_intraday  # noqa: E402

if __name__ == "__main__":
    params = StudyParams()
    bars = load_intraday(params)
    for k, df in bars.items():
        print(f"{k}: {len(df)} rows | t0={df['t'].min()} | t1={df['t'].max()}")
    print("cache:", ROOT / "research" / "nq-vwap-pullback" / "cache")
