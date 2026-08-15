import pandas as pd, numpy as np

NQ = 'research/ivamr/cache/NQ_n_0_1m.parquet'
ES = 'research/relative-value/cache/ES_n_0_1m.parquet'
T_CUT = 3.29

def load(path):
    df = pd.read_parquet(path)
    df['ts'] = pd.to_datetime(df['ts'])
    df['date'] = pd.to_datetime(df['date'])
    df['time'] = df['ts'].dt.strftime('%H:%M')
    return df.sort_values('ts').reset_index(drop=True)

def day_frame(df):
    days = []
    prev_day_last_close = np.nan
    for dt, x in df.groupby('date'):
        t = dict(zip(x['time'], x['close']))
        def r(a, b):
            return t[b]/t[a] - 1 if (a in t and b in t and t[a] > 0) else np.nan
        day = {'date': dt, 'prev_close': prev_day_last_close}
        day['gap'] = x['open'].iloc[0]/prev_day_last_close - 1 if prev_day_last_close > 0 else np.nan
        day['tds1'] = r('10:30','11:30'); day['tds1_fwd'] = r('11:30','16:00')
        day['tds2'] = r('09:30','10:30'); day['tds2_fwd'] = r('10:30','11:30')
        day['tds3'] = r('15:00','16:00')
        day['tds4'] = r('09:30','12:00'); day['tds4_fwd'] = r('12:00','16:00')
        day['oc'] = r('09:30','16:00')
        h1 = x[(x['time']>='09:30') & (x['time']<='10:30')]
        day['h1_ret'] = r('09:30','10:30')
        day['h1_vol'] = h1['close'].pct_change().std() if len(h1) > 5 else np.nan
        r30 = x[(x['time']>='09:30') & (x['time']<='10:00')]
        day['r30_vol'] = r30['close'].pct_change().std() if len(r30) > 5 else np.nan
        day['rest_vol_fwd'] = np.nan  # vs4 uses prev-20d avg r30 vol vs today r30 vol -> fwd rest-of-day
        days.append(day)
        prev_day_last_close = x['close'].iloc[-1]
    res = pd.DataFrame(days).set_index('date')
    res['cc_ret'] = (1 + res['gap']) * (1 + res['oc']) - 1
    return res

def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    if m.sum() < 10: return np.nan, np.nan, 0
    x, y = x[m], y[m]
    r = np.corrcoef(x, y)[0,1]
    t = r*np.sqrt(len(x)-2)/np.sqrt(max(1-r**2,1e-9))
    return r, t, len(x)

def run(name, path):
    df = load(path)
    res = day_frame(df)
    # wire forward references between days
    res['tds3_fwd'] = res['oc'].shift(-1)                    # next-day open-to-close
    res['sb3_fwd'] = res['gap'].shift(-1)                    # next-day gap
    res['sb2_mask'] = (res.index.dayofweek == 0)             # Monday rows
    res['cc_prev'] = res['cc_ret'].shift(1)                  # PREV-day close-to-close
    res['f_vol_pct'] = res['h1_vol'].rolling(60, min_periods=20).apply(lambda s: s.rank(pct=True).iloc[-1]).shift(1)  # PREV-day vol percentile
    res['vs1_fwd'] = res['h1_ret']                           # today first-hour return
    res['vs2_fwd'] = res['tds1_fwd']                         # today rest-of-day (11:30->16:00)
    res['vs3_up'] = (res['f_vol_pct'] >= 0.80).astype(float)  # vol regime up-switch state (prev-day pct)
    res['vs4_ratio'] = res['r30_vol'] / res['r30_vol'].rolling(20).mean().shift(1)
    res['vs4_fwd'] = res['tds1_fwd']
    dates = sorted(res.index); cut = dates[int(len(dates)*0.6)]
    print(f'=== {name} {len(res)} days, cut {pd.Timestamp(cut).date()} ===')
    tests = [
        ('tds1 h2->rest', 'tds1', 'tds1_fwd'),
        ('tds2 h1->h2', 'tds2', 'tds2_fwd'),
        ('tds3 last-h->nxt OC', 'tds3', 'tds3_fwd'),
        ('tds4 morning->aftn', 'tds4', 'tds4_fwd'),
        ('sb1 gap->same OC', 'gap', 'oc'),
        ('sb2 Mon gap->OC', 'gap', 'oc'),
        ('sb3 cc->next gap', 'cc_prev', 'sb3_fwd'),
        ('sb4 cc->same OC', 'cc_prev', 'oc'),
        ('vs1 volpct->h1', 'f_vol_pct', 'vs1_fwd'),
        ('vs2 volpct->rest', 'f_vol_pct', 'vs2_fwd'),
        ('vs3 upswitch->nxt OC', 'vs3_up', 'tds3_fwd'),
        ('vs4 volratio->rest', 'vs4_ratio', 'vs4_fwd'),
    ]
    for label, c1, c2 in tests:
        m = res.index < cut
        if label == 'sb2 Mon gap->OC':
            m = (res.index.dayofweek == 0)
            mm = m
            r_is, t_is, n_is = pearson(res.loc[mm & (res.index < cut), c1], res.loc[mm & (res.index < cut), c2])
            r_oos, t_oos, n_oos = pearson(res.loc[mm & (res.index >= cut), c1], res.loc[mm & (res.index >= cut), c2])
        else:
            r_is, t_is, n_is = pearson(res.loc[res.index<cut, c1], res.loc[res.index<cut, c2])
            r_oos, t_oos, n_oos = pearson(res.loc[res.index>=cut, c1], res.loc[res.index>=cut, c2])
        flag = 'SURVIVOR' if (np.sign(t_is)==np.sign(t_oos) and abs(t_is)>=T_CUT and abs(t_oos)>=T_CUT) else ''
        print(f'{label:28s} tIS={t_is:+6.2f} tOOS={t_oos:+6.2f} rIS={r_is:+.4f} rOOS={r_oos:+.4f} (n={n_is}/{n_oos}) {flag}')

run('NQ', NQ)
run('ES', ES)
