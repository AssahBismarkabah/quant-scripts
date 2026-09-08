# Phase A2: Capacity-Constrained Securities Mechanism Audit

**Status:** COMPLETE — `NO VIABLE MECHANISM FOUND`

**Authorization:** Explicit second cycle after Phase A1. A1 closed forced-flow and settlement only; it did not close the remaining mechanism families.

**Run boundary:** 2026-09-06; 15 concrete mechanisms investigated; no paid data, return analysis, backtest, parameter search, or strategy implementation.

## Scope and amendment

This cycle covered the full capacity-constrained securities family: small-cap and micro-cap equities, fund liquidity constraints, listing and quotation constraints, corporate-action supply constraints, securities lending restrictions, and illiquid small-cap options.

The following governance amendment is now recorded:

1. Phase A1, forced-flow and settlement, is complete with `NO VIABLE MECHANISM FOUND`.
2. A1 closes only its selected family; it does not close the entire mechanism-first program.
3. Phase A2 was authorized for one bounded capacity-constrained securities audit.
4. Any Phase A3 requires a separate explicit project amendment.
5. A failed or unverifiable A2 result does not authorize another family automatically.

The audit did not treat low market capitalization, low analyst coverage, wide spreads, “ignored” stocks, volatility, or an attractive historical pattern as mechanisms.

## Terminal result

`NO VIABLE MECHANISM FOUND`.

The sources establish genuine institutional size, liquidity, listing, borrowing, and market-making constraints. None supplied the complete chain required for one testable mechanism:

`capacity constraint → timestamped pre-trade observable → directional pressure → identifiable counterparty → executable retail advantage after friction → sufficient independent events`.

This is a mechanism and observability conclusion, not a claim that every small security is efficiently priced.

## Gate notation

- **G1 Constraint evidence:** primary source proves the defined institutional or market-participant constraint.
- **G2 Observable:** the constraint is known before the proposed trade using available data.
- **G3 Non-immediacy:** a specific reason exists for the effect to survive immediate arbitrage.
- **G4 Counterparty/execution:** the counterparty and executable venue exist at our scale.
- **G5 Friction/capacity:** spread, slippage, impact, fees, borrow, financing, rejects, and operational risk can be modeled.
- **G6 Sample sufficiency:** enough independent events exist without broadening the definition.

## Candidate dispositions

The complete registry is [phase_a_candidate_registry.md](../research/capacity-constrained-securities/phase_a_candidate_registry.md). The candidates were deliberately specific:

| ID | Mechanism | Gate outcome | Disposition |
|---|---|---|---|
| CC-01 | Open-end fund 15% illiquid-asset limit | G1 yes; G2 fund classifications are mostly private/non-timestamped; G3-G6 unavailable | `UNVERIFIABLE — DATA OR TIMING` |
| CC-02 | Fund highly-liquid-investment minimum and redemption management | G1 yes; no public fund-level trade direction or trigger timestamp | `UNVERIFIABLE — DATA OR TIMING` |
| CC-03 | Russell minimum market-cap and float eligibility | G1/G2 yes; already an index eligibility/rebalance family and not a new trade constraint | `CLOSED FAMILY OVERLAP` |
| CC-04 | Russell minimum price and exchange eligibility | G1/G2 yes; no mandatory directional trade by excluded securities | `REJECTED — NO MECHANISM` |
| CC-05 | Nasdaq listing minimum public float and market-maker requirements | G1 yes; listing eligibility is not a recurring trading obligation with known direction | `REJECTED — NO MECHANISM` |
| CC-06 | FINRA OTC minimum quotation-size obligations | G1 yes; quote-size floor does not identify directional pressure or profitable counterparty | `REJECTED — NO MECHANISM` |
| CC-07 | Regulation SHO locate requirement for hard-to-borrow small caps | G1 yes; this creates a short-side restriction, not a pre-trade long signal; shorting is not authorized without borrow data | `REJECTED — EXECUTION/FRICTION` |
| CC-08 | Threshold-security close-out requirement after persistent fails | G1/G2 yes; close-out direction and timing are not sufficiently observable before execution; high overlap with settlement/short-sale mechanics | `UNVERIFIABLE — DATA OR TIMING` |
| CC-09 | Public securities-lending transaction reporting | G1/G2 partial; reporting is not a historical, actionable locate/recall forecast | `UNVERIFIABLE — DATA OR TIMING` |
| CC-10 | IPO lockup expiration releases restricted supply | Contract dates can be public; issuer-holder behavior, actual supply, borrow, and event sample are not fixed prospectively | `UNVERIFIABLE — DATA OR TIMING` |
| CC-11 | Rule 144 resale-volume limits for restricted holders | Rule constrains selling, but does not force a trade or identify when a holder sells | `REJECTED — NO MECHANISM` |
| CC-12 | PIPE/private-placement resale registration becoming effective | Registration is observable; holder sale timing and price-insensitive direction are not | `UNVERIFIABLE — DATA OR TIMING` |
| CC-13 | Fractional-share cash settlement after reverse split/corporate action | Processing is mandatory for intermediaries; aggregate market pressure and executable direction are unknown | `REJECTED — NO MECHANISM` |
| CC-14 | Small-cap options market-maker affirmative quoting obligations | Obligations exist, but options-flow family is closed and small-cap quote depth/response is not observable with available data | `CLOSED FAMILY OVERLAP` |
| CC-15 | ETF/in-kind creation-redemption capacity applied to small underlying baskets | Primary-market access and AP flow are unavailable; duplicate of A1 ETF/AP mechanism | `CLOSED FAMILY OVERLAP` |

## Primary-source conclusion

The strongest evidence was regulatory and operational rather than predictive:

- SEC Rule 22e-4 limits open-end funds to 15% illiquid assets and requires liquidity classification, but the relevant fund classifications and internal decisions do not provide a public directional trade signal. [SEC liquidity-risk guide](https://www.sec.gov/resources-small-businesses/small-business-compliance-guides/investment-company-liquidity-risk-management-program-rules)
- FTSE Russell excludes securities below a minimum market capitalization and applies float and trading eligibility rules, but this belongs to the already closed index-rebalancing/eligibility family. [Russell US Equity Indexes methodology](https://research.ftserussell.com/products/downloads/Russell-US-indexes.pdf)
- Nasdaq listing rules require minimum public float and market-maker participation, but listing eligibility does not create a predictable forced trade in the secondary market. [Nasdaq Initial Listing Guide](https://listingcenter.nasdaq.com/Assets/Initialguide.pdf)
- FINRA quotation rules can require OTC market makers to honor displayed minimum sizes, but a quote-size obligation does not reveal directional pressure or a retail counterparty advantage. [FINRA Notice 93-54](https://www.finra.org/rules-guidance/notices/93-54)
- Regulation SHO requires a locate before most equity short sales and imposes close-out rules for fails, but this is a constraint on execution rather than a free long signal. [SEC Regulation SHO guidance](https://www.sec.gov/rules-regulations/staff-guidance/trading-markets-frequently-asked-questions-8)

## Phase B/C decision

No candidate passed all six gates. No candidate is approved for Phase B, and no Phase C trading test is authorized.

Phase A3 or another family requires an explicit project-level amendment. The capacity-constrained securities family is closed for this audit; it may not be reopened under a new name such as “microcap momentum,” “low-coverage alpha,” or “small-cap neglect.”

