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

atm = d[(d['[DTE]']>=30) & (d['[DTE]']<=60)].copy()
atm['absdist'] = atm['[STRIKE_DISTANCE_PCT]'].abs()
atm_iv = atm.sort_values('absdist').groupby('[QUOTE_DATE]').first()[['[C_IV]','[P_IV]']]
atm_iv['iv'] = (atm_iv['[C_IV]']+atm_iv['[P_IV]'])/2
m = atm_iv.reset_index().rename(columns={'[QUOTE_DATE]':'date'})
m['date'] = pd.to_datetime(m.date)
m = m.merge(u[['date','ret_next','ret_fwd5','ret_fwd21']], on='date').dropna(subset=['ret_fwd5'])

for hor in ['ret_next','ret_fwd5','ret_fwd21']:
    q = pd.qcut(m.iv.rank(method='first'), 5, labels=False)
    means = m.assign(q=q).groupby('q')[hor].mean()*1e4
    print(f'{hor}: buckets ' + ' '.join(f'{v:+.1f}' for v in means.values) + f' | spread={(means.iloc[4]-means.iloc[0]):+.1f} bps | corr={np.corrcoef(m.iv, m[hor])[0,1]:.4f}')

# IS/OOS split (60/40 by date)
dates = sorted(m.date.unique())
cut = dates[int(len(dates)*0.6)]
print('\nIS/OOS split at', cut.date())
for hor in ['ret_fwd5','ret_fwd21']:
    for lab, sub in [('IS', m[m.date<cut]), ('OOS', m[m.date>=cut])]:
        q = pd.qcut(sub.iv.rank(method='first'), 5, labels=False)
        means = sub.assign(q=q).groupby('q')[hor].mean()*1e4
        spread = means.iloc[4]-means.iloc[0]
        print(f'{hor} {lab} ({len(sub)}d): spread={spread:+.1f} bps | corr={np.corrcoef(sub.iv, sub[hor])[0,1]:.4f}')
