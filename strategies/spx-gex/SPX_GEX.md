# SPX Dealer Gamma Exposure

**Version:** 1.0
**Status:** Rejected at Level 1 (friction gate); Level-2 upgrade considered and DECLINED on V1 evidence (2026-08-04) - candidate closed, do not revisit without new evidence
**Classification:** Intraday Bias / Trend Following and Mean Reversion Regime Filter

## 1. Executive Summary

This document records the investigation of SPX options dealer gamma exposure as a daily regime filter for intraday behavior. The hypothesis was that positive dealer gamma favors mean reversion and negative dealer gamma favors momentum.

**Result:** The regime classifier works (Convention B produces both regimes with intuitive 2023 alignment), but the intraday playbook fails the conservative friction model. The candidate is rejected at Level 1.

The implementation provides a normalized input contract, a regime classifier, a mid-day backtest harness, and Databento adapters for SPX/SPXW options and SPY intraday bars.

## 2. The Economic Edge

The source of return, if it exists, comes from dealer hedging flows.

Options market makers must hedge changing delta exposure as the underlying moves and time decays. That hedging can dampen or amplify intraday moves depending on aggregate gamma.

The counterparty is the dealer hedging book. The research question was whether that structure survives realistic friction and can be turned into a machine-executable intraday regime filter.

**Level-1 Finding:** The regime classifier separates days into positive/negative gamma regimes that align with 2023 market narrative (spring/summer rally = positive gamma; Aug-Oct selloff = negative gamma). However, the intraday playbook (fade in positive regime, follow in negative regime) produces marginal edge that does not survive conservative friction.

### Gamma Regime Formula (Convention B — Standard Public Convention)

For the first pass, use the daily EOD chain to compute per-contract gamma exposure with option-type sign (standard public convention: dealers long calls, short puts on index level):

`contract_gex = gamma × open_interest × contract_multiplier × underlying_price² × 0.01 × sign`

where `sign = +1` for calls, `-1` for puts.

For SPX, the contract multiplier is `100`.

Aggregate dealer gamma exposure (no inversion — the type sign already encodes dealer positioning):

`dealer_gex = Σ contract_gex`

Regime label:

- `dealer_gex > 0` -> positive dealer gamma regime
- `dealer_gex < 0` -> negative dealer gamma regime

**Note:** The original doc formula (Convention A: invert aggregate of unsigned contract_gex) is structurally degenerate — it can never produce a positive regime because gamma > 0 for both calls and puts. Convention B was adopted per the spec's open question on sign convention and matches the public standard (perfiliev, SpotGamma, insiderfinance).

Treat the first pass as a regime classifier, not an executable edge.

### Execution Contract

The code path assumes two files when running the strategy in executable mode:

- a point file containing the SPX options snapshot
- a bars file containing the intraday SPY proxy bars

Supported local research commands:

- `make -C research/spx-gex smoke`
- `make -C research/spx-gex template`
- `make -C research/spx-gex point-template`
- `make -C research/spx-gex bars-template`
- `make -C research/spx-gex sessions-template`
- `make -C research/spx-gex backtest POINT=... BARS=...`
- `make -C research/spx-gex walk-forward INPUT=...`
- `make -C research/spx-gex normalize-cboe INPUT=...`
- `make -C research/spx-gex fetch-spy-bars START=... END=... OUTPUT=...`

## 3. Research Scope

- Underlying: SPX
- Signal source: SPX options chain and open interest (SPX monthlies + SPXW weeklies, combined with SUM dedupe)
- Execution target: SPY intraday price action as the tradable proxy for execution backtests
- Horizon: 5-minute to 15-minute intraday
- Regime design: daily dealer gamma sign and magnitude
- First-pass data route: Databento OPRA.PILLAR (SPX.OPT + SPXW.OPT statistics, stat_type=9) + OptionsDX EOD chains
- First-pass model: daily EOD regime classification before any intraday replay
- 0DTE handling in version one: exclude 0DTE from the first-pass gamma calculation and use only 1DTE and longer expirations from the previous day's EOD snapshot

This record documents the first SPX gamma-flow candidate and its Level-1 rejection.

## 4. Level-1 Test Results (2023-03-28 to 2023-12-29)

### Data
- **OptionsDX SPX EOD chains:** 12 monthly files, full chains (daily/weekly/monthly expiries), underlying within 0.05% of SPX close
- **Databento SPX.OPT (monthlies):** 250 trade days, 3.9M OI rows, 16,962 contracts/day
- **Databento SPXW.OPT (weeklies):** 250 trade days, 8.2M OI rows, 35,724 contracts/day
- **Combined OI (SUM dedupe):** ~50 expiries/day, ~15M OI/day
- **EQUS.MINI SPY 1m bars:** 101,627 bars, 2023-03-28..12-29

### Regime Distribution (Convention B)
| Regime | Sessions | Avg Net Edge (bps) | Win Rate |
|--------|----------|-------------------|----------|
| Positive | 122 | +0.64 | 45.9% |
| Negative | 70 | −5.02 | 50.0% |

Regime narrative alignment: Apr–Jul mostly positive (rally), Aug–Oct mostly negative (selloff), Nov–Dec mostly positive (year-end rally).

### Friction Model (Conservative)
- Slippage: 1 bps/side (2 bps round-trip)
- Commission: 0.1 bps
- SEC fee: 0.08 bps
- **Total: 2.18 bps per trade**

### Net After Friction
| Regime | Gross Edge | Net Edge (after 2.18 bps) |
|--------|------------|---------------------------|
| Positive | +0.64 bps | **−1.54 bps** |
| Negative | −5.02 bps | **−7.20 bps** |

**Result: Fails the conservative friction model (rejection gate triggered).**

## 5. Execution Assumptions (Level 1)

SPX remains the signal source. SPY is the tradable proxy used for execution testing because it is directly tradeable intraday while preserving exposure to the same broad market move.

### Friction Model
- SEC transaction fee: apply the current Section 31 rate at the time of testing
- Broker commission: configurable per share assumption for SPY
- Slippage: 1 basis point per side as the default conservative buffer
- Spread impact: approximate through midpoint minus slippage rather than ideal fills

**Total conservative friction: 2.18 bps per round-trip trade.**

## 5. Machine-Executable Rules

### 5.A Daily Regime Classification

At the end of the Cboe 15:45 snapshot, compute per-contract gamma exposure with option-type sign (standard public convention: dealers long calls, short puts on index level):

`contract_gex = gamma × open_interest × contract_multiplier × underlying_price² × 0.01 × sign`

where `sign = +1` for calls, `-1` for puts.

For SPX, the contract multiplier is `100`.

Aggregate dealer gamma exposure (no inversion — the type sign already encodes dealer positioning):

`dealer_gex = Σ contract_gex`

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

**Note:** No position sizing rule was defined (volatility targeting, risk-based sizing). This is a gap per institutional approach requirements.

## 6. Verified Status

The gamma-flow scaffold exists and passes the current test suite.

The implementation includes Databento adapters for SPX/SPXW options (OPRA.PILLAR statistics, stat_type=9) and SPY intraday bars (EQUS.MINI ohlcv-1m), OptionsDX EOD chain normalization, regime classifier (Convention B), and mid-day backtest harness with per-regime reporting.

**Level-1 Result: REJECTED** — fails conservative friction model (rejection gate: "the result fails a conservative friction model").

## 7. Next Step

**Candidate rejected at Level 1 and the Level-2 upgrade was considered and declined on 2026-08-04.** The pipeline (data adapters, regime classifier, backtest harness) is preserved for future candidates.

### Level-2 decline decision (2026-08-04) - record, do not re-litigate

The proposed Level-2 upgrade (intraday 0DTE zero-gamma/gamma-wall price-level triggers instead of time windows) was evaluated and rejected before any new data was fetched. The Level-1 results already answer the question the upgrade would test:

- Positive regime gross edge: **+0.64 bps** - a signal that barely exists before costs; 2.18 bps friction finished it.
- Negative regime gross edge: **-5.02 bps** - in the regime where the hypothesis predicts momentum, the playbook **lost money before any costs**. The signal is directionally wrong or absent at the 1-3 hour horizon, not friction-inefficient.

A price-level trigger changes when a trade is entered, not whether dealer gamma predicts short-horizon returns. If the predictability is absent at that horizon (per V1), a better trigger cannot manufacture it. Re-testing the same signal with a new execution wrapper carries a negative prior from our own data and would repeat the work without new information.

**Reopen condition (must be met before any Level-2 work):** new evidence that intraday dealer-gamma predicts returns at tradeable scale - e.g., independent peer-reviewed or broker research showing a net-of-cost edge at intraday horizons, or a new data source (intraday OI/flow) that demonstrably changes the V1 conclusion. The zero-gamma breakout claim alone is vendor marketing and is not sufficient per the spec's evidence-classification rule (promotional material does not validate a mechanic).

Remaining Level-2 requirements (position sizing, Monte Carlo validation, walk-forward, registered thresholds) are moot until the reopen condition is met.
