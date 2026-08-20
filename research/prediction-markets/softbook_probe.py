import glob
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / 'data' / 'football-data'

BOOKS = [('B365', ['B365H', 'B365D', 'B365A'], ['B365CH', 'B365CD', 'B365CA']),
         ('BMGM', ['BMGMH', 'BMGMD', 'BMGMA'], ['BMGMCH', 'BMGMCD', 'BMGMCA']),
         ('BV', ['BVH', 'BVD', 'BVA'], ['BVCH', 'BVCD', 'BVCA']),
         ('BW', ['BWH', 'BWD', 'BWA'], ['BWCH', 'BWCD', 'BWCA']),
         ('CL', ['CLH', 'CLD', 'CLA'], ['CLCH', 'CLCD', 'CLCA']),
         ('LB', ['LBH', 'LBD', 'LBA'], ['LBCH', 'LBCD', 'LBCA'])]


def load(season_glob):
    rows = []
    for f in sorted(glob.glob(str(DATA / season_glob))):
        df = pd.read_csv(f)
        league = Path(f).name.split('_')[0]
        for name, _, cc in BOOKS:
            if cc[0] not in df.columns or 'PSCH' not in df.columns:
                continue
            sub = df[df['PSCH'].notna() & df['PSCD'].notna() & df['PSCA'].notna() & df[cc[0]].notna()].copy()
            for leg, c in zip(['H', 'D', 'A'], cc):
                rows.append({'league': league, 'date': sub['Date'].astype(str), 'home': sub['HomeTeam'],
                             'away': sub['AwayTeam'], 'result': sub['FTR'], 'book': name, 'leg': leg,
                             'soft': sub[c].values, 'ps': sub['PSCH'].values if leg == 'H'
                             else (sub['PSCD'].values if leg == 'D' else sub['PSCA'].values)})
    return pd.concat([pd.DataFrame(r) for r in rows], ignore_index=True)


def dejuice(x, y, z):
    i = 1 / x + 1 / y + 1 / z
    return (1 / x) / i, (1 / y) / i, (1 / z) / i


def analyze(df, tag):
    res = []
    for (league, date, home, away, book), g in df.groupby(['league', 'date', 'home', 'away', 'book']):
        ph, pd_, pa = dejuice(g[g.leg == 'H']['ps'].iloc[0], g[g.leg == 'D']['ps'].iloc[0], g[g.leg == 'A']['ps'].iloc[0])
        pin = {'H': ph, 'D': pd_, 'A': pa}
        ftr = g['result'].iloc[0]
        for leg in ['H', 'D', 'A']:
            soft = g[g.leg == leg]['soft'].iloc[0]
            ev = soft * pin[leg] - 1
            won = int(ftr == leg)
            res.append({'league': league, 'date': date, 'home': home, 'away': away, 'book': book,
                        'leg': leg, 'soft': soft, 'ps': g[g.leg == leg]['ps'].iloc[0],
                        'p_sharp': pin[leg], 'ev': ev, 'won': won, 'result': ftr})
    r = pd.DataFrame(res)
    print(f'== {tag}: {len(r)} bet rows (fixture-book-leg) ==')
    for tau in (0.01, 0.02, 0.03, 0.04):
        s = r[r['ev'] > tau]
        if len(s) == 0:
            print(f'  tau={tau:.0%}: n=0'); continue
        roi = (s['won'] * (s['soft'] - 1) - (1 - s['won'])).mean()
        print(f'  tau={tau:.0%}: n={len(s)} win={s["won"].mean():.3f} ROI={roi:+.3%} (net {roi-0.01:+.3%})')
    # brier
    b = r.copy()
    b['ph'] = 0.0; b['pd_'] = 0.0; b['pa'] = 0.0
    for (league, date, home, away, book), g in b.groupby(['league', 'date', 'home', 'away', 'book']):
        ph, pd_, pa = dejuice(g[g.leg == 'H']['ps'].iloc[0], g[g.leg == 'D']['ps'].iloc[0], g[g.leg == 'A']['ps'].iloc[0])
        b.loc[g.index, 'ph'], b.loc[g.index, 'pd_'], b.loc[g.index, 'pa'] = ph, pd_, pa
    bb = b[b['leg'] == 'H'].copy()
    bb['brier_pin'] = ((bb['ph'] - (bb['result'] == 'H').astype(int)) ** 2 +
                       (bb['pd_'] - (bb['result'] == 'D').astype(int)) ** 2 +
                       (bb['pa'] - (bb['result'] == 'A').astype(int)) ** 2)
    brier = {'pinnacle': bb['brier_pin']}
    for name, _, cc in BOOKS:
        sbook = b[b['book'] == name]
        if len(sbook) == 0:
            print(f'  brier {name}: no data'); continue
        b2 = []
        for (league, date, home, away), g in sbook.groupby(['league', 'date', 'home', 'away']):
            so = {leg: g[g.leg == leg]['soft'].iloc[0] for leg in ['H', 'D', 'A']}
            sh, sd_, sa = dejuice(so['H'], so['D'], so['A'])
            b2.append({'result': g['result'].iloc[0], 'ph': sh, 'pd_': sd_, 'pa': sa})
        b2 = pd.DataFrame(b2)
        b2['brier_soft'] = ((b2['ph'] - (b2['result'] == 'H').astype(int)) ** 2 +
                            (b2['pd_'] - (b2['result'] == 'D').astype(int)) ** 2 +
                            (b2['pa'] - (b2['result'] == 'A').astype(int)) ** 2)
        brier[name] = b2['brier_soft'].mean()
        print(f'  brier {name}: {brier[name]:.4f} (n={len(b2)})')
    print(f'  brier Pinnacle: {bb["brier_pin"].mean():.4f}')
    # per-book realized at tau=2%
    s = r[(r['ev'] > 0.02)]
    if len(s):
        pb = s.groupby('book').apply(lambda x: pd.Series({'n': len(x), 'roi': (x['won'] * (x['soft'] - 1) - (1 - x['won'])).mean()})).reset_index()
        print(pb.to_string(index=False))
        half = s.copy()
        half['dt'] = pd.to_datetime(half['date'], format='%d/%m/%Y', errors='coerce')
        half['half'] = half['dt'].apply(lambda d: 'Aug-Oct' if d.month <= 10 else ('Nov-Jan' if d.month >= 11 else 'other'))
        ph = half[half['half'].isin(['Aug-Oct', 'Nov-Jan'])].groupby('half').apply(
            lambda x: pd.Series({'n': len(x), 'win': x['won'].mean(), 'roi': (x['won'] * (x['soft'] - 1) - (1 - x['won'])).mean()})).reset_index()
        print(ph.to_string(index=False))
        pl = s.groupby('league').apply(lambda x: pd.Series({'n': len(x), 'roi': (x['won'] * (x['soft'] - 1) - (1 - x['won'])).mean()})).reset_index()
        print(pl.to_string(index=False))
    r.to_csv(HERE / 'outputs' / f'softbook_{tag}.csv', index=False)
    return r


if __name__ == '__main__':
    is_ = load('*_2526.csv')
    analyze(is_, 'IS_2526')
    oos = load('*_2425.csv')
    analyze(oos, 'OOS_2425')