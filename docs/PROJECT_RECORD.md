# Project Record — Everything Tested, Where We Are Now

**Date:** 2026-08-17
**Type:** Complete, consolidated record of every research spec, probe, and verdict in this repo, and the current position it implies. This is the single source of truth for "what have we done / where are we now." Each row links to its full evidence file.

---

## 1. What this project is

A systematic, pre-registered search for a deployable trading edge at retail scale (small capital, free/retail-priced data, retail execution), across equity, futures, options, and crypto. The method, not any single test, is the product: every candidate is frozen in a spec before running, tested out-of-sample under honest costs, benchmarked against the correct alternative, and recorded with a gate that produces PASS/DISCONFIRMED/CLOSED — never "maybe."

**Result of the whole project, in one sentence:** with a validated measurement harness, every lane that is reachable at retail scale — free-data signals, order flow, options microstructure, sector rotation, risk-carry, and market-making — has been tested and measured dead; the lanes that still contain edge (colocation-speed execution, L2/queue-priority market making, capital that can warehouse risk) cost what a retail account cannot pay.

---

## 2. The method (why the verdicts are trustworthy)

- **Pre-registration:** every probe has a frozen spec (in `research-specs/`) written *before* results — method, data, gates, stop rules. No parameter is tuned to the outcome; a spec is the gate.
- **Positive control (2026-08-12):** Test A of the decision memo passed — the harness retrieves known embedded strong edges ~100% and never claims alpha on nulls (0% false positives). **Every DISCONFIRMED verdict below is therefore interpretable**: it means the candidate failed, not the pipeline.
- **Costs and benchmarks:** all probes net of realistic fees/slippage, benchmarked against the buy-and-hold alternative (index or asset), not against zero.
- **Anti-result-hunting rules:** OOS must agree in sign with IS; no survivor without a why; a scan with zero survivors is a valid result; closed families are not resurfaced (see §9).

---

## 3. Complete test record (chronological)

| # | Date | Candidate | Family | Verdict | One-line why |
|---|---|---|---|---|---|
| 1 | 2026-08-04 | Buyback timing ("buyback put") | Structural forced flow | **NOT ADVANCED** | 47 events; 20d point positive but insignificant (bootstrap p5<0), drop-best→0 |
| 2 | 2026-08-04 | Vol-targeting flow fade | Flow/deleveraging | **MEASURED-BUT-MARGINAL** | ~840 events 1993-2026; significant but ~1-2 bps over market drift; not tradable |
| 3 | 2026-08-04 | SPX dealer gamma (GEX) | Options/regime | **REJECTED L1, CLOSED** | Fails conservative friction; V1 finding: non-predictive before costs |
| 4 | 2026-08-04 | Funding basis carry (BTC) | Relative value | **REJECTED** | Fails under conservative model |
| 5 | 2026-08-04 | Index rebalancing | Event-driven | **REJECTED, CLOSED** | Edge is a single March-2025 S&P 600 batch; 2024 n/s, 2025 +1542, 2026 −786 bps |
| 6 | 2026-08-07 | 10b5-1 adoption timing | Data asymmetry | **DISCONFIRMED** | Sparsity: 3 events / 2 issuers vs required ≥30 in 993-filing EDGAR harvest; intrinsically sparse |
| 7 | 2026-08-08 | NQ VWAP-pullback | Intraday micro | **DISCONFIRMED** | ~61% win rate reproduces but net-negative IS and OOS; all 5 gates failed |
| 8 | 2026-08-08 | IVAMR (volume profile) | Intraday micro | **DISCONFIRMED** | All 5 gates failed on Databento NQ 1-min 2013-2023; net-negative both windows |
| 9 | 2026-08-08 | Short vol / VRP (V1-V3) | Risk-carry | **DISCONFIRMED** | V1: level real (+3-4 vol pts). V2: naive harvest is ruin (+452% / −95% DD). V3: stress-overlay flees the premium (skips +646%, keeps −26%) |
| 10 | 2026-08-09 | ORB / Gap-fill / "Oops" trio | Intraday opening | **DISCONFIRMED** | ORB + Oops fail all gates on NQ; gap-fill rate fails OOS (0.5885 < 0.60); gap fill not falsifiable as a trade |
| 11 | 2026-08-09 | PEAD (earnings drift) | Cross-sectional anomaly | **DISCONFIRMED** | Drift reproduces IS (+2.07%, PF 1.11) but fades OOS (≈0, PF 0.94) on 1998-2021 panel |
| 12 | 2026-08-10 | Bitcoin MVRV smart DCA | On-chain timing | **DISCONFIRMED** | DD benefit not reproducible in-sample (IS −83.7% vs −84.5% DD, CAGR 76% vs 161%); only one OOS window shows it |
| 13 | 2026-08-11 | MVRV × cycle confluence | On-chain timing | **CLOSED** | N=2 confluence events in 16 years; not testable; relaxed variants add nothing over MVRV alone |
| 14 | 2026-08-12 | Step 2b diverse basket (13 signals, long-only + basket) | Portfolio alpha | **FAILS-OOS** | Only clears under optimistic 1.5%/yr short-borrow; at realistic 5% hard-to-borrow it fails (p5 < 0) — the apparent edge was unborrowable short-legs |
| 15 | 2026-08-12 | Positive control (Test A + B) | Method | **PASS** | Harness retrieves known edges ~100%, 0% null false-positives — all verdicts interpretable |
| 16 | 2026-08-15 | Dealer gamma (paid lane, tested free) | Options | **DEAD** | LambdaClass SPY options 2008-2025 (24.7M rows): OI/gamma predicts vol (corr +0.47) but not returns; monetizing = short-vol = closed VRP family |
| 17 | 2026-08-15 | Order flow (paid lane, cached data) | Microstructure | **DEAD** | No predictive state above friction |
| 18 | 2026-08-15 | Derive pass Datasets A-D | Data mining | **EXHAUSTED, 0 survivors** | A: options 2/56 survivors rejected (tail gate). B: PEAD panel 5/12 = public rediscoveries. C: NQ/ES 0/24. D: unsupervised joint-state 0/12 |
| 19 | 2026-08-16 | Crypto perps derive pass (E) | Data mining | **EXHAUSTED, 0 candidates** | 1 gate-survivor (first-hour vol → rest-of-day) discarded on interrogation: Spearman ≈ 0, flips under trim, bull-phase beta artifact |
| 20 | 2026-08-16 | Short-term sector momentum (QC) | Cross-sectional momentum | **DISCONFIRMED** | Reproduced 1:1 (raw px, point-in-time ROC, fees): CAGR 9.6%/Sharpe 0.58 vs SPY 13.8%/0.81, QQQ 19.5%/0.91. Lags both in every window; only 2022 dodge (+2.1% vs −18.6%) which does not compound. QC-cloud's 62.6% (order log d274f46d) verified real but QQQ was +33.4% CAGR in that window |
| 21 | 2026-08-17 | **Liquidity provision (crypto perps)** | Market making | **DISCONFIRMED** | Mid-quote passive fills, BTC/ETH 1m 2020-2026, ~1.7M round trips: BTC mean −9.42 bps/trade (p5 −9.50), ETH −10.82; fills concentrate on adverse trade-throughs, continuation eats exit, fees finish. All 4 gates failed. Real MMs earn via queue priority/L2/colocation — none available to retail |

---

## 4. Additional records (mined, not probed)

- **Frontier mining (arXiv/SSRN/Crossref/Scholar, 478 papers):** funnel's honest output — no strong, freshly-available, free-data, forced-counterparty edge; recurring arXiv q-fin frontier is method/ABM/ML-heavy, nothing advanced. (`IA/research-frontier-mining.md`)
- **Structural-edge survey 2025-2026 (forced flows, 0DTE/gamma, T+1, quarter-end, data asymmetry):** all shortlist candidates either closed or tested-dead; buyback put tested-not-advanced. (`IA/structural-edge-survey-2025-2026.md`)
- **Five structural edges (transcript claims):** 5 of 5 resolved — PEAD + MVRV DISCONFIRMED by probes, ORB + VRP DISCONFIRMED (duplicate families), Congressional CLOSED. (`strategies/five-structural-edges/`)

---

## 5. Data owned (no purchase is justified by any result)

- Databento NQ/ES 1-min caches (2013-2023; pre-account-lock) — order-flow/relative-value research
- LambdaClass SPY options 2008-2025 (24.7M rows) — exhausted
- PEAD equity panel (2.4GB, ~5k US names 1998-2021) — exhausted
- Binance USDT-M 1m klines + funding (BTC/ETH, 2020→2026-07) — exhausted
- Coin Metrics MVRV (BTC 2010-2026) — exhausted
- SPY/VXX/SVXY/VIX/VIX3M/VIX9D, FRED T-bills — exhausted
- EDGAR full-text pipelines — 10b5-1 family closed on sparsity

---

## 6. Where we are now (the answer)

1. **The question is closed, by evidence.** "Is it me, or is the edge gone?" — the harness is validated (Test A PASS) and every reachable lane is measured dead. The answer: at retail scale with retail execution and retail-priced data, the accessible surface contains no deployable edge. The missing piece was never a strategy — it is that the remaining lanes cost what a retail account cannot pay (L2 feeds, execution infrastructure, capital that can warehouse risk). The capacity-constrained re-open (Probe #22 prediction markets; Probe #23 soft-book sports via the user's one-shot amendment) is also measured dead (2026-08-20) — both sides of the sports lane fail the pre-registered gates on realized outcomes.
2. **The two honest options (the decision memo's terminal fork):**
   - **(a) Stop.** The record is complete; the repo is a finished, trustworthy negative study — one of the only such records a retail trader is likely to ever see. Effort redirects to income work. No further research.
   - **(b) Change the game, not the search.** The only remaining lanes are cost-bearing: paid L2/order-book data + colocation-class execution (market making with real queue priority), or capacity-constrained corners that are by definition unverifiable at our scale, or capital large enough to warehouse risk (risk-carry with a ruin-accepting mandate). Each requires a capital commitment and a different operating model — a business decision, not a research question. If ever pursued, it must be pre-registered and gated exactly like everything above.
3. **The defensible middle (already measured, size it honestly):** risk-management overlay for drawdown reduction is real but small — ~2pp DD vs SPY over a decade, concentrated in 2022 (sector-momentum probe). Not alpha; deployable only as capital preservation, never as a returns strategy.

---

## 7. Framework and decision documents (map)

| Doc | Role |
|---|---|
| `IA/path-forward-decision-memo.md` | The governing decision doc: pre-registered 3-step program (positive control → aggregation → fork). Steps 1-2 executed: PASS then FAILS-OOS. Terminal fork: stop or cost-bearing |
| `IA/edge-discovery-direction.md` | Resolved the free-data vs microstructure tension; directed to exhaust free data via the derive pass first (done, exhausted) |
| `IA/derive-pass-stage1-spec.md` | The mining method + full status of datasets A-E (all exhausted) |
| `IA/data-inventory-stage1.md` | Inventory of all owned data + derive-pass results (8.9-8.16) |
| `IA/retail-edge-landscape.md` | Post-test synthesis: why the retail toolkit fails, why online traders appear profitable, and the LP result (Appendix C) |
| `IA/research-frontier-mining.md` | Paper-harvest pipeline + funnel read-out |
| `IA/research-pipeline-review.md` | Prior-candidate review table |
| `IA/structural-mechanics.md`, `IA/market-edge-framework.md`, `IA/institutional-approach.md` | Reference frameworks |
| `IA/Blueprint-for-the-Independent-Quant.md` | External-style blueprint (data-to-edge pipeline). **Diagnosed as the trap**: its Phase-2 automated edge discovery is the order-flow/derive path already tested dead; it never asks where edge comes from (see `retail-edge-landscape.md` §3 and this record §6) |
| `docs/README.md` | Link index (this record supersedes it as the status source) |

---

## 8. What is closed and must NOT be resurfaced

- Short-vol / VRP family (any form, including dealer-gamma monetization) — ruin tail; stress-conditioning flees the premium
- ORB / opening-range / gap family (incl. "IVB", "Oops") — tested dead; gap-fill not falsifiable as a trade
- Order-flow / quote-imbalance / aggression predictive states on the owned intraday data — no thesis survived
- Free-data cross-sectional equity signals (momentum, reversal, low-vol, PEAD family) — public rediscoveries, OOS-dead
- Bitcoin timing families (MVRV, cycle confluence, funding-basis carry) — dead or N=2
- 10b5-1 / buyback-timing family — sparse or insignificant
- Mid-quote passive liquidity provision without L2/queue priority — measured −9.4 bps/trade (2026-08-17)
- Index-rebalancing family — single-batch artifact
- Prediction markets / sports betting (Kalshi, Polymarket, soft-book sports) — Probe #22 (exchange side) + Probe #23 (soft-book side, user's one-shot amendment) both measured DEAD 2026-08-20; sports lane terminal on measurement; class not re-litigated per turning-point §5

---

## 9. Decision space (if this record is ever re-opened)

The only legitimate reopen conditions:
1. A **new capability** appears (L2 data, co-location, larger capital, order-flow data with a thesis) — i.e., the cost-bearing precondition changes. Then the new lane gets a pre-registered spec, same discipline.
2. A genuinely **new observable** with a forced-counterparty why that is not in the closed list above, with free/owned data — triaged through the frontier-mining funnel first.
3. **Capital preservation only:** a defensive overlay with the pre-measured ~2pp DD expectation, documented as risk management, not alpha.

None of these are open questions today. The record is complete.
