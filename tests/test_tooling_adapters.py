from __future__ import annotations

import os
import unittest

from microcloud_agent.adapters import (
    CanvasAdapter,
    ComputerUseAdapter,
    DNSAdapter,
    DockerAdapter,
    GitHubAdapter,
    PlaywrightAdapter,
    ReverseProxyAdapter,
    SSHAdapter,
    SnapAdapter,
    VPNAdapter,
    VSCodeAdapter,
)


class ToolingAdapterTests(unittest.TestCase):
    def tearDown(self) -> None:
        for name in ("PRIVILEGE_EXEC_PREFIX", "REVERSEPROXY_CONFIG_PATH"):
            os.environ.pop(name, None)

    def test_github_adapter_uses_gh(self) -> None:
        spec = GitHubAdapter().auth_status()
        self.assertEqual(spec.argv[:3], ["gh", "auth", "status"])

    def test_vscode_adapter_uses_code(self) -> None:
        spec = VSCodeAdapter().version()
        self.assertEqual(spec.argv, ["code", "--version"])

    def test_docker_adapter_uses_docker(self) -> None:
        spec = DockerAdapter().info()
        self.assertEqual(spec.argv, ["docker", "info"])

    def test_snap_adapter_uses_snap(self) -> None:
        spec = SnapAdapter().list()
        self.assertEqual(spec.argv, ["snap", "list"])

    def test_snap_adapter_can_install_microcloud_stack(self) -> None:
        specs = SnapAdapter().install_microcloud_stack()
        self.assertEqual(
            [spec.action for spec in specs],
            [
                "install_lxd",
                "install_microceph",
                "install_microovn",
                "install_microcloud",
                "hold_microcloud_stack",
            ],
        )
        self.assertTrue(all(spec.mutating for spec in specs))
        self.assertEqual(specs[0].argv, ["snap", "install", "lxd", "--cohort=+"])
        self.assertEqual(
            specs[-1].argv,
            ["snap", "refresh", "lxd", "microceph", "microovn", "microcloud", "--hold"],
        )

    def test_privilege_prefix_applies_to_mutating_commands(self) -> None:
        os.environ["PRIVILEGE_EXEC_PREFIX"] = "sudo"
        spec = DockerAdapter().prune_everything()
        self.assertEqual(spec.argv[:2], ["sudo", "docker"])

    def test_playwright_adapter_uses_playwright(self) -> None:
        spec = PlaywrightAdapter().version()
        self.assertEqual(spec.argv, ["playwright", "--version"])

    def test_canvas_adapter_uses_canvas(self) -> None:
        spec = CanvasAdapter().version()
        self.assertEqual(spec.argv, ["canvas", "--version"])

    def test_ssh_adapter_uses_ssh(self) -> None:
        spec = SSHAdapter().version()
        self.assertEqual(spec.argv, ["ssh", "-V"])

    def test_vpn_adapter_uses_tailscale_status(self) -> None:
        spec = VPNAdapter().status()
        self.assertEqual(spec.argv, ["tailscale", "status"])

    def test_dns_adapter_uses_resolvectl_and_dig(self) -> None:
        status = DNSAdapter().status()
        version = DNSAdapter().dig_version()
        self.assertEqual(status.argv, ["resolvectl", "status"])
        self.assertEqual(version.argv, ["dig", "-v"])

    def test_reverse_proxy_adapter_uses_nginx_config(self) -> None:
        os.environ["REVERSEPROXY_CONFIG_PATH"] = "/tmp/nginx.conf"
        spec = ReverseProxyAdapter().validate()
        self.assertEqual(spec.argv, ["nginx", "-t", "-c", "/tmp/nginx.conf"])

    def test_computeruse_adapter_uses_binary(self) -> None:
        spec = ComputerUseAdapter().version()
        self.assertEqual(spec.argv, ["computer-use", "--version"])
