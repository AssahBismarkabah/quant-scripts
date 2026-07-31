from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BinanceCredentials:
    api_key: str
    api_secret: str

    @classmethod
    def from_env(cls, dotenv_path: Path | None = None) -> "BinanceCredentials":
        _load_dotenv(dotenv_path)
        api_key = os.environ.get("BINANCE_API_KEY", "").strip()
        api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()
        if not api_key:
            raise RuntimeError("BINANCE_API_KEY is not set")
        if not api_secret:
            raise RuntimeError("BINANCE_API_SECRET is not set")
        return cls(api_key=api_key, api_secret=api_secret)


@dataclass(frozen=True)
class BinanceSettings:
    base_url: str = "https://api.binance.com"
    futures_base_url: str = "https://fapi.binance.com"


def _load_dotenv(dotenv_path: Path | None = None) -> None:
    env_path = dotenv_path if dotenv_path is not None else Path(__file__).resolve().parents[4] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
