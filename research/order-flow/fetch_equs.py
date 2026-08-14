import databento as db
key=''
for line in open('.env'):
    if line.startswith('DATABENTO_API_KEY'):
        key=line.split('=',1)[1].strip().strip('"').strip("'")
        break
cli = db.Historical(key=key)
syms = ['AAPL','MSFT','NVDA','AMZN','TSLA','META','GOOGL','GOOG','JPM','V','UNH','XOM','LLY','AVGO','COST','NFLX','WMT','BAC','PG','JNJ','HD','MA','ORCL','KO','PEP','CRM','CSCO','MCD','ABBV','ADBE','AMD','QCOM','TMO','NKE','IBM','MRNA','MU','INTC','UBER','PLTR']
for schema in ['trades', 'bbo-1s']:
    out = f'research/order-flow/cache/EQ_{schema}_2026q2.parquet'
    data = cli.timeseries.get_range(
        dataset='EQUS.MINI', schema=schema, stype_in='raw_symbol',
        symbols=syms, start='2026-05-01T00:00:00', end='2026-08-01T00:00:00')
    df = data.to_df()
    df.to_parquet(out)
    print(schema, 'rows:', len(df), '| symbols:', df.symbol.nunique(), '->', out)
