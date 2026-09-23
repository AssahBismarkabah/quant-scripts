"""Frozen constants for the memecoin launch-filter probe (see spec sections 2, 5, 9.2)."""

from __future__ import annotations

import os
from pathlib import Path

# --- Solana programs (spec section 9.2) ---
PUMP_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
PUMPSWAP_PROGRAM = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"

# Anchor 8-byte discriminator for the pump.fun 'create' instruction.
# Verified against pump IDL mirrors (spec 9.2, AllenHark/SolanaTracker refs).
CREATE_DISCRIMINATOR = bytes([24, 30, 200, 40, 5, 28, 7, 119])

# --- Helius ---
ENV_KEY = "HELIUS_API_KEY"
RPC_URL = "https://mainnet.helius-rpc.com/?api-key={api_key}"

# Free tier allows 10 requests/sec; run under that with headroom.
MAX_RPS = 8.0

# --- Dry run defaults (spec step 1 half-step) ---
DEFAULT_SAMPLE = 300

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "research" / "meme_launch_filter"


def helius_api_key() -> str:
    """Read the Helius key from env or a repo .env file (KEY=VALUE lines)."""
    key = os.environ.get(ENV_KEY)
    if key:
        return key.strip()
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{ENV_KEY}="):
                value = line.split("=", 1)[1].strip()
                if value:
                    return value
    raise RuntimeError(f"{ENV_KEY} not set (env or {env_file})")


# --- Dune (data pipeline pivot, spec section 6 step 1) ---
DUNE_ENV_KEY = "DUNE_API_KEY"
DUNE_API_BASE = "https://api.dune.com/api/v1"


def dune_api_key() -> str:
    """Read the Dune key from env or the same repo .env file."""
    key = os.environ.get(DUNE_ENV_KEY)
    if key:
        return key.strip()
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{DUNE_ENV_KEY}="):
                value = line.split("=", 1)[1].strip()
                if value:
                    return value
    raise RuntimeError(f"{DUNE_ENV_KEY} not set (env or {env_file})")
