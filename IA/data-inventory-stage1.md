
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
