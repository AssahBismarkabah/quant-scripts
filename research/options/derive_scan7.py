import pandas as pd, numpy as np

d = pd.read_parquet('/tmp/lambda_spy.parquet')
d['date'] = pd.to_datetime(d['date'])
u = pd.read_parquet('/tmp/lambda_spy_und.parquet')[['date','close']]
u['date'] = pd.to_datetime(u['date'])
u = u.sort_values('date').reset_index(drop=True)
u.columns = ['date','px']
u['ret_next'] = u.px.pct_change().shift(-1)
u['ret_fwd5'] = u.px.pct_change(5).shift(-5)
u['vol_fwd5'] = u.px.pct_change().rolling(5).std().shift(-5) * 1e4

gex = d.copy()
gex['dollar_gamma'] = gex['open_interest'] * gex['gamma'] * gex['strike'] * gex['mark'] * 100
gex['signed'] = gex['dollar_gamma'] * np.where(gex['type'] == 'call', -1.0, 1.0)
gexd = gex.groupby(['date', 'type'])['signed'].sum().unstack().reset_index()
gexd.columns = ['date', 'gex_call', 'gex_put']
gexd['gex'] = gexd.gex_call + gexd.gex_put
gexd = gexd.reset_index().merge(u, on='date')
gexd['gex_norm'] = gexd.gex / gexd.gex.abs().groupby(gexd.date.dt.year).transform('mean')

m = gexd.dropna(subset=['ret_fwd5'])
print(f'n days: {len(m)}, range {m.date.min().date()} .. {m.date.max().date()}')
print(f'corr(gex, ret_fwd5) = {np.corrcoef(m.gex, m.ret_fwd5)[0,1]:+.4f}')
print(f'corr(gex_norm, ret_fwd5) = {np.corrcoef(m.gex_norm, m.ret_fwd5)[0,1]:+.4f}')
print(f'corr(gex, vol_fwd5) = {np.corrcoef(m.gex, m.vol_fwd5)[0,1]:+.4f}')

for lab, col in [('gex_raw','gex'), ('gex_norm','gex_norm')]:
    print(f'\n=== Dealer gamma ({lab}) -> fwd returns, quintiles ===')
    for hor in ['ret_next','ret_fwd5']:
        q = pd.qcut(m[col].rank(method='first'), 5, labels=False)
        means = m.assign(q=q).groupby('q')[hor].mean()*1e4
        print(f'{hor}: ' + ' '.join(f'{v:+.1f}' for v in means.values) + f' | spread {(means.iloc[4]-means.iloc[0]):+.1f} bps')

    print(f'\n{lab} -> fwd5 realized vol, quintiles (bps/day):')
    q = pd.qcut(m[col].rank(method='first'), 5, labels=False)
    means = m.assign(q=q).groupby('q')['vol_fwd5'].mean()
    print('vol: ' + ' '.join(f'{v:.1f}' for v in means.values) + f' | diff {(means.iloc[4]-means.iloc[0]):+.1f}')

dates = sorted(m.date.unique())
cut = dates[int(len(dates)*0.6)]
print(f'\nIS/OOS cut {cut.date()}')
for lab, sub in [('IS', m[m.date<cut]), ('OOS', m[m.date>=cut])]:
    q = pd.qcut(sub['gex_norm'].rank(method='first'), 5, labels=False)
    means = sub.assign(q=q).groupby('q').ret_fwd5.mean()*1e4
    print(f'{lab} fwd5 gex_norm: ' + ' '.join(f'{v:+.1f}' for v in means.values) + f' | spread {(means.iloc[4]-means.iloc[0]):+.1f} bps')
