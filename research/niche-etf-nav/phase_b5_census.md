# B5-01 Daily NAV/Price Census

**Date:** 2026-09-18
**Status:** OBSERVABILITY TEST - data census only. No backtest, no P&L,
no strategy claim. Frozen-universe discipline per project preregistration rules.

## Scope and authorization

The user authorized reopening B5-01 for a free-data observability test on
2026-09-17. This census measures whether official SSGA NAV and end-of-day
price data show usable daily premium/dislocation structure. It does not
test the mechanism: the intraday ETF-vs-executable-basket leg requires the
blocked data sources recorded at the end of this document.

## Pre-specified universe (mechanical, frozen before fetching)

Rule: all SPDR US-listed ETFs with AUM under $400M, excluding leveraged and
inverse funds. Built from the SSGA product master file
(spdr-product-data-us-en.xlsx) by build_universe.py. Result: 70 funds,
frozen in frozen_universe_b5_01.csv before any price/NAV download.

## Data acquired

Per fund, two free SSGA endpoints were fetched by fetch_nav_price.py:

- navhist-us-en-{TICKER}.xlsx - official NAV history
- pdhist-us-en-{TICKER}.xlsx - price history including the daily
  published Premium/Discount column (units: percent)

70 of 70 funds downloaded with zero failures. Raw files cached in raw/
(gitignored, re-fetchable). Combined panel: nav_price_daily.parquet,
25,320 rows, 70 tickers, columns Date, nav, premium_reported (fraction),
ticker, abs_prem. Key discovery: SSGA already publishes the daily
premium/discount directly in pdhist, so no external price source is
needed for the daily census.

## Daily census results (corrected units, bps)

- Median premium across all fund-days: +2.0 bps (unbiased overall)
- p95 |premium|: 28.6 bps; p99: 78.3 bps
- Days with |premium| > 50 bps: 3.93%
- Days with |premium| > 100 bps: 265 events (1.05% of fund-days)
- Days with |premium| > 200 bps: 48

Top funds by mean |premium|: EEMX 69.7, QEMM 60.8, XCNY 59.4, MBND 34.6,
RWX 30.0 bps. All are EM/foreign-hours equity or currency ETFs where the
underlying closes while the ETF keeps trading - consistent with the
stale-NAV-mark mechanism, not with persistent free money.

History depth: pdhist covers only roughly the last 1.7 years per fund
(median); NAV history is longer (about 9 years for SIMS). The 265 event
days are listed in event_days_gt100bps.csv.

## Next-day convergence (pre-specified check)

For every day with |premium| > 100 bps, compare with the next official
NAV-day premium for the same fund (263 events with a successor row):

- Mean |premium| today: 170.8 bps -> mean next day: 83.1 bps
- Median |premium| today: 142.4 bps -> median next day: 59.5 bps
- Next-day |premium| smaller: 84.4% of events
- Next-day |premium| below 50 bps: 45.6%
- Sign flip next day: 47.1% (consistent with noise around NAV, not drift)
- Split by side: discounts (n=111) converge below 50 bps 43.2%; premiums
  (n=152) 47.4% - no directional asymmetry

Largest events resolve almost completely in one official NAV print, e.g.
DECO +1,056.8 bps -> +10.9 bps; SPDG +868.2 bps -> -3.0 bps. Persistence is
low overall (max run of consecutive >100 bps days: 6; median 0).

## Interpretation (census-level only)

Official end-of-day NAV deviations from close price are frequent but
strongly mean-reverting by the next NAV print. This is the daily signature
of stale NAV marks on hard-to-price or foreign-hours baskets, and it does
NOT establish tradable edge: these are official-NAV vs close-price gaps,
not synchronized executable prices. The mechanism test needs intraday
ETF bid/ask versus an executable basket valuation during the ETF session,
which is exactly the input the original feasibility audit could not own.

## Blocked items (unchanged blockers)

1. Databento historical NBBO - account locked (auth_account_locked via
   API with the key from .env). Requires contacting Databento support.
   This was the free-credits route for historical quote windows.
2. TWS / IB Gateway - not running (ports 7496/7497/4001/4002 closed; TWS
   installed at ~/Applications/Trader Workstation). Needed for IBKR
   historical BID_ASK on the intraday ETF-vs-basket leg (documented
   pacing: 60 requests/10 min, BID_ASK counts double; sub-30s bars only
   last 6 months).

## Disposition

Daily observability gate: PASSED - structure exists and is measurable on
free data. Mechanism gate: UNCHANGED UNVERIFIABLE - NAV/TIMING until an
intraday executable-basket route is unblocked. No trading conclusion is
drawn from this census.
