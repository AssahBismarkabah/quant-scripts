# Data Inventory for Stage 1 Free-Data Derive Pass

**Date:** 2026-08-13
**Type:** Data inventory / working reference. Records what data assets we own, their shape and limits, so the Stage 1 free-data derive pass (`edge-discovery-direction.md` §7) has a single source of truth for what can be tested. Not a research spec; no gates pre-registered here.
**Audience:** self. Used to pick what to run the derive method on and to avoid re-verifying data repeatedly.

---

## 1. Purpose

`edge-discovery-direction.md` §7 established the forward path: run the derive-from-data method (mine data -> observe -> objective rule -> why -> validate) on **free data we already own** before considering any paid moat (Stage 2). This document is the inventory of that free data: exactly what we have, where, its coverage, and its known caveats. It also records the SEQUENCING decision: which dataset the Stage 1 pass starts with.

Everything here is local, already-paid-for, cost-0 to use. No purchase, no new API dependency required for the ones marked as have.

---

## 2. Inventory of owned data (on disk)

### 2.1 Cross-sectional equity panel (HIGHEST breadth — primary Stage 1 target)

| Item | Source path | Shape | Coverage | Notes |
|---|---|---|---|---|
| PEAD price panel | `research/pead/cache/prices_adj_long.parquet` | 24,390,016 rows × [symbol, date, close_adjusted] | 7,786 symbols, 1998-01-02 → 2021-06-14 | **Best asset for a cross-sectional derive pass.** Daily adjusted close, near-full US market breadth, 23 years. Supports size/reversal/momentum/low-vol/liquidity/seasonality factorizations with real statistical power. |
| Raw stock prices | `research/pead/cache/stock_prices_latest.csv` | 1.9G CSV | (full sample) | Unhandled/greater coverage for the same universe; use `prices_adj_long` for clean adjusted work. |

### 2.2 Intraday / microstructure (the direction `edge-discovery-direction.md` pushes toward)

| Item | Source path | Shape | Coverage | Notes |
|---|---|---|---|---|
| NQ 1-min (fresh) | `research/nq-vwap-pullback/cache/NQ_n_0_1m.parquet` | 597,028 rows × [ts,date,o,h,l,c,volume] | 2020-08-03 → 2026-08-06 (~1,551 days) | **Freshest intraday we own.** Includes the recent 2024-26 regime. Natural home for microstructure-derived observations. |
| NQ 1-min (older) | `research/ivamr/cache/NQ_n_0_1m.parquet` | 973,224 rows × [ts,date,o,h,l,c,volume] | 2013-11-01 → 2023-12-29 (~2,527 days) | IVAMR's dataset. Longer history, stops before 2024. |
| NQ 1-min chunks | `research/ivamr/cache/chunks/`, `research/nq-vwap-pullback/cache/chunks/` (124 months) | monthly parquet | extends the two 1m files | Full granular monthly breakdown; use to extend/recompute either 1m series. |

### 2.3 Index / vol / macro series

| Item | Source path | Coverage | Notes |
|---|---|---|---|
| SPY clean long | `research/vol-targeting/cache/SPY_clean_long.parquet` | 1993-02-01 → 2026-07-31 (8,427 rows) | **Verified clean** OHLCV; the reliable long-equity line. |
| SPY variants | `research/vol-targeting/cache/SPY_clean.parquet`, `SPY_long.parquet`, `SPY_yahoo.parquet` | short / long / raw | Use `SPY_clean_long` for analysis; `SPY_clean` is short research series. |
| VIX / S&P | `research/vol-targeting/cache/VIXCLS.csv`, `SP500.csv` | 1990s → present | Closes. |
| CBOE vol idx | `research/vol-risk-premium/cache/VIX.csv`, `VIX3M.csv`, `VIX9D.csv` | official | Structure products (VIX3M/VIX9D). |
| Vol ETPs | `research/vol-risk-premium/cache/SVIX.parquet`, `SVXY.parquet`, `VXX.parquet` | | Implied/realized vol exposures for vol-risk work. |
| Single-name bars | `research/index-rebalancing/cache/bars/` (1,259 daily parquet) + `benchmark` + `calendar.parquet` | | Universe for index-rebal / rebal-date microstructure. |

### 2.4 Event / corporate-action panels

| Item | Source path | Notes |
|---|---|---|
| Buyback events | `research/buyback-timing/events/buyback_events.parquet`, `buyback_programs`, `buyback_events_ticker` + `cache/*.parquet` (~50 names) | BUFO-style corporate action timing. |
| 10b5-1 adoptions | `research/10b5-1-timing/events/adoption_events.parquet` + `cache/{SAM,SPY,TKO}.parquet` | Insider-trading-program adoption timing. |

### 2.5 Crypto

| Item | Source path | Notes |
|---|---|---|
| MVRV | `research/bitcoin-mvrv/cache/mvrv.parquet` (5,867 rows × [asset,CapMVRVCur,CapMrktCurUSD,CapRealUSD,supply,price]) | Coin Metrics, keyless. BTC realized/market cap. |

---

## 3. Live free sources still reachable

| Source | IDs available | Status |
|---|---|---|
| FRED (keyless) | DGS10, DGS2, T10Y2Y, DTB3, DEXUSAL, DEXUSEU, DCOILWTICO, IR3TIB01AUM156N/USM156N | **Working** — used in step2b. Terms/FX/oil/rates. |
| Yahoo Finance | chart API | **429 rate-limited** — not dependable for new pulls. |
| Stooq | | **Blocked** (JS proof-of-work). |
| CryptoQuant (`.env`) | | 403 on realized-cap. |

Rule of thumb: for NEW symbols rely on what is cached + FRED. Do not depend on Yahoo/Stooq.

---

## 4. Known data caveats (carry into every derive pass)

- PEAD panel ends **2021-06** (no 2021-26). It is history for cross-sectional discovery, not live/recent validation.
- The freshest recent intraday is the **nq-vwap-pullback** 1m (2020-2026); IVAMR 1m ends 2023-12.
- `SPY_clean` is a short research series; use `SPY_clean_long` for long-history work.
- Crypto: only BTC MVRV lineage; Yahoo/Stooq/CryptoQuant unreliable.
- Do not use the corrupted EQUS.MINI cache (per `data-and-portfolio-roadmap.md` rejects) — only the verified SPY lineage.

---

## 5. Sequencing decision — what we START the Stage 1 pass with

**Decision (2026-08-13):** the Stage 1 derive pass opens on the **PEAD cross-sectional panel** (`prices_adj_long.parquet`) as the primary target, because it has the most breadth (7,786 names) and longest clean history (23 yrs) of anything we own, which is exactly what a derive-then-validate needs to distinguish a real cross-sectional observation from noise.

Order of attack (Stage 1 = free-data derive pass):
1. **PEAD cross-sectional panel** — primary. Mine for an objective, machine-executable, cross-sectional observation with a why (e.g. a liquidity/reversal/size/seasonality condition) → run through the existing harness (IS/OOS split, Monte Carlo/reshuffle, friction). 
2. If #1 yields nothing, pivot to **fresh intraday** (`nq-vwap-pullback` 1m, 2020-2026) for a microstructure-derived observation — the direction the docs flag as the one with a genuine moat (order flow).
3. Then **IVAMR** 1m (2013-2023) if the fresh intraday shows anything worth extending longer.
4. Lucene-only / lower-breadth (vol series, event panels, MVRV) only if the above are genuinely mined out.

A hard rule: the derive method, not another pre-specified public anomaly, and no purchase before the free lane is genuinely exhausted.

---

## 6. Stage 1 first pass — observed data behavior (PEAD panel)

Explored the PEAD panel on 2026-08-13 (raw observation, no hypothesis yet). Recorded so the derive pass accounts for these structural facts.

### 6.1 Verified panel structure
- 7,786 symbols, 5,901 unique trading dates (daily), 1998-01-02 → 2021-06-14.
- Real full-market cross-section: AAPL/MSFT/IBM/F/XOM present; ETFs like SPY NOT present (no `SPY` row). So this is single-name equities, not index/ETF.
- Breadth grows over time: ~2,035 active symbols in 1998 → ~6-7,000 in 2017-2021.
- Symbols enter/exit over time (long-lived names have ~5,900 obs; median ~2,816; min 12).

### 6.2 Data-quality behaviors that MUST be handled in any derivation
1. **Adjustment artifacts:** 19,646 rows (0.08%) have |one-day change| > 50%, including ±inf and a min of −4,996x. These are split/dividend-adjusted close artifacts, not real returns. Any momentum/reversal/low-vol feature is contaminated unless these are excluded or capped. A corrupted symbol exists at median price ~$27.7M (exclude).
2. **Stale/unchanged prices:** 7.9% of symbol-days are an **exact 0.0 change**. Per-year 15-17% in 1998-2002 falling to ~4-8% by 2019-2021. This is concentrated in illiquid/microcap names: 14% of symbols have >20% stale days; worst is 98% (dead/delisted shell). Real median cross-sectional daily return is exactly 0.000000 over the full sample because the median falls on a stale row.
3. **Microcap/penny weight:** 17% of symbols have median price < $5; ~3.7% are sub-$1 penny. Cross-sectional signals are therefore dominated by illiquid, hard-to-trade names unless liquidity-filtered.

### 6.3 Cleaned cross-sectional median daily return by year (excl. artifacts & stale zeros)
Sensible economic signature: + (2003, 2009, 2013, 2016, 2017, 2019, 2021) ; − (1998-2000, 2002, 2008). Confirms that after excluding the two artifact classes the panel reflects real market behavior.

### 6.4 Implication for the derive pass (candidate directions, not yet hypotheses)
- Any cross-sectional factor MUST (a) exclude/cap |one-day move| > ~50-100%, and (b) apply a liquidity screen (price + stale-share) or the signal is a microcap/low-liquidity artifact, not a tradeable edge.
- The strong, persistent, concentrated **stale-price dimension itself** is an observable worth inspecting: a "how dead is this name" / liquidity-graded universe is a derived structure we can build objective rules on top of.
- The cleaned panel supports standard cross-sectional factorizations (momentum, reversal, low-vol, size) once the two noise classes are stripped.
- NOTE: panel ends 2021-06 — it is history for discovery, not recent/live validation.

---

## 7. Status

- **2026-08-13:** Document created as the working inventory + Stage 1 sequencing record. First exploration of the PEAD panel completed (Section 6 records the observed data behavior). Next action: convert one observed behavior into an objective, machine-executable condition with a why, then run it through the harness (IS/OOS, Monte Carlo, friction).
- **2026-08-13 (first derive pass):** Ran the liquidity/staleness descriptive scan (`research/pead/derive_liquidity_scan.py`, outputs `research/pead/outputs/liquidity_scan_summary.csv`). Result and verdict below.
- All changes uncommitted (per standing policy). This file is a reference; it does not pre-register gates.

### 7.1 First derive-pass result — liquidity/staleness dimension (measured, not an edge)

Objective condition tested (point-in-time, no lookahead): trailing-21d fraction of exact-0 daily changes (stale_share) + trailing median price, rank-tiled cross-section into 5 quintiles per date; forward equal-weight returns at 1/5/21d. Split IS (<2010) / OOS (≥2010). Run in `research/pead/derive_liquidity_scan.py`.

| Set | 1d tile0→tile4 | 5d tile0→tile4 | 21d tile0→tile4 |
|---|---|---|---|
| IS-all | 6.8→14.5 bps | 31.8→52.2 | 118.6→162.5 |
| OOS-all | 5.7→12.4 | 26.8→41.6 | 104.6→126.7 |
| **IS-liquid** | 4.8→2.5 | 22.1→15.1 | 81.1→51.6 |
| **OOS-liquid** | 4.7→2.1 | 23.1→11.7 | 94.0→44.8 |

(tile 0 = least stale/most liquid; tile 4 = most stale/least liquid. "liquid" = median price > $5 AND stale_share < 25%.)

**Finding:**
- On ALL names, the most-stale tile has HIGHER forward returns than the least-stale at every horizon (IS and OOS) — e.g. OOS 21d 126.7 vs 104.6 bps. Pattern is consistent across both halves.
- On the LIQUID-ONLY screen (the names we could actually trade), the direction REVERSES: most-stale tile now earns LESS (OOS-liquid 21d 94.0 vs 44.8). No monotone, economically strong spread survives in the tradable universe; the residual is weak and horizon-dependent.

**Verdict:** the "staleness → higher forward return" pattern is a **microcap/illiquid-price artifact**, not a tradeable edge. It fails exactly the honesty control (liquid-only screen) the plan built in — mirroring step2b's short-side microcap trap. **Measured dead-end for this dimension as a standalone signal.** No member-dropping / no re-tuning / no cell-selection; this is the recorded outcome.

**Notable for future passes:** the stale/illiquid universe is where fake edges live. Any future derived observation from this panel must be screened to liquid-only from the start or it will repeat this artifact. The tradable direction seen here (mildly higher forward return on the most-liquid end) is weak and non-monotonic — not pursued without a stronger, mechanistically-grounded why.

### 7.2 Second derive pass — short-horizon momentum & conditional liquidity (measured, friction-eaten)

Built on the first-pass finding by restricting to the **liquid-only universe** from the start (median price > $5 AND stale_share < 25%; 18.4M rows, 7,409 symbols). Script `research/pead/derive2_liquid_scan.py`, outputs `derive2_reversal_summary.csv`, `derive2_conditional_summary.csv`. Split IS (<2010) / OOS (≥2010). All features point-in-time/no-lookahead.

**Observation A — short-horizon prior-return momentum (NOT reversal):** tiling the liquid cross-section by prior-1d (and prior-5d) return, forward equal-weight returns are **monotone momentum**: prior winners keep winning, losers keep losing. Consistent both halves.

| Prior-5d tile (0=winners → 4=losers) | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| OOS 5d | 50.3 bps | 28.5 | 24.9 | 20.5 | 14.9 |
| OOS 21d | 163.8 | 113.8 | 103.5 | 96.1 | 82.0 |

Gross long-winner minus short-loser spread (OOS): 5d = **35.4 bps**, 21d = **81.8 bps**. Strong and consistent IS/OOS.

**Net-of-friction verdict (the decisive gate):**

| Horizon | Gross spread | @10bps/side (4 sides) | @20bps/side (4 sides) | @50bps/side |
|---|---|---|---|---|
| 5d | 35.4 bps | −4.6 bps | **−44.6 bps** | −164.6 bps |
| 21d | 81.8 bps | 41.8 bps | **+1.8 bps** | −118.2 bps |

At 5d the momentum spread is friction-eaten at any realistic cost; at 21d it barely reaches breakeven at 20bps/side and is deeply negative at 50bps/side (and the equal-weight small/liquid names plus short-borrow costs would push it negative). **This is a gross cross-sectional momentum phenomenon that does not survive honest friction. Not a tradeable edge.**

**Observation B — conditional liquidity (stale_share tile) × prior-5d sign:** at 21d, within most-liquidity tile, prior-5d LOSERS show higher forward return than winners (OOS: 143.4 vs 89.0 bps) — i.e. reversal in the most-liquid names. This conflicts with Observation A's momentum framing (different marginal vs conditional cuts) and is equally gross/untested net-of-cost; **not claimed as an edge.**

**Verdict:** second derived observation also **measured dead-end under friction** — the PEAD panel's cross-sectional price structure produces gross anomalies (liquidity, short-horizon momentum) that all fail to survive realistic costs, consistent with the program's history and step2b. The derive method is working as designed: cheaply rejecting false edges on the panel.

### 7.3 Overall Stage-1 PEAD-panel status and next options

- PEAD panel has now contributed THREE measured dead-ends: (1) liquidity/staleness standalone, (2) short-horizon momentum net-of-friction, (3) conditional liquidity inconsistent/friction-untested. The panel's cross-sectional price-only structure (daily CLOSE only) offers gross effects but nothing that survives costs — consistent with the free-data, no-moat outcome the program already concluded.
- **Limitation surfaced:** the panel has daily CLOSE only (no open/high/low, no volume). It cannot measure overnight-vs-intraday, order size, or any microstructure — the dimensions the docs flag as needing a data moat. The PEAD panel is likely near its useful end for derive work.
- **Next options (to choose with user):**
  1. Move to the **fresh intraday NQ panel (2020-2026)** — the one free dataset that DOES have the microstructure dimension (O/H/L/C + volume at 1-min) and is the direction the docs flag as having a genuine moat (order flow). Highest-value next step.
  2. Try a genuinely different PEAD angle not yet covered (e.g. fwd-return conditioned on relative-volume-like proxies) — but the panel lacks volume/float, so limited.
  3. Accept that free-data cross-sectional derivation is exhausted on this panel and treat the intraday dataset as the remaining free lane before any paid-data Stage 2.

## 8. Status (updated)

- **2026-08-13 (second derive pass complete):** Ran derive2_liquid_scan.py on the liquid-only PEAD universe. Observation A = short-horizon momentum (gross, strong IS/OOS) but friction-eaten net-of-cost (5d: -44.6 bps at 20bps/side; 21d: +1.8 bps breakeven). Observation B = conditional liquidity x sign reversal, inconsistent with A and untested net-of-cost. Both recorded as measured dead-ends/not-claimed in sec 7.2. The PEAD panel (price-only) appears near its useful end for derive work.
- **2026-08-13 (intraday observation begun):** Moved to the fresh intraday NQ panel (Databento GLBX.MDP3 continuous NQ futures, RTH 09:30-16:00 ET, 1-min OHLCV, 2020-08 to 2026-08, 1,551 days). Observed intraday structure (vol/volume U-shape, daily range ~229 pts median) and a NEW DERIVED signal (opening-range direction persistence) that is the first observation to hold IS and OOS. See 8.1.
- All changes uncommitted (per standing policy). Reference doc, not a gate pre-registration.

### 8.1 Derived intraday observation — opening-range direction persistence (first promising signal)

Data: research/nq-vwap-pullback/cache/NQ_n_0_1m.parquet.

Observation: if the first 30 (or 60) minutes of the session close UP vs the open, the rest of the day (30-to-close / 60-to-close) tends to close UP too (+); if DOWN, rest-of-day tends DOWN. This is intraday open-direction momentum/persistence, structurally distinct from the already-disconfirmed claim-copied strategies (VWAP mean-reversion, ORB, IVAMR).

| Window | Split | N up/down | Long-up - short-down spread, rest-of-day |
|---|---|---|---|
| 30 min | IS | 589/550 | +5.4 bps |
| 30 min | OOS | 227/184 | +3.9 bps |
| 60 min | IS | 583/557 | +10.8 bps |
| 60 min | OOS | 220/191 | +4.2 bps |

Long-side (up-open to rest-day-up) is the robust leg: +4.5/+4.6 bps IS and OOS at both windows. The short side is weaker/noisier OOS. Effect is real, consistent sign across IS/OOS, but THIN (4-11 bps per day, gross before friction). NQ futures friction is small (~0.25 bps/side), so net survivability is plausible but NOT yet established.

Status: this is a derived observation (not a marketed-claim copy), survives the simple IS/OOS sign check, and is the first such candidate in the program. NOT yet a rule/an edge - needs the full house harness (pre-registered gate, bootstrap p5, friction, look-ahead audit) to decide. Next step: formalize into a proper pre-registered probe.

### 8.2 Intraday context (already-disconfirmed claim candidates on the same data)
- NQ VWAP-pullback (2026-08-08): DISCONFIRMED - intraday trend-follow-with-pullback + VWAP mean-reversion.
- IVAMR (Break-in-Breakout, 2026-08-08): DISCONFIRMED.
- ORB / Gap-Fill / Oops (2026-08-09): ORB and Oops DISCONFIRMED; gap-fill grouped.
The derive method on this data must therefore find something structurally new (as 8.1 does), not re-test these.

### 8.3 Pre-registered probe of the opening-direction signal (DISCONFIRMED on significance gate)

Built the pre-registered probe `research/opening-direction/run_probe.py` on the COMBINED NQ panel (IVAMR 2013-2023 + vwap-pullback 2020-2026; overlap verified identical, deduped -> 3,197 trading days, 2013-11..2026-08). Rule: each RTH day, enter at close of first 30/60 min in the direction of that open-to-W-min return, hold to session close. Split IS 2013-2024 / OOS 2025-2026. Friction 0.5 (base) / 1.0 (stress) pts/turn. House gates incl. bootstrap p5 (n=5000).

| Window_friction | IS net pts/d | OOS net pts/d | OOS PF | OOS boot p5 |
|---|---|---|---|---|
| W30 base | +1.20 | +1.85 | 1.03 | -15.95 |
| W30 stress | +0.70 | +1.35 | 1.02 | -16.45 |
| W60 base | +2.22 | +3.97 | 1.06 | -13.20 |
| W60 stress | +1.72 | +3.47 | 1.05 | -13.70 |

**Verdict: DISCONFIRMED.** Mean net PnL IS positive in both halves and clears friction (gates g1/g3/g5 pass), but gate g2 (bootstrap p5 > 0) fails badly (p5 = -13 to -16 pts/day). Root cause: the edge is a thin mean tilt (+1.85 pts/day) buried under huge daily PnL variance (std ~220 pts, range -1,153..+1,783 pts on OOS W30; 47% of days negative). The mean positive tilt is NOT statistically distinguishable from zero under the house significance bar. This mirrors vol-fade/step2: a real-looking mean effect rejected on statistical robustness due to fat tails. Correct disciplined outcome; no re-selection performed.

**Data note:** combining the two owned NQ panels doubled the sample to 3,197 days for free (overlap verified byte-identical). This is a reusable free-data extension; the same combined panel is available for any future intraday derive on NQ.

### 8.4 Relative-value derive on ES vs NQ (no structure — dead end)

Pulled ES continuous 1-min OHLCV RTH from Databento (`research/relative-value/cache/ES_n_0_1m.parquet`, 2020-08..2026-08, 597k bars, same window as NQ). Ran the derive method on the relative-value family (the doc's why-grounded, direction-agnostic family).

Observed relationship: ES & NQ 1-min return correlation = 0.92 (extremely tight co-movement); daily NQ-on-ES beta = 1.28. But:
- **No mean reversion:** hedged spread daily autocorr = 0.999, sign-flip rate 0.4% (random-walk drift, no spring). Time-varying NQ/ES ratio reflects tech-vs-market drift, not a reverting spread.
- **No short-horizon relative reversion:** after NQ outperforms ES in a 5-min window, next-5m relative deviation ~ 0, sign-reverse ~49-50% (coin flip). A pairs-fade on the relative deviation yields ~0 bps.
- **No lead-lag / no autocorrelation:** corr(ES_t, NQ_{t+1}) ~ 0.009, corr(NQ_t, ES_{t+1}) ~ 0.015, own-minute autocorr ~ 0.006-0.013 — all effectively zero. No exploitable lead-lag.

**Verdict: dead end.** The ES/NQ relative-value family shows no mean reversion, no lead-lag, no autocorrelation — structurally nothing to trade. Recorded; no re-tuning / no selection.

### 8.5 Stage-1 free-data derive pass — status (correction 2026-08-13)

**Correction:** the prior framing "free is measured exhausted" was too absolute. What the derive method has been run on this session: PEAD cross-section, NQ intraday, ES/NQ relative value — all dead-ended. BUT the derive lane is NOT fully exhausted yet:

| Data | Family/observation | Result |
|---|---|---|
| PEAD cross-section | liquidity/staleness | dead (microcap artifact) |
| PEAD cross-section | short-horizon momentum | dead (friction-eaten) |
| PEAD cross-section | conditional liquidity x sign | dead (inconsistent, no-why) |
| NQ intraday (combined 2013-2026) | opening-direction persistence | dead (bootstrap p5, no-why) |
| ES vs NQ intraday | relative value / pairs / lead-lag | dead (no mean reversion, no structure) |
| **SPY + vol suite (VIX/SVXY/VXX/SVIX)** | **vol-risk-premium family (V1 level, V2 short-vol, V3 tail-overlay)** | **CLOSED as DISCONFIRMED 2026-08-08** |
| **index-rebal single-name bars (1,259 names)** | **index-rebalancing price-pressure (Level-1 + Level-2)** | **CLOSED as REJECTED 2026-08-04** |

Every derived observation run was put through the harness (IS/OOS, friction, bootstrap p5) and recorded — no re-selection, no member-dropping.

### 8.5b CORRECTION — the "last lane" (index-rebal bars) is ALSO already closed

**Correction (2026-08-13):** this document earlier listed the index-rebalancing single-name bars (1,259 names, 2023-2026) as the only owned dataset "NOT yet run through the derive method." On inspection this is wrong: those bars are the **same universe used by the index-rebalancing study**, which was **already fully adjudicated and REJECTED** in `IA/index-rebalancing-research-spec.md` (Level-1 study 2026-08-04, Level-2 robustness/capacity/borrow 2026-08-04, candidate closed). Its event tables (`events/spdji_reconciled.parquet`, `events/r2000_events.parquet`, `events/study_events.parquet`) and complete outputs (`outputs/results_base.parquet`, `level2_*.parquet`, `s10_validation.parquet`) are all on disk. The short-additions 10td edge was rejected on the pre-registered "single-year dependence" gate (one March 2025 batch); long-deletions failed in-sample; Russell 2000 inverted. **The index-rebal bars are not a fresh lane** — they are the already-closed study's data.

### 8.5c COMPLETE Stage-1 ledger — every owned free dataset is now accounted for

Running the full inventory: PEAD (derive→dead), NQ (derive→dead), ES/NQ (derive→dead), SPY+vol (already closed), buyback/10b5-1 (already closed), BTC MVRV (already closed), index-rebal bars (already closed). **There is no owned free dataset left to derive on that is not already measured/closed.** Stage 1 (free-data derive at cost 0) is genuinely exhausted across the complete inventory. The remaining decision is the genuine Stage-2 fork: (2a) buy a data moat (order flow / options microstructure / long intraday history) and run the SAME derive method on it, or (2b) STOP and preserve capital — both legitimate, data-backed, non-failure outcomes per `edge-discovery-direction.md` §7 and `institutional-approach.md` §Data-moat.

### 8.5a CORRECTION — the vol-risk-premium family is ALREADY CLOSED (not "open")

**Correction (2026-08-13):** an earlier draft of this section wrongly labeled the VRP family "OPEN - not yet a dead end." This was incorrect. `IA/vol-risk-premium-research-spec.md` already ran and adjudicated the ENTIRE family on 2026-08-08:
- **V1** (unconditional VRP level): MEASURED-POSITIVE-LEVEL (premium exists) — but a level is NOT an edge.
- **V2** (naive short-vol buy-and-hold SVXY + VRP-regime-gated): **DISCONFIRMED** — −95% max DD / −83% single day; gate FAIL.
- **V3** (tail-overlay: term-inversion / elevated-rising-VIX / equity-drawdown exits): **DISCONFIRMED** — total −26%, skips the premium-rich regimes. Candidate **CLOSED 2026-08-08**; doc says "No paid data, no further work recommended on this family."

**What I derived fresh this session (2026-08-13), and why it is NOT a new edge:** I observed that short-vol gated to "VIX < 90th percentile of prior year" (hold short-vol in normal vol, flat when VIX already extreme) gives +2,699% total but **max DD −66% / worst day −26%**. That measured result **still FAILS the VRP V3 tail gate (bound: max DD < −40%)** — same tail-dominance failure that closed the family. The 2018 volmageddon tail comes through regardless of VIX-level gating, exactly as V2/V3's diagnostics established. This is a re-confirmation of the closed conclusion, NOT a new edge, and I nearly mis-read it as promising before checking the spec. **Verdict: the vol suite is not an open lane; the family is closed.** No further short-vol/VRP derive work is justified on this data.

**Data note (worth keeping):** SVXY/VXX/SVIX + VIX/VIX3M/VIX9D + SPY_long remain on disk and are free/owned, but their entire tradeable short-vol conclusion is already recorded as DISCONFIRMED. The index-rebal single-name bars (1,259 names) remain the one owned dataset not yet run through the derive method.

### 8.6 Stage-2 first paid-data test — NQ order flow (trades + bbo-1s), RESULT: DEAD

**Test (2026-08-14):** Bounded first paid-data purchase per Stage-2 moat direction #1 (order flow). Current Databento key already has access — no upgrade needed (verified: full MBO pull works; unit prices GLBX.MDP3 historical: mbo $1.80/GB, mbp-10 $0.50/GB, bbo-1s $18/GB, trades $28/GB).

**Key finding on size:** full MBO is NOT needed for a first derive pass — it's 4.4 GB/10d vs bbo-1s 0.04 GB and trades 0.12 GB. The two core order-flow observations (aggression delta, quote imbalance) only need `trades` (aggressor side) + `bbo-1s` (top-of-book sizes).

**What was bought:** 3 months of NQ continuous (2026-05-01 → 2026-08-01), $43.53 total: `research/order-flow/cache/NQ_trades_2026q2.parquet` (26.7M trades, columns action/side/price/size/sequence), `research/order-flow/cache/NQ_bbo-1s_2026q2.parquet` (5.3M 1-sec snapshots, bid_px/ask_px/sizes/counts). Fetch script `research/order-flow/fetch_flow.py`. Degraded days flagged: 2026-05-24, 2026-07-30. RTH filter applied (09:30-16:00 ET).

**Derive scan** (`research/order-flow/derive_scan.py`, `derive_scan5.py`), aggressor delta and quote imbalance vs next-period return, RTH only, bucket-quintile spread in bps:

| Horizon | delta_vol corr | delta_vol spread | imb corr | imb spread |
|---|---|---|---|---|
| 1 min | 0.057 | +0.7 bps | 0.012 | +0.1 bps |
| 5 min | 0.029 | +1.3 bps | −0.008 | −0.2 bps |
| 15 min | 0.002 | +0.9 bps | 0.015 | +1.3 bps |
| 60 min | −0.012 | +0.7 bps | 0.032 | +1.9 bps |

**Verdict: DEAD.** All spreads 0.1-1.9 bps vs NQ friction of ~1 tick (≈1.4 bps at these prices) — every observation is at or below friction, correlations near zero, sign unstable across horizons. The two classic order-flow observations (aggression delta, quote imbalance) show no exploitable structure on NQ futures at 1-60 min horizons. This mirrors every prior free-data derive: measured dead under honest costs. The order-flow moat purchase did not change the outcome at this level.

### 8.7 Stage-2 second paid-data test — single-stock order flow (40 mega/large-cap names), RESULT: DISCONFIRMED at pre-registered probe

**Test (2026-08-14):** The right venue for order-flow asymmetry is single stocks (retail/informed flow), not hyper-efficient NQ. Bought 3 months (2026-05-01 → 2026-08-01) of `trades` + `bbo-1s` for 40 mega/large-cap names via EQUS.MINI — **$23 total** (trades $11.28, bbo-1s $11.75; equities unit prices: trades $6/GB, bbo-1s $4/GB — far cheaper than futures). Files: `research/order-flow/cache/EQ_trades_2026q2.parquet` (26.7M rows), `EQ_bbo-1s_2026q2.parquet` (36.7M rows). Fetch `research/order-flow/fetch_equs.py`.

**Naive 5-min scan** (`derive_equs.py`, `derive_equs2.py`) — aggression delta (buy−sell vol) and quote imbalance (bid−ask size) vs next-bin return, RTH, per-symbol quintiles:
- delta_vol: mean spread **+3.16 bps** (IS +3.39 / OOS +2.97), 22/40 names > 2 bps; top MU +16.6, INTC +11.9, AMD +8.0, TSLA +7.0
- imb: mean spread **+4.50 bps** (IS +3.68 / OOS +4.85), 24/40 names > 3 bps OOS

First observation in the whole program with magnitude above friction. Monotonicity was poor (12%/2%) — a warning that went into the probe.

**Pre-registered probe** (`research/order-flow/run_probe_equs.py`): long when delta_vol in top quintile, flat otherwise, 1-bin hold, 3 bps round-trip friction, point-in-time rolling 200-bin threshold, IS first 60% dates / OOS last 40%, bootstrap n=5000 seed 42, drop-best-symbol. **Result: DISCONFIRMED.**
- IS: −0.134 bps/trade (t=−1.96); OOS: −0.240 bps/trade (t=−2.76); **bootstrap p5 = −0.389 bps/trade (gate p5>0: FAIL)**; drop-best (MSFT): −0.272 bps/trade.

**Why the naive scan lied:** full-sample quintiles = lookahead; top-minus-bottom bucket contrast ≠ tradeable long-leg; friction 3 bps dwarfs the residual. Under honest rules the observation is negative. **Verdict: DEAD** — same conclusion as NQ order flow, free-data PEAD/NQ/ES, and the already-closed vol/index-rebal/event families. The order-flow data moat — the docs' highest-ranked Stage-2 direction — does not survive the harness on either venue (futures or single stocks).

### 8.8 Stage-2 options lane — free SPY options EOD data (2010-2023), RESULT: all four observations DEAD (2 confirm closed families)

**Context (2026-08-14):** The options-lane paid pull (Databento OPRA.PILLAR cbbo-1m SPY, planned $1.24) never ran — the Databento account was locked (`403 auth_account_locked`; new signups blocked at signup email stage). Per user instruction ("check the free sources then search well"), obtained the free **Kaggle `dudesurfin/spy-options-eod-volatility-surface-2010-2023`** dataset (MIT license, 486 MB, 14 files `research/options/cache/spy_eod_{2010..2023}.parquet`, **9,468,584 rows**, 3,508 trading days) — full SPY EOD chains with both call+put sides per row: bid/ask/last/volume, IV, delta/gamma/vega/theta/rho, DTE, strike distance, underlying close. **No open interest** (noted: OI-based dealer-gamma observation untestable on this source; DoltHub also lacks OI; optionsDX has it but is not needed for the verdict below).

**Observation 1 — put/call volume ratio → next-day return** (`derive_scan.py`): spread +4.6 bps, non-monotone (buckets +2.8/+3.4/+5.0/+4.7/+7.4), corr ≈ 0. DEAD.

**Observation 2 — ATM IV level (30-60 DTE) → forward return** (`derive_scan.py`, `derive_scan2.py`): monotone and IS/OOS-stable — fwd5 spread +36.2 bps IS / +54.1 bps OOS; fwd21 +141.7 / +315.6 bps; corr 0.09-0.17. **BUT this is the VRP premium restated, not a new edge.** Pre-registered V3-style tail gate (`tail_check.py`: long SPY when 250-day rolling IV > 80th pct): max drawdown **83.7% (gate <40%: FAIL)**, total **−163%**, worst days 2020-03-16 (−11.5%), 2020-03-12 (−9.6%), 2011-08-08 (−6.5%) — the entire premium is earned by eating tail days that cost more than the premium. **Confirms the closed VRP family with independent data; the gate that killed V2/V3 kills this too.** DEAD by adjudication.

**Observation 3 — options flow / hedging pressure** (Σ call_vol×Δ − Σ put_vol×|Δ|, chain-wide, normalized by total volume) → return (`derive_scan3.py`): naive fwd5 spread −40.7 bps with a *put-heavy → up* sign — the OPPOSITE of the flow mechanism (put-heavy should push dealers to sell SPY short-term), i.e. fear-premium contamination. corr(hedge_norm, IV) = −0.257; after demeaning within IV quintiles (`derive_scan6.py`) the gradient collapses to 4 flat buckets (≈+27-31 bps baseline) + one anomalous bucket (+2.4), spread −29.1 bps with no monotonicity (IS −26.7 / OOS −35.5 driven by a single bucket). DEAD — no distinct flow signal above the premium.

**Observation 4 — skew** (mean OTM put IV − OTM call IV, |strike−spot|>8%, 30-60 DTE) → return (`derive_scan6.py`): normal level +23.2 pts; fwd5 spread **−1.0 bps**, corr ≈ 0. DEAD.

**Verdict: options lane DEAD.** Four observation classes tested on 14 years of free full-chain data; none survives. Two are the closed VRP/risk-premium family (levels that only pay for tail risk we cannot bear at this scale), two are flat. Combined with §8.6/§8.7 (order flow), every Stage-2 moat direction is now adjudicated. Only the OI-based dealer-gamma variant remains untested, and it is the same premium family (gamma exposure = vol risk) with no reason to survive the tail gate that killed V2/V3/Obs 2.

### 8.9 OI-based dealer-gamma variant — RESULT: CLOSED (untestable-free)

**Question:** does dealer gamma (Σ OI×gamma, signed call/put) regime predict SPY forward returns/vol? The last untested variant of the options family (§8.8).

**Data requirement:** historical per-strike open interest for SPY, ~500 trading days.

**Free-source search result (exhaustive):**
- OCC Series Search (`marketdata.theocc.com/series-search`) — per-strike Call/Put OI but **current-only**: `reportDate` param ignored (20240102/20250102/20260813 return byte-identical output, 7294 SPY rows), UI date picker offers only the most recent settlement date (2026-08-14, Fri, the last trading day; today is 2026-08-15) forward. User-confirmed: no past dates available.
- OCC Daily Open Interest (`daily-open-interest?reportDate=MM/DD/YYYY&action=download`) — historical works (June 2026 downloaded) but **aggregate by class** (Equity/Index total), not per-strike.
- OCC Volume Query — per-underlying volume only, no OI, no strike.
- Kaggle dudesurfin / optionsDX free EOD — no OI field at all.
- DoltHub — no OI. Cboe DataShop Optsum — paid, ^SPX/^OEX/^VIX index only. Polygon as_of chains — paid (~$29/mo). FirstRate Data — paid.

**Verdict: CLOSED — untestable-free.** Historical per-strike OI requires paid data. The signal is the same vol-risk-premium family that failed the tail gate four times (§8.8 Obs 2, V2/V3). Volume-proxy of the same positioning concept was already flat after IV control (§8.8 Obs 3). Options lane: fully adjudicated, complete.

### 8.10 OI-based dealer-gamma variant — RESULT: DEAD (tested, LambdaClass free data)

**Data found:** GitHub LambdaClass `options_portfolio_backtester` release `data-v1` — `SPY_options.parquet` (24,681,665 rows, 2008-01-02..2025-12-12, per-strike bid/ask/volume/`open_interest` 100% populated/IV/delta/gamma/theta/vega/rho, types call/put) + `SPY_underlying.parquet` (daily OHLC, clean close series). SHA256 verified. MIT. **Historical per-strike OI exists free after all — §8.9's "untestable-free" verdict superseded.**

**Scan (`derive_scan7.py`):** dealer dollar gamma = Σ OI×γ×strike×100, signed −call/+put (dealers assumed short calls/long puts). 4,508 trading days, 2008-2025.

**Results:**
- Returns: corr(gex, fwd5) +0.02-0.05. Quintiles non-monotone: fwd5 +10.8/+22.6/+1.6/+34.5/+34.6 bps (spread +23.7 raw, +12.3 norm); IS spread −0.1 / OOS +26.2 bps. No stable gradient. DEAD.
- Realized vol: strongly monotone (fwd5 vol 56→150 bps/day, corr +0.47) — mechanism real: low-gamma regime = high forward vol.

**Verdict: DEAD.** Signal predicts vol, not returns; monetizing it = short-vol, the closed VRP family already failed by tail gate four times (§8.8 Obs 2, V2/V3, tail_check). Options lane: fully adjudicated and tested on 17 years of per-strike data, both OI-free and OI-based variants.

**Options lane FINAL: closed.** 5 observation classes, all DEAD, recorded §8.8/§8.10.
