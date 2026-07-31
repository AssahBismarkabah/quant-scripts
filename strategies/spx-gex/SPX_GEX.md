# SPX Dealer Gamma Exposure

**Version:** 1.0
**Status:** Pre-research
**Classification:** Intraday Bias / Trend Following and Mean Reversion Regime Filter

## 1. Executive Summary

This document records the next structural mechanic to investigate after the funding-basis candidate was rejected. The idea is to use SPX options dealer gamma exposure as a daily regime filter for intraday behavior.

The hypothesis is simple:

- positive gamma may favor mean reversion or pinning
- negative gamma may favor momentum or trend persistence

This is a research candidate, not a proven edge.

## 2. The Economic Edge

The source of return, if it exists, comes from dealer hedging flows.

Options market makers must hedge changing delta exposure as the underlying moves and time decays. That hedging can dampen or amplify intraday moves depending on aggregate gamma.

The counterparty is the dealer hedging book. The research question is whether that structure survives realistic friction and can be turned into a machine-executable intraday regime filter.

## 3. Research Scope

- Underlying: SPX
- Signal source: SPX options chain and open interest
- Execution target: SPX intraday price action
- Horizon: 5-minute to 15-minute intraday
- Regime design: daily dealer gamma sign and magnitude
- First-pass data route: Cboe EOD options data, with Databento reserved for deeper replay if required

This record is intentionally narrow. It documents the first SPX gamma-flow candidate, not every possible options strategy.

## 4. What Needs to Be Tested

The research pipeline will need to answer:

- can the daily gamma regime be reconstructed from historical data
- does the regime separate intraday trend and mean-reversion behavior
- does the result survive friction and out-of-sample splitting
- does the effect remain stable across different volatility states

## 5. Verified Status

No gamma-flow code has been written yet.

This strategy record exists so the new track is captured before implementation starts.

## 6. Next Step

Build the research pipeline only after the SPX data route and regime definition are frozen in the IA spec.
