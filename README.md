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
| [Vol Targeting Flow Fade](strategies/vol-targeting/VOL_TARGETING.md) | Flow-Driven / Forced-Deleveraging Fade | Rejected at second pass (2026-08-04): v1 1-day fade fails; v2 co-base cells (60d RV, VIX) fail bootstrap p5 gate in both cells; v1 bar cache found corrupted (35/839 days), v1 rejection confirmed on verified data |
| [IVAMR](strategies/ivamr/IVAMR.md) | Intraday Value Area Momentum & Mean Reversion | Not pursued (2026-08-04): no pre-2023 data for its own OOS protocol; behavioral edge |
| [SPX GEX](strategies/spx-gex/SPX_GEX.md) | Intraday Bias / Regime Filter | Rejected at Level 1 (friction gate); Level-2 upgrade declined (2026-08-04) |
| [Funding Basis](strategies/funding-basis/FUNDING_BASIS.md) | Relative Value / Funding Carry | Rejected Under Current Assumptions |
| [Index Rebalancing](strategies/index-rebalancing/INDEX_REBALANCING.md) | Event-Driven Mean Reversion | Rejected at Level 1-2 (2026-08-04): single-batch effect, fails persistence gate |

## Documentation

- [Documentation Index](docs/README.md)
