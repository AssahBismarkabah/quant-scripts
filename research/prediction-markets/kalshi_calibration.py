import math
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).parent / 'outputs'
BASE = 'https://external-api.kalshi.com/trade-api/v2'
SERIES = 'KXBTC15M'
ERASE = pd.Timestamp('2026-07-18', tz='UTC')


def get(url, params, tries=5):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=60)
            if r.status_code == 200:
                return r.json()
            time.sleep(2 * (i + 1))
        except Exception:
            time.sleep(2 * (i + 1))
    return None


def fee_cents(p):
    return math.ceil(0.07 * p * (1 - p) * 100 - 1e-9)


def main():
    rows = []
    cursor = None
    while True:
        params = {'series_ticker': SERIES, 'limit': 100, 'with_nested_markets': 'true'}
        if cursor:
            params['cursor'] = cursor
        d = get(BASE + '/events', params)
        if not d:
            break
        evs = d.get('events') or []
        for e in evs:
            for m in e.get('markets') or []:
                m = dict(m)
                m['event_ticker'] = e.get('event_ticker')
                rows.append(m)
        cursor = d.get('cursor')
        if not cursor or not evs:
            break
        old = min((e.get('close_time') or '9999') for e in evs)
        print(f'events={len(rows):,} oldest_close={old}', flush=True)
        if old < ERASE.isoformat():
            break
        time.sleep(1.2)
    df = pd.DataFrame(rows).drop_duplicates('ticker')
    df.to_parquet(OUT / 'kalshi_api_btc15m.parquet', index=False)
    print(f'total events w/ markets: {len(df)}', flush=True)

    df['final'] = pd.to_numeric(df['last_price_dollars'], errors='coerce')
    df['up'] = df['result'].astype(str).str.lower().eq('yes').astype(float)
    m = df[df['result'].isin(['yes', 'no']) & df['final'].notna()].copy()
    m = m[m['final'] <= 1.0]
    m['cents'] = m['final'] * 100
    m['bucket'] = pd.cut(m['cents'], bins=list(range(0, 101, 5)),
                         labels=False, include_lowest=True) * 5
    m['fee'] = m['final'].apply(fee_cents)
    print(f'calibration sample: {len(m)} markets '
          f'({m["close_time"].min()} .. {m["close_time"].max()})', flush=True)

    rows_out = []
    for b, g in m.groupby('bucket'):
        n = len(g)
        p_up = g['up'].mean()
        mid = b + 2.5
        rows_out.append({'bucket_pct': b, 'n': n, 'p_up': round(p_up, 4), 'mid': mid,
                         'gross_err_c': round((p_up - mid / 100) * 100, 2),
                         'buy_net_ev_c': round(p_up * 100 - (mid + g['fee'].mean()), 2),
                         'avg_final': round(g['final'].mean(), 3)})
    tab = pd.DataFrame(rows_out)
    tab.to_csv(OUT / 'kalshi_calibration_btc15m.csv', index=False)
    pd.set_option('display.width', 160)
    print(tab.to_string(index=False))
    pos = tab[tab['buy_net_ev_c'] > 0]
    print(f'\nfeasible buckets (buy_net_ev>0): {pos["bucket_pct"].tolist()} '
          f'(n={pos["n"].sum()})')


if __name__ == '__main__':
    main()