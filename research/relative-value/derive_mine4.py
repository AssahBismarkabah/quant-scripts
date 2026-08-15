"""Dataset D: unsupervised joint-state scan (spec §6). Frozen grid, 6 tests.

NQ primary (2013-2023), ES as OOS asset check (2020-2026).
Unit: one day. Features known at 10:30 (first hour + prior days).
"""

import pandas as pd, numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans

NQ = 'research/ivamr/cache/NQ_n_0_1m.parquet'
ES = 'research/relative-value/cache/ES_n_0_1m.parquet'
T_CUT = 3.29

FEATURES = ['h1_ret','h1_vol','h1_range','h1_logvol','vol_ratio','gap','cc_prev','skew']

def load(path):
    df = pd.read_parquet(path)
    df['ts'] = pd.to_datetime(df['ts'])
    df['date'] = pd.to_datetime(df['date'])
    df['time'] = df['ts'].dt.strftime('%H:%M')
    return df.sort_values('ts').reset_index(drop=True)

def day_frame(df):
    days = []
    prev_close = np.nan
    for dt, x in df.groupby('date'):
        t = dict(zip(x['time'], x['close']))
        def r(a, b):
            return t[b]/t[a] - 1 if (a in t and b in t and t[a] > 0) else np.nan
        h1 = x[(x['time']>='09:30') & (x['time']<='10:30')]
        rets = h1['close'].pct_change()
        h1_vol = rets.std() if len(rets) > 5 else np.nan
        d = {
            'date': dt,
            'h1_ret': r('09:30','10:30'),
            'h1_vol': h1_vol,
            'h1_range': (h1['high'].max() - h1['low'].min())/h1['open'].iloc[0] if len(h1) > 5 else np.nan,
            'h1_logvol': np.log(h1['volume'].sum() + 1) if len(h1) > 5 else np.nan,
            'gap': x['open'].iloc[0]/prev_close - 1 if prev_close > 0 else np.nan,
            'skew': (np.abs(rets).max()/h1_vol) if (len(rets) > 5 and h1_vol and h1_vol > 0) else np.nan,
            'oc': r('09:30','16:00'),
            'rest': r('10:30','16:00'),
        }
        days.append(d)
        prev_close = x['close'].iloc[-1]
    res = pd.DataFrame(days).set_index('date')
    res['cc_prev'] = (1 + res['gap']) * (1 + res['oc']) - 1
    res['cc_prev'] = res['cc_prev'].shift(1)
    res['vol_ratio'] = res['h1_vol'] / res['h1_vol'].rolling(20).mean().shift(1)
    res['nxt_oc'] = res['oc'].shift(-1)
    return res

def zscore(s):
    return (s - s.mean()) / s.std(ddof=1)

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = a[~np.isnan(a)]; b = b[~np.isnan(b)]
    if len(a) < 10 or len(b) < 10: return np.nan, 0, 0
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(va/len(a) + vb/len(b))
    if not se or np.isnan(se): return np.nan, 0, 0
    return (a.mean() - b.mean())/se, len(a), len(b)

def pearson_t(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    if m.sum() < 10: return np.nan, 0
    x, y = x[m], y[m]
    r = np.corrcoef(x, y)[0,1]
    t = r*np.sqrt(len(x)-2)/np.sqrt(max(1-r**2,1e-9))
    return t, len(x)

def run(name, path):
    df = load(path)
    res = day_frame(df)
    res = res.dropna(subset=FEATURES)
    for f in FEATURES:
        res[f] = zscore(res[f])
    dates = sorted(res.index); cut = dates[int(len(dates)*0.6)]
    is_idx = res.index < cut; oos_idx = res.index >= cut
    X = res[FEATURES].values
    iso = IsolationForest(n_estimators=200, contamination=0.10, random_state=42)
    iso.fit(X[is_idx])
    score = -iso.score_samples(X)  # higher = more anomalous
    res['anom'] = score
    res['anom_z'] = zscore(pd.Series(score, index=res.index))
    km = KMeans(n_clusters=3, n_init=10, random_state=42)
    labs = km.fit_predict(X[is_idx])
    # cluster centers from IS; assign OOS by nearest center
    centers = km.cluster_centers_
    def assign(xrow):
        return int(np.argmin(((centers - xrow)**2).sum(axis=1)))
    res['k'] = [assign(row) for row in X]
    # cluster with highest mean rest-return in IS = the "regime" state under test
    is_labels = labs
    is_rest = res.loc[is_idx, 'rest'].values
    cl_mean = {c: np.nanmean(is_rest[is_labels==c]) for c in range(3)}
    hot = max(cl_mean, key=cl_mean.get)
    res['hot'] = (res['k'] == hot).astype(int)

    print(f'=== {name} {len(res)} days, cut {pd.Timestamp(cut).date()} ===')
    tests = [
        ('T1 anom-cor -> rest', 'anom_z', 'rest', 'pearson'),
        ('T2 anom-cor -> nxt OC', 'anom_z', 'nxt_oc', 'pearson'),
        ('T3 anom-topdecile -> rest', None, 'rest', 'tdec'),
        ('T4 anom-topdecile -> nxt OC', None, 'nxt_oc', 'tdec'),
        ('T5 kmeans hot -> rest', 'hot', 'rest', 'welch'),
        ('T6 kmeans hot -> nxt OC', 'hot', 'nxt_oc', 'welch'),
    ]
    for label, c1, c2, kind in tests:
        if kind == 'pearson':
            t_is, n_is = pearson_t(res.loc[is_idx, c1], res.loc[is_idx, c2])
            t_oos, n_oos = pearson_t(res.loc[oos_idx, c1], res.loc[oos_idx, c2])
            e_is = e_oos = ''
        elif kind == 'tdec':
            th = res['anom'].quantile(0.90)
            hi = res['anom'] >= th
            t_is, n_is, _ = welch(res.loc[hi & is_idx, c2], res.loc[~hi & is_idx, c2])
            t_oos, n_oos, _ = welch(res.loc[hi & oos_idx, c2], res.loc[~hi & oos_idx, c2])
            e_is = f"top={res.loc[hi&is_idx,c2].mean()*1e4:+.0f}bps rest={res.loc[~hi&is_idx,c2].mean()*1e4:+.0f}"
            e_oos = f"top={res.loc[hi&oos_idx,c2].mean()*1e4:+.0f}bps rest={res.loc[~hi&oos_idx,c2].mean()*1e4:+.0f}"
        else:
            t_is, n_is, _ = welch(res.loc[res['hot']==1 & is_idx, c2], res.loc[res['hot']==0 & is_idx, c2])
            t_oos, n_oos, _ = welch(res.loc[res['hot']==1 & oos_idx, c2], res.loc[res['hot']==0 & oos_idx, c2])
            e_is = e_oos = ''
        flag = 'SURVIVOR' if (np.sign(t_is)==np.sign(t_oos) and abs(t_is)>=T_CUT and abs(t_oos)>=T_CUT) else ''
        print(f'{label:26s} tIS={t_is:+6.2f} tOOS={t_oos:+6.2f} {e_is} | {e_oos} (n={n_is}/{n_oos}) {flag}')

run('NQ', NQ)
run('ES', ES)
