# VWAP Book Source Audit — No Test Advanced

**Audit date:** 2026-08-21  
 (Trader Dale, 2024; 122 pages)  
**Decision:** **NO NEW TEST ADVANCED**

## What this audit decides

This is an audit of the book as a potential source of a *new, falsifiable* trading hypothesis. It does not decide that every possible anchored-VWAP strategy must lose. It decides the narrower and useful question: whether the source supplies a distinct, complete rule set that justifies another test in this project.

It does not. The source is educational and labels its examples hypothetical. It supplies illustrative charts and verbal heuristics, but no trade dataset, sample definition, fill model, parameter freeze, or out-of-sample evidence. Its embedded commercial links and product references are not part of this research process.

For a book-derived candidate to advance, it would need all of the following before code is written:

1. A rule that can be frozen without researcher-invented thresholds.
2. A distinct causal mechanism or observable, not a relabelling of a closed VWAP, volume-profile, opening-range, or order-flow family.
3. Reachable data and a realistic execution model.
4. Enough observations for a pre-registered out-of-sample decision.

No setup in the book clears all four.

## Claim-by-claim assessment

| Book setup | What the book actually fixes | Existing evidence / constraint | Decision |
|---|---|---|---|
| Daily, weekly, or yearly VWAP pullback | Price is above/below VWAP, then returns to it; the book also presents first-touch and optional confirmation variants (pp. 14–15, 76+). | This is the same broad intraday VWAP-pullback premise tested in [NQ VWAP-Pullback](../strategies/nq-vwap-pullback/NQ_VWAP_PULLBACK.md): the fully frozen version was net-negative in both IS and OOS, even before friction. The book is less specified, not a new mechanism. | Do not reopen. |
| Anchor at a swing point or start of a trend | The source explicitly leaves an “important” swing / trend start to chart judgment (pp. 24–31). | There is no reproducible event definition, no selection time, and no fixed exit. Defining pivots, size, and confirmation ourselves would create a new arbitrary parameterization of the already-tested VWAP-pullback family. | Not source-testable. |
| Anchor at major macro news | Use news that proves “game-changing” by causing a significant shift in sentiment; then trade the pullback (pp. 32–36). | The selection occurs after observing the reaction, which makes it hindsight-selected. The adjacent, fully frozen NFP/FOMC event test in [Probe #24](../research-specs/rule-of-four-probe24-spec.md) was terminally dead/unverifiable on its required sample gates. Different mechanics do not repair the missing pre-event selection rule or supply a new causal mechanism. | Not source-testable; no new test. |
| Anchor at a heavy-volume zone / use Volume Profile confluence | Identify a visually important high-volume rotation or barrier; combine it with VWAP and price action. | The zone, anchor point, and confluence are not formalized. The distinct, fully specified previous-day value-area construction in [IVAMR](../strategies/ivamr/IVAMR.md) was disconfirmed on NQ 1-minute data. | Not source-testable; adjacent family closed. |
| Anchor after a gap | Identify a “big” gap, anchor at the first bar after it, and trade a pullback (pp. 42–44). | “Big,” trade timing, stop, and exit are unspecified. This is an adjacent version of the closed opening-range/gap family, not a reason to choose fresh thresholds until one happens to work. | Not source-testable; no new test. |
| Anchor at earnings | Find an earnings release, anchor VWAP there, and trade pullbacks; the source allows daily or intraday charts (p. 45+). | Earnings are a genuinely distinct event label, but the actual rule is incomplete: no surprise definition, timestamp convention, gap/volume threshold, universe, entry, exit, or costs. [PEAD](../strategies/pead/PEAD.md) is adjacent rather than identical and failed OOS. Turning this sketch into code would be a *new researcher-designed hypothesis*, requiring point-in-time earnings data and a separate causal case—not a test of the book. | Do not advance from this source. |
| First VWAP-deviation rotation / trend trades | Trade bands when they appear “horizontal” (rotation) or “vertical” (trend), with pullbacks to a deviation (pp. 47–54). | No numerical band definition, slope window, regime threshold, stop, target, or trailing rule is fixed. The source itself says the visual classification is not foolproof. | Not source-testable. |
| Price-action / confluence confirmation | Prefer levels with strong reactions, repeated reactions, a break-and-return, or a confirmation candle. | “Strong,” “reaction,” and the rejection rule are left to visual judgment. This can be a human decision process, but it is not evidence of an edge until the acceptance/rejection policy is specified and audited over a sample. | Not source-testable. |
| Footprint, absorption, limit-order, or cumulative-delta confirmation | Look for large orders, absorption, or price/delta divergence near VWAP levels (pp. 82–86). | The source offers examples, not thresholds or execution rules. It also relies on footprint/order-flow tooling that is outside the current retail data/execution capability. The project’s reachable order-flow/quote-imbalance probes were dead; real liquidity provision remains conditional on L2/queue-priority infrastructure. | Capability-gated and rule-incomplete. |
| Stops, 1:1 targets, and trailing stop suggestions | Stops sit behind a reaction/swing/VWAP level; targets may use 1:1 risk/reward (pp. 98–110). | These are risk-management choices, not a signal. Their reference points are themselves discretionary, so they cannot turn an incomplete entry idea into a frozen edge. | Does not create a candidate. |

## Why no backtest was run

A backtest needs a rule written *before* looking at the result. Here, the missing choices are the hypothesis: what counts as a large gap, a significant swing, a horizontal band, meaningful absorption, an important earnings event, or a successful reaction. Choosing them after reading the book would test our choices, not the book’s strategy. Given the project record of 24 prior probes, that would be fresh degrees of freedom and p-hacking risk, not validation.

The book itself acknowledges this problem indirectly: it says a first-touch VWAP trade is unreliable and recommends adding confirmations. But it does not quantify which confirmations reject a valid setup, when they are observed, or how the resulting policy performs out of sample.

## The one idea worth separating, but not testing now

The earnings-anchored VWAP example is the only item with a potentially distinct event source. It should remain a **future capability-triggered hypothesis**, not a current test, unless all of this becomes available and is frozen *before* exploration:

- point-in-time earnings release timestamps and surprise data;
- liquid intraday equity trades with conservative spread/slippage assumptions;
- a pre-event selection rule (for example, a fixed surprise and gap criterion), exact anchor, entry, stop, exit, and maximum holding period;
- a causal rationale stronger than “VWAP is fair value,” identifying the forced or delayed counterparty flow; and
- a sufficiently large event census and untouched OOS period.

That would be a new research proposal with new data/capability, not evidence that this book already contains a deployable strategy.

## Conclusion

The book is useful as a vocabulary of discretionary chart references: anchored VWAP, event anchors, bands, volume-profile confluence, and order-flow confirmation. It does **not** overturn the capability audit or create a legitimate new strategy test. The correct action is to preserve the negative result: no test, no tuning, and no capital deployment based on these examples.

### Source locations reviewed

- Basic anchored-VWAP pullback and anchor list: book pp. 13–15.
- Swing/trend anchors: pp. 24–31.
- Macro, gap, and earnings anchors: pp. 32–46.
- Deviation-band setups: pp. 47–54.
- Entry confirmation and order-flow examples: pp. 76–86.
- Stop/target examples and basic setup: pp. 98–110.
