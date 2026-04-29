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


def github_bin() -> str:
    return binary_env("GITHUB_BIN", "gh")


def vscode_bin() -> str:
    return binary_env("VSCODE_BIN", "code")


def docker_bin() -> str:
    return binary_env("DOCKER_BIN", "docker")


def snap_bin() -> str:
    return binary_env("SNAP_BIN", "snap")


def playwright_bin() -> str:
    return binary_env("PLAYWRIGHT_BIN", "playwright")


def canvas_bin() -> str:
    return binary_env("CANVAS_BIN", "canvas")


def agentkernel_dependency_spec() -> str:
    return env("AGENTKERNEL_DEPENDENCY_SPEC", "agentkernel[api]>=0.3.3")


def agentkernel_agent_name() -> str:
    return env("AGENTKERNEL_AGENT_NAME", "microcloud-operator")


def agentkernel_agent_description() -> str:
    return env(
        "AGENTKERNEL_AGENT_DESCRIPTION",
        (
            "Canonical MicroCloud operator agent. Supports `health`, `workflows`, "
            "`plan <workflow> [environment]`, `run <workflow> [environment]`, "
            "and free-form chat for capability discovery."
        ),
    )


def agentkernel_default_environment() -> str:
    return env("AGENTKERNEL_DEFAULT_ENVIRONMENT", "lab")


def agentkernel_default_inventory() -> str:
    return env("AGENTKERNEL_DEFAULT_INVENTORY", "ansible/inventories/lab/hosts.ini")


def agentkernel_default_terraform_dir() -> str:
    return env("AGENTKERNEL_DEFAULT_TERRAFORM_DIR", "terraform/environments/lab")


def mattermost_webhook_url() -> str:
    return env("MATTERMOST_WEBHOOK_URL")


def mattermost_default_channel() -> str:
    return env("MATTERMOST_CHANNEL")


def mattermost_username() -> str:
    return env("MATTERMOST_USERNAME", "canonical-microcloud-agent")


def openapi_base_url() -> str:
    return env("OPENAPI_BASE_URL")


def openapi_bearer_token() -> str:
    return env("OPENAPI_BEARER_TOKEN")


def openapi_timeout_seconds() -> float:
    raw = env("OPENAPI_TIMEOUT_SECONDS", "15")
    try:
        return float(raw)
    except ValueError:
        return 15.0


def oidc_issuer_url() -> str:
    return env("OIDC_ISSUER_URL")


def oauth2_client_id() -> str:
    return env("OAUTH2_CLIENT_ID")


def oauth2_client_secret() -> str:
    return env("OAUTH2_CLIENT_SECRET")


def oauth2_scope() -> str:
    return env("OAUTH2_SCOPE")


def microcloud_ssh_target() -> str:
    return env("MICROCLOUD_SSH_TARGET")


def lxc_ssh_target() -> str:
    return env("LXC_SSH_TARGET", microcloud_ssh_target())


def maybe_remote(argv: list[str], ssh_target: str) -> list[str]:
    if not ssh_target:
        return argv
    return [*remote_exec_prefix(), ssh_target, shlex.join(argv)]
