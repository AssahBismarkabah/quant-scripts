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

print('=== 5-min bins, per-symbol: aggression delta + quote imbalance vs next-bin return ===')
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
    r1 = np.corrcoef(m.delta_vol, m.ret_next_t)[0,1]
    r2 = np.corrcoef(m.imb, m.ret_next_b)[0,1]
    q1 = pd.qcut(m.delta_vol.rank(method='first'), 5, labels=False)
    s1 = (m.assign(q=q1).groupby('q').ret_next_t.mean().iloc[[0,4]].diff().iloc[1])*1e4
    q2 = pd.qcut(m.imb.rank(method='first'), 5, labels=False)
    s2 = (m.assign(q=q2).groupby('q').ret_next_b.mean().iloc[[0,4]].diff().iloc[1])*1e4
    rows.append((sym, len(m), r1, s1, r2, s2))

res = pd.DataFrame(rows, columns=['symbol','n','corr_delta','spread_delta_bps','corr_imb','spread_imb_bps'])
print('mean corr delta: %.4f | mean spread delta: %+.2f bps' % (res.corr_delta.mean(), res.spread_delta_bps.mean()))
print('mean corr imb:   %.4f | mean spread imb:   %+.2f bps' % (res.corr_imb.mean(), res.spread_imb_bps.mean()))
print('n names with |spread_delta|>2bps:', (res.spread_delta_bps.abs()>2).sum(), '/', len(res))
print('n names with |spread_imb|>2bps:', (res.spread_imb_bps.abs()>2).sum(), '/', len(res))
print()
print(res.sort_values('spread_delta_bps', ascending=False).head(8).to_string(index=False))
