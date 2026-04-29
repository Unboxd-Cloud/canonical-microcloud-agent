from __future__ import annotations

from dataclasses import asdict

from .adapters import Context
from .chat import build_chat_response, chunk_text
from .config import (
    ansible_bin,
    ansible_inventory_bin,
    ansible_playbook_bin,
    caddy_bin,
    caddyfile_path,
    canvas_bin,
    computeruse_bin,
    dig_bin,
    dns_bin,
    docker_bin,
    github_bin,
    lxc_bin,
    lxc_ssh_target,
    mattermost_default_channel,
    mattermost_username,
    mattermost_webhook_url,
    microcloud_bin,
    microcloud_ssh_target,
    oauth2_client_id,
    oidc_issuer_url,
    openapi_base_url,
    playwright_bin,
    privilege_exec_prefix,
    remote_exec_prefix,
    reverseproxy_mode,
    reverseproxy_bin,
    reverseproxy_config_path,
    ssh_bin,
    snap_bin,
    terraform_bin,
    operator_ssh_target,
    vpn_bin,
    vscode_bin,
)
from .mattermost import MattermostNotifier, format_workflow_message
from .oidc import OIDCClient
from .openapi_client import OpenAPIClient
from .policy import approval_granted
from .runner import CommandRunner
from .workflows import WorkflowRegistry


class AgentService:
    def __init__(
        self,
        notifier: MattermostNotifier | None = None,
        oidc_client: OIDCClient | None = None,
        openapi_client: OpenAPIClient | None = None,
    ) -> None:
        self.runner = CommandRunner()
        self.registry = WorkflowRegistry()
        self.notifier = notifier or MattermostNotifier()
        self.oidc_client = oidc_client or OIDCClient()
        self.openapi_client = openapi_client or OpenAPIClient()

    def health(self) -> dict:
        return {
            "approval_granted": approval_granted(),
            "config": {
                "microcloud_bin": microcloud_bin(),
                "microcloud_ssh_target": microcloud_ssh_target(),
                "operator_ssh_target": operator_ssh_target(),
                "remote_exec_prefix": remote_exec_prefix(),
                "privilege_exec_prefix": privilege_exec_prefix(),
                "lxc_bin": lxc_bin(),
                "lxc_ssh_target": lxc_ssh_target(),
                "ansible_bin": ansible_bin(),
                "ansible_inventory_bin": ansible_inventory_bin(),
                "ansible_playbook_bin": ansible_playbook_bin(),
                "terraform_bin": terraform_bin(),
                "github_bin": github_bin(),
                "vscode_bin": vscode_bin(),
                "docker_bin": docker_bin(),
                "snap_bin": snap_bin(),
                "ssh_bin": ssh_bin(),
                "computeruse_bin": computeruse_bin(),
                "vpn_bin": vpn_bin(),
                "dns_bin": dns_bin(),
                "dig_bin": dig_bin(),
                "reverseproxy_bin": reverseproxy_bin(),
                "reverseproxy_mode": reverseproxy_mode(),
                "reverseproxy_config_path": reverseproxy_config_path(),
                "caddy_bin": caddy_bin(),
                "caddyfile_path": caddyfile_path(),
                "playwright_bin": playwright_bin(),
                "canvas_bin": canvas_bin(),
                "mattermost_webhook_configured": bool(mattermost_webhook_url()),
                "mattermost_channel": mattermost_default_channel(),
                "mattermost_username": mattermost_username(),
                "oidc_issuer_url": oidc_issuer_url(),
                "oauth2_client_id": oauth2_client_id(),
                "openapi_base_url": openapi_base_url(),
            },
            "tools": {
                "microcloud": self.runner.available(remote_exec_prefix()[0] if microcloud_ssh_target() else microcloud_bin()),
                "lxc": self.runner.available(remote_exec_prefix()[0] if lxc_ssh_target() else lxc_bin()),
                "ansible": self.runner.available(ansible_bin()),
                "ansible-inventory": self.runner.available(ansible_inventory_bin()),
                "ansible-playbook": self.runner.available(ansible_playbook_bin()),
                "terraform": self.runner.available(terraform_bin()),
                "github": self.runner.available(github_bin()),
                "vscode": self.runner.available(vscode_bin()),
                "docker": self.runner.available(remote_exec_prefix()[0] if operator_ssh_target() else docker_bin()),
                "snap": self.runner.available(remote_exec_prefix()[0] if operator_ssh_target() else snap_bin()),
                "ssh": self.runner.available(ssh_bin()),
                "computeruse": self.runner.available(remote_exec_prefix()[0] if operator_ssh_target() else computeruse_bin()),
                "vpn": self.runner.available(remote_exec_prefix()[0] if operator_ssh_target() else vpn_bin()),
                "dns": self.runner.available(remote_exec_prefix()[0] if operator_ssh_target() else dns_bin()),
                "dig": self.runner.available(remote_exec_prefix()[0] if operator_ssh_target() else dig_bin()),
                "reverseproxy": self.runner.available(
                    remote_exec_prefix()[0]
                    if operator_ssh_target()
                    else (caddy_bin() if reverseproxy_mode() == "caddy" else reverseproxy_bin())
                ),
                "playwright": self.runner.available(playwright_bin()),
                "canvas": self.runner.available(canvas_bin()),
            },
            "channels": {
                "mattermost": self.notifier.configured(),
                "oidc": self.oidc_client.configured(),
                "openapi": self.openapi_client.configured(),
            },
        }

    def plan(self, workflow_name: str, context: Context) -> dict:
        steps = self.registry.plan(workflow_name, context)
        return {
            "workflow": workflow_name,
            "context": asdict(context),
            "steps": [step.to_dict() for step in steps],
        }

    def run(self, workflow_name: str, context: Context) -> dict:
        steps = self.registry.plan(workflow_name, context)
        results = []
        for step in steps:
            result = self.runner.run(step.spec)
            results.append({"step": step.name, "result": result.to_dict()})
            if result.status != "ok":
                break
        return {
            "workflow": workflow_name,
            "context": asdict(context),
            "results": results,
        }

    def notify(self, message: str, channel: str | None = None) -> dict:
        return self.notifier.send(message, channel=channel)

    def notify_workflow(self, payload: dict, channel: str | None = None) -> dict:
        return self.notify(format_workflow_message(payload), channel=channel)

    def oidc_discovery(self) -> dict:
        return self.oidc_client.discovery_document()

    def oauth2_client_credentials(self) -> dict:
        return self.oidc_client.client_credentials_token()

    def openapi_request(
        self,
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        json_body: object | None = None,
    ) -> dict:
        return self.openapi_client.request(method, path, query=query, headers=headers, json_body=json_body)

    def chat(self, message: str) -> dict:
        workflows = [
            "assess_health",
            "bootstrap_cluster",
            "upgrade_cluster",
            "assess_operator_tooling",
            "install_microcloud_stack",
            "configure_single_node",
            "configure_multi_node",
            "docker_prune_everything",
        ]
        text = build_chat_response(message, self.health(), workflows)
        return {"message": message, "response": text}

    def stream_chat(self, message: str) -> list[str]:
        response = self.chat(message)["response"]
        return list(chunk_text(response))
