from __future__ import annotations

import io
import json
import unittest

from microcloud_agent.oidc import OIDCClient


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


class OIDCTests(unittest.TestCase):
    def test_discovery_document(self) -> None:
        calls: list[str] = []

        def opener(req, timeout=0):
            calls.append(req.full_url)
            return FakeResponse({"token_endpoint": "https://issuer.example/token"})

        client = OIDCClient(issuer_url="https://issuer.example", opener=opener)
        payload = client.discovery_document()
        self.assertEqual(payload["token_endpoint"], "https://issuer.example/token")
        self.assertTrue(calls[0].endswith("/.well-known/openid-configuration"))

    def test_client_credentials_token(self) -> None:
        calls: list[str] = []

        def opener(req, timeout=0):
            calls.append(req.full_url)
            if req.full_url.endswith("/.well-known/openid-configuration"):
                return FakeResponse({"token_endpoint": "https://issuer.example/token"})
            return FakeResponse({"access_token": "abc", "token_type": "Bearer"})

        client = OIDCClient(
            issuer_url="https://issuer.example",
            client_id="client",
            client_secret="secret",
            opener=opener,
        )
        payload = client.client_credentials_token()
        self.assertEqual(payload["access_token"], "abc")
        self.assertEqual(calls[-1], "https://issuer.example/token")
