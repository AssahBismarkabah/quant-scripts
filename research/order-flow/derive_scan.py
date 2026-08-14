import pandas as pd, numpy as np

t = pd.read_parquet('research/order-flow/cache/NQ_trades_2026q2.parquet',
                    columns=['ts_event','side','size','price'])
b = pd.read_parquet('research/order-flow/cache/NQ_bbo-1s_2026q2.parquet',
                    columns=['ts_event','bid_sz_00','ask_sz_00','bid_px_00','ask_px_00'])

et = t.ts_event.dt.tz_convert('America/New_York')
t = t[(et.dt.time >= pd.Timestamp('09:30').time()) & (et.dt.time < pd.Timestamp('16:00').time())].copy()
etb = b.ts_event.dt.tz_convert('America/New_York')
b = b[(etb.dt.time >= pd.Timestamp('09:30').time()) & (etb.dt.time < pd.Timestamp('16:00').time())].copy()
t['min'] = t.ts_event.dt.floor('min')
b['min'] = b.ts_event.dt.floor('min')

# Observation 1: aggression delta (vectorized)
buy = t[t.side=='B'].groupby('min').agg(bv=('size','sum'), bc=('size','count'))
sell = t[t.side=='S'].groupby('min').agg(sv=('size','sum'), sc=('size','count'))
tv = t.groupby('min').agg(vwap=('price','mean'), vol=('size','sum'))
ta = buy.join(sell, how='outer').join(tv).fillna(0)
ta['delta_vol'] = ta.bv - ta.sv
ta['delta_cnt'] = ta.bc - ta.sc
ta['ret_next'] = ta.vwap.pct_change().shift(-1)
ta['ret_fwd5'] = ta.vwap.pct_change(5).shift(-5)

# Observation 2: quote imbalance (vectorized)
last = b.sort_values('ts_event').groupby('min')[['bid_sz_00','ask_sz_00','bid_px_00','ask_px_00']].last()
bb = pd.DataFrame({'imb': (last.bid_sz_00-last.ask_sz_00)/(last.bid_sz_00+last.ask_sz_00),
                   'mid': (last.bid_px_00+last.ask_px_00)/2})
bb['ret_next'] = bb.mid.pct_change().shift(-1)

m = ta.join(bb[['imb','ret_next']], how='inner', lsuffix='_t', rsuffix='_b').dropna()
print('RTH minute obs:', len(m))

for name, x, y in [('aggr_delta_vol->next', m.delta_vol, m.ret_next_t),
                   ('aggr_delta_cnt->next', m.delta_cnt, m.ret_next_t),
                   ('quote_imb->next', m.imb, m.ret_next_t)]:
    r = np.corrcoef(x, y)[0,1]
    q = pd.qcut(x.rank(method='first'), 5, labels=False)
    means = pd.DataFrame({'x':x,'y':y,'q':q}).groupby('q').y.mean()
    spread = (means[4]-means[0])*1e4
    print(f'{name}: corr={r:.4f} | buckets(bps): ' +
          ' '.join(f'{v*1e4:+.1f}' for v in means.values) + f' | spread={spread:+.1f}')
