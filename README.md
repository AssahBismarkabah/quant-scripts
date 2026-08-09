# quant-scripts

A collection of quantitative trading strategies, research specs, and executable scaffolds.

## Tested Strategies

| Strategy | Type | Status |
|---|---|--|
| [NQ VWAP-Pullback / "Drift VWOP Pullback"](strategies/nq-vwap-pullback/NQ_VWAP_PULLBACK.md) | Execution microstructure (VWAP-anchored-at-open intraday pullback) | DISCONFIRMED (2026-08-08): pre-registered probe on Databento NQ; ~61% win rate reproduces but net-negative IS and OOS (all 5 gates failed) |
| [10b5-1 Adoption Timing / "Cooling-Off Watch"](strategies/10b5-1-timing/10B5-1_TIMING.md) | Data asymmetry (real-time EDGAR 10b5-1 adoption) + forced flow | DISCONFIRMED (2026-08-07): bounded probe fails sparsity gate — 3 events / 2 distinct issuers (TKO, SAM) vs required >=30 in a 993-filing harvest; intrinsic sparsity (issuers use program-authorization or lagged tables, not real-time adoption 8-Ks), family closed |
| [Buyback Timing / "Buyback Put"](strategies/buyback-timing/BUYBACK_TIMING.md) | Structural forced-flow / data asymmetry | Bounded study NOT ADVANCED (2026-08-04): 47 events, 20d point positive but insignificant (bootstrap p5<0), drop-best->zero; full multi-year sample pending |
| [Vol Targeting Flow Fade](strategies/vol-targeting/VOL_TARGETING.md) | Flow-Driven / Forced-Deleveraging Fade | Measured-but-marginal / no advance (2026-08-04): on extended 1993-2026 sample (~840 events) bootstrap p5 passes but effect is ~1-2 bps over market drift; v1 (1-day) and v2 (p5 gate on ~80 events) rejected earlier |
| [IVAMR](strategies/ivamr/IVAMR.md) | Intraday Value Area Momentum & Mean Reversion | DISCONFIRMED (2026-08-08): all 5 pre-registered gates failed; net-negative IS & OOS on NQ |
| [Opening-Range / Gap trio (ORB, Gap Fill, Oops)](strategies/opening-range-gap/OPENING_RANGE_GAP.md) | Intraday opening-range breakout / gap-reversion microstrategies | DISCONFIRMED (2026-08-09): ORB + Oops fail all pre-registered gates on NQ; Gap Fill not falsifiable as a trade (no stop/exit in source) and its raw gap-fill rate fails OOS (0.5885 < 0.60) |
| [SPX GEX](strategies/spx-gex/SPX_GEX.md) | Intraday Bias / Regime Filter | Rejected at Level 1 (friction gate); Level-2 upgrade declined (2026-08-04) |
| [Funding Basis](strategies/funding-basis/FUNDING_BASIS.md) | Relative Value / Funding Carry | Rejected Under Current Assumptions |
| [Index Rebalancing](strategies/index-rebalancing/INDEX_REBALANCING.md) | Event-Driven Mean Reversion | Rejected Level 1-2, then CLOSED (2026-08-04): S&P 600 short-additions is a single March-2025 batch; year-breakdown shows 2024 n/s, 2025 +1542 bps, 2026 -786 bps - not persistent |
| [Short Vol / VRP](strategies/vol-risk-premium/VOL_RISK_PREMIUM.md) | Options / Variance Risk Premium (short-vol premium capture) | DISCONFIRMED (2026-08-08): V1 level positive, V2 naive harvest is ruin (+452% / −95% DD, −83% single day), V3 stress-overlay kills the edge (skips +646% premium, keeps −26%) - [V3 design](strategies/vol-risk-premium/V3_TAIL_OVERLAY.md). Candidate closed |

## Documentation

- [Documentation Index](docs/README.md)

## Research Frontier Mining

Automated harvest of the recent quant-finance frontier (arXiv + Crossref + SSRN + Google Scholar) into a ranked, finance-gated, testable shortlist. See [the process doc](IA/research-frontier-mining.md); re-run via [the Makefile](research/frontier-mining/Makefile) (`make harvest`).

- [Ranked papers CSV](research/frontier-mining/outputs/frontier_papers.csv) — scored/ranked candidates; each row carries a `url` link to the paper (SSRN abstracts, DOI/journal pages, arXiv).

**Candidate verdicts** (latest first, tracked in [the process doc](IA/research-frontier-mining.md)):

- **Option Market Making with Hedging-Induced Market Impact** (Aubert/Chevalier/Ly Vath, Applied Mathematical Finance 2026) — **REJECTED, method / out of framework.** A stochastic-control + deep-hedging-style market-making *model* (hedging trades cause impact on the underlying), solved on a synthetic simulator with no real-data empirical result; learned policy just loses less than naive on generated paths. No forced counterparty to front-run, no tradable anomaly — same bin as Deep Hedging.
- **Relief-Gated Relative Rotation (QQQ-DIA)** (Xiong, arXiv 2607.06117, re-surfaced 2026-08-07 re-harvest) — **REJECTED, out of framework.** Two-ETF market-timing rule improving Sharpe vs 100% QQQ (0.87-0.94 vs 0.70-0.89) but trailing QQQ on CAGR in 3 of 4 windows; 354-506%/yr turnover. **Fails the core forced-counterparty pillar** — it's discretionary relative-timing against other allocators, not a structural-flow trade; published preprint + public GitHub (self-crowding); only beats QQQ on risk-adjusted grounds, not return.
- **Remaining 9.0/8.0 tier binned (one pass)** — the rest of the empirical frontier does not clear the bar: **"The hidden costs of hedge fund activism"** (EJF) — REJECTED, no tradable signal (descriptive liquidity finding, like Same Dollar). **"How Likely and How Deep?"** crash bounds (arXiv) — REJECTED, method. **"The Trillion Dollar Bonus"** (ManSci) — REJECTED, descriptive compensation. **"Deep Hedging Under Market Frictions"** (JRFM) — REJECTED, DRL method. 8.0s (momentum-crash/value studies, predatory index rebalancing) — REJECTED/closed (proprietary data, known-anomaly/closed-index-rebalancing buckets, not recent). All DeFi/ML/theory arXiv 9.0s — out of scope. **No untriaged empirical frontier candidate remains.**
- **AI and Exchange Rate Predictability** (Izadyar, arXiv 2608.00761) — **REGISTERED, not advanced.** LLM (ChatGPT/DeepSeek) classifies macro data releases into a cross-sectional FX strength signal (long top-2 / short bottom-2 G-10, monthly); gross Sharpe ~0.58-0.60 (36-48mo) with sig alpha over Carry/Momentum/Value. Best friction + free-data profile of any candidate so far, but weak on forced-counterparty and heavy decay/crowding risk — sample ends at GPT-4o's knowledge cutoff (Oct 2023), so the whole AI-era window is untested OOS. Only worth revisiting as a costly, current-LLM live replication.
- **Same Dollar, Different Impact** (Huang/Hu/Song/Xiang, SSRN 6266398) — **REJECTED, no tradable signal.** Shows separate-account (institutional) flows cause essentially zero price impact vs mutual-fund flows (despite comparable demand, same manager/strategy twins). It's a descriptive/asset-pricing result with nothing to capture and proprietary data; also *reduces* the prior on institutional-flow price-pressure trades.
- **VIX-ETP end-of-day hedging** (Bangsgaard & Kokholm, JBF 2025) — **REGISTERED, not advanced (heavy Level-2 required).** Gross EOD SPX-futures signal is real (Sharpe 1.47 naively), but the paper's own backtest shows **one tick of spread turns every naive variant negative (Sharpe -0.56)**; only a cost-threshold + model-forecast variant survives (+1.05%/yr, Sharpe 0.91), needing Bloomberg VIX-ETP AUM/flows + intraday SPX/VIX-futures tick data. Naive reversal dies on costs.
- **HK passive-flow weight-cap rebalancing** (Xu, SSRN 5703304) — **CLOSED, not viable post-friction.** Paper's own backtest: long-short Sharpe 1.10 (frictionless) -> 0.28 after HK stamp duty (0.13% x2 legs) + impact + borrow; concentrated in ~4-5 mega-caps, tiny event count.
