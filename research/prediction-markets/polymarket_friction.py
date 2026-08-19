import time

import pandas as pd
import requests

OUT = __import__('pathlib').Path(__file__).parent / 'outputs'
GAMMA = 'https://gamma-api.polymarket.com'
DATA = 'https://data-api.polymarket.com'
SLEEP = 0.35
HDR = {'User-Agent': 'Mozilla/5.0'}


def get(url, params, tries=4):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=HDR, timeout=30)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(1.5 * (i + 1))
    return None


def sample_markets():
    found = {}
    for q in ['Bitcoin Up or Down', 'Ethereum Up or Down', 'Solana Up or Down',
              'Dogecoin Up or Down', 'XRP Up or Down', 'BNB Up or Down',
              'Up or Down August', 'Up or Down July', 'Up or Down June']:
        d = get(GAMMA + '/public-search', {'q': q, 'limit_per_page': '30'})
        if not d:
            continue
        for e in d.get('events', []):
            ticker = e.get('ticker', '')
            if 'updown' not in ticker:
                continue
            mks = e.get('markets') or []
            if not mks:
                continue
            m = mks[0]
            clob = (m.get('clobTokenIds') or [''])[0]
            if not clob or not m.get('conditionId'):
                continue
            try:
                vol = float(e.get('volume') or 0)
            except Exception:
                vol = 0
            found[ticker] = {
                'ticker': ticker, 'title': e.get('title'), 'endDate': e.get('endDate'),
                'volume': vol, 'clob': clob, 'conditionId': m['conditionId']}
    df = pd.DataFrame(found.values()).drop_duplicates('conditionId')
    df = df.sort_values('volume', ascending=False)
    print(f'sampled updown markets: {len(df)}', flush=True)
    print(df.head(15)[['ticker', 'volume', 'endDate']].to_string(), flush=True)
    return df


def fetch_trades(condition_id):
    trades = []
    offset = 0
    while True:
        d = get(DATA + '/trades', {'market': condition_id, 'limit': '1000',
                                   'offset': str(offset), 'taker_only': 'false'})
        if not d:
            break
        if not d:
            break
        trades.extend(d)
        if len(d) < 1000:
            break
        offset += 1000
        time.sleep(SLEEP)
    return trades


def drift_stats(trades):
    if len(trades) < 50:
        return None
    tr = pd.DataFrame(trades)
    tr = tr[['timestamp', 'side', 'price', 'size']].dropna()
    tr['t'] = pd.to_numeric(tr['timestamp'], errors='coerce')
    tr['p'] = pd.to_numeric(tr['price'], errors='coerce')
    tr['s'] = pd.to_numeric(tr['size'], errors='coerce')
    tr = tr.dropna().sort_values('t').reset_index(drop=True)
    if len(tr) < 50:
        return None
    t0, t1 = tr['t'].min(), tr['t'].max()
    out = {'trades': len(tr), 'span_min': (t1 - t0) / 60.0}
    for lab, w in [('1m', 60), ('3m', 180), ('5m', 300)]:
        buys = sells = 0.0
        nb = ns = 0
        for row in tr.itertuples():
            fut = tr[(tr['t'] > row.t) & (tr['t'] <= row.t + w)]['p']
            if fut.empty:
                continue
            drift = fut.mean() - row.p
            if row.side == 'BUY':
                buys += drift
                nb += 1
            else:
                sells += drift
                ns += 1
        if nb + ns == 0:
            continue
        out[f'drift_{lab}_after_buy'] = buys / max(nb, 1)
        out[f'drift_{lab}_after_sell'] = sells / max(ns, 1)
        out[f'n_{lab}'] = nb + ns
    out['final'] = tr['p'].iloc[-1]
    out['first'] = tr['p'].iloc[0]
    return out


def main():
    mkt = sample_markets()
    mkt = mkt[mkt['volume'] >= 5000].head(40)
    rows = []
    for i, m in enumerate(mkt.to_dict('records')):
        trades = fetch_trades(m['conditionId'])
        st = drift_stats(trades)
        if not st:
            print(f"[{i}] {m['ticker']} vol=${m['volume']:,.0f} trades_fetched={len(trades)} SKIP", flush=True)
            continue
        st.update({k: m[k] for k in ('ticker', 'title', 'volume', 'endDate')})
        rows.append(st)
        print(f"[{i}] {m['ticker']} vol=${m['volume']:,.0f} trades={st['trades']} span={st['span_min']:.0f}m "
              f"buy5m={st.get('drift_5m_after_buy', float('nan')):+.4f} sell5m={st.get('drift_5m_after_sell', float('nan')):+.4f}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / 'polymarket_friction_summary.csv', index=False)
    if not df.empty:
        print('\n--- aggregate ---', flush=True)
        for lab in ['drift_1m_after_buy', 'drift_1m_after_sell', 'drift_3m_after_buy',
                    'drift_3m_after_sell', 'drift_5m_after_buy', 'drift_5m_after_sell']:
            if lab in df:
                print(f'{lab}: mean={df[lab].mean():+.4f} med={df[lab].median():+.4f} n={df[lab].notna().sum()}', flush=True)
        print(f'\nmarkets: {len(df)}, total trades: {df["trades"].sum():,}', flush=True)


if __name__ == '__main__':
    main()