from __future__ import annotations

import os
import unittest

from microcloud_agent.policy import APPROVAL_ENV_VAR, approval_granted, require_approval


class PolicyTests(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop(APPROVAL_ENV_VAR, None)

    def test_approval_denied_by_default(self) -> None:
        self.assertFalse(approval_granted())
        with self.assertRaises(PermissionError):
            require_approval()

    def test_approval_enabled_with_token(self) -> None:
        os.environ[APPROVAL_ENV_VAR] = "approved"
        self.assertTrue(approval_granted())
        require_approval()

