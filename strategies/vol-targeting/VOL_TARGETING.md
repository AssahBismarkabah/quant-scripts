# Target Volatility Fund Rebalancing Flow Fade

**Version:** 1.0
**Status:** First-pass complete (2026-08-04) - candidate REJECTED: H1 (fade) fails at the base cell after friction, split sample shows opposite signs, and the flow construction misses the window's biggest deleveraging episode (Aug 2024)
**Classification:** Flow-Driven / Forced-Deleveraging Fade (Category 1: Mathematical Mandates)

## 1. Executive Summary

This document records the investigation of target volatility fund rebalancing flows as a daily-frequency forced-flow fade. The hypothesis: vol-targeting funds (vol-target funds, risk parity, vol-managed variable annuities, systematic CTAs) are mandated to scale exposure inversely to forecast volatility — `exposure = target_vol / forecast_vol x AUM` — so every volatility move forces a mechanical flow. Large forced-sell days create temporary price impact that partially reverts within 1-5 days.

**Result:** Tested at first pass, then **rejected**. The literature confirmed the flows are real and enormous (single-day flows of -$29B to -$61B, 30-41% of SPX futures notional, per Barclays 2015; up to $2T in vol-strategy AUM per ECB 2020) and contractually forced. But the pre-registered test failed three gates: (1) the primary fade cell (hold 1 day, after base friction) is **-5.62 bps** (t=-0.14, bootstrap p_negative=0.56); (2) the split sample shows opposite signs (IS -5.44 / OOS +3.87 bps); (3) the flow construction fails the episode sanity check — the Aug 2024 vol spike (the window's biggest) ranks only 205/839 in flow magnitude. The flows exist; the daily-bar 20d-RV proxy does not extract them at tradable fidelity, and the extracted flows show no 1-day reversion after friction. A 5-day fade hint (+44 bps raw, t=1.58) is recorded, not chased. See section 6.

## 2. The Economic Edge

### The Why

Volatility-targeting strategies keep portfolio risk roughly constant by scaling exposure inversely to a volatility forecast. The scaling is rule-driven and non-discretionary: when forecast vol rises, the fund MUST sell; when it falls, the fund MUST buy. Deleveraging is fast (immediate selling into a falling market); releveraging is slow. The flows are procyclical and clustered because many funds use similar rules. Harvey et al. (2018, JPM) document the mechanics across 60+ assets; the ECB (May 2020 FSR) documents the procyclicality and quantifies risk-parity equity cuts in March 2020.

### The Counterparty

The counterparties are vol-target funds, risk-parity funds, vol-managed variable annuities, and systematic CTAs. They are not trading against us deliberately — they are fulfilling a mandate. This is Category 1 (mathematical constraint): the trade is contractually required and replenished every time volatility moves. Stronger than a behavioral premium (Category 4) and not dependent on a vendor's derived positioning data (unlike SPX GEX).

### The Trade

| Leg | Entry | Direction | Evidence |
|---|---|---|---|
| Fade forced sell-flow days | Open of first day after a bottom-decile sell-flow day | Long, hold 1-5 days | Feb 2018: SPX -4.1% then recovered; Mar 2020: V-bottom; Aug 2024: VIX 65 intraday spike then equity recovery; CBOE/Onali et al. document the forced-flow mechanics |
| Fade forced buy-flow days | Open of first day after a top-decile buy-flow day | Short (secondary, pre-registered as reported-not-traded in v1) | Releveraging is slow and gradual; buy flows are expected to be weaker signals — v1 trades only the sell side |

### Decay Warning

The alpha side of volatility management is contested out of sample (Cederburg, O'Doherty, Wang, Yan 2020; Bongaerts, Kang, van Dijk 2020): spanning alphas do not survive as implementable OOS strategies. The flow side is different — it is a mandate, not a behavioral premium — but the same OOS skepticism applies to any daily-frequency effect. The candidate is therefore tested under strict pre-registered gates, including a split-sample same-sign requirement and single-episode independence. No published daily fade edge was found; the question is open.

## 3. Machine-Executable Rules

### 3.A Event Definition

- Universe: S&P 500 proxy (SPY, fallback IVV), daily bars 2023-03-28 -> present (EQUS.MINI).
- Signal at close of day t: forecast_vol_t = 20d realized vol of SPY (base); exposure_t = min(cap, target / forecast_vol_t) x AUM; flow_t = exposure_t - exposure_{t-1}.
- Event day t = a day whose flow_t is in the bottom decile of the in-sample flow distribution (large forced sell).
- Base parameters (frozen): 20d RV, 10% vol target, 1.5x leverage cap, $1.0T AUM (constant), bottom-decile threshold.
- Robustness grid (reported, not selected): vol window {10, 60}, vol measure {EWMA 0.94, VIX}, AUM {$0.5T, $2T}, target {8%, 12%}, cap {1.0x, 2.0x, uncapped}, holding {2, 5} days.

### 3.B Entry

- Enter long at the open of day t+1 (signal known at t close; no look-ahead).
- Pre-registered primary H1: mean return from t+1 open > 0 after base friction (fade). H2 (continuation, mean < 0) is reported but is not a fallback: if H1 fails at the base cell, the candidate is rejected; the sign is not re-selected ex post.

### 3.C Exit

- Exit at end of planned holding window: 1, 2, or 5 trading days (grid).
- Pre-registered stop loss: -2% from entry.
- Force-close and record on data gaps.

### 3.D Position Sizing

- Equal-risk-weight per event, sized from the lower of portfolio risk budget, volatility target, and ES/SPY executable depth.
- Capacity: report position vs ES daily volume; documented flows of $30-60B/day confirm the complex far exceeds our scale.

## 4. Friction Model

| Cost | Base Case | Stress Case |
|---|---|---|
| Spread crossing | ~1.0 bps/side | ~3.0 bps/side (high-vol days) |
| Slippage | ~0.9 bps/side | ~2.9 bps/side |
| Exchange fees | ~0.1 bps/side (ES) | Same |
| Round trip | **4.0 bps** | **12.0 bps** |

Borrow: N/A (futures proxy). Execution at t+1 open, not mid/close.

**Registration:** Rejection if the base case does not clear 4 bps round trip. Stress case reported alongside.

## 5. Research Scope

- Signal source: public data only — SPY daily bars (EQUS.MINI) + VIX (FRED VIXCLS, robustness) + published AUM estimates
- Execution proxy: ES futures via SPY bars
- Horizon: 1-5 trading days after a forced sell-flow day
- Data route: Databento EQUS.MINI (existing pipeline) + FRED VIXCLS (free)
- First-pass design: daily event study, t+1 open entry, fixed holding grid, base + stress friction, S10-style bootstrap/reshuffle
- Excluded: intraday execution, options-based signals, single-stock flows, buy-flow shorting in v1

## 6. First-Pass Test Results

**Complete (2026-08-04).** Study implemented in `research/vol-targeting/` (run_study.py + Makefile), SPY daily bars from EQUS.MINI cache (839 sessions, 2023-03-28 -> 2026-08-01), flow constructed per the pre-registered base cell (20d RV, 10% target, 1.5x cap, $1.0T AUM constant), events = IS-trained bottom-decile flow days (73 events: 43 IS / 30 OOS).

- Same-day diagnostic: corr(flow, ret) = +0.15 — flows are procyclical (negative on down days), PASS. (Note: the spec's stated expected sign was corrected to positive; procyclical flows move with the market.)
- **Primary cell H1 (fade, hold 1 day): FAIL.** Mean hold1 = -1.62 bps raw, **-5.62 bps net of base friction** (t = -0.14, n = 73); -13.62 bps net of stress friction. Bootstrap (10k, seeded): p5 = -21 bps, p_negative = 0.56. Drop-best-day: -7.95 bps. Random-day control: +19.58 bps (events underperform random days).
- Split sample: IS -5.44 bps (n=43) vs OOS +3.87 bps (n=30) — **opposite signs**, fails the same-sign gate.
- Robustness grid (vol window x AUM x target x cap, 16 cells): base corner (vw=20) negative; all vw=60 cells positive (~+23 bps), vw=10 mixed. Effect flips with the vol window — single-corner dependence. AUM is fully scale-invariant (identical results at $0.5T and $2.0T, as predicted).
- Sanity/episode check: **Aug 2024 vol spike (VIX ~65 intraday) ranks only 205/839 in flow magnitude (-$16B)** — the 20d-RV construction misses the window's biggest deleveraging episode because realized vol was already elevated (17.3%) pre-spike; the top flow days are cap-threshold crossings from deep-calm states (2025-10-10: -$783B, 2024-12-18: -$667B). Apr 2025 tariff shock ranks 25/839 (-$113B).
- Non-result worth recording: hold5 mean = +44 bps raw (t=1.58, ALL), +74 bps (t=1.49, OOS). A fade hint at 5 days, but not significant, not the pre-registered primary, and not tested further — per the no-horizon-selection rule.

**First-pass conclusion: REJECTED.** Three independent gate failures: (1) H1 fails at the base cell after base friction (-5.62 bps, t=-0.14, bootstrap p_negative=0.56); (2) split sample opposite signs (IS -5.44 / OOS +3.87); (3) the flow construction fails the episode sanity check (Aug 2024 not a large flow day). The documented flows are real (ECB/IMF/Barclays) but the daily-bar 20d-RV proxy does not extract them at tradable fidelity, and the extracted flows show no reversion at the 1-day horizon after friction. The 5-day hint is recorded, not chased.

## 7. Rejection Gates

Reject if any of the following is true:
- Same-day diagnostic fails (flow days do not coincide with down days)
- H1 (fade) fails at the base cell after base friction — no sign-switching
- Effect does not survive the split sample with the same sign in both halves
- Effect depends on a single episode (Aug 2024 or Apr 2025)
- Effect depends on a single robustness corner
- Bootstrap p5 of the mean not positive; reshuffle or drop-best destroys the effect
- Result disappears when entry shifts from t+1 open to t+1 close
- Base-case friction gate fails
- Capacity not credible at the intended scale

## 8. Next Step

1. The candidate is rejected at first pass per the registered gates. Record the decision in the research spec (S11-equivalent) - done 2026-08-04.
2. Revisit only with new evidence: a higher-fidelity flow construction (implied-vol/EWMA-driven signals that would capture Aug 2024-class events; VIX-based exposure is testable with free FRED data), or intraday data to see the flow in the close itself. Any revisit requires a NEW pre-registration; the 20d-RV base cell is closed.
3. The scaffold (run_study.py, Makefile, cached SPY bars) remains reusable via `make study`.

## 9. Key References

- Moreira and Muir (2017), "Volatility-Managed Portfolios", Journal of Finance 72(4):1611-1644 — the foundational vol-targeting result (in-sample alphas; the alpha side we do NOT claim)
- Cederburg, O'Doherty, Wang, and Yan (2020), "On the performance of volatility-managed portfolios", JFE — OOS skepticism on the alpha side
- Bongaerts, Kang, and van Dijk (2020), "Conditional Volatility Targeting", FAJ — international OOS evidence and turnover costs
- Harvey, Hoyle, Korgaonkar, Rattray, Sargaison, and Van Hemert (2018), "The Impact of Volatility Targeting", JPM 45(1):14-33 — mechanics and tail reduction across 60+ assets
- ECB Financial Stability Review (May 2020), "Volatility-targeting strategies and the market sell-off" — AUM and procyclical deleveraging
- IMF GFSR (Oct 2017), Figure 1.21 — AUM by fund type
- Barclays Research (2015) via The Actuary Magazine — daily flows 30-41% of SPX futures notional
- CBOE (2018), "After the Volpocalypse" — XIV/SVXY forced-covering mechanics
- Onali et al. (2021), "Volmageddon and the Failure of Short Volatility Products", FAJ — leverage-rebalancing feedback loop
- NY Fed (Logan, 2020) — March 2020 levered-account deleveraging
- CCMR NBTF (2022), "The U.S. Treasury Market During the COVID-19 Crisis" — March 2020 selling and reversion
