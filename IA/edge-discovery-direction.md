# The Direction of Edge Discovery: Data -> Edge (post-free-data resolution)

**Date:** 2026-08-13
**Type:** Decision / methodology resolution. Supersedes the "measured-dead -> stop" dead-end by resolving WHERE a non-decayed edge can still come from, and HOW to derive it under our own discipline.
**Purpose:** End the confusion between two different models of getting an edge, and record the direction we must now take if we continue. This is the honest continuation of the fork left open by `path-forward-decision-memo.md` Step 3 option (a).
**Audience:** self. Feeds candidate selection and the next research phase.

---

## 1. Why this document exists

The program concluded that **free-data portfolio alpha at our scale is measured-dead** (sound harness, 13 single signals + all-long index-timing + diverse multi-asset/cross-sectional basket all failed OOS under honest costs). Taken literally, that leaves only "stop." But reviewing traders/approaches that appear to have a live edge (e.g. order-flow scalping names, vol-structur specialists) surfaced a contradiction that needed resolving:

- They seem to trade **discretionarily** (order-flow reading)
- Yet our framework demands **machine-executable rules** with a **why**

This document resolves that contradiction and records the correct forward direction. It is **not** a "find one more free candidate" move — that loop is closed. It defines how a *non-decayed* edge could be obtained, if we choose the cost-bearing path.

---

## 2. The resolved tension: two different models of "edge"

| | Academic/free-data model (what we exhausted) | Microstructure/order-flow model (what the referenced traders appear to use) |
|---|---|---|
| Edge lives in | a quantifiable anomaly (PEAD, MVRV, momentum...) | live liquidity, order flow, auction mechanics (POC, delta, aggression, MBO) |
| Freq | daily / monthly | intraday / tick |
| Data | free, public, everyone has it | paid/proprietary / hard to get (order book, depth, options OI) |
| Executable as | machine rule (yes) | usually discretionary skill, NOT a repeatable rule |
| Why it can persist | usually decays (public/arbs) | can persist IF the data/asymmetry is yours (moat) |

**Resolution:** The free-data model gives machine-rule edges that decay. The microstructure model can give a non-decayed edge **only if** (a) you own the data / asymmetry, AND (b) you convert the observation into an **objective, machine-executable rule with a why** — otherwise it is just discretionary skill (craft), which our framework correctly refuses to call a tradeable edge.

**There is no contradiction.** The people cited can be successful as *high-frequency liquidity readers* (a human craft) while their exact approach is not a backtestable edge — and separately, a **data moat can be turned into a real systematic edge** *if and only if* we can make the condition objective and validate it.

---

## 3. The direction that is left (and the one we had backwards?)

**Core resolution (the "move from data to edge" question):** Edges are **found by mining YOUR data for a repeatable observation, then converting it into an objective condition with a why** — NOT by starting from a public paper. This is the direction we have NOT yet systematically executed.

We started (reasonably) from pre-specified conditions in research papers — but every such edge is public, already arbitraged, and decays (that is why they all failed or were friction-eaten). The papers give you a *predefined test* but the edge is stale.

The direction that institutionally produces **non-decayed** edges:
```
data (yours / moat)  ->  observe a repeatable behavior  ->  define an OBJECTIVE condition
  ->  attach a WHY (who is forced, and why they give you money)
  ->  run through OUR harness (IS/OOS, Monte Carlo, friction)  ->  survives? then it is an edge
```

Key subtlety: **the observation is the beginning, not the end** (already in the framework). The hard, uncertain step is converting an observation into a rule that a machine can execute unconditionally — the exact step we could not make work for IVAMR and that we found riddled with discretion.

---

## 4. What "buying data" actually means now (reframed)

Buying/proprietary data is NOT "buy a DataFrame and an edge falls out." It is:
1. Acquire a data type we do not have (order flow / depth / MBO / options OI+IV surface / long intraday history).
2. **Then do the derivation step (section 3) ourselves**: mine it, find an observation, define an objective condition, attach a why, validate with our own harness.

The value of the data is **creating an asymmetry** (info other market participants don't uniformly act on). Without the derivation + validation step, paid data is "money for nothing." So paid data is a **necessary but not sufficient** condition for the remaining path.

---

## 5. Honest assessment of the remaining path (neutral prior)

- This is **harder and riskier** than following a paper: we are now the researcher deriving the hypothesis, with a high chance most derivations fail the harness.
- The bar is unchanged (objective rule, why, IS/OOS, MC, friction, no-go). No relaxation.
- The one thing that changes is the **input** (data moat) and the **direction** (derive, don't copy).
- If we are not willing to do BOTH (pay for data AND do open-ended, uncertain derivation), then the disciplined stop is still the correct answer — and that is a legitimate, data-backed decision, not a failure.

---

## 6. Decision status

- **2026-08-13:** Resolution recorded. Free-data ***pre-specified-anomaly*** phase: **closed** (measured-dead) — see §7 correction: this refers to the set of public anomalies we tested, NOT to the derive-from-data method, which remains open on free data. The fork broadens accordingly: free-data derive pass FIRST (Stage 1), then paid moat (Stage 2), then stop. No "buy before exhausting free" and no "free candidate #1" loop — the derive method is the forward path on free data.
- Open sub-decision if (a): which data moat to buy — order-flow (order book/MBO/delta) vs options microstructure (OI/IV/dealer gamma) vs long intraday history (for the already-scoped IVAMR/dealer-gamma candidates). Each is a separate pre-registered program with a hard no-go.

---

## 7. CORRECTION (recorded 2026-08-13): free data CAN be mined with the same process — exhaust it FIRST

The prior framing risked overstating "free data is dead." That is **too absolute.** What was actually measured-dead was a specific, narrow set of **public pre-specified anomalies** on free data (PEAD, MVRV, momentum, reversal, index-timing, etc.) — NOT the derive-from-data method itself, which we never actually ran on any data source.

**The method is data-source-agnostic.** "Mine data -> observe -> objective rule -> why -> validate" runs IDENTICALLY on free data, paid data, or years-old data. There is nothing about the derive process that requires paid data. So we are **wrong if we imply paid data is needed to run the derive step.**

**Free vs paid data differ only in asymmetry, not method:**
- The derive method is the same on both.
- On **free data**, any observation we derive, others can derive at the same cost -> no moat cushion -> the derived edge must be strong enough to survive entirely on its own. Higher (but not zero) chance of being noise-fit or already-arbitraged.
- On **paid data**, the asymmetry is structural/temporary -> a weaker-but-real derived edge has a better chance of persisting because fewer participants see the input.

**Correct sequencing (adopted 2026-08-13) — exhaust free derivation BEFORE paid:**
1. **Stage 1 (cost = 0):** Run the derive-from-data method on the free data we already own (incl. the years of historical data we have). Mine it for objective, machine-executable observations with a why; run each through the harness. No purchase required to at least try.
2. **Stage 2 (decision point):** If free-data derivation is genuinely exhausted AND a promising derived condition keeps failing only because the signal is too public (the moat matters), THEN — and only then — move to paid data, knowing we have genuinely exhausted the free lane first.
3. **No-waste rule:** We do not buy data before exhausting free derivation. This keeps the paid decision honest and bounded: paid data is justified only when the free barrier (lack of moat) is the binding constraint, not laziness or impatience.

**This is the forward direction to try now:** a free-data derive pass on our existing datasets. If it yields something objective that survives the harness -> we have an edge. If it fails across our data, we move to Stage 2 paid with the clean conscience that free is truly mined out.
