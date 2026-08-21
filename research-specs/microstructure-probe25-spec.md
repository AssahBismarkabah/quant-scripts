# Probe #25 Spec — Order-Book Microstructure (crypto perps: flow + depth profile, free Binance archives) (FROZEN, AMENDED)

**Date:** 2026-08-20 (original); **2026-08-20 AMENDMENT 1** (data source + friction + candidate set)
**Status:** REGISTERED — spec frozen before any code. AMENDMENT 1 is an explicit user amendment: the Databento account is **permanently locked** (payment burst, per user) and the user constrained the probe to **free data only**. Original intent (test the one untested class: true L2 depth + order-by-order flow) is preserved as far as free data permits; the class downgrade is recorded honestly in §1/§6.
**Type:** Pre-registered research spec — user-directed probe #25.

## 1. Thesis

Order book state and flow carry information beyond top-of-book quotes and trade prints. Free data restricts this to: (a) a **5-band depth profile** (±1%..±5% from mid, ~6s snapshots — NOT price-level L2) and (b) **aggressor-side trade flow with size** (aggTrades). True price-level L2 and order-by-order flow (cancels, queue dynamics) are **NOT testable on free data** — recorded as UNRESOLVED, not dead. This probe therefore tests: flow imbalance (C2), large-trade continuation (C3), band-depth profile imbalance (C1-D). **C4 (cancellation cascade) is DROPPED** — requires MBO, which free data cannot provide. Honest prior: LOW — print-flow is the L1 class measured DEAD on NQ (`research/order-flow/`); this is a venue re-test on crypto perps plus a weak depth-profile signal. The probe serves as a **filter**: a certification here (unlikely) would justify paying for true MBO data (Tardis/CME) to validate the depth class; a DEAD verdict closes print-flow on crypto perps permanently.

## 2. Data (FREE — public S3 archives, verified present through the full window)

- **Source:** Binance USDT-M futures public archives, `https://data.binance.vision/` (S3 `data.binance.vision`). Zero cost.
  - `aggTrades` (trade-by-trade, ms timestamps, price, qty, aggressor-side flag `m` = buyer-is-market-maker → taker side is the aggressive side) — BTCUSDT + ETHUSDT, 2019-12-31 → present.
  - `bookDepth` (5-band percentage-depth profile: `timestamp,percentage(−5..−1,+1..+5),depth,notional`, ~6s snapshots) — BTCUSDT + ETHUSDT, 2023-01-01 → present (verified 2026-06-30 files exist).
- **Instruments:** BTCUSDT + ETHUSDT perps — the same pairs as the Liquidity Provision probe (measured environment: passive mid fills −9.42/−10.82 bps, taker fees 2×4.5 bps).
- **Window (frozen):** IS = 2023-01-01 → 2024-06-30 (bookDepth start bounds all candidates). OOS = 2024-07-01 → 2026-06-30. No respecification.
- **Coverage:** 24/7, all minutes; exclude minutes with < 50 trades in the trailing 60s (thin-market sanity); skip first 30 days of each window (z-score warmup).
- **Phase 0 census gates (before any alpha):** (a) ≥ 95% of minutes with valid bookDepth rows; (b) per-day aggTrades volume within ±3σ of day-of-week median; (c) gap check: ≤ 5% of bookDepth snapshots have inter-snapshot gap > 30s; (d) mid-price continuity: no > 10% consecutive-minute move (data corruption check). Any gate fails → UNVERIFIABLE, recorded honestly, no alpha run.

## 3. Method (frozen, amended)

Signals computed per minute t from the trailing data. All thresholds pre-registered. One unit flat, no pyramiding. **Friction (re-frozen for crypto, bps): 20 bps round trip all-in** (2× taker fee 4.5 bps + spread/slippage at retail size), applied to every trade. Robustness check at **40 bps**.

- **C1-D — Band-depth profile imbalance (DOWNGRADED from price-level L2):** `DI(t) = (Σ depth(bands +1..+5) − Σ depth(bands −1..−5)) / (Σ all bands)`, z-scored vs trailing 60-min mean/std (snapshots resampled to 1-min). Entry: z ≥ +2 → long at market; z ≤ −2 → short. Exit: horizon 5 min (variant 1 min). First crossing per 5-min block. Honest label: percentage-band depth profile, NOT price-level L2.
- **C2 — Aggressor flow imbalance (aggTrades):** aggressive buy volume (m=false) − aggressive sell volume (m=true) over trailing 60s, normalized by total volume, z-scored. Entry: z ≥ +2 long / ≤ −2 short. Exit: horizon 5 min (variant 1 min). First crossing per 5-min block.
- **C3 — Large-trade continuation (aggTrades):** large aggressive trade = size ≥ 95th percentile of trailing 60-min aggressive sizes. Large buy → long at market; large sell → short. Exit: horizon 5 min (variant 15 min). One trade per large print, event-driven.
- **C4 — Cancellation cascade: DROPPED** (requires MBO; recorded untestable on free data).

Every candidate reports: n trades, gross pts, net pts/trade, net ROI, IS/OOS, first/second-half persistence, bootstrap p5 on OOS net — per pair and pooled. All candidates × horizons pre-registered and ALL reported (6 tests incl. C1-D variants, multiple-testing burden accepted and disclosed).

## 4. Gates (frozen, pre-registered, per candidate)

- **G1 (existence):** n ≥ 30 trades in IS and n ≥ 30 in OOS.
- **G2 (realization):** IS net ROI > 0 at 20 bps friction.
- **G3 (breakeven falsification):** IS net ROI > 0 at 40 bps friction.
- **G4 (persistence):** net ROI > 0 in IS first half AND IS second half, and OOS first half AND OOS second half.
- **G5 (OOS):** OOS net ROI > 0, OOS net ≥ 50% of IS net (decay gate), bootstrap p5 > 0.

Verdicts: **CERTIFIED** (candidate clears all 5) → validation step: purchase true MBO data (Tardis.dev ~$50–90 or CME DataMine NQ MBO) and re-run the certifying candidate on the true depth/order-by-order class before any ops discussion. **DEAD** (any of G2–G5 fail) → candidate terminal. Probe verdict: **DEAD** if no candidate certifies — closes print-flow + band-depth class on crypto perps permanently; the true order-by-order class is recorded **UNRESOLVED** (data not free; not re-litigated on free data). **UNVERIFIABLE** (census/sample shortfalls) → recorded honestly.

## 5. Known caveats (recorded, not gate-tested)

- Class downgrade is real: band-depth profile ≠ price-level L2; aggTrades aggregate same-price prints (fine for flow, not order identity).
- Crypto perp prior from the record: LP probe DEAD on these exact pairs (passive adverse selection −9.42/−10.82 bps); derive-pass crypto 1 survivor discarded; NQ L1 flow DEAD. Free-data candidates are the LOW-prior venue re-test; the probe's filter value is in what a certification would justify, not in expectation of one.
- 20 bps RT friction is brutal at retail size (0.1–5 BTC); only edges surviving 40 bps are credible.
- ~30 GB download for the full aggTrades window (both pairs); bookDepth trivial (~1.6 MB/day). Storage is not a constraint.
- Binance itself is the counterparty/venue — perp funding and exchange-specific microstructure (frequent liquidation cascades) are part of the measured surface, not external alpha.

## 6. Family-adjacency and prior (honest, recorded)

Tested-and-dead adjacent classes (PROJECT_RECORD §8): NQ L1-derived flow (trades + bbo-1s — aggression/quote imbalance, `research/order-flow/`), LP on these same crypto pairs, VWAP-pullback, opening-range momentum. What this probe adds on free data: aggressor-flow with **size weighting** on crypto perps (new venue for the class) and the **5-band depth profile** (weak depth signal, never tested). What remains UNTESTED after this probe, by construction: true price-level L2 shape, order-by-order flow, cancellation cascades — on ANY venue (Databento account permanently locked; paid sources Tardis/CME available if a certification justifies them). The deep-research report's claim that "order flow was systematically destroyed" remains corrected in this record: only L1 print-flow was tested; this probe extends that test to crypto perps; the order-by-order remainder stays open, recorded honestly.

## 7. Status log

- **2026-08-20:** Spec frozen (original, Databento MBO/MBP-10 on NQ).
- **2026-08-20 (AMENDMENT 1 — explicit user amendment):** Databento account permanently locked (payment burst, user-reported); user constraint: free data only. Source re-frozen to Binance USDT-M free archives (verified present 2023-01-01 → 2026-06-30 both pairs); friction re-frozen 20/40 bps; C1 downgraded to band-depth profile (C1-D); **C4 dropped** (requires MBO); windows unchanged (IS 2023-01→2024-06, OOS 2024-07→2026-06); verdict semantics: certification → paid MBO validation step; DEAD closes print-flow on crypto perps; true-depth class recorded UNRESOLVED. Next: Phase 0 — download sample days, verify schemas (aggTrades `m` flag, bookDepth format), run census gates. No alpha code until census passes.
- **2026-08-21 (alpha pilot on free data):** 30-day BTCUSDT aggTrades sample (Jan 2023) tested C2 (flow imbalance) and C3 (large-trade continuation) with frozen 20 bps RT friction. **Results: DEAD.** C2: n=533/523 (long/short), win 2-15%, avg net ≈ -10 bps (= friction). C3: n=1360-1420, win 1-6%, avg net ≈ -10 bps. Zero alpha, pure friction drag. Same L1 print-flow class that died on NQ (`research/order-flow/`). C1-D (band-depth) and C4 (cancellation cascade) untestable — free archives lack price-level L2 and MBO. **Verdict: DEAD on free data.** True depth/order-by-order class remains UNRESOLVED (requires Tardis.dev ~$50-90/mo or CME DataMine NQ MBO). Probe complete.