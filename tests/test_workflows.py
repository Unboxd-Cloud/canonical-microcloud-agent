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
        os.environ.pop("PRIVILEGE_EXEC_PREFIX", None)

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

    def test_assess_operator_tooling_plan_contains_expected_steps(self) -> None:
        registry = WorkflowRegistry()
        plan = registry.plan("assess_operator_tooling", Context(environment="lab"))
        self.assertEqual(
            [step.name for step in plan],
            [
                "github_auth_status",
                "vscode_version",
                "ssh_version",
                "docker_version",
                "snap_version",
                "vpn_status",
                "dns_status",
                "dig_version",
                "reverseproxy_validate",
                "computeruse_version",
                "playwright_version",
                "canvas_version",
            ],
        )

    def test_install_microcloud_stack_plan_contains_mutating_steps(self) -> None:
        registry = WorkflowRegistry()
        plan = registry.plan("install_microcloud_stack", Context(environment="lab"))
        self.assertEqual(
            [step.name for step in plan],
            [
                "install_lxd",
                "install_microceph",
                "install_microovn",
                "install_microcloud",
                "hold_microcloud_stack",
            ],
        )
        self.assertTrue(all(step.spec.mutating for step in plan))

    def test_configure_single_node_contains_bootstrap(self) -> None:
        registry = WorkflowRegistry()
        plan = registry.plan("configure_single_node", Context(environment="lab"))
        self.assertEqual(
            [step.name for step in plan],
            ["inventory", "preflight", "microcloud_bootstrap", "cluster_status"],
        )
        self.assertTrue(plan[2].spec.mutating)

    def test_configure_multi_node_requires_host(self) -> None:
        registry = WorkflowRegistry()
        with self.assertRaises(ValueError):
            registry.plan("configure_multi_node", Context(environment="lab"))

    def test_configure_multi_node_uses_host(self) -> None:
        registry = WorkflowRegistry()
        plan = registry.plan("configure_multi_node", Context(environment="lab", host="node-2"))
        self.assertEqual(
            [step.name for step in plan],
            ["inventory", "cluster_status", "microcloud_add_node", "instance_list"],
        )
        self.assertEqual(plan[2].spec.argv[-1], "node-2")

    def test_docker_prune_everything_contains_mutating_prune(self) -> None:
        registry = WorkflowRegistry()
        plan = registry.plan("docker_prune_everything", Context(environment="lab"))
        self.assertEqual([step.name for step in plan], ["docker_info", "docker_prune_everything"])
        self.assertFalse(plan[0].spec.mutating)
        self.assertTrue(plan[1].spec.mutating)
