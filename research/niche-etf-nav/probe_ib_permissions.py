from ib_async import IB, Stock
import logging

logging.getLogger('ib_async').setLevel(logging.WARNING)

ib = IB()
ib.connect('127.0.0.1', 4001, clientId=11, timeout=20)
results = []
for sym in ['SPY', 'EEMX']:
    q = ib.qualifyContracts(Stock(sym, 'SMART', 'USD'))
    for wts in ['TRADES', 'BID_ASK', 'MIDPOINT']:
        try:
            bars = ib.reqHistoricalData(q[0], endDateTime='', durationStr='2 D',
                barSizeSetting='1 min', whatToShow=wts, useRTH=True, formatDate=1)
            results.append((sym, wts, 'OK', len(bars)))
        except Exception as e:
            results.append((sym, wts, 'FAIL', str(e)[:100]))
ib.disconnect()
with open('research/niche-etf-nav/probe_result.txt', 'w') as f:
    for r in results:
        f.write(repr(r) + chr(10))
