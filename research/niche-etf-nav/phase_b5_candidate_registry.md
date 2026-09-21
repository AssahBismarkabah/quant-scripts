# B5 Candidate Registry

| ID | Concrete mechanism | Access/timing | Required fields | Friction/capacity | Six-gate disposition |
|---|---|---|---|---|---|
| B5-01 | A US-listed ETF holding difficult-to-price assets trades away from a fully executable basket | ETF secondary market through IBKR; holdings, ETF quote, underlying bid/ask, and NAV must overlap before entry | Point-in-time quantities, corporate actions, executable quotes, ETF quote, fees, slippage, tracking error, settlement | Coverage incomplete; basket hedge and capacity unresolved | G1 pass; G2 fail; G3 unresolved; G4 unresolved; G5 unresolved; G6 unestablished → `UNVERIFIABLE — NAV/TIMING` |
| B5-02 | AP creation/redemption impairment leaves an ETF away from NAV | Retail can trade ETF through IBKR but cannot act as AP | AP intent/capacity, basket, creation unit, cutoff, settlement, fees | Primary AP route unavailable | G1 pass; G2 fail; G3 closed overlap; remaining gates not reached → `CLOSED FAMILY OVERLAP` |

## Free-data re-verification note (2026-09-17)

[phase_b5_free_data_sources.md](phase_b5_free_data_sources.md) records that SSGA publishes full daily NAV and shares-outstanding history plus current-day holdings free of charge (fetched and verified), SEC N-PORT quarterly data sets are free (2019q4-2026q2), and IBKR historical BID_ASK is reachable within documented pacing limits. This establishes a no-new-spend acquisition route for B5-01 but does not change its disposition: reopening requires a re-frozen equity-ETF universe, actual data acquisition, and a re-run of the observability gate.
 
## Daily census (2026-09-18)
 
[phase_b5_census.md](phase_b5_census.md) records the authorized free-data observability test: a mechanically frozen 70-fund universe (SPDR US ETFs under 400M dollars, no leveraged/inverse), 25,320 fund-days of official SSGA NAV and published premium/discount data fetched with zero failures, and the pre-specified next-day convergence check. Result: 265 events above 100 bps (1.05 percent of fund-days), concentrated in EM/foreign-hours funds (EEMX, QEMM, XCNY); 84.4 percent shrink next day and 45.6 percent converge below 50 bps by the next NAV print. Daily observability gate PASSED; the B5-01 disposition is unchanged UNVERIFIABLE - NAV/TIMING because the intraday ETF-vs-executable-basket test remains blocked (Databento account locked; TWS/Gateway not running).
 
## B5-01 closure (2026-09-21)
 
Access route attempted: IB Gateway 10.51 installed and connected successfully (port 4001, live session); historical TRADES data flowed (780 one-minute bars per fund over 2 days), confirming the API path works end to end. Historical and live BID_ASK was refused: account has no US equities market-data subscription for API use. The cheapest sufficient feeds (NYSE American/BATS/ARCA/IEX Network B at USD 1.50/month; full basket coverage A+B+C at USD 4.50/month) are gated by IBKR's minimum-equity requirement for market-data activation, which the account does not currently meet. The Databento free-credits route remains blocked (auth_account_locked).
 
With no zero-spend route to synchronized intraday ETF and basket quotes, the mechanism test cannot be run with current access. B5-01 is closed as UNVERIFIABLE - ACCESS. The daily census result stands as the recorded observability finding. Legitimate reopen conditions (any one): (1) account equity rises above IBKR's market-data minimum and Network feeds are activated, (2) Databento account is unlocked, or (3) another owned/zero-cost source of synchronized intraday NBBO-class quotes becomes available. Reopening also requires a re-frozen universe and re-run of the observability gate, unchanged from prior notes.
