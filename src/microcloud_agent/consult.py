from __future__ import annotations

import json
import socket
import subprocess
from dataclasses import asdict, dataclass, field

from .memory import AgentMemory


def _run(argv: list[str]) -> str:
    try:
        completed = subprocess.run(argv, text=True, capture_output=True, check=False)
    except OSError:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


@dataclass
class SetupProposal:
    goal: str
    hostname: str
    topology: str
    detected_interfaces: list[str] = field(default_factory=list)
    detected_disks: list[str] = field(default_factory=list)
    installed_snaps: list[str] = field(default_factory=list)
    recommended_workflows: list[str] = field(default_factory=list)
    recommended_settings: dict[str, str] = field(default_factory=dict)
    missing_decisions: list[str] = field(default_factory=list)
    rationale: list[str] = field(default_factory=list)
    memory_hints: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def inspect_host() -> dict[str, object]:
    hostname = _run(["hostname"]) or socket.gethostname()
    ip_output = _run(["sh", "-c", "ip -o -4 addr show scope global 2>/dev/null || true"])
    lsblk_output = _run(["sh", "-c", "lsblk -dn -o NAME,SIZE,TYPE 2>/dev/null || true"])
    snap_output = _run(["sh", "-c", "snap list 2>/dev/null || true"])

    interfaces: list[str] = []
    for line in ip_output.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            name = parts[1]
            if name not in interfaces:
                interfaces.append(name)

    disks: list[str] = []
    for line in lsblk_output.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2] == "disk":
            disks.append(f"{parts[0]} ({parts[1]})")

    installed_snaps: list[str] = []
    for line in snap_output.splitlines()[1:]:
        parts = line.split()
        if parts:
            installed_snaps.append(parts[0])

    return {
        "hostname": hostname,
        "interfaces": interfaces,
        "disks": disks,
        "installed_snaps": installed_snaps,
    }


def build_setup_proposal(goal: str, memory: AgentMemory) -> SetupProposal:
    observed = inspect_host()
    hostname = str(observed["hostname"])
    interfaces = [str(item) for item in observed["interfaces"]]
    disks = [str(item) for item in observed["disks"]]
    installed_snaps = [str(item) for item in observed["installed_snaps"]]

    topology = str(memory.operator_preferences.get("topology", "single-node"))
    if "cluster" in goal.lower() or "multi" in goal.lower():
        topology = "multi-node"

    preferred_interface = str(memory.operator_preferences.get("interface", ""))
    if preferred_interface and preferred_interface not in interfaces:
        preferred_interface = ""
    if not preferred_interface and interfaces:
        preferred_interface = interfaces[0]

    recommended_workflows = ["install_microcloud_stack"]
    recommended_workflows.append("configure_single_node" if topology == "single-node" else "configure_multi_node")

    missing_decisions: list[str] = []
    if not preferred_interface:
        missing_decisions.append("Choose the network interface MicroCloud should use.")
    if topology == "multi-node":
        missing_decisions.append("Confirm the first additional node to join.")
    if disks:
        missing_decisions.append("Confirm whether MicroCeph should use a detected disk now or stay unconfigured.")

    rationale = [
        "I inspected the host first so the recommendation is grounded in the machine in front of us.",
        "I am keeping mutating steps separate so nothing changes until you confirm the configuration.",
    ]
    if "microcloud" in installed_snaps:
        rationale.append("MicroCloud already appears to be installed, so configuration may be the next step rather than installation.")
    else:
        rationale.append("MicroCloud does not appear to be installed yet, so the install workflow is still needed.")

    memory_hints: dict[str, str] = {}
    if memory.operator_preferences:
        memory_hints["operator_preferences"] = json.dumps(memory.operator_preferences, sort_keys=True)
    if memory.recent_goals:
        memory_hints["recent_goal"] = memory.recent_goals[0]

    return SetupProposal(
        goal=goal,
        hostname=hostname,
        topology=topology,
        detected_interfaces=interfaces,
        detected_disks=disks,
        installed_snaps=installed_snaps,
        recommended_workflows=recommended_workflows,
        recommended_settings={"interface": preferred_interface, "topology": topology},
        missing_decisions=missing_decisions,
        rationale=rationale,
        memory_hints=memory_hints,
    )
