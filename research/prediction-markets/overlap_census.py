import gzip
import re
from datetime import datetime

import pandas as pd

OUT = __import__('pathlib').Path(__file__).parent / 'outputs'

MONTHS = {m: i + 1 for i, m in enumerate(
    ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])}

ASSET_MAP = {
    'KXBTC15M': 'BTC', 'KXETH15M': 'ETH', 'KXDOGE15M': 'DOGE',
    'KXSOL15M': 'SOL', 'KXXRP15M': 'XRP', 'KXBNB15M': 'BNB',
    'KXBTC': 'BTC', 'KXETH': 'ETH', 'KXBTCD': 'BTC', 'KXETHD': 'ETH',
    'KXDOGED': 'DOGE', 'KXDOGE': 'DOGE', 'KXSOL': 'SOL', 'KXXRP': 'XRP',
}
ASSET_Q = {
    'Bitcoin': 'BTC', 'Ethereum': 'ETH', 'Dogecoin': 'DOGE',
    'Solana': 'SOL', 'XRP': 'XRP', 'Ripple': 'XRP', 'BNB': 'BNB',
}


def et_to_key(dt):
    return int(dt.strftime('%Y%m%d%H%M'))


def parse_kalshi_crypto(ev):
    m = re.fullmatch(r'(KX[A-Z0-9]+)-(26)([A-Z]{3})(\d{2})(\d{4})(?:-\d{2})?', ev)
    if not m:
        return None
    series, _, mon, day, hhmm = m.groups()
    asset = ASSET_MAP.get(series)
    if not asset or not series.endswith('15M'):
        return None
    end_et = datetime(2026, MONTHS[mon], int(day), int(hhmm[:2]), int(hhmm[2:]))
    return asset, et_to_key(end_et)


def parse_pm_crypto(q, end_date):
    asset = None
    for name, sym in ASSET_Q.items():
        if re.search(r'\b' + name + r'\b', q):
            asset = sym
            break
    if not asset or 'Up or Down' not in q or pd.isna(end_date):
        return None
    end_utc = pd.to_datetime(end_date, utc=True)
    end_et = end_utc.tz_convert('America/New_York')
    end_key = et_to_key(end_et)
    m = re.search(r'(\d{1,2}):(\d{2}) ?(AM|PM)-(\d{1,2}):(\d{2}) ?(AM|PM) ET', q)
    if m:
        sh, sm, sap, eh, em, eap = m.groups()
        sh = int(sh) % 12 + (12 if sap == 'PM' else 0)
        eh = int(eh) % 12 + (12 if eap == 'PM' else 0)
        start_et = end_et.replace(hour=sh, minute=int(sm), second=0, microsecond=0)
        return asset, et_to_key(start_et), end_key
    return None


def main():
    kalshi = pd.read_csv(gzip.open(OUT / 'kalshi-markets.csv.gz'),
                         usecols=['EVENT_TICKER'])
    evs = kalshi['EVENT_TICKER'].drop_duplicates()
    kc = []
    for ev in evs:
        p = parse_kalshi_crypto(ev)
        if p:
            asset, end_key = p
            kc.append((asset, end_key - 15, end_key, ev))
    kdf = pd.DataFrame(kc, columns=['asset', 'start_key', 'end_key', 'event']).drop_duplicates()
    print(f'Kalshi crypto 15m events: {len(kdf)}', flush=True)
    print(kdf.groupby('asset')['end_key'].count().to_string(), flush=True)

    pm = pd.read_parquet(OUT / 'polymarket_markets.partial.parquet',
                         columns=['id', 'question', 'volumeNum', 'endDate'])
    pc = []
    for q, ed in zip(pm['question'], pm['endDate']):
        p = parse_pm_crypto(q, ed)
        if p:
            pc.append((p[0], p[1], p[2], q))
    pdf = pd.DataFrame(pc, columns=['asset', 'start_key', 'end_key', 'question']).drop_duplicates()
    print(f'Polymarket crypto range-format up/down markets: {len(pdf)}', flush=True)
    print(pdf.groupby('asset')['end_key'].count().to_string(), flush=True)

    merged = kdf.merge(pdf, on=['asset', 'start_key', 'end_key'], how='inner')
    print(f'\n--- OVERLAP (same asset + same [start,end] window) ---')
    print(f'exact 15m windows matched: {merged["end_key"].nunique()}, market pairs: {len(merged)}')
    print(merged.groupby('asset')['end_key'].nunique().to_string())
    merged.to_csv(OUT / 'overlap_crypto.csv', index=False)

    k_only = kdf[~kdf.set_index(['asset', 'start_key', 'end_key']).index.isin(
        merged.set_index(['asset', 'start_key', 'end_key']).index)]
    print(f'\nKalshi-only windows: {len(k_only)}')
    print(k_only.groupby('asset')['end_key'].count().to_string())


if __name__ == '__main__':
    main()