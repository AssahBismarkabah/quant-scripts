import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).parent / 'outputs'
GAMMA = 'https://gamma-api.polymarket.com'


def main():
    tr = pd.read_parquet(OUT / 'pm_calib_trades.parquet')
    tr['start_epoch'] = tr['slug'].str.rsplit('-', n=1).str[-1].astype(int)
    tr['end'] = tr['start_epoch'] + 900
    tr['yes'] = tr['outcome'].isin(['Yes', 'Up']).astype(int)
    tr['notional'] = tr['price'] * tr['size']

    settled = {}
    for slug in tr['slug'].unique():
        try:
            ev = requests.get(GAMMA + '/events', params={'slug': slug}, timeout=30).json()
            if ev:
                op = ev[0]['markets'][0]['outcomePrices']
                import json
                op = json.loads(op) if isinstance(op, str) else op
                if op in (['1', '0'], ['0', '1']):
                    settled[slug] = op == ['1', '0']
        except Exception:
            pass
        time.sleep(0.15)
    print(f'settled windows: {len(settled)} / {tr["slug"].nunique()}')

    rows = []
    for slug, g in tr.groupby('slug'):
        if slug not in settled:
            continue
        up_won = settled[slug]
        for lbl, mins in (('t300', 300), ('t180', 180), ('t60', 60)):
            w = g[(g['end'] - g['ts'] <= mins) & (g['end'] - g['ts'] > 0)]
            wy = w[w['yes'] == 1]
            if len(wy) >= 3:
                ref = wy['notional'].sum() / wy['size'].sum()
            elif len(wy) >= 1:
                ref = wy.sort_values('ts')['price'].iloc[-1]
            else:
                ref = None
            rows.append({'slug': slug, 'horizon': lbl, 'ref': ref, 'up_won': up_won, 'trades': len(w)})
    df = pd.DataFrame(rows).dropna(subset=['ref'])
    print(f'ref rows: {len(df)}')

    for lbl in ('t300', 't180', 't60'):
        d = df[df['horizon'] == lbl]
        d = d[(d['ref'] >= 0.0) & (d['ref'] <= 1.0)]
        d['bin'] = (d['ref'] * 100 // 5 * 5).clip(0, 95).astype(int)
        agg = d.groupby('bin').agg(n=('up_won', 'size'), up=('up_won', 'sum')).reset_index()
        agg['p_up'] = agg['up'] / agg['n']
        agg['mid'] = agg['bin'] + 2.5
        agg['buy_ev'] = (agg['p_up'] * 100 - agg['mid']) - 1.5
        print(f'\n== PM BTC 15m calibration @ {lbl} (ref = VWAP last {lbl[1:]}s) ==')
        print(agg[['bin', 'n', 'p_up', 'buy_ev']].to_string(index=False))
    df.to_csv(OUT / 'pm_calibration_btc15m.csv', index=False)


if __name__ == '__main__':
    main()