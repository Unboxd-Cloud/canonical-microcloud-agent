from __future__ import annotations

from dataclasses import asdict, dataclass

from .adapters import AnsibleAdapter, Context, LxcAdapter, MicrocloudAdapter, TerraformAdapter
from .models import CommandSpec


@dataclass
class WorkflowStep:
    name: str
    spec: CommandSpec

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["spec"] = self.spec.to_dict()
        return payload


class WorkflowRegistry:
    def __init__(self) -> None:
        self.ansible = AnsibleAdapter()
        self.lxc = LxcAdapter()
        self.microcloud = MicrocloudAdapter()
        self.terraform = TerraformAdapter()

    def plan(self, workflow_name: str, context: Context) -> list[WorkflowStep]:
        if workflow_name == "assess_health":
            return [
                WorkflowStep("inventory", self.ansible.inventory(context.inventory)),
                WorkflowStep("gather_facts", self.ansible.gather_facts(context.inventory)),
                WorkflowStep("cluster_status", self.microcloud.status()),
                WorkflowStep("instance_list", self.lxc.list_instances()),
                WorkflowStep("terraform_validate", self.terraform.validate(context.terraform_dir)),
            ]
        if workflow_name == "bootstrap_cluster":
            return [
                WorkflowStep("preflight", self.ansible.preflight(context.inventory)),
                WorkflowStep("terraform_plan", self.terraform.plan(context.terraform_dir)),
                WorkflowStep("microcloud_bootstrap", self.microcloud.bootstrap()),
            ]
        if workflow_name == "upgrade_cluster":
            return [
                WorkflowStep("inventory", self.ansible.inventory(context.inventory)),
                WorkflowStep("cluster_status", self.microcloud.status()),
                WorkflowStep("terraform_plan", self.terraform.plan(context.terraform_dir)),
            ]
        raise KeyError(f"Unknown workflow '{workflow_name}'.")

