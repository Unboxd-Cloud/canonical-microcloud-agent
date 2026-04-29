from __future__ import annotations

import json
import unittest

from microcloud_agent.openapi_client import OpenAPIClient


class FakeResponse:
    def __init__(self, payload: object, status: int = 200) -> None:
        self.payload = json.dumps(payload).encode("utf-8")
        self.status = status

    def read(self) -> bytes:
        return self.payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class OpenAPIClientTests(unittest.TestCase):
    def test_request_uses_base_url_and_query(self) -> None:
        calls: list[str] = []

        def opener(req, timeout=0):
            calls.append(req.full_url)
            return FakeResponse({"ok": True})

        client = OpenAPIClient(base_url="https://api.example", opener=opener)
        payload = client.request("GET", "/health", query={"env": "lab"})
        self.assertTrue(payload["body"]["ok"])
        self.assertEqual(calls[0], "https://api.example/health?env=lab")
