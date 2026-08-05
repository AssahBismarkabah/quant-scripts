# quant-scripts

A collection of quantitative trading strategies, research specs, and executable scaffolds.

## Project Layout

- `docs/` contains the navigation index for the research material.
- `IA/` contains the institutional approach and research specifications.
- `src/` contains executable Python code.
- `tests/` contains verification for the code.

## Strategies

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
