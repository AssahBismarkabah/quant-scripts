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

## Documentation

- [Documentation Index](docs/README.md)

## Edge Workflows

- [Funding Basis Workflow](research/funding-basis/Makefile)

## Funding Basis Flow

1. Run `make -C research/funding-basis smoke` to verify Binance connectivity.
2. Run `make -C research/funding-basis dump SYMBOL=BTCUSDT INTERVAL=1h` to save BTCUSDT funding, mark, and spot fixtures.
3. Run `make -C research/funding-basis test` to validate the loaders and normalization logic.
4. Use the saved fixtures to drive the first backtest pass.
