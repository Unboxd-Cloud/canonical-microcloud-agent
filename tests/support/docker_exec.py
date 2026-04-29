from __future__ import annotations

import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: docker_exec.py <container_name> <shell_command>", file=sys.stderr)
        return 2

    container_name = sys.argv[1]
    shell_command = sys.argv[2]
    completed = subprocess.run(
        ["docker", "exec", container_name, "sh", "-lc", shell_command],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

