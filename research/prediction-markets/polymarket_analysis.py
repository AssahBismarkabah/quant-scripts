import sys
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent / 'outputs'


def family_key(row):
    q = str(row.get('question') or '')
    neg = str(row.get('negRisk') or '')
    parts = [p.strip() for p in q.split(':') if p.strip()]
    parts = [p.strip() for p in parts]
    base = parts[0] if parts else q[:40]
    if len(q) > 6 and ' vs ' in q and base == q[:40]:
        return base[:40]
    return base


def main(path):
    df = pd.read_parquet(path)
    print(f'rows: {len(df)}')
    print(f'cols: {list(df.columns)[:40]}')
    for c in ['volume_num', 'liquidity_num', 'feesEnabled', 'takerBaseFee',
              'uma_resolution_status', 'category', 'orderPriceMinTickSize',
              'orderMinSize']:
        if c in df.columns:
            print(f'-- {c}: missing={df[c].isna().mean():.2%}')
    if 'volume_num' in df.columns:
        v = pd.to_numeric(df['volume_num'], errors='coerce')
        df['volume_num'] = v.fillna(0)
        print('volume>0 share:', (v > 0).mean())
    if 'uma_resolution_status' in df.columns:
        print(df['uma_resolution_status'].value_counts(dropna=False).head(10).to_string())
    df['family'] = df.apply(family_key, axis=1)

    if 'volume_num' in df.columns:
        liq = df[df['volume_num'] > 0]
        fam = liq.groupby('family').agg(
            n_markets=('conditionId', 'size'),
            total_volume=('volume_num', 'sum'),
        ).sort_values('n_markets', ascending=False)
    else:
        fam = df.groupby('family').size().rename('n_markets').to_frame().sort_values('n_markets', ascending=False)
    print(f'families: {len(fam)}')
    print('--- top 25 families by market count (liquid) ---')
    print(fam.head(25).to_string())
    fam.to_csv(OUT / 'polymarket_families.csv')
    if 'takerBaseFee' in df.columns:
        print('--- takerBaseFee distribution ---')
        print(pd.to_numeric(df['takerBaseFee'], errors='coerce').describe().to_string())
    if 'orderPriceMinTickSize' in df.columns:
        print('--- orderPriceMinTickSize distribution ---')
        print(pd.to_numeric(df['orderPriceMinTickSize'], errors='coerce').describe().to_string())


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1
         else str(OUT / 'polymarket_markets.partial.parquet'))
