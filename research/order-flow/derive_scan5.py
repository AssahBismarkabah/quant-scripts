import pandas as pd, numpy as np

t = pd.read_parquet('research/order-flow/cache/NQ_trades_2026q2.parquet',
                    columns=['ts_event','side','size','price'])
b = pd.read_parquet('research/order-flow/cache/NQ_bbo-1s_2026q2.parquet',
                    columns=['ts_event','bid_sz_00','ask_sz_00','bid_px_00','ask_px_00'])

et = t.ts_event.dt.tz_convert('America/New_York')
t = t[(et.dt.time >= pd.Timestamp('09:30').time()) & (et.dt.time < pd.Timestamp('16:00').time())].copy()
etb = b.ts_event.dt.tz_convert('America/New_York')
b = b[(etb.dt.time >= pd.Timestamp('09:30').time()) & (etb.dt.time < pd.Timestamp('16:00').time())].copy()

for bar in [5, 15, 60]:
    t['bin'] = t.ts_event.dt.floor(f'{bar}min')
    b['bin'] = b.ts_event.dt.floor(f'{bar}min')
    buy = t[t.side=='B'].groupby('bin').agg(bv=('size','sum'))
    sell = t[t.side=='S'].groupby('bin').agg(sv=('size','sum'))
    tv = t.groupby('bin').agg(vwap=('price','mean'))
    ta = buy.join(sell).join(tv).fillna(0)
    ta['delta_vol'] = ta.bv - ta.sv
    ta['ret_next'] = ta.vwap.pct_change().shift(-1)
    last = b.sort_values('ts_event').groupby('bin')[['bid_sz_00','ask_sz_00','bid_px_00','ask_px_00']].last()
    bb = pd.DataFrame({'imb': (last.bid_sz_00-last.ask_sz_00)/(last.bid_sz_00+last.ask_sz_00),
                       'mid': (last.bid_px_00+last.ask_px_00)/2})
    bb['ret_next'] = bb.mid.pct_change().shift(-1)
    m = ta.join(bb[['imb','ret_next']], how='inner', lsuffix='_t', rsuffix='_b').dropna()
    print(f'--- {bar}min bars ({len(m)} obs) ---')
    for name, x, y in [('delta_vol', m.delta_vol, m.ret_next_t),
                       ('imb', m.imb, m.ret_next_b)]:
        r = np.corrcoef(x, y)[0,1]
        q = pd.qcut(x.rank(method='first'), 5, labels=False)
        means = pd.DataFrame({'x':x,'y':y,'q':q}).groupby('q').y.mean()
        spread = (means[4]-means[0])*1e4
        print(f'  {name}: corr={r:.4f} | spread={spread:+.1f} bps')
