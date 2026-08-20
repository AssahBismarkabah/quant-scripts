# Probe #24 Spec — Rule of Four (news-event range breakout, DAX + FTSE 100) (FROZEN)

**Date:** 2026-08-20
**Status:** REGISTERED — spec frozen before any code. Data is NOT yet owned (Phase 0 census required before the alpha run). User requested this probe directly ("there is one i want to test rule of 4", referencing the Tom Hougaard "Rule of Four" from the transcript). Recorded as a NEW probe in a distinct lane (news-event-anchored intraday breakout on EU index CFDs) with the honest family-adjacency note in §6: the ORB/opening-range family is in the PROJECT_RECORD §8 closed list (tested dead on NQ); this re-surfaces that family on a different market (EU indices) and a different anchor (macro news event vs session open). If it returns dead, the family is closed for good.
**Type:** Pre-registered research spec — user-directed probe #24.

## 1. Thesis

On scheduled macro releases (US Non-Farm Payrolls, FOMC statement), index markets spike and often **trend for the first 20-120 minutes** as participants price the new information (momentum/underreaction), before mean-reverting or fading. Tom Hougaard's public "Rule of Four" codifies this: after the release, the first four 5-minute candles form a range; a 5-minute close beyond that range is the entry trigger (breakout continuation), stop at the opposite side, targets at 1:1 / 1:2 / 1:3 of risk. This is a machine-executable, non-discretionary rule — it fits the harness constraint.

## 2. Data (NOT yet owned — Phase 0 census required)

- **Instrument (new):** DAX 40 (GER30 index CFD) and FTSE 100 (UK100 index CFD), continuous series from **Dukascopy free historical data** (datafeed.dukascopy.com). Resampled to 5-min bars. NOT in the owned Databento NQ/ES caches.
- **Event calendar (new):** NFP release dates/times (BLS schedule; first Friday, 08:30 ET, 12/yr) and FOMC statement days (Fed schedule; 14:00 ET, 8/yr), 2010-01-01 → 2025-12-31. ~320 event-days per market.
- **Anchoring (IANA zoneinfo, not fixed offsets):** event times are stored in America/New_York and converted per-event with Python `zoneinfo` to Europe/Berlin (DAX) and Europe/London (FTSE). US and EU DST transition dates differ (weeks apart in spring/fall), so a fixed +6h/+5h offset is WRONG and was corrected before the run. Candle C1 = [T, T+5) where T = release time in exchange-local time.
- **Phase 0 census gate (before any alpha):** fetch GER30 + UK100 5-min for all event days; require ≥90% of event days with complete, gap-free C1–C5 bars around T (window T−60min → T+180min); spot-check known NFP/FOMC moves. Below 90% coverage → UNVERIFIABLE, recorded honestly, no alpha run.

## 3. Method (frozen)

For every event day × market (DAX, FTSE):

1. T = release time (exchange-local). C1–C4 = four 5-min candles starting at T. Range: `H4 = max(high C1..C4)`, `L4 = min(low C1..C4)`.
2. **Entry (primary, strict):** candle C5 = [T+20, T+25). If C5 closes > H4 → long at C5 close. If C5 closes < L4 → short at C5 close. If neither (or impossible both), no trade. Only C5 may trigger.
   - **Variant V2 (frozen, reported separately):** any candle C5..C12 (60-min window) may trigger on a close beyond the range.
3. Stop (no buffer, frozen): long → L4; short → H4.
4. Targets (all frozen, primary = 1:2): TP 1:1, 1:2, 1:3 × risk; each reported as a separate pre-registered variant. No pyramiding, 1 unit flat, one trade per event per market.
5. **Time exit:** if neither target nor stop hit, exit at +120 min after entry (T+140 absolute). No overnight.
6. **Friction (frozen, brutal):** round-trip spread + slippage = **4 points** on GER30, **3 points** on UK100 (news-event slippage included). Applied to every trade's P&L in points.
7. **Persistence:** split IS into first/second halves; report net ROI both halves.
8. **OOS:** later calendar period, frozen rules, no re-tuning.

## 4. Gates (frozen, pre-registered)

Per market, then combined (both markets pooled):

- **G1 (existence):** ≥30 events in IS per market (long+short combined; direction split reported).
- **G2 (realization):** IS net ROI > 0 at primary 1:2, n ≥ 30 (per market).
- **G3 (breakeven falsification):** gross win rate at 1:2 must exceed the breakeven line `1/(1 + R_avg)` net of friction — the video's own breakeven claim, formalized. Failure = the pattern is random-entry-equivalent.
- **G4 (persistence):** IS net ROI > 0 in BOTH first and second halves at 1:2.
- **G5 (OOS):** OOS net ROI > 0 with same frozen rules, n ≥ 30 (per market).

Verdicts: **CERTIFIED** (all gates) → ops-pilot decision (separate); **DEAD** (any of G2–G5 fail) → terminal, ORB/opening-range family closed for good; **UNVERIFIABLE** (Phase 0 coverage or event-count shortfalls) → recorded honestly, no re-litigation.

## 5. Known caveats (recorded, not gate-tested)

- News-slippage dominance: entries fire within 20-25 min of the release; realized slippage can exceed the 4/3-point model. Mitigation: brutal model + the +120min exit; if the OOS is marginal, capacity check precedes any ops decision.
- CFD vs futures: GER30/UK100 CFDs are retail instruments; execution quality (requotes, weekend/holiday gaps) is part of the friction model, not separate alpha.
- Event-day count per market (~20/yr) is below the 30/yr gate used in prior probes if directions are split; gates are set at combined long+short n≥30 with direction splits reported, per §4.
- FOMC on DAX: DAX cash closes 17:30 CET; the 20:00 CET FOMC window trades only on GER30 CFD / FDAX futures. Data and gates are on the CFD series only.

## 6. Family-adjacency and prior (honest, recorded)

The ORB / opening-range / gap family is on the PROJECT_RECORD §8 closed list (tested dead on NQ 2013-2023; Gap Fill not falsifiable). The Rule of Four is the same breakout-mechanics family, re-anchored to a macro news event and run on EU index CFDs. Prior is therefore LOW — the user's explicit request is the reason this probe exists, not prior. Distinct elements that could matter: (1) EU index news microstructure is less arbitraged than NQ at retail-relevant size; (2) the event anchor (macro release) is a cleaner information shock than a session open; (3) underreaction-to-news is a documented behavioral phenomenon (PEAD analog). This probe tests whether ANY of that survives contact with friction. If DEAD, the family is closed permanently.

## 7. Status log

- **2026-08-20:** Spec frozen per user request. Next: Phase 0 census — acquire Dukascopy GER30 + UK100 5-min for all NFP/FOMC days 2010-2025 + build event calendar. No alpha code until census gate reads.
- **2026-08-20 (implementation):** Data acquired. Dukascopy free API verified (jetta.dukascopy.com, delta-encoded JSON; codes DEU.IDX-EUR / GBR.IDX-GBP). Data start dates: DAX 2013-09-30, FTSE 2011-09-19 (no earlier minutes). Event calendar built from BLS yearly schedules (NFP, 191 releases 2010-2025, incl. all documented exceptions: holidays, 2013 and 2025 shutdowns) and Federal Reserve statement pages + ScrapeFOMC datasets (FOMC, 130 statement days 2010-2025, incl. 2020 emergency meetings; excluded 2010-05-09 joint swap announcement and 2019-10-11 implementation statement as non-policy statements, decided pre-run). Timezone anchoring corrected per user direction to IANA zoneinfo (fixed +6h/+5h offsets are wrong; US/EU DST transitions differ). Phase 0 census PASSES: DAX 241/243 events full C1–C5 (99.2%), FTSE 263/268 (98.1%), both above the 90% gate; C1–C5 median range exceeds the prior-2h median on ~98% of event days, confirming the timezone mapping. Alpha run next.
- **2026-08-20 (alpha run):** Frozen protocol executed on the acquired data. Results below, recorded before any further analysis:

  Primary (strict C5 trigger):
  - DAX: UNVERIFIABLE per-market (IS n=15 < 30): IS net -2.98 pts, OOS net -2.70 pts (n=20).
  - FTSE: UNVERIFIABLE per-market (IS n=15 < 30): IS net +0.36 pts, OOS net -10.19 pts (n=25).
  - POOLED: DEAD (IS n=30, IS netR +0.071; OOS n=45, OOS netR -0.089; G3/G4/G5 fail).

  V2 (C5..C12 trigger, pre-registered variant):
  - DAX: DEAD: IS n=54 net +1.33 pts, OOS n=105 net -2.84 pts (G3/G4/G5 fail).
  - FTSE: DEAD: IS n=74 net +0.19 pts, OOS n=111 net -5.03 pts (G3/G5 fail).
  - POOLED: DEAD: IS n=128 netR +0.065, OOS n=216 netR -0.139 (G3/G5 fail).

  Verdict: **DEAD** — every configuration with sufficient sample fails G3/G4/G5 OOS; the strict primary trigger lacks IS sample per market (UNVERIFIABLE per-market, DEAD pooled). Per §4, the ORB/opening-range family is closed permanently. This is the terminal record for the Rule of Four on EU index CFDs.
