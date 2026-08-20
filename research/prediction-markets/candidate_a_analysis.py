from pathlib import Path

import pandas as pd

OUT = Path(__file__).parent / 'outputs'


def main():
    m = pd.read_csv(OUT / 'candidate_a_matches.csv')
    tr = pd.read_parquet(OUT / 'candidate_a_pm_trades.parquet')
    end_map = {}
    for col, endcol in (('pm_home_market', 'pm_home_end'), ('pm_away_market', 'pm_away_end'), ('pm_draw_market', 'pm_home_end')):
        for _, r in m[m[col].notna()].iterrows():
            end_map[r[col]] = r[endcol]
    tr['end'] = pd.to_datetime(tr['question'].map(end_map), utc=True, errors='coerce')
    tr = tr[tr['end'].notna()]
    tr['ts_utc'] = pd.to_datetime(tr['ts'], unit='s', utc=True)
    tr['yes'] = tr['outcome'].eq('Yes').astype(int)
    tr['notional'] = tr['price'] * tr['size']

    kickoff = tr['end'].iloc[0].tz_convert('UTC')
    refs = []
    for cid, g in tr.groupby('cid'):
        g = g[g['ts_utc'] < g['end']]
        if len(g) == 0:
            refs.append({'cid': cid, 'pm_ref': None, 'pm_last': None, 'trades': 0})
            continue
        win = g[g['yes'] == 1]
        if len(win) == 0:
            refs.append({'cid': cid, 'pm_ref': None, 'pm_last': None, 'trades': len(g)})
            continue
        g30 = g[g['ts_utc'] >= (g['end'] - pd.Timedelta(minutes=30))]
        w30 = g30[g30['yes'] == 1]
        if len(w30) >= 3:
            vwap = (w30['notional'].sum() / w30['size'].sum())
        else:
            vwap = win.sort_values('ts_utc')['price'].iloc[-1]
        last = win.sort_values('ts_utc')['price'].iloc[-1]
        refs.append({'cid': cid, 'pm_ref': vwap, 'pm_last': last, 'trades': len(g)})
    ref = pd.DataFrame(refs)
    m = m.merge(ref.rename(columns={'cid': 'pm_home_cid', 'pm_ref': 'pm_h', 'pm_last': 'pm_h_last'}),
                on='pm_home_cid', how='left', suffixes=('', '_h'))
    m = m.merge(ref.rename(columns={'cid': 'pm_away_cid', 'pm_ref': 'pm_a', 'pm_last': 'pm_a_last'}),
                on='pm_away_cid', how='left', suffixes=('', '_a'))
    m = m.merge(ref.rename(columns={'cid': 'pm_draw_cid', 'pm_ref': 'pm_d', 'pm_last': 'pm_d_last'}),
                on='pm_draw_cid', how='left', suffixes=('', '_d'))

    inv = 1.0 / m[['psch', 'pscd', 'psca']].astype(float)
    s3 = inv.sum(axis=1)
    m['p_h'] = inv['psch'] / s3
    m['p_d'] = inv['pscd'] / s3
    m['p_a'] = inv['psca'] / s3

    m['d_h'] = m['pm_h'] - m['p_h']
    m['d_a'] = m['pm_a'] - m['p_a']
    m['d_draw'] = m['pm_d'] - m['p_d']
    m['max_div'] = m[['d_h', 'd_a', 'd_draw']].abs().max(axis=1)

    def result(r):
        if pd.isna(r['fhg']) or pd.isna(r['ftag']):
            return None
        if r['fhg'] > r['ftag']:
            return 'H'
        if r['ftag'] > r['fhg']:
            return 'A'
        return 'D'

    m['res'] = m.apply(result, axis=1)
    pm_win = []
    for _, r in m.iterrows():
        vals = [(r['pm_h'], 'H'), (r['pm_a'], 'A'), (r['pm_d'], 'D')]
        vals = [(p, s) for p, s in vals if pd.notna(p)]
        pm_win.append(max(vals)[1] if vals else None)
    m['pm_pick'] = pm_win
    m['pin_pick'] = m[['p_h', 'p_d', 'p_a']].idxmax(axis=1).map({'p_h': 'H', 'p_d': 'D', 'p_a': 'A'})

    m['pm_correct'] = m.apply(lambda r: r['pm_pick'] == r['res'] if r['res'] and r['pm_pick'] else None, axis=1)
    m['pin_correct'] = m.apply(lambda r: r['pin_pick'] == r['res'] if r['res'] else None, axis=1)

    print(f'fixtures: {len(m)} | with pm_h: {m["pm_h"].notna().sum()} | with pm_a: {m["pm_a"].notna().sum()} | with pm_d: {m["pm_d"].notna().sum()}')
    print(f'full 3-way (h+a+d): {m[["pm_h","pm_a","pm_d"]].notna().all(axis=1).sum()}')
    c = m[m['pm_correct'].notna()]
    print(f'\noutcome picks (n={len(c)}): PM correct {c["pm_correct"].mean()*100:.1f}% | Pinnacle correct {c["pin_correct"].mean()*100:.1f}%')
    print(f'PM==Pinnacle pick: {(m["pm_pick"]==m["pin_pick"]).mean()*100:.1f}%')
    full = m[m[['pm_h', 'pm_a', 'pm_d']].notna().all(axis=1)]
    print(f'\n3-way sum check (n={len(full)}): pm_h+pm_a+pm_d mean {full[["pm_h","pm_a","pm_d"]].sum(axis=1).mean():.3f} vs Pinnacle 1.000')
    print(f'draw: pm_d mean {full["pm_d"].mean():.3f} vs p_d mean {full["p_d"].mean():.3f}')
    print(f'\n== DIVERGENCE CENSUS (|PM - Pinnacle2way|) ==')
    for thr in (0.01, 0.02, 0.04, 0.06, 0.10):
        n = (m['max_div'] > thr).sum()
        print(f'  >{thr*100:.0f}c: {n} fixtures  ({n/len(m)*100:.1f}%)')
    d = m[m['max_div'] > 0.04]
    print(f'\nlargest divergences (>4c): {len(d)}')
    if len(d):
        print(d[['league', 'fd_date', 'home', 'away', 'pm_h', 'pm_a', 'p_h', 'p_a', 'max_div', 'res', 'pm_pick', 'pin_pick']].nlargest(12, 'max_div').to_string())
    m.to_csv(OUT / 'candidate_a_analysis.csv', index=False)
    print('\nsaved outputs/candidate_a_analysis.csv')


if __name__ == '__main__':
    main()