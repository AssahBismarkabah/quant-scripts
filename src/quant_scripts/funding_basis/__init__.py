from __future__ import annotations

from .cli import build_parser, main
from .config import BinanceCredentials, BinanceSettings
from .client import BinanceRestClient
from .binance import BinanceFileMarketDataSource, BinanceRecordType
from .backtest import FundingBasisBacktest, FundingBasisTradeResult
from .ingest import BinanceIngestionService
from .normalize import (
    funding_rate_rows_to_dataset,
    mark_price_klines_to_dataset,
    spot_klines_to_dataset,
)
from .models import (
    FundingEvent,
    FundingBasisTrade,
    MarginAssumptions,
    MarginMode,
    MarketSnapshot,
    NormalizedDataset,
    TradeDecision,
    WickStressResult,
    build_funding_event,
    validate_trade_window,
    wick_stress,
)
from .sources import FileMarketDataSource, MarketDataSource, SourceFormat
from .validation import DatasetValidationReport, validate_dataset

__all__ = [
    "DatasetValidationReport",
    "BinanceFileMarketDataSource",
    "BinanceRecordType",
    "BinanceCredentials",
    "BinanceSettings",
    "BinanceRestClient",
    "build_parser",
    "main",
    "BinanceIngestionService",
    "FileMarketDataSource",
    "FundingBasisBacktest",
    "FundingBasisTrade",
    "FundingBasisTradeResult",
    "FundingEvent",
    "MarginAssumptions",
    "MarginMode",
    "MarketDataSource",
    "MarketSnapshot",
    "NormalizedDataset",
    "SourceFormat",
    "TradeDecision",
    "WickStressResult",
    "build_funding_event",
    "funding_rate_rows_to_dataset",
    "mark_price_klines_to_dataset",
    "validate_dataset",
    "validate_trade_window",
    "spot_klines_to_dataset",
    "wick_stress",
]
