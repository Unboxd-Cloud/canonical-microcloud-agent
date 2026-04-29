from __future__ import annotations

import unittest

from microcloud_agent.models import CommandSpec
from microcloud_agent.runner import CommandRunner


class RunnerTests(unittest.TestCase):
    def test_missing_binary_is_reported_cleanly(self) -> None:
        runner = CommandRunner()
        result = runner.run(CommandSpec(tool="test", action="missing", argv=["__not_a_real_binary__"]))
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.exit_code, 127)

