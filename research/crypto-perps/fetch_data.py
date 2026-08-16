import io, zipfile, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests

CACHE = Path('research/crypto-perps/cache')
RAW = CACHE / 'raw'
CACHE.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)
BASE = 'https://data.binance.vision/data/futures/um/monthly'

KLINE_COLS = ['open_time','open','high','low','close','volume','close_time',
              'quote_volume','count','taker_buy_volume','taker_buy_quote_volume','ignore']

def months(start, end):
    out = []
    d = pd.Period(start, 'M')
    while d <= pd.Period(end, 'M'):
        out.append(d.strftime('%Y-%m'))
        d = d + 1
    return out

def fetch(stream, asset, ym, url):
    local = RAW / f'{stream}_{asset}_{ym}.zip'
    if local.exists():
        return local.read_bytes() or b''
    raw = _fetch(url)
    if raw is None:
        return None
    local.write_bytes(raw)
    return raw

def _fetch(url, attempts=4):
    for i in range(attempts):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.content
        except Exception as e:
            if i == attempts - 1:
                raise
            print(f'retry {url} ({e})', flush=True)

def load_klines(asset, ym):
    url = f'{BASE}/klines/{asset}/1m/{asset}-1m-{ym}.zip'
    raw = fetch('k', asset, ym, url)
    if raw is None:
        return asset, ym, None, 0
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            df = pd.read_csv(f, header=None, names=KLINE_COLS)
    if str(df['open_time'].iloc[0]) == 'open_time':
        df = df.iloc[1:].reset_index(drop=True)
    df['open_time'] = pd.to_numeric(df['open_time'], errors='coerce')
    df = df[['open_time','open','high','low','close']].copy()
    for c in ['open','high','low','close']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return asset, ym, df, len(df)

def load_funding(asset, ym):
    url = f'{BASE}/fundingRate/{asset}/{asset}-fundingRate-{ym}.zip'
    raw = fetch('f', asset, ym, url)
    if raw is None:
        return asset, ym, None, 0
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            df = pd.read_csv(f)
    cols = {c.lower(): c for c in df.columns}
    ft = 'calc_time' if 'calc_time' in cols else ('fundingtime' if 'fundingtime' in cols else 'funding_time')
    fr = 'last_funding_rate' if 'last_funding_rate' in cols else ('fundingrate' if 'fundingrate' in cols else 'funding_rate')
    df = df[[ft, fr]].copy()
    df.columns = ['funding_time','funding_rate']
    if str(df['funding_time'].iloc[0]).lower() in ('fundingtime','calc_time'):
        df = df.iloc[1:].reset_index(drop=True)
    df['funding_time'] = pd.to_numeric(df['funding_time'], errors='coerce')
    df['funding_rate'] = pd.to_numeric(df['funding_rate'], errors='coerce')
    return asset, ym, df, len(df)

def run_stream(assets, yms, loader, out_name, required):
    parts = {a: [] for a in assets}
    rows = {a: 0 for a in assets}
    gaps = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(loader, a, ym) for a in assets for ym in yms]
        for f in as_completed(futs):
            asset, ym, df, n = f.result()
            if df is None:
                gaps.append((asset, ym))
                continue
            parts[asset].append(df)
            rows[asset] += n
            print(f'{asset} {ym}: {n:>8,d} rows', flush=True)
    for a in assets:
        if rows[a] == 0:
            print(f'FATAL: no {required} data for {a}')
            sys.exit(1)
        full = pd.concat(parts[a], ignore_index=True).sort_values('open_time' if 'open_time' in parts[a][0].columns else 'funding_time')
        path = CACHE / out_name.format(a)
        full.to_parquet(path, index=False)
        print(f'== saved {path} total {len(full):,d} rows ==')
    if gaps:
        print('GAPS (404):', gaps)

if __name__ == '__main__':
    assets = ['BTCUSDT', 'ETHUSDT']
    yms = months('2019-09', '2026-07')
    run_stream(assets, yms, load_klines, '{}_1m.parquet', 'kline')
    run_stream(assets, yms, load_funding, '{}_funding.parquet', 'funding')
