from __future__ import annotations

import json
import csv
from datetime import datetime
from pathlib import Path

from .cboe import load_cboe_export_payload
from .models import (
    GEXContract,
    GEXDataPoint,
    IntradayBar,
    build_gex_data_point,
    calculate_dealer_gex,
    classify_regime,
    validate_gex_data_point,
)


def load_gex_point(path: Path) -> tuple[GEXDataPoint, list[IntradayBar]]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")
    if path.suffix.lower() in {".zip"}:
        return load_gex_payload(load_cboe_export_payload(path))
    if path.suffix.lower() == ".csv":
        return load_gex_point_csv(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return load_gex_payload(payload)


def load_gex_point_csv(path: Path) -> tuple[GEXDataPoint, list[IntradayBar]]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    if not rows:
        raise ValueError("csv input must contain at least one row")

    point_row = rows[0]
    point = build_gex_data_point(
        snapshot_time=datetime.fromisoformat(point_row["snapshot_time"]),
        underlying_symbol=point_row["underlying_symbol"],
        underlying_price=float(point_row["underlying_price"]),
        contracts=[
            GEXContract(
                option_type=row["option_type"],
                strike=float(row["strike"]),
                expiration=datetime.fromisoformat(row["expiration"]),
                open_interest=float(row["open_interest"]),
                gamma=float(row["gamma"]),
                contract_multiplier=float(row.get("contract_multiplier", 100.0)),
            )
            for row in rows
            if row.get("record_type", "contract") == "contract"
        ],
        exclude_0dte=point_row.get("exclude_0dte", "true").lower() == "true",
    )
    bars = [
        IntradayBar(
            ts=datetime.fromisoformat(row["ts"]),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
        )
        for row in rows
        if row.get("record_type") == "bar"
    ]
    validate_gex_data_point(point)
    return point, sorted(bars, key=lambda item: item.ts)


def load_gex_payload(payload: dict[str, object]) -> tuple[GEXDataPoint, list[IntradayBar]]:
    point = build_gex_data_point(
        snapshot_time=datetime.fromisoformat(payload["snapshot_time"]),
        underlying_symbol=payload["underlying_symbol"],
        underlying_price=float(payload["underlying_price"]),
        contracts=[
            GEXContract(
                option_type=item["option_type"],
                strike=float(item["strike"]),
                expiration=datetime.fromisoformat(item["expiration"]),
                open_interest=float(item["open_interest"]),
                gamma=float(item["gamma"]),
                contract_multiplier=float(item.get("contract_multiplier", 100.0)),
            )
            for item in payload["contracts"]
        ],
        exclude_0dte=bool(payload.get("exclude_0dte", True)),
    )
    bars = [
        IntradayBar(
            ts=datetime.fromisoformat(item["ts"]),
            open=float(item["open"]),
            high=float(item["high"]),
            low=float(item["low"]),
            close=float(item["close"]),
        )
        for item in payload.get("bars", [])
    ]
    validate_gex_data_point(point)
    return point, sorted(bars, key=lambda item: item.ts)


def load_gex_files(point_path: Path, bars_path: Path | None = None) -> tuple[GEXDataPoint, list[IntradayBar]]:
    point, bars = load_gex_point(point_path)
    if bars_path is not None:
        bars = load_intraday_bars(bars_path)
    return point, bars


def load_session_list(path: Path) -> list[tuple[GEXDataPoint, list[IntradayBar]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [load_gex_payload(item) for item in payload]
    if isinstance(payload, dict) and "sessions" in payload:
        return [load_gex_payload(item) for item in payload["sessions"]]
    return [load_gex_payload(payload)]


def load_intraday_bars(path: Path) -> list[IntradayBar]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")
    if path.suffix.lower() == ".csv":
        return load_intraday_bars_csv(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        bars_payload = payload
    else:
        bars_payload = payload.get("bars", [])
    return sorted(
        [
            IntradayBar(
                ts=datetime.fromisoformat(item["ts"]),
                open=float(item["open"]),
                high=float(item["high"]),
                low=float(item["low"]),
                close=float(item["close"]),
            )
            for item in bars_payload
        ],
        key=lambda item: item.ts,
    )


def load_intraday_bars_csv(path: Path) -> list[IntradayBar]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    return sorted(
        [
            IntradayBar(
                ts=datetime.fromisoformat(row["ts"]),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
            )
            for row in rows
        ],
        key=lambda item: item.ts,
    )


def summarize_input(path: Path) -> dict[str, object]:
    point, bars = load_gex_point(path)
    dealer_gex = calculate_dealer_gex(point)
    return {
        "underlying_symbol": point.underlying_symbol,
        "snapshot_time": point.snapshot_time.isoformat(),
        "contract_count": len(point.contracts),
        "bar_count": len(bars),
        "dealer_gex": dealer_gex,
        "regime": classify_regime(dealer_gex).value,
    }


def normalize_cboe_input(path: Path) -> dict[str, object]:
    return load_cboe_export_payload(path)


def sample_input_payload() -> dict[str, object]:
    return {
        "snapshot_time": "2026-08-01T15:45:00+00:00",
        "underlying_symbol": "SPX",
        "underlying_price": 5000.0,
        "exclude_0dte": True,
        "contracts": [
            {
                "option_type": "call",
                "strike": 5000.0,
                "expiration": "2026-08-02T00:00:00+00:00",
                "open_interest": 1000.0,
                "gamma": 0.02,
                "contract_multiplier": 100.0,
            }
        ],
        "bars": [
            {
                "ts": "2026-08-01T11:30:00+00:00",
                "open": 5000.0,
                "high": 5010.0,
                "low": 4990.0,
                "close": 5000.0,
            },
            {
                "ts": "2026-08-01T13:30:00+00:00",
                "open": 5000.0,
                "high": 5020.0,
                "low": 4995.0,
                "close": 5010.0,
            },
            {
                "ts": "2026-08-01T15:00:00+00:00",
                "open": 5010.0,
                "high": 5025.0,
                "low": 5005.0,
                "close": 5020.0,
            },
        ],
    }


def sample_sessions_payload() -> dict[str, object]:
    return {"sessions": [sample_input_payload(), sample_input_payload()]}


def sample_point_payload() -> dict[str, object]:
    payload = sample_input_payload()
    return {key: value for key, value in payload.items() if key != "bars"}


def sample_bars_payload() -> list[dict[str, object]]:
    return sample_input_payload()["bars"]  # type: ignore[return-value]


def sample_csv_payload() -> str:
    rows = [
        "record_type,snapshot_time,underlying_symbol,underlying_price,exclude_0dte,option_type,strike,expiration,open_interest,gamma,contract_multiplier,ts,open,high,low,close",
        "contract,2026-08-01T15:45:00+00:00,SPX,5000.0,true,call,5000.0,2026-08-02T00:00:00+00:00,1000.0,0.02,100.0,,,,",
        "bar,2026-08-01T15:45:00+00:00,SPX,5000.0,true,,,,,,,2026-08-01T11:30:00+00:00,5000.0,5010.0,4990.0,5000.0",
        "bar,2026-08-01T15:45:00+00:00,SPX,5000.0,true,,,,,,,2026-08-01T13:30:00+00:00,5000.0,5020.0,4995.0,5010.0",
        "bar,2026-08-01T15:45:00+00:00,SPX,5000.0,true,,,,,,,2026-08-01T15:00:00+00:00,5010.0,5025.0,5005.0,5020.0",
    ]
    return "\n".join(rows)
