from __future__ import annotations

import json
import unittest

from microcloud_agent.adapters import Context
from microcloud_agent.agentkernel_bridge import route_prompt
from microcloud_agent.config import agentkernel_default_environment


class StubService:
    def health(self) -> dict:
        return {"status": "ok"}

    def plan(self, workflow: str, context: Context) -> dict:
        return {"mode": "plan", "workflow": workflow, "environment": context.environment}

    def run(self, workflow: str, context: Context) -> dict:
        return {"mode": "run", "workflow": workflow, "environment": context.environment}

    def chat(self, message: str) -> dict:
        return {"message": message, "response": "chat"}


class AgentKernelBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = StubService()

    def test_health_prompt_routes_to_health(self) -> None:
        payload = json.loads(route_prompt(self.service, "health"))
        self.assertEqual(payload["status"], "ok")

    def test_plan_prompt_routes_to_plan(self) -> None:
        payload = json.loads(route_prompt(self.service, "plan assess_health prod"))
        self.assertEqual(payload["mode"], "plan")
        self.assertEqual(payload["workflow"], "assess_health")
        self.assertEqual(payload["environment"], "prod")

    def test_run_prompt_routes_to_run(self) -> None:
        payload = json.loads(route_prompt(self.service, "run upgrade_cluster stage"))
        self.assertEqual(payload["mode"], "run")
        self.assertEqual(payload["workflow"], "upgrade_cluster")
        self.assertEqual(payload["environment"], "stage")

    def test_plan_prompt_uses_configured_defaults(self) -> None:
        payload = json.loads(route_prompt(self.service, "plan assess_health"))
        self.assertEqual(payload["mode"], "plan")
        self.assertEqual(payload["environment"], agentkernel_default_environment())

    def test_chat_prompt_routes_to_chat(self) -> None:
        payload = json.loads(route_prompt(self.service, "what workflows do you support?"))
        self.assertEqual(payload["response"], "chat")


if __name__ == "__main__":
    unittest.main()
