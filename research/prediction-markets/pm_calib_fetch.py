import json
import random
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).parent / 'outputs'
DATA = 'https://data-api.polymarket.com'
GAMMA = 'https://gamma-api.polymarket.com'
ET_ZONE = None

def get(url, params, tries=5):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=60)
            if r.status_code == 200:
                return r.json()
            time.sleep(1.0 * (i + 1))
        except Exception:
            time.sleep(1.0 * (i + 1))
    return None

def fetch_trades_window(cid, kickoff_epoch):
    trades = []
    floor = kickoff_epoch - 300
    offset = 0
    for _ in range(20):
        p = {'market': cid, 'limit': '1000', 'takerOnly': 'false', 'offset': str(offset)}
        d = get(DATA + '/trades', p)
        if not d:
            break
        page_min = min(t['timestamp'] for t in d)
        trades.extend(t for t in d if t['timestamp'] >= floor)
        if len(d) < 1000 or page_min < floor:
            break
        offset += len(d)
        time.sleep(0.05)
    return trades

def main():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    ET = ZoneInfo('America/New_York')
    random.seed(31)
    cands = []
    for _ in range(600):
        mo = random.choice([6, 7, 8]); d = random.randrange(1, 29); hh = random.randrange(0, 24); mm = random.choice([0, 15, 30, 45])
        try:
            datetime(2026, mo, d, hh, mm)
        except ValueError:
            continue
        cands.append((mo, d, hh, mm))
    cands = list(dict.fromkeys(cands))[:400]
    state_path = OUT / 'pm_calib_fetch_state.json'
    done = set(json.loads(state_path.read_text())) if state_path.exists() else set()
    rows_path = OUT / 'pm_calib_trades.parquet'
    rows = []
    if rows_path.exists():
        rows = pd.read_parquet(rows_path).to_dict('records')
    print(f'sampling {len(cands)} windows | already done: {len(done)} | cached: {len(rows)}', flush=True)
    for mo, d, hh, mm in cands:
        start_et = datetime(2026, mo, d, hh, mm, tzinfo=ET)
        slug = f"btc-updown-15m-{int(start_et.timestamp())}"
        if slug in done:
            continue
        ev = get(GAMMA + '/events', {'slug': slug})
        if not ev:
            done.add(slug); continue
        mkt = ev[0]['markets'][0]
        cid = mkt['conditionId']
        kick = int(datetime.fromisoformat(mkt['endDate'].replace('Z', '+00:00')).timestamp())
        t = fetch_trades_window(cid, kick)
        for x in t:
            rows.append({'slug': slug, 'ts': int(x['timestamp']), 'price': float(x['price']),
                         'size': float(x['size']), 'outcome': x.get('outcome')})
        done.add(slug)
        if len(done) % 50 == 0:
            pd.DataFrame(rows).to_parquet(rows_path)
            state_path.write_text(json.dumps(sorted(done)))
            print(f'  {len(done)}/{len(cands)} done, {len(rows)} trades', flush=True)
    pd.DataFrame(rows).to_parquet(rows_path)
    state_path.write_text(json.dumps(sorted(done)))
    print(f'COMPLETE: {len(rows)} trades -> outputs/pm_calib_trades.parquet', flush=True)

if __name__ == '__main__':
    main()