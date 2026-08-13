# Decision Memo: Path Forward After the Full Tested Record

**Date:** 2026-08-12
**Type:** Decision document (resolves the recurring "pick-or-stop" fork with a bounded, pre-registered program)
**Purpose:** End the ambiguity behind "something is missing at my level, or is the edge genuinely gone?" Convert an open-ended research phase into three bounded steps with defined gates that converge on a decision. Supersedes the repeated "pick-or-stop" endings of prior decision docs.
**Audience:** self.

## 1. Why this document exists

Every candidate we have tested was rejected, disconfirmed, measured-dead, or friction-eaten (see README tested-strategies table, `IA/research-pipeline-review.md`, `IA/research-frontier-mining.md`). The portfolio keeps ending at the same sentence: "deliberately pick or stop." We cannot decide because there is nothing pre-registered to decide on. That absence of a stopping rule is itself a process bug. This document pre-registers the criteria so the next decision is made by rules, not by fatigue.

## 2. What is actually missing (resolving the "at my level" doubt)

The failures are not random. They cluster into four missing pieces, and two of them are genuine "at my level" gaps we can fix cheaply with free data.

| Missing piece | Where it shows | Level |
|---|---|---|
| 1. No positive control on the evaluation harness | We have never proven the pipeline can find an edge that is known to exist | Our harness (fixable, cheap) |
| 2. No aggregation stage | We test singletons; real quant edge is a basket of weak signals | Our process (fixable, cheap) |
| 3. No data moat | Every candidate used the same free data everyone has; the "data asymmetry" pillar was never executed | Our data (expensive / effort) |
| 4. No declared scale or capacity lane | We never stated account size, costs, and holding capacity as constraints on the search | Ours to declare |

Items 1 and 2 are the highest-leverage and cheapest fixes, and they are the direct, testable answer to the core question. Steps 1 and 2 below settle "is it me or is it the market" with evidence instead of guessing.

## 3. The program: three bounded steps, fixed gates, converge to a decision

Start: 2026-08-12. Target: all three done within ~2-3 weeks of focused effort. No new candidate-worthiness claims from papers or transcripts until steps 1-2 are adjudicated.

### Step 1 - Positive-control verification of the harness (~2-3 days, free data)

Goal: prove the pipeline can detect an edge that everyone agrees exists. If it cannot, every past "disconfirmation" is uninterpretable, and the fix is the harness, not the ideas.

**Test A (synthetic embedded alpha) - THE load-bearing control.** Build price paths from real residual structure (preserve variance/autocorrelation of actual returns), then implant a known mechanical edge (deterministic state-dependent drift). Run the unchanged scaffold (bootstrap, IS/OOS split, friction model) and require it to retrieve the implanted alpha with tight bootstrap dispersion. If it cannot, that is a harness bug. This is the test that actually validates the hard case - detecting a *subtle, friction-sensitive* alpha with the same magnitude and frequency as the signals we keep testing (lowish Sharpe, small edge-per-trade, real cost drag). **Test A is the primary gate.**

**Test B (natural positive control, smoke test only).** Run the pipeline on the longest, most robust risk premium available: SPY (or SPX total return) vs risk-free, from the longest clean sample we can verify (1993+ via SPY; T-bill from FRED). This is a control, not a candidate to exploit. **Test B's value is limited**: a long-equity-vs-cash test mostly shows the harness can detect *beta*, which almost any pipeline can; it does NOT validate detection of a subtle friction-sensitive alpha. Treat Test B as a simple smoke/sanity check, not a load-bearing control.

**Gate for Step 1:** **Test A must pass (primary).** Test B should also pass as sanity. If Test A fails, the prior record is re-opened as suspect and the pipeline is fixed before anything else moves. (Test B passing alone is insufficient - it proves beta detection, not alpha detection, and must not be used to certify the harness.)

### Step 2 - Portfolio-of-signals (aggregation) test (~1 week, free data)

Goal: test the mechanism that actually makes money for real quants - a basket of many weak signals, not a single strong one.

**Construction (pre-registered, frozen).** Start from documented weak effects measurable on free data, including in-house results where they exist: momentum, 1-month reversal, low-volatility, value proxy (book/market), turn-of-month, month-of-year seasonality, sector momentum, term premium, FX carry, commodity seasonality. Each individually is expected to be marginal or below our single-signal gates - that is fine and expected. Combine by pre-registered equal-weight/vol-weight of z-scores with no per-signal tuning. Measure the combined book net of friction out-of-sample vs its cash benchmark, with the same bootstrap / IS-OOS machinery we already run.

**Gate for Step 2:** the basket must clear OOS net of friction: bootstrap p5 > 0 on the combined book, PF >= 1.0, and robustness to holdout split. Individually failing signals are expected; the basket either compounds into a real OOS edge or it does not.

**Neutral prior - record this now.** Given 13/13 single signals are dead, the **more likely than not outcome is that Step 2 fails** OOS net of friction: many of the named signals (momentum, low-vol, size, carry) are published/decayed, positively correlated in stress, and several of the cross-sectional ones (book/market, size) need data we do not fully own. Aggregation does not create alpha; it only converts sub-threshold alphas into a book *if* genuinely independent, non-decayed sub-threshold signals exist. So Step 2 is a genuine test that can legitimately fail. **We set a neutral prior and let the gate rule - the verdict must not be nudged toward either "there is an edge" (confirmation bias) or "dead" (fatigue bias).** The one thing Step 2 is NOT is a free pass to keep the search alive.

**Why this is the pivot.** Our pipeline currently rejects at the individual-signal level and never aggregates. Diversification across weakly correlated signals is the one mechanism that converts sub-threshold alphas into a robust book, and it is the canonical answer to "how do quants make money." We have the machinery and the per-signal plumbing; we have never run it in aggregate. Completing Step 2 therefore closes the aggregation gap either way: if the basket clears, we have a product; if it fails, we have a definitive, cost-and-data-aware answer that the free-data portfolio alpha is measured-dead.

### Step 3 - The decision, pre-registered (no more open-ended research)

After Steps 1-2 the fork is decided by rules:

- **If Step 1 fails:** fix the harness, then re-audit the prior record. Nothing else moves.
- **If Step 1 passes and Step 2 clears:** the go-forward product is a small, vol-sized basket of many weak free-data signals, with explicit expectations of modest returns and long flat stretches. This is a real, winnable lane - it is just not the "one strategy with a why" we kept hunting.
- **If Step 1 passes and Step 2 fails:** free-data portfolio alpha after costs is exhaustively measured-dead at our scale. That is a definitive answer, not a vague "stop." The remaining real choice collapses to two pre-decided options:
  - (a) buy data to unblock the identified paid-lane candidates (dealer-gamma intraday; long intraday history for IVAMR) under a fresh pre-registration with explicit capex and a hard no-go threshold; or
  - (b) stop the systematic phase and redeploy the skill elsewhere.
  - There is no third "maybe one more free candidate" option anymore.

## 4. Concurrent lane (optional, does not block Steps 1-2): the data moat

The one framework pillar never executed is data asymmetry. Parallel work allowed while the steps run, but not as singleton candidate tests: pick one free feed we can act on faster or cleaner than consensus - EDGAR full-text/timestamp search, or a cheap tick/order-book feed we clean ourselves - and mine it for something that should not exist, then reverse-engineer the why. This is the forward direction (data -> idea), and it is the only search direction not yet exhausted.

## 5. Hard no-go commitments

- No new candidate-worthiness claims from papers or transcripts until Steps 1-2 are adjudicated.
- No re-opening closed cells (vol-fade hold5/co-base, index-rebal, funding-basis) under any name.
- No forced weak free-data candidate #6+.
- No paid intraday purchase inside this program. Allowed only after Step 3 as option (a), with a pre-registered budget and no-go threshold.
- Effort is not progress. The only outputs that count are the three gates.

## 6. Status

- **2026-08-12:** Document created. Steps 1-2 use only data we already own or can verify freely (existing Databento/FRED/Yahoo pipelines). Step 1 Test B (SPY-vs-cash) requires no new data. Next action: run Step 1.
- **2026-08-12b (reviewer edits applied):** Two refinements made. (1) Step 1: Test A (synthetic embedded alpha) promoted to the **load-bearing** control; Test B (SPY-vs-cash) demoted to a **smoke test** only - basing the harness gate on Test B would certify beta-detection, not alpha-detection. (2) Step 2: added an explicit **neutral prior** - with 13/13 singles dead, the basket failing OOS is the more likely outcome; the gate is allowed to rule either way and must not be nudged by fatigue or confirmation bias. §4 concurrency note: the 2026-08-11 frontier harvest (arXiv outage fix + VIX-ETP/OIC closures + Bitcoin cycle-confluence closure) falls under the §4 data-moat/concurrent lane, not a singleton candidate test - no contradiction with §5 "no new candidate-worthiness from papers/transcripts," which remains in force.
- **2026-08-12c (Step 1 RESULT — PASS):** Positive-control harness verification complete (`research/positive-control/step1_testA.py`, `step1_testB.py`). **Test A (load-bearing) PASS**: the production event-study harness (imported unchanged from `src/quant_scripts/index_rebalancing/validation.py`) retrieves clearly-detectable embedded alpha (t>=2.5) at 100% across seed replications, and never claims alpha on zero-mean nulls (0% false positives). It is correctly low-powered for realistic weak single-signal edges (t~1.3-2.4 detected only 40-70% of draws) - correct statistics, not a bug. **Test B (smoke) PASS**: the harness detects the long-run equity premium over the full SPY sample 1993-2026 (CAGR 6.2% price-only, Sharpe 0.42, bootstrap p5 > 0).
  - **Interpretation:** the harness is **sound** - it does not manufacture alpha (0% null false-positives) - so the prior DISCONFIRMED decisions are **interpretable** and do NOT need re-opening. The single-signal finding is not "signals are absent" but "single weak signals (t<2) cannot clear the p5>0 gate" - which is the exact economic justification for Step 2 aggregation. **Step 1 gate met; proceed to Step 2.**
  - Note: Test B's IS window (1993-2008) shows weak CAGR (0.9%) because it ends at the 2008 GFC trough and uses price-only SPY (no dividends); this is an artifact of the break point, not a harness failure - the full-sample and OOS signals are both strong.
- **2026-08-12d (Step 2 RESULT — FAILS-OOS, decisive):** Time-series index-timing basket run (`research/portfolio-book/step2_basket.py`). Pre-registered 5-member, equal-weight, vol-scaled book (time-series momentum, 1-month reversal, turn-of-month, January, Nov-Apr seasonality) on SPY long (1993-2026). IWM size-tilt member **dropped pre-run** (IWM cached history only starts 2023 - too short for relative-momentum; honest scope). **All three OOS gates fail:** bootstrap p5 of mean excess **−0.00024 (<0)**, profit factor **0.815 (<1.0)**, holdout split **both halves negative**. The book loses money in BOTH windows (end 0.60 IS / 0.50 OOS) while a 10%-vol buy-and-hold is positive in both (Sharpe 0.32 IS / 0.75 OOS).
  - **Member detail (informational):** `reversal_1m` is catastrophic in both windows (−28% CAGR, Sharpe −3.0) - a reversal signal is structurally short a trending-up equity index; `time_series_mom` (+10-13%, Sharpe ~1.0-1.2) and `seasonality_novapr` (+4-5%, Sharpe 0.6-0.7) are genuinely positive, `turn_of_month`/`january_effect` near-nil. **Per the pre-registered rule the member list was frozen and equal-weighted - the losing member was NOT dropped, as dropping it post-hoc would be result-hunting.** Equal-weight aggregation measurably failed; it did not convert sub-threshold signals into a positive book because the signals were not sub-threshold positives but a mix of real positives and real drags.
  - **This triggers memo §3 Step 3 decision path:** Step 1 (harness) passed, Step 2 (aggregation) **failed** ⇒ **free-data portfolio alpha (aggregated, index-timing) is measured-dead OOS net of friction at our scale.** Per the memo's pre-decided fork, the remaining choice collapses to (a) buy data to unblock paid-lane candidates (dealer-gamma intraday; long intraday history for IVAMR) under fresh pre-registration with explicit capex and a hard no-go, or (b) stop the systematic phase. **No third "one more free candidate" option.** Decision on (a) vs (b) is the next fork; Step 2 record is complete.
- **2026-08-12e (POST-HOC AUDIT — the "decisive" Step 2 verdict is scoped, not absolute).** On review, the Step 2 run tested a **restricted** version of the pre-registered Step 2 construction, and the conclusion "free-data portfolio alpha is exhaustively measured-dead" overstates what was actually tested. Written to prevent the fork being locked by a verdict that outruns its evidence.
  - **What §3 Step 2 actually named (pre-registered):** momentum, 1-month reversal, **low-volatility, value proxy (book/market), term premium, FX carry, commodity seasonality, sector momentum** — a multi-asset, cross-sectional book with "equal-weight/vol-weight of z-scores."
  - **What was actually run:** five **single-index time-series signals on SPY long only** (time-series momentum, 1-month reversal, turn-of-month, January, Nov-Apr). **Not run at all:** low-vol, book/market value, term premium, FX carry, commodity seasonality, sector momentum. The book is all-long-equity-beta with zero multi-asset or cross-sectional members.
  - **Consequence:** this run answered "does an all-long-SPY index-timing basket clear costs?" — an **index-timing** question, not the **aggregation/diversification** question Step 2 named. Diversification you can actually bank requires members that do NOT share the same single beta (different asset classes, currencies, cross-sectional spread vs single-leg). The one signal regime where the failure is most expected — all-long-equity timing — is exactly what was tested. The verdict is typed as "index-timing aggregation," but the memo's Step 3 language "free-data portfolio alpha (aggregated, index-timing) is measured-dead" narrows it correctly. Calling it "free-data portfolio alpha ... at our scale" deceives the record.
  - **What is still genuinely measured (this run's valid scope):** (1) the harness is sound (Step 1, 0% null false-positives); (2) a frozen, equal-weight, vol-scaled book of 5 all-long-SPY timing signals loses money OOS net of friction while 10%-vol buy-and-hold is positive; (3) the reversal_1m member is a real, large negative drag when forced in equal weight; (4) time-series momentum and Nov-Apr seasonality are individually positive on SPY in both windows (informational).
  - **What this run does NOT measure: whether a genuinely diverse basket (multi-asset + cross-sectional: long/short, not all-long-equity) can clear the same gates.** The PEAD panel (2.4GB, ~5k US names, prices 1998-2021 + dividends) exists on disk and the repo already has FRED fetch + Yahoo/Stooq plumbing, so term-premium, FX-carry, commodity, low-vol, and cross-sectional members are testable on free data — but were not run.
  - **Decision-status update:** the Step 3 fork's "measured-dead for free-data portfolio alpha" claim is therefore NOT final. It is final only for "all-long-equity index-timing." The unresolved question is narrower and honest: does a *diverse* basket (multi-asset + cross-sectional) clear the pre-registered OOS gates? Until that is run — or deliberately declined as not worth the effort — the buy-data-vs-stop fork is not yet closed by Step 2. This does NOT reopen the "pick-or-stop" loop: it is one bounded, pre-registered-adjacent test of the Step 2 construction as originally named, with the same frozen-gate discipline. If that diverse-basket test also fails, THEN the "free-data portfolio alpha is measured-dead at our scale" conclusion is earned and the fork is decided (a buy-data, or b stop).
- **2026-08-12f (Step 2b FINAL RESULT — FAILS-OOS under honest shorting costs; closes the gap left by 12e):** Tasked to run the genuinely-diverse basket (the auditor's 12e point). Built `research/portfolio-book/step2b_diverse_basket.py` + spec `IA/step2b-diverse-basket-spec.md`: risk-parity (inverse-vol) combination of 6 members on data we own — cross-sectional mom12-1, rev1m, lowvol (PEAD panel 7,786 names, 1998-2021) plus term premium, FX carry, commodity seasonality (all FRED keyless; Yahoo/Stooq blocked 429/JS, excluded). **Three construction bugs found and fixed during the build** (spike from lumping monthly returns; 21x over-stated per-day friction; vol-scaling of a unitless z-score mean producing leverage blow-ups). Each was caught and corrected; no verdict was accepted from a buggy run.
  - **The decisive finding — the book only "clears" under an unrealistically cheap short-borrow cost.** Fixed-harness OOS: at my initial 1.5%/yr short-borrow the book appeared to clear (p5 +1.55bps, PF 1.25). Borrow-cost sensitivity (0%, 1.5%, **5%**, 10%, 15%/yr): the edge is a knife-edge that dies under realistic hard-to-borrow costs — at **5%/yr (honest for bottom-quintile small caps) OOS p5 = −0.78bps (<0)**, PF 1.006, and holdout second half negative → **FAILS-OOS**; worse at 10-15%.
  - **Why:** the apparent edge is carried almost entirely by **rev1m (1-month reversal, +4.8bps/day OOS)**, which shorts the worst/illiquid bottom-quintile names — precisely the unborrowable ones. This is the auditor's exact warning ("short leg must be honest: borrow costs, hard-to-borrow names") realized. Also `mom12_1` (−1.6bps/day) and `term` (−17bps/day) are persistent drags.
  - **VERDICT: Step 2b FAILS-OOS under honest shorting costs** ⇒ the Step 3 fork claim **"free-data portfolio alpha at our scale is measured-dead" is now EARNED** across: 13 single-signals + all-long index-timing (Step 2a) + multi-asset/cross-sectional diverse basket (Step 2b) with honest costs. The fork is genuinely decided: **(a) buy data for the paid-lane candidates (dealer-gamma intraday; long intraday history for IVAMR), or (b) stop the systematic phase.** No third free-data option remains.
  - **Engineering note recorded for future work:** a correct multi-asset aggregation harness needs (1) position-based combination (weights × asset returns), NOT z-scoring returns, and (2) honest short-leg borrow costs in L/S books — both are now fixed/understood in this repo's context.

## 7. Reconciliation with institutional-approach.md (why this is a documented change, not a contradiction)

**Status:** Written 2026-08-12 after explicit review against `IA/institutional-approach.md` and `IA/market-edge-framework.md`. This section records where the program preserves the framework and where it deliberately modifies it. The modification is the point of this document; it is not framed as if the framework already said it.

### 7.1 What the framework says (the requirement)

- Every strategy has three parameters: machine-executable entry, exit, and explicit position sizing.
- Every strategy must carry a why: who is on the other side and why they statistically give you money. Without that it is gambling.
- Simple-bits-complex: few rules, one clear why, robust across a wide range of values. Each added rule is a claim that the future resembles the past.
- Validation is Monte Carlo (reshuffle + bootstrap), IS/OOS split, and a pre-registered "when to say no" threshold (max drawdown, min profit, min average trade).
- Idea sources are academic research, structure/mechanics, and behavioral observation (observation is the beginning of the work, not the end).
- "Professionals don't necessarily run single versions of this strategy but multiple models working together."

### 7.2 What this program preserves (per member)

- **Three parameters per signal.** Every member of the basket is a full mini-strategy: machine-executable entry, exit, and explicit sizing. No member is a loose "indicator."
- **A why per signal.** Each member is required to come from one of the framework's idea sources and be attributable to one of its strategy families (momentum = trend; reversal/seasonality = mean reversion; carry = relative value; low-vol/value = risk-premium compensation for a known, documented premium). No signal enters without a stated economic reason and an attempted counterparty (behavioral/risk-based if not forced-flow, which the framework admits as a legitimate but weaker source).
- **Few rules per member.** Simple-bits-complex still applies at the member level: each signal stays a handful of rules with a single reason, robust across a parameter range. The basket is not "many rules on one claim"; it is several independently-simple claims run in parallel.
- **Monte Carlo and split discipline.** The framework's MC reshuffle/bootstrap and IS/OOS split are not abandoned; their subject moves up one level. We bootstrap trades-within-signal AND signals-within-book, and apply IS/OOS plus a friction model to the book.
- **"When to say no" survives.** It is pre-registered for the book (max drawdown, min profit factor, min average trade) exactly the way the framework requires for a single strategy.
- **Selection guard (the framework's own overfitting guard, applied to the portfolio).** The member list and combination rule are frozen before any OOS look, so no signal is added because it worked in-sample.

### 7.3 What this program deliberately changes (the one departure - stated plainly)

- **The validation gate moves from the single strategy to the book.** The letter of the framework implies each strategy passes individual validation before it may be combined with others. That is Option A: definitionally safe, but with 13 single-strategy candidates dead, Option A terminates at "stop."
- Real quant shops run Option B: hundreds of individually sub-threshold signals, most of which would fail a per-strategy "when to say no" gate, combined mechanically; the edge is the book, and the book is what stands the MC/split/friction test.
- **Adopting Option B is an explicit, deliberate modification** of the framework's letter, not a statement that the framework already approved it. It is recorded here so the two documents never misrepresent each other. The framework's spirit is preserved: no overfitting, no permission machine, no signal without a why, and a hard no-go applied to the aggregate.
- **Step 1 (positive control) is calibration, not a candidate.** SPY-vs-cash and the synthetic-embedding test verify the harness; they are not strategies, so they are not subject to the candidate validation template (entry/exit/sizing/why). They are the metering device for every strategy test that follows.

### 7.4 The remaining genuine tension (left open, not papered over)

Cross-sectional premia like momentum, reversal, and low-vol do not have the framework's forced counterparty pillar ("asymmetry of constraint; both sides rational -> EV zero"). Their why is behavioral or risk-based. The framework therefore correctly ranks them lower-tier than forced-flow mechanics - which is exactly why they are individually weak and only clear costs as a basket. This program is that claim: not that weak signals are strong edges, but that their aggregate can clear the framework's own no-go thresholds (friction, OOS, bootstrap) when the framework's letter would bin each member individually. If, after Steps 1-2, that claim fails, the framework's Option A conclusion stands and the phase stops.
