from __future__ import annotations

from dataclasses import asdict, dataclass

from .adapters import (
    AnsibleAdapter,
    CanvasAdapter,
    ComputerUseAdapter,
    Context,
    DNSAdapter,
    DockerAdapter,
    GitHubAdapter,
    LxcAdapter,
    MicrocloudAdapter,
    PlaywrightAdapter,
    ReverseProxyAdapter,
    SSHAdapter,
    SnapAdapter,
    TerraformAdapter,
    VPNAdapter,
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
        self.computeruse = ComputerUseAdapter()
        self.dns = DNSAdapter()
        self.docker = DockerAdapter()
        self.github = GitHubAdapter()
        self.lxc = LxcAdapter()
        self.microcloud = MicrocloudAdapter()
        self.playwright = PlaywrightAdapter()
        self.reverseproxy = ReverseProxyAdapter()
        self.ssh = SSHAdapter()
        self.snap = SnapAdapter()
        self.terraform = TerraformAdapter()
        self.vpn = VPNAdapter()
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
                WorkflowStep("ssh_version", self.ssh.version()),
                WorkflowStep("docker_version", self.docker.version()),
                WorkflowStep("snap_version", self.snap.version()),
                WorkflowStep("vpn_status", self.vpn.status()),
                WorkflowStep("dns_status", self.dns.status()),
                WorkflowStep("dig_version", self.dns.dig_version()),
                WorkflowStep("reverseproxy_validate", self.reverseproxy.validate()),
                WorkflowStep("computeruse_version", self.computeruse.version()),
                WorkflowStep("playwright_version", self.playwright.version()),
                WorkflowStep("canvas_version", self.canvas.version()),
            ]
        if workflow_name == "install_microcloud_stack":
            return [WorkflowStep(spec.action, spec) for spec in self.snap.install_microcloud_stack()]
        if workflow_name == "configure_single_node":
            return [
                WorkflowStep("inventory", self.ansible.inventory(context.inventory)),
                WorkflowStep("preflight", self.ansible.preflight(context.inventory)),
                WorkflowStep("microcloud_bootstrap", self.microcloud.bootstrap()),
                WorkflowStep("cluster_status", self.microcloud.status()),
            ]
        if workflow_name == "configure_multi_node":
            if not context.host:
                raise ValueError("configure_multi_node requires context.host")
            return [
                WorkflowStep("inventory", self.ansible.inventory(context.inventory)),
                WorkflowStep("cluster_status", self.microcloud.status()),
                WorkflowStep("microcloud_add_node", self.microcloud.add_node(context.host)),
                WorkflowStep("instance_list", self.lxc.list_instances()),
            ]
        if workflow_name == "docker_prune_everything":
            return [
                WorkflowStep("docker_info", self.docker.info()),
                WorkflowStep("docker_prune_everything", self.docker.prune_everything()),
            ]
        raise KeyError(f"Unknown workflow '{workflow_name}'.")
