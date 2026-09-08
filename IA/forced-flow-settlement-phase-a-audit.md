# Phase A: Forced-Flow and Settlement Mechanism Audit

**Status:** COMPLETE — `NO VIABLE MECHANISM FOUND`

**Run boundary:** 2026-09-06; 12 concrete candidates investigated; no backtest, return comparison, parameter search, or paid-data purchase.

## Purpose and stop rule

This was a bounded mechanism-discovery cycle. A candidate had to identify a constrained participant, a causal external rule, a pre-trade observable, a plausible reason for non-immediacy, an executable retail path, conservative friction/capacity, and enough independent events. The cycle was limited to 15 calendar days or 20 candidates, whichever came first. It terminated after 12 candidates because the remaining variants were duplicates of rejected or already-closed families.

No candidate was allowed to proceed to historical P&L after failing a gate.

## Result

`NO VIABLE MECHANISM FOUND`.

The audit found real settlement and participation rules, but no mechanism that simultaneously provided (a) an observable directional pressure before trading and (b) an executable retail-scale advantage after friction. This is a mechanism/observability conclusion, not a claim that markets cannot contain forced flows.

## Gate notation

- **G1 Constraint evidence:** primary source proves a defined participant must trade or is materially constrained.
- **G2 Observable:** the constraint is observable before the proposed trade with data available to us.
- **G3 Non-immediacy:** a credible reason exists for pressure not to be instantly arbitraged.
- **G4 Counterparty/execution:** both the other side and our execution path are identifiable.
- **G5 Friction/capacity:** spread, slippage, impact, fees, financing, borrow, and operational limits can be modeled.
- **G6 Sample sufficiency:** enough independent events exist without loosening the definition.

## Candidate registry

The full structured registry is [phase_a_candidate_registry.md](../research/forced-flow-settlement/phase_a_candidate_registry.md). The dispositions are summarized here:

| ID | Concrete mechanism | Overlap decision | Disposition |
|---|---|---|---|
| FF-01 | CME ES/MES quarterly SOQ cash settlement | Settlement; distinct from ordinary ORB, but equity-index settlement execution is not observable directionally | `UNVERIFIABLE — DATA OR TIMING` |
| FF-02 | CME NQ quarterly SOQ cash settlement | Same settlement family as FF-01; no materially distinct mechanism | `CLOSED FAMILY OVERLAP` |
| FF-03 | CME TMAC marker execution around settlement | Settlement execution facility, not a forced directional participant flow | `REJECTED — NO MECHANISM` |
| FF-04 | ETF authorized-participant creation/redemption | Distinct primary-market plumbing; retail cannot use the creation/redemption path | `UNVERIFIABLE — DATA OR TIMING` |
| FF-05 | Cash-created ETF/ETP baskets at a scheduled cutoff | Same AP mechanism as FF-04 | `CLOSED FAMILY OVERLAP` |
| FF-06 | S&P index constituent/float rebalance flow | Explicitly overlaps the already closed index-rebalancing family | `CLOSED FAMILY OVERLAP` |
| FF-07 | Treasury auction primary-dealer participation | Auction rules prove participation, not price-insensitive directional demand; no pre-trade direction | `UNVERIFIABLE — DATA OR TIMING` |
| FF-08 | Treasury buyback eligibility and delivery requirement | Primary-source rule exists, but eligibility and accepted-offer direction are not available as a retail pre-trade signal | `UNVERIFIABLE — DATA OR TIMING` |
| FF-09 | Treasury futures delivery/first-notice constraints | Delivery obligations exist, but deliverable choice, positions, and pressure are not observable to us before execution | `UNVERIFIABLE — DATA OR TIMING` |
| FF-10 | OCC cash-settled index/currency option exercise settlement | Settlement is mechanical cash transfer, not a known directional flow; options family is already closed | `CLOSED FAMILY OVERLAP` |
| FF-11 | Mandatory corporate-action distribution/settlement | A corporate action is mandatory for processing, not necessarily a price-insensitive trade by a constrained participant | `REJECTED — NO MECHANISM` |
| FF-12 | Clearing/margin liquidation or buy-in | Forced action can occur, but trigger, participant, timing, and direction are not observable before the event | `UNVERIFIABLE — DATA OR TIMING` |

## Evidence and decisions

The primary-source record is [phase_a_source_evidence.md](../research/forced-flow-settlement/phase_a_source_evidence.md). The strongest sources establish rules, not an investable edge:

- CME defines ES/S&P 500 final settlement by a Special Opening Quotation from component-stock opening prices, with cash settlement for expiring contracts. That establishes a settlement constraint, but not whether the pressure is buy or sell, who must trade, or a retail-accessible execution advantage. [CME final settlement procedures](https://www.cmegroup.com/trading/equity-index/settlement.html), [CME Rule 363](https://www.cmegroup.com/rulebook/CME/IV/350/363/363.pdf)
- CME describes TMAC as a way to execute at a settlement marker. That is an execution service for participants managing settlement risk, not evidence of a predictable price distortion available to a small trader. [CME TMAC](https://www.cmegroup.com/markets/equities/tmac-on-equity-index-futures.html)
- SEC ETF prospectuses establish that only authorized participants can create or redeem creation units, while retail investors trade in the secondary market. This proves an access asymmetry, but does not give us the AP's basket order, timing, or direction before the trade. [SEC ETF prospectus example](https://www.sec.gov/Archives/edgar/data/1100663/000119312525211179/d34352d485apos.htm)
- Treasury's official auction material establishes eligible bidders, auction deadlines, and primary-dealer participation. It does not establish that a predictable forced directional flow remains after the auction or that a Cameroon-based retail trader can observe and execute against it. [Treasury auction FAQ](https://www.treasurydirect.gov/help-center/faqs/auction-faqs/), [Treasury primary-dealer criteria](https://www.treasurydirect.gov/files/laws-and-regulations/gsa/gsa-reg-gsr-92-rpt.pdf)
- OCC rules establish cash settlement and exercise/assignment mechanics. They do not establish a pre-trade directional imbalance. [OCC cash-settled currency options](https://www.theocc.com/clearance-and-settlement/clearing/u-s-dollar-cash-settled-currency-options)
- S&P methodology establishes scheduled index changes, but this is the project’s already closed index-rebalancing family. [S&P methodology example](https://www.spglobal.com/spdji/en/methodology/article/dow-jones-bic-50-index-methodology/)

## Why no candidate advanced

The recurring failure was not lack of a rule. It was the missing chain:

`external constraint → known participant and direction → observable before execution → identifiable counterparty → executable trade after friction`.

The sources support pieces of that chain, but none of the 12 candidates supplied the whole chain with currently available data and venue access. Buying data would not cure a candidate that is already closed, lacks directional observability, or cannot be executed through the relevant primary/settlement mechanism.

## Phase B and C decision

No candidate is approved for Phase B. Therefore no Phase C test is authorized. The current project record remains terminal under the mechanism-first rule: systematic discovery stops unless the project receives an explicit amendment with a materially different scope, capability, or mechanism.

This document does not claim that the user cannot ever trade profitably. It records that this bounded forced-flow/settlement audit did not identify a defensible next test.
