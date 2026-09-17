# B15 Spin-Off Feasibility Audit

**Date:** 2026-09-17  
**Status:** S04 SUBTYPE CLOSED — NO TRADING TEST AUTHORIZED

## Decision being investigated

The candidate is not “spin-offs outperform.” It is the narrower mechanism that a parent distributes a new security, some recipients may be unable or unwilling to hold it, and that supply may temporarily exceed natural demand after the security becomes tradable.

This is an observability and execution audit. It does not inspect returns, charts, P&L, or parameters.

## What primary sources establish

- SEC Form 10 materials establish that a spin-off can distribute shares pro rata to parent shareholders and that the new issuer becomes an independent reporting company. A recent Form 10 example also specifies record date, distribution date, book-entry delivery, and treatment of fractional shares. [SEC Form 10 example](https://www.sec.gov/Archives/edgar/data/2064953/000206495325000006/exhibit991-form10.htm)
- DTCC corporate-action documentation establishes that spin-offs have formal announcement, ex-date, record/payable, settlement, and distributed-security fields. [DTCC corporate-action testing](https://www.dtcc.com/ust1/-/media/Files/PDFs/T2/T1-Corporate-Actions-Testing.pdf)
- DTCC explains that settlement conventions determine entitlement processing around ex-dates and spin-offs. [DTCC T+1 functional changes](https://www.dtcc.com/-/media/Files/PDFs/T2/T1-Functional-Changes.pdf)

These sources establish the event mechanics. They do not establish forced selling, a predictable price direction, a delayed-arbitrage effect, or profitability.

## Gate assessment

| Gate | Required evidence | Current disposition |
|---|---|---|
| Distinct mechanism | Materially distinct from closed index-flow and ordinary corporate-action work | **Provisional pass**; must remain ownership/supply-specific |
| Participant constraint | Primary evidence that a defined recipient must or predictably will sell | **Fail pending evidence** |
| Pre-trade observability | Point-in-time event, entitlement, and first-tradable timestamps | **Unverified** |
| Non-immediacy | Specific reason supply is not instantly absorbed | **Unverified** |
| Counterparty/execution | Identifiable buyer and IBKR-executable entry/unwind | **Unverified** |
| Friction/capacity | Spread, impact, fees, corporate-action handling, and size ceiling | **Unverified** |
| Sample sufficiency | Enough independent events for frozen IS/OOS test | **Unverified** |

## Required feasibility work

1. Build a source-only event inventory from SEC Form 10/10-12B, 8-K, issuer information statements, exchange notices, and DTCC records.
2. For each event, record filing time, effectiveness, record date, distribution date, ex-date, first trading date, ratio, fractional-share treatment, listing venue, and ticker/CUSIP changes.
3. Search the primary documents for an actual recipient constraint: mandate, index eligibility rule, custody restriction, tax/settlement restriction, or documented distribution policy. Receipt alone is not a constraint.
4. Verify whether the resulting security and historical prices are reconstructible without survivorship or adjusted-price leakage.
5. Freeze a long-only test specification only if every gate passes. Otherwise record `UNVERIFIABLE` or `REJECTED — NO MECHANISM`.

## Current terminal result

`S04: NO VIABLE MODERN EXECUTABLE EVENT FOUND; broader B15 spin-off family not proven impossible`

## Initial census finding (2026-09-17)

A pilot EDGAR full-text census for 2025 Q1 returned the search cap of 100 hits in each month. The rows included many filings whose descriptions did not identify a spin-off, and the index response did not reliably populate an acceptance timestamp. Therefore the search output is a discovery queue only; it is not evidence of 220 spin-offs and cannot be used for event counts or returns. The next implementation step must retrieve and classify the underlying primary documents, then independently record transaction dates and timestamps.

The primary-document classifier completed on the 220-row pilot queue: 124 were unrelated or unconfirmed, 71 were spin-off mentions requiring review, and 25 were likely spin-off documents requiring review. Several rows repeat the same transaction through amendments or parent/spinco filings, so these are filings rather than independent events. Transaction-level deduplication is required before the sample-sufficiency gate.

The initial transaction registry is recorded in [`research/spin-offs/phase_b_candidate_registry.md`](../research/spin-offs/phase_b_candidate_registry.md). Three confirmed examples are currently recorded, and all remain `UNVERIFIABLE` because the reviewed sources establish event mechanics but not a defined recipient selling constraint or a complete prospective execution record.

The full primary-document extraction pass covered all 25 likely rows from the pilot and produced [`research/spin-offs/outputs/primary_evidence_review.csv`](../research/spin-offs/outputs/primary_evidence_review.csv). The rows still require transaction-level human review; repeated parent/spinco filings and planned/non-spin-off mentions remain mixed. No reviewed row supplied explicit evidence of a recipient being required to sell.

This document authorizes only the feasibility/data-census work above. It does not authorize a backtest, data purchase, new account, or live trade.
