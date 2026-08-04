### **target volatility fund rebalancing research specification**

**Status:** Pre-research specification (2026-08-04) — literature pass complete, data route verified, gates pre-registered. No backtest code written yet.

**Classification:** Candidate mechanic / Flow-driven systematic deleveraging (Category 1: Mathematical mandates, "must-do trades")

**Purpose:** Define the research question, evidence requirements, data, execution assumptions, and rejection gates before writing collection or backtest code.

---

### **the research question**

Can the forced daily rebalancing flows of the volatility-targeting complex (vol-target funds, risk-parity funds, vol-managed variable annuities, systematic CTAs with vol overlays) be measured from public daily data, and does the temporary price impact of those flows revert within 1-5 days, producing positive expected value after friction?

This is a hypothesis. It is not yet an edge, strategy, or approval to trade.

The first implementation targets the US equity index complex (S&P 500 proxy) using daily bars from the existing EQUS.MINI pipeline plus a free implied-volatility series (VIX, FRED VIXCLS). No new paid data is required for the first pass.

---

### **the market and instruments**

- **Asset class:** US equity index (S&P 500 proxy)
- **Primary execution proxy:** S&P 500 futures (ES) — modeled via SPY daily bars
- **Signal inputs:** SPY realized volatility, VIX implied volatility, vol-target complex AUM estimates
- **Strategy family:** Flow-driven / forced-deleveraging fade (Category 1 mechanic)
- **Initial horizon:** 1-5 trading days after a measured forced-flow day
- **Excluded initially:** Options, single-stock flows, non-US indices, intraday execution, leveraged directional bets

---

### **the proposed mechanic**

Volatility-targeting strategies maintain a roughly constant portfolio risk level by scaling exposure inversely to a volatility forecast:

`exposure = target_vol / forecast_vol × AUM`

The scaling is rule-driven, not discretionary. When forecast volatility rises, the fund must sell; when it falls, the fund must buy. The rebalance is contractually forced by the mandate (Category 1: the fund cannot choose not to trade). This creates a mechanical, procyclical flow:

- **Deleveraging is fast:** a vol spike forces immediate selling into a falling market.
- **Releveraging is slow:** funds rebuild exposure gradually after the storm passes.

The candidate trade: measure the daily flow of the vol-target complex, identify large forced-sell days, and fade the temporary price impact over the following 1-5 days.

The candidate fails conceptually if the observed return is primarily unexplained directional exposure, data artifact, or a permanent repricing rather than a temporary impact.

---

### **research findings**

The first literature pass produces the following conclusions:

- **The signal side is contested out of sample.** Moreira and Muir (2017, Journal of Finance 72(4):1611-1644) show vol-managed portfolios earn large in-sample alphas (market 4.22%/yr, momentum 11.00%/yr, 1,061 months). But Cederburg, O'Doherty, Wang, and Yan (2020, JFE) reproduce the spanning alphas (77 of 103 vol-scaled strategies positive) yet find no systematic out-of-sample Sharpe improvement; the gains concentrate in momentum-related strategies, and "the trading strategies implied by spanning regressions are not implementable in real time." Bongaerts, Kang, and van Dijk (2020, FAJ) find conventional vol-targeting gives no consistent international risk-adjusted improvement, with turnover of 1.8-2.6x per year. **Conclusion: we do NOT claim the alpha side. Our claim is the flow side.**
- **The flow side is documented and enormous.** ECB Financial Stability Review (May 2020 box, "Volatility-targeting strategies and the market sell-off"): globally up to USD 2 trillion in some form of volatility strategies, with USD 300 billion in ~100 risk-parity funds; documents the procyclical deleveraging of risk-parity equity exposure in March 2020. IMF GFSR (Oct 2017, Figure 1.21): variable annuities with vol targets $440B AUM (target 8-12%), CTA/systematic $220B, risk parity $150-175B, with 69%/19% three-year AUM growth. Barclays Research (2015, via The Actuary Magazine): managed-volatility complex ~$400B as of mid-2015, and single-day vol-target rebalance flows of −$29B to −$61B equal to **30-41% of SPX futures notional** on those days (Oct 14 2013: −$53B = 41%; Jul 1 2015: −$47B = 30%).
- **The flows are forced, which is the asymmetry we trade.** CBOE ("After the Volpocalypse", 2018): XIV and SVXY were short ~280,000 VIX futures ($280M vega) on Feb 5 2018; the >100% VIX spike forced mechanical covering; short-vol ETP assets fell from $3.7B to ~$525M. Onali et al. (2021, Financial Analysts Journal, "Volmageddon and the Failure of Short Volatility Products"): 2x and inverse vol ETPs needed to buy ~113,000 contracts (>20% of all outstanding VIX futures) during the Feb 5 2018 rebalancing — the leverage rebalancing itself was a major price mover. The mandate forces the trade regardless of price.
- **March 2020 confirmed the mechanism at scale in equities.** NY Fed (Logan, Oct 2020, "Treasury Market Liquidity and Early Lessons from the Pandemic Shock"): levered accounts and relative-value funds cut positions, futures margins rose, basis-trade positions unwound. CCMR NBTF report (2022): regulators could not fully attribute the March 2020 Treasury selling ($287B foreign, $236B mutual fund, $170B household reductions Q4'19→Q1'20) with transaction data — the sellers include forced deleveragers, and the price impact reversed only after Fed intervention.
- **The impact is temporary in the documented episodes.** Feb 2018: VIX futures spiked then partially reverted over the following days; SPX fell 4.1% on Feb 5 then recovered over subsequent sessions. March 2020: the S&P 500 bottomed on Mar 23 then V-reversed. Aug 2024: VIX spiked to ~65 intraday on Aug 5, equities recovered within days. This supports the fade hypothesis (H1, pre-registered below) but does not prove it persists in the 2023-2026 window — that is the falsifiable question.
- **Volatility clustering is the driver of flow timing.** Dreyer and Hubrich (2017, "Tail Risk Mitigation with Managed Volatility Strategies"), Harvey et al. (2018, JPM 45(1):14-33, "The Impact of Volatility Targeting"): realized vol is persistent and forecastable at short horizons; vol targeting reduces left tails and max drawdowns across 60+ assets. The persistence of vol means the flow signal is measurable from daily bars alone.
- **AUM estimates vary; the signal does not depend on them for direction.** The flow direction and timing come from the change in 1/σ. AUM only scales the flow. The significance tests in this study are AUM-scale-invariant; AUM enters only for capacity and sanity magnitudes. This is a robustness property, not a weakness.
- **No published paper was found claiming a persistent daily-frequency "fade the vol-target flow" edge with daily data.** Practitioner and academic work documents the flows and the episodes but not a systematic tradable rule. The candidate's core question is therefore open, which is exactly why it is worth a pre-registered test.

The research changes the working hypothesis from:

> Volatility-managed portfolios earn alpha (Moreira-Muir).

to:

> Volatility-targeting funds are forced to rebalance by mandate; the resulting daily flows create measurable temporary price impact that reverts within 1-5 days; the reversion can be captured with daily bars after friction.

---

### **version-one research scope**

- **Research universe:** S&P 500 proxy (SPY, fallback IVV) daily OHLCV bars from EQUS.MINI (2023-03-28 → present).
- **Volatility inputs:** SPY 20-day realized vol (base); 10d/60d realized, EWMA(0.94), and VIX level as robustness.
- **AUM estimate:** $1.0T base (constant through sample), $0.5T and $2.0T robustness. Constant because the signal's direction and timing do not depend on AUM.
- **Vol target:** 10% annualized (base); 8% and 12% robustness.
- **Leverage cap:** 1.5x (base); 1.0x, 2.0x, uncapped robustness.
- **Direction:** Fade the forced flow — long after large forced-sell days, held 1-5 days. Pre-registered primary hypothesis H1 (see model section).
- **Execution proxy:** ES futures modeled via SPY bars; entry at the open of the first trading day after the flow day.
- **Excluded from version one:** Intraday execution, options-based signals, single-stock flows, non-US indices, buying the flow day itself.

This is a research scope, not a trading approval.

---

### **source register**

#### **Academic and research sources**

- Moreira and Muir (2017), "Volatility-Managed Portfolios", Journal of Finance 72(4):1611-1644 — the foundational vol-targeting result (in-sample alphas; the alpha side we do NOT claim).
- Cederburg, O'Doherty, Wang, and Yan (2020), "On the performance of volatility-managed portfolios", Journal of Financial Economics — OOS skepticism on the alpha side.
- Bongaerts, Kang, and van Dijk (2020), "Conditional Volatility Targeting", Financial Analysts Journal — international OOS evidence and turnover costs.
- Barroso and Santa-Clara (2015), "Momentum has its moments", JFE; Daniel and Moskowitz (2016) — vol-managed momentum (the one robust OOS alpha corner).
- Harvey, Hoyle, Korgaonkar, Rattray, Sargaison, and Van Hemert (2018), "The Impact of Volatility Targeting", JPM 45(1):14-33, DOI 10.3905/jpm.2018.45.1.014 — tail reduction and vol-targeting mechanics across 60+ assets.
- Dreyer and Hubrich (2017), "Tail Risk Mitigation with Managed Volatility Strategies" — vol clustering as the driver.
- Onali et al. (2021), "Volmageddon and the Failure of Short Volatility Products", Financial Analysts Journal — leverage-rebalancing feedback loop quantification (Feb 2018).
- CBOE (2018), "After the Volpocalypse: Market Observations" — XIV/SVXY positioning and forced covering mechanics.

#### **Official / institutional sources**

- ECB Financial Stability Review, May 2020 box, "Volatility-targeting strategies and the market sell-off" — AUM ($2T vol strategies, $300B risk parity) and procyclical deleveraging model estimates.
- IMF Global Financial Stability Report, Oct 2017, Figure 1.21 — AUM table: variable annuities $440B (8-12% targets), CTA/systematic $220B, risk parity $150-175B.
- NY Fed (Logan), Oct 2020 speech, "Treasury Market Liquidity and Early Lessons from the Pandemic Shock" — March 2020 levered-account deleveraging and basis-trade unwind.
- Committee on Capital Markets Regulation, "The U.S. Treasury Market During the COVID-19 Crisis" (NBTF, 2022) — March 2020 selling attribution.
- Barclays Research (2015) via The Actuary Magazine, "The Volatility Regime" — ~$400B managed-vol complex; daily flows 30-41% of SPX futures notional.

#### **Data sources**

- Databento EQUS.MINI (existing pipeline): SPY daily OHLCV, 2023-03-28 → present. Coverage of SPY to be verified; fallback IVV.
- FRED VIXCLS (free): VIX daily close for the implied-vol robustness variant.

#### **Tavily research assessment**

Tavily was used for four focused queries covering the alpha-side literature, the Feb 2018 volmageddon mechanics, the March 2020 deleveraging episodes, and AUM/flow magnitudes. Results were useful for locating primary sources and quantifying flows. No published daily-frequency tradable rule for fading vol-target flows was found; none of the returned figures were adopted as return targets. Research output is evidence discovery, not validation.

---

### **the why and the counterparty**

The candidate source of return is not that volatility is mean-reverting, and not that vol-managed portfolios outperform. The source is the interaction between:

- vol-targeting mandates that force exposure to be cut when forecast vol rises (Category 1: the fund must trade);
- the procyclical clustering of those cuts — many funds rebalance on similar rules at similar times;
- the temporary price impact of the forced flows;
- the reversion that follows when the forced flow stops.

The likely counterparties are vol-target funds, risk-parity funds, vol-managed variable annuities, and systematic CTAs that must transact on their own schedules regardless of price. This is a stronger constraint than a behavioral premium: the trade is contractually required by the mandate, and it is replenished every time volatility moves.

The hypothesis fails conceptually if the measured "flow days" coincide with fundamental repricing (in which case the impact is permanent and the fade loses money), or if the flow measurement is dominated by noise.

---

### **what must be established before coding**

1. Confirm SPY daily OHLCV coverage in EQUS.MINI for the full sample; verify against a second source (e.g., Yahoo/Stooq) for a sample window.
2. Confirm VIXCLS availability from FRED (free API key) or CBOE historical CSV.
3. Freeze the base parameters: 20d RV, 10% target, 1.5x cap, $1.0T AUM, entry at T+1 open, holding 1-5 days, H1 direction (fade).
4. Pre-register the robustness grid and the split-sample boundary (2024-12-31 / 2025-01-01).
5. Confirm the friction model assumptions for ES/SPY: base 2.0 bps/side, stress 6.0 bps/side (see cost model).
6. Confirm the signal timing has no look-ahead: signal computed from data through day T close, trade at T+1 open.
7. Confirm the same-day diagnostic (flow days should coincide with down days) before trusting the flow measure.
8. Verify the Aug 2024 and Apr 2025 vol-spike episodes appear as large negative flow days in the constructed series (sanity check of the pipeline).

---

### **required data**

#### **Signal inputs**

- SPY (or IVV) daily OHLCV: full sample 2023-03-28 → present.
- VIX daily close (FRED VIXCLS): full sample, same dates.
- AUM estimates: static step function from IMF/ECB/Barclays figures, constant through sample (scale-invariance documented above).

#### **Series constructed**

- 20d realized vol of SPY daily returns (base); 10d/60d, EWMA(0.94), VIX (robustness).
- exposure_t = min(cap, target / forecast_vol_t) × AUM
- flow_t = exposure_t − exposure_{t−1} (dollar flow executed at close of day t, known at t close)

---

### **data validation**

- Verify no missing/gapped SPY sessions; reconcile bar count against a second source for one quarter.
- Verify the SPY series has no corporate-action artifacts (splits) — SPY is a clean ETF, low risk, but check price continuity.
- Verify VIXCLS alignment to SPY trading dates (VIX has a slightly different calendar).
- Check that the flow series has the expected sign pattern on the Aug 2024 / Apr 2025 vol spikes.
- Keep raw data immutable; store derived series separately.
- Record retrieval times, sources, and known limitations.

---

### **minimum machine-executable model**

#### **Signal**

At close of day t:

- forecast_vol_t from the pre-registered base rule (20d RV of SPY through day t);
- exposure_t = min(cap, target / forecast_vol_t) × AUM;
- flow_t = exposure_t − exposure_{t−1}.

The flow is known at t close with no look-ahead. The same-day diagnostic: regress day-t SPY return on flow_t; expect a significant positive relationship (flows are procyclical: negative on down days, positive on up days) — this is a sanity check, not the trade.

#### **Entry condition (pre-registered primary H1)**

Enter long at the open of day t+1 when flow_t is in the bottom decile of the in-sample flow distribution (large forced sell), holding 1, 2, or 5 trading days (tested as a fixed grid, not selected). H1: mean return from t+1 open > 0 after base friction.

Pre-registered alternative H2 (continuation): mean return < 0. H2 is reported but is NOT a fallback — the candidate is rejected if H1 fails at the base cell; the sign is not re-selected ex post.

#### **Exit conditions**

- Planned holding period ends (1/2/5 days).
- Stop loss: pre-registered, e.g., −2% from entry.
- Force-close on any data gap.

#### **Position sizing**

- Equal-risk-weight per event; sized from the lower of portfolio risk budget, volatility target, and ES depth.
- Capacity check: typical ES/SPY daily volume vs our position; flow events of $30-60B confirm the complex is far larger than our capacity needs.

---

### **cost model**

- **Base case:** 2.0 bps/side round trip via SPY/ES (spread crossing ~1.0 bp + slippage ~0.9 bp + exchange fee ~0.1 bp). Round trip: 4.0 bps.
- **Stress case:** 6.0 bps/side (spreads widen on high-vol days, the exact days we trade). Round trip: 12.0 bps.
- **Borrow:** N/A (futures proxy).
- **Timing:** entry at t+1 open — model open-price execution, not mid/close.
- No result is valid if it uses mid-price fills while claiming executable returns. The friction gate uses the base case; the stress case is reported alongside.

---

### **validation plan**

#### **Economic validation**

- Verify the same-day diagnostic (flows coincide with down days) — if flows do not track market direction, the flow measure is noise.
- Verify the fade return is not concentrated in the Aug 2024 or Apr 2025 episode (single-event dependence is a rejection gate).
- Compare against a buy-and-hold benchmark and against random-day entry (reshuffle control).

#### **Statistical validation**

- Split sample: 2023-03-28 → 2024-12-31 (IS) and 2025-01-01 → 2026-08-01 (OOS). Freeze rules before OOS.
- Bootstrap the day returns (S10-style, 10,000 sims, seeded): p5 of the bootstrap mean must be positive in the base cell.
- Reshuffle day returns (destroy serial correlation): the effect must survive.
- Drop-best-day test: the effect must survive removing the single best day.

#### **Robustness validation**

The result must not depend on: one vol window {10,20,60}, one vol measure {RV, EWMA, VIX}, one AUM level {$0.5T, $1T, $2T}, one target {8%, 10%, 12%}, one cap {1.0x, 1.5x, 2.0x}, one holding {1, 2, 5}, one friction assumption {2, 6 bps/side}, or one episode (Aug 2024 / Apr 2025).

The base cell is pre-registered; robustness is reported as a neighborhood, not selected.

#### **Capacity validation**

- Position size vs ES daily volume (capacity is expected to be a non-issue at our scale; report the number anyway).
- Flow magnitude sanity: the documented $30-60B daily flows confirm the complex is not something we can move.

---

### **rejection gates**

Reject the candidate if any of the following is true:

- the same-day diagnostic fails (flow days do not coincide with down days — flow measure is noise);
- H1 (fade) fails at the base cell after base friction — no sign-switching to H2;
- the effect does not survive the split sample with the same sign in both halves;
- the effect depends on a single episode (Aug 2024 or Apr 2025);
- the effect depends on a single robustness corner (one vol window, one AUM level, one target, one cap, one holding);
- bootstrap p5 of the mean is not positive, or reshuffle/drop-best destroys the effect;
- the result disappears when entry is shifted from t+1 open to t+1 close (timing fragility);
- the friction gate fails (base case does not clear 4 bps round trip);
- capacity is not credible at the intended scale (expected: non-binding, but must be reported).

A failed candidate is a successful research outcome. It prevents capital from being allocated to an unverified story.

---

### **tavily research questions**

Research should answer these questions before implementation:

1. What is the size of the vol-target complex over time (AUM), and how does it vary by fund type?
2. What rebalancing frequencies and rules do the main fund types use (daily/weekly, RV vs implied)?
3. What documented episodes show vol-target flows moving prices (2013-2015 flows, Feb 2018, Mar 2020, Aug 2024)?
4. What is the documented speed of releveraging vs deleveraging (asymmetry)?
5. What evidence exists for persistence of any fade strategy after costs?
6. What is the competitive landscape (who is already trading the flows)?
7. Which alternative explanations could produce an apparent fade return (regime, drift, data artifact)?
8. What is the appropriate minimum paper-trading period before any capital is considered?

The Tavily pass adds two explicit research controls:

- Do not use published flow magnitudes or episode returns as return forecasts.
- Do not treat a parameter choice as valid until it is tested across the full pre-registered grid.

Search results must be classified as: primary academic evidence; official institutional documentation; reliable market-data documentation; practitioner evidence; anecdotal or promotional material. Promotional material is not sufficient to validate the mechanic.

---

### **research status and unresolved questions**

The initial research pass is complete. Four focused Tavily queries were run and the key primary sources located (Moreira-Muir JF 2017; Cederburg et al. JFE 2020; Bongaerts et al. FAJ 2020; Harvey et al. JPM 2018; ECB FSR May 2020 box; IMF GFSR Oct 2017; CBOE volpocalypse paper; Onali et al. FAJ 2021; NY Fed Logan 2020; CCMR NBTF 2022; Barclays/The Actuary 2015).

Implementation status (2026-08-04): first-pass study complete and candidate REJECTED per the pre-registered gates (see Current Decision). Data verified: SPY daily bars in EQUS.MINI (839 sessions, full window) and VIXCLS from FRED (free CSV). Scaffold in `research/vol-targeting/` (run_study.py + Makefile), kept for any revisit.

Resolved since pre-research:

- **Implemented:** SPY coverage confirmed in EQUS.MINI; bars cached; VIXCLS download route confirmed (FRED CSV, no key).
- **Implemented:** Same-day diagnostic PASS (corr +0.15, flows procyclical).
- **Implemented:** Base cell, split sample, bootstrap, drop-best, random-day control, robustness grid — all failed or marginal per gates.
- **Implemented:** Episode sanity check FAIL — Aug 2024 not a large constructed flow day (rank 205/839, -$16B).
- **Closed:** 20d-RV base cell rejected; revisit requires new pre-registration (VIX/EWMA-driven construction or intraday data).

Still unresolved after the rejection, and who resolves each item:

- **Research:** Whether an implied-vol/EWMA-driven flow construction (testable with free VIX data) captures Aug 2024-class deleveraging — the precondition for any revisit.
- **User:** Confirm the intended capital scale (drives whether capacity reporting matters at all).

### **current known limitations**

- The sample window (2023-03-28 → 2026-08) contains no 2018/2020-scale crisis; the two in-window vol episodes (Aug 2024, Apr 2025) are mild by comparison. The daily-frequency mechanic is testable in this window, but the crisis-regime behavior of the flows is not fully testable — this is documented, not ignored.
- The flow model is a simplification: one fund complex, one vol rule, static AUM, no fund-by-fund variation in target/cap/rebalance timing. Real flows are smoother and spread across days; the model's flow will be noisier than reality, which biases against finding an effect (conservative).
- The alpha-side literature (Cederburg, Bongaerts) says most vol-management effects do not survive OOS; the same skepticism applies to the flow-side fade. That is the point of the pre-registered gates.
- SPY daily bars measure close-to-close; intraday impact dynamics are invisible. The fade edge, if it exists at all with daily bars, is the residual impact that survives to t+1.

---

### **definition of done before coding**

No collection or backtest code begins until:

- the research questions have been answered with cited sources;
- instruments have been selected with reasons (SPY/ES proxy, VIX robustness);
- the data schema and historical availability are confirmed (SPY in EQUS.MINI, VIXCLS from FRED);
- the signal formula, timing, and no-look-ahead property are frozen in writing;
- entry, exit, and sizing rules are frozen (H1, base cell, grid, split boundary);
- rejection thresholds are registered;
- the known risks and failure modes are documented;
- the friction model is specified (2.0/6.0 bps per side).

The outcome of this document may be approval to code, revision of the hypothesis, or rejection of the candidate.

### **current decision**

The candidate is rejected at first pass (2026-08-04), per the pre-registered gates:

1. **H1 fails at the base cell after base friction.** Fade mean hold1 = -1.62 bps raw, -5.62 bps net base (t = -0.14, n = 73); -13.62 bps net stress. Bootstrap (10k, seeded): p5 = -21 bps, p_negative = 0.56. Drop-best: -7.95 bps. Random-day control: +19.58 bps.
2. **Split sample shows opposite signs.** IS -5.44 bps (n=43) vs OOS +3.87 bps (n=30).
3. **Episode sanity check fails.** The Aug 2024 vol spike (window's biggest) ranks 205/839 in constructed flow magnitude (-$16B); the 20d-RV construction misses implied-vol-driven deleveraging events. Apr 2025 ranks 25/839 (-$113B). Top flow days are cap-threshold crossings from deep-calm states (2025-10-10: -$783B; 2024-12-18: -$667B).
4. Robustness: base corner negative; effect flips with vol window (all vw=60 cells ~+23 bps). AUM scale-invariance confirmed (identical at $0.5T/$2T).

Recorded non-result: hold5 = +44 bps raw (t=1.58), OOS +74 bps (t=1.49) — a fade hint at 5 days, not significant, not the pre-registered primary; not chased per the no-horizon-selection rule.

The code, data, and scaffold are kept (`research/vol-targeting/`). A revisit requires a new pre-registration with a higher-fidelity flow construction (implied-vol/EWMA-driven exposure, which would capture Aug 2024-class events; VIX-based exposure is testable with free FRED data) or intraday data. The 20d-RV base cell is closed.

**Addendum (2026-08-04, data integrity):** the v2 revisit (`IA/vol-targeting-revisit-research-spec.md`) verified the SPY bar cache against FRED SP500 and Yahoo and found it corrupted on 35/839 sessions (up to -349 bps level errors on event days such as 2025-04-02). The v1 re-run on the verified clean series (`research/vol-targeting/cache/SPY_clean.parquet`, `make study-v1-clean`) shows: H1 (hold1) still fails (-3.23 raw / -7.23 net base bps, t=-0.31) — the v1 rejection stands; but the recorded split-sample sign-flip and Aug 2024 episode failures were cache artifacts (on clean bars: IS -3.93 / OOS -2.34 same sign; Aug 5 2024 ranks in the bottom decile). The v2 candidate was also tested and rejected at its pre-registered bootstrap gate (see the revisit spec Current Decision).
