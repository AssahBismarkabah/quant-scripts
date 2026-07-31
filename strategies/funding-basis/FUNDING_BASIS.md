# BTCUSDT Binance Funding Basis Carry

**Version:** 1.0
**Status:** Rejected Under Current Assumptions
**Classification:** Relative Value / Structural Funding Carry

## 1. Executive Summary

This document records the funding-basis candidate that was researched through the Binance BTCUSDT spot and USDⓈ-M perpetual workflow. The idea was simple: buy spot, short the perpetual, collect funding, and survive fees, spread, slippage, timing risk, and basis movement.

The pipeline was implemented and verified. The candidate did not survive validation under the current conservative execution model.

## 2. The Economic Edge

The supposed edge comes from structural funding flows in perpetual futures. In theory, when the perpetual trades rich to spot and funding is positive, a hedged long-spot / short-perp position can collect the funding transfer while remaining directionally neutral.

The real test is whether that funding survives:

- executable entry and exit spreads
- fees
- slippage around the funding timestamp
- basis movement during the holding window
- liquidation and margin risk

On the observed June and July BTCUSDT samples, the answer was no.

## 3. Research Scope

- Venue: Binance
- Instruments: BTCUSDT spot and BTCUSDT USDⓈ-M perpetual
- Direction: positive-funding carry only
- Execution model: conservative, pre-funding entry and post-funding exit
- Data mode: historical venue snapshots and candles

This record is intentionally narrow. It documents one candidate implementation, not the entire perpetual-funding concept.

## 4. What Was Tested

The research pipeline was built to:

- download Binance funding history
- download mark and spot history over a configurable time range
- replay the sampled window with a fixed funding event buffer
- apply conservative spread, fee, slippage, and liquidation assumptions
- classify rejected trades by reason
- sweep basis and net-edge thresholds
- compare multiple monthly windows and simple regime splits

The final study covered:

- June 1, 2026 to June 30, 2026
- July 1, 2026 to July 31, 2026

## 5. Result

The candidate failed under the current assumptions.

Observed results:

- Short initial window: mildly positive
- Wider July window: negative average net edge after costs
- June window: negative average net edge after costs

This means the apparent edge in the small sample did not generalize to the longer samples we tested.

## 6. Why It Failed

The rejection was not because the mechanics were undefined. The pipeline worked.

The main failure modes were:

- negative basis capture on many windows
- gross edge too small after costs on some windows
- average net edge turning negative on the longer samples

## 7. Verified Implementation

The following were implemented and tested:

- Binance live data ingestion
- historical dump and replay workflow
- funding, mark, and spot sampling
- per-trade diagnostics
- basis threshold sweep
- net-edge threshold sweep
- simple regime split across each sample

## 8. Decision

Rejected under the current conservative model.

This strategy record should be treated as a verified failed candidate, not as a deployable edge.

## 9. Next Step

Move to the next mechanic in `IA/structural-mechanics.md` or define a materially different execution model if this candidate is revisited later.
