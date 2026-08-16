# Crypto Perpetuals Derive Pass — Research Spec

**Status:** PRE-REGISTERED 2026-08-16 — grid frozen before any fetch or code. No post-hoc test selection.

**Type:** Pre-registered derive-pass scan (dataset E of the derive program; method per `../IA/derive-pass-stage1-spec.md`).

**Purpose:** The derive pass covered options (A), PEAD (B), NQ/ES intraday linear (C), NQ/ES unsupervised joint-state (D) — all zero-survivor. Crypto perpetuals were never scanned with this method. Prior crypto work was narrow: MVRV valuation-timing DISCONFIRMED (deep probe, Coin Metrics) and the funding-basis hedged-carry candidate Rejected (2 months, June-July 2026, explicitly narrow by its own record). This scan tests the untouched predictive-state families on multi-year perp data with the same frozen-grid method, so the verdict is comparable and trustworthy.

**Closed cells (NOT re-opened under any name, per `../IA/path-forward-decision-memo.md`):**
- Hedged funding-carry construction (spot-long / perp-short P&L) — closed, NOT in this grid.
- MVRV / on-chain valuation timing (Coin Metrics) — DISCONFIRMED, NOT in this grid (and not in this data anyway).
- VRP family, vol-fade, index-rebal, IVAMR — unrelated to this data; untouched.

A funding-state feature (vs4) is included ONLY as a directional predictor of perp returns. If it survives, adjudication must show it is NOT the carry cell restated (no two-leg P&L, no funding-collection construction) before any advancement.

## 1. Data (owned-free, verified reachable 2026-08-16)

- **Source:** Binance `data.binance.vision` (free, keyless, no rate limits): monthly USDⓈ-M futures kline + fundingRate files.
- **Primary asset:** BTCUSDT perpetual, 1m klines, 2019-09-10 (perpetual launch) → latest complete month. Also BTCUSDT fundingRate (8h snapshots).
- **OOS asset check:** ETHUSDT perpetual, 1m klines, 2019-11 → latest (ES-analog; any survivor must reproduce directionally there).
- **Cache:** `research/crypto-perps/cache/` (gitignored); outputs `research/crypto-perps/outputs/`.

## 2. Unit and horizon

- **Unit of observation: one day (UTC).** Crypto trades 24/7; day = 00:00-24:00 UTC, aligned so the 08:00/16:00/00:00 UTC funding settlements fall inside well-defined windows.
- **Features:** scalar states known at time t (computed from bars ≤ t). Forward returns: remainder-of-day or next-window, all fully lagged (no contemporaneous use of the predicted window).
- **Method (frozen, per Dataset C/D):** per-day series; Pearson correlation of state vs forward return; IS/OOS 60/40 split by date; survivor requires same sign AND |t| ≥ 3.29 (Bonferroni for 12 tests) in BOTH halves.

## 3. Frozen grid — 12 tests, 3 axes

Unit = UTC day. Let h1 = 00:00-01:00 UTC, h_last = 23:00-24:00 UTC, rest-of-day = 01:00-24:00 UTC.

### Axis 1 — Time-of-day structure (4 tests)
| id | state (at t) | forward | meaning |
|---|---|---|---|
| tds1 | first-hour return r(00-01) | rest-of-day return r(01-24) | does the first hour predict the rest? |
| tds2 | first-hour log-vol (range/|ret|) | rest-of-day return r(01-24) | does early vol predict direction? |
| tds3 | last-hour return r(23-24) | next-day first-hour r(t+1, 00-01) | does the close predict tomorrow's open? |
| tds4 | morning-half return r(00-12) | afternoon-half return r(12-24) | morning/afternoon carry? |

### Axis 2 — Session/funding-anchor & calendar structure (4 tests)
| id | state (at t) | forward | meaning |
|---|---|---|---|
| sb1 | hour return r(07-08) (before 08:00 UTC funding settlement) | next-8h return r(08-16) | is the funding-settlement hour informative? |
| sb2 | Monday h1 return | Monday rest-of-day return | Monday-first-hour effect (weekly reset)? |
| sb3 | weekend (Sat+Sun, 48h) day returns vs weekday day returns | — | Welch on equal-weight daily series; weekend effect? |
| sb4 | weekday effect: each of Mon-Fri mean day-return vs others | — | Welch per weekday vs rest, Bonferroni over 5 | 

(Calendar tests sb2-sb4 are time-series market effects, NOT rank-IC, per the Dataset B method note.)

### Axis 3 — Vol-state & funding-state transitions (4 tests)
| id | state (at t) | forward | meaning |
|---|---|---|---|
| vs1 | trailing 7-day log-vol percentile | next-day return r(t+1, 00-24) | high/low vol regime → direction? |
| vs2 | vol up-switch (7d vol ≥ 1.5× prior 7d vol) | next-day return | vol-shock → direction? |
| vs3 | trailing 7-day return | next-day return | weekly momentum/reversal? |
| vs4 | trailing 7-day mean funding rate (8h snapshots) | next-day return | extreme funding → direction? (directional only; carry construction out of scope) |

## 4. Gates (survivor requirements — FROZEN)

1. Same sign in IS and OOS, |t| ≥ 3.29 in BOTH (Bonferroni, 12 tests).
2. Effect must reproduce in the ETHUSDT asset check (same sign, |t| ≥ 2.0 there — asset check is weaker by design, asset ≠ time replication).
3. No look-ahead: any feature later found to use data from the predicted window fails and is re-run with the fix applied to both windows.
4. A survivor without a why is discarded (per derive-pass §6 anti-result-hunting).

**Zero survivors is a valid result** — it extends the "zero edges in owned free data" verdict to the final untested asset class and closes the derive program across markets.

## 5. Data QA gates (before scanning)

- OHLC sanity: high ≥ low ≥ open/close within tolerance; no zero-price bars in the predicted windows (known artifact class); duplicate/NaN timestamps dropped with count logged.
- Funding file coverage ≥ 90% of expected 8h snapshots over the sample.
- If BTCUSDT or ETHUSDT perp kline history is unavailable or corrupt for any month, the month is dropped and the gap logged — not silently interpolated.

## 6. Status log

- **2026-08-16:** Grid frozen above. Binance access verified (key valid, futures account reachable; data.binance.vision HTTP 200). Closed cells recorded. Cache dir gitignored. Next: fetch script → download → scan script → run.
- **2026-08-16 (fetch QA):** Download complete — BTCUSDT + ETHUSDT 1m klines and 8h funding, 2020-01-01 → 2026-07-31. 2,404 full UTC days each, 3,461,760 kline rows each (every minute present), 7,212 funding snapshots each, zero duplicate timestamps, zero OHLC violations, zero NaN. Gaps logged: kline/funding files 404 for 2019-09..2019-12 (perpetual data begins 2020-01; both months dropped per QA gate, not interpolated). Structural fixes recorded: 2022+ monthly kline files carry a header row (stripped + dtype coerced); futures funding files use `calc_time`/`last_funding_rate` columns.
- **2026-08-16 (scan RESULT):** 11/12 tests dead on BTC. **1 gate-survivor: tds2 (first-hour vol → rest-of-day return), BTC tIS +4.06/tOOS +4.02, ETH asset check +3.10/+2.83.** Interrogation (Spearman, trim, quintiles, high-vs-low spread, by-year regime, vol-clustering controls) — **DISCARDED**: Spearman ≈ 0, trim |rest|≥5% collapses it (ETH OOS flips sign), quintiles U-shaped, spread t 1.04/1.80, effect inverted in the 2022 bear and 2023/2024 (bull-phase beta artifact, no stable why). **Verdict: Dataset E exhausted, 0 harness candidates. Recorded §8.16 of `../IA/data-inventory-stage1.md`.**
