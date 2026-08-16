# Stage-1 Free-Data Derive Pass — Pre-registered Spec

**Date:** 2026-08-15
**Type:** Pre-registered research program (the derive-from-data method from `edge-discovery-direction.md` §3/§7, never previously run).
**Purpose:** Mine data we already own for a repeatable observation -> objective machine-executable condition -> why -> harness. Ends with either a surviving edge, a documented exhausted-dataset record, or the Stage-2 paid decision.

## 1. Method (frozen)

For each dataset, in order:

1. **Define the scan space explicitly, in advance** (axes: which variables, which transforms, which horizons). Written down BEFORE running.
2. **Compute the candidate grid**: a wide set of predictive state variables (dozens to hundreds), each a daily/weekly time series.
3. **Screen honestly, multiple-testing-aware**: each candidate tested IS/OOS with the fixed harness. Because we scan many candidates, false positives are expected by chance — the gate must account for that (BH/FDR-style threshold AND IS+OOS consistency AND a t-threshold that survives a multiplicity adjustment).
4. **Observation -> why**: only survivors with a coherent economic why (who is forced, why they pay) proceed. A survivor without a why is noise-fit and discarded.
5. **Full harness on survivors**: bootstrap p5 > 0 net of friction, IS/OOS consistency, tail gate (no strategy whose required trade is in the VRP family that already failed).

**Anti-result-hunting rules (pre-registered, apply to all scans):**
- The scan grid is written before results are seen; adding candidates after seeing winners is forbidden.
- No survivor is accepted on IS alone; OOS must agree in sign.
- No survivor is accepted without a why.
- A scan that produces zero survivors is a valid result ("dataset exhausted for this grid").
- The VRP family (short-vol trades) is closed regardless of any surface result.

## 2. Datasets (owned, free, in priority order)

| # | Dataset | Location | What it gives us that papers don't re-test |
|---|---|---|---|
| A | LambdaClass SPY options 2008-2025 (24.7M rows) | `/tmp/lambda_spy.parquet` | Full per-strike OI, volume, IV, greeks, bid/ask. Tested: IV level, skew, PC volume, hedge flow, dealer gamma (all dead). **Untested axes: OI change dynamics, OI walls/concentration by strike, IV surface shape (curvature/term), volume-OI ratio, spread-of-options, moneyness-concentration shifts, day-of-week/expiry-week structure.** |
| B | PEAD panel (2.4GB, ~5k US names 1998-2021) | `research/pead/` | Cross-sectional daily prices + dividends. Tested: momentum, reversal, lowvol, liquidity. **Untested axes: overnight vs intraday return split, earnings-adjacent structure, calendar microstructure, size-liquidity interaction timing.** |
| C | NQ/ES intraday 1-min (Databento, dead account but cached) | `research/order-flow/cache/`, `research/relative-value/` | Tested: aggression, quote imbalance, opening-range momentum, VWAP pullback. **Untested axes: time-of-day return structure beyond opening range, session boundary effects, volatility-state transitions (regime-dependent means).** |
| D | EDGAR full-text (concurrent moat lane, optional) | fetch pipelines exist | Untested entirely. |

## 3. Gate (frozen)

A candidate **survives screening** iff:
1. IS t-stat and OOS t-stat have the same sign;
2. |IS t| and |OOS t| both exceed the multiplicity-adjusted threshold (Bonferroni for n_candidates at 0.05, or FDR q<0.10 — stated per scan);
3. The implied trade is not in the closed VRP/short-vol family;
4. A why exists (forced counterparty or documented behavior), recorded in the scan output.

Then the full harness (bootstrap p5 > 0 after friction 3-6 bps, IS/OOS, tail gate).

## 4. Status

- **2026-08-15:** Spec written. First scan: Dataset A (options) — grid to be listed next before running.
- **2026-08-15b:** Dataset A complete — 2/56 survivors, both rejected (§8.11): PC-OI ratio collapsed under IV control (VRP restated); call-volume-share passed IV+dbl-demean controls and bootstrap p5 (+13.6 bps) but failed the −40% tail gate (DD −80.6%). Grid exhausted.
- **2026-08-15c:** Dataset B complete — 5/12 cross-sectional survivors are all re-discoveries of public anomalies already killed in Step 2b (rev1m/mom12-1/lowvol families on the same panel); calendar family (time-series method, 3 tests) all dead; earnings axis underpowered (0.7% match). No new observation → no harness candidate. Grid exhausted (§8.12). **Method note recorded: cross-sectional candidates are tested via daily rank-IC series (~5,900 days), NOT row-count t-stats; calendar dummies are constant cross-sectionally so they are tested as time-series market effects, not rank IC.**
- **2026-08-15d:** Dataset C grid frozen (below) BEFORE scan code. Next: implement + run.
- **2026-08-15e:** Dataset C complete — 0/12 survivors on NQ, 0/12 on ES (§8.13). Two contemporaneous self-correlation artifacts (cc_ret vs today-OC; f_vol_pct vs today-h1) caught via absurd t-stats and fixed by lagging before accepting any verdict. **Derive pass FINAL (§8.14): all three datasets exhausted — Dataset A 2/56 rejected, B 5/12 public rediscoveries, C 0/24. No objective edge above friction in owned free data. Stage-2 paid-vs-stop decision point reached.**
- **2026-08-15f:** **Dataset D (unsupervised joint-state scan) grid frozen below — the last untried blueprint method (Phase 2 unsupervised anomaly/regime detection, IA/Blueprint-for-the-Independent-Quant.md).** Rationale: all prior scans were single-feature LINEAR tests; unsupervised joint-state detection (Isolation Forest anomaly score + K-means regimes) asks "is today's COMBINATION of features unusual, and do joint states predict forward returns?" — a different functional form that linear correlations cannot see. Weak prior (everything else on this data died), cheap, data owned. Either finds a joint-state observation or closes the method inventory completely.
- **2026-08-15g:** Dataset D complete — **0 survivors of 12** (6 NQ, 6 ES; ES best T1 tIS +1.37/tOOS +3.01 fails IS bar). §8.15. Anomaly score ≈ vol+volume in disguise, both already dead. **Method inventory COMPLETE: every blueprint method runnable on owned free data has now been run (supervised-linear AND unsupervised-joint). The "zero edges in owned free data" verdict now covers both functional forms. Derive pass FINAL stands (§8.14) — the buy-vs-stop fork is decided on evidence; nothing in the Stage-2 list requires purchase.**
- **2026-08-16h (Dataset E — crypto perps, BTC/ETH):** New pre-registered scan (spec `research-specs/crypto-perps-derive-spec.md`, frozen before any fetch). Binance free `data.binance.vision`: BTCUSDT + ETHUSDT USDⓈ-M perpetual 1m klines + 8h funding, 2020-01 → 2026-07 (2,404 UTC days, QA clean). 12 tests, 3 axes (time-of-day, session/calendar, vol/funding-state); closed cells (funding-carry, MVRV) excluded. **11/12 dead; 1 gate-survivor (tds2 first-hour vol → rest-of-day: BTC +4.06/+4.02, ETH asset check +3.10/+2.83) — DISCARDED on interrogation** (Spearman ≈ 0; trim |rest|≥5% collapses it, ETH OOS flips sign; quintiles U-shaped; spread t 1.04/1.80; effect inverted in 2022 bear and 2023/24 — bull-phase beta artifact, no why). §8.16. **Derive program now COMPLETE across all owned free-data asset classes (equity panel, equity options, index futures, crypto perps). Zero harness candidates anywhere; §8.14 closure strengthened, not weakened — the one gate-passer died exactly as the interrogation pattern was designed to catch it.**

## 6. Dataset D (NQ/ES intraday, unsupervised joint-state) — frozen grid (2026-08-15)

Data: same as Dataset C. Unit: **one day**. Features (all known at time t, from first hour + prior days): h1_ret, h1_vol, h1_range/close, h1_volume (log), h1_vol/prev20d_vol, gap, prev-cc_ret, h1 vol skew (max 1-min |move| / h1_vol). Standardized cross-sectionally (z-score over days, rolling-60d for vol percentile) BEFORE any model.

**Method (frozen, 6 pre-registered tests):**
1. **ISO-ANOM → rest-of-day (10:30→16:00):** Isolation Forest (n_estimators=200, contamination=0.10) trained on IS days only; anomaly score (rank-normalized) correlated with same-day remainder return. IS/OOS same sign, |t|>=3.29 both halves.
2. **ISO-ANOM → next-day OC:** same score, next-day open-to-close return.
3. **ISO top-decile vs rest → rest-of-day:** mean remainder return of top-10% anomaly days vs all others, Welch t-test, both halves.
4. **ISO top-decile vs rest → next-day OC.**
5. **KMEANS-3 regime → rest-of-day:** K-means (k=3, n_init=10) on the 9 features, IS-trained; forward return mean of the highest-anomaly cluster vs the rest, Welch t-test, IS/OOS.
6. **KMEANS-3 regime → next-day OC.**
ES (2020-2026) = out-of-sample asset check for any survivor (model refit, same frozen features).

**Anti-result-hunting (pre-registered):** features and k fixed before results; contamination 0.10 fixed; no hyperparameter tuning after seeing scores; a survivor without a why is discarded; VRP family closed. Zero survivors is a valid result — the method inventory is then complete. Any survivor gets the interrogation pattern (controls vs vol/momentum/calendar, why) then full harness.

## 5. Dataset C (NQ/ES intraday) — frozen grid (2026-08-15)

Data: NQ 1-min 2013-11→2023-12 (`research/ivamr/cache/NQ_n_0_1m.parquet`, ~973k rows), ES 1-min 2020-08→2026-08 (`research/relative-value/cache/ES_n_0_1m.parquet`, ~597k rows). Session 09:30-16:00 ET. Unit of observation: **one day** (per-day scalar states, ~2,530 NQ days / ~1,550 ES days) — t-stats on the day-series, NOT on rows.

**Test method (frozen):** each candidate = scalar state known at time t → correlate (Pearson) with a forward return (remainder-of-day or next-day). Per-day series, IS/OOS split by date, same-sign + |t|>=3.29 both halves (Bonferroni for 12 tests; 3.29 is conservative). Tested on NQ (2013-2023) with ES (2020-2026) as an out-of-sample asset check for any survivor.

**Axis 1 — time-of-day structure beyond opening range (4):**
- tds1: hour-2 return (10:30→11:30) → remainder-of-day (11:30→16:00)
- tds2: hour-1 return (09:30→10:30) → hour-2 (10:30→11:30)
- tds3: last-hour return (15:00→16:00) → next-day open-to-close
- tds4: morning return (09:30→12:00) → afternoon (12:00→16:00)

**Axis 2 — session boundary effects (4):**
- sb1: overnight gap (today open vs prev close) → same-day open-to-close
- sb2: Friday close→Monday open gap → Monday open-to-close
- sb3: prev-day close-to-close return → next-day overnight gap (gap continuation vs fade)
- sb4: prev-day close-to-close return → same-day open-to-close

**Axis 3 — volatility-state transitions (4):**
- vs1: prev-day realized vol percentile (vs own 60d) → today first-hour return
- vs2: prev-day realized vol percentile → today remainder-of-day (10:30→16:00)
- vs3: vol-regime up-switch (percentile crosses 80th) → next-day open-to-close
- vs4: first-30-min vol vs prev-20d avg vol → remainder-of-day

**Pre-stated adjudication:** survivors get the interrogation pattern (control for known-dead confounds: gap continuation = momentum family? volatility = VRP? hour-2 = opening-range-momentum variant already dead?) then full harness. Zero survivors is a valid result. Then the Stage-2 paid-vs-stop decision point is reached.
