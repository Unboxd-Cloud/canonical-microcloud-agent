from __future__ import annotations

import unittest

from microcloud_agent.adapters import CanvasAdapter, DockerAdapter, GitHubAdapter, PlaywrightAdapter, SnapAdapter, VSCodeAdapter


class ToolingAdapterTests(unittest.TestCase):
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

    def test_playwright_adapter_uses_playwright(self) -> None:
        spec = PlaywrightAdapter().version()
        self.assertEqual(spec.argv, ["playwright", "--version"])

    def test_canvas_adapter_uses_canvas(self) -> None:
        spec = CanvasAdapter().version()
        self.assertEqual(spec.argv, ["canvas", "--version"])
