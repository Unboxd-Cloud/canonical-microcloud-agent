from __future__ import annotations

from dataclasses import asdict, dataclass

from .adapters import (
    AnsibleAdapter,
    CanvasAdapter,
    Context,
    DockerAdapter,
    GitHubAdapter,
    LxcAdapter,
    MicrocloudAdapter,
    PlaywrightAdapter,
    SnapAdapter,
    TerraformAdapter,
    VSCodeAdapter,
)
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
        self.canvas = CanvasAdapter()
        self.docker = DockerAdapter()
        self.github = GitHubAdapter()
        self.lxc = LxcAdapter()
        self.microcloud = MicrocloudAdapter()
        self.playwright = PlaywrightAdapter()
        self.snap = SnapAdapter()
        self.terraform = TerraformAdapter()
        self.vscode = VSCodeAdapter()

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
        if workflow_name == "assess_operator_tooling":
            return [
                WorkflowStep("github_auth_status", self.github.auth_status()),
                WorkflowStep("vscode_version", self.vscode.version()),
                WorkflowStep("docker_version", self.docker.version()),
                WorkflowStep("snap_version", self.snap.version()),
                WorkflowStep("playwright_version", self.playwright.version()),
                WorkflowStep("canvas_version", self.canvas.version()),
            ]
        raise KeyError(f"Unknown workflow '{workflow_name}'.")
