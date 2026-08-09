"""Fetch PEAD data from the Kaggle "US Historical Stock Prices With Earnings Data"
dataset (tsaustin/us-historical-stock-prices-with-earnings-data).

Reads KAGGLE_USERNAME + KAGGLE_API_TOKEN from the repo ROOT .env (see .env.example),
authenticates the Kaggle API, and downloads the zipped dataset into research/pead/cache/.
Keeps the zip and list of files written to research/pead/cache/manifest.json so a
subsequent run can skip an already-downloaded zip.

Usage: .venv/bin/python research/pead/fetch_pead_data.py
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "research" / "pead" / "cache"
DATASET = "tsaustin/us-historical-stock-prices-with-earnings-data"
ZIP = CACHE / "earnings_dataset.zip"
MANIFEST = CACHE / "manifest.json"


def _env_from_root():
    env = {}
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"')
    return env


def _write_kaggle_json(env: dict) -> tuple[str, str]:
    kdir = Path.home() / ".kaggle"
    kdir.mkdir(parents=True, exist_ok=True)
    kf = kdir / "kaggle.json"
    username = env.get("KAGGLE_USERNAME", "")
    token = env.get("KAGGLE_API_TOKEN", "")
    if not username or not token:
        raise SystemExit("KAGGLE_USERNAME / KAGGLE_API_TOKEN missing from ROOT .env")
    kf.write_text(json.dumps({"username": username, "key": token}))
    os.chmod(kf, stat.S_IRUSR | stat.S_IWUSR)
    return username, token


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    env = _env_from_root()
    username, token = _write_kaggle_json(env)
    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = token

    import kaggle

    kaggle.api.authenticate()

    if ZIP.exists():
        print(f"zip already present: {ZIP} (size {ZIP.stat().st_size/1e6:.1f} MB)")
    else:
        print(f"downloading {DATASET} -> {ZIP.name} ...")
        kaggle.api.dataset_download_files(DATASET, path=str(CACHE), unzip=False)
        # kaggle names the file <dataset-name>.zip
        auto = CACHE / "us-historical-stock-prices-with-earnings-data.zip"
        if auto.exists() and auto != ZIP:
            auto.rename(ZIP)
        if not ZIP.exists():
            raise SystemExit("expected download zip not found")

    # list contents + write manifest
    with zipfile.ZipFile(ZIP) as zf:
        names = zf.namelist()
    sizes = {}
    with zipfile.ZipFile(ZIP) as zf:
        for i in zf.infolist():
            sizes[i.filename] = i.file_size
    MANIFEST.write_text(json.dumps(
        {"dataset": DATASET, "zip": ZIP.name, "zip_bytes": ZIP.stat().st_size,
         "files": [{"name": n, "bytes": sizes.get(n, 0)} for n in names]}, indent=2))
    print(f"zip size: {ZIP.stat().st_size/1e6:.1f} MB")
    print("contents:")
    for n in names:
        print(f"  {n}  ({sizes.get(n,0)/1e6:.1f} MB)")
    print(f"manifest -> {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
