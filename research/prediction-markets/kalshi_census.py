import json
import time
from pathlib import Path

import pandas as pd
import requests

SPEC = Path(__file__).parents[1] / 'research-specs/prediction-markets-probe22-spec.md'
OUT = Path(__file__).parent / 'outputs'
OUT.mkdir(exist_ok=True)

BASE = 'https://external-api.kalshi.com/trade-api/v2'
LIMIT = 1000
PAGE_SLEEP_S = 0.1
CHECKPOINT_EVERY = 100
MAX_ATTEMPTS = 6
BACKOFF_S = 5
STATE = OUT / 'pull_state.json'
KEEP_FIELDS = [
    'ticker', 'event_ticker', 'market_type', 'yes_sub_title', 'no_sub_title',
    'created_time', 'open_time', 'close_time', 'latest_expiration_time',
    'settlement_timer_seconds', 'status', 'notional_value_dollars',
    'yes_bid_dollars', 'yes_ask_dollars', 'no_bid_dollars', 'no_ask_dollars',
    'yes_bid_size_fp', 'yes_ask_size_fp', 'last_price_dollars',
    'previous_price_dollars', 'volume_fp', 'volume_24h_fp', 'open_interest_fp',
    'result', 'can_close_early', 'expiration_value', 'rules_primary',
    'rules_secondary',
]
PHASES = {
    '/markets': {'params': {'status': 'settled'}, 'label': 'live'},
    '/historical/markets': {'params': {}, 'label': 'hist'},
}


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


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {}


def save_state(state):
    STATE.write_text(json.dumps(state, indent=1))


def get_paginated(path, params, label, checkpoint):
    state = load_state()
    entry = state.get(path)
    cursors = entry['cursors'] if entry else []
    rows = []
    if checkpoint.exists() and entry:
        rows = pd.read_parquet(checkpoint).to_dict('records')
    resume = len(rows) // LIMIT
    print(f'{label} start/resume rows={len(rows)} pages={resume}', flush=True)
    cursor = cursors[resume] if resume < len(cursors) else None
    page = resume
    while True:
        q = {'limit': LIMIT}
        q.update(params)
        if cursor:
            q['cursor'] = cursor
        data = fetch(BASE + path, q)
        batch = data.get('markets') or []
        rows.extend(batch)
        cursor = data.get('cursor')
        page += 1
        if len(cursors) > resume:
            cursors = cursors[:resume]
        cursors.append(cursor)
        state[path] = {'params': params, 'cursors': cursors}
        save_state(state)
        if page % CHECKPOINT_EVERY == 0:
            print(f'{label} page={page} rows={len(rows)}', flush=True)
            pd.DataFrame(rows).to_parquet(checkpoint, index=False)
        if not cursor or not batch:
            print(f'{label} done page={page} rows={len(rows)}', flush=True)
            break
        time.sleep(PAGE_SLEEP_S)
    return rows


def main():
    cutoff = fetch(BASE + '/historical/cutoff', {})
    (OUT / 'kalshi_cutoff.json').write_text(
        json.dumps(cutoff, indent=2, sort_keys=True)
    )

    collected = {}
    for path, cfg in PHASES.items():
        ckpt = OUT / f'{cfg["label"]}.partial.parquet'
        rows = get_paginated(path, cfg['params'], cfg['label'], ckpt)
        for row in rows:
            row['_source'] = cfg['label']
        pd.DataFrame(rows).to_parquet(ckpt, index=False)
        collected[cfg['label']] = rows

    table = pd.DataFrame(
        collected['live'] + collected['hist']
    ).drop_duplicates(subset='ticker', keep='first')
    missing = [c for c in KEEP_FIELDS + ['_source'] if c not in table.columns]
    for c in missing:
        table[c] = None
    table = table[KEEP_FIELDS + ['_source']].copy()
    table['_fetched_utc'] = pd.Timestamp.now(tz='UTC').isoformat()
    table.to_parquet(OUT / 'kalshi_markets.parquet', index=False)
    for label, cfg in PHASES.items():
        (OUT / f'{cfg["label"]}.partial.parquet').unlink(missing_ok=True)
    if STATE.exists():
        STATE.unlink()

    n = len(table)
    by_source = table.groupby('_source').size().to_dict()
    by_status = table.groupby('status').size().to_dict()
    by_type = table.groupby('market_type').size().to_dict()
    has_result = int(table['result'].notna() & table['result'].ne(''))
    has_rules = int(table['rules_primary'].notna() & table['rules_primary'].ne(''))
    vol = pd.to_numeric(table['volume_fp'], errors='coerce').fillna(0)
    quantiles = vol.quantile([0.5, 0.9, 0.99, 0.999]).round(0).to_dict()
    close_year = pd.to_datetime(table['close_time'], errors='coerce').dt.year
    by_close_year = close_year.value_counts().sort_index().to_dict()
    final_resolved = table[
        (table['status'].isin(['determined', 'finalized']))
        & (table['result'].isin(['yes', 'no']))
    ]

    summary = {
        'fetched_utc': table['_fetched_utc'].iloc[0],
        'cutoff': cutoff,
        'total_markets': int(n),
        'by_source': by_source,
        'by_status': by_status,
        'by_market_type': by_type,
        'markets_with_result': has_result,
        'markets_with_rules_text': has_rules,
        'resolved_yes_no': int(len(final_resolved)),
        'volume_fp_quantiles': quantiles,
        'by_close_year': by_close_year,
    }
    (OUT / 'kalshi_census_summary.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str)
    )
    print(json.dumps(summary, indent=2, default=str))


if __name__ == '__main__':
    main()
