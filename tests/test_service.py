from __future__ import annotations

import unittest

from microcloud_agent.adapters import Context
from microcloud_agent.service import AgentService


class StubNotifier:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str | None]] = []

    def send(self, message: str, channel: str | None = None) -> dict:
        self.messages.append((message, channel))
        return {"status_code": 200, "body": "ok"}


class StubOIDCClient:
    def discovery_document(self) -> dict:
        return {"issuer": "https://issuer.example", "token_endpoint": "https://issuer.example/token"}

    def client_credentials_token(self) -> dict:
        return {"access_token": "abc", "token_type": "Bearer"}

    def configured(self) -> bool:
        return True


class StubOpenAPIClient:
    def request(self, method: str, path: str, query=None, headers=None, json_body=None) -> dict:
        return {"status_code": 200, "body": {"method": method, "path": path}}

    def configured(self) -> bool:
        return True


class ServiceTests(unittest.TestCase):
    def test_notify_workflow_uses_notifier(self) -> None:
        notifier = StubNotifier()
        service = AgentService(notifier=notifier)
        payload = service.plan("assess_health", Context(environment="lab"))
        result = service.notify_workflow(payload, channel="platform")
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(notifier.messages[0][1], "platform")
        self.assertIn("MicroCloud plan `assess_health`", notifier.messages[0][0])

    def test_oidc_and_openapi_methods_delegate(self) -> None:
        service = AgentService(
            notifier=StubNotifier(),
            oidc_client=StubOIDCClient(),
            openapi_client=StubOpenAPIClient(),
        )
        self.assertEqual(service.oidc_discovery()["issuer"], "https://issuer.example")
        self.assertEqual(service.oauth2_client_credentials()["access_token"], "abc")
        self.assertEqual(service.openapi_request("GET", "/health")["body"]["path"], "/health")
