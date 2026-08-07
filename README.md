# quant-scripts

A collection of quantitative trading strategies, research specs, and executable scaffolds.

## Tested Strategies

| Strategy | Type | Status |
|---|---|---|
| [Buyback Timing / "Buyback Put"](strategies/buyback-timing/BUYBACK_TIMING.md) | Structural forced-flow / data asymmetry | Bounded study NOT ADVANCED (2026-08-04): 47 events, 20d point positive but insignificant (bootstrap p5<0), drop-best->zero; full multi-year sample pending |
| [Vol Targeting Flow Fade](strategies/vol-targeting/VOL_TARGETING.md) | Flow-Driven / Forced-Deleveraging Fade | Measured-but-marginal / no advance (2026-08-04): on extended 1993-2026 sample (~840 events) bootstrap p5 passes but effect is ~1-2 bps over market drift; v1 (1-day) and v2 (p5 gate on ~80 events) rejected earlier |
| [IVAMR](strategies/ivamr/IVAMR.md) | Intraday Value Area Momentum & Mean Reversion | Not pursued (2026-08-04): no pre-2023 data for its own OOS protocol; behavioral edge |
| [SPX GEX](strategies/spx-gex/SPX_GEX.md) | Intraday Bias / Regime Filter | Rejected at Level 1 (friction gate); Level-2 upgrade declined (2026-08-04) |
| [Funding Basis](strategies/funding-basis/FUNDING_BASIS.md) | Relative Value / Funding Carry | Rejected Under Current Assumptions |
| [Index Rebalancing](strategies/index-rebalancing/INDEX_REBALANCING.md) | Event-Driven Mean Reversion | Rejected Level 1-2, then CLOSED (2026-08-04): S&P 600 short-additions is a single March-2025 batch; year-breakdown shows 2024 n/s, 2025 +1542 bps, 2026 -786 bps - not persistent |

## Documentation

- [Documentation Index](docs/README.md)

## Research Frontier Mining

Automated harvest of the recent quant-finance frontier (arXiv + Crossref + SSRN + Google Scholar) into a ranked, finance-gated, testable shortlist. See [the process doc](IA/research-frontier-mining.md); re-run via [the Makefile](research/frontier-mining/Makefile) (`make harvest`).

- [Ranked papers CSV](research/frontier-mining/outputs/frontier_papers.csv) — scored/ranked candidates; each row carries a `url` link to the paper (SSRN abstracts, DOI/journal pages, arXiv).

**Candidate verdicts** (latest first, tracked in [the process doc](IA/research-frontier-mining.md)):

- **Same Dollar, Different Impact** (Huang/Hu/Song/Xiang, SSRN 6266398) — **REJECTED, no tradable signal.** Shows separate-account (institutional) flows cause essentially zero price impact vs mutual-fund flows (despite comparable demand, same manager/strategy twins). It's a descriptive/asset-pricing result with nothing to capture and proprietary data; also *reduces* the prior on institutional-flow price-pressure trades.
- **VIX-ETP end-of-day hedging** (Bangsgaard & Kokholm, JBF 2025) — **REGISTERED, not advanced (heavy Level-2 required).** Gross EOD SPX-futures signal is real (Sharpe 1.47 naively), but the paper's own backtest shows **one tick of spread turns every naive variant negative (Sharpe -0.56)**; only a cost-threshold + model-forecast variant survives (+1.05%/yr, Sharpe 0.91), needing Bloomberg VIX-ETP AUM/flows + intraday SPX/VIX-futures tick data. Naive reversal dies on costs.
- **HK passive-flow weight-cap rebalancing** (Xu, SSRN 5703304) — **CLOSED, not viable post-friction.** Paper's own backtest: long-short Sharpe 1.10 (frictionless) -> 0.28 after HK stamp duty (0.13% x2 legs) + impact + borrow; concentrated in ~4-5 mega-caps, tiny event count.
