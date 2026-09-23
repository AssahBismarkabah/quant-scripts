"""Minimal Helius JSON-RPC client with rate limiting for the launch pull."""

from __future__ import annotations

import json
import time

import certifi
import requests

from .config import MAX_RPS, RPC_URL


class HeliusClient:
    def __init__(self, api_key: str, max_rps: float = MAX_RPS) -> None:
        self.url = RPC_URL.format(api_key=api_key)
        self._min_interval = 1.0 / max_rps
        self._last_call = 0.0
        self.calls = 0
        self._req_id = 0
        self._session = requests.Session()
        self._session.verify = certifi.where()
        self._session.headers.update({"Content-Type": "application/json"})

    def _call(self, method: str, params: list) -> dict:
        # Retry transient failures (connection resets, 429/5xx) with backoff.
        last_exc: Exception | None = None
        for attempt in range(4):
            wait = self._min_interval - (time.monotonic() - self._last_call)
            if wait > 0:
                time.sleep(wait)
            self._last_call = time.monotonic()
            self.calls += 1
            self._req_id += 1
            payload = json.dumps(
                {"jsonrpc": "2.0", "id": self._req_id, "method": method, "params": params}
            )
            try:
                response = self._session.post(self.url, data=payload, timeout=60)
                if response.status_code == 429 or 500 <= response.status_code < 600:
                    last_exc = RuntimeError(
                        f"Helius HTTP {response.status_code}: {response.text[:200]!r}"
                    )
                    time.sleep(2.0 * (2**attempt))
                    continue
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Helius HTTP {response.status_code}: {response.text[:200]!r}"
                    )
                body = response.json()
                if "error" in body:
                    raise RuntimeError(f"RPC error on {method}: {body['error']}")
                return body["result"]
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_exc = exc
                time.sleep(2.0 * (2**attempt))
        raise RuntimeError(f"Helius request failed after retries: {last_exc}")

    def get_signatures_for_address(
        self, address: str, before: str | None = None, until: str | None = None, limit: int = 1000
    ) -> list[dict]:
        options: dict = {"limit": min(limit, 1000)}
        if before:
            options["before"] = before
        if until:
            options["until"] = until
        return self._call("getSignaturesForAddress", [address, options])

    def get_transaction(self, signature: str) -> dict | None:
        return self._call(
            "getTransaction",
            [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}],
        )
