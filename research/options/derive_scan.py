import pandas as pd, numpy as np

# load all years
frames = []
for y in range(2010, 2024):
    df = pd.read_parquet(f'research/options/cache/spy_eod_{y}.parquet')
    frames.append(df)
d = pd.concat(frames, ignore_index=True)
print('total rows:', len(d), '| dates:', d['[QUOTE_DATE]'].nunique(), '| range:', d['[QUOTE_DATE]'].min(), '->', d['[QUOTE_DATE]'].max())

# use underlying close as the price series
u = d[['[QUOTE_DATE]','[UNDERLYING_LAST]']].drop_duplicates().sort_values('[QUOTE_DATE]').reset_index(drop=True)
u.columns = ['date','px']
u['ret_next'] = u.px.pct_change().shift(-1)
u['ret_fwd5'] = u.px.pct_change(5).shift(-5)

# Observation 1: put/call volume ratio (sentiment/hedging flow)
d['date'] = d['[QUOTE_DATE]']
pv = d.groupby('date').apply(lambda g: pd.Series({
    'call_vol': g['[C_VOLUME]'].fillna(0).sum(),
    'put_vol': g['[P_VOLUME]'].fillna(0).sum(),
}), include_groups=False).reset_index()
pv['pc_ratio'] = pv.put_vol/(pv.call_vol+1)
m1 = pv.merge(u[['date','ret_next']], on='date')

# Observation 2: ATM IV (30-60 DTE, closest to money) -> future realized vol / return
atm = d[(d['[DTE]']>=30) & (d['[DTE]']<=60)].copy()
atm['absdist'] = atm['[STRIKE_DISTANCE_PCT]'].abs()
atm_iv = atm.sort_values('absdist').groupby('date').first()[['[C_IV]','[P_IV]','[UNDERLYING_LAST]']]
atm_iv.columns = ['civ','piv','px']
atm_iv['iv'] = (atm_iv.civ + atm_iv.piv)/2
m2 = atm_iv.merge(u[['date','ret_next','ret_fwd5']], on='date')

print()
print('=== Observation 1: put/call volume ratio -> next-day SPY return ===')
r = np.corrcoef(m1.pc_ratio, m1.ret_next)[0,1]
q = pd.qcut(m1.pc_ratio.rank(method='first'), 5, labels=False)
means = m1.assign(q=q).groupby('q').ret_next.mean()*1e4
print(f'corr={r:.4f} | buckets (bps): ' + ' '.join(f'{v:+.1f}' for v in means.values) + f' | spread={(means.iloc[4]-means.iloc[0]):+.1f} bps')

print()
print('=== Observation 2: ATM IV vs realized (VRP level check) ===')
m2['realized_next'] = m2.px.pct_change().rolling(20).std().shift(-20)*np.sqrt(252)
vrp = m2.dropna(subset=['realized_next'])
print(f'n={len(vrp)} | mean IV={vrp.iv.mean()*100:.1f}% | mean fwd 20d realized={vrp.realized_next.mean()*100:.1f}% | VRP={((vrp.iv.mean()-vrp.realized_next.mean())*100):+.1f} pts')
r = np.corrcoef(vrp.iv, vrp.ret_fwd5)[0,1]
print(f'corr(ATM IV, fwd 5d ret)={r:.4f}')
q = pd.qcut(vrp.iv.rank(method='first'), 5, labels=False)
means = vrp.assign(q=q).groupby('q').ret_fwd5.mean()*1e4
print('IV quintile -> fwd 5d ret (bps): ' + ' '.join(f'{v:+.1f}' for v in means.values))
