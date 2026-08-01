from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .models import IntradayBar


@dataclass(frozen=True)
class DatabentoBarRequest:
    dataset: str
    symbol: str
    start: datetime
    end: datetime
    schema: str = "ohlcv-1m"


def load_spy_intraday_bars(path: Path) -> list[IntradayBar]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")
    if path.suffix.lower() == ".csv":
        return load_spy_intraday_bars_csv(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    bars_payload = payload if isinstance(payload, list) else payload.get("bars", [])
    return _parse_bars(bars_payload)


def load_spy_intraday_bars_csv(path: Path) -> list[IntradayBar]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    return _parse_bars(rows)


def write_spy_intraday_bars_json(path: Path, bars: Iterable[IntradayBar]) -> None:
    payload = {
        "symbol": "SPY",
        "bars": [
            {
                "ts": bar.ts.isoformat(),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
            }
            for bar in sorted(bars, key=lambda item: item.ts)
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def fetch_spy_intraday_bars(request: DatabentoBarRequest) -> list[IntradayBar]:
    try:
        import databento as db
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "databento is not installed; install the databento client and set DATABENTO_API_KEY"
        ) from exc

    client = db.Historical()
    data = client.timeseries.get_range(
        dataset=request.dataset,
        symbols=request.symbol,
        schema=request.schema,
        start=request.start.isoformat(),
        end=request.end.isoformat(),
    )
    rows = list(data.to_dicts())
    bars: list[IntradayBar] = []
    for row in rows:
        ts = row.get("ts_event") or row.get("ts") or row.get("timestamp")
        if ts is None:
            continue
        bars.append(
            IntradayBar(
                ts=_coerce_timestamp(ts),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
            )
        )
    return sorted(bars, key=lambda item: item.ts)


def _parse_bars(rows: Iterable[dict[str, object]]) -> list[IntradayBar]:
    bars: list[IntradayBar] = []
    for row in rows:
        ts = row.get("ts") or row.get("ts_event") or row.get("timestamp")
        if ts is None:
            continue
        bars.append(
            IntradayBar(
                ts=_coerce_timestamp(ts),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
            )
        )
    return sorted(bars, key=lambda item: item.ts)


def _coerce_timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    if isinstance(value, int):
        return datetime.fromtimestamp(value / 1_000_000_000, tz=timezone.utc)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)
    raise TypeError(f"unsupported timestamp type: {type(value)!r}")
