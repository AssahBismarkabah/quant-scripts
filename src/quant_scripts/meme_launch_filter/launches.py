"""Parse pump.fun launch (create) transactions from RPC responses.

The dry run exists to validate these parsers against real payloads before the
full pull freezes them (spec step 1, failure mode 1: birth records, not snapshots).
"""

from __future__ import annotations

import base64
from dataclasses import dataclass

from .config import CREATE_DISCRIMINATOR, PUMP_PROGRAM


_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58decode(value: str) -> bytes:
    """Decode base58 (Bitcoin-style alphabet, as used by Solana RPC 'json' encodings)."""
    num = 0
    for ch in value:
        num = num * 58 + _B58_ALPHABET.index(ch)
    raw = num.to_bytes((num.bit_length() + 7) // 8, "big")
    pad = 0
    for ch in value:
        if ch == "1":
            pad += 1
        else:
            break
    return b"\x00" * pad + raw


@dataclass(frozen=True)
class CreateRecord:
    signature: str
    block_time: int | None  # unix seconds
    slot: int | None
    mint: str
    creator: str | None
    bonding_curve: str | None
    n_accounts: int


def decode_account(pubkey_raw: object) -> str | None:
    """RPC jsonParsed returns accounts as base58 strings when parsed, else base64 blobs."""
    if isinstance(pubkey_raw, str):
        return pubkey_raw
    return None


def find_create_instruction(tx: dict) -> dict | None:
    """Return the first top-level instruction matching the pump program + create discriminator.

    jsonParsed encoding may present instructions as {'programIdName': ..., 'accounts': [...],
    'data': {'parsed': ...}} or raw. We walk both shapes defensively; the dry run validates
    which shape actually arrives.
    """
    message = (tx.get("transaction") or {}).get("message") or {}
    instructions = message.get("instructions") or []
    for ins in instructions:
        program_id = ins.get("programId") or ins.get("programIdName")
        if program_id != PUMP_PROGRAM:
            continue
        data_field = ins.get("data")
        raw = None
        if isinstance(data_field, dict):
            raw = data_field.get("raw") or (data_field.get("parsed") or {}).get("raw")
        elif isinstance(data_field, str):
            raw = data_field
        if raw is None:
            continue
        decoded = None
        try:
            # json/jsonParsed encodings return raw instruction data as base58.
            decoded = b58decode(raw)
        except (ValueError, KeyError):
            try:
                decoded = base64.b64decode(raw)
            except Exception:
                decoded = None
        if decoded is None or len(decoded) < 8:
            continue
        if bytes(decoded[:8]) == CREATE_DISCRIMINATOR:
            return ins
    return None


def parse_create(tx: dict, signature: str) -> CreateRecord | None:
    """Extract a CreateRecord from a create transaction (account order validated in dry run)."""
    create_ins = find_create_instruction(tx)
    if create_ins is None:
        return None
    accounts = create_ins.get("accounts") or []
    if isinstance(accounts, dict):
        accounts = accounts.get("pubkeys") or []
    # jsonParsed sometimes wraps accounts as [{'pubkey': ...}, ...]; normalize.
    names = []
    for acc in accounts:
        if isinstance(acc, dict):
            names.append(decode_account(acc.get("pubkey")))
        else:
            names.append(decode_account(acc))
    mint = names[0] if len(names) > 0 else None
    creator = names[6] if len(names) > 6 else None
    bonding_curve = names[1] if len(names) > 1 else None
    if mint is None:
        return None
    return CreateRecord(
        signature=signature,
        block_time=tx.get("blockTime"),
        slot=tx.get("slot"),
        mint=mint,
        creator=creator,
        bonding_curve=bonding_curve,
        n_accounts=len(names),
    )
