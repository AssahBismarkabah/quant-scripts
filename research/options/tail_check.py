import pandas as pd, numpy as np

frames = []
for y in range(2010, 2024):
    frames.append(pd.read_parquet(f'research/options/cache/spy_eod_{y}.parquet'))
d = pd.concat(frames, ignore_index=True)
u = d[['[QUOTE_DATE]','[UNDERLYING_LAST]']].drop_duplicates().sort_values('[QUOTE_DATE]').reset_index(drop=True)
u.columns = ['date','px']
u['date'] = pd.to_datetime(u.date)
u['ret'] = u.px.pct_change()

atm = d[(d['[DTE]']>=30) & (d['[DTE]']<=60)].copy()
atm['absdist'] = atm['[STRIKE_DISTANCE_PCT]'].abs()
atm_iv = atm.sort_values('absdist').groupby('[QUOTE_DATE]').first()[['[C_IV]','[P_IV]']]
atm_iv['iv'] = (atm_iv['[C_IV]']+atm_iv['[P_IV]'])/2
m = atm_iv.reset_index().rename(columns={'[QUOTE_DATE]':'date'})
m['date'] = pd.to_datetime(m.date)
m = m.merge(u[['date','ret']], on='date')

# pre-registered V3-style rule: long SPY when ATM IV in top quintile (rolling, point-in-time)
m = m.sort_values('date')
m['iv_thr'] = m.iv.rolling(250, min_periods=100).quantile(0.8)
m['sig'] = (m.iv > m.iv_thr).astype(int)
m['pnl'] = m.sig * m.ret
book = m.dropna(subset=['iv_thr'])

# tail stats on the long-book (same gates as VRP V3)
eq = (1+book.pnl.fillna(0)).cumprod()
dd = (eq.cummax()-eq)/eq.cummax()
worst_day = book.pnl.min()
print(f'exposure days: {book.sig.sum()} / {len(book)} ({book.sig.mean()*100:.0f}%)')
print(f'total return: {(book.pnl.sum()*100):+.1f}% | annualized: {((1+book.pnl.sum())**(252/len(book))-1)*100:+.1f}%')
print(f'max drawdown: {dd.max()*100:.1f}%  <- V3 gate: must be < 40%')
print(f'worst single day: {worst_day*100:.1f}%  <- V3 gate: must be > -25%')
print(f'crisis days under signal (worst 10):')
print(book.nsmallest(10, 'pnl')[['date','pnl','iv']].to_string(index=False))
