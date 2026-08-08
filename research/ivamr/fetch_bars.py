"""Fetch + cache NQ 1-min bars (Databento) for the IVAMR probe.

Usage: .venv/bin/python research/ivamr/fetch_bars.py

Downloads 2013-11-01..2023-12-31 (starts before the IS window so the first IS
trading day has a prior-day profile) once and caches to cache/NQ_n_0_1m.parquet.
Subsequent runs reuse the cache (resumable via 30-day chunk files).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from quant_scripts.ivamr.config import StudyParams  # noqa: E402
from quant_scripts.ivamr.bars import load_intraday  # noqa: E402

if __name__ == "__main__":
    params = StudyParams()
    bars = load_intraday(params)
    for k, df in bars.items():
        print(f"{k}: {len(df)} rows | t0={df['t'].min()} | t1={df['t'].max()}")
    print("cache:", ROOT / "research" / "ivamr" / "cache")
