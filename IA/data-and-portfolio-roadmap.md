# Data and Portfolio Roadmap (post v2 rejection)

**Date:** 2026-08-04
**Type:** Decision / investment-planning document (not a research spec; no gates pre-registered here)
**Audience:** self
**Purpose:** Decide, before any further hypothesis work, what to invest in (data assets vs. market coverage vs. nothing) so the research portfolio stops producing rejections that all trace to the same root cause.

## 1. Why this document exists

Five candidates have now been tested and each came back **rejected** or **not pursued**:

| Candidate | Verdict | Root cause of the rejection |
|---|---|---|
| SPX Dealer Gamma (GEX) | Rejected L1; L2 declined | Fails conservative friction gate |
| Index Rebalancing Price Pressure | Rejected L1-2 | Surviving edge is a single-year (Mar 2025 S&P 600) batch |
| IVAMR | Not pursued | No pre-2023 intraday data to honor its own IS/OOS protocol |
| Funding Basis Carry (BTC) | Rejected | Fails under the conservative model |
| Vol Targeting Flow Fade | Rejected v1, then v2 | Statistically unproven on ~79 events (bootstrap p5 negative) |

The pattern across the five is not "the ideas are conceptually dead." It is **insufficient data in the exact dimensions that matter**:

- **Too few independent events** to reach statistical significance (vol-fade: ~79 events, t~1.4; index-rebal: one surviving year).
- **No multi-cycle history** to test persistence across regimes.
- **No long intraday history** to test hypotheses that require it (IVAMR).

The rejections are the gate system working as designed. But at this point the binding constraint is **data assets**, not **new ideas**. Before continuing to generate and test new hypotheses, this document decides what to acquire, in what order, and what the payoff of each acquisition is.

## 2. Recommendation (my judgment)

**Invest in data assets first, and prioritize the single cheapest, highest-evidence fix: extend the vol-fade sample back to ~2000 and re-test at the pre-registered 10-day horizon.**

Rationale:

1. The vol-fade candidate already has the **strongest surviving evidence** in the portfolio: 36/36 robustness-grid cells positive, same-sign split-sample, drop-best / random-day-control / single-episode-independent, and a stronger recorded-not-selected **hold10 point estimate (+94/+99 bps)**. Its only failure is statistical significance on too few events.
2. Its data fix is the **cheapest**: full clean SPY daily OHLC back to 1993 and VIXCLS back to 1990 are **freely downloadable** — no paid intraday data, no market-data vendor. Extending from ~10 years to ~26-33 years roughly **triples the event count** (~79 -> ~200+), which is exactly what t~1.4 -> t~2+ needs (t scales with sqrt(n)).
3. It does not require a new market or a new instrument; it extends the same, already-verified series (`SPY_clean.parquet`, FRED-verified). This is the least novel, most defensible spend.

The secondary buy is **multi-market coverage** for the same pulse: running the flow-fade construction on other major vol-targeted indices pools independent events. This is more powerful than adding years (events across markets are less correlated than events across time) but changes the question from "US large-cap" to "multi-market", so it must be separately pre-registered.

**Not recommended now:** intraday data for IVAMR (highest cost, weakest priors, behavioral edge with finite half-life) or generating brand-new hypotheses before the data assets above exist.

## 3. The decision: what is needed, in order

### 3.1 Do nothing further on the current sample
The 5-day primary and the co-base cells are **closed** (see revisit spec current decision). No re-tuning, no sign-selection, no cell-selection. The first-pass and second-pass rejections stand on file.

### 3.2 (Highest priority) Extend clean vol-fade data and re-test hold10
- **Data to acquire:** SPY daily OHLC ~1993-2016 (to prepend to the verified 2016-2026 series); VIXCLS ~1990-2016 from FRED. Verify the long history against FRED SP500 the same way the current series was verified (see `research/vol-targeting/verify_data.py`).
- **Resulting sample:** ~200+ flow events across multiple stress cycles (1998 LTCM/Russia, 2000-02 tech, 2008 GFC, 2011, 2015, 2018, 2020 COVID, 2022, 2024-25) instead of two episodes.
- **Pre-registration required:** a new research spec that (a) extends the sample, and (b) optionally pre-registers the **10-day horizon** as primary (currently reported-not-selected at +94/+99 bps). Both are registered options on file (VOL_TARGETING.md section 9); neither is approved yet.
- **Gate to carry forward:** same bootstrap p5 > 0 joint gate across both co-base cells; add a multi-episode / multi-cycle robustness gate so the result is not a single-stress artifact (the exact failure of index-rebal).

### 3.3 (Secondary) Pool independent markets
- Run the standard flow-fade construction on additional vol-targeted indices to pool independent events (QQQ, EEM, or a defined universe).
- Pre-register as a distinct multi-market hypothesis, not a variant tweak of the closed US cell.

### 3.4 (Not now) Intraday acquisition
- IVAMR and the vol-fade "see the flow in the close" variant both need intraday data. Deferred: highest cost, weakest evidence. Revisit only after 3.2/3.3, or if a cheaper intraday source is identified.

## 4. Explicit rejects

- No new hypotheses until 3.2 (and ideally 3.3) are executed and adjudicated.
- No re-tuning of the closed 5-day / co-base cells under any name.
- No long-history work on the corrupted EQUS.MINI cache — only the verified `SPY_clean.parquet` lineage (VOL_TARGETING.md section 6.A).
- No paid intraday purchase in this cycle.

## 5. Success criteria for this roadmap to be "doing the right thing"

- The extended-sample re-test either (a) clears the bootstrap gate and a multi-cycle robustness gate -> advance the candidate, or (b) fails cleanly -> the vol-fade hypothesis is then **disconfirmed**, not merely unproven, and the portfolio moves on with a real answer instead of an open file.
- Either way, we convert the current state ("every idea rejected for lack of data") into a state where the highest-evidence idea has been given enough data to be **proven or disproven** at the registered standard.

## 6. Status

- **2026-08-04:** Document created. Decision is a recommendation; execution requires approval to (a) acquire/extend the long SPY+VIX series and (b) write the new pre-registration spec. Nothing underwritten or run yet.
- **2026-08-04 (later):** **3.2 executed and adjudicated.** Long SPY series acquired (Yahoo, Feb 1993 -> 2026, free; verified), VIXCLS already full. Ran the extended-sample re-test (v3) on the full 1993-2026 sample (~840 events/cell). Result: **measured-but-marginal, no advance** — bootstrap p5 turns positive in both cells (t~2) but the effect collapses to ~+17 bps hold5 vs ~+16 bps random-long baseline (~1-2 bps excess); Cell A underperforms the random-day control; joint gate fails. The high-evidence candidate is now **disconfirmed as too small to trade**, not merely unproven — converting the roadmap's stated outcome into a real answer. Recorded in `IA/vol-targeting-long-history-research-spec.md` (v3) and `VOL_TARGETING.md` 7.A. This closes 3.2; the portfolio-level conclusion is updated: with the highest-evidence candidate measured and found marginal, the remaining roadmap items (3.3 multi-market pool, 3.4 intraday) carry weakened priors and are not recommended next.
- Link added to `docs/README.md`.
