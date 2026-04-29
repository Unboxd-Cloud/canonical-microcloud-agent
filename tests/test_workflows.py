from __future__ import annotations

import os
import unittest

from microcloud_agent.adapters import Context
from microcloud_agent.workflows import WorkflowRegistry


class WorkflowTests(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("MICROCLOUD_SSH_TARGET", None)
        os.environ.pop("LXC_SSH_TARGET", None)
        os.environ.pop("REMOTE_EXEC_PREFIX", None)

    def test_assess_health_plan_contains_expected_steps(self) -> None:
        registry = WorkflowRegistry()
        plan = registry.plan("assess_health", Context(environment="lab"))
        self.assertEqual(
            [step.name for step in plan],
            ["inventory", "gather_facts", "cluster_status", "instance_list", "terraform_validate"],
        )

    def test_bootstrap_cluster_contains_mutating_step(self) -> None:
        registry = WorkflowRegistry()
        plan = registry.plan("bootstrap_cluster", Context(environment="lab"))
        self.assertTrue(plan[-1].spec.mutating)

    def test_microcloud_command_uses_ssh_when_target_is_set(self) -> None:
        os.environ["MICROCLOUD_SSH_TARGET"] = "ubuntu@microcloud-host"
        registry = WorkflowRegistry()
        plan = registry.plan("assess_health", Context(environment="lab"))
        self.assertEqual(plan[2].spec.argv[0], "ssh")

    def test_lxc_command_uses_ssh_when_target_is_set(self) -> None:
        os.environ["LXC_SSH_TARGET"] = "ubuntu@microcloud-host"
        registry = WorkflowRegistry()
        plan = registry.plan("assess_health", Context(environment="lab"))
        self.assertEqual(plan[3].spec.argv[0], "ssh")

    def test_lxc_command_falls_back_to_microcloud_target(self) -> None:
        os.environ["MICROCLOUD_SSH_TARGET"] = "ubuntu@microcloud-host"
        registry = WorkflowRegistry()
        plan = registry.plan("assess_health", Context(environment="lab"))
        self.assertEqual(plan[3].spec.argv[0], "ssh")

    def test_remote_exec_prefix_can_use_tailscale_ssh(self) -> None:
        os.environ["REMOTE_EXEC_PREFIX"] = "tailscale ssh"
        os.environ["MICROCLOUD_SSH_TARGET"] = "ubuntu@microcloud-host"
        registry = WorkflowRegistry()
        plan = registry.plan("assess_health", Context(environment="lab"))
        self.assertEqual(plan[2].spec.argv[:2], ["tailscale", "ssh"])
