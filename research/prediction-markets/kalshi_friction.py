import gzip
from pathlib import Path

import numpy as np
import pandas as pd

SPEC = Path(__file__).parents[1] / 'research-specs/prediction-markets-probe22-spec.md'
OUT = Path(__file__).parent / 'outputs'
TRADES = OUT / 'trades'
FOCUS_SERIES = [
    'KXBTC15M', 'KXBTCD', 'KXETH15M', 'KXGOLD15M', 'KXXRP15M', 'KXSOL15M',
    'KXDOGE15M', 'KXMLBGAME',
]
HORIZONS_MIN = [5, 30, 60]
CHUNK = 2_000_000
MAX_FILLS_PER_MARKET = 20_000
CAP_PER_SERIES_H = 400_000
RNG = np.random.default_rng(7)
SPAN_SANITY_MIN = 0.05


def iter_chunks(path):
    return pd.read_csv(
        gzip.open(path), usecols=[
            'DT', 'SERIES_TICKER', 'MARKET_TICKER', 'SIDE', 'SIZE', 'PRICE',
        ], chunksize=CHUNK,
    )


def forward_drift(t, px, side, h):
    n = len(t)
    out = np.empty(n)
    out[:] = np.nan
    j = 0
    for i in range(n):
        lim = t[i] + h
        while j < n and t[j] <= lim:
            j += 1
        if j <= i + 1:
            continue
        vwap = np.average(px[i + 1:j])
        out[i] = np.where(side[i] == 'BUY', vwap - px[i], px[i] - vwap)
    return out


def main():
    files = sorted(TRADES.glob('*.csv.gz'))
    if not files:
        raise SystemExit('no trade files found')
    print(f'{len(files)} trade days', flush=True)

    drift = {(s, h): [] for s in FOCUS_SERIES for h in HORIZONS_MIN}
    vol_rows = []
    n_fills_by_sh = {(s, h): 0 for s in FOCUS_SERIES for h in HORIZONS_MIN}
    for f in files:
        parts = []
        for chunk in iter_chunks(f):
            chunk = chunk[chunk['SERIES_TICKER'].isin(FOCUS_SERIES)]
            if not chunk.empty:
                parts.append(chunk)
        if not parts:
            continue
        df = pd.concat(parts, ignore_index=True)
        dt = pd.to_datetime(df['DT'], utc=True).dt.tz_localize(None)
        df['ts'] = dt.astype('datetime64[ns]').astype('int64') // 10 ** 9
        df = df.rename(columns={'SIDE': 'side_taker'})
        df['price'] = pd.to_numeric(df['PRICE'], errors='coerce')

        for series, g in df.groupby('SERIES_TICKER', sort=False):
            vol_rows.append({
                'series': series,
                'day': f.name,
                'n_trades': int(len(g)),
                'n_markets': int(g['MARKET_TICKER'].nunique()),
                'median_size': float(g['SIZE'].median()),
                'median_price': float(g['price'].median()),
                'p01_price': float(g['price'].quantile(0.01)),
                'p99_price': float(g['price'].quantile(0.99)),
            })

        for market, g in df.groupby('MARKET_TICKER', sort=False):
            if g['ts'].nunique() < 20:
                continue
            span_min = (g['ts'].max() - g['ts'].min()) / 60
            if span_min < SPAN_SANITY_MIN:
                raise RuntimeError(
                    f'span sanity failed for {market}: {span_min:.3f} min')
            if len(g) > MAX_FILLS_PER_MARKET:
                g = g.sample(MAX_FILLS_PER_MARKET, random_state=RNG)
            g = g.sort_values('ts')
            series = g['SERIES_TICKER'].iloc[0]
            for h in HORIZONS_MIN:
                d = forward_drift(g['ts'].to_numpy(),
                                  g['price'].to_numpy(),
                                  g['side_taker'].to_numpy(), h * 60)
                d = d[~np.isnan(d)]
                key = (series, h)
                if len(d) == 0:
                    continue
                drift[key].append(d)
                n_fills_by_sh[key] += len(d)
                total = sum(len(x) for x in drift[key])
                if total > CAP_PER_SERIES_H:
                    merged = np.concatenate(drift[key])
                    idx = RNG.choice(len(merged), CAP_PER_SERIES_H, replace=False)
                    drift[key] = [merged[idx]]
        print(f'processed {f.name}', flush=True)

    rows = []
    for (series, h), arrays in drift.items():
        if not arrays:
            continue
        d = np.concatenate(arrays)
        rows.append({
            'series': series, 'h_min': h,
            'n_fills': n_fills_by_sh[(series, h)],
            'mean_drift_cents': round(float(d.mean() * 100), 4),
            'median_drift_cents': round(float(np.median(d) * 100), 4),
            'p95_drift_cents': round(float(np.quantile(d, 0.95) * 100), 4),
            'adverse_share': round(float((d > 0).mean()), 4),
            'sample_cap_reached': len(d) >= CAP_PER_SERIES_H,
        })
    table = pd.DataFrame(rows).sort_values(['series', 'h_min'])
    table.to_csv(OUT / 'kalshi_friction_summary.csv', index=False)
    print('--- friction/adverse-selection summary (cents) ---')
    print(table.to_string(index=False))

    fam = pd.DataFrame(vol_rows)
    fam_sum = fam.groupby('series').agg(
        days=('day', 'nunique'),
        total_trades=('n_trades', 'sum'),
        markets_per_day_mean=('n_markets', 'mean'),
    ).round(1)
    fam_sum.to_csv(OUT / 'kalshi_series_volume_summary.csv')
    print('--- series volume ---')
    print(fam_sum.to_string())


if __name__ == '__main__':
    main()
