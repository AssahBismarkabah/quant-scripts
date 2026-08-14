import pandas as pd, numpy as np
from pathlib import Path

RNG = np.random.default_rng(42)
OUT = Path('research/order-flow/outputs'); OUT.mkdir(exist_ok=True)

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
t['date'] = t.ts_event.dt.normalize()
b['date'] = b.ts_event.dt.normalize()

FEAT = 'delta_vol'   # pre-registered: aggression delta (buy vol - sell vol), 5-min bins
FRICTION_BPS = 3.0   # 1.5 bps per side, round-trip

parts = []
for sym, g in t.groupby('symbol'):
    bg = g[g.side=='B'].groupby('bin')['size'].sum()
    sg = g[g.side=='S'].groupby('bin')['size'].sum()
    vw = g.groupby('bin').price.mean()
    d = pd.DataFrame({'delta_vol': (bg.reindex(vw.index).fillna(0) - sg.reindex(vw.index).fillna(0)), 'vwap': vw})
    d['ret_next'] = d.vwap.pct_change().shift(-1)
    d['date'] = d.index.to_series().dt.normalize().values if False else None
    dd = d.reset_index()
    dd['date'] = dd['bin'].dt.normalize()
    dd['symbol'] = sym
    parts.append(dd)
m = pd.concat(parts).dropna()
print('total obs:', len(m), '| symbols:', m.symbol.nunique())

# pre-registered rule: each 5-min bin, within each symbol, go long when delta_vol in top quintile (per symbol),
# flat otherwise. Position held 1 bin. Net of 3bps round-trip friction.
def run(mdf, seed):
    rng = np.random.default_rng(seed)
    mdf = mdf.copy()
    # per-symbol rolling quintile threshold (point-in-time: prior bins only)
    mdf = mdf.sort_values(['symbol','bin'])
    mdf['thr'] = mdf.groupby('symbol')['delta_vol'].transform(lambda s: s.rolling(200, min_periods=50).quantile(0.8))
    mdf['sig'] = (mdf.delta_vol > mdf.thr).astype(int)
    mdf['pnl'] = mdf.sig * mdf.ret_next - FRICTION_BPS*1e-4*mdf.sig
    # skip bins with no prior data (warmup)
    mdf.loc[mdf.thr.isna(), 'pnl'] = np.nan
    return mdf.dropna(subset=['pnl'])

m = run(m, 1)
dates = sorted(m.date.unique())
cut = dates[int(len(dates)*0.6)]
is_ = m[m.date < cut]; oos = m[m.date >= cut]

def stats(df):
    p = df.pnl
    total = p.sum(); n = len(p)
    mean = p.mean(); std = p.std(ddof=1)
    tstat = mean/(std/np.sqrt(n)) if std>0 else 0
    return total, n, mean, std, tstat

print('=== IS (first 60%% dates) ===')
tot, n, mean, std, ts = stats(is_)
print(f'total={tot*1e4:+.1f} bps over {n} trades | mean={mean*1e4:+.3f} bps/trade | t={ts:.2f}')
print('=== OOS (last 40%% dates) ===')
tot, n, mean, std, ts = stats(oos)
print(f'total={tot*1e4:+.1f} bps over {n} trades | mean={mean*1e4:+.3f} bps/trade | t={ts:.2f}')

# bootstrap p5 on OOS
means = []
p = oos.pnl.values
for _ in range(5000):
    means.append(RNG.choice(p, size=len(p), replace=True).mean())
p5 = np.percentile(means, 5)
print(f'=== bootstrap p5 (OOS, 5000, seed 42) ===')
print(f'p5 of mean = {p5*1e4:+.3f} bps/trade | observed mean = {oos.pnl.mean()*1e4:+.3f} bps/trade | gate: p5 > 0')

# drop-best: drop best single symbol
by_sym = oos.groupby('symbol').pnl.sum()
drop = oos[oos.symbol != by_sym.idxmax()]
tot2, n2, mean2, std2, ts2 = stats(drop)
print(f'=== drop-best-symbol (OOS) ===')
print(f'dropped {by_sym.idxmax()} | mean={mean2*1e4:+.3f} bps/trade | t={ts2:.2f}')
