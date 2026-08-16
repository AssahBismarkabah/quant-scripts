
### 8.11 Stage-1 derive pass — Dataset A (SPY options 2008-2025, LambdaClass) — RESULT: 2 survivors of 56, both REJECTED

First-ever execution of the derive-from-data method (`derive-pass-stage1-spec.md`, `derive_mine1.py`). Frozen grid: 28 candidates x 2 horizons = 56 tests, Bonferroni |t|>=3.29, IS (2008-2018.10) + OOS (2018.10-2025) same-sign gate.

**Survivors (2):**
- **PC OI ratio (level)** -> fwd5: tIS +3.74 / tOOS +4.89. REJECTED under IV control: corr(PC-OI, ATM IV)=+0.169; after IV-quintile demeaning OOS rho collapses +0.087 -> +0.001. It was the closed IV/VRP level restated. DEAD.
- **Call volume share** -> fwd5: tIS +3.53 / tOOS +3.42, rho +0.06-0.08. Survived IV control (corr with IV only +0.143; residual OOS +0.033) AND (IV x momentum21) double-demean (IS +0.070 / OOS +0.023; top-quintile +38.5 bps/5d vs others +12-22). Bootstrap p5 +13.6 bps (n=896 trades, 6 bps friction) — first p5>0 in the program. **REJECTED by the pre-registered tail gate: max DD −80.6% vs −40%.** DEAD.

**Why (recorded, explains both):** call-volume-share is negatively correlated with trailing returns (prior5 −0.32, prior21 −0.40) — call volume share spikes after market drops = retail dip-buying of calls (counterparty: institutions selling calls into that demand). Pays on average because crashes rebound; dies catastrophically when declines continue (DD −80.6%). Same equity-risk-premium family already killed in V2/V3/Obs 2 — now expressed via options positioning instead of IV.

**Method result: derive pass works.** 2/56 candidates cleared the multiplicity+consistency screen (vs 0 expected by chance at 56 tests); the IV-control and tail-gate layers correctly rejected both. Not a harness artifact: for the first time a scan produced genuine repeatable observations, and the gates adjudicated them. Dataset A grid: exhausted for this pass (recorded in spec). Next: Dataset B (PEAD panel) or C (intraday) grids.

### 8.12 Stage-1 derive pass — Dataset B (PEAD panel, 24.4M rows, 1998-2021) — RESULT: no new observations; all 5 survivors are public anomalies already killed

`derive_mine2.py`. Frozen grid: 12 cross-sectional candidates (ret21, ret63, dist_hi252, dist_lo252, pos_hl63, vol63, avg252_dist, ret5, max_dd63, days_to_hi252, days_to_earn, earn_win7) x fwd21 horizon. Method: daily cross-sectional rank IC -> t-test on the daily IC series (~5,900 days, NOT 24M rows — row-count t-stats are meaningless: rho -0.03 on 24M rows gives |t|=91). Bonferroni |t|>=3.29, IS 1998-2012.01 / OOS -> 2021, same-sign gate. **Plus a separate calendar family (fri/mon/eom) as time-series market tests** — calendar dummies are constant across stocks within a day, so cross-sectional rank IC is structurally impossible for them; that is a market-timing question, not a cross-sectional one.

**Survivors (5 of 12):** ret21 (tIS −15.6/tOOS −6.1), dist_hi252 (+3.8/+12.7), dist_lo252 (−7.9/−9.0), vol63 (−10.3/−15.3), ret5 (−22.1/−10.3).

**Adjudication: all five are re-discoveries of classic public cross-sectional anomalies on the SAME panel already killed in Step 2b** under honest shorting costs (rev1m/mom12-1/lowvol — `step2b_diverse_basket.py`, 2026-08-12f): 5d/21d short-term reversal (ret5, ret21), 52-week-high/low distance momentum (dist_hi252, dist_lo252), low-volatility (vol63). None is a NEW observation. The derive pass exists to find what papers don't already re-test; these are the textbook first page of the cross-sectional literature. No candidate proceeds to the harness — they were already harnessed in Step 2b and died on borrow costs + friction. DEAD as a class.

**Calendar family (3):** all dead. fri tOOS +0.08, mon −2.24, eom −0.26; sign-flips IS/OOS for mon/eom. (Garbage days excluded: 3 split-artifact days — TMK 2019-08-08 +88,099x, TMK 2019-08-12, AST 2019-05-10 — winsorized before test; a raw run produced meaningless bps.)

**Earnings axis (2):** underpowered, not testable — earnings_latest.csv matches only 0.7% of price rows (nIS=658 days), earn_win7 nIS=2 days. days_to_earn tIS −0.63/tOOS −2.66, below bar with a broken IS. Recorded as data-coverage-limited, not a survivor.

**Grid note:** announced 21-candidate grid not fully implementable on this data — no volume/sector/open columns exist (dollar-volume percentile, overnight vs intraday split, liquidity rank axes are uncomputable here); frozen grid as run = 12 cross-sectional + 3 calendar, recorded in the spec before results for the calendar axes. **One mid-run error caught and reverted:** I briefly added post-hoc interaction candidates (ret21 x dist_hi252 etc.) after seeing the first-9 results — that is exactly the forbidden result-hunting move from the spec §1; reverted to the frozen grid before the final run.

**Dataset B verdict: exhausted for this pass — grid produced only public-anomaly rediscoveries; no new observation; no harness candidate.** Cross-sectional daily data at our scale with honest short-borrow costs is measured-dead (consistent with Step 2b). Next: Dataset C (NQ/ES intraday 1-min).

### 8.13 Stage-1 derive pass — Dataset C (NQ/ES intraday 1-min) — RESULT: 0 survivors of 12 (NQ) / 0 of 12 (ES)

`derive_mine3.py`. Frozen grid per spec §5: 12 tests, 3 axes (time-of-day structure beyond opening range, session-boundary effects, volatility-state transitions), unit = one day (2,527 NQ days 2013-2023 / 1,551 ES days 2020-2026), Pearson per-day series, IS/OOS by date, |t|>=3.29 both halves. NQ primary, ES as out-of-sample asset check.

**Two self-correlation artifacts caught and fixed during the scan** (identical class to the SB4 t=+45 blow-up): (1) `cc_ret` was built from TODAY's gap and OC, so correlating it with today's OC was mechanical self-correlation (tIS +45.5); fixed to prev-day close-to-close (`cc_prev`), sb4 drops to tIS −0.51. (2) `f_vol_pct` used TODAY's h1_vol against today's h1_ret — contemporaneous vol-return asymmetry (tIS −5.83), not predictive; lagged to prev-day percentile, vs1 drops to tIS +0.90. Both were pre-spec-tests; no verdict was accepted from a buggy run.

**All 24 tests dead after lags:**
- NQ: best were tds3 (last-h → next-day OC, tIS −3.18/tOOS −1.96 — fails bar), sb1 (gap→OC, sign flip −2.60/+2.17), sb4 (tOOS −3.05, tIS −0.51 sign flip), vs4 (sign flip +1.02/−3.42). Nothing passes.
- ES (OOS asset): tds1/tds2/tds3/tds4 all |t|<2.5; sb1 tOOS −3.34 with tIS −0.59 (sign flip); sb2 Monday-gap rOOS −0.39 but tIS −0.83 vs tOOS −4.57 with IS sign flip (+0.26 vs −0.39 correlation); vs-family dead.

**Why recorded:** gap-continuation and last-hour effects are the classic public intraday/day-of-week patterns, weak and regime-unstable in modern data (2020-2026 ES shows the opposite sign of 2013-2020 NQ in several axes — the effects died or inverted post-2020). No forced-counterparty story survives with a stable sign across both assets.

**Dataset C verdict: exhausted — zero survivors across 24 tests.** The intraday micro-timing axes on data we own are measured-dead.

### 8.14 Stage-1 derive pass — FINAL: all datasets exhausted, zero surviving edges

- Dataset A (options): 2/56 survivors, both rejected (PC-OI = VRP restated under IV control; call-volume-share passed controls + bootstrap p5>0 but failed −40% tail gate with DD −80.6%). §8.11.
- Dataset B (PEAD cross-section): 5/12 survivors, all public-anomaly rediscoveries (reversal/momentum/low-vol) already killed in Step 2b under honest short-borrow costs. No new observation. §8.12.
- Dataset C (intraday): 0/12 (NQ), 0/12 (ES), all dead after lag corrections. §8.13.

**Per spec §4, the Stage-2 decision point is reached**: the free-data derive pass found no objective machine-executable edge above friction 3-6 bps in any owned dataset. This is consistent with (and now formally executes) the Step 2b-earned claim "free-data portfolio alpha at our scale is measured-dead". Options before the user: (a) Stage-2 paid data for the remaining untested candidate (IVAMR long-intraday — `research/ivamr/`), (b) stop the systematic phase, (c) expand the derive grid (not recommended per anti-result-hunting rules — grid expansion after full-dataset exhaustion is post-hoc).

### 8.15 Stage-1 derive pass — Dataset D (unsupervised joint-state, NQ/ES) — RESULT: 0 survivors of 12; method inventory COMPLETE

`derive_mine4.py`, spec §6 (frozen before any results). The last untried blueprint method (Blueprint Phase 2: unsupervised anomaly/regime detection — Isolation Forest + K-means). Rationale: all prior scans were single-feature LINEAR tests; this asks whether JOINT combinations of features (h1 ret/vol/range/logvol, vol_ratio, gap, prev-cc, skew — 9 features, z-scored) predict forward returns. Weak prior recorded in the spec; cheap; owned data.

**Results (6 pre-registered tests per asset):**
- NQ (2,426 days): T1 anom→rest +0.23/−0.66 (sign flip), T2 anom→nxtOC −0.46/+0.34 (flip), T3 top-decile→rest +0.69/+0.02 (top decile +15 bps IS but +3 bps OOS — dies), T4 top-decile→nxtOC −0.09/−0.16, T5 K3-hot→rest +0.41/+0.30, T6 K3-hot→nxtOC −0.05/−0.23. **0 survivors.**
- ES (1,478 days, OOS asset check): best was T1 anom→rest tIS +1.37/tOOS +3.01 — fails the IS bar (1.37 < 3.29), so not a survivor under the frozen same-sign |t|>=3.29 gate. All others |t|<1.4. **0 survivors.**

**Interpretation:** joint-state anomaly and regime structure in first-hour NQ/ES microstructure carries no forward-return information beyond what the linear scans already measured. The anomaly score is essentially vol-plus-volume in disguise (both already dead). The blueprint's Phase-2 unsupervised discovery method is executed on the owned data and finds nothing.

**Method inventory is now COMPLETE:** Phase 1 (data) done, Phase 2 (unsupervised discovery) done — dead, Phase 3 (validation incl. positive control) done, Phase 4/5 blocked upstream by zero survivors. Every method in `IA/Blueprint-for-the-Independent-Quant.md` that can be run on owned free data has now been run. The derive pass closure in §8.14 stands and is strengthened: the "zero edges in owned free data" verdict now covers supervised-linear AND unsupervised-joint methods.

**CORRECTION RECORDED 2026-08-15 (session-memory error fixed): IVAMR is NOT untested and requires NO paid data.** The pre-registered probe ran 2026-08-08 on the cached Databento NQ 1-min 2013-2023 (fetched before the account lock) — DISCONFIRMED, all 5 gates failed (IS net −1096.89, OOS net −3695.53, OOS wr 0.479, PF 0.78, kill-switch days 51.9%; gate 6 look-ahead PASSED). Evidence: `strategies/ivamr/IVAMR.md` §10, `research/ivamr/outputs/probe_summary.json`. **All three Stage-2 moat candidates are now CLOSED on evidence: order-flow DEAD, dealer-gamma DEAD, IVAMR DISCONFIRMED. The buy-vs-stop fork on paid intraday data is decided — there is nothing left in the Stage-2 list that requires purchase.**

### 8.16 Stage-1 derive pass — Dataset E (crypto perps, BTC/ETH) — RESULT: 1 gate-survivor, DISCARDED on interrogation; 0 harness candidates

`derive_mine5.py` + `interrogate_mine5.py`, spec `research-specs/crypto-perps-derive-spec.md` (frozen 2026-08-16 before any fetch or code). The final untested asset class: Binance USDⓈ-M perpetuals, free `data.binance.vision` monthly 1m klines + 8h funding, 2020-01-01 → 2026-07-31 (2,404 full UTC days, zero missing minutes, zero OHLC violations — QA clean). BTC primary, ETH as pre-registered OOS asset check. 12 pre-registered tests, 3 axes (time-of-day, session/funding-anchor + calendar, vol/funding-state). Closed cells honored: hedged funding-carry construction and MVRV timing NOT re-tested. Binance key verified working before the scan.

**Results:** 11/12 dead outright. **1 gate-survivor: tds2 (first-hour 00:00-01:00 UTC vol → rest-of-day return): BTC tIS +4.06/tOOS +4.02 (r +0.106/+0.129), ETH asset check tIS +3.10/tOOS +2.83 — passes the frozen same-sign |t|>=3.29 + asset-check bar.** Calendar family all dead (Mon/Sun/weekday effects |t|<2.1); funding-state directional predictor vs4 dead (t −1.05/+0.80); vol-state vs1-vs3 dead.

**Interrogation (per protocol): DISCARDED.** The survivor fails every robustness test and has no stable why:
- Spearman ≈ 0 (BTC rho +0.025/+0.047, t 0.95/1.46; ETH +0.039/+0.003) — relationship is not monotonic; the Pearson is carried by a handful of extreme days.
- Trimming |rest-of-day| ≥ 5% (~9% of days) collapses it: BTC t 4.06→0.39; ETH OOS flips sign (t −0.67).
- Quintiles U-shaped, not monotonic (Q1 and Q5 positive, Q2-Q4 ≈ 0/negative) — no implementable "high vol → long" rule.
- The tradable high-quintile-vs-low-quintile spread fails the bar: t 1.04/1.80 (BTC), 0.83/0.34 (ETH).
- By-year decomposition shows regime dependence: effect INVERTED in the 2022 bear year (BTC hi −27bp vs lo −12bp) and in 2023/2024 on both assets — present only in bull phases, i.e. a bull-market beta artifact, not a structural edge.
- Vol-clustering check: h1_vol is persistent (r=+0.51 vs prev-day vol6) but prev-day vol predicts nothing (r=+0.02) — the correlation lives only in same-day extremes.

**Verdict: Dataset E exhausted — 0 harness candidates. The derive program is now complete across ALL owned free-data asset classes (equity panel, US equity options, equity-index futures, crypto perpetuals) and both functional forms (supervised-linear, unsupervised-joint). The §8.14 closure ("zero objective edge above friction in owned free data at our scale") now covers the final untested market. No paid-data purchase is warranted by any surviving observation.**

Data and scripts: `research/crypto-perps/` (fetch_data.py, derive_mine5.py, interrogate_mine5.py; raw monthly zips + parquets in gitignored cache/). Note: fetch required two structural fixes (2022+ kline files carry a header row; funding files use calc_time/last_funding_rate) — recorded in the spec's QA log.
