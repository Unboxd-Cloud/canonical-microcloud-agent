from __future__ import annotations

import os


APPROVAL_ENV_VAR = "MICROCLOUD_AGENT_APPROVAL"
APPROVAL_VALUE = "approved"


def approval_granted() -> bool:
    return os.environ.get(APPROVAL_ENV_VAR) == APPROVAL_VALUE


def require_approval() -> None:
    if not approval_granted():
        raise PermissionError(
            f"Mutating action blocked. Set {APPROVAL_ENV_VAR}={APPROVAL_VALUE} to continue."
        )

