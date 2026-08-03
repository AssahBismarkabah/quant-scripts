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
| [IVAMR](strategies/ivamr/IVAMR.md) | Intraday Value Area Momentum & Mean Reversion | Ready for Backtesting |
| [SPX GEX](strategies/spx-gex/SPX_GEX.md) | Intraday Bias / Regime Filter | Rejected at Level 1 (friction gate) |
| [Funding Basis](strategies/funding-basis/FUNDING_BASIS.md) | Relative Value / Funding Carry | Rejected Under Current Assumptions |
| [Index Rebalancing](strategies/index-rebalancing/INDEX_REBALANCING.md) | Event-Driven Mean Reversion | Pre-Backtest (Level 1 spec approved) |

## Documentation

- [Documentation Index](docs/README.md)
