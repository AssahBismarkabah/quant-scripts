import pandas as pd, numpy as np

def spearman(x, y):
    rx = pd.Series(x).rank().values
    ry = pd.Series(y).rank().values
    rho = np.corrcoef(rx, ry)[0, 1]
    return rho

d = pd.read_parquet('/tmp/lambda_spy.parquet',
    columns=['date','expiration','strike','type','open_interest','volume','implied_volatility','delta','gamma','mark','bid','ask'])
d['date'] = pd.to_datetime(d['date'])
d['expiration'] = pd.to_datetime(d['expiration'])
d['dte'] = (d['expiration'] - d['date']).dt.days

u = pd.read_parquet('/tmp/lambda_spy_und.parquet')[['date','close']]
u['date'] = pd.to_datetime(u['date'])
u = u.sort_values('date').reset_index(drop=True)
u['ret_next'] = u.close.pct_change().shift(-1)
u['ret_fwd5'] = u.close.pct_change(5).shift(-5)

d = d.merge(u[['date','close','ret_next','ret_fwd5']], on='date', how='left')
d['mn'] = d['strike'] / d['close'] - 1.0
d['absd'] = d['delta'].abs()

def bucket(mn):
    b = pd.cut(mn, [-99,-0.08,-0.02,0.02,0.08,99], labels=['farput','put','atm','call','farcall'])
    return b

d['bk'] = bucket(d['mn'])
d['dg'] = d['open_interest'] * d['gamma'] * d['strike'] * d['close'] * 100
d['dd'] = d['open_interest'] * d['delta'] * d['strike'] * d['close'] * 100
d['spr'] = (d['ask'] - d['bid']) / d['mark'].replace(0, np.nan)

g = d.groupby(['date','bk']).agg(
    oi=('open_interest','sum'), vol=('volume','sum'),
    dg=('dg','sum'), dd=('dd','sum'), spr=('spr','mean'),
    iv=('implied_volatility','mean'), n=('strike','count'))
g = g.unstack('bk')
g.columns = [f'{c}_{l}' for c,l in g.columns]
g = g.reset_index()

d['oi_dte_w'] = d['dte'] * d['open_interest']
day = d.groupby('date').agg(
    tot_oi=('open_interest','sum'), tot_vol=('volume','sum'),
    oi_dte_w=('oi_dte_w','sum'), n_contracts=('strike','count')).reset_index()
day['oi_dte'] = day['oi_dte_w'] / day['tot_oi'].replace(0, np.nan)
day = day.drop(columns=['oi_dte_w'])

print('STEP feat merge', flush=True)
feat = g.merge(day, on='date')
tot = feat.tot_oi.replace(0, np.nan)
feat['turnover_chain'] = feat.tot_vol / tot
feat['turnover_atm'] = feat.vol_atm / feat.oi_atm.replace(0, np.nan)
feat['share_oi_atm'] = feat.oi_atm / tot
feat['share_vol_atm'] = feat.vol_atm / feat.tot_vol.replace(0, np.nan)
feat['share_vol_call'] = (feat.vol_call + feat.vol_farcall) / feat.tot_vol.replace(0, np.nan)
feat['pc_oi'] = (feat.oi_call + feat.oi_farcall) / (feat.oi_put + feat.oi_farput).replace(0, np.nan)
feat['oi_herf'] = (d.groupby('date').apply(lambda x: ((x['open_interest']/x['open_interest'].sum())**2).sum(), include_groups=False))
feat['exp_week_share'] = d[d.dte<7].groupby('date')['open_interest'].sum() / tot
feat['iv_disp'] = d.groupby('date')['implied_volatility'].std()

print('STEP feat->m merge', flush=True)
m = feat.merge(u[['date','ret_next','ret_fwd5']], on='date', how='left')
print('STEP diffs', flush=True)
m['d_oi_atm'] = m.oi_atm.diff()
m['d_oi_call'] = m.oi_call.diff()
m['d_oi_put'] = m.oi_put.diff()
m['d_oi_farput'] = m.oi_farput.diff()
m['d_pc'] = m.pc_oi.diff()
m['d_dg'] = m.dg_atm.diff() + m.dg_call.diff() + m.dg_put.diff()
m['d_dd'] = m.dd_atm.diff() + m.dd_call.diff() + m.dd_put.diff()
m['iv_term'] = m.iv_call - m.iv_farcall
print('STEP set_index+dropna', flush=True)
m = m.set_index('date')

cands = {
 'd_oi_atm': 'dlog OI ATM bucket (d/d)',
 'd_oi_call': 'dlog OI OTM-call bucket (d/d)',
 'd_oi_put': 'dlog OI OTM-put bucket (d/d)',
 'd_oi_farput': 'dlog OI far-put bucket (d/d)',
 'd_pc': 'd PC OI ratio (d/d)',
 'd_dg': 'd dollar gamma (d/d)',
 'd_dd': 'd dollar delta (d/d)',
 'turnover_chain': 'volume/OI chain-wide',
 'turnover_atm': 'volume/OI ATM',
 'share_oi_atm': 'OI share ATM',
 'share_vol_atm': 'volume share ATM',
 'share_vol_call': 'call volume share',
 'pc_oi': 'PC OI ratio (level)',
 'oi_herf': 'OI concentration Herfindahl',
 'oi_dte': 'OI-weighted avg DTE',
 'exp_week_share': 'OI share <7DTE',
 'iv_term': 'IV term (long-short)',
 'iv_disp': 'IV cross-sectional dispersion',
 'spr_atm': 'ATM bid-ask spread',
 'spr_put': 'OTM-put bid-ask spread',
}
horizons = {'ret_next': 'next-day', 'ret_fwd5': 'fwd-5d'}

# also add per-bucket dollar-gamma levels as candidates
for b in ['atm','call','put','farput']:
    cands[f'dg_{b}'] = f'dollar gamma {b} (level)'
    cands[f'oi_{b}'] = f'OI {b} (level)'

n = len(cands)*len(horizons)
t_crit = 3.29  # norm.ppf(1 - 0.05/(2*52)) approx
print(f'candidates: {len(cands)} x {len(horizons)} horizons = {n} tests; Bonferroni |t|>={t_crit:.2f}')

m = m.dropna(subset=['ret_next'])
dates = sorted(m.index)
cut = dates[int(len(dates)*0.6)]
print(f'IS/OOS cut {pd.Timestamp(cut).date()}')

survivors = []
print('STEP candidate loop', flush=True)
for name, lab in cands.items():
    if name not in m.columns or m[name].isna().all():
        continue
    for h, hlab in horizons.items():
        sub = m[m[h].notna()].dropna(subset=[name])
        if len(sub) < 200:
            continue
        is_ = sub[sub.index < cut]; oos = sub[sub.index >= cut]
        ti = stats.ttest_rel if False else None
        r_is = spearman(is_[name], is_[h])
        r_oos = spearman(oos[name], oos[h])
        ti_is = r_is * np.sqrt(len(is_)-2) / np.sqrt(max(1-r_is**2, 1e-9))
        ti_oos = r_oos * np.sqrt(len(oos)-2) / np.sqrt(max(1-r_oos**2, 1e-9))
        if np.sign(ti_is) == np.sign(ti_oos) and abs(ti_is) >= t_crit and abs(ti_oos) >= t_crit:
            survivors.append((name, lab, h, hlab, ti_is, ti_oos, r_is, r_oos))

print(f'\n=== SURVIVORS (IS & OOS same sign, both |t| >= {t_crit:.2f}): {len(survivors)} ===')
for s in survivors:
    print(f'{s[1]:45s} [{s[0]:15s}] {s[3]:8s} tIS={s[4]:+.2f} tOOS={s[5]:+.2f} rhoIS={s[6]:+.4f} rhoOOS={s[7]:+.4f}')

print('\n=== top |t| per horizon (informational, includes non-survivors) ===')
for h in horizons:
    rows = []
    print('STEP candidate loop', flush=True)
    for name, lab in cands.items():
        if name not in m.columns: continue
        sub = m[m[h].notna()].dropna(subset=[name])
        if len(sub) < 200: continue
        is_ = sub[sub.index < cut]; oos = sub[sub.index >= cut]
        r_is = spearman(is_[name], is_[h]); r_oos = spearman(oos[name], oos[h])
        ti_is = r_is * np.sqrt(len(is_)-2) / np.sqrt(max(1-r_is**2, 1e-9))
        ti_oos = r_oos * np.sqrt(len(oos)-2) / np.sqrt(max(1-r_oos**2, 1e-9))
        rows.append((lab, ti_is, ti_oos, r_is, r_oos))
    rows.sort(key=lambda x: abs(x[1]), reverse=True)
    print(f'\n[{h}]')
    for r in rows[:8]:
        print(f'  {r[0]:45s} tIS={r[1]:+.2f} tOOS={r[2]:+.2f} rhoIS={r[3]:+.4f} rhoOOS={r[4]:+.4f}')