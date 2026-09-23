"""Minimal Dune client for ad-hoc SQL execution (spec step 1 pivot)."""

from __future__ import annotations

import time

import certifi
import requests

from .config import DUNE_API_BASE


class DuneClient:
    def __init__(self, api_key: str, poll_interval: float = 3.0, max_poll_seconds: float = 900.0) -> None:
        self._headers = {"X-Dune-API-Key": api_key}
        self.poll_interval = poll_interval
        self.max_poll_seconds = max_poll_seconds
        self.calls = 0
        self._session = requests.Session()
        self._session.verify = certifi.where()

    def _post(self, path: str, body: dict) -> dict:
        last_exc: Exception | None = None
        for attempt in range(4):
            try:
                self.calls += 1
                response = self._session.post(
                    f"{DUNE_API_BASE}{path}", json=body, headers=self._headers, timeout=60
                )
                if response.status_code == 429 or 500 <= response.status_code < 600:
                    last_exc = RuntimeError(f"Dune HTTP {response.status_code}: {response.text[:200]!r}")
                    time.sleep(2.0 * (2**attempt))
                    continue
                if response.status_code != 200:
                    raise RuntimeError(f"Dune HTTP {response.status_code}: {response.text[:300]!r}")
                return response.json()
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_exc = exc
                time.sleep(2.0 * (2**attempt))
        raise RuntimeError(f"Dune POST {path} failed after retries: {last_exc}")

    def _get(self, path: str) -> dict:
        last_exc: Exception | None = None
        for attempt in range(4):
            try:
                self.calls += 1
                response = self._session.get(
                    f"{DUNE_API_BASE}{path}", headers=self._headers, timeout=60
                )
                if response.status_code == 429 or 500 <= response.status_code < 600:
                    last_exc = RuntimeError(f"Dune HTTP {response.status_code}: {response.text[:200]!r}")
                    time.sleep(2.0 * (2**attempt))
                    continue
                if response.status_code != 200:
                    raise RuntimeError(f"Dune HTTP {response.status_code}: {response.text[:300]!r}")
                return response.json()
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_exc = exc
                time.sleep(2.0 * (2**attempt))
        raise RuntimeError(f"Dune GET {path} failed after retries: {last_exc}")

    def execute_sql(self, sql: str, performance: str = "medium") -> str:
        body = {"sql": sql, "performance": performance}
        result = self._post("/sql/execute", body)
        execution_id = result.get("execution_id")
        if not execution_id:
            raise RuntimeError(f"Dune execute response missing execution_id: {result}")
        return str(execution_id)

    def get_results(self, execution_id: str, state_timeout: bool = True) -> dict:
        """Poll until the execution completes or fails; returns the results payload."""
        deadline = time.monotonic() + self.max_poll_seconds
        while True:
            payload = self._get(f"/execution/{execution_id}/results")
            state = (payload.get("state") or "").upper()
            if "COMPLETED" in state:
                return payload
            if state.endswith(("FAILED", "CANCELED")) or "FAILED" in state:
                raise RuntimeError(f"Dune execution {execution_id} ended in state {state}: {payload.get('error', payload)}")
            if state_timeout and time.monotonic() > deadline:
                raise RuntimeError(f"Dune execution {execution_id} still {state} after {self.max_poll_seconds}s")
            time.sleep(self.poll_interval)
