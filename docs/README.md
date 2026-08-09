# Documentation Index

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
- [Buyback Timing Research Spec](../IA/buyback-timing-research-spec.md)
- [NQ VWAP-Pullback Research Spec](../IA/nq-vwap-pullback-research-spec.md)
- [10b5-1 Adoption Timing Research Spec](../IA/10b5-1-adoption-timing-research-spec.md)
- [Vol Risk Premium Research Spec](../IA/vol-risk-premium-research-spec.md)

## Strategy Specs

- [NQ VWAP-Pullback / "Drift VWOP Pullback"](../strategies/nq-vwap-pullback/NQ_VWAP_PULLBACK.md) - DISCONFIRMED (2026-08-08): pre-registered probe on Databento NQ; ~61% win rate reproduces but net-negative IS and OOS (all 5 gates failed)
- [10b5-1 Adoption Timing / "Cooling-Off Watch"](../strategies/10b5-1-timing/10B5-1_TIMING.md) - DISCONFIRMED (2026-08-07): real-time issuer 10b5-1 repurchase-adoption signal fails the pre-registered sparsity gate (2 distinct issuers vs >=30 in a 993-filing EDGAR harvest); intrinsically sparse, family closed
- [Buyback Timing / "Buyback Put"](../strategies/buyback-timing/BUYBACK_TIMING.md) - Bounded study NOT ADVANCED (2026-08-04): 47 events, 20d point positive but insignificant (t 0.64, bootstrap p5<0), drop-best->zero; full multi-year sample pending
- [Vol Targeting Flow Fade](../strategies/vol-targeting/VOL_TARGETING.md) - MEASURED-BUT-MARGINAL (2026-08-04): statistical significance on extended 1993-2026 sample (~840 events) but ~1-2 bps excess over a random long hold; no advance. Prior rejections: v2 p5 gate, v1 on verified data
- [IVAMR](../strategies/ivamr/IVAMR.md) - DISCONFIRMED (2026-08-08): all 5 pre-registered gates failed on Databento NQ 1-min
- [SPX GEX](../strategies/spx-gex/SPX_GEX.md) - rejected Level 1, L2 declined (2026-08-04)
- [Funding Basis](../strategies/funding-basis/FUNDING_BASIS.md) - rejected
- [Index Rebalancing](../strategies/index-rebalancing/INDEX_REBALANCING.md) - Rejected L1-2, then CLOSED (2026-08-04): single March-2025 S&P 600 batch; year-breakdown not persistent (2024 n/s, 2025 +1542, 2026 -786 bps)
- [Short Vol / VRP](../strategies/vol-risk-premium/VOL_RISK_PREMIUM.md) - MEASURED-POSITIVE-LEVEL, NOT ADVANCED (2026-08-08): V1 VRP level positive all eras; harvestability incl. tail is V2

## Code

- `src/quant_scripts/funding_basis.py` contains the current executable research scaffold for funding-basis validation.
- `src/quant_scripts/buyback_timing/` contains the buyback-timing pipeline (harvest/classify, mapping, bars, bounded event study). Research workflow: `research/buyback-timing/Makefile` (`make harvest`, `make study`).

