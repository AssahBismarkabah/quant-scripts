from __future__ import annotations

import csv
import io
import json
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import GEXContract, GEXDataPoint, build_gex_data_point, validate_gex_data_point


@dataclass(frozen=True)
class CboeOptionRow:
    option_type: str
    strike: float
    expiration: datetime
    open_interest: float
    gamma: float
    underlying_symbol: str
    underlying_price: float
    snapshot_time: datetime
    contract_multiplier: float = 100.0


_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "snapshot_time": ("snapshot_time", "quote_date", "as_of", "date", "trade_date"),
    "underlying_symbol": ("underlying_symbol", "root", "symbol", "underlying", "product"),
    "underlying_price": (
        "underlying_price",
        "active_underlying_price_1545",
        "active_underlying_price",
        "underlying_last",
        "underlying_last_price",
        "spot_price",
    ),
    "option_type": ("option_type", "call_put", "cp_flag", "put_call", "type"),
    "strike": ("strike", "strike_price", "exercise_price"),
    "expiration": ("expiration", "expiry", "expiration_date", "exp_date", "maturity"),
    "open_interest": ("open_interest", "oi", "open_interest_1545"),
    "gamma": ("gamma", "gamma_1545", "gamma1545", "gamma_eod"),
    "contract_multiplier": ("contract_multiplier", "multiplier"),
}


def load_cboe_export(path: Path) -> GEXDataPoint:
    rows = list(iter_cboe_rows(path))
    if not rows:
        raise ValueError("cboe export must contain at least one option row")

    normalized = [normalize_cboe_row(row) for row in rows]
    first = normalized[0]
    contracts = [
        GEXContract(
            option_type=row.option_type,
            strike=row.strike,
            expiration=row.expiration,
            open_interest=row.open_interest,
            gamma=row.gamma,
            contract_multiplier=row.contract_multiplier,
        )
        for row in normalized
    ]
    point = build_gex_data_point(
        snapshot_time=first.snapshot_time,
        underlying_symbol=first.underlying_symbol,
        underlying_price=first.underlying_price,
        contracts=contracts,
        exclude_0dte=True,
    )
    validate_gex_data_point(point)
    return point


def load_cboe_export_payload(path: Path) -> dict[str, object]:
    point = load_cboe_export(path)
    return {
        "snapshot_time": point.snapshot_time.isoformat(),
        "underlying_symbol": point.underlying_symbol,
        "underlying_price": point.underlying_price,
        "exclude_0dte": point.exclude_0dte,
        "contracts": [
            {
                "option_type": contract.option_type,
                "strike": contract.strike,
                "expiration": contract.expiration.isoformat(),
                "open_interest": contract.open_interest,
                "gamma": contract.gamma,
                "contract_multiplier": contract.contract_multiplier,
            }
            for contract in point.contracts
        ],
    }


def write_cboe_normalized_payload(path: Path, output: Path) -> None:
    payload = load_cboe_export_payload(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_cboe_normalized_point(path: Path, output: Path) -> None:
    write_cboe_normalized_payload(path, output)


def iter_cboe_rows(path: Path) -> Iterable[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            csv_members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_members:
                raise ValueError("zip archive does not contain a csv export")
            with archive.open(csv_members[0]) as handle:
                text = io.TextIOWrapper(handle, encoding="utf-8-sig")
                yield from csv.DictReader(text)
        return

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def normalize_cboe_row(row: dict[str, str]) -> CboeOptionRow:
    normalized = {key: _get_value(row, aliases) for key, aliases in _COLUMN_ALIASES.items()}
    missing = [key for key, value in normalized.items() if value in (None, "") and key != "contract_multiplier"]
    if missing:
        raise ValueError(f"missing required cboe columns: {', '.join(sorted(missing))}")

    snapshot_time = _parse_datetime(normalized["snapshot_time"])
    expiration = _parse_datetime(normalized["expiration"])
    option_type = _normalize_option_type(str(normalized["option_type"]))
    underlying_symbol = str(normalized["underlying_symbol"]).upper()

    return CboeOptionRow(
        option_type=option_type,
        strike=float(normalized["strike"]),
        expiration=expiration,
        open_interest=float(normalized["open_interest"]),
        gamma=float(normalized["gamma"]),
        underlying_symbol=underlying_symbol,
        underlying_price=float(normalized["underlying_price"]),
        snapshot_time=snapshot_time,
        contract_multiplier=float(normalized.get("contract_multiplier") or 100.0),
    )


def _get_value(row: dict[str, str], aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        normalized_alias = _normalize_header(alias)
        for key, value in row.items():
            if key is not None and _normalize_header(key) == normalized_alias:
                return value
    return None


def _parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        if len(value) == 10:
            return datetime.fromisoformat(f"{value}T00:00:00")
        raise


def _normalize_option_type(value: str) -> str:
    cleaned = value.strip().lower()
    if cleaned in {"c", "call", "calls"}:
        return "call"
    if cleaned in {"p", "put", "puts"}:
        return "put"
    return cleaned


def _normalize_header(value: str) -> str:
    return "".join(ch for ch in value.strip().lower() if ch.isalnum())
