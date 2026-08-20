import json
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).parent / 'outputs'
DATA = 'https://data-api.polymarket.com'

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
    """Fetch trades in [kickoff-3600, kickoff); newest-first via offset, stop when pages cross the window floor."""
    trades = []
    floor = kickoff_epoch - 3600
    offset = 0
    for _ in range(250):
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
    m = pd.read_csv(OUT / 'candidate_a_matches.csv')
    cids = {}
    for _, r in m.iterrows():
        kick = r['pm_home_end'] if pd.notna(r.get('pm_home_end')) else r.get('pm_away_end')
        if pd.isna(kick):
            continue
        kepoch = int(pd.to_datetime(kick, utc=True).timestamp())
        for side in ('home', 'away', 'draw'):
            col = f'pm_{side}_cid'
            if pd.notna(r.get(col)) and r[col] not in cids:
                q = r['pm_home_market'] if side == 'home' else (r['pm_away_market'] if side == 'away' else r['pm_draw_market'])
                cids[r[col]] = (q, side, kepoch)
    cids_list = list(cids.items())
    done_path = OUT / 'candidate_a_fetch_state.json'
    done = set(json.loads(done_path.read_text())) if done_path.exists() else set()
    all_t = []
    p_path = OUT / 'candidate_a_pm_trades.parquet'
    if p_path.exists():
        all_t = pd.read_parquet(p_path).to_dict('records')
    print(f'unique markets: {len(cids_list)} | already done: {len(done)} | cached trades: {len(all_t)}', flush=True)
    for cid, (q, side, kepoch) in cids_list:
        if cid in done:
            continue
        t = fetch_trades_window(cid, kepoch)
        for x in t:
            all_t.append({'cid': cid, 'side': side, 'question': q,
                          'ts': int(x['timestamp']), 'price': float(x['price']),
                          'size': float(x['size']), 'outcome': x.get('outcome')})
        done.add(cid)
        if len(done) % 50 == 0:
            pd.DataFrame(all_t).to_parquet(p_path)
            done_path.write_text(json.dumps(sorted(done)))
            print(f'  {len(done)}/{len(cids_list)} done, {len(all_t)} trades', flush=True)
    pd.DataFrame(all_t).to_parquet(p_path)
    done_path.write_text(json.dumps(sorted(done)))
    print(f'COMPLETE: {len(all_t)} trades -> outputs/candidate_a_pm_trades.parquet', flush=True)

if __name__ == '__main__':
    main()