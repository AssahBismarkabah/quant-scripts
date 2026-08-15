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
