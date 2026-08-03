from __future__ import annotations

import csv
import io
import json
import zipfile
from dataclasses import dataclass
from datetime import datetime
from datetime import date
from datetime import time
from zoneinfo import ZoneInfo
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
    as_of: date | None = None


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
    "as_of": ("trade_date", "as_of", "quote_date", "date"),
}


def load_optionsdx_chain(path: Path, snapshot_date: date | None = None, exclude_0dte: bool = False) -> GEXDataPoint:
    rows = list(iter_rows(path))
    if not rows:
        raise ValueError("optionsdx chain export must contain at least one row")

    normalized = [normalize_chain_row(row) for row in rows]
    if snapshot_date is not None:
        normalized = _filter_chain_date(normalized, snapshot_date)
    return _chain_point_from_rows(normalized, exclude_0dte=exclude_0dte)


def _chain_point_from_rows(normalized: list[ChainRow], exclude_0dte: bool = False) -> GEXDataPoint:
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
        exclude_0dte=exclude_0dte,
    )
    validate_gex_data_point(point)
    return point


def _filter_chain_date(normalized: list[ChainRow], snapshot_date: date) -> list[ChainRow]:
    filtered = [row for row in normalized if row.snapshot_time.date() == snapshot_date]
    if not filtered:
        available = sorted({row.snapshot_time.date() for row in normalized})
        raise ValueError(
            "chain export contains no rows for snapshot date "
            f"{snapshot_date.isoformat()}; available dates: "
            f"{', '.join(day.isoformat() for day in available)}"
        )
    return filtered


def load_databento_open_interest(path: Path, as_of: date | None = None) -> list[OpenInterestRow]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else payload.get("rows", payload.get("records", []))
    else:
        rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    normalized = [normalize_oi_row(row) for row in rows]
    if as_of is not None:
        normalized = [row for row in normalized if row.as_of == as_of]
    return _dedupe_open_interest(normalized)


def _dedupe_open_interest(rows: list[OpenInterestRow]) -> list[OpenInterestRow]:
    # Exports may contain repeated snapshots for the same contract (one row per
    # trade date, with no date column). Keep the highest open interest per key so
    # a trailing zero snapshot cannot zero out the real value.
    best: dict[tuple[str, float, str], OpenInterestRow] = {}
    for row in rows:
        key = _contract_key(row.option_type, row.strike, row.expiration)
        existing = best.get(key)
        if existing is None or row.open_interest > existing.open_interest:
            best[key] = row
    return sorted(best.values(), key=lambda row: (row.expiration, row.strike, row.option_type))


def load_optionsdx_rows(path: Path) -> list[ChainRow]:
    rows = list(iter_rows(path))
    if not rows:
        raise ValueError("optionsdx chain export must contain at least one row")
    normalized = []
    for row in rows:
        chain_row = normalize_chain_row(row)
        if chain_row is not None:
            normalized.append(chain_row)
    if not normalized:
        raise ValueError("optionsdx chain export contains no rows with usable greeks")
    return normalized


def merge_optionsdx_with_open_interest(
    chain_path: Path,
    oi_path: Path,
    snapshot_date: date | None = None,
    oi_as_of: date | None = None,
    exclude_0dte: bool = False,
    chain_rows: list[ChainRow] | None = None,
    oi_rows: list[OpenInterestRow] | None = None,
) -> GEXDataPoint:
    if chain_rows is None:
        normalized = load_optionsdx_rows(chain_path)
    else:
        normalized = chain_rows
    if snapshot_date is None:
        snapshot_date = min(row.snapshot_time.date() for row in normalized)
    chain_point = _chain_point_from_rows(
        _filter_chain_date(normalized, snapshot_date),
        exclude_0dte=exclude_0dte,
    )
    if oi_rows is None:
        oi_rows = load_databento_open_interest(oi_path, as_of=oi_as_of)
    elif oi_as_of is not None:
        oi_rows = [row for row in oi_rows if row.as_of == oi_as_of]
    oi_index = {
        _contract_key(row.option_type, row.strike, row.expiration): row.open_interest for row in oi_rows
    }

    contracts = []
    for contract in chain_point.contracts:
        if chain_point.exclude_0dte and contract.expiration.date() == chain_point.snapshot_time.date():
            continue
        key = _contract_key(contract.option_type, contract.strike, contract.expiration)
        contracts.append(
            GEXContract(
                option_type=contract.option_type,
                strike=contract.strike,
                expiration=contract.expiration,
                open_interest=oi_index.get(key, 0.0),
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
    trade_date = start.date()
    cutoff = end
    if cutoff <= start:
        cutoff = datetime.combine(trade_date, time(9, 30), tzinfo=ZoneInfo("America/New_York"))

    def _fetch_definition_frame():
        return client.timeseries.get_range(
            dataset=dataset,
            symbols=symbol,
            schema="definition",
            stype_in="parent",
            start=trade_date,
        ).to_df().reset_index()

    def _fetch_statistics_frame():
        stats = client.timeseries.get_range(
            dataset=dataset,
            symbols=symbol,
            schema=schema,
            stype_in="parent",
            start=trade_date,
            end=cutoff,
        ).to_df().reset_index()
        if "stat_type" not in stats.columns:
            return stats.iloc[0:0]
        return stats[stats["stat_type"].isin((9, "9", "open_interest", "OPEN_INTEREST"))]

    definition = _fetch_definition_frame()
    statistics = _fetch_statistics_frame()
    if definition.empty or statistics.empty:
        return []

    if "symbol" not in definition.columns or "symbol" not in statistics.columns:
        return []

    merged = definition.merge(
        statistics[["symbol", "quantity", "ts_event"]].rename(columns={"ts_event": "oi_ts_event"}),
        on="symbol",
        how="inner",
    )
    rows: list[OpenInterestRow] = []
    for _, row in merged.iterrows():
        strike = row.get("strike_price") or row.get("strike") or row.get("exercise_price")
        expiration = row.get("expiration") or row.get("expiry") or row.get("expire_date")
        instrument_class = row.get("instrument_class") or row.get("call_put") or row.get("cp_flag")
        open_interest = row.get("quantity")
        if strike is None or expiration is None or instrument_class is None or open_interest is None:
            continue
        rows.append(
            OpenInterestRow(
                option_type=_normalize_option_type(str(instrument_class)),
                strike=float(strike),
                expiration=_parse_datetime(str(expiration)),
                open_interest=float(open_interest),
                as_of=pd_to_date(row.get("oi_ts_event")),
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
        writer.writerow(["option_type", "strike", "expiration", "open_interest", "trade_date"])
        for row in rows:
            writer.writerow(
                [
                    row.option_type,
                    row.strike,
                    row.expiration.isoformat(),
                    row.open_interest,
                    row.as_of.isoformat() if row.as_of is not None else "",
                ]
            )


def write_merged_payload(
    chain_path: Path,
    oi_path: Path,
    output: Path,
    snapshot_date: date | None = None,
    oi_as_of: date | None = None,
    exclude_0dte: bool = False,
) -> None:
    point = merge_optionsdx_with_open_interest(
        chain_path,
        oi_path,
        snapshot_date=snapshot_date,
        oi_as_of=oi_as_of,
        exclude_0dte=exclude_0dte,
    )
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


def normalize_chain_row(row: dict[str, str]) -> ChainRow | None:
    lookup = _header_lookup(row)
    normalized = {key: _get_value(lookup, aliases) for key, aliases in _CHAIN_ALIASES.items()}
    missing = [key for key, value in normalized.items() if value in (None, "") and key not in {"contract_multiplier", "underlying_symbol", "option_type"}]
    if missing:
        raise ValueError(f"missing required chain columns: {', '.join(sorted(missing))}")

    call_gamma = _pick_gamma(lookup, "call")
    put_gamma = _pick_gamma(lookup, "put")
    if call_gamma is None or put_gamma is None:
        # unquoted contract row (blank greeks) carries no usable chain data
        return None

    return ChainRow(
        strike=float(normalized["strike"]),
        expiration=_parse_datetime(normalized["expiration"]),
        underlying_symbol=str(normalized.get("underlying_symbol") or "SPX").upper(),
        underlying_price=float(normalized["underlying_price"]),
        snapshot_time=_parse_datetime(normalized["snapshot_time"]),
        contract_multiplier=float(normalized.get("contract_multiplier") or 100.0),
        call_gamma=call_gamma,
        put_gamma=put_gamma,
    )


def normalize_oi_row(row: dict[str, str]) -> OpenInterestRow:
    lookup = _header_lookup(row)
    normalized = {key: _get_value(lookup, aliases) for key, aliases in _OI_ALIASES.items()}
    missing = [key for key, value in normalized.items() if value in (None, "") and key != "as_of"]
    if missing:
        raise ValueError(f"missing required open interest columns: {', '.join(sorted(missing))}")
    return OpenInterestRow(
        option_type=_normalize_option_type(str(normalized["option_type"])),
        strike=float(normalized["strike"]),
        expiration=_parse_datetime(normalized["expiration"]),
        open_interest=float(normalized["open_interest"]),
        as_of=_parse_date(normalized["as_of"]) if normalized.get("as_of") not in (None, "") else None,
    )


def _parse_date(value: str) -> date:
    value = value.strip()
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        raise ValueError(f"invalid date value: {value}")


def pd_to_date(value: object) -> date | None:
    if value is None:
        return None
    try:
        from pandas import Timestamp, NaT
    except ImportError:  # pragma: no cover
        return None
    if value is NaT:
        return None
    if isinstance(value, Timestamp):
        return value.date()
    return _parse_date(str(value))


def _pick_gamma(lookup: dict[str, str], option_type: str) -> float | None:
    aliases = ("C_GAMMA", "c_gamma", "gamma") if option_type == "call" else ("P_GAMMA", "p_gamma", "gamma")
    value = _get_value(lookup, aliases)
    if value in (None, ""):
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return float(cleaned)


def _header_lookup(row: dict[str, str]) -> dict[str, str]:
    return {
        _normalize_header(key): value
        for key, value in row.items()
        if key is not None
    }


def _contract_key(option_type: str, strike: float, expiration: datetime) -> tuple[str, float, str]:
    return (option_type, round(strike, 6), expiration.date().isoformat())


def _get_value(lookup: dict[str, str], aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        value = lookup.get(_normalize_header(alias))
        if value not in (None, ""):
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


def _chunked(values: list[dict[str, object]], size: int) -> Iterable[list[dict[str, object]]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]
