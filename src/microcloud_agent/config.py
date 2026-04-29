from __future__ import annotations

import os
import shlex


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def remote_exec_prefix() -> list[str]:
    raw = env("REMOTE_EXEC_PREFIX", "ssh")
    return shlex.split(raw)


def binary_env(name: str, default: str) -> str:
    return env(name, default)


def microcloud_bin() -> str:
    return binary_env("MICROCLOUD_BIN", "microcloud")


def lxc_bin() -> str:
    return binary_env("LXC_BIN", "lxc")


def ansible_bin() -> str:
    return binary_env("ANSIBLE_BIN", "ansible")


def ansible_inventory_bin() -> str:
    return binary_env("ANSIBLE_INVENTORY_BIN", "ansible-inventory")


def ansible_playbook_bin() -> str:
    return binary_env("ANSIBLE_PLAYBOOK_BIN", "ansible-playbook")


def terraform_bin() -> str:
    return binary_env("TERRAFORM_BIN", "terraform")


def microcloud_ssh_target() -> str:
    return env("MICROCLOUD_SSH_TARGET")


def lxc_ssh_target() -> str:
    return env("LXC_SSH_TARGET", microcloud_ssh_target())


def maybe_remote(argv: list[str], ssh_target: str) -> list[str]:
    if not ssh_target:
        return argv
    return [*remote_exec_prefix(), ssh_target, shlex.join(argv)]
