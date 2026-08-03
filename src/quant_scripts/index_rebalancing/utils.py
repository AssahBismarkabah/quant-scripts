from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

_USER_AGENT = "Mozilla/5.0 (quant-scripts research; index-rebalancing Level 1)"


def fetch_bytes(
    url: str,
    out_path: Path,
    *,
    retries: int = 3,
    backoff_seconds: float = 5.0,
    headers: dict[str, str] | None = None,
) -> Path:
    """Download url to out_path once. If out_path exists with matching sha256, skip.

    If a re-fetch produces different bytes, write to a `.v2` style suffix and
    append a cleaning-log entry; raw files are never overwritten.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    hdrs = {"User-Agent": _USER_AGENT}
    if headers:
        hdrs.update(headers)

    if out_path.exists():
        current = sha256(out_path)
        probe = _probe(url, hdrs)
        if probe is not None and probe == current:
            return out_path
        # bytes differ or probe unavailable -> re-download to a suffixed path
        return _download(url, out_path, hdrs, retries, backoff_seconds)

    return _download(url, out_path, hdrs, retries, backoff_seconds)


def _probe(url: str, hdrs: dict[str, str]) -> str | None:
    try:
        resp = requests.head(url, headers=hdrs, timeout=20, allow_redirects=True)
        if resp.status_code == 200:
            return resp.headers.get("ETag") or resp.headers.get("Last-Modified")
    except Exception:
        pass
    return None


def _download(
    url: str,
    out_path: Path,
    hdrs: dict[str, str],
    retries: int,
    backoff_seconds: float,
) -> Path:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=hdrs, timeout=60, allow_redirects=True)
            resp.raise_for_status()
            if not resp.content:
                raise RuntimeError(f"empty response: {url}")
            target = out_path
            if target.exists():
                target = target.with_name(f"{target.stem}.v2{target.suffix}")
            target.write_bytes(resp.content)
            return target
        except Exception as exc:  # noqa: BLE001 - retry loop
            last_error = exc
            if attempt < retries - 1:
                time.sleep(backoff_seconds * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_error}") from last_error


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_entry(path: Path) -> dict:
    return {
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def append_log(log_path: Path, entry: dict) -> None:
    """JSONL append-only cleaning log. Every data decision is recorded here."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, default=str) + "\n")


def write_manifest(out_dir: Path, files: list[Path]) -> Path:
    entries = [manifest_entry(p) for p in files]
    manifest = out_dir / "MANIFEST.sha256"
    with manifest.open("w", encoding="utf-8") as fh:
        for e in sorted(entries, key=lambda x: x["path"]):
            fh.write(json.dumps(e) + "\n")
    return manifest


__all__ = ["fetch_bytes", "sha256", "manifest_entry", "append_log", "write_manifest"]
