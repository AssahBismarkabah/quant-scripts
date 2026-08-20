import math
import json
import random
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests

OUT = Path(__file__).parent / 'outputs'
GAMMA = 'https://gamma-api.polymarket.com'
KALSHI = 'https://api.elections.kalshi.com/trade-api/v2/markets'
ET = ZoneInfo('America/New_York')


def et_key_to_epoch(et_key: str) -> int:
    dt = datetime.strptime(et_key, '%Y%m%d%H%M').replace(tzinfo=ET)
    return int(dt.timestamp())


def get(url, params, tries=6):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=60)
            if r.status_code == 200:
                return r.json()
            time.sleep(1.5 * (i + 1))
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def main():
    ov = pd.read_csv(OUT / 'overlap_crypto.csv')
    random.seed(22)
    idx = random.sample(range(len(ov)), min(1200, len(ov)))
    sample = ov.iloc[idx].copy()

    rows = []
    for _, w in sample.iterrows():
        asset = w['asset'].lower()
        slug = f'{asset}-updown-15m-{et_key_to_epoch(str(w["start_key"]))}'
        want_end = et_key_to_epoch(str(w['end_key']))
        ev = get(GAMMA + '/events', {'slug': slug})
        pm = None
        match = False
        if ev:
            for m in (ev[0].get('markets') or []) if isinstance(ev, list) and ev else []:
                out = m.get('outcomes')
                if isinstance(out, str):
                    try:
                        out = json.loads(out)
                    except Exception:
                        out = None
                if out and out[0] in ('Up', 'Down'):
                    pm = m
                    break
        if pm is None:
            rows.append({'kalshi_event': w['event'], 'asset': w['asset'],
                         'pm_slug': slug, 'pm_found': False})
            continue
        try:
            ev_end = int(datetime.fromisoformat(ev[0]['endDate'].replace('Z', '+00:00')).timestamp())
            match = ev_end == want_end
        except Exception:
            match = False
        op = pm.get('outcomePrices') or []
        if isinstance(op, str):
            try:
                op = json.loads(op)
            except Exception:
                op = []
        p_up = float(op[0]) if len(op) == 2 else None
        rows.append({
            'kalshi_event': w['event'], 'asset': w['asset'], 'pm_slug': slug,
            'pm_found': True, 'pm_window_match': match, 'conditionId': pm.get('conditionId'),
            'pm_up_price': p_up, 'pm_last_trade': _f(pm.get('lastTradePrice')),
            'pm_volume': pm.get('volumeNum'), 'pm_closed': pm.get('closed'),
        })
        time.sleep(0.9)

    div = pd.DataFrame(rows)
    div.to_csv(OUT / 'divergence_crossplatform_raw.csv', index=False)
    hit = div[div['pm_found']]
    print(f'sample: {len(div)} | polymarket found: {len(hit)} | window-matched: {hit["pm_window_match"].sum() if len(hit) else 0}')

    kres = _kalshi_results_and_finals(hit)
    div = div.merge(kres, on='kalshi_event', how='left')
    div['kalshi_up'] = div['kalshi_result'].map({'yes': 1.0, 'no': 0.0})
    div['pm_up_winner'] = div['pm_up_price'].apply(lambda p: 1.0 if p == 1.0 else (0.0 if p == 0.0 else None))
    div['outcome_agree'] = div.apply(
        lambda r: None if pd.isna(r['kalshi_up']) or pd.isna(r['pm_up_winner'])
        else r['kalshi_up'] == r['pm_up_winner'], axis=1)
    both_p = div.dropna(subset=['kalshi_final', 'pm_last_trade'])
    div['final_div_c'] = (div['kalshi_final'] - div['pm_last_trade']) * 100
    div.to_csv(OUT / 'divergence_crossplatform.csv', index=False)

    print('\n== outcome agreement (Kalshi result vs Polymarket winner) ==')
    agg = div['outcome_agree'].dropna()
    if len(agg):
        print(f'  n={len(agg)} | agree={agg.sum():.0f} | disagree={len(agg)-agg.sum():.0f} '
              f'({100*(len(agg)-agg.sum())/len(agg):.3f}%)')
    print('\n== final price divergence (kalshi - polymarket), cents ==')
    d = div['final_div_c'].dropna()
    if len(d):
        print(f'  n={len(d)} | mean={d.mean():+.2f} | std={d.std():.2f} | '
              f'median={d.median():+.2f} | |div|>3c: {(d.abs()>3).sum()} | >10c: {(d.abs()>10).sum()}')
        print('  |div| histogram (cents):')
        h = d.abs().pipe(lambda s: pd.cut(s, [0,1,2,3,5,10,25,50,100]).value_counts().sort_index())
        for k, v in h.items():
            print(f'    {k}: {v}')
    print('\n== disagreement events detail (candidate C events) ==')
    dis = div[div['outcome_agree'] == False][['kalshi_event', 'asset', 'kalshi_result',
                                              'pm_up_price', 'kalshi_final', 'pm_last_trade']]
    print(dis.to_string(index=False) if len(dis) else '  none')


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _kalshi_results_and_finals(div):
    evs = div['kalshi_event'].dropna().unique().tolist()
    cat = pd.read_csv(gzip_open(OUT / 'kalshi-markets.csv.gz'),
                      usecols=['EVENT_TICKER', 'MARKET_TICKER', 'RESULT'], low_memory=False)
    cat = cat.dropna(subset=['RESULT']).drop_duplicates('EVENT_TICKER')
    cat['RESULT'] = cat['RESULT'].astype(str).str.lower()
    res_map = dict(zip(cat['EVENT_TICKER'], cat['RESULT']))
    mt_map = dict(zip(cat['EVENT_TICKER'], cat['MARKET_TICKER']))
    final_map = {}
    for i in range(0, len(evs), 25):
        chunk = [mt_map.get(t) for t in evs[i:i + 25] if mt_map.get(t)]
        if not chunk:
            continue
        d = get(KALSHI, {'tickers': ','.join(chunk)})
        if d:
            for m in d.get('markets') or []:
                final_map[m['ticker'].rsplit('-', 1)[0]] = _f(m.get('last_price_dollars'))
        time.sleep(0.4)
    return pd.DataFrame({'kalshi_event': evs,
                         'kalshi_result': [res_map.get(e) for e in evs],
                         'kalshi_final': [final_map.get(e) for e in evs]})


def gzip_open(p):
    import gzip
    return gzip.open(p)


if __name__ == '__main__':
    main()