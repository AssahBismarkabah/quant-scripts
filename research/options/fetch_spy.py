import databento as db, json
import pandas as pd
key=''
for line in open('.env'):
    if line.startswith('DATABENTO_API_KEY'):
        key=line.split('=',1)[1].strip().strip('"').strip("'")
        break
cli = db.Historical(key=key)
near = json.load(open('/tmp/spy_near.json'))
batches = [near[i:i+2000] for i in range(0, len(near), 2000)]
out = 'research/options/cache/SPY_cbbo-1m_2026-07.parquet'
frames = []
for bi, batch in enumerate(batches):
    print(f'batch {bi+1}/{len(batches)}...', flush=True)
    data = cli.timeseries.get_range(dataset='OPRA.PILLAR', schema='cbbo-1m',
                                    stype_in='raw_symbol', symbols=batch,
                                    start='2026-07-01T00:00:00', end='2026-08-01T00:00:00')
    frames.append(data.to_df())
df = pd.concat(frames)
df.to_parquet(out)
print('rows:', len(df), '| GB on disk:', round(df.memory_usage(deep=True).sum()/1e9, 2), '->', out)
