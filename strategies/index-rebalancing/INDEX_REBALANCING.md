# Index Rebalancing Price Pressure

**Version:** 1.0
**Status:** Level 1 in progress (research spec approved, data verifications passed, event-table construction next)
**Classification:** Relative Value / Event-Driven Mean Reversion (Category 2: Regulatory & Mandate Constraints)

## 1. Executive Summary

This document records the investigation of index rebalancing price pressure as an event-driven mean reversion strategy. The hypothesis: index-tracking funds are forced to buy additions and sell deletions on a fixed schedule regardless of price, creating temporary price distortion that partially reverses after the effective date.

**Result:** Not yet tested. The hypothesis is heavily documented in the academic literature (40 years of evidence), but the effect has demonstrably decayed in the S&P 500 (Bennett, Stulz, and Wang, 2022). The surviving venue is small-cap indices: S&P SmallCap 600, S&P MidCap 400, and Russell 2000.

The implementation will provide an event-table builder (additions/deletions with announcement and effective dates), a post-effective-date backtest harness, and a friction model that includes borrow cost for the short leg.

## 2. The Economic Edge

### The Why

Index-tracking funds, ETFs, and benchmarked active funds must align their holdings with the published index composition. When a stock is added to an index, index funds are forced to buy it; when deleted, forced to sell — regardless of price. Pavlova and Sikorskaya (2023) show this demand is highly inelastic: a 1% increase in benchmarking intensity raises June returns by 27 bps. Gabaix and Koijen (2021) show one dollar of inelastic buying moves prices by roughly five dollars.

### The Counterparty

The counterparties are passive index funds, ETFs, and benchmarked active funds that must transact on the index schedule. They are not trading against us deliberately — they are fulfilling a mandate. They give up the post-reversal return because tracking the new composition is mandatory.

### The Trade

The distortion reverses once the forced flow stops:

| Leg | Entry | Direction | Evidence |
|---|---|---|---|
| Long deletions | Open after effective date | Buy | Chen, Noronha, Singal (2004): -14% avg, gone within 60 days; Sui (2006): +4.9% in 20 days; Arnott et al. (2023): deletions beat additions by >20% in the year after |
| Short additions | Open after effective date | Short (borrow permitting) | Sui (2006): -2.3% in 20 days; Alpha Architect (2014-2023): -5.7% reversal in the month after reconstitution |

### Decay Warning

The effect has decayed to ~zero in the S&P 500 (Bennett, Stulz, Wang, 2022; Preston and Soe, 2021). This strategy deliberately excludes the S&P 500 and targets small-cap indices where the effect persists (112x reconstitution-day volume for S&P 600, 120x for Russell 2000).

## 3. Machine-Executable Rules

### 3.A Event Definition

- Universe: S&P SmallCap 600 and S&P MidCap 400 additions/deletions (Russell 2000 pending list availability)
- Only discretionary changes (market-cap driven). Exclude M&A, bankruptcy, spin-off, and IPO-driven events.
- Event fields: ticker, index, action (addition/deletion), announcement date, effective date, reason category

### 3.B Entry

- Enter at the open of the first trading day after the effective date
- Long deletions: buy the deleted stock
- Short additions: short the added stock only if borrow is available below the pre-registered fee cap
- Minimum liquidity filter: average daily dollar volume above pre-registered threshold
- Minimum price history: one year of trading before the event

### 3.C Exit

- Exit at the end of the planned holding window: 10, 20, 40, or 60 trading days (tested as a parameter range)
- Force-close and record if delisted or acquired during the window
- Pre-registered stop loss

### 3.D Position Sizing

- Equal-risk-weight across events (volatility targeting per event)
- Sized from the lower of: portfolio risk budget, volatility target, executable depth

## 4. Friction Model

| Cost | Base Case | Stress Case |
|---|---|---|
| Slippage | 1.5 bps/side | 10 bps/side (S&P 600 names) |
| Commission | Per-share proxy | Same |
| SEC fee | Section 31 | Same |
| Borrow (short leg) | Modeled, fee cap pre-registered | Hard-to-borrow filter |

**Registration:** Rejection if the base case does not clear friction after borrow.

## 5. Research Scope

- Signal source: Publicly announced index changes (S&P DJI press releases, FTSE Russell lists)
- Execution proxy: The constituent stocks themselves
- Horizon: 10-60 trading days after effective date
- Data route: Databento EQUS.MINI (ohlcv-1m) + S&P DJI press releases
- First-pass design: Daily event study, buy-and-hold windows
- Excluded: S&P 500 (decayed), micro-caps, M&A-driven events, borrow-unavailable shorts

## 6. Level-1 Test Results

**Not yet run.** Level 1 requires the three data verifications from the research spec:
1. EQUS.MINI small-cap coverage (incl. delisted names)
2. S&P DJI announcement-date archive availability
3. FTSE Russell historical list availability

## 7. Rejection Gates

Reject if any of the following is true:
- Post-effective-date reversal does not survive the base-case friction model
- Reversal disappears or inverts out of sample
- Result depends only on S&P 500 changes or a single year
- Event table cannot be reconstructed without look-ahead
- Borrow costs exceed the short-side edge
- Long-deletions leg alone is not profitable after friction
- Monte Carlo/bootstrap shows unacceptable drawdown or ruin probability
- Capacity too low for intended capital

## 8. Next Step

1. Verify EQUS.MINI small-cap coverage
2. Verify S&P DJI announcement-date archive
3. Verify FTSE Russell historical list availability
4. If all three pass: build the event-table builder and Level-1 backtest harness
5. If any fails: revise the venue or data route before coding

## 9. Key References

- Shleifer (1986), Journal of Finance — permanent addition effect, downward-sloping demand
- Harris and Gurel (1986), Journal of Finance — temporary price pressure
- Chen, Noronha, Singal (2004), Journal of Finance — asymmetry: additions permanent, deletions temporary
- Chang, Hong, Liskovich (2015), RFS — Russell cutoff, ~20% inclusion effect
- Pavlova and Sikorskaya (2023), RFS — inelastic benchmarked demand
- Gabaix and Koijen (2021) — inelastic markets hypothesis
- Arnott, Brightman, Kalesnik, Wu (2023), FAJ — post-rebalance reversal, deletions beat additions >20%
- Bennett, Stulz, Wang (2022) — the disappearing index effect (S&P 500 decay)
- Reed (2018) — loan fee distribution (borrow cost)
- Alpha Architect (2024) — 2014-2023 practitioner study, 3,488 additions, 2,517 deletions
