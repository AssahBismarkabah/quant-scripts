# Mechanism-First Edge Audit

**Date:** 2026-09-06  
**Status:** PHASE A4 EXECUTED — `NO VIABLE MECHANISM FOUND` (2026-09-08)  
**Scope:** One bounded research cycle after the completed free-data strategy search

## 1. Why this document exists

The project has repeatedly followed this loop:

```text
public data -> indicator or pattern -> backtest -> costs -> OOS -> failure
```

The harness is validated by the positive control, and the tested free-data strategy surface has produced no surviving deployable edge. The latest ES/Market Profile test is another example: the data-quality gate passed, but the defined construction was negative in-sample and out-of-sample.

The next question must therefore change from:

> Which strategy should we test next?

to:

> What economic constraint could cause a participant to trade at a price that another participant can systematically exploit?

This document records that change. It is a mechanism-audit plan, not a claim that such a mechanism exists.

The authorized cycles are recorded in [Phase A1: Forced-Flow and Settlement Mechanism Audit](forced-flow-settlement-phase-a-audit.md), [Phase A2: Capacity-Constrained Securities Mechanism Audit](capacity-constrained-securities-phase-a-audit.md), [Phase A3: Specialist Information Mechanism Audit](specialist-information-phase-a-audit.md), and [Phase A4: Fragmented and Operational Markets Mechanism Audit](fragmented-operational-phase-a-audit.md). A1 investigated 12 candidates, A2 15, A3 12, and A4 12 against primary sources and the six gates; none advanced to Phase B. No historical return search or data purchase was authorized. A5 requires a separate explicit project amendment.

## 2. What the other-agent proposal gets right

The proposal is accurate in four important ways:

1. A statistical relationship is not an explanation for an edge. We need a reason the relationship could persist after discovery and costs.
2. The strongest candidate is a constrained participant: someone who must trade, cannot optimize timing or price fully, or faces a rule that creates predictable demand or supply.
3. Small size can be an advantage only where the opportunity is too small, fragmented, operationally difficult, or capacity-limited for large institutions to pursue.
4. The mechanism must be specified before historical returns are inspected. Otherwise the process becomes another form of strategy mining.

The proposal is incomplete if read as permission to keep opening new markets indefinitely. Our turning-point record already imposed a one-shot rule on capacity-constrained arenas: one pre-registered probe, then return to stop if the result is dead or unverifiable. Any new cycle must explicitly amend that rule before work begins.

## 3. The mechanism standard

Before code or historical P&L, a candidate must answer all of these questions:

| Question | Required answer |
| --- | --- |
| Who trades? | A defined participant class, not “the market” |
| Why must they trade? | A mandate, settlement rule, hedge, rebalance, liquidation, inventory constraint, or other externally imposed reason |
| What prevents immediate arbitrage? | Capacity, timing, information, fragmentation, liquidity, operational, or mandate constraint |
| What is the observable? | A timestamped input available before the proposed trade |
| What pressure should it create? | Direction, price area, horizon, and expected decay of the distortion |
| Who is the counterparty? | The participant supplying liquidity and why they accept the price |
| What is our advantage? | Size, speed, access, specialization, patience, or a data/execution capability we actually possess |
| What is the friction? | Spread, slippage, impact, fees, borrow, financing, rejects, and operational loss |
| When does the edge disappear? | A defined exit/expiry/event, not “when it feels done” |
| How much capacity exists? | A conservative capital or liquidity cap before impact removes the return |

If any row is unanswered, the candidate is a mechanism hypothesis only and cannot enter the backtest queue.

## 3A. What this cycle is trying to discover

The cycle is not searching directly for a profitable strategy. It is searching for one economically credible mechanism that could plausibly produce a profitable strategy at retail scale.

The output of Phase A/B is therefore one of:

* **NO VIABLE MECHANISM FOUND** — stop the systematic search.
* **ONE MECHANISM APPROVED FOR A SINGLE TEST** — write one separate pre-registered trading specification.
* **UNVERIFIABLE** — the proposed constraint or observable cannot be established with reliable historical/prospective data.

A mechanism that passes the audit has not demonstrated profitability. It has earned only the right to be tested once. It may not generate a parameter grid, multiple asset variants, or discretionary exceptions.

## 4. Candidate mechanism families

This is a shortlist for source and mechanism research, not a list of strategies to test blindly.

A family is not itself a candidate. It can only generate specific candidate mechanisms. “Microcaps,” “specialist information,” and “fragmented markets” are market characteristics or research areas, not hypotheses.

| Family | Why it could create distortion | First verification question | Current status |
| --- | --- | --- | --- |
| Forced institutional flow | A mandate or index/portfolio rule creates price-insensitive demand or supply | Can the obligation and timing be observed before the flow, and is the flow large relative to available liquidity? | Previously tested variants; only a genuinely different mechanism may reopen |
| Settlement or contract mechanics | Expiry, fixing, collateral, or settlement rules force synchronized transactions | Is the rule mechanically binding, and can execution occur before other participants hedge it away? | Candidate family, not approved |
| Capacity-constrained securities | Low institutional participation may permit slower price discovery | Can “neglect” be measured without survivorship bias, and can fills be modeled at executable prices? | One possible next arena, but must be long-only unless borrow is verified |
| Specialist information | Local or domain-specific information may reach prices slowly | Can the information be sourced prospectively and timestamped without relying on hindsight? | High risk of repeating the sparse EDGAR failure |
| Fragmented/operational markets | Small venues or instruments may have avoidable coordination or settlement frictions | Is the opportunity legal, executable, and large enough after withdrawal, spread, and failure risk? | Requires separate operational audit |

The following are not mechanisms by themselves: momentum, RSI, candlestick patterns, “institutional levels,” wide spreads, low coverage, a high backtest Sharpe, or a chart pattern.

A valid formulation must look like: “Participant X is constrained by rule Y; observable Z reveals the constraint at time T; the constraint should create pressure D over horizon H; counterparty Q absorbs it for reason R; and we can execute at retail scale under cost model C.”

## 5. One-cycle workflow

The cycle has a hard cap of one mechanism shortlist and one selected hypothesis.

### Phase A — Source and mechanism audit

For each candidate, record primary evidence for the participant constraint, the rule creating it, and the expected timing. Reject candidates supported only by trading education, influencer claims, correlations, or post-hoc charts.

### Phase B — Observability and execution audit

Before return data, verify that the observable exists historically and prospectively, that its timestamps are usable, and that the proposed trade can be executed with a conservative friction model. If the observable cannot be reconstructed, verdict is **UNVERIFIABLE**.

### Phase C — Pre-register one hypothesis

The selected candidate receives a separate research spec containing:

```text
MECHANISM: participant X is constrained by Y.
OBSERVABLE: Y is measured by data Z at time T.
EXPECTED EFFECT: distortion D should occur over horizon H.
COUNTERPARTY: participant Q supplies the other side for reason R.
EXECUTION: entry, exit, sizing, and all costs are defined before results.
CAPACITY: the strategy stops scaling at conservative cap C.
FALSIFICATION: exact IS/OOS, robustness, and data gates.
```

### Phase D — Backtest only after approval of the spec

Use the existing harness discipline: causal timestamps, untouched OOS, realistic costs, benchmark comparison, bootstrap or equivalent robustness, and a terminal verdict of **CERTIFIED**, **DEAD**, or **UNVERIFIABLE**.

The decision flow is:

```text
credible constraint?
  no  -> NO VIABLE MECHANISM FOUND / stop
  yes -> observable before trade?
           no  -> UNVERIFIABLE
           yes -> executable at retail scale?
                    no  -> UNVERIFIABLE
                    yes -> authorize one pre-registered test
```

If the test is authorized, its result is still only **CERTIFIED**, **DEAD**, or **UNVERIFIABLE**. **CERTIFIED** means the frozen trading test cleared its gates; it does not mean guaranteed profitability or permission to scale without paper/live validation.

## 6. Hard exclusion rules

Do not proceed with a candidate if:

* the mechanism is merely “price tends to rise/fall after X”;
* the alleged forced flow is not independently observable;
* the result depends on assumed fills in a wide or thin market;
* the candidate requires shorting without verified borrow and borrow-cost data;
* the edge is simply a previously closed family with a new name;
* a parameter grid is needed to discover the hypothesis;
* the only evidence is an in-sample return or a visual chart example;
* the required capability is unavailable but the missing capability is being hand-waved;
* the candidate cannot reach the minimum sample size without loosening the definition.

Wide spreads are friction, not evidence of an edge. Low coverage is a possible reason for slower discovery, not proof that prices are wrong.

## 7. Decision gates for the mechanism audit

The mechanism cycle itself passes only if one candidate has:

1. A documented participant constraint from a credible primary source.
2. A measurable observable available before the proposed trade.
3. A plausible explanation for why the distortion is not immediately arbitraged.
4. A counterparty and execution path that exist at our scale.
5. A conservative friction and capacity model that can be implemented with available data.
6. A forecast of sufficient event frequency for a meaningful OOS test.

If no candidate passes all six gates within an explicitly authorized family cycle, that family cycle returns **NO VIABLE MECHANISM FOUND**. A later family requires a separate explicit project amendment. A candidate that reaches the gates is not an edge; it earns only one pre-registered test.

## 8. Relationship to the existing project record

This document does not reopen the failed ES value-area strategy, NQ IVAMR, prediction markets, sports betting, ORB, VWAP, PEAD, short-vol, liquidity provision, or other closed families. It also does not override the terminal capacity-constrained-arena rule. It defines the evidence required if the user deliberately chooses to amend that rule for one new mechanism audit.

The two valid decisions from here are therefore:

* **Stop systematic edge discovery** and redirect effort to income or a different business.
* **Explicitly authorize a separately scoped mechanism-audit cycle**, with a fixed time budget and no automatic right to open another cycle after a dead or unverifiable result.

Neither choice implies that the user lacks skill. They are business decisions about whether the expected value of one more bounded investigation justifies its time and possible data/infrastructure cost.

## 9. Consolidated five-lane result

This section is the canonical summary of the five-part search. The first lane is the broad public-data and retail-strategy program already recorded in the project history. The remaining four lanes are the mechanism-first audits A1-A4.

| Lane | What was investigated | What the record showed | Status | Terminal decision |
|---|---|---|---|---|
| 1. Public data and ordinary retail strategies | Public price/volume signals, cross-sectional equity signals, PEAD, VWAP/Market Profile, ORB/gap, IVAMR, options/VRP, order flow, liquidity provision, funding/basis, prediction markets, sports, and related strategy families | The validated harness reproduced positive controls, but the tested public-data strategies failed OOS, costs, robustness, sample, or execution gates. The remaining liquid-market edges require capabilities we do not have: L2/queue priority, speed, proprietary information, or more capital. | **EXHAUSTED / CLOSED** | No additional public-data strategy search is authorized. |
| 2. A1 — Forced-flow and settlement | 12 concrete mechanisms: SOQ settlement, TMAC, ETF AP creation/redemption, Treasury auctions/buybacks, delivery constraints, OCC settlement, and corporate-action processing | Official rules proved that settlement and participation constraints exist, but no candidate supplied observable direction, identifiable counterparty, retail execution advantage, and sufficient events after friction. | **COMPLETE — NO VIABLE MECHANISM FOUND** | No Phase B or C test authorized. |
| 3. A2 — Capacity-constrained securities | 15 concrete mechanisms: fund liquidity limits, index eligibility, listing requirements, OTC quotation obligations, Regulation SHO, threshold fails, IPO lockups, PIPE unlocks, corporate actions, small-cap options, and ETF AP capacity | Institutional size and liquidity constraints were real, but they did not produce a timestamped directional signal with lawful access, executable economics, and sufficient independent events. | **COMPLETE — NO VIABLE MECHANISM FOUND** | No Phase B or C test authorized. |
| 4. A3 — Specialist information | 12 concrete mechanisms: BVMAC/BEAC local information, broker/client flow, SVT allocation data, procurement, commodity supply chain, port/inventory data, payment flows, exchange-member notices, and local networks | BVMAC and BEAC information is public, not exclusive. Private broker, SVT, operational, and network information was not available through a verified lawful access path. | **COMPLETE — NO VIABLE MECHANISM FOUND** | No Phase B or C test authorized. |
| 5. A4 — Fragmented and operational markets | 12 concrete mechanisms: BVMAC routing/fixing, CEMAC Treasury access, CEX-to-CEX, fiat/stablecoin ramps, CEX/DEX, DEX pools, cross-chain bridges, funding/basis, and operational halts | Real operational frictions exist, but no candidate had simultaneous executable access, reliable transfer and settlement, identifiable persistence, complete cost modeling, and sufficient capacity. | **COMPLETE — NO VIABLE MECHANISM FOUND** | No Phase B or C test authorized. |

### Consolidated conclusion

Across all five lanes, nothing passed the complete chain:

```text
economic or operational reason
→ observable before entry
→ identifiable counterparty
→ lawful and executable access
→ survives spread, slippage, fees, transfer, custody, and impact
→ sufficient independent events
```

The result is not “profitable trading is mathematically impossible.” The result is narrower and evidence-based: under the current capability set—public/free data, retail execution, IBKR access, no exclusive information, no verified private flow, no queue-priority infrastructure, and no new venue/custody capability—there is no defensible next trading test.

Detailed candidate registries and source evidence remain linked in the A1-A4 audit documents above. This section records their combined status without replacing those detailed records.
