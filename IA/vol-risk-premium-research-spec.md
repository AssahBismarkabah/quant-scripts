# Short Volatility / Variance Risk Premium — Research & Pre-Registration Specification

**Status:** Pre-research specification (exploratory scope, no probe approved yet) — 2026-08-08
**Source claim:** Andrea (a practitioner) describing short options premium as "the only true glitch in the matrix," specifically selling option premium to capture implied volatility that is systematically overpriced versus realized volatility, with named conditional setups (FOMC implied-vol spikes, earnings).
**Classification:** Options / volatility risk premium (short-vol, premium capture). Candidate mechanic.

> This is an **exploratory** research spec. It defines the question, the mechanic, the evidence, and the data reality **before** any probe is approved. A probe and strict gates would be pre-registered as a separate follow-up (or folded in here) only after the data route is confirmed.

---

## 1. The research question

Is there a pre-registerable, friction-adjusted, out-of-sample edge in **selling implied volatility** (collecting the variance/volatility risk premium) on the S&P 500 / NQ complex, using data we can verifiably own or obtain free?

Two increasingly specific sub-questions:

1. **Unconditional VRP:** Does implied variance (VIX²) systematically exceed subsequently-realized variance (the variance risk premium), and is that premium economically harvestable after costs? — testable **today with owned data**.
2. **Conditional / event premium:** Is implied volatility meaningfully overpriced specifically around **FOMC and earnings** events (the guest's named setup), and does a short-straddle/strangle premia-capture survive realistic tail risk and option-position P&L? — requires **option-price/IV history we do not own**.

The broader question for the research program: this is the first candidate we have surfaced that is a *structural* (risk-premium) edge rather than the retail-behavioral intraday flow family we keep falsifying (VWAP-pullback, IVAMR). It deserves an honest test, not a shortcut to approval.

---

## 2. The proposed mechanic (per the claim) and the honest prior

### The claim

- Investors with large equity exposure systematically buy crash protection (puts). They overpay for it because their dominant fear is market decline.
- The seller of that protection ("the insurance broker") collects option premium / implied volatility.
- Historically, implied volatility tends to exceed realized volatility, so the seller captures the difference on average (the **volatility risk premium**).
- This is structural because it monetizes persistent risk aversion, not a transient pricing error.
- The guest's concrete entry: short the **implied-vol spike** around FOMC and earnings — selling premium when expected vol is "always overpriced."

### Honest prior (caution)

- **The VRP is real but well-documented and decaying.** The most important finding for us (see §4) is Dew-Becker (2025), *The decline of the S&P 500 variance risk premium*: over the last ~17 years the VIX has become **nearly an unbiased predictor** of realized vol — the premium has largely collapsed. This is the same **edge-decay** failure class our program repeatedly encounters. A naive "always short vol" probe is likely to fail a strict gate.
- **The return distribution is violently non-normal.** Quantpedia flags short-vol strategies can lose up to −800% in single events (e.g. 1987, 2018 `volmageddon`). The win rate is high and the tail is enormous — the mirror image of the ``high-win-rate-no-edge`` traps we just disconfirmed. A rigorous test must model the tail, not just average premium.
- **Crowding/decay:** the strategy is widely monetized by every option market maker and hedge fund (short-gamma/vega, carry). The guest himself frames it as one of many edges, not a free lunch.
- **The guest is a promoter as well as a trader** (sells software, links to affiliate-funded content). "Profiting from the fear of billionaires" is marketing framing, not a mechanism. His orderflow/intraday content is the same family we have falsified. Only the **premium-capture / short-vol** claim is structurally distinct and worth our effort.

---

## 3. How this differs from what we have already falsified

| Prior candidate | Verdict | Why this is different |
|---|---|---|
| NQ VWAP-pullback | DISCONFIRMED | Directional intraday retail-flow mechanic; gross-negative. Not a risk-premium. |
| IVAMR (volume profile) | DISCONFIRMED | Behavioral intraday value-area mechanic; net-negative. Not a risk-premium. |
| SPX dealer GEX intraday | REJECTED (friction) | Gamma-regime *intraday directional* filter; died on 2.18 bps friction. |
| **Short vol / VRP (this)** | **untested** | **Sells a risky asset (vol) to collect a premium — a carry/risk-premium mechanic, structurally different.** |

The distinguishing feature: this is not a *directional move* bet; it is a *premium/insurance* bet with a positive carry and a rare, severe negative tail. It must be evaluated on its own tail-aware gates, not the intraday gates used above.

---

## 4. Research findings (literature + data pass, 2026-08-08)

### 4.A The variance risk premium is real and persistent historically, but decaying

- **Bollerslev, Tauchen, Zhou (2009), "Expected Stock Returns and Variance Risk Premia"** — establishes the VRP as `VIX² − E[realized variance]` and shows it predicts equity returns. This is the canonical definition and methodology. Sample: VIX daily 1990+.
- **Hansen, Huang, Tong, Wang (2024), "Realized GARCH, CBOE VIX, and the Volatility Risk Premium"** — closed-form link between VIX, realized vol, and the VRP.
- **Dew-Becker (2025), "The decline of the S&P 500 variance risk premium"** — **decisive caution**: shows the VIX has converged to realized volatility over ~17 years; "VIX has been nearly an unbiased predictor of realized volatility." The average premium is near zero now.
- **ECB working paper**, "The VIX, the Variance Premium and Stock Market Volatility" — models VRP from 1990; supports the premium existing but time-varying.

### 4.B The risk is tail-shaped and requires margin/loss discipline

- **Quantpedia, "Volatility Risk Premium Effect"** — short-vol (sell puts/straddles) can lose up to −800% in a single event; strong serial correlation in large negative days; needs substantial margin reserves.
- **AQR (Israelov, Nielsen)** — short-vol component historically ~1.0 Sharpe in isolation but the *implementation* embeds unintended exposures (short equity-reversal bet) that dominate risk. The naive ``sell premium, keep the carry`` is not the reviewed edge.

### 4.C Conditional / event premium is the guest's actual trade, but harder

- The FOMC/earnings "short the IV spike" setup is a real, recognized pattern (shorting event-induced IV premium). It is testable only with **option-price or IV history by strike and expiry** — which we do **not** own and which is **not freely available at scale** (see 4.D).

### 4.D Data reality — what we can test with owned/free data today vs. what needs paid data

**Owned / already on disk:**
- `research/vol-targeting/cache/VIXCLS.csv` — **CBOE VIX close, daily 1990-01-02 → 2026-07-31** (9,544 rows). This is the model-free 1-month implied-vol proxy.
- `research/vol-targeting/cache/SPY_clean_long.parquet` / `SPY_long.parquet` — **SPY daily 1993-02-01 → 2026-07-31** (8,4xx rows), OHLCV. Sufficient to compute realized variance.
- Databento NQ futures intraday (back to 2013) — the tradable instrument the guest names (NQ options), available for execution modeling.
- SPX dealer-GEX options chain data (gamma/OI) — **not** option prices/IV; not directly usable for premium capture.

**=> The unconditional VRP probe (VIX² vs realized var) is fully testable with owned data and the Bollerslev-style method, 1993→present.**

**Not freely available at scale (needed for the conditional/event/option-P&L version):**
- **CBOE DataShop Volatility Surfaces** — price/delta-relative IV surfaces from **Aug 2011**; paid subscription product.
- **OptionMetrics** (IVyDB) — full option prices/IV since 1996; academic/institutional paid license.
- **IVolatility** — EOD option prices + IV, pay-per-use (retail ≈ $0.20-0.60 per ticker/day).
- **SpiderRock** — historical IV surfaces; commercial/paid.
- **Kaggle "S&P500 Options (SPY) Implied Volatility"** — a free set, but limited horizon, unverified provenance/completeness; **not** research-grade without independent validation.

**=> The conditional/event short-straddle version (with realistic option P&L and tail risk) is NOT testable with owned data and has no reliable free full-history IV source. It would require a paid data purchase or a proxy-based approximation.** This is a documented decision point, not a silent assumption.

---

## 5. Version-one scope boundary (proposed, not yet approved)

Because the guest's headline setup requires option data we do not own, the proposed *owned-data* first probe targets the **unconditional variance risk premium**:

- **Question:** does `VIX² − realized-variance` (measured a la Bollerslev et al. 2009) represent a harvestable premium on SPY/NQ over 1993→present, after conservative costs, with correct tail handling and an IS/OOS split?
- **Signal source:** CBOE VIX (implied) vs realized variance computed from SPY daily returns.
- **Execution target:** SPY (equity) or NQ futures (index) as tradable proxies for the short-vol/hedged position.
- **Explicitly deferred (needs paid data or a proxy):** short-straddle/strangle around FOMC and earnings with realistic option P&L, skew, and tail simulation.

This scope is proposed so the spec can name data gaps without over-committing. **No probe is approved in this document.**

---

## 6. Required data

### Owned (sufficient for V1 unconditional VRP)
- CBOE VIX close (daily, 1990→present) — **owned**.
- Realized underlying: SPY daily OHLC (1993→present) or NQ futures — **owned**.
- Risk-free rate series for excess-return calculation — to be sourced (free: FRED DGS3MO / TB3MS).

### Needed (for conditional/event version)
- Option price or IV history by strike + expiry on SPX/SPY or NQ (start ~2011+ for paid surfaces).
- Event calendar: FOMC meeting dates and named-company earnings dates (mostly free; FOMC dates free from Fed).

### Data validation principles (pre-registered when a probe is approved)
- Use closing VIX and close-to-close returns; verify no look-ahead between signal date and realized window.
- Realized variance over the matching forward window (e.g. next 21/22 trading days) to align with the 1-month VIX.
- Reconcile VIX series against CBOE published history.
- Store raw immutable; record source, retrieval time, version, known limitations.

---

## 7. Minimum machine-executable model (proposed for V1)

#### Signal
`VRP_t = VIX_t² − RV_t→t+h` where `RV_t→t+h` is realized variance over the forward window (annualized `×12/252` convention per Bollerslev). The tradable signal is a **short-vol** position when the premium is positive and (for a conditional variant) when implied is elevated relative to its own history.

#### Entry / sizing
- Short the volatility position (via SPY short or hedged NQ, or a short-VRP factor proxy) only under the pre-registered regime (positive premium + term-structure / level filter).
- Size from a **tail-aware** risk budget, not from premium yield. Vol ≈ risky carry; static sizing is the classic failure.

#### Exit
- Hold to the horizon, roll, or exit on a pre-registered tail/level trigger (VIX breach, realized-vol spike). Frozen before OOS.

#### Cost model
- Conservative friction for the chosen instrument (SPY: spread+commission+SEC; NQ: tick/commission).
- Short-vol risk requires modeling the **bad tail** — margin, financing, and a realized-vol spike that marks the position down. Preferred: compute on a proxy that captures the move, then stress the tail separately.

#### Rejection gates (to be frozen at probe time)
Reject if any of:
1. Fails a pre-registered net-of-cost edge threshold (e.g. significant positive mean VRP) — **especially if only significant pre-2009** (decay evidence says it collapsed).
2. Profit originates solely from a handful of extreme premium periods (pre-2010) and is absent in the modern OOS window.
3. Bootstrap/Monte-Carlo p5 ≤ 0 or draws-down/ruin unacceptable, given the −800%-class tail.
4. The look-ahead / stale-data audit fails.
5. Result depends on one window, one convention (12 vs 21-day RV), or one asset.

---

## 8. Decision points / open questions

- **Choice of underlying for V1:** SPY (realized vol source, simple) vs NQ futures (guest's actual instrument, harder). SPY is the natural first pass; NQ is the deployment instrument.
- **Whether to attempt a free-data conditional probe** (FOMC/earnings) using the Kaggle SPY-IV set + our own bars **only** if its provenance and completeness pass validation — otherwise treat as paid-data-gated.
- **Whether the VRP decay finding (Dew-Becker) is treated as prior that the modern OOS should fail** — i.e. the probe's real value is to confirm or refute the decay on our own data, not to produce a deployable edge.
- **Which IV proxy** if we ever need options P&L: CBOE surfaces (paid, 2011+) are the cleanest route; OptionMetrics if academic license available.

---

## 9. What we are deciding

This document moves the short-vol / variance-risk-premium claim from "guru sells it, sounds structural" to **a scoped, data-grounded candidate** with:

1. a real owned-data first probe (unconditional VRP, 1993→present) that **can** be run now;
2. an honest prior that the modern premium has **decayed toward zero** (so a clean disconfirmation is a plausible, valuable outcome);
3. a clear record that the **conditional FOMC/earnings short-straddle version is not testable with owned data** and needs paid IV history.

The decision this document produces is: **whether to approve the owned-data VRP probe, and whether to treat the event version as paid-data-gated.** A failed probe is a successful research outcome — it prevents capital being allocated to a "glitch" story that is likely already harvested-and-decayed.

---

## 10. Status

- **2026-08-08:** Spec drafted (exploratory). Source identified from a trader interview (short-vol / variance risk premium; FOMC/earnings event setup). Literature + data pass complete: VRP documented (Bollerslev 2009; Hansen et al. 2024), **decay** documented (Dew-Becker 2025), tail risk documented (Quantpedia; AQR). Data reality established: **owned** VIX (1990+) + SPY (1993+) make the unconditional VRP probe runnable now; **no free full-history option/IV data** makes the conditional event version paid-data-gated.
- **Next (not yet done):** user decision on §8 open questions; pre-register the V1 probe's frozen gates and split only if the owned-data probe is approved.
