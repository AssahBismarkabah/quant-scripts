# B5 Niche-ETF NAV Dislocation Candidate Registry

| ID | Mechanism | Required observable | Current access | Key failure/gap | Gate disposition |
|---|---|---|---|---|---|
| B5-01 | Stale/infrequently traded underlying assets create ETF price versus executable value divergence | Point-in-time holdings, reliable underlying marks, ETF quotes, and executable basket valuation | US-listed ETF trading may be available through IBKR; owned data does not provide a validated intraday basket-value history | NAV mark may be stale rather than mispriced; hedge/basket costs and timing are unresolved | `UNVERIFIABLE — NAV/TIMING` |
| B5-02 | AP creation/redemption impairment leaves secondary ETF price away from NAV | Live AP basket, capacity, cutoff, creation/redemption terms, and simultaneous ETF/basket execution | AP primary-market access is unavailable; only secondary ETF trading is available | Cannot observe AP intent/capacity or execute the primary arbitrage | `CLOSED FAMILY OVERLAP` |

## Source evidence

- SEC requires qualifying ETFs to post the holdings used for NAV calculation before regular trading. This does not provide historical intraday executable NAV.
- SEC prospectuses describe creation units, baskets, cutoffs, and AP agreements. This does not make the AP process available to ordinary investors.
- No candidate has been selected by a return result. No backtest is authorized.

