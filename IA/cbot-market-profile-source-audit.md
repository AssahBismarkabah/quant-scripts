# CBOT Six-Part Market Profile Study Guide: Full Source Audit

**Source:** *A Six-Part Study Guide to Market Profile*, Chicago Board of Trade, 1996 edition; 346 PDF pages, printed pp. 1-335.  
**Audit date:** 2026-09-01  
**Purpose:** Determine whether the guide supplies a specified, evidence-backed ES/MES strategy, or materially changes the pre-registered [ES Previous-Day Value-Area Opening-State Study](es-value-area-opening-state-research-spec.md).

## Conclusion

The guide supports the **research question**, not a deployable strategy: use prior value and developing activity to judge whether the market is returning to old value or establishing new value. It does not provide a mechanically specified entry/exit system, a performance sample, a win rate, an ES/MES study, or a backtest.

The ES study remains aligned and can proceed as one reduced, falsifiable implementation. No rule should be added from this guide. The guide makes the study's limitations clearer:

1. Its real method combines price/time profile information with LDB volume and CBOT participant categories. We lack that data.
2. It treats context and judgment as necessary, not optional.
3. It says initial-balance duration is market-specific; our first-hour state is a frozen operational convention, not a CBOT-proven ES parameter.
4. It increasingly treats the 24-hour distribution, rather than one exchange session, as the natural analytical unit. Our previous-RTH profile is a bounded proxy.

## What was reviewed

The complete guide was extracted and read by its six stated parts, including the introduction, all part conclusions, glossary, and final disclaimer.

| Part | Subject | Relevant finding | Effect on ES study |
| --- | --- | --- | --- |
| I, printed pp. 1-45 | Single-session Profile, auction, balance/imbalance, initial balance, responsive/initiating activity | Defines the vocabulary and describes range extension/failure qualitatively. It says initial balance must be determined for each market; historical examples differ by product and session length. | Supports testing an opening-state proxy once. Does not validate the 60-minute ES choice or wick thresholds. |
| II, pp. 46-86 | Long-term auction chart | Uses daily value movement and classifies activity as initiating or responsive. Describes failed range extension as no follow-through, while warning that the distinction can require judgment. | Our mechanical rejection/retest tests only a simplified slice; no new rule is safely extractable. |
| III, pp. 87-122 | Perception of value | The guide's directional explanations rely on participants' changing perception of value, not a static level alone. | Confirms that VAH/VAL/POC alone are insufficient evidence of direction. |
| IV, pp. 123-188 | Distribution process and global capital | Moves from a session-centered model toward evolving distributions across time; treats a session boundary as an analytical simplification in global markets. | Confirms that prior-RTH anchoring is a research convention, not a natural market boundary. |
| V, pp. 189-266 | Market activity at work | Identifies reference points, then asks how the market behaves there. Its examples require surrounding distribution, location in a larger move, activity, and follow-through. | Supports conditional testing rather than unconditional level touches. It does not specify objective ES entry, stop, or target rules. |
| VI, pp. 267-335 | Liquidity Data Bank volume analysis | Adds actual volume-at-price and CBOT Customer Trade Indicator categories. Says volume alone is meaningless and that continuation/reversal still requires subjective judgment. | Material capability gap: one-minute OHLCV cannot reproduce LDB or participant-category analysis. |

## Exact source boundaries

The following are concepts the guide actually provides:

* The 70% range/value area is constructed from the highest-volume price and expanded outward until about 70% of session volume is included (printed pp. 50-51).
* Above, below, and within value are descriptive states, associated with initiating and responsive activity in its framework (Part I/II).
* An initial balance is the period during which two-sided trade establishes a range; the guide explicitly says the duration changes by market and changing session structure (printed p. 8).
* A failed range extension is described as an attempted extension without follow-through. The text calls its visual forms general guidelines and says judgment is needed to distinguish it from other uncertainty (printed pp. 53-57).
* The central practical problem is whether price returns to an old value area or continues to a new value area (printed p. 334).

The guide does **not** provide:

* ES or MES data, sample period, transactions, trade log, expectancy, profit factor, drawdown, or an out-of-sample result.
* A 67% POC-return statistic, an 80% rule usable as a tested ES entry, or any universal probability.
* A 40% wick rule, one-point retest tolerance, fixed 2- or 2.5-point stop, fixed 10-/20-point target, or a claim that these are optimal.
* A rule that the first hour is correct for ES.
* A proof that profile levels represent institutional inventory or will be defended.

## The LDB capability gap

Part VI is not just a minor addition. The guide calls the Liquidity Data Bank the second part of Market Profile data. It uses actual volume at price and separates local-floor-trader, commercial-clearing-member, and residual outside-customer participation. It uses that information to interpret whether price movement is effectively facilitating trade.

Our owned ES one-minute cache has OHLCV bars only. It cannot identify trade volume at each price, aggressive buyer/seller direction, or participant category. Even its profile is a bar-close allocation proxy. Therefore:

* We cannot claim to be testing the full CBOT/LDB method.
* We should not infer trader intent or institutional participation from our proxy profile.
* A pass on the ES study would justify trade-level volume-at-price replication, not a claim that the book has been proven.

## Decision for the ES study

Proceed exactly as pre-registered in [the ES study](es-value-area-opening-state-research-spec.md): fixed prior-RTH proxy profile, first-hour state, later confirmation, stated costs, and strict combined OOS gates.

Do not add a new filter, alter the initial-balance duration, or choose rules from the guide after outcomes are known. If the frozen test fails, this source audit is not a reason to rescue it with judgment; it only defines what a distinct future study would need: prospectively labelled context and, preferably, trade-level volume-at-price/participant data.

## Source and use notice

The guide itself says it is educational material, not a trading recommendation. This audit uses it as a source of definitions and qualitative hypotheses only.

