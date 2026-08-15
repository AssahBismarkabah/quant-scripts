import pandas as pd, numpy as np

p = pd.read_parquet('research/pead/cache/prices_adj_long.parquet')
p['date'] = pd.to_datetime(p['date'])
p = p.sort_values(['symbol','date']).reset_index(drop=True)

g = p.groupby('symbol', sort=False)
px = p['close_adjusted']
p2 = p.copy()
p2['ret5'] = g['close_adjusted'].transform(lambda s: s.pct_change(5))
p2['ret21'] = g['close_adjusted'].transform(lambda s: s.pct_change(21))
p2['ret63'] = g['close_adjusted'].transform(lambda s: s.pct_change(63))
p2['vol63'] = g['close_adjusted'].transform(lambda s: s.pct_change().rolling(63).std())
p2['hi63'] = g['close_adjusted'].transform(lambda s: s.rolling(63).max())
p2['lo63'] = g['close_adjusted'].transform(lambda s: s.rolling(63).min())
p2['hi252'] = g['close_adjusted'].transform(lambda s: s.rolling(252).max())
p2['lo252'] = g['close_adjusted'].transform(lambda s: s.rolling(252).min())
p2['avg252'] = g['close_adjusted'].transform(lambda s: s.rolling(252).mean())
p2['fwd21'] = g['close_adjusted'].transform(lambda s: s.shift(-21)/s - 1)
p2['max_dd63'] = (p2['close_adjusted'] / g['close_adjusted'].transform(lambda s: s.rolling(63).max()) - 1).rolling(1).max()
p2['max_dd63'] = g['close_adjusted'].transform(lambda s: (s / s.rolling(63).max() - 1))

def xz(df, col):
    m = df.groupby('date')[col].transform('mean')
    sd = df.groupby('date')[col].transform('std')
    return (df[col] - m) / sd.replace(0, np.nan)

cands = {}
cands['ret21'] = xz(p2, 'ret21')
cands['ret63'] = xz(p2, 'ret63')
cands['dist_hi252'] = xz(p2.assign(v=p2['close_adjusted']/p2['hi252']-1), 'v')
cands['dist_lo252'] = xz(p2.assign(v=p2['close_adjusted']/p2['lo252']-1), 'v')
cands['pos_hl63'] = xz(p2.assign(v=(p2['close_adjusted']-p2['lo63'])/(p2['hi63']-p2['lo63']).replace(0,np.nan)), 'v')
cands['vol63'] = xz(p2, 'vol63')
cands['avg252_dist'] = xz(p2.assign(v=p2['close_adjusted']/p2['avg252']-1), 'v')
cands['ret5'] = xz(p2, 'ret5')
cands['max_dd63'] = xz(p2, 'max_dd63')

# --- frozen-grid remaining axes computable from THIS data (no volume/sector/open columns exist -> those announced axes are not computable here, recorded as such in the spec) ---
p2['dow'] = p2['date'].dt.dayofweek
p2['moy'] = p2['date'].dt.month
p2['dom'] = p2['date'].dt.day
p2['days_to_hi252'] = g['close_adjusted'].transform(lambda s: np.arange(len(s)) - s.rolling(252).apply(lambda w: np.argmax(w) if len(w) else 0, raw=True))

cands['days_to_hi252'] = xz(p2, 'days_to_hi252')

# earnings proximity from the earnings file
e = pd.read_csv('research/pead/cache/earnings_latest.csv', usecols=['symbol','date'])
e['date'] = pd.to_datetime(e['date'])
e['next_earn'] = e.groupby('symbol')['date'].shift(-1)
p2 = p2.merge(e, on=['symbol','date'], how='left')
p2['days_to_earn'] = (p2['next_earn'] - p2['date']).dt.days
cands['days_to_earn'] = xz(p2, 'days_to_earn')
cands['earn_win7'] = xz(p2.assign(v=((p2['days_to_earn'] > 0) & (p2['days_to_earn'] <= 7)).astype(int)), 'v')

out = pd.DataFrame({'symbol': p2.symbol.values, 'date': p2.date.values, 'fwd21': p2.fwd21.values})
for k in cands:
    out[k] = cands[k].values

def spearman(x, y):
    rx = pd.Series(x).rank().values; ry = pd.Series(y).rank().values
    return np.corrcoef(rx, ry)[0,1]

n = len(cands)
t_crit = 3.29
dates = sorted(p.date.unique()); cut = dates[int(len(dates)*0.6)]
print(f'candidates: {n}; Bonferroni |t|>={t_crit:.2f}; cut {pd.Timestamp(cut).date()}')
print('method: daily cross-sectional rank IC -> t-test on daily IC series (n_days, NOT n_rows)')

out['date'] = pd.to_datetime(out.date)
for name in cands:
    sub = out.dropna(subset=[name,'fwd21'])
    ic = sub.groupby('date').apply(lambda x: spearman(x[name], x.fwd21), include_groups=False)
    ic = ic.dropna()
    is_ic = ic[ic.index < cut]; oos_ic = ic[ic.index >= cut]
    ti_is = is_ic.mean() / is_ic.std(ddof=1) * np.sqrt(len(is_ic)) if len(is_ic) > 2 else np.nan
    ti_oos = oos_ic.mean() / oos_ic.std(ddof=1) * np.sqrt(len(oos_ic)) if len(oos_ic) > 2 else np.nan
    flag = 'SURVIVOR' if (np.sign(ti_is)==np.sign(ti_oos) and abs(ti_is)>=t_crit and abs(ti_oos)>=t_crit) else ''
    print(f'{name:12s} tIS={ti_is:+6.2f} tOOS={ti_oos:+6.2f} ICIS={is_ic.mean():+.4f} ICOOS={oos_ic.mean():+.4f} (nIS={len(is_ic)},nOOS={len(oos_ic)})  {flag}')

# --- calendar family: time-series market test (calendar dummies are constant cross-sectionally -> rank IC impossible) ---
# market = equal-weight daily return of all stocks; test mean return on treatment day vs other days, Welch t-test, Bonferroni across 3
mw = out.copy()
mw['ret1'] = p2['close_adjusted'].groupby(p2['symbol'], sort=False).pct_change().values
mr = mw.replace([np.inf, -np.inf], np.nan).groupby('date').agg(mkt=('ret1','mean'), n=('ret1','size')).dropna()
mr['fri'] = (mr.index.dayofweek == 4).astype(int)
mr['mon'] = (mr.index.dayofweek == 0).astype(int)
mr['eom'] = ((mr.index.day >= 27) | (mr.index.day <= 2)).astype(int)

def welch(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2: return np.nan
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(va/na + vb/nb)
    if se == 0: return np.nan
    return (a.mean() - b.mean()) / se

for cal in ['fri','mon','eom']:
    is_mr = mr[mr.index < cut]; oos_mr = mr[mr.index >= cut]
    t_is = welch(is_mr.loc[is_mr[cal]==1,'mkt'], is_mr.loc[is_mr[cal]==0,'mkt'])
    t_oos = welch(oos_mr.loc[oos_mr[cal]==1,'mkt'], oos_mr.loc[oos_mr[cal]==0,'mkt'])
    bps_is = (is_mr.loc[is_mr[cal]==1,'mkt'].mean() - is_mr.loc[is_mr[cal]==0,'mkt'].mean()) * 1e4
    bps_oos = (oos_mr.loc[oos_mr[cal]==1,'mkt'].mean() - oos_mr.loc[oos_mr[cal]==0,'mkt'].mean()) * 1e4
    flag = 'SURVIVOR' if (np.sign(t_is)==np.sign(t_oos) and abs(t_is)>=t_crit and abs(t_oos)>=t_crit) else ''
    print(f'{cal+"_eff":12s} tIS={t_is:+6.2f} tOOS={t_oos:+6.2f} bpsIS={bps_is:+7.2f} bpsOOS={bps_oos:+7.2f}  {flag}')
