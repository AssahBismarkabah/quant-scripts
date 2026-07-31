# SPX Dealer Gamma Exposure

**Version:** 1.0
**Status:** Pre-research
**Classification:** Intraday Bias / Trend Following and Mean Reversion Regime Filter

## 1. Executive Summary

This document records the next structural mechanic to investigate after the funding-basis candidate was rejected. The idea is to use SPX options dealer gamma exposure as a daily regime filter for intraday behavior.

The hypothesis is simple:

- positive dealer gamma may favor mean reversion or pinning
- negative dealer gamma may favor momentum or trend persistence

This is a research candidate, not a proven edge.

## 2. The Economic Edge

The source of return, if it exists, comes from dealer hedging flows.

Options market makers must hedge changing delta exposure as the underlying moves and time decays. That hedging can dampen or amplify intraday moves depending on aggregate gamma.

The counterparty is the dealer hedging book. The research question is whether that structure survives realistic friction and can be turned into a machine-executable intraday regime filter.

### Gamma Regime Formula

For the first pass, use the daily EOD chain to compute:

`contract_gex = gamma × open_interest × contract_multiplier × underlying_price² × 0.01`

For SPX, the contract multiplier is `100`.

First compute aggregate customer-side gamma exposure:

`aggregate_gex = Σ contract_gex`

Then invert the aggregate to approximate dealer positioning:

`dealer_gex = -1 × aggregate_gex`

Regime label:

- `dealer_gex > 0` -> positive dealer gamma regime
- `dealer_gex < 0` -> negative dealer gamma regime

Treat the first pass as a regime classifier, not an executable edge.

## 3. Research Scope

- Underlying: SPX
- Signal source: SPX options chain and open interest
- Execution target: SPX intraday price action
- Horizon: 5-minute to 15-minute intraday
- Regime design: daily dealer gamma sign and magnitude
- First-pass data route: Cboe EOD options data, with Databento reserved for deeper replay if required
- First-pass model: daily EOD regime classification before any intraday replay
- 0DTE handling in version one: exclude 0DTE from the first-pass gamma calculation and use only 1DTE and longer expirations from the previous day's EOD snapshot

This record is intentionally narrow. It documents the first SPX gamma-flow candidate, not every possible options strategy.

## 4. What Needs to Be Tested

The research pipeline will need to answer:

- can the daily gamma regime be reconstructed from historical data
- does the regime separate intraday trend and mean-reversion behavior
- does the result survive friction and out-of-sample splitting
- does the effect remain stable across different volatility states

## 5. Machine-Executable Rules

### 5.A Daily Regime Classification

At the end of the Cboe 15:45 snapshot, compute:

`contract_gex = gamma × open_interest × contract_multiplier × underlying_price² × 0.01`

For SPX, the contract multiplier is `100`.

Then aggregate:

`aggregate_gex = Σ contract_gex`

Invert the aggregate to approximate dealer positioning:

`dealer_gex = -1 × aggregate_gex`

If `dealer_gex > 0`, the day is a positive dealer gamma regime.

If `dealer_gex < 0`, the day is a negative dealer gamma regime.

### 5.B Intraday Entry

The gamma regime is the researched filter. The first pass avoids the open and close auction periods because they are dominated by opening and closing cross flow rather than clean dealer hedging signals. The intraday test window is therefore set to a mid-day slice.

Common setup:

- evaluation time: 13:30 ET
- lookback return: 11:30 ET to 13:30 ET
- holding period: 13:30 ET to 15:00 ET

Positive dealer gamma regime:

- if the 11:30 ET to 13:30 ET return is positive, enter short at 13:30 ET and exit at 15:00 ET
- if the 11:30 ET to 13:30 ET return is negative, enter long at 13:30 ET and exit at 15:00 ET

Negative dealer gamma regime:

- if the 11:30 ET to 13:30 ET return is positive, enter long at 13:30 ET and exit at 15:00 ET
- if the 11:30 ET to 13:30 ET return is negative, enter short at 13:30 ET and exit at 15:00 ET

### 5.C Intraday Exit

- exit all positions at 15:00 ET
- if the trade cannot be established at 13:30 ET, skip it

### 5.D Trade Filter

- only one regime may be active on a given day
- if the regime is ambiguous or the data quality check fails, do not trade

## 5. Verified Status

No gamma-flow code has been written yet.

This strategy record exists so the new track is captured before implementation starts.

## 6. Next Step

Build the research pipeline only after the SPX data route and regime definition are frozen in the IA spec.
