from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import BinanceCredentials, BinanceSettings


@dataclass(frozen=True)
class BinanceRestClient:
    credentials: BinanceCredentials | None = None
    settings: BinanceSettings = BinanceSettings()

    def get_server_time(self) -> dict[str, Any]:
        return self._request("GET", f"{self.settings.futures_base_url}/fapi/v1/time")

    def get_futures_exchange_info(self) -> dict[str, Any]:
        return self._request("GET", f"{self.settings.futures_base_url}/fapi/v1/exchangeInfo")

    def get_futures_funding_rate_history(
        self,
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"symbol": symbol}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        if limit is not None:
            params["limit"] = limit
        return self._request_list("GET", f"{self.settings.futures_base_url}/fapi/v1/fundingRate", params=params)

    def get_futures_mark_price_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        params: dict[str, Any] = {"symbol": symbol, "interval": interval}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        if limit is not None:
            params["limit"] = limit
        return self._request_list("GET", f"{self.settings.futures_base_url}/fapi/v1/markPriceKlines", params=params)

    def get_spot_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        params: dict[str, Any] = {"symbol": symbol, "interval": interval}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        if limit is not None:
            params["limit"] = limit
        return self._request_list("GET", f"{self.settings.base_url}/api/v3/klines", params=params)

    def get_futures_account(self) -> dict[str, Any]:
        return self._signed_request("GET", f"{self.settings.futures_base_url}/fapi/v2/account")

    def _request(self, method: str, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if params:
            url = f"{url}?{urlencode(params)}"
        request = Request(url=url, method=method)
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def _request_list(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> list[Any]:
        if params:
            url = f"{url}?{urlencode(params)}"
        request = Request(url=url, method=method)
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, list):
                raise TypeError(f"expected list payload from {url}")
            return payload

    def _signed_request(self, method: str, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.credentials is None:
            raise RuntimeError("Binance credentials are required for signed requests")

        payload = dict(params or {})
        payload["timestamp"] = int(time.time() * 1000)
        query = urlencode(payload)
        signature = hmac.new(
            self.credentials.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signed_url = f"{url}?{query}&signature={signature}"
        request = Request(url=signed_url, method=method)
        request.add_header("X-MBX-APIKEY", self.credentials.api_key)
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
