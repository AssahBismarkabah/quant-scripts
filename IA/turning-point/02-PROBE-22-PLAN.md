# Probe #22 Plan — Prediction Markets (Kalshi primary, Polymarket secondary)

**Date:** 2026-08-17
**Type:** Pre-registered research plan (agent's plan recorded in full). Companion to `01-capacity-constrained-arenas.md` (the turning-point thesis). Probe #22 is the first capacity-constrained probe; per our rule it is effectively a one-shot class decision — the verdict must be clean (CERTIFIED / DEAD / UNVERIFIABLE), never "unverifiable dressed up."
**Origin:** main agent's plan, recorded verbatim in substance. Two corrections precede the plan because they change what we should actually do.

## Correction 1 — The execution vehicle does not fit the new arena (confidence: high)

The record states prop capital is available as the execution vehicle for a machine-executable edge. Prop firms (Topstep, Apex, etc.) are futures and FX. Neither Kalshi, nor Polymarket, nor micro-cap equities are tradeable through a prop firm. **The capacity-constrained class is, almost entirely, an own-cash-account class.** If prop capital is the *only* deployable capital, the capacity-constrained fork is effectively closed before it starts — the futures-accessible corners are the liquid futures lanes already measured dead. Decide this first. If there is no own capital of at least $5k–$25k to put at risk in a Kalshi/Polymarket account, the prediction-market probe is a research exercise, not a path to income.

## Correction 2 — The 2026 base rate is not the 2016 academic base rate (confidence: high)

Prediction markets have been professionalized hard since 2023–2024: Kalshi sports volume dominated by professional market makers (Susquehanna widely reported as dominant maker); Polymarket political markets arbitraged by bots against polling aggregators and betting exchanges; the classic favorite-longshot bias (Snowberg & Wolfers) partially arbitraged. **Prior on a certified, family-supporting edge here: 20–35%, not optimism.** The probe is worth running because the data is free and the harness transfers; it is not worth running as hope.

## Target: Probe #22 = Prediction Markets (Kalshi primary, Polymarket secondary)

Reasons, ranked:

1. **Data is official, clean, free.** Kalshi publishes historical market data (trades, book snapshots for many markets). Polymarket trade history is on-chain (Polygon) via CLOB API and subgraphs. Contrast: micro-cap equities' free feeds have broken corporate actions, missing OTC prints, survivorship rot — a data-quality trap that consumes months and produces garbage verdicts.
2. **Event counts are high.** Sparsity killed 10b5-1 (3 events) and MVRV confluence (N=2). Kalshi has resolved tens of thousands of markets. The ≥30-events-per-gate discipline is satisfiable here — a real verdict instead of "unverifiable."
3. **Costs are modelable and structural.** Kalshi fee formula is mechanical: fee ≈ 0.07 × P × (1−P) per contract, rounded up to the cent (verify current schedule in Phase 0; maker fees/rebates differ by market class). At P=0.50 that is 1.75¢ on a 50¢ contract — ~3.5% of premium, one way. Brutal friction, exactly what our discipline demands. Polymarket historically zero-fee on most markets (verify — schedule changed for some categories in 2025). Wide spreads on thin books are measurable from book snapshots.
4. **There is an external oracle.** In sports and many event markets, Pinnacle's closing line is the sharpest probability estimate that exists in betting — it accepts sharp money and does not limit winners. Borrow the sharpest market's probability; trade the soft market's divergence from it. This answers the old "data-to-edge vs thesis-to-edge" question: the thesis is imported from a sharper market; our data work is the mapping, timing, and friction model.

**Why not micro-cap equities first:** two of its three pillars are already damaged goods in our record — small-cap shorting is a measured illusion (Step 2b died on borrow), EDGAR filing signals are measured sparse/insignificant (10b5-1, buyback put). What remains is "slow price discovery in uncovered names," real as a phenomenon but nearly impossible to backtest honestly with free data (assumed fills do not exist at assumed prices). It is probe #23 *if* our rule allows it after #22 — and the rule says if the first capacity-constrained probe returns dead or unverifiable, the class is not re-litigated. Probe selection is a one-shot decision; prediction markets maximize the probability of a clean verdict.

## Research sequence

### Phase 0 — Data census and friction characterization (1–2 weeks). No alpha research allowed.

Deliverables, pre-registered as inputs:

1. Pull Kalshi historical data (official CSV/API). Build market metadata table: ticker, category, resolution criteria, open/close dates, volume, OI, settlement. Pull Polymarket history via CLOB API/subgraph. Same table.
2. **Overlap census:** join platforms on event identity. Brutal here — "same event" is a trap. Kalshi and Polymarket word resolution criteria differently (settlement sources, deadlines, edge cases). Classify overlaps as *provably identical resolution*, *probably identical*, *not comparable*. Only the first class supports mechanical arbitrage. The count alone tells whether cross-platform arb is a candidate or a corpse.
3. **Friction model:** realized spreads and book depth by category and liquidity tier; Kalshi fee drag across the price range. Cost table: "to trade category X at size Y, round-trip friction is Z cents." This table is the wall every later candidate must climb.
4. **Adverse-selection measurement (LP probe autopsy, ported):** on thin-book markets, when passive resting orders fill, what does price do in the next 5/30/60 minutes? If fills concentrate on adverse jumps — the exact mechanism that printed −9.42 bps/trade on the perps LP test — any passive-liquidity candidate is pre-dead; do not waste a probe slot.

**Phase 0 gate:** at least one market family with ≥30 liquid resolved markets per quarter, honest friction below ~2–3 cents round trip, book data deep enough to model fills. If no family passes: verdict "dead on friction," stop before spending a probe.

### Phase 1 — Calibration baseline (1 week)

Before testing any trade, measure what the markets do:

- For every resolved market: final price (implied probability) and outcome. Bin by price (0–5%, 5–10%, …, 95–100%). Empirical resolution frequency per bin, per platform, per era (pre-2023, 2024, 2025–2026 — the pro-ization is recent).
- Output: calibration curve. 5% bin resolves 8% → longshots underpriced; resolves 3% → overpriced (classic longshot bias). Net of the fee formula.
- Costs almost nothing given Phase 0 data; constrains everything after — any "edge" must be consistent with the curve or it is a backtest artifact.

### Phase 2 — One spec, ranked candidates

One arena, one spec. Candidates in strict priority order, each with its own gate, promotion rule: *advances only if it clears net-of-friction, OOS sign agreement, N ≥ 30.*

- **Candidate A (highest prior): Sharp-line divergence.** For markets with a corresponding betting market, reference probability from Pinnacle's closing line with overround removed (multiplicative normalization: p*_i = p_i / Σp_j). Signal: when Kalshi/Polymarket price deviates from p* by more than (modeled friction × 2), bet toward p*. Measure the divergence distribution first — if divergences exceeding 2× friction occur fewer than 30 times/year/platform, the candidate is unverifiable-dead before trading. Why is clean: soft market priced by recreational flow and slow makers; sharp price discovered by the market that tolerates sharps. The oldest true edge in betting; the question is only whether enough survives on-exchange at our size.
- **Candidate B (pre-registered secondary): Net calibration skew.** From the Phase 1 curve, systematically buy the mispriced bin (typically buy NO on overpriced longshots) net of fees, restricted to sufficient liquidity. Why: recreational preference for lottery payoffs. Risk: mostly arbitraged by 2025–2026; may be flat net of fees → dead.
- **Candidate C (pre-registered tertiary): Cross-platform convergence.** Only if Phase 0's overlap census found meaningful provably-identical markets. Buy the cheap side across platforms, hold to resolution. Why: same event, two prices, forced convergence at settlement. Risks: capital lockup until resolution; settlement-criteria mismatch (the real killer — mis-mapped "identical" markets blow this trade up); likely low event counts.
- **Candidate D: Passive market-making on thin books — NOT-PROBED unless Phase 0's adverse-selection measurement is favorable.** Given the LP post-mortem, prior is low. Do not spend the probe slot by default.

**Excluded by construction:** UMA/oracle dispute "edge," wording-ambiguity sniping, anything requiring discretionary judgment of resolution criteria. Not machine-executable, not backtestable, violates the non-discretionary constraint. It is the prediction-market version of retail gambling.

### Phase 3 — Execution pilot (only on CERTIFIED)

If a candidate certifies: deploy with the smallest possible live size for 30+ trades. The pilot's single job: measure realized slippage vs modeled friction. Realized worse than model by more than a pre-registered tolerance → back to Phase 0 friction model, do not scale. Kill-switch: daily loss cap and total-pilot loss cap, hard-coded, identical logic to the existing harness. Only after realized friction matches does sizing begin, with a pre-registered capacity ramp and a hard stop at measured capacity (the point where our own fills start moving the book).

## Pre-registration document contents (before any code)

1. Universe definition: categories, liquidity floor, date ranges, IS/OOS split by calendar time (not random — these markets structural-break; OOS must be later than IS).
2. Phase 0 cost table, frozen as the friction model.
3. Per-candidate: signal definition, entry/exit rules, the 2× friction threshold, N ≥ 30 gate, OOS sign-agreement gate.
4. The three verdicts, explicitly: CERTIFIED / DEAD / UNVERIFIABLE — and the rule that UNVERIFIABLE is terminal, not a reason to loosen N.
5. Capacity pre-estimate: for each candidate, the book depth at which our fill moves price >1 cent — the capacity cap, written down now.
6. Stop rule: if all candidates fail, the class is closed and the fork returns to stop. No re-litigation.

## Pre-mortem: the five ways this probe dies (write into the spec)

1. **Arb-compression death:** divergence distribution <30 events/year exceeding 2× friction. Bots got there first. (Most likely death for Candidate C.)
2. **Fee-formula death:** skew exists gross, dies net of 0.07×P×(1−P). (Plausible for B on Kalshi; Polymarket's zero-fee structure is where B survives if anywhere.)
3. **Sparsity death:** overlap census or divergence census returns counts too low for our gates. Verdict: UNVERIFIABLE — recorded honestly, exactly as MVRV confluence was.
4. **Adverse-selection death:** fills on thin books concentrate on news jumps, same −9 bps mechanism as the perps LP probe. (Kills any passive candidate.)
5. **Capacity death:** the edge certifies but book depth caps it at $20–50k deployed, i.e., $5–15k/year. The most dangerous outcome — a real edge that cannot feed a family. Pre-register minimum viable capacity now; if certified capacity is below the number that matters, the honest verdict is "real but insufficient," and that is a stop, not a maybe.

## Timeline and income honesty check

Phase 0–1: 2–3 weeks. Phase 2: 3–4 weeks. Phase 3 pilot if certified: 4–6 weeks. **Total: 8–13 weeks to a terminal verdict.** If not resolved by then, something is wrong with execution, not the market.

The known number: even the best-case certified outcome at our capital scale is probably a five-figure annual edge in year one, with the real payoff being compounding process and capital together over years. If "sustain the family" means income within months, this probe does not change the expected-value ranking from the decision memo — income work still dominates, and the probe becomes a nights-and-weekends experiment rather than the plan. Decide which it is before pulling the first dataset; that decision determines how much time the probe is allowed to consume.

## Next concrete action

Write the Phase 0 section of Spec #22 — data census, overlap census, friction table — and freeze it. The Kalshi historical data pull is the first script. Nothing else until Phase 0's gate is read.

## Status

- **2026-08-19 (Candidate A measured → DEAD, soccer census):** Polymarket soccer moneylines vs Pinnacle closing lines (football-data.co.uk 2025/26 season, 5 leagues, Aug 2025–Jan 2026): 191 matched fixtures, 80 full 3-way. PM internal consistency 1.005; PM draw prob 0.262 vs Pinnacle 0.261. Divergence census: >1¢: 36% of fixtures, >2¢: 7.3%, >4¢: 1 (0.5%, 4.9¢), >6¢: 0, >10¢: 0. **Verdict: unverifiable-dead per pre-registered gate (1 event >4¢ in ~5 months ≪ 30/yr).** PM's sports pricing is welded to the sharp line within ~2¢ (same in-house MM engine prices all PM sports; prior for MLB/NBA/CS2 is identical). Two data-layer discoveries along the way: (1) data-api `before`/`after` params are IGNORED (offset pagination is the only correct method); (2) PM sports markets continue trading POST-kickoff until oracle resolution — reference prices must filter `ts < kickoff`. Artifacts: `candidate_a_matches.csv`, `candidate_a_pm_trades.parquet`, `candidate_a_analysis.csv`, scripts `candidate_a_soccer.py` / `candidate_a_fetch_trades.py` / `candidate_a_analysis.py`.
- **2026-08-19 (Candidate B measured on Polymarket → DEAD):** 353 BTC 15m windows (Jun–Aug 2026), PM price refs at T−300s/T−180s/T−60s from data-api trades (offset-paginated, ts < kickoff filter, Up/Down outcome labels). PM calibration mirrors Kalshi: tails extreme-bimodal (135/353 windows ≤5¢ or ≥90¢ at T−300), 0–5¢ bucket p_up=0.00% (n=65+), 95–100¢ bucket p_up=100% (n=70+) — perfectly calibrated, no longshot bias. Aggregate mid-bin (10–90¢): T−300 priced 56.1¢ vs realized 56.3% (n=190); T−180: 56.0 vs 55.9 (n=136); T−60: 60.6 vs 61.0 (n=77). Per-bin "100% win" cells (75–85¢, n≈13) are small-n noise. Verdict: B dead on BOTH platforms (Kalshi Phase 1 baseline, spec §6; this PM curve). Artifacts: `pm_calib_trades.parquet`, `pm_calibration_btc15m.csv`, scripts `pm_calib_fetch.py` / `pm_calib_analysis.py`. **PM data is CLEAN (no kingsets-style contamination) — the T−60 curve here is the real entry-horizon read, and it shows no exploitable skew.**
- **2026-08-19 — PROBE TERMINAL READ (all pre-registered candidates measured → DEAD):** B dead on Kalshi and Polymarket (calibration clean, no skew net of fees); C dead (94.2% settle agreement, disagreements are micro-move oracle noise); A dead on the most liquid representative family (PM soccer within ~2¢ of Pinnacle closing lines; 1 event >4¢ in 5 months ≪ 30/yr gate). Per the plan's own stop rule (pre-registered, no re-litigation): **the class is closed on measurement; verdicts recorded as DEAD, not UNVERIFIABLE** (each surface was measured, not sparse — the data answered). Unmeasured at stop: A on MLB/NBA/CS2/tennis (Pinnacle quota-limited) and Kalshi-side sports divergence (API finals only Jun 13+, no sharp-line source at scale) — prior is identical (same PM MM engine prices all sports); the theoretical live oracle-observation variant (observe Chainlink stream + RTI boundary values in the final seconds) is noted as the only structural possibility and is not an income surface (sub-1¢/window EV, execution risk, capacity ~$1–10k). The probe's honest bottom line: the measured surfaces are arb-compressed on both platforms; consistent with pre-registered death #1 (arb-compression death).
- **2026-08-17:** Plan recorded. Decisions made per plan's own recommendations (not re-litigated):
  - **D1 — own cash:** Phases 0–2 proceed regardless of capital (data is free, harness transfers); own cash (≥$5k–$25k) gates only Phase 3. No cash at certification ⇒ verdict "CERTIFIED-BUT-NOT-EXECUTABLE," a stop, not a maybe.
  - **D2 — income honesty:** income work remains priority; probe is the disciplined secondary effort, hard budget 8–13 weeks to terminal verdict.
  - **D3 — Phase 0 spec:** written and frozen at `research-specs/prediction-markets-probe22-spec.md` (2026-08-17). Next action: Kalshi historical data pull — the first script.
- **2026-08-19 (Phase 1 baseline + Candidate C):** Phase 0 gate PASSED, committed as `37105db`. Phase 1 finals calibration DONE (Kalshi BTC 15m, API finals): 6,396 markets, finals extreme-bimodal, both tail bins perfectly calibrated, no exploitable final-price skew (spec §6). Kingsets trades files are TRUNCATED + synthetic terminal marks (API `last_price_dollars` = ground truth; see spec §6).
  - **Candidate C measured → DEAD.** Kalshi vs Polymarket on 1,198 provably-identical 15m windows (all 4 cryptos, API finals Jun 13–Jul 24 + catalog results Apr–Jul): settle agreement 94.2%; the 5.8% disagreements are all micro-move windows (median BTC |move| 0.025%, max 0.11%) where the two settlement oracles (CF Benchmarks RTI vs Chainlink stream) sample boundary instants differently — mechanical noise, no ex-ante signal, no capacity. Final-price divergence on same-direction windows: median ~0¢; the apparent >10¢ tail is entirely gamma `lastTradePrice` staleness on illiquid PM markets (vol < 10k contracts; closing quotes agree with Kalshi). The overlap census join was re-validated as CORRECT (event ticker = window end; PM slug = window start; endDate guards matched 1200/1200). Verdict: dead on arb-compression/sparsity per pre-registered gate — no 30 events/year > 2× friction. Theoretical live-only variant (observe Chainlink stream + RTI boundary values in the last seconds, trade the flip) noted but not an income surface. Fixed `divergence_crossplatform.py` (Kalshi batch must use MARKET_TICKER from catalog, not event ticker + '-00'; verified `api.elections.kalshi.com`). Artifacts: `outputs/divergence_finalprice_jun13.csv`, `outputs/pm_settle_vs_btc.csv`, `outputs/divergence_crossplatform.csv`.