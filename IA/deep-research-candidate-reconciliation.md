# Deep Research Candidate Reconciliation

**Source:** [Small-Trader Advantage Audit](deep-research-report.md)

**Date:** 2026-09-12

**Status:** COMPLETE — no candidate currently eligible for a backtest

## Purpose

The deep-research report generated 30 hypotheses and selected five for feasibility discussion. This reconciliation compares all 30 against the existing project record before allowing any new test.

The report did not discover five validated strategies. It produced a candidate universe. Most candidates are relabeled versions of families already tested or closed.

Each candidate receives exactly one disposition:

- **DUPLICATE / CLOSED** — materially overlaps an existing closed family.
- **INTERESTING BUT UNVERIFIABLE** — potentially distinct, but a required mechanism, observable, access path, execution model, or sample has not been established.
- **ELIGIBLE FOR ONE TEST** — survives reconciliation and all mechanism/data gates. No candidate reached this status.

## Reconciliation of all 30 candidates

| ID | Candidate | Existing overlap or issue | Disposition |
|---|---|---|---|
| B1 | Microcap no-analyst reversal | Public reversal/anomaly search; no defined constrained participant | `DUPLICATE / CLOSED` |
| B2 | Index inclusion demand | Index-rebalancing/forced-flow family already closed | `DUPLICATE / CLOSED` |
| B3 | Low-float tender-offer arbitrage | Corporate-event/merger-arbitrage mechanism; price converges toward known consideration, not a demonstrated small-trader advantage | `INTERESTING BUT UNVERIFIABLE` |
| B4 | Thin-index sell-off | Index deletion and forced-flow family | `DUPLICATE / CLOSED` |
| B5 | Niche-ETF NAV premium/discount | Potentially distinct AP-arbitrage impairment; real-time executable NAV is unresolved | `INTERESTING BUT UNVERIFIABLE` |
| B6 | Commodity-ETF rebalance | Scheduled roll/forced-flow mechanism; no new observable or counterparty advantage | `DUPLICATE / CLOSED` |
| B7 | Frontier-market ETF stale price | Market-closed/opening-gap family; operational and execution route unresolved | `DUPLICATE / CLOSED` |
| B8 | Junk-ETF discount | ETF/NAV and credit-flow mechanism; underlying valuation and real-time NAV are unresolved | `INTERESTING BUT UNVERIFIABLE` |
| B9 | Exotic-FX futures mispricing | Scheduled policy/news event; no forced directional participant or retail execution advantage | `DUPLICATE / CLOSED` |
| B10 | Local-rate futures flow | Specialist/local flow unavailable; obscure-futures execution unverified | `INTERESTING BUT UNVERIFIABLE` |
| B11 | ChiNext/MICEX cross-market lag | Fragmented cross-venue arbitrage; simultaneous access, settlement, capital controls, and borrow unresolved | `DUPLICATE / CLOSED` |
| B12 | China Stock Connect quota delay | Specialist/operational access and cross-border restrictions; no verified retail route | `DUPLICATE / CLOSED` |
| B13 | Emerging-index rebalance | Index-rebalancing/forced-flow family | `DUPLICATE / CLOSED` |
| B14 | Quarterly dividend drift | Public calendar/anomaly and corporate-action family; no small-trader-specific mechanism | `DUPLICATE / CLOSED` |
| B15 | Spin-off release | Potentially distinct ownership, unwanted-distribution, and price-discovery mechanism; participant behavior and sample require verification | `INTERESTING BUT UNVERIFIABLE` |
| B16 | Tender-offer retreat | Corporate-event/forced-flow idea; outcome and timing are event-specific, with no verified counterparty advantage | `INTERESTING BUT UNVERIFIABLE` |
| B17 | Index reconstitution peak-end | Index-flow/window-dressing family already closed | `DUPLICATE / CLOSED` |
| B18 | Closing auction imbalance | Operational auction/order-flow family; requires imbalance data and execution capability not available in scope | `DUPLICATE / CLOSED` |
| B19 | Open auction gap | ORB/opening-range/gap family permanently closed | `DUPLICATE / CLOSED` |
| B20 | January effect | Calendar/public anomaly family | `DUPLICATE / CLOSED` |
| B21 | Momentum fading | Public reversal/price-pattern family | `DUPLICATE / CLOSED` |
| B22 | Sector rotation | Public cross-sectional/macro rotation family already tested | `DUPLICATE / CLOSED` |
| B23 | Microcap value factor | Public cross-sectional value factor; changing the universe does not establish a new mechanism | `DUPLICATE / CLOSED` |
| B24 | Microcap momentum factor | Public cross-sectional momentum family | `DUPLICATE / CLOSED` |
| B25 | Forex carry spread | Carry/relative-value family; no specific small-trader mechanism | `DUPLICATE / CLOSED` |
| B26 | Commodity basis/backwardation | Public term-structure/carry factor; no specialist small-trader advantage | `DUPLICATE / CLOSED` |
| B27 | EDGAR filing drift | PEAD, EDGAR, buyback, and filing-timing families already closed | `DUPLICATE / CLOSED` |
| B28 | Exchange-change pressure | Index/operational flow family; exchange change does not prove forced buying | `DUPLICATE / CLOSED` |
| B29 | Retail-sector sentiment | Social/public sentiment and short-horizon reversal family | `DUPLICATE / CLOSED` |
| B30 | Liquidity-corridor unwind | Microcap price/volume pattern and manipulation-risk family; no lawful causal mechanism | `DUPLICATE / CLOSED` |

## Surviving candidates

Only two candidates are sufficiently distinct to deserve a separate feasibility document:

### B15 — Spin-offs

The candidate is not “spin-offs outperform.” The mechanism requiring investigation is:

> A parent distributes a new security to shareholders; some recipients are constrained, indifferent, or economically unwilling to hold it; predictable supply reaches the market; natural buyers are slower or less willing to absorb it; the resulting dislocation persists long enough for a small trader to acquire the security and benefit from normalization.

Before any backtest, we must verify:

- who receives the shares and which holders may be forced or incentivized to sell;
- whether institutional mandates, index rules, or custody restrictions create predictable supply;
- whether the distribution and first tradable timestamps are reconstructible point-in-time;
- whether a retail trader can enter after distribution without paying away the effect;
- whether there are enough independent spin-offs for IS/OOS testing;
- whether the historical effect is still present after realistic spread, impact, corporate-action handling, and benchmark costs.

**Current disposition:** `INTERESTING BUT UNVERIFIABLE`.

### B5 — Niche-ETF NAV dislocation

The candidate is not “ETF prices revert.” The mechanism requiring investigation is:

> Authorized-participant creation/redemption arbitrage becomes impaired in a thin ETF or an ETF holding stale/infrequently traded assets, allowing the exchange price to deviate from executable underlying value.

Before any backtest, we must verify:

- an intraday NAV or executable basket-value reconstruction using free/owned data;
- the timestamp at which the deviation becomes observable;
- AP creation/redemption terms and whether they actually permit convergence;
- whether the ETF price deviation is distinct from stale underlying marks or ordinary spread;
- complete costs, including ETF spread, basket spread, creation/redemption fees, financing, and tracking error;
- enough independent deviations for an untouched OOS test.

**Current disposition:** `INTERESTING BUT UNVERIFIABLE`.

## Why no candidate is eligible for a backtest

An eligible candidate must pass every gate below before historical returns are inspected:

| Gate | Requirement | Current result |
|---|---|---|
| Distinct mechanism | Not a rebranding of a closed family | Only B5 and B15 pass provisionally |
| Participant | Defined constrained participant | B5/B15 require further source work |
| Observable | Timestamped before entry | B5 currently unresolved; B15 needs reconstruction audit |
| Persistence | Explicit reason arbitrage is delayed | Plausible but not established |
| Counterparty | Identifiable natural counterparty | Not established |
| Small-trader advantage | Size/flexibility specifically helps | Plausible but not demonstrated |
| Execution | IBKR-accessible with realistic orders | Instrument access likely, event execution unresolved |
| Friction | Complete cost model | Not frozen |
| Capacity | Survives intended position size | Not established |
| Sample | Enough independent events for IS/OOS | Not established |
| Falsification | Frozen kill criteria | Not yet preregistered |

Therefore, no backtest is authorized by the deep-research report.

## Decision

The deep-research report does not overturn the five-lane audit and does not justify five tests. It narrows the next possible research step to a separate feasibility audit of B15 and B5.

The order of work is:

```text
30 candidates
→ reconciliation against closed project record
→ 28 closed or unresolved alternatives removed
→ feasibility audit for B15 and B5
→ zero, one, or two candidates pass
→ preregister only the survivors
→ run at most one frozen test per approved mechanism
```

No data purchase, backtest, parameter search, or strategy implementation is authorized by this document. If both B15 and B5 fail feasibility, the deep-research branch terminates under the current capability set.

## Source record

- [Deep Research report](deep-research-report.md)
- [Consolidated five-lane mechanism audit](mechanism-first-edge-audit.md)
- [Project record](../docs/PROJECT_RECORD.md)
- [A1 forced-flow and settlement audit](forced-flow-settlement-phase-a-audit.md)
- [A2 capacity-constrained securities audit](capacity-constrained-securities-phase-a-audit.md)
- [A3 specialist-information audit](specialist-information-phase-a-audit.md)
- [A4 fragmented/operational audit](fragmented-operational-phase-a-audit.md)
