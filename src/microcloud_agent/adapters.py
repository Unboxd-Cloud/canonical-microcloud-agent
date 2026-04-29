from __future__ import annotations

from dataclasses import dataclass

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
    maybe_operator_remote,
    maybe_privileged,
    maybe_remote,
    microcloud_bin,
    microcloud_ssh_target,
    playwright_bin,
    reverseproxy_bin,
    reverseproxy_config_path,
    reverseproxy_mode,
    ssh_bin,
    snap_bin,
    terraform_bin,
    vpn_bin,
    vscode_bin,
)
from .models import CommandSpec


@dataclass
class Context:
    environment: str
    inventory: str = "ansible/inventories/lab/hosts.ini"
    terraform_dir: str = "terraform/environments/lab"
    service: str = ""
    host: str = ""


class MicrocloudAdapter:
    name = "microcloud"

    def status(self) -> CommandSpec:
        return CommandSpec(
            self.name,
            "status",
            maybe_remote([microcloud_bin(), "status"], microcloud_ssh_target()),
        )

    def bootstrap(self) -> CommandSpec:
        return CommandSpec(
            self.name,
            "bootstrap",
            maybe_remote(maybe_privileged([microcloud_bin(), "init"]), microcloud_ssh_target()),
            mutating=True,
        )

    def add_node(self, name: str) -> CommandSpec:
        return CommandSpec(
            self.name,
            "add_node",
            maybe_remote(maybe_privileged([microcloud_bin(), "add", name]), microcloud_ssh_target()),
            mutating=True,
        )


class LxcAdapter:
    name = "lxc"

    def list_instances(self) -> CommandSpec:
        return CommandSpec(
            self.name,
            "list_instances",
            maybe_remote([lxc_bin(), "list", "--format", "json"], lxc_ssh_target()),
        )

    def info(self, target: str) -> CommandSpec:
        return CommandSpec(
            self.name,
            "info",
            maybe_remote([lxc_bin(), "info", target], lxc_ssh_target()),
        )


class AnsibleAdapter:
    name = "ansible"

    def inventory(self, inventory_path: str) -> CommandSpec:
        return CommandSpec(
            self.name,
            "inventory",
            [ansible_inventory_bin(), "-i", inventory_path, "--list"],
        )

    def gather_facts(self, inventory_path: str) -> CommandSpec:
        return CommandSpec(
            self.name,
            "gather_facts",
            [ansible_bin(), "all", "-m", "setup", "-i", inventory_path],
        )

    def preflight(self, inventory_path: str) -> CommandSpec:
        return CommandSpec(
            self.name,
            "preflight",
            [ansible_playbook_bin(), "-i", inventory_path, "ansible/site.yml"],
        )


class TerraformAdapter:
    name = "terraform"

    def validate(self, terraform_dir: str) -> CommandSpec:
        return CommandSpec(
            self.name,
            "validate",
            [terraform_bin(), "-chdir=" + terraform_dir, "validate"],
        )

    def plan(self, terraform_dir: str) -> CommandSpec:
        return CommandSpec(
            self.name,
            "plan",
            [terraform_bin(), "-chdir=" + terraform_dir, "plan", "-input=false"],
        )

    def apply(self, terraform_dir: str) -> CommandSpec:
        return CommandSpec(
            self.name,
            "apply",
            [terraform_bin(), "-chdir=" + terraform_dir, "apply", "-auto-approve"],
            mutating=True,
        )


class GitHubAdapter:
    name = "github"

    def auth_status(self) -> CommandSpec:
        return CommandSpec(self.name, "auth_status", [github_bin(), "auth", "status"])

    def repo_view(self) -> CommandSpec:
        return CommandSpec(self.name, "repo_view", [github_bin(), "repo", "view"])


class VSCodeAdapter:
    name = "vscode"

    def version(self) -> CommandSpec:
        return CommandSpec(self.name, "version", [vscode_bin(), "--version"])

    def list_extensions(self) -> CommandSpec:
        return CommandSpec(self.name, "list_extensions", [vscode_bin(), "--list-extensions"])


class DockerAdapter:
    name = "docker"

    def version(self) -> CommandSpec:
        return CommandSpec(self.name, "version", maybe_operator_remote([docker_bin(), "--version"]))

    def info(self) -> CommandSpec:
        return CommandSpec(self.name, "info", maybe_operator_remote([docker_bin(), "info"]))

    def prune_everything(self) -> CommandSpec:
        return CommandSpec(
            self.name,
            "prune_everything",
            maybe_operator_remote(maybe_privileged([docker_bin(), "system", "prune", "-a", "--volumes", "-f"])),
            mutating=True,
        )


class SnapAdapter:
    name = "snap"

    def version(self) -> CommandSpec:
        return CommandSpec(self.name, "version", maybe_operator_remote([snap_bin(), "version"]))

    def list(self) -> CommandSpec:
        return CommandSpec(self.name, "list", maybe_operator_remote([snap_bin(), "list"]))

    def install_microcloud_stack(self) -> list[CommandSpec]:
        return [
            CommandSpec(
                self.name,
                "install_lxd",
                maybe_operator_remote(maybe_privileged([snap_bin(), "install", "lxd", "--cohort=+"])),
                mutating=True,
            ),
            CommandSpec(
                self.name,
                "install_microceph",
                maybe_operator_remote(maybe_privileged([snap_bin(), "install", "microceph", "--cohort=+"])),
                mutating=True,
            ),
            CommandSpec(
                self.name,
                "install_microovn",
                maybe_operator_remote(maybe_privileged([snap_bin(), "install", "microovn", "--cohort=+"])),
                mutating=True,
            ),
            CommandSpec(
                self.name,
                "install_microcloud",
                maybe_operator_remote(maybe_privileged([snap_bin(), "install", "microcloud", "--cohort=+"])),
                mutating=True,
            ),
            CommandSpec(
                self.name,
                "hold_microcloud_stack",
                maybe_operator_remote(
                    maybe_privileged(
                        [snap_bin(), "refresh", "lxd", "microceph", "microovn", "microcloud", "--hold"]
                    )
                ),
                mutating=True,
            ),
        ]


class SSHAdapter:
    name = "ssh"

    def version(self) -> CommandSpec:
        return CommandSpec(self.name, "version", [ssh_bin(), "-V"])


class ComputerUseAdapter:
    name = "computeruse"

    def version(self) -> CommandSpec:
        return CommandSpec(self.name, "version", maybe_operator_remote([computeruse_bin(), "--version"]))


class VPNAdapter:
    name = "vpn"

    def status(self) -> CommandSpec:
        return CommandSpec(self.name, "status", maybe_operator_remote([vpn_bin(), "status"]))


class DNSAdapter:
    name = "dns"

    def status(self) -> CommandSpec:
        return CommandSpec(self.name, "status", maybe_operator_remote([dns_bin(), "status"]))

    def dig_version(self) -> CommandSpec:
        return CommandSpec(self.name, "dig_version", maybe_operator_remote([dig_bin(), "-v"]))


class ReverseProxyAdapter:
    name = "reverseproxy"

    def validate(self) -> CommandSpec:
        if reverseproxy_mode() == "caddy":
            return CommandSpec(
                self.name,
                "validate",
                maybe_operator_remote([caddy_bin(), "validate", "--config", caddyfile_path()]),
                metadata={"mode": "caddy"},
            )
        return CommandSpec(
            self.name,
            "validate",
            maybe_operator_remote(maybe_privileged([reverseproxy_bin(), "-t", "-c", reverseproxy_config_path()])),
            metadata={"mode": "nginx"},
        )


class PlaywrightAdapter:
    name = "playwright"

    def version(self) -> CommandSpec:
        return CommandSpec(self.name, "version", [playwright_bin(), "--version"])


class CanvasAdapter:
    name = "canvas"

    def version(self) -> CommandSpec:
        return CommandSpec(self.name, "version", [canvas_bin(), "--version"])
