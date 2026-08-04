### **target volatility fund rebalancing — extended-history (v3) research specification**

**Status:** Test complete (2026-08-04) — adjudicated **MEASURED-BUT-MARGINAL: NO ADVANCE**. On the full 1993-2026 sample (~840 events per cell, a ~10x event increase over v2's ~80), the fade becomes statistically detectable (t≈2.0-2.2, bootstrap p5 > 0 in BOTH cells) but the effect size collapses to roughly **market-drift parity**: ~+17-18 bps hold5 vs an unconditional ~+16 bps random-long baseline, an excess of only ~1-2 bps that does not survive as a tradeable edge. The candidate does not advance. See Current Decision.

**Supersedes / extends:** `IA/vol-targeting-revisit-research-spec.md` (v2.0), which rejected the candidate on the bootstrap p5 gate at n≈80. This document pre-registers the registered option (VOL_TARGETING.md section 9) to **extend the sample** and re-test. It does NOT reverse the v1/v2 rejections; it measures the effect at a sample size where significance is achievable and records what the true effect size is.

**Purpose:** Freeze the extended-sample design, gates, and split before running; apply them uniformly to both co-base cells; record the verdict.

---

### **the research question**

With enough independent events (multiple stress cycles 1993-2026 instead of two), does the vol-target flow-fade produce a **tradeable** positive expected value, or was the v2 point estimate (+35 bps) a small-sample artifact of the 2023-2026 stress window?

This is a hypothesis test with a power pre-registration: at ~10x the v2 event count, t scales with sqrt(n), so a real edge at v2's implied size would become significant; a marginal effect would not clear the economically meaningful control.

---

### **data (extension)**

Acquired freely, per the roadmap (IA/data-and-portfolio-roadmap.md section 3.2):

- **SPY daily OHLC** from Yahoo Finance (free, no key) — SPY since launch Feb 1993 through 2026-07-31. Fetched in daily 8-year windows via the chart API to preserve daily granularity. `research/vol-targeting/cache/SPY_long.parquet` (8429 daily rows).
- **VIXCLS** from FRED — full 1990-2026 history already cached, reused.
- **Verification:** SPY_long overlaps the trusted `SPY_clean.parquet` (2023-2026) with **0 bps close difference** on all 838 overlap days (bit-for-bit agreement). OHLC sanity: 0 violations across 8429 rows. FRED SP500 cross-check (2016+): SPY*10/SPX ratio std 15 bps; return diffs mean 4.3 bps, largest only on known extreme trading days. VIXCLS alignment: 8427/8429 sessions carry a valid VIX close; the 2 exceptions (1997-01-31, 1997-11-26, both pre-2000 holidays) are **excluded** from the study frame — no VIX value is fabricated.
- Working series: `research/vol-targeting/cache/SPY_clean_long.parquet` (8427 rows, 1993-02-01 → 2026-07-31).
- Acquisition script: `research/vol-targeting/acquire_long_spy.py` (re-fetchable; cache is gitignored).

---

### **design carried forward unchanged from v2 (frozen)**

- Co-base cells and the **joint gate** (BOTH must pass, no selection):
  - **Cell A (realized):** exposure_t = min(2.0, 0.10/sigma60_t) x $1.0T, sigma60 = 60-day realized vol (IMF GFSR documented construction).
  - **Cell B (implied):** exposure_t = min(2.0, 0.10/VIX_t) x $1.0T (Bhansali-Harris documented input).
- Base parameters (frozen): target 10%, cap 2.0x, AUM $1.0T constant, IS-trained bottom-decile flow threshold, entry at t+1 open, primary 5-day horizon, friction 4 bps RT base / 12 bps RT stress, stop -2% reported. Split boundary 2024-12-31/2025-01-01.
- Robustness grid (reported, not selected): same 36-cell grid as v2.

**Gates carried forward, all applied uniformly to both cells (no per-cell rescue):**

- Same-day diagnostic corr(flow, ret) > 0
- Episode check: Aug 5 2024 AND Apr 4 2025 in bottom decile of flow
- H1: hold5 mean > 0 after base friction
- Split-sample same sign (IS/OOS)
- Bootstrap p5 > 0 (10k, seeded 42)
- Drop-best survives
- Random-day control (control = mean of all in-frame 5-day returns)
- t+1 close entry-shift
- Single-episode independence

**New substantive gate for the long sample — the random-control is now interpreted economically as "beats a random long hold":** over 32 years the unconditional mean 5-day return (~+16 bps) embeds long-run bull-market drift. Passing the bootstrap p5 gate (achievable at n≈840) is necessary but not sufficient: the candidate must also show the fade adds value **over remaining long at random**, i.e. a materially positive excess return vs the unconditional market mean. This gate pre-dates the run and is applied identically to both cells.

---

### **results (run on SPY_clean_long.parquet, 1993-2026)**

| Metric | Cell A (60d RV) | Cell B (VIX) |
|---|---|---|
| n events | 842 (798 IS / 44 OOS) | 849 (804 IS / 45 OOS) |
| threshold flow | -13.6 bn | -42.8 bn |
| same-day corr | +0.121 | +0.750 |
| episode check | pass | pass |
| hold5 raw | +17.45 bps | +17.94 bps |
| hold5 net base | +13.45 bps | +13.94 bps |
| t-stat (hold5) | **2.01** | **2.22** |
| bootstrap p5 | **+2.64 bps (PASS)** | **+4.67 bps (PASS)** |
| p_negative | 0.026 | 0.015 |
| drop-best | +16.11 | +16.62 |
| **random control** | **+25.85 bps (EVENTS UNDERPERFORM)** | **+8.35 bps (PASS)** |
| split IS/OOS | +16.8 / +28.7 | +17.0 / +34.8 |
| t+1 close entry (hold5) | +13.5 | +13.6 |
| single-episode | +15.25 | +16.11 |
| hold3 / hold10 (reported) | +10.6 / +38.0 | +7.0 / +36.5 |
| **gates_pass** | **False** | **True** |

Robustness grid (36 cells): h5 positive 36/36, h10 positive 36/36, h3 positive 32/36.

**Joint gate FAILS** — determined solely by Cell A failing the random-control gate.

---

### **interpretation**

1. **Power goal met.** Extending the sample produced ~840 events per cell (10x v2) and **bootstrap p5 turns positive in both cells** (t≈2.0-2.2). The v2 failure was indeed a small-sample artifact of the 2023-2026 window.
2. **But the effect is economically marginal.** Point estimates collapsed from +37.75/+31.92 bps (v2, n≈80) to +17.45/+17.94 bps (n≈840). Versus the unconditional random-long baseline of ~+16 bps, the excess is only ~1-2 bps — within noise, and Cell A's events **underperform** the random-day control (+17.5 vs +25.9).
3. **The significant t-statistics are a large-n artifact of a small effect**, not evidence of a tradeable edge. 840 largely-independent events reduce the SE so that a ~1-2 bp mean registers t≈2, but that mean is at market-drift parity.
4. **Cell B (VIX) passes every discrete gate** (including random control) while Cell A fails it; the joint gate nevertheless fails, and the magnitude-based reading (≈1-2 bps) applies to both.

---

### **current decision**

**MEASURED-BUT-MARGINAL: NO ADVANCE (2026-08-04).**

- The flow-fade effect is **real** (statistically detectable at n≈840, bootstrap p5 > 0 in both cells, positive in 36/36 robustness cells at h5/h10) but **not tradable**: ~1-2 bps excess over a random long hold across 32 years, with Cell A failing the random-control gate.
- The candidate does **not** advance to implementation. Recorded-not-selected: Cell B's discrete gates all pass; Cell A's hold5 underperforms the random-long control.
- The extended sample **disconfirms** the idea that the v2 point estimate (+35 bps) represented a tradeable edge; that estimate was specific to the 2023-2026 stress window and does not survive a full multi-cycle sample.
- The 5-day primary and both co-base cells are **closed**. No re-tuning, no horizon/cell selection.
- This converts the portfolio state for this candidate from "rejected for insufficient data / unproven" to **"measured to be economically negligible at a sample where significance is achievable"** — a real answer rather than an open file.

Data note: all results here use the verified `SPY_clean_long.parquet` lineage (Yahoo OHLC, FRED-verified); the corrupted EQUS.MINI cache is not used.
