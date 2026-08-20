import re
import pathlib
from datetime import datetime

import pandas as pd

OUT = pathlib.Path(__file__).parent / 'outputs'
DATA = pathlib.Path(__file__).parent / 'data' / 'football-data'
PM = pd.read_parquet(OUT / 'polymarket_markets.partial.parquet',
                     columns=['id', 'question', 'conditionId', 'slug', 'endDate', 'volumeNum',
                              'closed', 'sportsMarketType', 'gameStartTime', 'outcomes', 'outcomePrices'])

LEAGUES = {'EPL': 'EPL', 'Championship': 'Championship', 'LaLiga': 'LaLiga', 'SerieA': 'SerieA', 'Bundesliga': 'Bundesliga'}

ALIAS = {
    'Wolverhampton': 'Wolves', 'Wolverhampton Wanderers': 'Wolves', 'Sheffield United': 'Sheffield Utd',
    'Sheffield United FC': 'Sheffield Utd', 'Manchester United': 'Man United', 'Manchester City': 'Man City',
    'Newcastle United': 'Newcastle', 'West Ham United': 'West Ham', 'Tottenham Hotspur': 'Tottenham',
    'Brighton and Hove Albion': 'Brighton', 'Nottingham Forest': 'Nottm Forest', 'Ipswich Town': 'Ipswich',
    'Leeds United': 'Leeds', 'Athletic Club': 'Athletic Bilbao', 'Atlético Madrid': 'Atletico Madrid',
    'Celta Vigo': 'Celta', 'Real Betis': 'Betis', 'Deportivo Alavés': 'Alaves', 'UD Las Palmas': 'Las Palmas',
    'Las Palmas': 'Las Palmas', 'Villarreal CF': 'Villarreal', 'RCD Espanyol': 'Espanyol', 'Getafe CF': 'Getafe',
    'Osasuna': 'Osasuna', 'Real Valladolid': 'Valladolid', 'Leganés': 'Leganes', 'Girona': 'Girona',
    'Rayo Vallecano': 'Rayo Vallecano', 'Real Sociedad': 'Real Sociedad', 'Sevilla FC': 'Sevilla',
    'Valencia CF': 'Valencia', 'Mallorca': 'Mallorca', 'Barcelona': 'Barcelona', 'Real Madrid': 'Real Madrid',
    'Inter': 'Inter Milan', 'AC Milan': 'AC Milan', 'Juventus': 'Juventus', 'Napoli': 'Napoli',
    'Atalanta': 'Atalanta', 'Roma': 'Roma', 'Lazio': 'Lazio', 'Fiorentina': 'Fiorentina',
    'Bologna': 'Bologna', 'Torino': 'Torino', 'Udinese': 'Udinese', 'Genoa': 'Genoa',
    'Cagliari': 'Cagliari', 'Verona': 'Verona', 'Parma': 'Parma', 'Monza': 'Monza', 'Lecce': 'Lecce',
    'Como': 'Como', 'Empoli': 'Empoli', 'Venezia': 'Venezia', 'Bayern Munich': 'Bayern Munich',
    'Borussia Dortmund': 'Dortmund', 'RB Leipzig': 'RB Leipzig', 'Bayer Leverkusen': 'Leverkusen',
    'Eintracht Frankfurt': 'Eintracht Frankfurt', 'VfB Stuttgart': 'Stuttgart', 'SC Freiburg': 'Freiburg',
    'Werder Bremen': 'Werder Bremen', 'VfL Wolfsburg': 'Wolfsburg', 'FC Augsburg': 'Augsburg',
    'Borussia Monchengladbach': 'Gladbach', '1. FSV Mainz 05': 'Mainz', '1. FC Union Berlin': 'Union Berlin',
    'FC St. Pauli': 'St. Pauli', 'TSG Hoffenheim': 'Hoffenheim', 'Holstein Kiel': 'Holstein Kiel',
    'FC Heidenheim': 'Heidenheim', 'VfL Bochum': 'Bochum',
}

def norm(name):
    name = str(name).strip()
    for k, v in ALIAS.items():
        if k.lower() in name.lower():
            return v
    return re.sub(r'\s+', ' ', name).strip()

def parse_fd_date(s):
    return datetime.strptime(str(s), '%d/%m/%Y').date()

def main():
    rows = []
    for league, fn in LEAGUES.items():
        f = DATA / f'{fn}_2526.csv'
        if not f.exists():
            continue
        d = pd.read_csv(f)
        for _, r in d.iterrows():
            if pd.isna(r.get('PSCH')):
                continue
            rows.append({
                'league': league, 'fd_date': parse_fd_date(r['Date']),
                'home': norm(r['HomeTeam']), 'away': norm(r['AwayTeam']),
                'psch': float(r['PSCH']), 'pscd': float(r['PSCD']), 'psca': float(r['PSCA']),
                'fhg': r['FTHG'], 'ftag': r['FTAG'],
            })
    fd = pd.DataFrame(rows)
    fd['fd_date_iso'] = pd.to_datetime(fd['fd_date'])
    print(f'football-data fixtures with Pinnacle closing: {len(fd)}')

    pm = PM[PM['sportsMarketType'].isin(['moneyline', 'child_moneyline'])].copy()
    pm['q'] = pm['question'].astype(str)
    pm['end'] = pd.to_datetime(pm['endDate'], utc=True, errors='coerce')
    pm['date'] = pm['end'].dt.date
    win = pm['q'].str.extract(r'Will (.+?) win on (\d{4}-\d{2}-\d{2})\?')
    pm['win_team'] = win[0]
    pm['win_date'] = win[1]
    draw = pm['q'].str.extract(r'Will (.+?) vs\. (.+?) end in a draw\?')
    pm['draw_a'] = draw[0]
    pm['draw_b'] = draw[1]

    matched = []
    for _, f in fd.iterrows():
        day = f['fd_date']
        w = pm[(pm['date'] == day) & pm['win'].notna()]
        draws = pm[(pm['date'] == day) & pm['draw'].notna()]
        rec = {'league': f['league'], 'fd_date': day, 'home': f['home'], 'away': f['away'],
               'psch': f['psch'], 'pscd': f['pscd'], 'psca': f['psca'],
               'fhg': f['fhg'], 'ftag': f['ftag']}
        found = False
        for side, name in (('home', f['home']), ('away', f['away'])):
            m = w[w['win'].str[0].apply(lambda s: norm(s) == name if s else False)]
            if len(m):
                r = m.iloc[0]
                rec[f'pm_{side}_market'] = r['question']; rec[f'pm_{side}_cid'] = r['conditionId']
                rec[f'pm_{side}_vol'] = r['volumeNum']; rec[f'pm_{side}_end'] = r['end']
                found = True
        for _, r in draws.iterrows():
            if norm(r['draw'].str[0]) == f['home'] and norm(r['draw'].str[1]) == f['away']:
                rec['pm_draw_market'] = r['question']; rec['pm_draw_cid'] = r['conditionId']
                rec['pm_draw_vol'] = r['volumeNum']
                found = True
        if found:
            matched.append(rec)
    mdf = pd.DataFrame(matched)
    print(f'fixtures with >=1 PM market: {len(mdf)}')
    both = mdf[mdf['pm_home_cid'].notna() & mdf['pm_away_cid'].notna()]
    print(f'with both home+away moneyline: {len(both)}')
    print(mdf.groupby('league').size().to_string())
    mdf.to_csv(OUT / 'candidate_a_matches.csv', index=False)
    print('saved outputs/candidate_a_matches.csv')

if __name__ == '__main__':
    main()