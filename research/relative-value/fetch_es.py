"""Fetch + cache ES continuous 1-min OHLCV RTH bars (Databento) for relative-value work.

Same convention as research/nq-vwap-pullback/fetch_bars.py: GLBX.MDP3, ES.n.0
continuous lead contract, 1-minute OHLCV, RTH 09:30..16:00 ET, cached resumably
in research/relative-value/cache/.

Usage: .venv/bin/python research/relative-value/fetch_es.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / "research" / "relative-value" / "cache"
SYMBOL = "ES.n.0"
DATASET = "GLBX.MDP3"
W0 = "2020-08-01"
W1 = "2026-08-07"


def _api_key() -> str:
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == "DATABENTO_API_KEY":
                return v.strip()
    import os
    return os.environ.get("DATABENTO_API_KEY", "")


def _clean(raw) -> None:
    import pandas as pd
    frame = raw.to_df()
    if isinstance(frame.index, pd.DatetimeIndex):
        frame = frame.reset_index()
    for col in ("ts_event", "ts"):
        if col in frame.columns:
            frame["ts"] = pd.to_datetime(frame[col], utc=True)
            break
    frame = frame[frame["ts"].notna()].copy()
    frame["ts"] = frame["ts"].dt.tz_convert("America/New_York")
    frame["open"] = frame["open"].astype(float)
    frame["high"] = frame["high"].astype(float)
    frame["low"] = frame["low"].astype(float)
    frame["close"] = frame["close"].astype(float)
    frame["volume"] = frame["volume"].fillna(0).astype(float)
    import datetime as _dt
    rth_s = _dt.time(9, 30); rth_e = _dt.time(16, 0)
    frame = frame[frame["ts"].dt.time.between(rth_s, rth_e)].copy()
    frame["date"] = frame["ts"].dt.date
    return frame[["ts", "date", "open", "high", "low", "close", "volume"]].sort_values("ts").reset_index(drop=True)


def main() -> None:
    import databento as db
    import pandas as pd
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / "ES_n_0_1m.parquet"
    if cache.exists():
        print("ES cache already exists:", cache)
        return
    client = db.Historical(key=_api_key())
    import datetime as _dt, time as _time, zoneinfo
    etz = zoneinfo.ZoneInfo("America/New_York")
    w0 = pd.Timestamp(W0, tz=etz); w1 = pd.Timestamp(W1, tz=etz)
    boundaries = list(pd.date_range(w0, w1 + pd.Timedelta(days=30), freq="30D"))
    chunk_dir = CACHE_DIR / "chunks"; chunk_dir.mkdir(parents=True, exist_ok=True)
    chunks = []
    for lo, hi in zip(boundaries, boundaries[1:]):
        end = min(hi, w1)
        if end <= lo:
            continue
        cfile = chunk_dir / f"{lo.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.parquet"
        if cfile.exists():
            chunks.append(cfile); continue
        for attempt in range(3):
            try:
                data = client.timeseries.get_range(
                    dataset=DATASET, schema="ohlcv-1m", stype_in="continuous",
                    symbols=[SYMBOL], start=lo.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
                out = _clean(data); out.to_parquet(cfile); chunks.append(cfile); break
            except Exception as exc:
                if attempt == 2:
                    raise
                _time.sleep(10 * (attempt + 1))
    frames = [pd.read_parquet(c) for c in chunks]
    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates(subset="ts", keep="last").sort_values("ts").reset_index(drop=True)
    out.to_parquet(cache)
    print("wrote", cache, "rows", len(out), "span", out["date"].min(), out["date"].max())


if __name__ == "__main__":
    main()
