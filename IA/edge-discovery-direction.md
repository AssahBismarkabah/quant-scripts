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

- **2026-08-13:** Resolution recorded. Free-data anomaly phase: **closed** (measured-dead). The only remaining route to a non-decayed edge is the **data-moat + derive-from-data + objective-rule + validate** path (memo Step 3 option (a), now with the direction made explicit). The fork is still genuinely: (a) commit to buying a microstructure/data moat and doing the uncertain derivation, or (b) stop. No third "free candidate" option.
- Open sub-decision if (a): which data moat to buy — order-flow (order book/MBO/delta) vs options microstructure (OI/IV/dealer gamma) vs long intraday history (for the already-scoped IVAMR/dealer-gamma candidates). Each is a separate pre-registered program with a hard no-go.
