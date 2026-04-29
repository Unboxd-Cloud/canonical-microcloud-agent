from __future__ import annotations

from dataclasses import asdict

from .adapters import Context
from .config import (
    ansible_bin,
    ansible_inventory_bin,
    ansible_playbook_bin,
    lxc_bin,
    lxc_ssh_target,
    microcloud_bin,
    microcloud_ssh_target,
    remote_exec_prefix,
    terraform_bin,
)
from .policy import approval_granted
from .runner import CommandRunner
from .workflows import WorkflowRegistry


class AgentService:
    def __init__(self) -> None:
        self.runner = CommandRunner()
        self.registry = WorkflowRegistry()

    def health(self) -> dict:
        return {
            "approval_granted": approval_granted(),
            "config": {
                "microcloud_bin": microcloud_bin(),
                "microcloud_ssh_target": microcloud_ssh_target(),
                "remote_exec_prefix": remote_exec_prefix(),
                "lxc_bin": lxc_bin(),
                "lxc_ssh_target": lxc_ssh_target(),
                "ansible_bin": ansible_bin(),
                "ansible_inventory_bin": ansible_inventory_bin(),
                "ansible_playbook_bin": ansible_playbook_bin(),
                "terraform_bin": terraform_bin(),
            },
            "tools": {
                "microcloud": self.runner.available(remote_exec_prefix()[0] if microcloud_ssh_target() else microcloud_bin()),
                "lxc": self.runner.available(remote_exec_prefix()[0] if lxc_ssh_target() else lxc_bin()),
                "ansible": self.runner.available(ansible_bin()),
                "ansible-inventory": self.runner.available(ansible_inventory_bin()),
                "ansible-playbook": self.runner.available(ansible_playbook_bin()),
                "terraform": self.runner.available(terraform_bin()),
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
