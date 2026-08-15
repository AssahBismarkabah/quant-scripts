# 10b5-1 Adoption Timing — Research & Pre-Registration Specification

**Status:** Pre-research specification (bounded falsifiable mini-test, 2026-08-07)
**Classification:** Data asymmetry (SEC EDGAR real-time 8-K 10b5-1 adoption) + Structural forced-flow (corporate repurchase mandate)
**Supersedes/extends:** A **distinct, narrower** event than the broad repurchase-program signal in `buyback-timing-research-spec.md` / `../strategies/buyback-timing/BUYBACK_TIMING.md` (which was TESTED-NOT-ADVANCED on a bounded sample). This spec isolates the **real-time Rule 10b5-1 repurchase-plan adoption event** (Form 8-K Item 8.01), the one genuinely non-lagged, machine-readable forward signal in the family, and tests it as a cheap falsifiable probe before any larger build.
**Purpose:** Decide, with a pre-registered gate and a bounded sample, whether the 10b5-1 adoption signal is worth scaling — or should be cleanly disconfirmed — before spending anything beyond what the existing EDGAR stack already provides.

---

## 1. The research question

Do real-time **Rule 10b5-1 repurchase-plan adoptions** (disclosed via Form 8-K, machine-readable, near-real-time) predict positive, tradeable forward returns after friction and after controlling for market/momentum/size exposure?

The claim is **conditional**: since the SEC 2022 amendments (effective Feb 2023), an issuer adopting a 10b5-1 repurchase plan must observe a **30-day cooling-off period** before buyback trading may begin. So an adoption event gives us a **forward, scheduled, non-lagged** signal that corporate buying is about to start ~30 trading sessions later and continue on a formula (date/price). Unlike the lagged quarterly 10b-18 daily-disclosure tables, the 8-K adoption is near-real-time.

This is a hypothesis, not an edge. It is a probe. If it fails the pre-registered gate on the bounded sample, the family is disconfirmed and we stop — the same gate-discipline that closed vol-fade and index-rebalancing with real answers.

---

## 2. How this differs from the (not-advanced) buyback study — and the honest prior

The bounded buyback study (H1 2026, 47 events, `BUYBACK_TIMING.md`) tested a **broader** signal: new repurchase *program/authorization* announcements. Its findings were:
- (+1,+20) primary: +118 bps net (t 0.64), but **bootstrap p5 negative (−189) → gate FAIL**; drop-best collapses to ~zero; short horizons (+1,+5 / +1,+10) **underperform the index** (negative rel-SPY) — consistent with post-2001 decay of announcement effects.

This new spec **narrows** the event to the **10b5-1 adoption 8-K** specifically, and changes the entry to the **cooling-off-expiry** timing (Tier B), which the broad study did not isolate. Two consequences:
1. The signal is **real-time and forward** (the broad study used announcement dates, not the forward 10b5-1 lockup structure). This is the mechanistic difference that could matter.
2. But the honest prior is a **caution**, not excitement: the same EDGAR family just failed its gate. So this must be run as a strict falsification with the same bootstrap-gate discipline, NOT as a way to resurface a dead line under a new name.

If the short-horizon underperformance reproduces (the broad study's clearest negative), that alone should terminate the family.

---

## 3. Mechanism / why

**Counterparty:** the repurchasing **corporation**, executing a committed Rule 10b5-1 plan. It is a constrained, schedule-driven buyer that must trade on its plan even in weak tape, and (per Stephens & Weisbach 1998; Busch & Obernberger 2016; Cook et al. 2004) repurchase *execution* provides price support and precedes positive abnormal returns.

**The real-time forward angle:** the 8-K 10b5-1 adoption is disclosed *before* buying begins (30-day cooling-off for issuers) — a genuinely non-lagged, scheduleable signal that most run-of-the-mill buyback-followers (who use the lagged quarterly tables or only large-cap programs) do not act on at adoption time.

**Failure modes (pre-listed):** the effect is (a) just low-beta/value/momentum exposure (the vol-fade beat-random confound), (b) fully decayed post-2001 (documented CFA/2019-JCF decay), or (c) too sparse / announced after the fact to trade. Also the new-real-risk: the same family already failed its bounded gate, so (d) this is a resurfacing of a dead line — the strict gate must guard against that.

---

## 4. Pre-registered test design (bounded, cheap, falsifiable)

**Universe:** US equities with a **10b5-1 repurchase-plan adoption 8-K** (Item 8.01 or 7.01 referencing a Rule 10b5-1 repurchase plan), harvested from EDGAR full-text search. Focus on liquid names only (e.g. price ≥ $5, some ADV filter) to keep friction credible; report on the full set and the liquid subset.

**Signal / event date:** the 8-K filing date (real-time disclosure) of a 10b5-1 repurchase-plan adoption. Dedup to distinct issuer-announcements (90-day window per issuer) to keep events independent. Exclude if it is the *same* as a broader program announcement already counted in the buyback study — we want adoptions, not authorizations.

**Entry (two arms, pre-registered):**
- **Tier A (adoption-time):** long at open of session t+1 after the 8-K adoption date t. This tests whether the mere adoption (undervaluation signal) is tradeable.
- **Tier B (cooling-off expiry, primary):** long ~**30 trading sessions after adoption** — i.e. enter when the issuer's buyback window actually opens. This is the forward, non-lagged signal that is mechanistically distinct and the reason to run this probe.

**Horizons (primary = (+1,+20) after entry):** (+1,+5), (+1,+10), (+1,+20) reported; (+1,+20) primary. Time exits; no intraday.

**Sizing:** equal-$(or equal-risk) among events; volatility-targeted per the institutional approach if n sufficient.

**Friction:** 20 bps round trip base (conservative single-stock), 40 bps stress. Report net-of-friction.

**Control (mandatory):** the "beats random-day / beats market" gate. Report each horizon vs SPY (rel-SPY) and vs a matched non-adopting control on size/BM/momentum/beta. The point is to rule out the low-beta/value/momentum confound.

---

## 5. Pre-registered rejection gates (this probe FAILS if ANY holds)

1. **Bootstrap p5 negative at the primary horizon** (bootstrap p5 of net return < 0) — the exact gate that failed the buyback study and vol-fade v2. Fail ⇒ disconfirm.
2. **Short-horizon underperformance reproduces:** (+1,+5) or (+1,+10) rel-SPY negative (as in the broad study). This is the family's documented failure signature; its reproduction terminates the family.
3. **Effect vanishes vs the matched control / random-day** after beta-momentum-size adjustment (the vol-fade beat-random confound).
4. **Too few independent events** (e.g. fewer than ~30 distinct liquid events) to be meaningful.
5. **Not tradable: entry not realistic** (e.g. adoption and cooling-off expiry both unusable in practice, or the 30-day window makes the signal stale).
6. **A survivorship / look-ahead artifact:** 8-K date != actual disclosure availability, or bars unavailable for delisted names, or the "adoption" is actually the lagged program announcement (i.e. we accidentally re-ran the buyback study).

---

## 6. Data & tools (all already owned — this is why it is cheap)

- **EDGAR** (free): full-text search + retrieval for Form 8-K containing "10b5-1" repurchase adoption; the pipeline already exists (`pdfplumber`/`requests`; feasibility confirmed in the buyback spec).
- **Bars:** verified daily OHLC lineage (`SPY_clean.parquet` style verification) from Yahoo; corporate-action calendar.
- **No paid data, no intraday, no options, no leverage.** This is deliberately the same cheap-data discipline.

---

## 7. What we are deciding

This probe decides, cheaply, whether the **10b5-1 adoption/cooling-off-expiry** signal — the one piece of the buyback family that is genuinely real-time and data-asymmetric — clears the gate. Two outcomes:
- **Clears** ⇒ scale: full multi-year sample, official index membership, persistence/decay gate, then a strategy doc and possible deployment.
- **Fails cleanly** ⇒ the buyback/10b5-1 family is **disconfirmed, not merely unproven**, and we move on with a real answer — no further spend, no resurfacing.

**Gate discipline:** this is a falsification run, not a fishing expedition. The primary (+1,+20), Tier B arm and the (pre-registered) gates above are fixed before running.

---

## 8. Status

- **2026-08-07:** Spec created as the cheapest falsifiable probe in the "build our own moat" pivot.
- **2026-08-07 (later — probe EXECUTED and DISCONFIRMED):** Full EDGAR harvest run (2025-07-01..2026-07-31, 993 8-K filings classified with a resumable cache). Genuine issuer 10b5-1 repurchase-plan adoptions: **3 events / 2 distinct issuers** (TKO x2, SAM) vs the pre-registered ≥30 → **gate FAIL on sparsity**. Rejection reasons across the 993 confirm this is real sparsity, not a classifier bug: ~432 incidental rule citations, ~140 officer/director 10b5-1 *sales* plans, ~100 financing/underwriting docs citing 10b5-1. Issuers disclose buybacks via the broad repurchase-program authorization 8-K or the lagged quarterly tables, not dedicated real-time adoption events. **Verdict: DISCONFIRMED (sparsity), no-advance, family closed at this construction.** Full details in `../strategies/10b5-1-timing/10B5-1_TIMING.md` §7.
- Outcome per §7: the probe failed **cleanly** (specific signal missing density) with a real answer and no further spend — the falsification this spec was designed to produce. No resurfacing. Nothing traded.
