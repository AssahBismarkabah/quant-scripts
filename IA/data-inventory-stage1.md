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

## 6. Status

- **2026-08-13:** Document created as the working inventory + Stage 1 sequencing record. No code written yet. Next action: decide the first derivation to run on the PEAD panel (or, if preferred, on the fresh intraday) before opening the first Stage-1 attempt.
- All changes uncommitted (per standing policy). This file is a reference; it does not pre-register gates.
