import pandas as pd, numpy as np
from scipy import stats

T_CUT = 3.29

def load_klines(path):
    df = pd.read_parquet(path)
    df['ts'] = pd.to_datetime(df['open_time'], unit='ms')
    df['date'] = df['ts'].dt.normalize()
    df['min'] = df['ts'].dt.strftime('%H:%M')
    return df.sort_values('ts').reset_index(drop=True)

def load_funding(path):
    df = pd.read_parquet(path)
    df['ts'] = pd.to_datetime(df['funding_time'], unit='ms')
    return df.sort_values('ts').reset_index(drop=True)

def day_frame(kl, funding):
    days = []
    prev_close = np.nan
    for dt, x in kl.groupby('date'):
        t = dict(zip(x['min'], x['close']))
        op = dict(zip(x['min'], x['open']))
        hi = dict(zip(x['min'], x['high']))
        lo = dict(zip(x['min'], x['low']))
        def r(a, b):
            return t[b]/t[a] - 1 if (a in t and b in t and t[a] > 0) else np.nan
        day = {'date': dt, 'cc': prev_close}
        day['h1_ret'] = r('00:00', '01:00')
        day['rest_fwd'] = r('01:00', '23:59')
        h1 = x[(x['min'] >= '00:00') & (x['min'] <= '00:59')]
        day['h1_vol'] = h1['close'].pct_change().std() if len(h1) > 5 else np.nan
        day['last_h'] = r('23:00', '23:59')
        day['morning'] = r('00:00', '12:00')
        day['afternoon'] = r('12:00', '23:59')
        day['sb1'] = r('07:00', '08:00')
        day['sb1_fwd'] = r('08:00', '16:00')
        day['day_ret'] = prev_close and (x['close'].iloc[-1]/prev_close - 1) if prev_close > 0 else np.nan
        prev_close = x['close'].iloc[-1]
        days.append(day)
    res = pd.DataFrame(days).set_index('date')
    res['tds3_fwd'] = res['h1_ret'].shift(-1)
    res['next_day'] = res['day_ret'].shift(-1)
    vol7 = res['day_ret'].rolling(7).std()
    res['vol7_pct'] = vol7.rolling(252, min_periods=60).apply(lambda s: s.rank(pct=True).iloc[-1]).shift(1)
    res['vol_up'] = ((vol7 >= 1.5 * vol7.shift(7)) & vol7.notna() & vol7.shift(7).notna()).astype(float).shift(1)
    res['ret7'] = (res['day_ret'] + 1).rolling(7).apply(np.prod, raw=True).shift(1) - 1
    if funding is not None:
        f = funding.set_index('ts')['funding_rate']
        f7 = f.resample('D').last().rolling(7, min_periods=5).mean().shift(1)
        res['fund7'] = f7.reindex(res.index)
    else:
        res['fund7'] = np.nan
    return res

def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    if m.sum() < 10: return np.nan, np.nan, 0
    x, y = x[m], y[m]
    r = np.corrcoef(x, y)[0, 1]
    t = r*np.sqrt(len(x)-2)/np.sqrt(max(1-r**2, 1e-9))
    return r, t, len(x)

def welch(a, b):
    a = np.asarray(a, float)[~np.isnan(np.asarray(a, float))]
    b = np.asarray(b, float)[~np.isnan(np.asarray(b, float))]
    if len(a) < 10 or len(b) < 10: return np.nan, np.nan, len(a), len(b)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return a.mean()-b.mean(), t, len(a), len(b)

def run(name, kpath, fpath):
    kl = load_klines(kpath)
    funding = load_funding(fpath)
    res = day_frame(kl, funding)
    dates = sorted(res.index); cut = dates[int(len(dates)*0.6)]
    res['mon'] = (res.index.dayofweek == 0)
    res['sun'] = (res.index.dayofweek == 6)
    print(f'=== {name} {len(res)} days, cut {pd.Timestamp(cut).date()}, IS/OOS {sum(res.index<cut)}/{sum(res.index>=cut)} ===')
    tests = [
        ('tds1 h1->rest',       'h1_ret',  'rest_fwd',  'pearson'),
        ('tds2 h1vol->rest',    'h1_vol',  'rest_fwd',  'pearson'),
        ('tds3 lastH->nxt h1',  'last_h',  'tds3_fwd',  'pearson'),
        ('tds4 morning->aftn',  'morning', 'afternoon', 'pearson'),
        ('sb1 fundH->nxt8h',    'sb1',     'sb1_fwd',   'pearson'),
        ('sb2 Mon h1->Mon rest','h1_ret',  'rest_fwd',  'pearson', 'mon'),
        ('sb3 Sun vs wkday',    'day_ret', 'day_ret',   'welch',   'sun'),
        ('sb4 Mon vs rest',     'day_ret', 'day_ret',   'welch',   'mon'),
        ('vs1 vol7pct->nxt',    'vol7_pct','next_day',  'pearson'),
        ('vs2 volUp->nxt',      'vol_up',  'next_day',  'pearson'),
        ('vs3 ret7->nxt',       'ret7',    'next_day',  'pearson'),
        ('vs4 fund7->nxt',      'fund7',   'next_day',  'pearson'),
    ]
    rows = []
    for t in tests:
        label, c1, c2, kind, *mask = t
        is_mask = res.index < cut
        oos_mask = res.index >= cut
        if kind == 'welch':
            grp = mask[0]
            a_is = res.loc[is_mask & res[grp], c1]; b_is = res.loc[is_mask & ~res[grp], c1]
            a_oos = res.loc[oos_mask & res[grp], c1]; b_oos = res.loc[oos_mask & ~res[grp], c1]
            r_is, t_is, n_is, _ = welch(a_is, b_is); r_oos, t_oos, n_oos, _ = welch(a_oos, b_oos)
        elif mask and mask[0] == 'mon':
            a_is = res.loc[is_mask & res['mon'], c1]; b_is = res.loc[is_mask & res['mon'], c2]
            a_oos = res.loc[oos_mask & res['mon'], c1]; b_oos = res.loc[oos_mask & res['mon'], c2]
            r_is, t_is, n_is = pearson(a_is, b_is); r_oos, t_oos, n_oos = pearson(a_oos, b_oos)
        else:
            r_is, t_is, n_is = pearson(res.loc[is_mask, c1], res.loc[is_mask, c2])
            r_oos, t_oos, n_oos = pearson(res.loc[oos_mask, c1], res.loc[oos_mask, c2])
        flag = 'SURVIVOR' if (np.sign(t_is) == np.sign(t_oos) and abs(t_is) >= T_CUT and abs(t_oos) >= T_CUT) else ''
        print(f'{label:24s} tIS={t_is:+6.2f} tOOS={t_oos:+6.2f} rIS={r_is:+.4f} rOOS={r_oos:+.4f} (n={n_is}/{n_oos}) {flag}')
        rows.append({'test': label, 'tIS': t_is, 'tOOS': t_oos, 'rIS': r_is, 'rOOS': r_oos, 'nIS': n_is, 'nOOS': n_oos, 'flag': flag})
    return res, rows, cut

if __name__ == '__main__':
    base = 'research/crypto-perps/cache'
    for name, sym in [('BTC', 'BTCUSDT'), ('ETH', 'ETHUSDT')]:
        run(name, f'{base}/{sym}_1m.parquet', f'{base}/{sym}_funding.parquet')
