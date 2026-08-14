import pandas as pd, numpy as np

frames = []
for y in range(2010, 2024):
    frames.append(pd.read_parquet(f'research/options/cache/spy_eod_{y}.parquet'))
d = pd.concat(frames, ignore_index=True)
u = d[['[QUOTE_DATE]','[UNDERLYING_LAST]']].drop_duplicates().sort_values('[QUOTE_DATE]').reset_index(drop=True)
u.columns = ['date','px']
u['date'] = pd.to_datetime(u.date)
u['ret_next'] = u.px.pct_change().shift(-1)
u['ret_fwd5'] = u.px.pct_change(5).shift(-5)
u = u[['date','ret_next','ret_fwd5']]

atm = d[(d['[DTE]']>=30) & (d['[DTE]']<=60)].copy()
atm['absdist'] = atm['[STRIKE_DISTANCE_PCT]'].abs()
atm_iv = atm.sort_values('absdist').groupby('[QUOTE_DATE]').first()[['[C_IV]','[P_IV]']]
atm_iv['iv'] = (atm_iv['[C_IV]']+atm_iv['[P_IV]'])/2
iv = atm_iv.reset_index().rename(columns={'[QUOTE_DATE]':'date'})
iv['date'] = pd.to_datetime(iv.date)

d['call_dv'] = d['[C_VOLUME]'].fillna(0) * d['[C_DELTA]'].fillna(0)
d['put_dv'] = d['[P_VOLUME]'].fillna(0) * d['[P_DELTA]'].fillna(0).abs()
flow = d.groupby('[QUOTE_DATE]').apply(lambda g: pd.Series({
    'hedge': (g.call_dv.sum() - g.put_dv.sum()),
    'totvol': (g['[C_VOLUME]'].fillna(0).sum() + g['[P_VOLUME]'].fillna(0).sum()),
}), include_groups=False).reset_index().rename(columns={'[QUOTE_DATE]':'date'})
flow['date'] = pd.to_datetime(flow.date)
flow['hedge_norm'] = flow.hedge / (flow.totvol+1)

m = flow.merge(iv[['date','iv']], on='date').merge(u, on='date')
m['iv_q'] = pd.qcut(m.iv.rank(method='first'), 5, labels=False)
iv_means = m.groupby('iv_q').hedge_norm.transform('mean')
m['hres'] = m.hedge_norm - iv_means
print(f'corr(hedge_norm, iv) = {np.corrcoef(m.hedge_norm, m.iv)[0,1]:.4f}')
print(f'corr(hres, ret_fwd5) = {np.corrcoef(m.hres, m.ret_fwd5)[0,1]:.4f}')

print()
print('=== Obs 3 net-of-IV: hedge residual -> returns (naive) ===')
for hor in ['ret_next','ret_fwd5']:
    q = pd.qcut(m.hres.rank(method='first'), 5, labels=False)
    means = m.assign(q=q).groupby('q')[hor].mean()*1e4
    print(f'{hor}: buckets ' + ' '.join(f'{v:+.1f}' for v in means.values) + f' | spread={(means.iloc[4]-means.iloc[0]):+.1f} bps')

dates = sorted(m.date.unique())
cut = dates[int(len(dates)*0.6)]
print(f'IS/OOS cut {cut.date()}')
for lab, sub in [('IS', m[m.date<cut]), ('OOS', m[m.date>=cut])]:
    q = pd.qcut(sub.hres.rank(method='first'), 5, labels=False)
    means = sub.assign(q=q).groupby('q').ret_fwd5.mean()*1e4
    print(f'{lab} fwd5: ' + ' '.join(f'{v:+.1f}' for v in means.values) + f' | spread={(means.iloc[4]-means.iloc[0]):+.1f} bps')

print()
print('=== Obs 4: skew -> returns (signed distance from strike vs underlying) ===')
sub = d[(d['[DTE]']>=30) & (d['[DTE]']<=60)].copy()
sub['sdist'] = (sub['[STRIKE]'] - sub['[UNDERLYING_LAST]']) / sub['[UNDERLYING_LAST]']
puts = sub[sub.sdist < -0.08].groupby('[QUOTE_DATE]')['[P_IV]'].mean()
calls = sub[sub.sdist > 0.08].groupby('[QUOTE_DATE]')['[C_IV]'].mean()
sk = pd.DataFrame({'put_iv': puts, 'call_iv': calls}).dropna()
sk['skew'] = sk['put_iv'] - sk['call_iv']
sk = sk.reset_index().rename(columns={'[QUOTE_DATE]':'date'})
sk['date'] = pd.to_datetime(sk.date)
m4 = sk.merge(u, on='date')
print(f'n={len(m4)} | skew mean: {m4["skew"].mean()*100:+.1f} pts (normal: puts richer)')
for hor in ['ret_next','ret_fwd5']:
    q = pd.qcut(m4['skew'].rank(method='first'), 5, labels=False)
    means = m4.assign(q=q).groupby('q')[hor].mean()*1e4
    print(f'{hor}: buckets ' + ' '.join(f'{v:+.1f}' for v in means.values) + f' | spread={(means.iloc[4]-means.iloc[0]):+.1f} bps | corr={np.corrcoef(m4["skew"], m4[hor])[0,1]:.4f}')
