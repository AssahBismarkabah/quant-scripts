### **target volatility fund rebalancing — revisit research specification (v2.0)**

**Status:** Test complete (2026-08-04) — candidate REJECTED at the pre-registered bootstrap p5 gate in both co-base cells (p5 -4.84 bps Cell A, -5.39 bps Cell B at the 5-day primary). All other gates passed, including the episode check that failed in v1. Data verification additionally found the v1 bar cache corrupted on 35/839 days; all v2 results use the verified clean series. See Current Decision and `../strategies/vol-targeting/VOL_TARGETING.md` section 7.

**Supersedes:** The v1.0 specification's 20d-RV base cell, which was tested and REJECTED on 2026-08-04 (see `../strategies/vol-targeting/VOL_TARGETING.md` section 6). This document pre-registers a NEW construction justified by the documented practice of the vol-target complex, not by the v1 results.

**Purpose:** Define the revised research question, the evidence for the revised construction, the data, the execution assumptions, and the rejection gates before writing or modifying backtest code.

---

### **the research question**

Can the forced rebalancing flows of the volatility-targeting complex be measured at tradable fidelity from public daily data — using the volatility measures the complex actually uses (documented ~60-day realized volatility and the VIX index) — and does the temporary price impact of large forced-sell days revert within one trading week (5 days), producing positive expected value after friction?

The v1 answer was NO for a 20-day realized-volatility construction at the 1-day horizon, with the diagnosed measurement flaw that the window's biggest implied-volatility deleveraging event (Aug 2024) barely registered in the constructed flows. This revisit fixes the construction and re-tests with a mechanically grounded horizon.

This is a hypothesis. It is not yet an edge, strategy, or approval to trade.

---

### **the market and instruments**

- **Asset class:** US equity index (S&P 500 proxy)
- **Primary execution proxy:** S&P 500 futures (ES) — modeled via SPY daily bars
- **Signal inputs:** SPY daily bars (realized vol), VIX daily close (FRED VIXCLS, free)
- **Strategy family:** Flow-driven / forced-deleveraging fade (Category 1 mechanic)
- **Initial horizon:** 5 trading days (one week) — primary; 3 and 10 days in the robustness grid
- **Excluded initially:** Options, single-stock flows, non-US indices, intraday execution, leveraged directional bets

---

### **the proposed mechanic (revised)**

Unchanged from v1: vol-targeting exposure is rule-driven and non-discretionary — `exposure = target_vol / forecast_vol x AUM` — so every volatility move forces a mechanical flow, deleveraging fast and releveraging slowly.

The revision has three parts, each justified by documentation rather than by v1 data:

1. **The volatility measure.** The IMF Global Financial Stability Report (Oct 2017, Figure 1.21, footnote 1) documents the standard construction of the vol-target complex: leverage of a 60/40 portfolio with a 12% volatility target, computed on a **60-day realized-volatility moving window**, with the S&P 500 exposure proxied by the AQR Risk Parity mutual fund. The v1 construction used a 20-day window — shorter than the documented practice. Bhansali and Harris (2018, FAJ) document that the vol-contingent complex ("volatility targeters, trend following investors, risk parity funds") uses **the VIX as a major input parameter**, and Barclays/The Actuary (2015) note some funds rebalance on implied-versus-realized. Both measures are therefore documented inputs of the real complex. The revisit tests both as co-base cells (below).

2. **The leverage cap.** The same IMF exhibit shows the complex's leverage ranging roughly 1.0-2.5x. The v1 cap of 1.5x flattened flows during calm stretches and concentrated flow spikes at cap-threshold crossings (the top v1 flow days were such crossings, not vol events). The revisit uses cap 2.0x as base, within the documented range, and reports 1.5x/2.5x/uncapped.

3. **The horizon.** The v1 1-day fade failed. The reversion timing of the documented episodes is one week or more: Feb 2018 SPX recovered over ~5-10 sessions; March 2020 bottomed Mar 23 and V-reversed; Aug 2024 bottomed Aug 5 and recovered over the following sessions; Apr 2025 bottomed Apr 9 (five sessions after the Apr 2 shock) then posted its largest one-day gain since WWII on Apr 10 and continued recovering (BIS Quarterly Review, Sept 2025 box). The vol-return literature documents a horizon pattern consistent with this: contemporaneous volatility shocks depress returns (French, Schwert, Stambaugh 1987), variance weakly or negatively predicts returns at short horizons where it strongly forecasts variance, and positively at longer horizons (Volatility Expectations and Returns, UNC working paper 2020); conditional volatility predicts excess returns positively out of sample in GARCH-in-mean models (Expected Stock Returns and Volatility: Three Decades Later). The primary horizon is therefore pre-registered at 5 trading days, grounded in episode mechanics and the horizon pattern, with 3 and 10 days in the robustness grid.

The candidate fails conceptually if the observed return is primarily unexplained directional exposure, a data artifact (including the Aug 5 2024 VIX index construction issue documented by the SEC), or a permanent repricing rather than temporary impact.

---

### **research findings (revisit deep dive)**

The revisit literature pass adds the following conclusions:

- **The complex's construction is documented, and it is not 20d realized vol.** IMF GFSR Oct 2017 (Figure 1.21 + footnote): 60-day realized-vol window, AQR Risk Parity proxy, leverage ~1-2.5x, targets 8-15% by fund type (variable annuities 8-12%, risk parity 10-15%, CTA 15%). The v1 robustness grid's lone positive corner (60-day window, ~+23 bps) is therefore the documented base, not a selected winner.
- **The VIX is a major input of the vol-contingent complex.** Bhansali and Harris (2018, FAJ 74(2):12-23, "Everybody's Doing It: Short Volatility Strategies and Shadow Financial Insurers"): risk parity ~$500B, vol targeting ~$350B, risk-premium harvesting ~$300B, trend following ~$300B, plus explicit vol sellers — over $1.5T in short-volatility-contingent strategies that reduce exposure when VIX rises, per their design specifications. Barclays (2015, via The Actuary): most managed-vol funds rebalance daily on realized vol; a subset rebalances intraday on implied-vs-realized. Research Affiliates (2024): practitioner implementations use rules such as max of trailing 10/20/30-day volatility.
- **Both in-window episodes are documented as forced-deleveraging events, which is exactly what a VIX-driven construction should capture.**
  - **Aug 2024:** BIS Bulletin 90 (Aquilina, Lombardi, Schrimpf, Sushko 2024) — the VIX spike was amplified by deleveraging pressures and margin increases; strategies predicated on contained volatility were forced to unwind; aggregate US hedge-fund leverage had built up in the preceding low-volatility period. SEC DERA Working Paper 2504 (2025) — the Aug 5 VIX index rose from 23.9 to >65 pre-market while VIX futures stayed below 35; the index spike was partly driven by illiquid deep-OTM put quotes in the VIX calculation. **Implication:** the VIX close (38.57 on Aug 5) is the defensible daily signal; the intraday 65 is partly artifact.
  - **Apr 2025:** St. Louis Fed (June 2025) — the Apr 2-8 VIX move (+30.8 points) is the 99.9th percentile of daily changes since 1990; SPX -12.9% (99.9th percentile). Cboe Index Insights (May 2025) — VIX into the mid-50s on several days; one-month realized vol ~43%, highest since 2020. CEPR VoxEU (Benigno 2025) — a documented margin-call/deleveraging amplification loop. BIS Quarterly Review (Sept 2025) — the recovery through mid-May was driven mainly by policy reversal, and ~75% of the rise from the Apr 9 trough to end-July was unrelated to tariffs; the market normalized fast.
- **The flow-response to VIX is micro-documented.** Cheng, Kirilenko, and Xiong (2015, Review of Finance 19:1733-1781) — in distress, financial traders reduce net positions when VIX rises, and risk flows to hedgers (commodity futures). Cheng (2019, RFS 32(1):180-227, "The VIX Premium") — VIX futures returns are predictable and market participants reduce futures exposure as risk rises.
- **The vol-return horizon pattern supports a weekly fade, not a daily one.** French, Schwert, and Stambaugh (1987) — contemporaneous vol shocks depress returns. "Volatility Expectations and Returns" (UNC working paper, 2020) — variance weakly/negatively predicts returns at short horizons where it strongly forecasts variance, positively at longer horizons. "Expected Stock Returns and Volatility: Three Decades Later" (FSS follow-up) — conditional volatility positively predicts excess returns out of sample.
- **Smoothing is the norm, not the exception.** Bianchi and Bianco (2022, "Smoothing volatility targeting", arXiv:2212.07288) — standard realized-vol targeting has erratic turnover and leverage; practitioners smooth forecasts. The 60-day window is itself a smoothing device; this supports using 60d RV over 20d and explains why funds do not rebalance violently on single-day vol moves.
- **End-of-day hedging impact is documented.** Bangsgaard and Kokholm (2025, Journal of Banking & Finance 180, "The stock market impact of volatility hedging: Evidence from end-of-day trading by VIX ETPs") — vol-hedging ETP flows impact markets at the end of day. This supports modeling the flow at day-t close and trading at t+1 open, and motivates the t+1-close entry-shift gate.
- **The v1 data contributed one diagnostic, not a parameter choice:** the v1 robustness grid showed the 60-day window was the only positive corner and the 5-day horizon the only positive horizon. Both are now independently justified by the sources above (IMF documentation; episode timing; horizon literature). The v1 numbers themselves are not used as targets.

The research changes the working hypothesis from:

> The vol-target complex's flows can be measured with a 20-day realized-volatility rule and fade at the 1-day horizon.

to:

> The vol-target complex's flows are documented as driven by ~60-day realized volatility and by the VIX; both constructions should capture the Aug 2024 and Apr 2025 deleveraging episodes; the resulting temporary impact reverts within one trading week and can be captured with daily bars after friction.

---

### **version-two research scope (co-base cells)**

- **Universe:** S&P 500 proxy (SPY, fallback IVV), daily bars 2023-03-28 → present (EQUS.MINI, verified in v1).
- **Signal inputs:** SPY realized vol; VIX daily close (FRED VIXCLS, verified in v1).
- **Co-base cells (BOTH must pass — joint gate, no selection between them):**
  - **Cell A (realized):** exposure_t = min(cap, target / sigma60_t) x AUM, sigma60 = 60-day realized vol of SPY (documented by IMF GFSR).
  - **Cell B (implied):** exposure_t = min(cap, target / VIX_t) x AUM, VIX in decimal (documented by Bhansali-Harris; The Actuary).
- **Base parameters (frozen):** target 10% (in both documented ranges); cap 2.0x (within documented 1-2.5x); AUM $1.0T constant (scale-invariant for direction); event threshold = IS-trained bottom decile of flow.
- **Entry:** long at the open of day t+1, where t is a bottom-decile sell-flow day. Signal known at t close; no look-ahead.
- **Primary horizon:** 5 trading days. Robustness grid: 3 and 10 days (reported, not selected).
- **Primary hypothesis H1 (fade):** mean return from t+1 open over 5 days > 0 after base friction, in BOTH cells A and B.
- **Alternative H2 (continuation):** reported; NOT a fallback. If H1 fails in either cell at the base parameters, the candidate is rejected; the sign and horizon are not re-selected ex post.
- **Robustness grid (reported, not selected):** vol window {30, 120} and EWMA(0.94) for Cell A; VIX variant Cell B with cap {1.5, 2.5, uncapped}; AUM {$0.5T, $2T}; target {8%, 12%}; friction {2, 6 bps/side}; entry at t+1 close (timing fragility).
- **Excluded:** intraday execution, options-based signals, single-stock flows, non-US indices, shorting buy-flow days in v2.

This is a research scope, not a trading approval.

---

### **source register**

#### **Academic and research sources (new for the revisit)**

- Bhansali and Harris (2018), "Everybody's Doing It: Short Volatility Strategies and Shadow Financial Insurers", Financial Analysts Journal 74(2):12-23 — the vol-contingent complex (~$1.5T), VIX as a major input, procyclical exposure reduction, feedback-loop risk.
- Cheng, Kirilenko, and Xiong (2015), "Convective Risk Flows in Commodity Futures Markets", Review of Finance 19:1733-1781 — financial traders cut positions when VIX rises in distress; risk flows to hedgers.
- Cheng (2019), "The VIX Premium", Review of Financial Studies 32(1):180-227 — VIX futures return predictability; participants reduce exposure as risk rises.
- French, Schwert, and Stambaugh (1987) — contemporaneous negative volatility-return relation.
- "Volatility Expectations and Returns" (UNC working paper, 2020) — variance negatively predicts returns at short horizons, positively at longer horizons.
- "Expected Stock Returns and Volatility: Three Decades Later" (FSS follow-up) — conditional volatility positively predicts excess returns out of sample (GARCH-in-mean).
- Bianchi and Bianco (2022), "Smoothing volatility targeting", arXiv:2212.07288 — smoothing of vol forecasts is standard; raw realized-vol targeting is erratic.
- Bangsgaard and Kokholm (2025), "The stock market impact of volatility hedging: Evidence from end-of-day trading by VIX ETPs", Journal of Banking & Finance 180 — end-of-day vol-hedging market impact.
- Aquilina, Lombardi, Schrimpf, and Sushko (2024), "The market turbulence and carry trade unwind of August 2024", BIS Bulletin No. 90 — Aug 2024 deleveraging amplification, margin increases, leverage build-up.
- SEC DERA (2025), "Demystify the Surge in VIX", Working Paper 2504 — Aug 5 2024 VIX index spike partly a construction artifact; VIX futures stayed below 35.
- St. Louis Fed, On the Economy (June 2025), "Financial Market Volatility in the Spring of 2025" — Apr 2025 VIX move in the 99.9th percentile since 1990.
- Benigno (2025), "Why the tariffs caused turmoil in financial markets", CEPR VoxEU — the margin-call/deleveraging amplification loop of Apr 2025.
- BIS Quarterly Review (Sept 2025), "Understanding the swift market recovery after the April 2025 tariff shock" — fast post-Apr 9 reversion.
- Cboe, Index Insights: April (May 2025) — Apr 2025 vol metrics (VIX mid-50s, 1m realized ~43%).

#### **Carried over from v1 (still in force)**

- Moreira and Muir (2017), Journal of Finance 72(4):1611-1644 — vol-managed portfolios (alpha side we do NOT claim).
- Harvey, Hoyle, Korgaonkar, Rattray, Sargaison, and Van Hemert (2018), JPM 45(1):14-33, DOI 10.3905/jpm.2018.45.1.014 — vol-targeting mechanics and tail reduction.
- Cederburg, O'Doherty, Wang, and Yan (2020), JFE — OOS skepticism on the alpha side.
- Bongaerts, Kang, and van Dijk (2020), FAJ — international OOS evidence; turnover.
- ECB Financial Stability Review (May 2020), "Volatility-targeting strategies and the market sell-off" — AUM and procyclical deleveraging.
- IMF GFSR (Oct 2017), Figure 1.21 + footnote — **the documented 60-day realized-vol construction, AUM by fund type, leverage range, target ranges.**
- Barclays Research (2015) via The Actuary Magazine, "The Volatility Regime" — managed-vol complex ~$400B, daily flows 30-41% of SPX futures notional, rebalancing practice (daily realized; some intraday implied-vs-realized).
- CBOE (2018), "After the Volpocalypse" — XIV/SVXY forced-covering mechanics.
- Onali et al. (2021), "Volmageddon and the Failure of Short Volatility Products", FAJ — leverage-rebalancing feedback loop.
- NY Fed (Logan, 2020) — March 2020 levered-account deleveraging.
- CCMR NBTF (2022) — March 2020 selling and reversion.
- Research Affiliates (2024), "Harnessing Volatility Targeting in Multi-Asset Portfolios" — practitioner implementation rules (e.g., max of 10/20/30-day vol).

#### **Data sources**

- Databento EQUS.MINI (existing pipeline): SPY daily OHLCV, 2023-03-28 → present (verified in v1; 839 sessions).
- FRED VIXCLS (free CSV, no key): VIX daily close, 1990 → present (verified in v1; 875 in-window observations).

#### **Tavily research assessment**

Eight focused queries were run across the v1 and revisit passes. Results were used to locate primary sources and to document the complex's actual construction (IMF), its VIX dependence (Bhansali-Harris), and the two in-window episodes (BIS, SEC, StL Fed, CEPR, Cboe). No published daily-frequency fade edge was found in either pass. No figures from search summaries were adopted as return targets. Research output is evidence discovery, not validation.

---

### **the why and the counterparty**

Unchanged in substance from v1, with the counterparty base now better documented: the counterparties are variable-annuity vol-management programs, risk-parity funds, vol-target funds, and systematic CTAs — roughly $1.5T of vol-contingent strategies (Bhansali-Harris) plus the annuity complex (IMF: $440B in vol-managed VAs; Barclays: ~$400B managed-vol) that must cut exposure when their documented vol input rises. The trade is contractually required by the mandate and replenished every time volatility moves.

The hypothesis fails conceptually if the measured "flow days" coincide with fundamental repricing (permanent impact), if the flow measurement is dominated by noise (v1's Aug 2024 miss), or if the VIX-based construction inherits the index artifact documented by the SEC.

---

### **what must be established before coding**

1. Confirm SPY bar quality on the Databento degraded days flagged in v1 (2025-03-24, 2025-04-04, 2025-05-06) against a second source — 2025-04-04 is a critical event day (SPY -5.72%).
2. Confirm VIXCLS alignment to SPY sessions (VIX has a slightly different calendar).
3. Freeze the co-base cells, base parameters, primary 5-day horizon, and joint gate (both cells must pass).
4. Pre-register the robustness grid and the split-sample boundary (2024-12-31 / 2025-01-01), unchanged from v1.
5. Confirm the friction model: 2.0 bps/side base, 6.0 bps/side stress (ES/SPY), entry at t+1 open.
6. Confirm no look-ahead: signal from data through t close; trade at t+1 open.
7. Confirm the same-day diagnostic for BOTH cells (flow days coincide with down days), and the episode check for BOTH cells (Aug 2024 and Apr 2025 must appear in the top decile of sell-flow days — the v1 failure mode).
8. Document the SEC VIX artifact: if the VIX-close series is used, note Aug 5 2024's close (38.57) is the daily signal, and the intraday 65 was partly a construction artifact.

---

### **required data**

#### **Signal inputs**

- SPY (or IVV) daily OHLCV: full sample 2023-03-28 → present (cached in v1).
- VIX daily close (FRED VIXCLS): full sample (download route verified in v1).
- AUM estimates: constant step function from the documented figures (base $1.0T; scale-invariance of direction documented in v1).

#### **Series constructed**

- Cell A: sigma60_t = 60-day realized vol of SPY returns through t; exposure = min(2.0, 0.10/sigma60) x 1e12; flow = diff.
- Cell B: exposure = min(2.0, 0.10/VIX_t) x 1e12; flow = diff.
- Forward returns from t+1 open: hold 3/5/10 sessions.

---

### **data validation**

- Verify SPY session continuity and bar quality on the flagged degraded days (2025-03-24, 2025-04-04, 2025-05-06) against a second source.
- Verify VIXCLS alignment and that VIX closes on all SPY sessions; interpolate nothing.
- Verify both flow series produce the expected signs on the documented episodes: Aug 5 2024 (VIX 23.9 → 38.6 close) and Apr 4/7 2025 (VIX ~30 → ~60) must be large negative flow days in Cell B, and meaningful in Cell A.
- Keep raw data immutable; store derived series separately; record retrieval times and sources.

---

### **minimum machine-executable model**

#### **Signal**

At close of day t, for each cell: forecast vol (documented construction), exposure, flow. Known at t close; no look-ahead. Same-day diagnostic per cell: corr(flow, day-t return) > 0 expected (procyclical) — sanity check, not the trade.

#### **Entry condition (pre-registered primary H1)**

Enter long at the open of day t+1 when flow_t is in the bottom decile of the IS-trained flow distribution, in each cell independently. Measure mean return from t+1 open over 5 trading days. H1: > 0 after base friction in BOTH cells. H2 reported, not a fallback.

#### **Exit conditions**

- Planned holding window ends (3/5/10 days; 5 primary).
- Stop loss: -2% from entry (pre-registered).
- Force-close and record on data gaps.

#### **Position sizing**

- Equal-risk-weight per event; sized from the lower of portfolio risk budget, volatility target, and ES/SPY depth.
- Capacity: report position vs ES daily volume; documented daily flows of $30-60B confirm the complex far exceeds our scale.

---

### **cost model**

- **Base case:** 2.0 bps/side via ES/SPY (spread ~1.0 + slippage ~0.9 + fees ~0.1). Round trip: 4.0 bps.
- **Stress case:** 6.0 bps/side (high-vol days). Round trip: 12.0 bps.
- **Borrow:** N/A (futures proxy).
- **Timing:** entry at t+1 open (base); t+1 close as the timing-fragility gate.
- No result is valid if it uses mid-price fills while claiming executable returns.

---

### **validation plan**

#### **Economic validation**

- Same-day diagnostic per cell (flows coincide with down days).
- Episode check per cell (Aug 2024 and Apr 2025 in the top decile of sell-flow days).
- Fade return not concentrated in a single episode (single-event dependence is a rejection gate).
- Compare against buy-and-hold and random-day entry (reshuffle control).

#### **Statistical validation**

- Split sample: IS 2023-03-28 → 2024-12-31 | OOS 2025-01-01 → 2026-08-01. Rules frozen before OOS.
- Bootstrap (10,000 sims, seeded): p5 of the mean > 0 in both cells at the primary horizon.
- Reshuffle day returns (destroy serial correlation): effect survives.
- Drop-best-day: effect survives.

#### **Robustness validation**

The result must not depend on: one vol measure (Cell A vs B must agree), one vol window {30, 60, 120, EWMA}, one AUM level, one target {8, 10, 12}, one cap {1.5, 2.0, 2.5, uncapped}, one horizon {3, 5, 10}, one friction assumption, one episode. The co-base joint gate replaces the v1 single-corner design: consistency across the two documented constructions is the requirement.

#### **Capacity validation**

- Position size vs ES daily volume (expected non-binding at our scale; report anyway).
- Flow magnitude sanity vs documented $30-60B daily flows.

---

### **rejection gates**

Reject the candidate if any of the following is true:

- the same-day diagnostic fails in either cell (flow measure is noise);
- the episode check fails in either cell (Aug 2024 or Apr 2025 not large sell-flow days — the v1 failure mode persists);
- H1 fails in EITHER cell at the base parameters after base friction — no sign-switching, no horizon-switching, no cell-selection;
- the split sample fails to show the same sign in both halves in both cells;
- the effect depends on a single episode (Aug 2024 or Apr 2025);
- the effect depends on a single robustness corner within a cell;
- bootstrap p5 of the mean is not positive in both cells, or reshuffle/drop-best destroys the effect;
- the result disappears when entry shifts from t+1 open to t+1 close (timing fragility);
- the base-case friction gate fails (4 bps round trip);
- capacity is not credible at the intended scale.

A failed candidate is a successful research outcome. It prevents capital from being allocated to an unverified story.

---

### **tavily research questions**

Research should answer these questions before implementation:

1. What volatility measures do the main fund types actually use (window length, EWMA, VIX), and how has that practice changed over time?
2. What rebalancing frequencies and timing (close vs open) are documented per fund type?
3. How large are the flows relative to SPX futures volume today, and how does that compare to the 2013-2015 Barclays figures?
4. What documented episodes (2013-2015, Feb 2018, Mar 2020, Aug 2024, Apr 2025) show the price impact and its reversion timing?
5. Is there any published evidence of a daily or weekly fade after vol-target deleveraging (none found so far — the question remains open)?
6. Who is already trading the flows (competitive landscape)?
7. Which alternative explanations could produce an apparent fade return (regime, drift, VIX artifact, data issue)?
8. What minimum paper-trading period is appropriate before any capital is considered?

Search results must be classified as: primary academic evidence; official institutional documentation; reliable market-data documentation; practitioner evidence; anecdotal or promotional material. Promotional material is not sufficient to validate the mechanic.

---

### **research status and unresolved questions**

The revisit research pass is complete. Eight focused Tavily queries across both passes located and confirmed the key primary sources: the IMF's documented 60-day construction, Bhansali-Harris on the VIX dependence of the ~$1.5T complex, the BIS/SEC/StL Fed/CEPR documentation of both in-window episodes, and the horizon-pattern literature.

Resolved since v1 rejection:

- **Implemented:** SPY bars cached; VIXCLS route verified; v1 study scaffold runs (`../research/vol-targeting`).
- **Diagnosed and documented:** v1's flow construction missed Aug 2024 because 20d realized vol was already elevated pre-spike; top v1 flow days were cap-threshold crossings; the only positive robustness corners (60d window, 5-day horizon) are now independently justified by documentation.
- **Pre-registered:** co-base cells A (60d RV) and B (VIX close), cap 2.0x, target 10%, 5-day primary horizon, joint gate, robustness grid, split boundary, friction, episode checks.

Still unresolved before coding, and who resolves each item:

- **Research:** Verify SPY bar quality on the degraded days (2025-03-24, 2025-04-04, 2025-05-06) against a second source — 2025-04-04 is a critical event day.
- **Research:** Confirm VIXCLS download and alignment to SPY sessions.
- **Assumption:** AUM $1.0T constant — direction is scale-invariant (verified empirically in v1: identical results at $0.5T and $2.0T).
- **User:** Confirm the intended capital scale (drives whether capacity reporting matters at all).

Resolved during implementation (2026-08-04):

- **Data quality:** The three Databento-flagged days are minor (<=26 bps), but the full three-way check (Databento cache vs FRED SP500 vs Yahoo) found the cached EQUS.MINI bars corrupted on 35/839 sessions (up to -349 bps level errors on 2025-04-02, +220 bps on 2026-04-07). Yahoo and FRED SP500 agree throughout (11 bps std). All v2 results use `../research/vol-targeting/cache/SPY_clean.parquet` (Yahoo OHLC). The v1 re-run on clean bars is recorded in the strategy doc section 6.A: H1 rejection stands; the split-sample and episode gate failures recorded in v1 were cache artifacts.
- **VIXCLS:** downloaded from FRED (free CSV), aligned to SPY sessions 839/839 with zero missing.
- **Cell B episode signs:** verified before the study — Aug 5 2024 flow -$168B, Apr 4 2025 flow -$112B under the base VIX construction.
- **Study:** `../research/vol-targeting/run_study_v2.py` implemented and run (`make study-v2`); JSON output at `../research/vol-targeting/outputs/v2_study.json`.

### **current known limitations**

- The window (2023-03-28 → 2026-08) still contains no 2018/2020-scale crisis; Aug 2024 and Apr 2025 are the two documented stress episodes and are both in-window — this revisit is specifically constructed to capture them.
- The VIX index has documented construction artifacts on extreme days (SEC DERA 2025); the close is used, and the artifact is recorded rather than ignored.
- Daily bars cannot see intraday impact; the edge tested is the residual impact that survives to t+1 open and reverts within a week. If the impact reverts intraday, the daily-bar test will still reject — that is a real possibility the gates are designed to admit.
- The alpha-side literature (Cederburg, Bongaerts) remains a standing warning that most vol-management effects do not survive OOS; the same skepticism applies to the flow-side fade.

---

### **definition of done before coding**

No collection or backtest code begins until:

- the research questions have been answered with cited sources (done for this pass);
- the co-base cells and parameters are frozen in writing (done above);
- data quality on the flagged days is verified (pending);
- entry, exit, and sizing rules are frozen (done above);
- rejection thresholds are registered (done above);
- the known risks and failure modes are documented (done above);
- the friction model is specified (done above).

The outcome of this document may be approval to code, revision of the hypothesis, or rejection of the candidate.

### **current decision**

The revisit was tested on 2026-08-04 and the candidate is REJECTED per the pre-registered gates. The v1 rejection stands and is not reversed by this document; this is a NEW pre-registration justified by documented practice (IMF 60-day construction; VIX as a complex input), not by v1 data. The joint gate (both cells must pass) is designed to prevent the single-corner selection that the v1 robustness grid exposed.

Results in brief (full record: `../strategies/vol-targeting/VOL_TARGETING.md` section 7; JSON: `../research/vol-targeting/outputs/v2_study.json`):

1. **The v2 construction is validated as a flow measure.** Both cells pass the same-day diagnostic (corr +0.12 / +0.75) and the episode check (Aug 5 2024 and Apr 4 2025 in the bottom decile of flow, ranks 0.005-0.012) — the v1 failure mode is fixed. Top flow days are now vol events, not cap-threshold crossings.
2. **H1 (fade) point estimates are positive in both cells:** hold5 net-of-base-friction +37.75 bps (t=1.46, n=79) and +31.92 bps (t=1.42, n=80). Split samples same-sign; drop-best, random-day control, t+1-close entry, stop-adjusted, and single-episode independence all pass; the robustness grid is positive in 36/36 cells at 3/5/10-day horizons.
3. **The bootstrap p5 gate fails in BOTH cells:** one-sided 95% lower bound of the mean -4.84 bps (A) and -5.39 bps (B); p_negative 0.073/0.075. The effect is not statistically distinguishable from zero at the pre-registered threshold, so the candidate is rejected as unproven despite uniformly positive point estimates.
4. Recorded-not-selected: hold10 point estimates +94.6/+99.2 bps. Any future revisit must pre-register a longer horizon or an extended sample; the 5-day primary and the co-base cells are closed.

Data integrity finding (2026-08-04): the v1 EQUS.MINI bar cache was corrupted on 35/839 sessions; v1's recorded split-sample and episode failures were cache artifacts (v1's overall rejection stands on verified data — see strategy doc section 6.A). All v2 results use the verified clean series.
