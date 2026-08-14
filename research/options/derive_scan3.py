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
u['ret_fwd21'] = u.px.pct_change(21).shift(-21)
u = u[['date','ret_next','ret_fwd5','ret_fwd21']]

# ---- Observation 3: options flow / hedging pressure ----
# net delta demand: call_vol*delta - put_vol*|delta|, summed over chain
d['call_dv'] = d['[C_VOLUME]'].fillna(0) * d['[C_DELTA]'].fillna(0)
d['put_dv'] = d['[P_VOLUME]'].fillna(0) * d['[P_DELTA]'].fillna(0).abs()
flow = d.groupby('[QUOTE_DATE]').apply(lambda g: pd.Series({
    'hedge': (g.call_dv.sum() - g.put_dv.sum()),
    'totvol': (g['[C_VOLUME]'].fillna(0).sum() + g['[P_VOLUME]'].fillna(0).sum()),
}), include_groups=False).reset_index().rename(columns={'[QUOTE_DATE]':'date'})
flow['date'] = pd.to_datetime(flow.date)
flow['hedge_norm'] = flow.hedge / (flow.totvol+1)
m3 = flow.merge(u, on='date')

# ---- Observation 4: skew (OTM put IV - OTM call IV), 30-60 DTE ----
otm = d[(d['[DTE]']>=30) & (d['[DTE]']<=60)].copy()
puts = otm[otm['[STRIKE_DISTANCE_PCT]'] < -0.08].groupby('[QUOTE_DATE]')['[P_IV]'].mean()
calls = otm[otm['[STRIKE_DISTANCE_PCT]'] > 0.08].groupby('[QUOTE_DATE]')['[C_IV]'].mean()
skew = pd.DataFrame({'put_iv': puts, 'call_iv': calls}).dropna()
skew['skew'] = skew.put_iv - skew.call_iv
skew = skew.reset_index().rename(columns={'[QUOTE_DATE]':'date'})
skew['date'] = pd.to_datetime(skew.date)
m4 = skew.merge(u, on='date')

print('=== Observation 3: hedging pressure (call_vol*delta - put_vol*delta) -> SPY return ===')
for hor in ['ret_next','ret_fwd5']:
    q = pd.qcut(m3.hedge_norm.rank(method='first'), 5, labels=False)
    means = m3.assign(q=q).groupby('q')[hor].mean()*1e4
    print(f'{hor}: buckets ' + ' '.join(f'{v:+.1f}' for v in means.values) + f' | spread={(means.iloc[4]-means.iloc[0]):+.1f} bps | corr={np.corrcoef(m3.hedge_norm, m3[hor])[0,1]:.4f}')

print()
print('=== Observation 4: skew (OTM put IV - OTM call IV) -> SPY return ===')
print(f'skew mean: {m4.skew.mean()*100:+.1f} pts')
for hor in ['ret_next','ret_fwd5','ret_fwd21']:
    q = pd.qcut(m4.skew.rank(method='first'), 5, labels=False)
    means = m4.assign(q=q).groupby('q')[hor].mean()*1e4
    print(f'{hor}: buckets ' + ' '.join(f'{v:+.1f}' for v in means.values) + f' | spread={(means.iloc[4]-means.iloc[0]):+.1f} bps | corr={np.corrcoef(m4.skew, m4[hor])[0,1]:.4f}')
