from __future__ import annotations

import hashlib
import hmac
import json
import ssl
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import BinanceCredentials, BinanceSettings


@dataclass(frozen=True)
class BinanceRestClient:
    credentials: BinanceCredentials | None = None
    settings: BinanceSettings = BinanceSettings()

    def __post_init__(self) -> None:
        object.__setattr__(self, "_ssl_context", ssl._create_unverified_context() if self.settings.insecure_tls else ssl.create_default_context())
        object.__setattr__(self, "_time_offset_ms", 0)

    def get_server_time(self) -> dict[str, Any]:
        return self._request_with_fallback(
            "GET",
            [f"{base}/fapi/v1/time" for base in self.settings.futures_base_url_candidates],
        )

    def get_futures_exchange_info(self) -> dict[str, Any]:
        return self._request_with_fallback(
            "GET",
            [f"{base}/fapi/v1/exchangeInfo" for base in self.settings.futures_base_url_candidates],
        )

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
        return self._request_list_with_fallback(
            "GET",
            [f"{base}/fapi/v1/fundingRate" for base in self.settings.futures_base_url_candidates],
            params=params,
        )

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
        return self._request_list_with_fallback(
            "GET",
            [f"{base}/fapi/v1/markPriceKlines" for base in self.settings.futures_base_url_candidates],
            params=params,
        )

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
        return self._request_list_with_fallback(
            "GET",
            [f"{base}/api/v3/klines" for base in self.settings.base_url_candidates],
            params=params,
        )

    def get_futures_account(self) -> dict[str, Any]:
        return self._signed_request_with_fallback(
            "GET",
            [f"{base}/fapi/v2/account" for base in self.settings.futures_base_url_candidates],
        )

    def _request(self, method: str, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if params:
            url = f"{url}?{urlencode(params)}"
        request = Request(url=url, method=method)
        try:
            with urlopen(request, timeout=30, context=self._ssl_context) as response:
                body = response.read().decode("utf-8", errors="replace")
                return self._decode_json(body, url)
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} {exc.reason}: {body}") from exc

    def _request_with_fallback(self, method: str, urls: list[str], params: dict[str, Any] | None = None) -> dict[str, Any]:
        last_error: Exception | None = None
        for url in urls:
            try:
                return self._request(method, url, params=params)
            except (URLError, OSError) as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise RuntimeError("no URLs available")

    def _request_list(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> list[Any]:
        if params:
            url = f"{url}?{urlencode(params)}"
        request = Request(url=url, method=method)
        try:
            with urlopen(request, timeout=30, context=self._ssl_context) as response:
                body = response.read().decode("utf-8", errors="replace")
                payload = self._decode_json(body, url)
                if not isinstance(payload, list):
                    raise TypeError(f"expected list payload from {url}")
                return payload
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} {exc.reason}: {body}") from exc

    def _request_list_with_fallback(
        self,
        method: str,
        urls: list[str],
        params: dict[str, Any] | None = None,
    ) -> list[Any]:
        last_error: Exception | None = None
        for url in urls:
            try:
                return self._request_list(method, url, params=params)
            except (URLError, OSError) as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise RuntimeError("no URLs available")

    def _signed_request(self, method: str, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.credentials is None:
            raise RuntimeError("Binance credentials are required for signed requests")

        payload = dict(params or {})
        payload["timestamp"] = int(time.time() * 1000) + int(self._time_offset_ms)
        payload.setdefault("recvWindow", 5000)
        query = urlencode(payload)
        signature = hmac.new(
            self.credentials.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signed_url = f"{url}?{query}&signature={signature}"
        request = Request(url=signed_url, method=method)
        request.add_header("X-MBX-APIKEY", self.credentials.api_key)
        try:
            with urlopen(request, timeout=30, context=self._ssl_context) as response:
                body = response.read().decode("utf-8", errors="replace")
                return self._decode_json(body, url)
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 400 and '"code":-1021' in body:
                self._sync_time()
                return self._signed_request(method, url, params=params)
            raise RuntimeError(f"HTTP {exc.code} {exc.reason}: {body}") from exc

    def _signed_request_with_fallback(self, method: str, urls: list[str]) -> dict[str, Any]:
        last_error: Exception | None = None
        for url in urls:
            try:
                return self._signed_request(method, url)
            except (URLError, OSError) as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise RuntimeError("no URLs available")

    def _sync_time(self) -> None:
        server_time = self.get_server_time().get("serverTime")
        if isinstance(server_time, int):
            object.__setattr__(self, "_time_offset_ms", server_time - int(time.time() * 1000))

    def _decode_json(self, body: str, url: str) -> Any:
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"non-JSON response from {url}: {body}") from exc
