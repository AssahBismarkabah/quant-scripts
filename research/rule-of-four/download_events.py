"""Download Dukascopy event-window data for Probe #24 (Rule of 4).

Fetches 1-minute BID candles from Dukascopy's free jetta API for the DAX and
FTSE index CFDs, aggregates to 5-minute OHLCV, converts timestamps to the
exchange timezone, and writes per-instrument per-year Parquet files with only
the bars around scheduled macro events (NFP / FOMC).

API (verified):
  GET https://jetta.dukascopy.com/v1/candles/minute/{CODE}/{BID}/{yyyy}/{mm}/{dd}
  Response: delta-encoded JSON {timestamp, multiplier, open, high, low, close,
    shift, times, opens, highs, lows, closes, volumes}.
  Codes: DEU.IDX-EUR (Germany 40 index CFD), GBR.IDX-GBP (FTSE 100 index CFD).

Pre-registered conventions (frozen before run):
  - Event times from events/fomc.csv and events/nfp.csv (America/New_York).
  - Window: T-120 min .. T+180 min exchange time (Europe/Berlin for DAX,
    Europe/London for FTSE).
  - T is the event release instant; C1..C5 bars defined in the spec.
  - Output: data/{dax|ftse}/YYYY.parquet, column layout below.

Run: python3 research/rule-of-four/download_events.py [--code DEU.IDX-EUR|GBR.IDX-GBP] [--year 2010]
     With no args, downloads everything not already cached.
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
import urllib.parse
import urllib.request
import zoneinfo
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / "events"
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

SSL_CTX = ssl.create_default_context(cafile="/etc/ssl/cert.pem")

BASE = "https://jetta.dukascopy.com/v1/candles/minute"
WINDOW_MIN = 120   # before T
WINDOW_AFTER = 180  # after T

MARKETS = {
    "DAX": {"code": "DEU.IDX-EUR", "tz": "Europe/Berlin"},
    "FTSE": {"code": "GBR.IDX-GBP", "tz": "Europe/London"},
}

M5 = pd.Timedelta("5min")


def _fetch_json(url: str, retries: int = 3) -> dict | None:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45, context=SSL_CTX) as r:
                if r.status != 200:
                    print(f"  HTTP {r.status}: {url}", flush=True)
                    return None
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001
            print(f"  retry {attempt+1}/{retries}: {e}", flush=True)
            time.sleep(2 * (attempt + 1))
    return None


def decode_candles(data: dict) -> list[list]:
    """Decode delta-encoded candles, gap-filling flat bars, -> [ts,o,h,l,c,v]."""
    length = len(data["times"])
    if length == 0:
        return []
    mult = float(data["multiplier"])
    # getPriceScale: decimals in coefficient minus exponent
    low = str(mult).lower()
    if "e" in low:
        c, e = low.split("e")
    else:
        c, e = low, "0"
    decimal_places = len(c.split(".")[1]) if "." in c else 0
    scale = max(0, decimal_places - int(e))
    def price(u):
        return round(u * mult, scale)
    ts = float(data["timestamp"])
    ou = round(float(data["open"]) / mult)
    hu = round(float(data["high"]) / mult)
    lu = round(float(data["low"]) / mult)
    cu = round(float(data["close"]) / mult)
    prev_cu = cu
    shift = float(data["shift"])
    res = []
    for i in range(length):
        td = int(data["times"][i])
        gap_count = td - (0 if i == 0 else 1)
        for g in range(gap_count):
            flat_ts = ts + (g if i == 0 else g + 1) * shift
            fp = price(prev_cu)
            res.append([flat_ts, fp, fp, fp, fp, 0.0])
        ts += td * shift
        ou += int(data["opens"][i])
        hu += int(data["highs"][i])
        lu += int(data["lows"][i])
        cu += int(data["closes"][i])
        prev_cu = cu
        res.append([ts, price(ou), price(hu), price(lu), price(cu), float(data["volumes"][i])])
    return res


def load_events() -> pd.DataFrame:
    frames = []
    for fname in ("fomc.csv", "nfp.csv"):
        df = pd.read_csv(EVENTS / fname)
        frames.append(df)
    ev = pd.concat(frames, ignore_index=True)
    ev["ts_et"] = pd.to_datetime(ev["date"] + " " + ev["time_et"], format="%Y-%m-%d %H:%M")
    return ev


def day_urls(market, date: pd.Timestamp) -> list[str]:
    return [f"{BASE}/{market['code']}/BID/{date.year}/{date.month:02d}/{date.day:02d}"]


def fetch_day(code: str, date: pd.Timestamp) -> pd.DataFrame | None:
    url = f"{BASE}/{code}/BID/{date.year}/{date.month:02d}/{date.day:02d}"
    data = _fetch_json(url)
    if data is None or not data.get("times"):
        return None
    rows = decode_candles(data)
    df = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
    flat = (df["open"] == df["high"]) & (df["high"] == df["low"]) & (df["low"] == df["close"]) & (df["volume"] == 0)
    df = df[~flat].copy()  # drop gap-fill flat bars (real zero-volume candles with price range are kept)
    df = df[df["low"] <= df["high"]].copy()
    return df


def aggregate_m5(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("ts").copy()
    sec = (df["ts"] // 1000).astype("int64")
    bucket = (sec // (5 * 60)) * (5 * 60)
    df["bucket"] = bucket
    g = df.groupby("bucket").agg(
        open=("open", "first"), high=("high", "max"), low=("low", "min"),
        close=("close", "last"), volume=("volume", "sum"),
    ).reset_index()
    g["ts"] = pd.to_datetime(g["bucket"], unit="s", utc=True)
    return g[["ts", "open", "high", "low", "close", "volume"]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", choices=list(MARKETS), default=None)
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    ev = load_events()
    markets = [args.code] if args.code else list(MARKETS)

    for mkey in markets:
        m = MARKETS[mkey]
        tz = zoneinfo.ZoneInfo(m["tz"])
        ny = zoneinfo.ZoneInfo("America/New_York")
        events = ev.copy()
        events["ts_exch"] = events["ts_et"].dt.tz_localize(ny).dt.tz_convert(tz)
        events = events.sort_values("ts_exch").reset_index(drop=True)
        if args.year:
            events = events[events["ts_exch"].dt.year == args.year]
        out = DATA / mkey.lower()
        out.mkdir(exist_ok=True)

        # group by year to write one parquet per year
        by_year = events.groupby(events["ts_exch"].dt.year)
        total_events = 0
        for year, grp in by_year:
            parq = out / f"{year}.parquet"
            if parq.exists() and not args.force:
                print(f"[{mkey}] {year} exists, skip", flush=True)
                continue
            rows = []
            for _, e in grp.iterrows():
                t0 = e["ts_exch"]
                day_start = t0 - pd.Timedelta(hours=12)
                day_end = t0 + pd.Timedelta(hours=12)
                day = t0.date()
                df = fetch_day(m["code"], pd.Timestamp(day))
                time.sleep(0.4)  # rate-limit politeness
                if df is None:
                    print(f"  [{mkey}] {day} no data", flush=True)
                    continue
                win_start = t0 - pd.Timedelta(minutes=WINDOW_MIN)
                win_end = t0 + pd.Timedelta(minutes=WINDOW_AFTER)
                m5 = aggregate_m5(df)
                m5["ts"] = m5["ts"].dt.tz_convert(tz)
                win = m5[(m5["ts"] >= win_start) & (m5["ts"] < win_end)].copy()
                if win.empty:
                    print(f"  [{mkey}] {day} window empty (t0={t0})", flush=True)
                    continue
                win["event_date"] = str(day)
                win["event_time_exch"] = t0.strftime("%Y-%m-%d %H:%M:%S")
                win["event_type"] = e["type"]
                rows.append(win)
                total_events += 1
                print(f"  [{mkey}] {day} {e['type']} t0={t0.strftime('%H:%M')} bars={len(win)}", flush=True)
            if rows:
                res = pd.concat(rows, ignore_index=True)
                res.to_parquet(parq)
                print(f"[{mkey}] {year}: {len(grp)} events, {len(res)} bars -> {parq.name}", flush=True)
        print(f"[{mkey}] total events processed: {total_events}", flush=True)


if __name__ == "__main__":
    main()