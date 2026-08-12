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
