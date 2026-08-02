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
class ChainRow:
    strike: float
    expiration: datetime
    underlying_symbol: str
    underlying_price: float
    snapshot_time: datetime
    contract_multiplier: float = 100.0
    call_gamma: float = 0.0
    put_gamma: float = 0.0


@dataclass(frozen=True)
class OpenInterestRow:
    option_type: str
    strike: float
    expiration: datetime
    open_interest: float


_CHAIN_ALIASES: dict[str, tuple[str, ...]] = {
    "snapshot_time": ("quote_date", "snapshot_time", "as_of", "date", "trade_date"),
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
    "expiration": ("expiration", "expire_date", "expiry", "expiration_date", "exp_date", "maturity"),
    "gamma": ("gamma", "c_gamma", "p_gamma", "gamma_1545", "gamma_eod"),
    "contract_multiplier": ("contract_multiplier", "multiplier"),
}

_OI_ALIASES: dict[str, tuple[str, ...]] = {
    "option_type": ("option_type", "call_put", "cp_flag", "put_call", "type", "instrument_class"),
    "strike": ("strike", "strike_price", "exercise_price"),
    "expiration": ("expiration", "expire_date", "expiry", "expiration_date", "exp_date", "maturity"),
    "open_interest": ("open_interest", "oi", "open_interest_1545"),
}


def load_optionsdx_chain(path: Path) -> GEXDataPoint:
    rows = list(iter_rows(path))
    if not rows:
        raise ValueError("optionsdx chain export must contain at least one row")

    normalized = [normalize_chain_row(row) for row in rows]
    first = normalized[0]
    contracts: list[GEXContract] = []
    for row in normalized:
        contracts.extend(
            [
                GEXContract(
                    option_type="call",
                    strike=row.strike,
                    expiration=row.expiration,
                    open_interest=0.0,
                    gamma=row.call_gamma,
                    contract_multiplier=row.contract_multiplier,
                ),
                GEXContract(
                    option_type="put",
                    strike=row.strike,
                    expiration=row.expiration,
                    open_interest=0.0,
                    gamma=row.put_gamma,
                    contract_multiplier=row.contract_multiplier,
                ),
            ]
        )
    point = build_gex_data_point(
        snapshot_time=first.snapshot_time,
        underlying_symbol=first.underlying_symbol,
        underlying_price=first.underlying_price,
        contracts=contracts,
        exclude_0dte=True,
    )
    validate_gex_data_point(point)
    return point


def load_databento_open_interest(path: Path) -> list[OpenInterestRow]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else payload.get("rows", payload.get("records", []))
        return [normalize_oi_row(row) for row in rows]
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    return [normalize_oi_row(row) for row in rows]


def merge_optionsdx_with_open_interest(chain_path: Path, oi_path: Path) -> GEXDataPoint:
    chain_point = load_optionsdx_chain(chain_path)
    oi_rows = load_databento_open_interest(oi_path)
    oi_index = {
        _contract_key(row.option_type, row.strike, row.expiration): row.open_interest for row in oi_rows
    }

    contracts = []
    for contract in chain_point.contracts:
        key = _contract_key(contract.option_type, contract.strike, contract.expiration)
        if key not in oi_index:
            raise ValueError(f"missing open interest for contract: {contract.option_type} {contract.strike} {contract.expiration.date()}")
        contracts.append(
            GEXContract(
                option_type=contract.option_type,
                strike=contract.strike,
                expiration=contract.expiration,
                open_interest=oi_index[key],
                gamma=contract.gamma,
                contract_multiplier=contract.contract_multiplier,
            )
        )

    point = build_gex_data_point(
        snapshot_time=chain_point.snapshot_time,
        underlying_symbol=chain_point.underlying_symbol,
        underlying_price=chain_point.underlying_price,
        contracts=contracts,
        exclude_0dte=chain_point.exclude_0dte,
    )
    validate_gex_data_point(point)
    return point


def fetch_databento_open_interest(
    dataset: str,
    symbol: str,
    start: datetime,
    end: datetime,
    schema: str = "statistics",
) -> list[OpenInterestRow]:
    try:
        import databento as db
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "databento is not installed; install the databento client and set DATABENTO_API_KEY"
        ) from exc

    client = db.Historical()
    data = client.timeseries.get_range(
        dataset=dataset,
        symbols=symbol,
        schema=schema,
        stype_in="parent",
        start=start.isoformat(),
        end=end.isoformat(),
    )
    frame = data.to_df().reset_index()
    rows: list[OpenInterestRow] = []
    for _, row in frame.iterrows():
        strike = row.get("strike_price") or row.get("strike") or row.get("exercise_price")
        expiration = row.get("expiration") or row.get("expiry") or row.get("expire_date")
        open_interest = row.get("open_interest")
        instrument_class = row.get("instrument_class") or row.get("call_put") or row.get("cp_flag")
        if strike is None or expiration is None or open_interest is None or instrument_class is None:
            continue
        rows.append(
            OpenInterestRow(
                option_type=_normalize_option_type(str(instrument_class)),
                strike=float(strike),
                expiration=_parse_datetime(str(expiration)),
                open_interest=float(open_interest),
            )
        )
    return rows


def write_databento_open_interest_csv(
    path: Path,
    dataset: str,
    symbol: str,
    start: datetime,
    end: datetime,
    schema: str = "statistics",
) -> None:
    rows = fetch_databento_open_interest(dataset=dataset, symbol=symbol, start=start, end=end, schema=schema)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["option_type", "strike", "expiration", "open_interest"])
        for row in rows:
            writer.writerow([row.option_type, row.strike, row.expiration.isoformat(), row.open_interest])


def write_merged_payload(chain_path: Path, oi_path: Path, output: Path) -> None:
    point = merge_optionsdx_with_open_interest(chain_path, oi_path)
    payload = {
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
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def iter_rows(path: Path) -> Iterable[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            candidates = [name for name in archive.namelist() if name.lower().endswith((".txt", ".csv"))]
            if not candidates:
                raise ValueError("zip archive does not contain a txt or csv export")
            with archive.open(candidates[0]) as handle:
                text = io.TextIOWrapper(handle, encoding="utf-8-sig")
                yield from csv.DictReader(text)
        return
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def normalize_chain_row(row: dict[str, str]) -> ChainRow:
    normalized = {key: _get_value(row, aliases) for key, aliases in _CHAIN_ALIASES.items()}
    missing = [key for key, value in normalized.items() if value in (None, "") and key not in {"contract_multiplier", "underlying_symbol", "option_type"}]
    if missing:
        raise ValueError(f"missing required chain columns: {', '.join(sorted(missing))}")

    return ChainRow(
        strike=float(normalized["strike"]),
        expiration=_parse_datetime(normalized["expiration"]),
        underlying_symbol=str(normalized.get("underlying_symbol") or "SPX").upper(),
        underlying_price=float(normalized["underlying_price"]),
        snapshot_time=_parse_datetime(normalized["snapshot_time"]),
        contract_multiplier=float(normalized.get("contract_multiplier") or 100.0),
        call_gamma=_pick_gamma(row, "call"),
        put_gamma=_pick_gamma(row, "put"),
    )


def normalize_oi_row(row: dict[str, str]) -> OpenInterestRow:
    normalized = {key: _get_value(row, aliases) for key, aliases in _OI_ALIASES.items()}
    missing = [key for key, value in normalized.items() if value in (None, "")]
    if missing:
        raise ValueError(f"missing required open interest columns: {', '.join(sorted(missing))}")
    return OpenInterestRow(
        option_type=_normalize_option_type(str(normalized["option_type"])),
        strike=float(normalized["strike"]),
        expiration=_parse_datetime(normalized["expiration"]),
        open_interest=float(normalized["open_interest"]),
    )


def _pick_gamma(row: dict[str, str], option_type: str) -> float:
    aliases = ("C_GAMMA", "c_gamma", "gamma") if option_type == "call" else ("P_GAMMA", "p_gamma", "gamma")
    value = _get_value(row, aliases)
    if value in (None, ""):
        raise ValueError(f"missing {option_type} gamma column")
    return float(value)


def _contract_key(option_type: str, strike: float, expiration: datetime) -> tuple[str, float, str]:
    return (option_type, round(strike, 6), expiration.date().isoformat())


def _get_value(row: dict[str, str], aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        normalized_alias = _normalize_header(alias)
        for key, value in row.items():
            if key is not None and _normalize_header(key) == normalized_alias:
                return value
    return None


def _parse_datetime(value: str) -> datetime:
    value = value.strip()
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
