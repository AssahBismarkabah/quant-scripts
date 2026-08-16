import pandas as pd, numpy as np
from scipy import stats
import sys
sys.path.insert(0, 'research/crypto-perps')
import derive_mine5 as dm

def load_res(sym):
    kl = dm.load_klines(f'research/crypto-perps/cache/{sym}_1m.parquet')
    f = dm.load_funding(f'research/crypto-perps/cache/{sym}_funding.parquet')
    return dm.day_frame(kl, f)

def spearman(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    if m.sum() < 10: return np.nan, np.nan, 0
    rho, p = stats.spearmanr(x[m], y[m])
    t = rho*np.sqrt(m.sum()-2)/np.sqrt(max(1-rho**2, 1e-9))
    return rho, t, m.sum()

def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    if m.sum() < 10: return np.nan, np.nan, 0
    r = np.corrcoef(x[m], y[m])[0, 1]
    t = r*np.sqrt(m.sum()-2)/np.sqrt(max(1-r**2, 1e-9))
    return r, t, m.sum()

def gate(res, cut, c1='h1_vol', c2='rest_fwd'):
    m_is = res.index < cut; m_oos = res.index >= cut
    r_is, t_is, n_is = pearson(res.loc[m_is, c1], res.loc[m_is, c2])
    r_oos, t_oos, n_oos = pearson(res.loc[m_oos, c1], res.loc[m_oos, c2])
    ok = np.sign(t_is) == np.sign(t_oos) and abs(t_is) >= 3.29 and abs(t_oos) >= 3.29
    return r_is, t_is, r_oos, t_oos, n_is, n_oos, ok

for sym in ['BTCUSDT', 'ETHUSDT']:
    res = load_res(sym)
    dates = sorted(res.index); cut = dates[int(len(dates)*0.6)]
    print(f'\n########## {sym} ##########')
    print(f'cut {pd.Timestamp(cut).date()}  n={len(res)}')

    m_is = res.index < cut; m_oos = res.index >= cut
    r_is, t_is, n_is = pearson(res.loc[m_is,'h1_vol'], res.loc[m_is,'rest_fwd'])
    r_oos, t_oos, n_oos = pearson(res.loc[m_oos,'h1_vol'], res.loc[m_oos,'rest_fwd'])
    rho_is, trho_is, _ = spearman(res.loc[m_is,'h1_vol'], res.loc[m_is,'rest_fwd'])
    rho_oos, trho_oos, _ = spearman(res.loc[m_oos,'h1_vol'], res.loc[m_oos,'rest_fwd'])
    print(f'Pearson  IS r={r_is:+.4f} t={t_is:+.2f} | OOS r={r_oos:+.4f} t={t_oos:+.2f}')
    print(f'Spearman IS rho={rho_is:+.4f} t={trho_is:+.2f} | OOS rho={rho_oos:+.4f} t={trho_oos:+.2f}')

    trim = res[res['rest_fwd'].abs() < 0.05]
    m_is = trim.index < cut; m_oos = trim.index >= cut
    r_is, t_is, n_is = pearson(trim.loc[m_is,'h1_vol'], trim.loc[m_is,'rest_fwd'])
    r_oos, t_oos, n_oos = pearson(trim.loc[m_oos,'h1_vol'], trim.loc[m_oos,'rest_fwd'])
    print(f'Trim |rest|<5%:  IS r={r_is:+.4f} t={t_is:+.2f} (n={n_is}) | OOS r={r_oos:+.4f} t={t_oos:+.2f} (n={n_oos})')

    m_is = res.index < cut; m_oos = res.index >= cut
    q_is = pd.qcut(res.loc[m_is,'h1_vol'], 5, labels=False).to_numpy()
    q_oos = pd.qcut(res.loc[m_oos,'h1_vol'], 5, labels=False).to_numpy()
    for half, mask, q in [('IS', m_is, q_is), ('OOS', m_oos, q_oos)]:
        idx = res.index[mask]
        row = []
        for k in range(5):
            mean = res.loc[idx[q==k], 'rest_fwd'].mean()
            row.append(f'Q{k+1}={mean*1e4:+.1f}bp')
        print(f'  {half} mean rest-of-day by h1_vol quintile: ' + ' '.join(row))
    idx_is = res.index[m_is]; idx_oos = res.index[m_oos]
    hi = res.loc[idx_is[q_is>=3], 'rest_fwd']; lo = res.loc[idx_is[q_is<3], 'rest_fwd']
    t, p = stats.ttest_ind(hi.dropna(), lo.dropna(), equal_var=False)
    hi2 = res.loc[idx_oos[q_oos>=3], 'rest_fwd']; lo2 = res.loc[idx_oos[q_oos<3], 'rest_fwd']
    t2, p2 = stats.ttest_ind(hi2.dropna(), lo2.dropna(), equal_var=False)
    print(f'  high-Q vs low-Q spread: IS {(hi.mean()-lo.mean())*1e4:+.1f}bp t={t:+.2f} | OOS {(hi2.mean()-lo2.mean())*1e4:+.1f}bp t={t2:+.2f}')

    res['year'] = res.index.year
    print('  by-year: mean rest-of-day (bps) in high vs low h1_vol half (within-year split)')
    for yr, g in res.groupby('year'):
        if len(g) < 100: continue
        med = g['h1_vol'].median()
        hi_y = g.loc[g['h1_vol']>med, 'rest_fwd']; lo_y = g.loc[g['h1_vol']<=med, 'rest_fwd']
        print(f'    {yr}: hi={hi_y.mean()*1e4:+6.1f}bp n={len(hi_y):3d}  lo={lo_y.mean()*1e4:+6.1f}bp n={len(lo_y):3d}')

    res['vol7'] = res['day_ret'].rolling(7).std()
    res['ret7'] = (res['day_ret']+1).rolling(7).apply(np.prod, raw=True) - 1
    res['dow'] = res.index.dayofweek
    ctrl = pd.get_dummies(res['dow'], prefix='dow', drop_first=True)
    X = ctrl.join(res[['vol7','ret7']])
    sub = res[['h1_vol','rest_fwd']].join(X)
    sub = sub.dropna()
    C = sub[X.columns].to_numpy()
    C = np.column_stack([C, np.ones(len(sub))]).astype(float)
    def resid(y):
        beta, *_ = np.linalg.lstsq(C, y.to_numpy(), rcond=None)
        return y.to_numpy() - C @ beta
    rx = resid(sub['h1_vol']); ry = resid(sub['rest_fwd'])
    r_p, t_p, n_p = pearson(rx, ry)
    rho_p, trho_p, _ = spearman(rx, ry)
    print(f'  partial OLS ctrl[dow,vol7,ret7]: Pearson r={r_p:+.4f} t={t_p:+.2f} | Spearman rho={rho_p:+.4f} t={trho_p:+.2f} n={n_p}')

    res['vol6'] = res['day_ret'].rolling(6).std().shift(1)
    sub6 = res[['h1_vol','rest_fwd','vol6']].dropna()
    r_v6, t_v6, n_v6 = pearson(sub6['h1_vol'], sub6['vol6'])
    r_rem, t_rem, n_rem = pearson(sub6['rest_fwd'], sub6['vol6'])
    print(f'  mech check: h1_vol vs PREV-day vol6 r={r_v6:+.4f} | prev vol6 vs rest_fwd r={r_rem:+.4f} (vol-clustering confound)')