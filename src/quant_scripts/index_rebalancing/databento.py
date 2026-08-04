from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from .config import DatabentoCredentials


def client_from_env(dotenv_path: Path | None = None):
    """Create a Databento Historical client, reading the API key from .env."""
    import databento as db

    creds = DatabentoCredentials.from_env(dotenv_path)
    if not creds.api_key:
        raise RuntimeError("DATABENTO_API_KEY not found; source the repo .env first")
    return db.Historical(key=creds.api_key)


def resolve_listing(
    symbol: str,
    start: date,
    end: date,
    *,
    client,
    dataset: str = "EQUS.MINI",
) -> dict:
    """Resolve a raw symbol's listing window in the dataset.

    Returns {"status": ok|partial|not_found, "start_date": date|None,
    "end_date": date|None, "mappings": [...]}.
    """
    result = client.symbology.resolve(
        dataset=dataset,
        symbols=symbol,
        stype_in="raw_symbol",
        stype_out="instrument_id",
        start_date=start,
        end_date=end,
    )
    # response format: {"result": {symbol: [{"d0", "d1", "s"}], ...}, "partial": [], "not_found": []}
    entries = (result.get("result") or {}).get(symbol, [])
    if not entries:
        return {"status": "not_found", "start_date": None, "end_date": None, "mappings": []}
    if symbol in (result.get("not_found") or []):
        return {"status": "not_found", "start_date": None, "end_date": None, "mappings": []}
    mappings = []
    first_start = None
    last_end = None
    for e in entries:
        mapping = {"start_date": e.get("d0"), "end_date": e.get("d1")}
        mappings.append(mapping)
        try:
            d = pd.Timestamp(e["d0"]).date()
            if first_start is None or d < first_start:
                first_start = d
        except Exception:
            pass
        if e.get("d1"):
            try:
                d = pd.Timestamp(e["d1"]).date()
                if last_end is None or d > last_end:
                    last_end = d
            except Exception:
                pass
    status = "ok"
    if first_start is not None and first_start > start:
        status = "partial"
    return {"status": status, "start_date": first_start, "end_date": last_end, "mappings": mappings}


def fetch_daily_bars(
    symbols: list[str],
    start: date,
    end: date,
    *,
    out_dir: Path,
    client,
    dataset: str = "EQUS.MINI",
    schema: str = "ohlcv-1d",
    chunk_size: int = 50,
) -> dict[str, Path]:
    """Fetch ohlcv-1d bars for symbols into per-symbol parquet cache.

    Symbols are batched (chunk_size per resolve/get_range call) so ~1,700
    symbols cost ~40 API requests instead of one round-trip per symbol.
    A failed chunk does not break the batch. Start is clipped to the listing
    date when the symbol was not listed for the whole window. Returns
    {ticker: parquet_path}.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    pending = [s for s in symbols if not (out_dir / f"{s}.parquet").exists()]
    for i in range(0, len(pending), chunk_size):
        chunk = pending[i : i + chunk_size]
        try:
            resolved = client.symbology.resolve(
                dataset=dataset,
                symbols=",".join(chunk),
                stype_in="raw_symbol",
                stype_out="instrument_id",
                start_date=start,
                end_date=end,
            )
        except Exception:
            continue
        results = resolved.get("result") or {}
        listed = {s: e for s, e in results.items() if e}
        if not listed:
            continue
        try:
            store = client.timeseries.get_range(
                dataset=dataset,
                start=start,
                end=end,
                symbols=",".join(listed),
                schema=schema,
                stype_in="raw_symbol",
                stype_out="instrument_id",
            )
        except Exception:
            continue
        try:
            df = store.to_df()
        except Exception:
            continue
        if df is None or df.empty:
            continue
        if "symbol" not in df.columns:
            continue
        for symbol, sub in df.groupby("symbol", sort=False):
            if symbol not in listed:
                continue
            out_path = out_dir / f"{symbol}.parquet"
            _write_bars(sub, out_path)
            paths[symbol] = out_path
    # report symbols that resolve to an instrument but returned no bars
    return paths


def _write_bars(df: pd.DataFrame, out_path: Path) -> None:
    """Normalize a Databento ohlcv-1d frame to {ts_date, open, high, low, close, volume}.

    In ohlcv-1d the ts_event is the DataFrame index (daily bar timestamp);
    for ohlcv-1m it is a column. Both layouts are handled.
    """
    cols = {"open", "high", "low", "close", "volume"}
    keep = [c for c in cols if c in df.columns]
    out = df[keep].copy()
    if "ts_event" in df.columns:
        ts = pd.to_datetime(out["ts_event"], utc=True)
        out = out.drop(columns=["ts_event"])
    else:
        ts = pd.to_datetime(df.index, utc=True)
    out["ts_date"] = ts.date
    out = out.sort_values("ts_date")
    out.to_parquet(out_path, index=False)


def load_bars(ticker: str, bars_dir: Path) -> pd.DataFrame:
    """Load cached daily bars: index ts_date, columns o/h/l/c/volume."""
    path = bars_dir / f"{ticker}.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    if "ts_date" in df.columns:
        df["ts_date"] = pd.to_datetime(df["ts_date"]).dt.date
        return df.set_index("ts_date").sort_index()
    if df.index.name == "ts_date":
        df.index = pd.to_datetime(df.index).date
        return df.sort_index()
    # fallback: index of timestamps
    df.index = pd.to_datetime(df.index).date
    return df.sort_index()


def session_dates(
    start: date,
    end: date,
    *,
    client,
    out_dir: Path,
    benchmark: str = "SPY",
    dataset: str = "EQUS.MINI",
) -> list[date]:
    """Trading calendar from benchmark ETF ohlcv-1d ts_dates, cached."""
    cache_path = out_dir / "calendar.parquet"
    if cache_path.exists():
        df = pd.read_parquet(cache_path)
        return [pd.Timestamp(d).date() for d in df["ts_date"].tolist()]
    out_dir.mkdir(parents=True, exist_ok=True)
    store = client.timeseries.get_range(
        dataset=dataset,
        start=start,
        end=end,
        symbols=benchmark,
        schema="ohlcv-1d",
        stype_in="raw_symbol",
        stype_out="instrument_id",
    )
    df = store.to_df()
    if "ts_event" in df.columns:
        dates = sorted({pd.Timestamp(ts).date() for ts in df["ts_event"]})
    else:
        dates = sorted({pd.Timestamp(ts).date() for ts in df.index})
    pd.DataFrame({"ts_date": [d.isoformat() for d in dates]}).to_parquet(cache_path, index=False)
    return dates


def first_session_after(d: date, calendar: list[date]) -> date | None:
    """First session strictly after d."""
    for s in calendar:
        if s > d:
            return s
    return None


def last_session_at_or_before(d: date, calendar: list[date]) -> date | None:
    result = None
    for s in calendar:
        if s <= d:
            result = s
        else:
            break
    return result


__all__ = [
    "client_from_env",
    "resolve_listing",
    "fetch_daily_bars",
    "load_bars",
    "session_dates",
    "first_session_after",
    "last_session_at_or_before",
]
