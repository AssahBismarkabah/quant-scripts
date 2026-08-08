# Short Volatility / Variance Risk Premium (VRP)

**Version:** 1.0
**Status:** Candidate — exploratory spec only, NO probe approved yet (2026-08-08). Pre-registered probe + strict gates pending user decision. See `IA/vol-risk-premium-research-spec.md`.
**Classification:** Options / Variance Risk Premium (short-vol, premium capture / carry)
**Source claim:** practitioner interview (Andrea) — "short options premium / profiting from the fear of billionaires," specifically selling implied volatility when it is overpriced, with FOMC and earnings "short the IV spike" setups.

## 1. Executive Summary

This document records the candidate for **collecting the volatility risk premium** — selling implied volatility (via options/vol exposure) to harvest the systematic tendency of implied vol to exceed realized vol. It is the first candidate in this program that is a *structural risk-premium* edge rather than a retail-behavioral intraday mechanic.

**Current status: NOT proven, NOT approved.** The exploratory research spec is written. Key finding: the unconditional VRP is testable **now with owned data** (VIX 1990+ and SPY 1993+), but the premium is **well-documented as decaying toward zero over the last ~17 years** (Dew-Becker 2025), and the conditional FOMC/earnings options version needs **option-price/IV history we do not own**. The `strategies/spx-gex` dealer-gamma candidate (the closest prior options work) was already rejected at the friction gate.

## 2. The Economic Edge (the claim)

The proposed source of return is the **volatility risk premium**:

`VRP = implied-variance − expected-realized-variance ≈ VIX² − RV(forward)`

Investors with large equity exposure systematically buy crash protection and overpay for it (fear dominates). The seller of that protection collects option premium / implied vol. On average implied vol exceeds realized vol, so the seller captures the difference.

The guest's concrete conditional setup: **short the implied-vol spike around FOMC and earnings** — sell the insurance when the "fire is already going on" and insurance is expensive, expecting vol to mean-revert.

## 3. Why this is different from what we disconfirmed

| Prior | Verdict | Contrast |
|---|---|---|
| NQ VWAP-pullback | DISCONFIRMED | Directional intraday move bet, gross-negative. Not a risk premium. |
| IVAMR | DISCONFIRMED | Directional intraday volume-profile bet, net-negative. Not a risk premium. |
| SPX dealer-GEX intraday | REJECTED (friction) | Gamma-regime *directional* intraday filter; died on 2.18 bps friction. |
| **Short-vol / VRP (this)** | **untested** | Sells a risky asset (vol) for premium — a **carry / insurance** bet with high win rate and a rare, severe negative tail. |

It must be assessed with **tail-aware** gates, not the intraday gates used on the directional candidates.

## 4. Empirical / literature evidence

- **VRP exists:** Bollerslev, Tauchen, Zhou (2009) define `VIX² − E[RV]` and show it predicts equity returns. Hansen et al. (2024) formalize VIX/VRP. ECB (2014) models it from 1990.
- **VRP has decayed:** Dew-Becker (2025), *The decline of the S&P 500 variance risk premium* — over the last ~17 years the VIX has become **nearly an unbiased predictor** of realized vol; the premium has largely collapsed. A naive "always short vol" claim is likely to fail a strict modern OOS gate.
- **Tail risk is extreme:** Quantpedia notes short-vol can lose up to −800% in a single event; strong serial correlation in large negative days; large margin reserves needed. AQR (Israelov/Nielsen) shows naive short-vol nets unintended (equity-reversal) exposures that dominate risk.
- **Crowding:** monetized by every option market maker and hedge fund. The "glitch" framing is marketing; the mechanic is widely known.

## 5. Machine-Executable Model (proposed for V1 — not yet frozen)

**Signal:** `VRP_t = VIX_t² − RV_{t→t+h}` (realized variance over the forward window, annualized, a la Bollerslev). Short the vol position only under a pre-registered positive-premium regime with a level/term-structure filter.

**Sizing:** tail-aware risk budget (vol is risky carry; static sizing is the classic failure mode). Never size from premium yield alone.

**Exit:** fixed horizon/roll, or a pre-registered tail/level trigger (VIX breach, realized-vol spike). Frozen before OOS.

**Cost model:** conservative friction for the chosen instrument (SPY or NQ). Model the bad tail explicitly: margin, financing, realized-vol spike marking the position down.

## 6. Data (owned vs needed)

**Owned (sufficient for the unconditional VRP probe):**
- `research/vol-targeting/cache/VIXCLS.csv` — CBOE VIX close, daily 1990-01-02 → 2026-07-31.
- `research/vol-targeting/cache/SPY_long.parquet` / `SPY_clean_long.parquet` — SPY daily 1993-02 → 2026-07.
- Databento NQ futures (2013+) for execution modeling.

**Needed but NOT owned (for the conditional FOMC/earnings short-straddle version):**
- Option prices / IV by strike + expiry (SPX/SPY or NQ). Free-at-scale source does not exist; CBOE DataShop surfaces (2011+, paid), OptionMetrics, IVolatility (pay-per-use), SpiderRock (commercial). Paid-data decision required.

**=> Unconditional VRP: testable today with owned data. Conditional event options version: paid-data-gated.**

## 7. Validation & Rejection Gates (draft — to be frozen at probe time)

Reject if any:
1. Net-of-cost VRP is not significantly positive in the modern OOS window (premium decayed) — especially if only pre-2009.
2. Profit comes only from a handful of extreme premium periods absent in the modern window.
3. Bootstrap/Monte-Carlo p5 ≤ 0, or drawdown/ruin unacceptable given the −800%-class tail.
4. Look-ahead / stale-data audit fails.
5. Result depends on one window, one convention, or one asset.

## 8. Go / No-Go and Decision Points

The exploratory spec (`IA/vol-risk-premium-research-spec.md`) documents the decision points: underlying choice (SPY vs NQ) for V1; whether to attempt a free-data conditional probe only if the Kaggle SPY-IV set validates; and whether to treat the event version as paid-data-gated. **No probe is approved until those are resolved and gates are pre-registered.**

## 9. Verified Status

- **2026-08-08:** Spec + strategy record created (exploratory). No code written, no probe run, no approval. Candidate is documentation-ready, not test-ready.
- This is a **candidate spec**, not an approved strategy. Treating it as approved before the data route and gates are pinned would repeat the pattern of every prior candidate this program has disconfirmed.
