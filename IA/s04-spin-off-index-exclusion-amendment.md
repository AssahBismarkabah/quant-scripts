# S04 Amendment: Spin-Off Index-Exclusion Feasibility Audit

**Date:** 2026-09-17  
**Status:** COMPLETE — NO VIABLE MODERN EXECUTABLE EVENT FOUND

## Scope

This amendment reopens one narrow subtype of B15 spin-offs: a parent distributes a new security, a defined tracked index excludes that security, and the index methodology requires or directs a tracking fund to dispose of it at a specified time.

This does not reopen the general index-rebalancing family, ordinary spin-off drift, PEAD, corporate-action drift, or discretionary shareholder selling.

## Why this is distinct enough to investigate

The existing index-rebalancing test examined broad scheduled constituent changes. S04 instead requires a corporate-action-specific chain:

`pro-rata distribution → index eligibility decision → defined fund disposal rule → known execution time`

The distinction is provisional and must be proven. The Abarbanell, Bushee, and Raedy study supports institutional preference-driven rebalancing after spin-offs but reports little general abnormal-price evidence, so the mechanism is not presumed profitable.

## Feasibility gates

| Gate | Requirement | Status |
|---|---|---|
| Corporate event | Genuine completed spin-off with primary documentation | Open |
| Index rule | Primary index methodology identifies treatment and exclusion | Open |
| Participant | A defined tracking fund is required or compelled to dispose | Open |
| Timestamp | Rule and disposal time are known before execution | Open |
| Execution | The security and relevant execution venue are accessible through IBKR | Open |
| Friction | Spread, impact, fees, auction access, and tracking error are modelable | Open |
| Sample | Modern independent events support an IS/OOS split | Open |
| Distinctness | The chain is materially different from the closed broad rebalancing test | Open |

## Stop rules

Stop as `CLOSED FAMILY OVERLAP` if the candidate reduces to ordinary index deletion or if no corporate-action-specific rule can be shown. Stop as `UNVERIFIABLE` if index membership, timing, access, or event coverage cannot be reconstructed. No historical return analysis is permitted until every gate passes.

## Required output

Create a separate frozen trading specification only if this audit passes all gates. That specification must use one fixed index methodology, a point-in-time event universe, causal entry timing, conservative closing execution, and an untouched OOS period.

## Research checkpoint (2026-09-17)

The official S&P policy confirms that an ineligible spin-off may be removed after at least one regular-way trading day, and that a tracking fund should be able to sell to match the index. [S&P spin-off policy](https://www.spglobal.com/spdji/en/documents/index-policies/20150205-spin-off-consultation.pdf) However, the modern confirmed SanDisk event was added to the S&P SmallCap 600 rather than excluded. [S&P SanDisk announcement](https://press.spglobal.com/2025-02-19-SanDisk-Set-to-Join-S-P-SmallCap-600)

No qualifying modern S04 event was verified in the bounded review. The policy is mechanism evidence, not an event sample or a return result.

## Terminal disposition

`NO VIABLE MODERN EXECUTABLE EVENT FOUND`

The review found policy support and historical evidence of institutional rebalancing, but no modern event with verified index exclusion, executable retail access, conservative friction economics, and sufficient independent observations. No backtest is authorized.

The search located a concrete near-match in S&P’s February 2021 announcement: TechnipFMC was removed ahead of its spin-off and Technip Energies was expected to trade as an OTC ADR. Because the child’s executable venue and friction are not established in our current scope, it is recorded as `REJECTED — EXECUTION/FRICTION`, not as a test candidate.
