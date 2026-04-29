from __future__ import annotations

import shutil
import subprocess

from .models import CommandResult, CommandSpec
from .policy import require_approval


class CommandRunner:
    def which(self, program: str) -> str | None:
        return shutil.which(program)

    def available(self, program: str) -> bool:
        return self.which(program) is not None

    def run(self, spec: CommandSpec) -> CommandResult:
        if spec.mutating:
            require_approval()

        binary = spec.argv[0]
        if not self.available(binary):
            return CommandResult(
                tool=spec.tool,
                action=spec.action,
                argv=spec.argv,
                exit_code=127,
                stdout="",
                stderr=f"Required binary '{binary}' is not installed or not on PATH.",
                status="unavailable",
            )

        completed = subprocess.run(
            spec.argv,
            cwd=spec.cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        return CommandResult(
            tool=spec.tool,
            action=spec.action,
            argv=spec.argv,
            exit_code=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
            status="ok" if completed.returncode == 0 else "error",
        )

