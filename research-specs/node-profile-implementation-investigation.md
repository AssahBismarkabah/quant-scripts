# Investigation — Faithful implementation of the four volume-profile swing setups

**Date:** 2026-08-25  
**Status:** Phase 1 investigation complete; implementation is intentionally not started  
**Related prototype:** `src/quant_scripts/node_profile/`  
**Related provisional spec:** `research-specs/node-profile-setups-spec.md`

## 1. Conclusion first

The four setups can be implemented as a two-stage system, but the existing prototype is not a faithful implementation of the screenshots.

The correct architecture is:

```text
market bars
  -> detect candidate structure and its start/end anchors
  -> build volume-at-price profile only inside that structure
  -> select POC/HVN/cluster
  -> wait for departure and return/retest
  -> classify reaction, failure, or reversal
  -> emit a candidate for human approval or a fully frozen backtest
```

The current prototype skips the first step. It chooses rolling windows such as 30 sessions, profiles that window, and calls the result a setup. That is why it can generate plausible-looking levels but does not reproduce the user's actual process of drawing a box, trend leg, or rejection event.

The right next implementation is therefore a **structure detector plus profile engine**, not another threshold adjustment to the current rolling-window detector.

## 2. What the screenshots establish

### S1 — Volume accumulation / distribution box

The trader first sees a sideways price channel or box. The profile is drawn from the left boundary of that box to the right boundary, before the expansion. The POC/HVN inside the box becomes the level. Price later returns to that level.

The anchor is structural, not a fixed number of bars:

```text
first confirmed box boundary -> last bar inside the box -> expansion -> return to HVN/POC
```

The same structure is used for a long accumulation interpretation or a short distribution interpretation. The direction is not determined by the profile alone; it comes from the subsequent departure and the trader's interpretation of which side is defending the level.

### S2 — Trend-leg cluster

The trader identifies a directional leg, draws the profile from the start of the leg to the end of that leg, and marks the highest-volume cluster. Price must leave the cluster and later return to it.

The end anchor is not “today” and not necessarily the highest high. It is the end of the completed leg before the retracement or next structural phase. A live detector must delay the anchor until the leg's end is confirmed; otherwise the historical profile will use future information.

### S3 — Rejection

The trader identifies a sharp move into an area followed by an aggressive reversal. The profile is drawn around the rejection structure, not merely around one large wick. The highest-volume area inside that event is marked, and a later return is traded in the direction of the rejection.

The screenshots therefore require three separate concepts:

1. approach/displacement into the level;
2. rejection and displacement away from it;
3. a later retest of the volume area.

“Wick > 1 ATR” is only a possible feature. It is not equivalent to the setup.

### S4 — Reversal after level failure

This is a state transition applied to an existing volume level, not a separate way to draw a profile:

```text
original level -> price returns -> level does not react -> price closes through
-> price returns from the opposite side -> reversal entry
```

The screenshot explicitly says a small reaction before failure does not count as a valid reversal; price must clearly pass through the level. Therefore the implementation needs acceptance-through-level and opposite-side-retest rules, not merely “stop was hit.”

## 3. Volume-profile calculation

### 3.1 Exact version required for fidelity

For a selected structural interval `[anchor_start, anchor_end]`, use lower-timeframe bars or trades:

1. choose a price-row resolution, ideally a whole number of ticks;
2. map each lower-timeframe bar/trade volume to the price rows it actually traded;
3. sum volume by price row;
4. POC is the row with maximum volume;
5. HVNs/clusters are contiguous or near-contiguous high-volume rows separated from surrounding rows by a measurable volume drop;
6. optionally compute VAH/VAL from a frozen value-area percentage.

TradingView's official documentation describes this same general model: profiles are calculated from lower-timeframe data, POC is the highest-volume row, and value area is commonly 70% of volume. Its documentation also states that row size is a material input. The implementation must therefore record the source timeframe, row size, price tick size, and allocation method as provenance. [TradingView volume-profile methodology](https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/)

### 3.2 Why the current daily approximation is not exact

The current `_profile_for_bars()` spreads each daily bar's volume evenly across every price bin between its low and high. This is an approximation. A daily bar with a low of 100, high of 110, and 10 million shares does not tell us how much traded at 100, 105, or 110.

Consequences:

- the POC can move because of the allocation assumption rather than actual traded volume;
- two profiles with identical daily OHLCV can have different true intraday profiles;
- a rejection profile cannot be reproduced faithfully from daily OHLCV alone;
- the screenshot's volume cluster may be based on intraday bars unavailable in the owned daily panel.

The daily version may remain as a coarse candidate prefilter, but it must not be presented as an exact reproduction or as the basis for a definitive backtest of the visual strategy.

## 4. Anchor detection design

The implementation needs an explicit anchor object:

```text
StructureAnchor {
    kind: BOX | TREND_LEG | REJECTION
    start_time
    end_time
    direction: UP | DOWN | NEUTRAL
    confirmation_time
    detection_features
    human_review: REQUIRED | ACCEPTED | REJECTED
}
```

### 4.1 Candidate box detector

A candidate box should be generated from confirmed swing pivots, not an arbitrary calendar window. Candidate conditions:

- upper and lower boundaries are derived from confirmed pivot highs/lows;
- the boundaries are within a volatility-scaled width;
- there are at least two touches or near-touches on each side;
- closes remain inside the boundaries except for a permitted tolerance;
- the box persists for a minimum number of bars;
- the eventual departure exceeds a frozen displacement threshold;
- the profile interval ends before the departure bar, not after it.

The detector should return several plausible boxes, not silently select one “correct” box. A human chart reader can see nested boxes; a deterministic algorithm should preserve that ambiguity and rank candidates by touch count, duration, width stability, and departure strength.

### 4.2 Candidate trend-leg detector

A candidate trend leg should use confirmed pivots and measure:

- direction of the leg;
- net displacement relative to ATR;
- directional efficiency (net move divided by total absolute movement);
- number and depth of countertrend pullbacks;
- leg start and end confirmation delay;
- whether the leg ends before a meaningful retracement.

The profile is frozen at the leg's confirmation time. A live implementation must not use the eventual final high/low until that high/low is knowable.

### 4.3 Candidate rejection detector

A candidate rejection event requires more than a wick:

- an approach into a local or previously established level;
- an excursion beyond or into that level;
- a large adverse displacement or range expansion;
- a close back through a meaningful fraction of the excursion;
- follow-through in the rejection direction;
- a profile interval covering the event from approach through rejection completion.

The minimum viable implementation should expose the raw features and let a review layer decide whether it is a genuine rejection. It should not reduce this to one ATR threshold.

## 5. Return and failure state machine

Every profile level should move through states:

```text
PROPOSED
  -> ESTABLISHED (profile and anchor confirmed)
  -> DEPARTED (price leaves node by frozen distance)
  -> RETESTED (price reaches node band from outside)
  -> REACTED (moves away in expected direction)
  -> FAILED (closes through and accepts beyond level)
  -> FLIPPED (returns from opposite side)
```

This state machine prevents the two degeneracies found in the prototype:

- repeatedly labeling price as “returning” to a profile that is recomputed around current price;
- treating a level as failed merely because one intrabar low/high touched it.

The exact definitions still need to be frozen:

- node band: POC row, HVN cluster, or full value-area subzone;
- departure distance: absolute ticks, ATR multiple, or percentage;
- retest: intrabar touch versus close inside the band;
- reaction: minimum move away and time allowed;
- acceptance beyond level: one close, multiple closes, or close plus follow-through.

These are implementation decisions, not facts derivable from the screenshots.

## 6. Data and capability gate

For exact screenshot fidelity, the minimum data contract is:

- instrument and exchange;
- chart timeframe used by the trader;
- lower-timeframe bars or trades covering every profiled interval;
- OHLCV plus timestamp, timezone, tick size, and session calendar;
- split/corporate-action adjustment for equities;
- a declared volume allocation method;
- enough history to form both in-sample and out-of-sample structural events.

The owned equity panel is daily OHLCV through 2021. It is sufficient for a rough structural prototype, but not for exact intraday volume-at-price profiles like those shown in the screenshots. The current repository has intraday caches for NQ/ES, but those are different instruments and cannot validate a stock/forex screenshot strategy.

Before implementation, the instrument and timeframe must be frozen. Otherwise “the strategy” could change materially between daily stocks, intraday stocks, futures, forex tick volume, or crypto volume.

## 7. Proposed implementation stages

### Stage A — specification and review, no trading claim

Implement data structures and visual diagnostics:

- `StructureAnchor` candidates for boxes, legs, and rejection events;
- exact anchor start/end/confirmation timestamps;
- profile calculation with selectable row size and volume source;
- plots that show the candles, anchors, profile, POC/HVN, departure, and return;
- human review fields and exported candidate files.

Success criterion: on the four supplied screenshot examples, the user can inspect the generated candidate and say whether the selected structure matches the intended box/leg/rejection.

### Stage B — semi-automated watchlist

Scan a chosen universe, rank candidates, and require human acceptance before any order. Store the accepted/rejected decision and reason. This is the appropriate first deployable product for a discretionary system.

### Stage C — frozen quantitative replay

Only after the candidate definitions match the user's visual decisions, freeze entry, stop, target, overlap/dedup, and reversal rules. Then run descriptive forward-return analysis and benchmark against buy-and-hold. Do not call it a validated edge unless it clears a pre-registered out-of-sample gate on appropriate data.

## 8. Decisions required before coding the faithful version

The following cannot be safely guessed from the screenshots:

1. instrument/universe;
2. chart timeframe and execution timeframe;
3. whether the profile is total volume or buy/sell/delta volume;
4. exact meaning of “the box” and “end of the trend” in ambiguous charts;
5. exact HVN/cluster selection rule;
6. exact definition of strong rejection;
7. exact retest and failure rules;
8. whether one profile can create multiple trades or expires after one retest;
9. stop, target, time stop, and reversal sizing;
10. whether human approval remains part of live execution.

These are not minor parameters. They define the strategy. Any implementation that fills them in silently would be implementing a new strategy rather than yours.

## 9. Phase 1 verdict

**Implementation is feasible, but the faithful version is semi-automated first.** The profile calculation is deterministic; structural anchor selection is a candidate-detection and human-review problem until the user's visual definitions are frozen. The daily panel is insufficient for exact screenshot-level volume profiles; intraday data for the actual traded instrument is required for fidelity.

The current rolling-window detector should remain labeled as a provisional mechanics demo. It should not be extended into a backtest until the anchor and data decisions above are resolved.
