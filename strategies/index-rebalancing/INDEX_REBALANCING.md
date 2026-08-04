# Index Rebalancing Price Pressure

**Version:** 1.0
**Status:** Level 1-2 complete (2026-08-04) - candidate REJECTED: surviving short-additions edge is a single-year (March 2025 S&P 600) batch effect, fails the registered robustness gate
**Classification:** Relative Value / Event-Driven Mean Reversion (Category 2: Regulatory & Mandate Constraints)

## 1. Executive Summary

This document records the investigation of index rebalancing price pressure as an event-driven mean reversion strategy. The hypothesis: index-tracking funds are forced to buy additions and sell deletions on a fixed schedule regardless of price, creating temporary price distortion that partially reverses after the effective date.

**Result:** Tested at Level 1 and Level 2, then **rejected**. The effect has demonstrably decayed in the S&P 500 (Bennett, Stulz, and Wang, 2022), and the Level-1 study found the reversal only in a narrow cell: shorting S&P 600 additions held ~10 trading days after the effective date (+769 bps abnormal, t=2.88). Level-2 robustness testing (2026-08-04) showed that cell is a **single-batch phenomenon**: the March 2025 S&P 600 reconstitution (11 events, +2,081 to +4,526 bps each) drives the entire mean; 2024 was flat, September/December 2025 mixed-to-negative, 2026 negative. Under the pre-registered gate "result depends on a single year", the candidate is rejected. The primary long-deletions leg never cleared its gate, and Russell 2000 additions show a permanent, not temporary, inclusion effect. See sections 6 and 8.

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

- Universe: S&P SmallCap 600 and S&P MidCap 400 additions (short leg, ~10td hold); deletions leg and Russell 2000 excluded per Level-1 findings. **NOTE: candidate rejected at Level 1-2 (single-year effect); section retained for reference.**
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

**Complete (2026-08-04).** All three data verifications from the research spec passed on 2026-08-03 (EQUS.MINI small-cap coverage incl. delisted names; S&P DJI announcement-date archive; FTSE Russell historical list availability). Event tables were built and cross-validated (1,204 S&P events, 98.63% date agreement vs Wikipedia; 1,196 Russell events validated vs official recaps), and the event study ran over 1,604 events (2024-2026, benchmark-adjusted vs IJR/IJH/IWM, base and stress friction).

Headline cells, mean abnormal bps after friction:

| Venue / action | 10td | 20td | 40td | 60td |
|---|---|---|---|---|
| S&P 600 additions (short) | **+769** (t=2.88, n=35) | +320 | -170 | +8 |
| S&P 400 additions (short) | +498 (t=1.73, n=32) | -23 | -495 | -7 |
| S&P 600 deletions (long) | -352 | -73 | +891 (t=1.45, n=14) | +478 |
| S&P 400 deletions (long) | +89 | +25 | +876 (t=1.13, n=6) | +456 |
| Russell 2000 additions (short) | -730 | -1,072 | -1,393 | -3,440 |
| Russell 2000 deletions (long) | n=1 | n=1 | n=1 | n=1 |

S10 validation (10,000 bootstrap/reshuffle simulations, seeded): only S&P 600 additions @10td is robust end-to-end (100% positive bootstrap means, survives stress friction and dropping the best trade, zero ruin paths). S&P 400 additions @10td is marginal-positive (p5 of bootstrap near zero). The long-deletions 40td cells fail robustness (bootstrap p5 crosses zero; best single trade drives a large share; n=14 and n=6). Russell 2000 additions are inverted (0% positive bootstrap means) - consistent with a largely permanent inclusion effect in Russell (Chang, Hong, Liskovich 2015).

**Limitations:** 2023 events excluded by the 252-session history gate (data starts 2023-03-28), so all traded events are 2024-2026 and no out-of-sample year split is possible. Russell 2000 deletions are microcap drops failing the $5M ADDV gate (largest 2025 deletion: $3.7M) - only one Russell deletion event survives. Borrow cost is modeled (flat fee base, hard-to-borrow filter stress), no borrow-fee dataset available. Capacity not measured (needs depth data, Level 2).

**Level-2 robustness (2026-08-04, cached daily bars, no new data):**

- Liquidity sweep: the short-additions edge strengthens with the ADDV gate ($2M: +461 bps t=2.77, n=96; $10M: +930 t=3.02, n=30) - no microcap dependence on liquidity.
- Year breakdown: S&P 600 additions 10td is +139 (2024, n=11), +1,542 (2025, n=19, t=3.93), **-786 (2026, n=5, t=-3.54)**. The 2025 number is one batch: the March 2025 reconstitution (11 events, +2,081 to +4,526 bps each). September 2025 is mixed, December 2025 negative. S&P 400 additions are positive in 2025-2026 (n=17 and n=5) but negative in 2024 (n=10).
- Capacity: 10 tradeable batches, $8.2M total at 1% participation, $40.8M at 5%, $81.5M at 10% of ADDV20; median batch $3.8M at 5%. Small but not the binding constraint.
- Borrow: break-even annual fee that would zero the 10td short edge is 14,657 bps (S&P 600) / 11,338 bps (S&P 400); at the 300 bps hard-to-borrow cap the edge is unchanged (+393 vs +396). Borrow is not binding at the 10-day horizon.

**Level-2 conclusion: REJECTED.** The surviving short-additions cell fails the pre-registered "result depends on a single year" gate: it is one reconstitution batch (March 2025 S&P 600). Liquidity, capacity, and borrow all pass; the year dependence is disqualifying. No leg or venue from this hypothesis advances without new evidence (longer history, other venues, independent effect confirmation).

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

1. The candidate is rejected at Level 1-2 per the registered gates. Record the rejection decision in the research spec (S11) - done 2026-08-04.
2. Revisit only with new evidence: a longer history (EQUS full dataset or another licensed source to include 2023 and pre-2023 reconstitutions), a different venue, or an independent confirmation of the effect outside the March 2025 S&P 600 batch.
3. The data pipeline (event tables, bars, study, S10, Level-2 analysis) remains reusable for any future revisit via the Makefile targets.

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
