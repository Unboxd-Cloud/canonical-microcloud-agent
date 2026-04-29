from __future__ import annotations

import unittest

from microcloud_agent.mattermost import MattermostNotifier, format_workflow_message


class MattermostTests(unittest.TestCase):
    def test_notifier_reports_unconfigured(self) -> None:
        notifier = MattermostNotifier(webhook_url="")
        self.assertFalse(notifier.configured())
        with self.assertRaises(RuntimeError):
            notifier.send("hello")

    def test_format_plan_message(self) -> None:
        payload = {
            "workflow": "assess_health",
            "context": {"environment": "lab"},
            "steps": [
                {"name": "inventory", "spec": {"argv": ["ansible-inventory", "--list"]}},
            ],
        }
        text = format_workflow_message(payload)
        self.assertIn("MicroCloud plan `assess_health` in `lab`", text)
        self.assertIn("ansible-inventory --list", text)

    def test_format_run_message(self) -> None:
        payload = {
            "workflow": "assess_health",
            "context": {"environment": "lab"},
            "results": [
                {
                    "step": "inventory",
                    "result": {
                        "status": "ok",
                        "tool": "ansible",
                        "action": "inventory",
                        "stderr": "",
                    },
                }
            ],
        }
        text = format_workflow_message(payload)
        self.assertIn("MicroCloud workflow `assess_health` in `lab`", text)
        self.assertIn("inventory", text)

