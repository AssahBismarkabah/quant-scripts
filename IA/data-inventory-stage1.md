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

### 7.2 Next options (to choose with user)
1. Refine liquidity into a **conditional** hypothesis (e.g. liquidity interacted with a return/momentum state) — only if a concrete why justifies it; not automatic.
2. Move to the next observation class: **reversal/short-horizon** on the CLEANED, liquid-only panel (the per-name jump/stale structure suggests overnight vs intraday spread may be measurable).
3. Move to the **fresh intraday** NQ panel (2020-2026) for the microstructure direction.
