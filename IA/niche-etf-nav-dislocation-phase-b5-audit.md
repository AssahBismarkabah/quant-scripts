# B5 Niche-ETF NAV Dislocation Feasibility Audit

**Date:** 2026-09-17  
**Status:** COMPLETE — UNVERIFIABLE / CLOSED FAMILY OVERLAP

## Scope

US-listed ETFs only. Two mechanisms were evaluated separately:

1. stale or infrequently traded underlying assets creating a difference between ETF price and executable underlying value;
2. impaired AP creation/redemption.

No return analysis, backtest, parameter search, data purchase, or new account was used.

## Primary-source findings

SEC materials establish that ETFs publish portfolio holdings used for NAV calculations before regular trading and that APs create/redeem creation units using baskets. [SEC website-posting requirements](https://www.sec.gov/about/divisions-offices/division-investment-management/accounting-disclosure-information/adi-2025-15) [SEC ETF prospectus example](https://www.sec.gov/Archives/edgar/data/1633061/000121390026010237/ea0273008-32_497.htm)

The same sources establish that non-AP investors cannot directly create or redeem individual ETF shares; orders must be placed through an AP. This confirms an access asymmetry, not a retail trading advantage. SEC materials also describe the arbitrage mechanism as intended to keep ETF prices near NAV. [SEC ETF creation/redemption disclosure](https://www.sec.gov/Archives/edgar/data/1884021/000121390025102126/ea0262228-04_485apos.htm)

## Gate decisions

| Mechanism | Constraint/mechanics | NAV/timing | Execution | Distinctness | Sample | Disposition |
|---|---|---|---|---|---|---|
| Stale underlying NAV | Difficult-to-price holdings can make marks stale, but a stale mark is not executable value | Daily holdings are available; intraday executable basket value is not established with owned data | ETF execution may be available, but hedging/underlying execution and costs are not frozen | Provisionally distinct from AP primary-market flow | Not established | `UNVERIFIABLE — NAV/TIMING` |
| AP creation/redemption impairment | APs use creation units and baskets; retail cannot directly access the primary process | Basket/NAV disclosures do not reveal AP intent or live capacity | Retail cannot perform the primary arbitrage directly | Direct overlap with closed A1 FF-04/FF-05 | Not relevant before overlap gate | `CLOSED FAMILY OVERLAP` |

## Current terminal result

`UNVERIFIABLE`

The stale-underlying hypothesis remains economically plausible but cannot currently be distinguished from stale marks, ordinary ETF spreads, or tracking error using the owned data and verified execution path. The AP hypothesis is closed as a duplicate of A1 because the required convergence mechanism is AP-only.

No B5 mechanism is approved for a trading test. A future test would require a separately authorized capability upgrade providing point-in-time holdings, intraday indicative value or executable basket valuation, and verified historical bid/ask data.

