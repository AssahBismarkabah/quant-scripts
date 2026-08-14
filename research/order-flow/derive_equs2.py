import pandas as pd, numpy as np

t = pd.read_parquet('research/order-flow/cache/EQ_trades_2026q2.parquet',
                    columns=['ts_event','side','size','price','symbol'])
b = pd.read_parquet('research/order-flow/cache/EQ_bbo-1s_2026q2.parquet',
                    columns=['ts_event','symbol','bid_px_00','ask_px_00','bid_sz_00','ask_sz_00'])

et = t.ts_event.dt.tz_convert('America/New_York')
t = t[(et.dt.time >= pd.Timestamp('09:30').time()) & (et.dt.time < pd.Timestamp('16:00').time())].copy()
etb = b.ts_event.dt.tz_convert('America/New_York')
b = b[(etb.dt.time >= pd.Timestamp('09:30').time()) & (etb.dt.time < pd.Timestamp('16:00').time())].copy()
t['bin'] = t.ts_event.dt.floor('5min')
b['bin'] = b.ts_event.dt.floor('5min')
t['date'] = t.ts_event.dt.date
b['date'] = b.ts_event.dt.date

rows = []
for sym, g in t.groupby('symbol'):
    bg = g[g.side=='B'].groupby('bin')['size'].sum()
    sg = g[g.side=='S'].groupby('bin')['size'].sum()
    vw = g.groupby('bin').price.mean()
    d = pd.DataFrame({'delta_vol': (bg.reindex(vw.index).fillna(0) - sg.reindex(vw.index).fillna(0)), 'vwap': vw})
    d['ret_next'] = d.vwap.pct_change().shift(-1)
    last = b[b.symbol==sym].sort_values('ts_event').groupby('bin')[['bid_sz_00','ask_sz_00','bid_px_00','ask_px_00']].last()
    imb = pd.DataFrame({'imb': (last.bid_sz_00-last.ask_sz_00)/(last.bid_sz_00+last.ask_sz_00),
                        'mid': (last.bid_px_00+last.ask_px_00)/2})
    imb['ret_next'] = imb.mid.pct_change().shift(-1)
    m = d.join(imb[['imb','ret_next']], how='inner', lsuffix='_t', rsuffix='_b').dropna()
    if len(m) < 100: continue
    for feat, retcol in [('delta_vol','ret_next_t'), ('imb','ret_next_b')]:
        q = pd.qcut(m[feat].rank(method='first'), 5, labels=False)
        gq = m.assign(q=q)
        # consistency: % of names with monotone increasing buckets
        means = gq.groupby('q')[retcol].mean()
        mono = all(means.iloc[i] < means.iloc[i+1] for i in range(4))
        s = (means.iloc[4]-means.iloc[0])*1e4
        # IS/OOS: first 60% vs last 40% of dates
        dates = sorted(g.date.unique())
        cut = dates[int(len(dates)*0.6)]
        m2 = m.join(g[['bin','date']].drop_duplicates('bin').set_index('bin'), on='bin') if False else m
        mm = m.reset_index().merge(g[['bin','date']].drop_duplicates('bin'), on='bin')
        is_ = mm[mm.date < cut]; oos = mm[mm.date >= cut]
        def spread(df):
            if len(df) < 100: return np.nan
            qq = pd.qcut(df[feat].rank(method='first'), 5, labels=False)
            return (df.assign(q=qq).groupby('q')[retcol].mean().iloc[[0,4]].diff().iloc[1])*1e4
        rows.append((sym, feat, s, mono, spread(is_), spread(oos)))

res = pd.DataFrame(rows, columns=['symbol','feat','spread_bps','monotone','is_bps','oos_bps']).dropna()
print('=== 5-min single-stock order flow: IS/OOS + monotonicity ===')
for feat in ['delta_vol','imb']:
    r = res[res.feat==feat]
    print(f'--- {feat} ---')
    print(f'  names: {len(r)} | mean spread: {r.spread_bps.mean():+.2f} bps | monotone: {r.monotone.mean()*100:.0f}%')
    print(f'  IS mean: {r.is_bps.mean():+.2f} | OOS mean: {r.oos_bps.mean():+.2f}')
    print(f'  names with OOS spread > 3bps: {(r.oos_bps.abs()>3).sum()}/{len(r)}')
