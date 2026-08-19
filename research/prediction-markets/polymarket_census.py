import json
import time
from pathlib import Path

import pandas as pd
import requests

SPEC = Path(__file__).parents[1] / 'research-specs/prediction-markets-probe22-spec.md'
OUT = Path(__file__).parent / 'outputs'
OUT.mkdir(exist_ok=True)

BASE = 'https://gamma-api.polymarket.com'
LIMIT = 100
PAGE_SLEEP_S = 0.2
CHECKPOINT_EVERY = 100
MAX_ATTEMPTS = 6
BACKOFF_S = 5
STATE = OUT / 'pm_state.json'
CKPT = OUT / 'polymarket_markets.partial.parquet'
KEEP_FIELDS = [
    'id', 'conditionId', 'question', 'description', 'slug', 'category',
    'startDate', 'endDate', 'closed', 'active', 'volume', 'volume24hr',
    'liquidity', 'outcomePrices', 'outcomes', 'resolutionSource',
    'umaResolutionStatuses', 'feeType', 'feesEnabled', 'takerBaseFee',
    'makerBaseFee', 'orderMinSize', 'orderPriceMinTickSize', 'spread',
    'lastTradePrice', 'negRisk', 'cyom', 'marketType', 'createdAt', 'updatedAt',
]


def fetch(url, params):
    last = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            r = requests.get(url, params=params, timeout=60)
            if r.status_code >= 500:
                raise ConnectionError(f'HTTP {r.status_code}')
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last = e
            if attempt < MAX_ATTEMPTS:
                time.sleep(BACKOFF_S * 2 ** (attempt - 1))
    raise last


def main():
    state = {}
    if STATE.exists():
        state = json.loads(STATE.read_text())
    rows = []
    if CKPT.exists():
        rows = pd.read_parquet(CKPT).to_dict('records')
    cursor = state.get('after_cursor')
    print(f'start/resume rows={len(rows)} cursor={"yes" if cursor else "no"}',
          flush=True)
    page = 0
    while True:
        params = {'limit': LIMIT, 'closed': 'true'}
        if cursor:
            params['after_cursor'] = cursor
        data = fetch(BASE + '/markets/keyset', params)
        batch = data.get('markets') or []
        if not batch:
            break
        rows.extend(batch)
        cursor = data.get('next_cursor')
        STATE.write_text(json.dumps({'after_cursor': cursor or ''}, indent=1))
        page += 1
        if page % CHECKPOINT_EVERY == 0:
            print(f'page={page} rows={len(rows)}', flush=True)
            tmp = CKPT.with_suffix('.parquet.tmp')
            pd.DataFrame(rows).to_parquet(tmp, index=False)
            tmp.replace(CKPT)
        if not cursor:
            print(f'done page={page} rows={len(rows)}', flush=True)
            break
        time.sleep(PAGE_SLEEP_S)

    table = pd.DataFrame(rows).drop_duplicates(subset='conditionId', keep='first')
    for c in KEEP_FIELDS:
        if c not in table.columns:
            table[c] = None
    table = table[KEEP_FIELDS].copy()
    table['_fetched_utc'] = pd.Timestamp.now(tz='UTC').isoformat()
    table.to_parquet(OUT / 'polymarket_markets.parquet', index=False)
    CKPT.unlink(missing_ok=True)
    if STATE.exists():
        STATE.unlink()

    n = len(table)
    closed = int(table['closed'].astype(str).str.lower().isin(['true', '1']).sum())
    vol = pd.to_numeric(table['volume'], errors='coerce').fillna(0)
    liq = pd.to_numeric(table['liquidity'], errors='coerce').fillna(0)
    end_year = pd.to_datetime(table['endDate'], errors='coerce').dt.year
    has_rules = int(table['question'].notna() & table['question'].ne(''))
    has_fee = int(table['feesEnabled'].astype(str).str.lower().isin(['true', '1']).sum())
    fee_types = table['feeType'].value_counts().to_dict()
    taker_fee = pd.to_numeric(table['takerBaseFee'], errors='coerce')
    categories = table['category'].value_counts().head(20).to_dict()

    summary = {
        'fetched_utc': table['_fetched_utc'].iloc[0],
        'total_markets': int(n),
        'closed_markets': closed,
        'markets_with_question_rules': int(has_rules),
        'fees_enabled_share': round(has_fee / n, 4),
        'fee_type_counts': fee_types,
        'taker_base_fee_pct_quantiles': taker_fee.quantile(
            [0.5, 0.9, 0.99]
        ).to_dict() if taker_fee.notna().any() else {},
        'volume_quantiles': vol.quantile([0.5, 0.9, 0.99]).round(0).to_dict(),
        'liquidity_quantiles': liq.quantile([0.5, 0.9, 0.99]).round(0).to_dict(),
        'volume_gt_0_share': round((vol > 0).mean(), 4),
        'by_end_date_year': end_year.value_counts().sort_index().to_dict(),
        'top_categories': categories,
    }
    (OUT / 'polymarket_census_summary.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str)
    )
    print(json.dumps(summary, indent=2, default=str))


if __name__ == '__main__':
    main()
