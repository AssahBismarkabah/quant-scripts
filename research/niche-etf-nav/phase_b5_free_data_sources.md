# B5 Free and Low-Cost Data Source Survey

**Date:** 2026-09-17
**Status:** INFORMATIONAL - no purchase, no backtest, no status change

## Purpose

The B5 feasibility audit closed with UNVERIFIABLE because point-in-time
executable basket history was not established with owned data. This survey
records which of the missing B5-01 inputs have free or already-subscribed
routes. It does not reopen B5-01; reopening requires a new authorization
decision and a re-frozen universe.

## Source verification method

Each source marked VERIFIED was fetched live on 2026-09-17 from this
workspace. Sources marked REPORTED come from web search results and still
require a fetch test before use.

## Input-by-input findings

### Official daily NAV history - VERIFIED FREE

SSGA publishes full NAV history as XLSX on each SPDR product page:

    https://www.ssga.com/library-content/products/fund-data/etfs/us/navhist-us-en-spy.xlsx
    https://www.ssga.com/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx

The SPY NAV file fetched successfully (HTTP 200, OOXML, 5,892 rows, roughly
23 years) with columns Date, NAV, Shares Outstanding, Total Net Assets. The
daily holdings file fetched successfully (HTTP 200, OOXML) with Name, Ticker,
CUSIP, SEDOL, Weight, Sector, Shares Held as of the latest trading day.
Pattern: navhist-us-en-TICKER.xlsx and holdings-daily-us-en-TICKER.xlsx.

REPORTED: iShares publishes equivalent per-fund downloads (NAV history and
holdings with historical asOfDate support), but the ajax URL pattern tested
on 2026-09-17 returned HTML; the documented scraper
https://github.com/talsan/ishares shows the working extraction route. An
iShares NAV-history downloader also exists at
https://github.com/shafiquejamal/ishares-etf-data-download.

### Point-in-time holdings - FREE with coverage limits

SEC Form N-PORT data sets are free bulk downloads, VERIFIED on
https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets
with quarterly files 2019q4 through 2026q2 present. Coverage: quarterly,
position-level, CUSIP/ISIN identifiers. N-PORT does not cover ETFs organized
as unit investment trusts (SPDR US ETFs are UITs), so per-ETF coverage must
be checked per issuer; SSGA daily-holdings files cover the current day only,
so a UIT-holdings time series must come from issuer archives or a paid
vendor.

### Intraday quotes for the ETF and equities - FREE ROUTE, THROUGHPUT-LIMITED

IBKR historical BID_ASK is available to existing accounts at no added cost.
VERIFIED constraints from official docs
(https://interactivebrokers.github.io/tws-api/historical_limitations.html):
at most 60 historical requests per 10 minutes, with each BID_ASK request
counted twice (effectively 30 per 10 minutes); bars of 30 seconds or finer
are unavailable older than 6 months; time and sales beyond 3 years is
unavailable; no data exists for delisted securities (survivorship
constraint).

Consequence: a few hundred ETF-day events with 1-minute bars (or finer within
the last 6 months) are reachable for free; thousands of events over many
years are not.

REPORTED: Databento provides 125 USD of free historical credits to new users
(https://databento.com/pricing), usable for NBBO on specific date windows.
Massive (formerly Polygon) historical quotes require the Advanced tier at
199 USD/month (https://massive.com/pricing). Alpaca free tier is IEX-only
and not a suitable NBBO proxy. Free 1-minute OHLC repositories exist but do
not provide bid/ask.

### Shares outstanding and flows - FREE

SSGA navhist files include daily Shares Outstanding (VERIFIED above). ETF
Global flows are commercial (Snowflake marketplace listing); free
community-maintained flow datasets exist (REPORTED:
https://github.com/isaergun/etf-flows-data).

### Creation/redemption baskets - FREE CURRENT-DAY ONLY

SSGA daily holdings files are the current creation basket; historical basket
changes must be reconstructed from holdings-file archives that issuers do
not host historically. This remains the one input with no free historical
route, but B5-01 (secondary-market dislocation versus executable basket)
does not require the historical AP basket, only the daily disclosed
portfolio.

## What this changes for B5-01

A testable equity-ETF design using only free or owned sources:

1. Re-freeze the universe to equity-holding niche ETFs from issuers that
   publish daily holdings and NAV archives, replacing the current bond
   universe whose underlyings have no US quotes.
2. Build daily point-in-time holdings from issuer archives and SEC N-PORT
   quarters.
3. Pull ETF and large-underlying BID_ASK bars from IBKR within its pacing
   and depth limits, with Databento free credits reserved for event windows.
4. Feed the existing coverage-aware valuation in
   src/quant_scripts/niche_etf_nav/valuation.py (requires adding a coverage
   threshold instead of the current all-or-nothing rule).

Remaining gates after data: cost-model freeze, event-sample census, and
preregistered kill criteria. This survey alone does not authorize any of it.

## Registry cross-reference

The candidate registry remains authoritative. B5-01 stays
UNVERIFIABLE - NAV/TIMING until data is actually acquired and the gate is
re-run; this document only establishes that the acquisition route exists
without new spend.
