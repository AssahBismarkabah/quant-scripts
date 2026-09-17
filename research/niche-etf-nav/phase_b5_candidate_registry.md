# B5 Candidate Registry

| ID | Concrete mechanism | Access/timing | Required fields | Friction/capacity | Six-gate disposition |
|---|---|---|---|---|---|
| B5-01 | A US-listed ETF holding difficult-to-price assets trades away from a fully executable basket | ETF secondary market through IBKR; holdings, ETF quote, underlying bid/ask, and NAV must overlap before entry | Point-in-time quantities, corporate actions, executable quotes, ETF quote, fees, slippage, tracking error, settlement | Coverage incomplete; basket hedge and capacity unresolved | G1 pass; G2 fail; G3 unresolved; G4 unresolved; G5 unresolved; G6 unestablished → `UNVERIFIABLE — NAV/TIMING` |
| B5-02 | AP creation/redemption impairment leaves an ETF away from NAV | Retail can trade ETF through IBKR but cannot act as AP | AP intent/capacity, basket, creation unit, cutoff, settlement, fees | Primary AP route unavailable | G1 pass; G2 fail; G3 closed overlap; remaining gates not reached → `CLOSED FAMILY OVERLAP` |

## Free-data re-verification note (2026-09-17)

[phase_b5_free_data_sources.md](phase_b5_free_data_sources.md) records that SSGA publishes full daily NAV and shares-outstanding history plus current-day holdings free of charge (fetched and verified), SEC N-PORT quarterly data sets are free (2019q4-2026q2), and IBKR historical BID_ASK is reachable within documented pacing limits. This establishes a no-new-spend acquisition route for B5-01 but does not change its disposition: reopening requires a re-frozen equity-ETF universe, actual data acquisition, and a re-run of the observability gate.
