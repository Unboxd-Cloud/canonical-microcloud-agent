from __future__ import annotations

from dataclasses import dataclass

from .config import (
    ansible_bin,
    ansible_inventory_bin,
    ansible_playbook_bin,
    lxc_bin,
    lxc_ssh_target,
    maybe_remote,
    microcloud_bin,
    microcloud_ssh_target,
    terraform_bin,
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
            maybe_remote([microcloud_bin(), "init"], microcloud_ssh_target()),
            mutating=True,
        )

    def add_node(self, name: str) -> CommandSpec:
        return CommandSpec(
            self.name,
            "add_node",
            maybe_remote([microcloud_bin(), "add", name], microcloud_ssh_target()),
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
