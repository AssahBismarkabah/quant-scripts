# Phase A4: Fragmented and Operational Markets Mechanism Audit

**Status:** COMPLETE — `NO VIABLE MECHANISM FOUND`

**Authorization:** Explicit final bounded mechanism cycle after A1, A2, and A3.

**Run boundary:** 2026-09-08; 12 concrete mechanisms investigated; no paid data, new account, backtest, historical P&L, parameter search, or strategy implementation.

## Scope and governance amendment

Phase A4 covered venue fragmentation, settlement, custody, transfer, withdrawal, and operational coordination. It did not reopen forced-flow/settlement, capacity-constrained securities, specialist information, funding basis, passive liquidity provision, prediction markets, sports, or any other closed family.

The project record now states:

1. A1, A2, and A3 are complete with `NO VIABLE MECHANISM FOUND`.
2. A4 was explicitly authorized as the next bounded cycle.
3. A4 does not reopen A1-A3.
4. Any A5 requires a separate explicit project amendment.
5. If A4 fails or is unverifiable, the systematic mechanism search terminates unless a materially new capability appears.

## Terminal result

`NO VIABLE MECHANISM FOUND`.

The audit found genuine operational differences: BVMAC broker-mediated fixing, CEMAC Treasury primary-market access restrictions, AMM fees and price impact, and exchange/chain transfer constraints. None produced the complete chain required for one executable retail mechanism:

`simultaneous observable discrepancy → funded access to both sides → reliable transfer/settlement → identifiable counterparty → net positive economics after every cost and failure mode`.

Displayed price differences, wide spreads, or theoretical arbitrage are not evidence of an executable opportunity.

## Gate notation

- **G1 Mechanism evidence:** primary documentation proves the operational or venue rule.
- **G2 Observable/executable state:** both sides and the discrepancy can be observed and executed before entry.
- **G3 Transfer/settlement:** assets, cash, collateral, and proceeds can move through the required route.
- **G4 Counterparty/persistence:** the counterparty and reason for persistence are identifiable.
- **G5 Complete friction:** fees, spreads, slippage, gas, funding, withdrawal, transfer time, limits, taxes, failures, custody, and downtime are modeled.
- **G6 Capacity/events:** sufficient independent executable events and size exist without loosening the definition.

## Candidate dispositions

The complete registry is [phase_a_candidate_registry.md](../research/fragmented-operational/phase_a_candidate_registry.md).

| ID | Mechanism | Disposition |
|---|---|---|
| FO-01 | BVMAC broker-to-broker routing or fixing discrepancy | `UNVERIFIABLE — DATA OR EXECUTION` |
| FO-02 | BVMAC displayed demand/supply versus executable fill | `REJECTED — NO MECHANISM` |
| FO-03 | BVMAC secondary-market settlement/custody mismatch | `REJECTED — TRANSFER/CUSTODY` |
| FO-04 | CEMAC Treasury primary-versus-secondary access | `CLOSED FAMILY OVERLAP` |
| FO-05 | CEMAC Treasury dealer quote obligations | `UNVERIFIABLE — DATA OR EXECUTION` |
| FO-06 | CEX-to-CEX spot transfer arbitrage | `UNVERIFIABLE — DATA OR EXECUTION` |
| FO-07 | Stablecoin/fiat on-ramp or off-ramp spread | `UNVERIFIABLE — DATA OR EXECUTION` |
| FO-08 | CEX-to-DEX spot discrepancy | `UNVERIFIABLE — DATA OR EXECUTION` |
| FO-09 | DEX pool price discrepancy and atomic routing | `CLOSED FAMILY OVERLAP` |
| FO-10 | Cross-chain bridge or settlement latency | `REJECTED — TRANSFER/CUSTODY` |
| FO-11 | Perpetual-futures funding or venue basis transfer | `CLOSED FAMILY OVERLAP` |
| FO-12 | Exchange outage, withdrawal halt, or operational break | `REJECTED — NO MECHANISM` |

## Primary-source findings

- BVMAC is broker-mediated, uses a fixing structure, and publishes official market information. Its existing feasibility audit found no verified direct machine-execution route and documented weak liquidity and significant broker costs. This is an execution/access problem, not an arbitrage mechanism. [BVMAC access](https://www.bvm-ac.org/espace-investisseurs-fr/investisseurs-acces-aux-produits-boursiers/), [BVMAC rules](https://www.bvm-ac.org/wp-content/uploads/2019/11/Reglement-BVMAC.pdf), [existing feasibility audit](bvmac-cemac-feasibility.md)
- BEAC states that the CEMAC Treasury primary market is reserved for Specialists in Treasury Securities, while the secondary market uses dealer quotes. We do not possess SVT access or a verified cross-market execution route. [BEAC market structure](https://www.beac.int/m-des-titres-publics/presentation-generale/)
- Uniswap’s official documentation confirms that swaps incur pool fees and price impact, and that execution depends on gas, slippage tolerance, pool liquidity, and transaction ordering. This proves operational costs and risk; it does not establish a persistent arbitrage after costs. [Uniswap fees](https://developers.uniswap.org/docs/get-started/concepts/fees), [Uniswap swaps](https://developers.uniswap.org/docs/get-started/concepts/traders/swaps)

## Phase B/C decision

No candidate passed all six gates. No candidate is approved for Phase B, and no Phase C trading test is authorized.

The systematic mechanism search is now terminal under the current capability set. A future A5 requires a new capability or materially new access condition, not another scan of the same venues.

