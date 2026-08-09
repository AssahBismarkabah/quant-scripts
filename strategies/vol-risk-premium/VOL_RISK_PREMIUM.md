# Short Volatility / Variance Risk Premium (VRP)

**Version:** 1.3
**Status:** DISCONFIRMED (2026-08-08) - short-vol / VRP claim fully tested and closed. V1: level positive (+3.3..+4.1 vol pts). V2: naive harvest is ruin (+452% but −95% DD, −83% single day). V3: a stress-overlay fix FAILS — it flees the premium-rich regimes (skipped +646%, kept −26%), proving the tail can't be dodged without killing the harvest. Candidate CLOSED. Full spec: `IA/vol-risk-premium-research-spec.md`; V3 design: `V3_TAIL_OVERLAY.md`.
**Classification:** Options / Variance Risk Premium (short-vol, premium capture / carry)
**Source claim:** practitioner interview (Andrea) — "short options premium / profiting from the fear of billionaires," specifically selling implied volatility when it is overpriced, with FOMC and earnings "short the IV spike" setups.

## 1. Executive Summary

This document records the candidate for **collecting the volatility risk premium** — selling implied volatility (via options/vol exposure) to harvest the systematic tendency of implied vol to exceed realized vol. It is the first candidate in this program that is a *structural risk-premium* edge rather than a retail-behavioral intraday mechanic.

**Current status: DISCONFIRMED.** V1 (owned VIX+SPY) confirmed the VRP *level* is positive and persistent. V2 (free SVXY data, including the 2018 volmageddon and 2020 COVID tails) showed it is **not a harvestable edge**: buy-and-hold long short-vol returned +452% but with a **−82.96% single-day loss (2018-02-06)** and a **−95.25% max drawdown**; the regime gate barely helped (−90.9% DD) because premium is richest right before the crash. Per the frozen tail-survival gate, this is ruin risk, not an edge. **NOT approved to trade; candidate CLOSED.**

**Data note (corrected 2026-08-08):** all versions of the claim are testable with owned + **free** data — the short-vol P&L and conditional FOMC/earnings versions use **free short-vol ETPs (SVXY/VXX, Yahoo), free CFE VIX futures (2004+), and a free SPY EOD options dataset (2010-2023, Kaggle)**. No paid data is required; an earlier assessment that the event version needed paid IV data was wrong (see spec §4.D correction).

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

## 6. Data (owned vs free — corrected 2026-08-08)

**Unconditional VRP — owned:**
- `research/vol-targeting/cache/VIXCLS.csv` — CBOE VIX close, daily 1990-01-02 → 2026-07-31 (FRED, free).
- `research/vol-targeting/cache/SPY_long.parquet` / `SPY_clean_long.parquet` — SPY daily 1993-02 → 2026-07 (Yahoo, free).
- Databento NQ futures (2013+) for execution modeling.

**Short-vol P&L — free:**
- **SVXY** (short-vol ETP, −1× VIX short-term futures) and **VXX** (long-vol), free via Yahoo; simulated XIV/VXX backtests to 2004 available free.
- **CFE VIX futures** per-contract history 2004+ — free from CBOE futures historical data page (term structure / contango signal).

**Conditional / event options version — free (source of record):**
- **OptionsDX SPY Option Chains** — free ($0), full SPY chains 2010-2023 (all strikes × expiries, bid/ask/last, IV, Greeks, OI). Verified directly.
- **Kaggle "SPY Options EOD 2010-2023"** (MIT) — ready Parquet copy of the OptionsDX chains; **Kaggle SPY IV 2014-25** (CC0).
- **Cleaning method:** free arXiv paper (2501.11164, Visagie) — model-free procedure to strip arbitrage/outlier/duplicate prices from the recorded chains before backtesting.
- **VIX Options:** OptionsDX sells VIX chains at $0-20/yr (cheap/free); CBOE DataShop is the premium alternative.

**=> No paid data required for any version.** OptionsDX (primary), CFE VIX futures, and short-vol ETPs plus VIX/SPY (owned) cover all three versions. Paid professional IV surfaces / tick-level OPRA options are optional polish only. Free option-chain files must be run through the arXiv cleaning procedure and validated for completeness before use.

## 7. Validation & Rejection Gates (draft — to be frozen at probe time)

Reject if any:
1. Net-of-cost VRP is not significantly positive in the modern OOS window (premium decayed) — especially if only pre-2009.
2. Profit comes only from a handful of extreme premium periods absent in the modern window.
3. Bootstrap/Monte-Carlo p5 ≤ 0, or drawdown/ruin unacceptable given the −800%-class tail.
4. Look-ahead / stale-data audit fails.
5. Result depends on one window, one convention, or one asset.

## 8. Go / No-Go and Decision Points

The exploratory spec (`IA/vol-risk-premium-research-spec.md`) documents the decision points: underlying choice (SPY vs NQ) for V1; which of the three free-data versions to run first (unconditional VRP, short-vol ETP/VIX-futures P&L, or conditional FOMC/earnings via free SPY EOD options); and validation of the free Kaggle options set. **No probe is approved until those are resolved, the free data is validated, and gates are pre-registered.**

## 9. Verified Status

- **2026-08-08:** Spec + strategy record created (exploratory). Data route confirmed via primary sources the same day: **OptionsDX SPY Option Chains ($0, 2010-2023)** + a free arXiv cleaning method (2501.11164) + free short-vol ETPs / CFE VIX futures make the candidate testable with no paid data.
- **2026-08-08 (later):** **V1** (owned VIX+SPY): VRP level positive all eras → not an edge by itself.
- **2026-08-08 (later):** **V2** (free SVXY): naive short-vol +452% but −95% DD → **DISCONFIRMED** (tail).
- **2026-08-08 (later):** **V3** (free SVXY + CBOE VIX/VIX3M/VIX9D term-structure overlay): overlay bounded the tail (62%) but **destroyed the harvest** (skipped +646% of the premium, kept −26%) → **DISCONFIRMED**. The stress-overlay flees the premium-rich regimes.
- **This candidate is CLOSED.** The short-vol / VRP "glitch" is a real premium *level* that is not tradeable: naive capture is ruin, and the natural tail-overlay fix kills the edge. No remaining branch warrants pursuit absent a materially different mechanism.

- This is a **candidate spec**, not an approved strategy. Treating it as approved before the data route is validated (esp. the free Kaggle options set) and gates are pinned would repeat the pattern of every prior candidate this program has disconfirmed.
