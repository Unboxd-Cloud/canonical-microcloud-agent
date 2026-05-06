from __future__ import annotations

import unittest
from unittest.mock import patch

from microcloud_agent.consult import build_setup_proposal
from microcloud_agent.memory import AgentMemory


class ConsultTests(unittest.TestCase):
    @patch("microcloud_agent.consult.inspect_host")
    def test_build_setup_proposal_uses_host_context_and_memory(self, inspect_host) -> None:
        inspect_host.return_value = {
            "hostname": "edge-01",
            "interfaces": ["ens3"],
            "disks": ["sda (100G)"],
            "installed_snaps": [],
        }
        memory = AgentMemory(
            operator_preferences={"topology": "single-node", "interface": "ens3"},
            recent_goals=["install microcloud"],
        )

        proposal = build_setup_proposal("install microcloud", memory)

        self.assertEqual(proposal.hostname, "edge-01")
        self.assertEqual(proposal.recommended_settings["interface"], "ens3")
        self.assertIn("install_microcloud_stack", proposal.recommended_workflows)
        self.assertIn("configure_single_node", proposal.recommended_workflows)
        self.assertTrue(proposal.missing_decisions)
