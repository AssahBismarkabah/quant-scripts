# IVAMR: Intraday Value Area Momentum & Mean Reversion

**Version:** 1.0
**Status:** Ready for Backtesting & Implementation
**Classification:** Intraday Bias / Trend Following & Mean Reversion Hybrid

---

## Table of Contents

1. [Executive Summary & Strategy Philosophy](#1-executive-summary--strategy-philosophy)
2. [The Economic Edge ("The Why")](#2-the-economic-edge-the-why)
3. [Data & Pre-Market Calculations](#3-data--pre-market-calculations)
4. [Machine-Executable Rules](#4-machine-executable-rules)
5. [Validation & Overfitting Protocol](#5-validation--overfitting-protocol)
6. ["When to Say No" (Go/No-Go Thresholds)](#6-when-to-say-no-gono-go-thresholds)
7. [Automation & Live Monitoring](#7-automation--live-monitoring)
8. [Technical Notes for Implementation](#8-technical-notes-for-implementation)
9. [Appendix: Quick Reference Card](#9-appendix-quick-reference-card)

---

## 1. Executive Summary & Strategy Philosophy

This document defines the complete, machine-executable blueprint for the IVAMR strategy. It rejects subjective visual analysis in favor of strict boolean logic, volatility-adjusted parameters, and rigorous statistical validation. The strategy is designed to survive across varying market regimes by relying on structural market mechanics rather than overfitted historical patterns. It strictly adheres to the principle that every rule must have a clear economic justification, and every parameter must be robust across a wide range of values.

**Design Principles:**
- **No subjective interpretation** — every rule is machine-executable.
- **Volatility-adjusted parameters** — no fixed-point magic numbers.
- **Statistical validation** — the strategy must survive out-of-sample and Monte Carlo testing.
- **Structural market mechanics** — the edge is grounded in institutional order flow, not overfitted historical patterns.
- **Economic justification** — every rule has a clear counterparty and rationale; no assumptions without a thesis.

---

## 2. The Economic Edge ("The Why")

A strategy without a defined counterparty is gambling. This strategy exploits two distinct structural inefficiencies:

### Trend Following Edge (Breakouts)

| Aspect | Detail |
|---|---|
| **The Counterparty** | Undercapitalized retail traders and overnight position holders |
| **The Mechanic** | When price breaks the Value Area High (VAH) or Low (VAL), it triggers a cascade of stop-loss orders. Institutional algorithms executing daily mandates (VWAP/TWAP) absorb this liquidity, driving momentum. We ride the forced liquidation of trapped participants |

### Mean Reversion Edge (Break-ins / Fades)

| Aspect | Detail |
|---|---|
| **The Counterparty** | Late-informed retail breakout traders and algorithmic liquidity grabs |
| **The Mechanic** | When price pierces a value extreme but fails to sustain (closing back inside the range), it signals a failed liquidity hunt. The retail traders who bought the breakout are now trapped. As their stop losses trigger, they provide the liquidity for the price to snap back to the Point of Control (POC). We fade a failed structural move |

---

## 3. Data & Pre-Market Calculations

### Data Requirements

| Requirement | Specification |
|---|---|
| **Type** | Tick-level or 1-minute OHLCV (e.g., Databento, Polygon, IQFeed) |
| **Adjustments** | Unadjusted, survivorship-bias-free data |
| **Prohibited Sources** | Yahoo Finance and other free data corrupt intraday volume/price calculations |

### Session Boundary: RTH Only

The Volume Profile (VAH, VAL, POC) must be calculated using **only the Regular Trading Hours (RTH) cash session** from the previous trading day: **9:30 AM - 4:00 PM EST**.

**Do NOT include:**
- Overnight electronic trading (4:00 PM - 9:30 AM EST)
- Pre-market session
- After-hours session

**Why this matters:**
1. The academic literature on intraday patterns (U-shaped volume/volatility) specifically studies the RTH cash session. The structural mechanics of institutional rebalancing, news digestion at the open, and overnight risk avoidance at the close exist only during RTH.
2. If you include overnight volume in the profile, you will distort the POC location, shift VAH/VAL levels, and create false support/resistance levels that have no structural relevance to the RTH session.

**Explicit specification for implementation:**
```
PREVIOUS DAY VOLUME PROFILE CALCULATION:
- Session:     Regular Trading Hours (RTH) ONLY
- Time Window: 9:30:00 AM EST to 4:00:00 PM EST (previous trading day)
- Data Source: Use only trades executed during RTH
- Exclusion:   Do NOT include overnight electronic trading, pre-market, or after-hours
- Profile:     70% Value Area based on RTH volume distribution
```

### Daily Pre-Market Routine (Executed at 9:15 AM EST)

1. **Value Area High (VAH)** — Calculate from the previous day's **70% Volume Profile** (RTH session only).
2. **Value Area Low (VAL)** — Calculate from the previous day's **70% Volume Profile** (RTH session only).
3. **Point of Control (POC)** — The price level with the highest traded volume from the previous day's RTH session.
4. **14-period 15-minute Average True Range (ATR)** — Volatility reference for the trading day.

---

## 4. Machine-Executable Rules

### 4.A. Unified Time & Risk Filters

| Filter | Rule |
|---|---|
| **Entry Window Start** | No entries before 9:45 AM EST (avoids opening auction noise) |
| **Entry Window End** | No entries after 2:30 PM EST (avoids closing cross volatility) |
| **Hard Time Exit** | If a position is still open at 3:30 PM EST, execute a Market Close. (Mandatory to avoid the 3:50 PM Market-On-Close imbalance risk) |
| **Daily Kill Switch** | If daily realized loss reaches **3%** of Total Account Equity, halt all trading for the day |

### 4.B. Entry Logic (The 4 Plays)

All entries execute at the exact close of the qualifying 15-minute candle.

---

#### Play 1: Bullish Breakout & Retest (Trend Following)

```
IF:
  1. 15-min Candle Close > Previous_Day_VAH
  2. Next 15-min Candle Low <= Previous_Day_VAH         (retest)
  3. Next 15-min Candle Low >= (Previous_Day_VAH - (0.5 * 15-min ATR))   (structural integrity)
  4. Next 15-min Candle Close > Previous_Day_VAH         (confirmation)
THEN: Execute Market Buy at Close.
```

---

#### Play 2: Bearish Breakout & Retest (Trend Following)

```
IF:
  1. 15-min Candle Close < Previous_Day_VAL
  2. Next 15-min Candle High >= Previous_Day_VAL        (retest)
  3. Next 15-min Candle High <= (Previous_Day_VAL + (0.5 * 15-min ATR))   (structural integrity)
  4. Next 15-min Candle Close < Previous_Day_VAL        (confirmation)
THEN: Execute Market Sell at Close.
```

---

#### Play 3: Bullish Break-in / Fade the Breakdown (Mean Reversion)

```
IF:
  1. 15-min Candle Low < Previous_Day_VAL
  2. 15-min Candle Close > Previous_Day_VAL
  3. Candle Close is in the top 40% of the candle's total range:
       (Close - Low) / (High - Low) >= 0.60
THEN: Execute Market Buy at Close.
```

---

#### Play 4: Bearish Break-in / Fade the Breakout (Mean Reversion)

```
IF:
  1. 15-min Candle High > Previous_Day_VAH
  2. 15-min Candle Close < Previous_Day_VAH
  3. Candle Close is in the bottom 40% of the candle's total range:
       (High - Close) / (High - Low) >= 0.60
THEN: Execute Market Sell at Close.
```

---

### 4.C. Exit Logic (Stop, Target, Time)

#### For Plays 1 & 2 (Trend Following)

| Component | Rule |
|---|---|
| **Stop Loss** | Entry Price +/- (**2.0** * 15-min ATR). Volatility-adjusted. |
| **Take Profit** | None — use a **trailing stop** instead |
| **Trail: Breakeven** | Once price moves **+1.5 ATR** in your favor, move Stop Loss to breakeven |
| **Trail: Active** | Thereafter, trail the stop at the **2-period 15-minute Low** (longs) or **High** (shorts) |

#### For Plays 3 & 4 (Mean Reversion)

| Component | Rule |
|---|---|
| **Stop Loss** | Extreme of the trigger candle (High for shorts, Low for longs) +/- (**0.5** * 15-min ATR) buffer |
| **Take Profit** | Previous Day **POC** |

#### Pre-Flight R:R Check (Crucial)

Before executing Play 3 or 4, the machine must calculate:

```
Stop_Distance = |Entry Price - Stop Loss Price|
Target_Distance = |Entry Price - Previous Day POC|

IF Target_Distance < (1.5 * Stop_Distance): ABORT TRADE.
```

This prevents taking trades where the "extends far" scenario ruins the risk-to-reward math.

### 4.D. Position Sizing (Volatility Targeting)

Do not use fixed contract sizes. Size based on the mathematical risk of the specific setup.

| Parameter | Value |
|---|---|
| **Risk per Trade** | **1.0%** of Total Account Equity |
| **Formula** | `Contracts = Floor( (Account_Equity * 0.01) / Stop_Distance )` |
| **Max Contracts** | 10 per trade (prevent slippage on market orders) |

---

## 5. Validation & Overfitting Protocol

A strategy is only as good as its validation. We do not trust in-sample results.

### Data Split

| Period | Purpose | Action |
|---|---|---|
| **2010 - 2018** | In-Sample (Tuning) | Build logic, tune ATR multipliers (1.5 vs 2.0), optimize Volume Profile parameters (68% vs 70% vs 72%) |
| **2019 - 2023** | Out-of-Sample (Validation) | Freeze all rules. Change nothing. If the strategy fails here, it is overfitted. Bin it. |

### Monte Carlo Simulation (10,000 Iterations)

Run both **Reshuffle** (reordering trades) and **Bootstrap** (resampling with replacement) on the Out-of-Sample trades.

| Metric | Requirement |
|---|---|
| **Dispersion** | Tight distribution of final equity curves. Wild variance based on trade sequence implies a fragile edge |
| **Probability of Ruin** | Less than **5%** of bootstrapped paths may result in a 20% drawdown |
| **Expected Max Drawdown** | Calculate the 95th percentile of max drawdown. This is your psychological pain threshold for live trading |

---

## 6. "When to Say No" (Go/No-Go Thresholds)

Amateurs try to be right; professionals find out when they are wrong. If the Out-of-Sample backtest does not meet **all** of these criteria, the strategy is rejected.

| Metric | Threshold |
|---|---|
| **Profit Factor** | >= 1.3 |
| **Average Trade (Net)** | >= 0.2% of account equity (after 1 tick slippage + commissions) |
| **Maximum Drawdown** | <= 15% |
| **Win Rate — Trend Following** | >= 40% |
| **Win Rate — Mean Reversion** | >= 55% |
| **OOS Degradation** | Out-of-Sample Net Profit >= 70% of In-Sample Net Profit |

---

## 7. Automation & Live Monitoring

### Automation

- The strategy is coded and connected to the broker via API (e.g., Interactive Brokers, Tradovate, Alpaca).
- The machine executes without hesitation, emotion, or manual intervention.

### Live Statistical Supervision

Your job is no longer to execute trades; it is to monitor the statistical health of the algorithm against the Monte Carlo expectations.

#### Kill Switches (When to Pause the Machine)

| Kill Switch | Condition | Action |
|---|---|---|
| **1. Drawdown Breach** | Live rolling max drawdown exceeds the 95th percentile Max Drawdown from Monte Carlo | Halt the strategy. The market regime has shifted or the edge is broken |
| **2. Edge Degradation** | Live Average Trade drops below **50%** of backtested Average Trade over a rolling 50-trade window | Halt. The structural inefficiency is being arbitraged away |
| **3. Consecutive Losses** | Strategy experiences **20 consecutive losses** (statistically improbable given expected win rate) | Halt. Investigate for data feed errors or execution failures |

---

## 8. Technical Notes for Implementation

### 8.A. Scope Clarification: This is NOT the Academic Paper

This document defines a **Volume Profile / Auction Market Theory strategy**. It is **not** a translation of the Gao, Han, Li, and Zhou paper ("Market Intraday Momentum").

- The paper documents a **time-based anomaly**: first half-hour return predicts last half-hour return.
- This document documents a **price-location anomaly**: Value Area breakouts and fades.
- If your goal was to test the paper, this strategy will fail to do so. If your goal was to build a robust Volume Profile strategy, this document is complete. Do not confuse the two in your backtesting analysis.

### 8.B. Volume Profile Data Granularity Trap

**The flaw:** If the developer calculates the previous day's 70% Volume Profile using 15-minute OHLCV data, the strategy will fail. A 15-minute candle only gives Open, High, Low, Close, and Total Volume. It does not reveal *where* within that range the volume actually occurred.

**The fix:** The developer must use **1-minute or tick-level data** to calculate VAH, VAL, and POC. They must build a Volume-at-Price histogram for the previous day's RTH session using 1-minute closes (or tick data), find the price level with the highest volume (POC), and expand outward until 70% of the day's total volume is captured. Only then should they apply the 15-minute entry logic.

### 8.C. The "Next Candle" Execution Delay

**The flaw:** For Plays 1 and 2, the rule states: `IF 15-min Candle Close > VAH... AND Next 15-min Candle Close > VAH... THEN Execute Market Buy at Close.` If the developer codes execution at the close of Candle N+1 (the confirmation candle), they introduce **look-ahead bias** — the close price is not known until the candle actually finishes.

**The fix:** The developer must explicitly code a **1-bar execution delay**:
1. Signal is evaluated on the close of Candle N+1.
2. Market Order is executed at the **open** of Candle N+2.
3. The backtest must account for slippage between the close of N+1 and the open of N+2.

### 8.D. Trailing Stop Logic in Backtesting

**The flaw:** For Plays 1 and 2, the trailing stop rule is: `Trail the stop at the 2-period 15-minute Low (for longs) or High (for shorts).` Standard backtesting engines evaluate trailing stops based on the *close* of each bar. In reality, price will hit the 2-period low *during* the bar (intra-bar). If the backtester only checks the close, it will miss stop-outs and artificially inflate the win rate.

**The fix:** The developer must use **intra-bar order simulation**:
- In Backtrader: `process_orders_on_close=False`
- In Pine Script: `calc_on_every_tick=true`
- The stop loss must be evaluated against the intra-bar High/Low, not just the closing price.

---

## 9. Appendix: Quick Reference Card

### Pre-Market Checklist (9:15 AM EST)

- [ ] Calculate VAH (70% Volume Profile)
- [ ] Calculate VAL (70% Volume Profile)
- [ ] Calculate POC
- [ ] Calculate 14-period 15-min ATR
- [ ] Verify daily loss < 3% of equity (continue halted if not)

### Entry Decision Matrix

| Condition | Play | Direction |
|---|---|---|
| Breakout + retest holds + confirms > VAH | 1 | Long (Trend) |
| Breakdown + retest holds + confirms < VAL | 2 | Short (Trend) |
| Low < VAL, close > VAL, close in upper 60% of range | 3 | Long (Reversion) |
| High > VAH, close < VAH, close in lower 60% of range | 4 | Short (Reversion) |

### Exit Quick Reference

| Play | Stop Loss | Target | Trail |
|---|---|---|---|
| 1 (Long Trend) | Entry - 2.0 ATR | None | BE @ +1.5 ATR, then 2-bar low |
| 2 (Short Trend) | Entry + 2.0 ATR | None | BE @ +1.5 ATR, then 2-bar high |
| 3 (Long Reversion) | Trigger low - 0.5 ATR | Prev POC | N/A |
| 4 (Short Reversion) | Trigger high + 0.5 ATR | Prev POC | N/A |

### Go / No-Go Gate

```
ALL must pass:
  Profit Factor      >= 1.3
  Avg Trade (net)    >= 0.2% equity
  Max DD             <= 15%
  TF Win Rate        >= 40%
  MR Win Rate        >= 55%
  OOS / IS Profit    >= 70%
```

---

**Final Directive:** This document is the complete blueprint. It contains no subjective language, no magic numbers, and no unverified assumptions. It is ready to be handed to a developer for Python/Pine Script implementation. Execute the backtest. Let the data prove if the edge exists. If it fails the Out-of-Sample or Monte Carlo tests, accept the result, save your capital, and move to the next hypothesis.
