"""Row storage helpers: parquet (preferred) with Dune JSON fallback.

Heavy per-day pulls (step1_launches/firsthour/trades, step2_paths, step1_merged)
are stored as zstd parquet so the repo stays small. Fresh Dune pulls still write
the original JSON wrapper; convert_to_parquet() mirrors it to .parquet and
load_rows() always prefers the parquet copy.

Counts for step1_merged live in parquet schema metadata under b"counts".
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

# Kinds stored as parquet (converted from the Dune JSON wrapper).
PARQUET_KINDS = ("step1_launches", "step1_firsthour", "step1_trades", "step2_paths", "step1_merged")


def load_rows(day_dir: Path | str, name: str) -> list[dict[str, Any]]:
    """Return result rows for name; parquet preferred, Dune JSON fallback."""
    day_dir = Path(day_dir)
    pq_path = day_dir / f"{name}.parquet"
    if pq_path.exists():
        if name == "step1_merged":
            return load_merged(day_dir)["tokens_flat"]
        return pq.read_table(pq_path).to_pylist()
    js_path = day_dir / f"{name}.json"
    if js_path.exists():
        payload = json.loads(js_path.read_text())
        if name == "step1_merged":
            return _merged_rows_from_json(payload)
        return (payload.get("result") or {}).get("rows") or []
    raise FileNotFoundError(f"{name}: no .parquet or .json under {day_dir}")


def save_rows(day_dir: Path | str, name: str, rows: list[dict[str, Any]], meta: dict | None = None) -> Path:
    day_dir = Path(day_dir)
    day_dir.mkdir(parents=True, exist_ok=True)
    pq_path = day_dir / f"{name}.parquet"
    table = pa.Table.from_pylist(rows)
    if meta:
        table = table.replace_schema_metadata({b"dune": json.dumps(meta).encode()})
    pq.write_table(table, pq_path, compression="zstd")
    return pq_path


def has_rows(day_dir: Path | str, name: str) -> bool:
    try:
        return bool(load_rows(day_dir, name))
    except FileNotFoundError:
        return False


def load_merged(day_dir: Path | str) -> dict[str, Any]:
    """Return {"counts": {...}, "tokens": {bucket: [rec, ...]}, "tokens_flat": [...]}."""
    day_dir = Path(day_dir)
    pq_path = day_dir / "step1_merged.parquet"
    if pq_path.exists():
        table = pq.read_table(pq_path)
        raw_meta = (table.schema.metadata or {}).get(b"counts")
        counts = json.loads(raw_meta) if raw_meta else {}
        flat = table.to_pylist()
        tokens: dict[str, list[dict]] = {}
        for row in flat:
            r = dict(row)
            bucket = r.pop("bucket", None)
            tokens.setdefault(bucket or "unknown", []).append(r)
        if not counts:
            counts = {k: len(v) for k, v in tokens.items()}
        return {"counts": counts, "tokens": tokens, "tokens_flat": flat}
    js_path = day_dir / "step1_merged.json"
    if js_path.exists():
        payload = json.loads(js_path.read_text())
        flat = _merged_rows_from_json(payload)
        return {
            "counts": payload.get("counts") or {},
            "tokens": payload.get("tokens") or {},
            "tokens_flat": flat,
        }
    raise FileNotFoundError(f"step1_merged: no .parquet or .json under {day_dir}")


def save_merged(day_dir: Path | str, counts: dict, tokens: dict[str, list[dict]]) -> Path:
    flat: list[dict] = []
    for bucket, recs in tokens.items():
        for r in recs:
            flat.append({**r, "bucket": bucket})
    day_dir = Path(day_dir)
    day_dir.mkdir(parents=True, exist_ok=True)
    pq_path = day_dir / "step1_merged.parquet"
    table = pa.Table.from_pylist(flat)
    table = table.replace_schema_metadata({b"counts": json.dumps(counts).encode()})
    pq.write_table(table, pq_path, compression="zstd")
    return pq_path


def _merged_rows_from_json(payload: dict) -> list[dict]:
    flat: list[dict] = []
    for bucket, recs in (payload.get("tokens") or {}).items():
        for r in recs:
            flat.append({**r, "bucket": bucket})
    return flat


def convert_dune_json(json_path: Path | str) -> Path | None:
    """Write a parquet sibling for a heavy Dune JSON wrapper. Returns pq path or None."""
    json_path = Path(json_path)
    name = json_path.stem
    if name not in PARQUET_KINDS:
        return None
    if not json_path.exists():
        return None
    payload = json.loads(json_path.read_text())
    if name == "step1_merged":
        counts = payload.get("counts") or {}
        tokens = payload.get("tokens") or {}
        return save_merged(json_path.parent, counts, tokens)
    rows = (payload.get("result") or {}).get("rows") or []
    keep = {k: payload.get(k) for k in ("execution_id", "state", "expires_at") if k in payload}
    return save_rows(json_path.parent, name, rows, meta=keep or None)


def main() -> None:
    """Convert every heavy JSON under research/meme_launch_filter to parquet."""
    import sys

    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("research/meme_launch_filter")
    n = 0
    total_json = total_pq = 0
    for day_dir in sorted(p for p in base.iterdir() if p.is_dir() and p.name.startswith("20")):
        for kind in PARQUET_KINDS:
            jp = day_dir / f"{kind}.json"
            if not jp.exists():
                continue
            total_json += jp.stat().st_size
            pq_path = convert_dune_json(jp)
            if pq_path and pq_path.exists():
                total_pq += pq_path.stat().st_size
                n += 1
                print(f"{pq_path.relative_to(base)}  {jp.stat().st_size/1e6:.1f} MB -> {pq_path.stat().st_size/1e6:.1f} MB")
    print(f"\nconverted {n} files: {total_json/1e6:.1f} MB json -> {total_pq/1e6:.1f} MB parquet")


if __name__ == "__main__":
    main()
