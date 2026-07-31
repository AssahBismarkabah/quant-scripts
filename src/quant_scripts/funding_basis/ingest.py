from __future__ import annotations

from dataclasses import dataclass

from .client import BinanceRestClient
from .normalize import (
    funding_rate_rows_to_dataset,
    mark_price_klines_to_dataset,
    spot_klines_to_dataset,
)
from .models import NormalizedDataset


@dataclass(frozen=True)
class BinanceIngestionService:
    client: BinanceRestClient

    def load_funding_history(
        self,
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> NormalizedDataset:
        rows = self.client.get_futures_funding_rate_history(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        return funding_rate_rows_to_dataset(rows=rows, venue="binance", symbol=symbol, source="binance:futures:fundingRate")

    def load_mark_price_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> NormalizedDataset:
        rows = self.client.get_futures_mark_price_klines(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        return mark_price_klines_to_dataset(rows=rows, venue="binance", symbol=symbol, source="binance:futures:markPriceKlines")

    def load_spot_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> NormalizedDataset:
        rows = self.client.get_spot_klines(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        return spot_klines_to_dataset(rows=rows, venue="binance", symbol=symbol, source="binance:spot:klines")

