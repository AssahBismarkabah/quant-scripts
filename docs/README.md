# Documentation Index

## Status (read this first)

- [PROJECT RECORD — everything tested, where we are now](PROJECT_RECORD.md) — the complete, consolidated record: 21 tests, 0 surviving edges, validated harness, terminal fork (stop or cost-bearing). Single source of truth; supersedes this index as the status document.
- [BVMAC/CEMAC Retail-Scale Trading Feasibility](../IA/bvmac-cemac-feasibility.md) — primary-source local-market assessment (2026-08-21): account/data access exists, but the daily cash fixing, thin equity market, high published transaction costs, and no identified mechanism make active trading a NO-GO under current evidence.
- [BVMAC Broker Capability Audit](../IA/bvmac-broker-capability-audit.md) — broker-by-broker evidence audit (2026-08-21): service differences exist, but no published customer capability changes BVMAC’s active-trading feasibility; four documented-active brokers are the only sensible written-verification shortlist.
- [VWAP Book Source Audit](../IA/vwap-book-source-audit.md) — source audit (2026-08-21): no book-derived setup is both distinct and sufficiently specified to justify a new test; the earnings example remains only a future capability-triggered hypothesis, not a strategy.
- [Turning Point — Capacity-Constrained Arenas](../IA/turning-point/01-capacity-constrained-arenas.md) — re-opens the fork for one class: lanes where retail size is the advantage (prediction markets, micro-cap long-only, small-cap options, obscure crypto). Triage of probeability with free data; the next probe must be pre-registered, with "unverifiable" accepted as a legitimate verdict.
- [Probe #22 Plan — Prediction Markets](../IA/turning-point/02-PROBE-22-PLAN.md) — the full recorded plan: two corrections (execution vehicle doesn't fit the arena; 2026 base rate), target selection, Phase 0-3 research sequence with gates, ranked candidates A-D, pre-registration contents, five-way pre-mortem, timeline (8-13 weeks to terminal verdict).
- [Probe #22 Spec — Phase 0 (FROZEN)](../research-specs/prediction-markets-probe22-spec.md) — the data census, overlap census, friction model, and adverse-selection measurement, pre-registered before any code. Decisions D1-D3 recorded. Gate: one family with ≥30 liquid resolved markets/quarter, <2-3¢ round-trip friction, book depth sufficient; FAIL = "dead on friction."
- [Probe #23 Spec — Soft-Book vs Pinnacle (TERMINAL — DEAD)](../research-specs/softbook-vs-pinnacle-probe23-spec.md) — the user's one-shot amendment (the only re-opening): soft-book closing vs de-juiced Pinnacle closing, flat-stake realized backtest, Brier falsification, gates G1-G5. Verdict 2026-08-20: DEAD — IS realized ROI −33.3% net at τ=2% (n=468); soft-book Brier equals Pinnacle's (snapshot-timing artifact, not mispricing). Sports lane terminal on measurement.
- [Probe #24 Spec — Rule of Four (DEAD ON MEASUREMENT, 2026-08-20)](../research-specs/rule-of-four-probe24-spec.md) — user-directed news-event breakout probe on DAX + FTSE 100 (Tom Hougaard "Rule of Four"): first 4 5-min candles after NFP/FOMC = range, breakout entry, opposite-side stop, 1:1/1:2/1:3 targets. Full frozen protocol run: Phase 0 census passed, primary trigger UNVERIFIABLE per-market but DEAD pooled, V2 trigger DEAD on both markets — every config with sufficient sample fails OOS. ORB/opening-range family closed permanently.

## Research Framework

- [Institutional Approach](../IA/institutional-approach.md)
- [Market Edge Framework](../IA/market-edge-framework.md)
- [Structural Mechanics](../IA/structural-mechanics.md)
- [Funding Basis Research Spec](../IA/funding-basis-research-spec.md)
- [Vol Targeting Research Spec](../IA/vol-targeting-research-spec.md)
- [Vol Targeting Revisit Research Spec (v2)](../IA/vol-targeting-revisit-research-spec.md)
- [Vol Targeting Long-History Research Spec (v3)](../IA/vol-targeting-long-history-research-spec.md)
- [Data and Portfolio Roadmap](../IA/data-and-portfolio-roadmap.md)
- [Research Pipeline Review](../IA/research-pipeline-review.md)
- [2025-2026 Structural Edge Survey](../IA/structural-edge-survey-2025-2026.md)
- [Retail Edge Landscape — Post-Test Synthesis](../IA/retail-edge-landscape.md)
- [Buyback Timing Research Spec](../IA/buyback-timing-research-spec.md)
- [NQ VWAP-Pullback Research Spec](../IA/nq-vwap-pullback-research-spec.md)
- [10b5-1 Adoption Timing Research Spec](../IA/10b5-1-adoption-timing-research-spec.md)
- [Vol Risk Premium Research Spec](../IA/vol-risk-premium-research-spec.md)
- [Short Vol: Tail-Overlay Premium Capture (V3)](../strategies/vol-risk-premium/V3_TAIL_OVERLAY.md)
- [Opening Range & Gap Strategies Research Spec](../IA/opening-range-gap-strategies-research-spec.md)
- [Five Structural Edges Research Spec](../IA/five-structural-edges-research-spec.md)
- [Bitcoin MVRV Research Spec](../IA/bitcoin-mvrv-research-spec.md)
- [PEAD Research Spec](../IA/pead-research-spec.md)

## Strategy Specs

- [NQ VWAP-Pullback / "Drift VWOP Pullback"](../strategies/nq-vwap-pullback/NQ_VWAP_PULLBACK.md) - DISCONFIRMED (2026-08-08): pre-registered probe on Databento NQ; ~61% win rate reproduces but net-negative IS and OOS (all 5 gates failed)
- [10b5-1 Adoption Timing / "Cooling-Off Watch"](../strategies/10b5-1-timing/10B5-1_TIMING.md) - DISCONFIRMED (2026-08-07): real-time issuer 10b5-1 repurchase-adoption signal fails the pre-registered sparsity gate (2 distinct issuers vs >=30 in a 993-filing EDGAR harvest); intrinsically sparse, family closed
- [Buyback Timing / "Buyback Put"](../strategies/buyback-timing/BUYBACK_TIMING.md) - Bounded study NOT ADVANCED (2026-08-04): 47 events, 20d point positive but insignificant (t 0.64, bootstrap p5<0), drop-best->zero; full multi-year sample pending
- [Vol Targeting Flow Fade](../strategies/vol-targeting/VOL_TARGETING.md) - MEASURED-BUT-MARGINAL (2026-08-04): statistical significance on extended 1993-2026 sample (~840 events) but ~1-2 bps excess over a random long hold; no advance. Prior rejections: v2 p5 gate, v1 on verified data
- [IVAMR](../strategies/ivamr/IVAMR.md) - DISCONFIRMED (2026-08-08): all 5 pre-registered gates failed on Databento NQ 1-min
- [Opening-Range / Gap trio (ORB, Gap Fill, Oops)](../strategies/opening-range-gap/OPENING_RANGE_GAP.md) - DISCONFIRMED (2026-08-09): ORB + Oops fail all pre-registered gates on NQ; Gap Fill not falsifiable as a trade (no stop/exit in source) and its raw gap-fill rate fails OOS (0.5885 < 0.60)
- [SPX GEX](../strategies/spx-gex/SPX_GEX.md) - rejected Level 1, L2 declined (2026-08-04)
- [Funding Basis](../strategies/funding-basis/FUNDING_BASIS.md) - rejected
- [Index Rebalancing](../strategies/index-rebalancing/INDEX_REBALANCING.md) - Rejected L1-2, then CLOSED (2026-08-04): single March-2025 S&P 600 batch; year-breakdown not persistent (2024 n/s, 2025 +1542, 2026 -786 bps)
- [Short Vol / VRP](../strategies/vol-risk-premium/VOL_RISK_PREMIUM.md) - DISCONFIRMED (2026-08-08): V1 level positive; V2 naive harvest is ruin (+452%/-95% DD); V3 stress-overlay kills edge - [V3](vol-risk-premium/V3_TAIL_OVERLAY.md)
- [Five Structural Edges (PEAD / Congressional / Bitcoin MVRV)](../strategies/five-structural-edges/FIVE_STRUCTURAL_EDGES.md) - EXTRACTION/CLOSED (2026-08-10): all 5 claims resolved — PEAD + Bitcoin MVRV DISCONFIRMED by probes, ORB + VRP DISCONFIRMED (duplicate families), Congressional CLOSED; no deployable edge
- [PEAD (Earnings-Surprise Drift)](../strategies/pead/PEAD.md) - DISCONFIRMED (2026-08-09): drift reproduces IS (+2.07%, PF 1.11) but fades OOS (≈0, PF 0.94) on Kaggle US panel 2012-2021; no net OOS edge
- [Bitcoin MVRV Smart DCA](../strategies/bitcoin-mvrv/BITCOIN_MVRV.md) - DISCONFIRMED (2026-08-10): dynamic DCA drawdown benefit not reproducible in-sample (IS −83.7% vs −84.5% DD, CAGR 76% vs 161%); only OOS 2021-26 shows it (−53% vs −77%); Coin Metrics community data

## Code

- `src/quant_scripts/funding_basis.py` contains the current executable research scaffold for funding-basis validation.
- `src/quant_scripts/buyback_timing/` contains the buyback-timing pipeline (harvest/classify, mapping, bars, bounded event study). Research workflow: `research/buyback-timing/Makefile` (`make harvest`, `make study`).
- `src/quant_scripts/opening_range_gap/` contains the opening-range / gap trio probe (ORB, Gap Fill, Oops). Research workflow: `research/opening-range-gap/Makefile` (`make probe`); reads the owned NQ 1-min caches, no new fetch.
