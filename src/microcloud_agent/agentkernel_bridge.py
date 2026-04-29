from __future__ import annotations

import json

from .adapters import Context
from .config import (
    agentkernel_default_environment,
    agentkernel_default_inventory,
    agentkernel_default_terraform_dir,
)

SUPPORTED_WORKFLOWS = (
    "assess_health",
    "bootstrap_cluster",
    "upgrade_cluster",
    "assess_operator_tooling",
    "install_microcloud_stack",
    "configure_single_node",
    "configure_multi_node",
    "docker_prune_everything",
)


def route_prompt(service: object, prompt: str) -> str:
    normalized = prompt.strip()
    if not normalized:
        return json.dumps({"error": "empty prompt"}, indent=2)

    words = normalized.split()
    command = words[0].lower()

    if command == "health":
        return json.dumps(service.health(), indent=2)
    if command == "workflows":
        return json.dumps({"workflows": list(SUPPORTED_WORKFLOWS)}, indent=2)
    if command in {"plan", "run"}:
        return _route_workflow_command(service, command, words[1:])

    return json.dumps(service.chat(prompt), indent=2)


def _route_workflow_command(service: object, command: str, args: list[str]) -> str:
    if not args:
        return json.dumps(
            {
                "error": f"missing workflow name for '{command}'",
                "workflows": list(SUPPORTED_WORKFLOWS),
            },
            indent=2,
        )

    workflow = args[0]
    environment = args[1] if len(args) > 1 else agentkernel_default_environment()
    inventory = args[2] if len(args) > 2 else agentkernel_default_inventory()
    terraform_dir = args[3] if len(args) > 3 else agentkernel_default_terraform_dir()
    host = args[4] if len(args) > 4 else ""
    context = Context(
        environment=environment,
        inventory=inventory,
        terraform_dir=terraform_dir,
        host=host,
    )

    if command == "plan":
        return json.dumps(service.plan(workflow, context), indent=2)
    return json.dumps(service.run(workflow, context), indent=2)
