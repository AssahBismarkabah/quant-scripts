"""Run the bounded event study for the 10b5-1 adoption-timing probe.

Usage: .venv/bin/python research/10b5-1-timing/run_study.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from quant_scripts.ten_b5_one_timing.event_study import run  # noqa: E402

if __name__ == "__main__":
    res = run()
    research = ROOT / "research" / "10b5-1-timing"
    (research / "outputs").mkdir(parents=True, exist_ok=True)
    res["frame"].to_parquet(research / "outputs" / "probe_frame.parquet")
    nA = int(res["frame"][res["frame"]["tier"] == "A"]["ticker"].nunique()) if not res["frame"].empty else 0
    nB = int(res["frame"][res["frame"]["tier"] == "B"]["ticker"].nunique()) if not res["frame"].empty else 0
    summary = {
        "n_distinct_tierA": nA,
        "n_distinct_tierB": nB,
        "gates": res["gates"],
        "gates_pass": res["gates_pass"],
        "notes": res["notes"],
    }
    import json

    (research / "outputs" / "probe_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
