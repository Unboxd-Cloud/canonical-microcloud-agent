from __future__ import annotations

import os
import shutil
import unittest

import docker
from testcontainers.core.container import DockerContainer

from microcloud_agent.adapters import Context
from microcloud_agent.service import AgentService


def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        client = docker.from_env()
        client.ping()
    except Exception:
        return False
    return True


@unittest.skipUnless(docker_available(), "docker CLI is required for integration tests")
class TestcontainersIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._old_env)

    def test_remote_lxc_execution_via_container_transport(self) -> None:
        with DockerContainer("alpine:3.20").with_command(["sh", "-lc", "sleep 300"]) as container:
            setup = container.exec(
                [
                    "sh",
                    "-lc",
                    "cat >/usr/local/bin/lxc <<'EOF'\n"
                    "#!/bin/sh\n"
                    "if [ \"$1\" = \"list\" ] && [ \"$2\" = \"--format\" ] && [ \"$3\" = \"json\" ]; then\n"
                    "  printf '[]\\n'\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo unexpected args: \"$@\" >&2\n"
                    "exit 1\n"
                    "EOF\n"
                    "chmod +x /usr/local/bin/lxc"
                ]
            )
            self.assertEqual(setup.exit_code, 0)

            os.environ["REMOTE_EXEC_PREFIX"] = "python3 tests/support/docker_exec.py"
            os.environ["LXC_SSH_TARGET"] = container.get_wrapped_container().name
            os.environ["MICROCLOUD_SSH_TARGET"] = ""

            service = AgentService()
            result = service.runner.run(service.registry.lxc.list_instances())

            self.assertEqual(result.status, "ok")
            self.assertEqual(result.stdout, "[]")

            plan = service.plan("assess_health", Context(environment="lab"))
            self.assertEqual(plan["steps"][3]["name"], "instance_list")
