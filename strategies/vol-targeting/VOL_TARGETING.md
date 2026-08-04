# Target Volatility Fund Rebalancing Flow Fade

**Version:** 2.0
**Status:** Second-pass (revisit) complete (2026-08-04) - candidate REJECTED at the pre-registered bootstrap p5 gate in BOTH co-base cells (A: 60d RV, B: VIX close). All other gates passed, including the episode check that failed in v1. v1's rejection stands on verified data; v1's recorded split-sample and episode failures were artifacts of a corrupted bar cache (see section 6.A).
**Classification:** Flow-Driven / Forced-Deleveraging Fade (Category 1: Mathematical Mandates)

## 1. Executive Summary

This document records the investigation of target volatility fund rebalancing flows as a daily-frequency forced-flow fade. The hypothesis: vol-targeting funds (vol-target funds, risk parity, vol-managed variable annuities, systematic CTAs) are mandated to scale exposure inversely to forecast volatility — `exposure = target_vol / forecast_vol x AUM` — so every volatility move forces a mechanical flow. Large forced-sell days create temporary price impact that partially reverts within 1-5 days.

**Result:** Tested at first pass, then **rejected**. The literature confirmed the flows are real and enormous (single-day flows of -$29B to -$61B, 30-41% of SPX futures notional, per Barclays 2015; up to $2T in vol-strategy AUM per ECB 2020) and contractually forced. But the pre-registered test failed three gates: (1) the primary fade cell (hold 1 day, after base friction) is **-5.62 bps** (t=-0.14, bootstrap p_negative=0.56); (2) the split sample shows opposite signs (IS -5.44 / OOS +3.87 bps); (3) the flow construction fails the episode sanity check — the Aug 2024 vol spike (the window's biggest) ranks only 205/839 in flow magnitude. The flows exist; the daily-bar 20d-RV proxy does not extract them at tradable fidelity, and the extracted flows show no 1-day reversion after friction. A 5-day fade hint (+44 bps raw, t=1.58) is recorded, not chased. See section 6.

**Revisit (v2) result:** Tested at second pass, then **rejected at the statistical gate**. The revisit re-built the flow on the volatility measures the complex actually uses — 60-day realized vol (IMF GFSR Oct 2017 documented construction) and the VIX close (Bhansali-Harris 2018 documented input) — with a pre-registered 5-day horizon and a joint gate (BOTH cells must pass). Both constructions now capture the Aug 2024 and Apr 2025 deleveraging episodes (v1's failure mode fixed) and produce uniformly positive fade point estimates: hold5 net-of-base-friction **+37.75 bps (Cell A)** and **+31.92 bps (Cell B)**, same-sign split samples, robust to drop-best, random-day control, t+1-close entry, and single-episode dependence; the robustness grid is positive in 36/36 cells at 3/5/10-day horizons. But the pre-registered bootstrap gate fails in both cells: the one-sided 95% lower bound of the mean (p5) is **-4.84 bps (A)** and **-5.39 bps (B)**. The candidate is therefore rejected as unproven — the positive point estimates are recorded as a hypothesis, not an edge. Additionally, data verification for v2 found the v1 bar cache was corrupted on 35/839 days; v1 re-run on verified bars still rejects (hold1 negative), so v1's conclusion stands. See sections 6.A and 7.

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

### 6.A Data-integrity re-run on verified bars (2026-08-04)

The v2 pre-registration required verifying SPY bar quality against a second source before coding. The verification (FRED SP500 + Yahoo daily bars, cross-checked three ways) found the cached EQUS.MINI SPY bars used in v1 were **corrupted on 35 of 839 sessions (4.2%)** — days where the cached close deviates >0.5% from both independent sources, including the biggest event days: 2025-04-02 (-349 bps level error), 2026-04-07 (+220), 2025-04-22 (+178), 2025-05-28 (+151), 2025-04-08 (-121), 2024-08-05 (+107). The two clean sources agree tightly (Yahoo vs SPX/10: std 11 bps, max 0.5%; cached vs SPX/10: std 27 bps, min 0.96).

v1 was therefore re-run on the verified series (`make study-v1-clean`, `research/vol-targeting/cache/SPY_clean.parquet`):

- **H1 (hold1) rejection STANDS:** -3.23 bps raw, **-7.23 bps net base** (t=-0.31, n=77, bootstrap p_negative=0.63). Same-day diagnostic +0.18, PASS.
- **Split-sample failure was a data artifact:** on clean bars IS -3.93 / OOS -2.34 — SAME sign (both negative). The effect is still not a fade, but the recorded sign-flip gate failure no longer holds.
- **Episode failure was a data artifact:** on clean bars Aug 5 2024 is a bottom-decile sell-flow day (flow -$79B, percentile rank 0.046); Apr 4 2025 ranks 0.048. The 20d-RV construction does capture the episodes; the corrupted bars hid them.
- Top flow days remain cap-threshold crossings from deep-calm states (2024-12-18 -$713B, 2025-10-10 -$635B) — the structural limitation of a 20d window with a low cap.
- The 5-day hint is stronger on clean bars: hold5 +37.8 bps (t=1.49), OOS +62.4 bps (t=1.57).

**Implication:** v1's overall rejection stands (H1 negative at the 1-day horizon either way), but two of its three recorded gate failures were artifacts of the corrupted cache. All v2 work uses the verified `SPY_clean.parquet` (Yahoo OHLC; DB volume attached, unverified, for capacity reporting only).

## 7. Second-Pass (v2) Test Results

**Complete (2026-08-04).** Pre-registered in `IA/vol-targeting-revisit-research-spec.md` (v2.0). Study: `research/vol-targeting/run_study_v2.py` (`make study-v2`). Data: `SPY_clean.parquet` + FRED VIXCLS (aligned 839/839 sessions).

Co-base cells with a joint gate (BOTH must pass, no selection):
- **Cell A (realized):** exposure = min(2.0, 0.10 / sigma60) x $1.0T, sigma60 = 60-day realized vol (IMF GFSR Oct 2017 documented construction).
- **Cell B (implied):** exposure = min(2.0, 0.10 / VIX) x $1.0T, VIX in decimal (Bhansali-Harris 2018 documented input; The Actuary/Barclays 2015).
- Events: IS-trained bottom-decile flow days (Cell A: 79 events, 39 IS / 40 OOS; Cell B: 80 events, 45 IS / 35 OOS). Entry t+1 open. Primary horizon 5 trading days. Friction 4 bps RT base / 12 bps RT stress. Stop -2% (reported).

| Pre-registered gate (each cell) | Cell A | Cell B | Verdict |
|---|---|---|---|
| Same-day diagnostic corr(flow, ret) > 0 | +0.121 | +0.750 | PASS |
| Episode check: Aug 5 2024 AND Apr 4 2025 in bottom decile | ranks 0.006 / 0.009 | ranks 0.005 / 0.012 | PASS — v1 failure mode fixed |
| H1: hold5 mean > 0 after base friction | +37.75 bps | +31.92 bps | PASS |
| Split sample, same sign (IS / OOS) | +44.9 / +38.7 | +41.2 / +29.2 | PASS |
| Bootstrap p5 > 0 (10k, seeded 42) | **-4.84 bps** | **-5.39 bps** | **FAIL** |
| Drop-best survives | +30.55 bps | +24.80 bps | PASS |
| Beats random-day control | 41.75 > 36.62 | 35.92 > 9.59 | PASS |
| t+1 close entry shift (timing fragility) | +41.18 bps | +25.03 bps | PASS |
| Single-episode independence | +28.6 w/o Aug-24 / +32.7 w/o Apr-25 | +28.0 / +24.9 | PASS |

Primary hold5 detail: raw +41.75 bps (t=1.46) / +35.92 (t=1.42); net stress +29.75 / +23.92; stop-adjusted +38.35 / +34.87; bootstrap p_negative 0.073 / 0.075.
Horizons (reported, not selected): hold3 +25.3 / +40.1; hold5 +41.8 / +35.9; hold10 +94.6 / +99.2 bps.
Robustness grid (36 cells: vol windows 30/60/120 + EWMA 0.94, caps 1.5/2.5/uncapped, AUM $0.5T/$2T, targets 8%/12%): **36/36 positive at all three horizons**; AUM scale-invariance confirmed again.
Top sell-flow days are now vol events, not cap crossings: Cell A includes 2025-04-03/04/09 and 2024-08-05; Cell B includes 2024-08-05 (-$168B), 2025-04-03 (-$132B), 2024-09-03, 2026-01-20, 2024-12-18.

**Second-pass conclusion: REJECTED at the pre-registered bootstrap p5 gate in BOTH cells.** All other gates pass, including the v1 failure mode (episode check) and joint consistency across the two independently documented constructions. Point estimates are uniformly positive (+24 to +42 bps at hold5; 36/36 grid cells positive at 3/5/10 days), but the pre-registered statistical threshold is not met: the one-sided 95% lower bound of the event-return mean is negative in both cells (-4.8 / -5.4 bps; t ~1.4-1.5). Per the no-sign-switching / no-horizon-switching / no-cell-selection rule, the candidate is rejected as unproven. The positive point estimates and the stronger hold10 (+94/+99 bps, pre-registered as reported-not-selected) are recorded as a hypothesis for a future pre-registered revisit with more data — not as an edge.

## 8. Rejection Gates

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

## 9. Next Step

1. The candidate is rejected at second pass per the registered gates (bootstrap p5 in both cells). Recorded in this document and in the v2 research spec - done 2026-08-04.
2. The v2 construction itself is validated as a flow measure (episode check passes, same-day diagnostic passes, flows are vol-event-driven, not cap-crossings) — that part of the hypothesis is no longer in question. What failed is the statistical significance of the fade at the 5-day horizon on ~80 events.
3. A further revisit requires a NEW pre-registration. Registered options, in order of defensibility: (a) extend the sample (the window contains only two stress episodes; the effect and its uncertainty need more events); (b) pre-register the 10-day horizon, whose point estimate (+94/+99 bps) is stronger but was reported-not-selected in v2; (c) intraday data to see the flow in the close itself. No option is approved; all require a new spec.
4. Data note: all future work on this candidate must use the verified `research/vol-targeting/cache/SPY_clean.parquet` series, not the corrupted EQUS.MINI cache (see 6.A).

## 10. Key References

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

### v2 references (construction evidence; full register in the v2 spec)

- IMF GFSR (Oct 2017), Figure 1.21 + footnote — the documented 60-day realized-vol construction of the vol-target complex (leverage range 1-2.5x, targets 8-15% by fund type)
- Bhansali and Harris (2018), "Everybody's Doing It: Short Volatility Strategies and Shadow Financial Insurers", FAJ 74(2):12-23 — the ~$1.5T vol-contingent complex; VIX as a major input
- BIS Bulletin No. 90 (Aquilina, Lombardi, Schrimpf, Sushko, 2024) — Aug 2024 deleveraging amplification
- SEC DERA Working Paper 2504 (2025) — Aug 5 2024 VIX index spike partly a construction artifact; VIX close is the defensible daily signal
- St. Louis Fed On the Economy (June 2025) — Apr 2025 VIX move in the 99.9th percentile since 1990
- Benigno (2025), CEPR VoxEU — the Apr 2025 margin-call/deleveraging loop
- BIS Quarterly Review (Sept 2025) — post-Apr 9 recovery dynamics
- French, Schwert, and Stambaugh (1987); UNC working paper (2020); FSS follow-up — the vol-return horizon pattern (weak/negative short-horizon relation, positive longer-horizon) supporting the 5-day primary
- Bianchi and Bianco (2022), "Smoothing volatility targeting", arXiv:2212.07288 — 60-day smoothing as documented practice
- Bangsgaard and Kokholm (2025), JBF 180 — end-of-day vol-hedging market impact
