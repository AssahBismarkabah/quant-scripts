import databento as db
key=''
for line in open('.env'):
    if line.startswith('DATABENTO_API_KEY'):
        key=line.split('=',1)[1].strip().strip('"').strip("'")
        break
cli = db.Historical(key=key)
for schema in ['trades', 'bbo-1s']:
    out = f'research/order-flow/cache/NQ_{schema}_2026q2.parquet'
    data = cli.timeseries.get_range(
        dataset='GLBX.MDP3', schema=schema, stype_in='continuous',
        symbols=['NQ.n.0'], start='2026-05-01T00:00:00', end='2026-08-01T00:00:00')
    df = data.to_df()
    df.to_parquet(out)
    print(schema, 'rows:', len(df), '->', out)
