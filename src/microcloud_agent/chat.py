from __future__ import annotations

from typing import Iterable


def chunk_text(text: str) -> Iterable[str]:
    words = text.split()
    for word in words:
        yield f"{word} "


def build_chat_response(message: str, health: dict, workflows: list[str]) -> str:
    normalized = message.lower()
    if "health" in normalized or "status" in normalized:
        available = [name for name, enabled in health["tools"].items() if enabled]
        return (
            f"Agent health is available. Approval is set to {health['approval_granted']}. "
            f"Configured tools currently detected: {', '.join(available) if available else 'none'}."
        )
    if "workflow" in normalized or "plan" in normalized:
        return f"Available workflows are: {', '.join(workflows)}."
    if "mattermost" in normalized:
        configured = health["config"]["mattermost_webhook_configured"]
        channel = health["config"]["mattermost_channel"] or "unset"
        return f"Mattermost webhook configured: {configured}. Default channel: {channel}."
    if "oidc" in normalized or "oauth" in normalized:
        return "OIDC and OAuth2 support are available through discovery and client-credentials token retrieval."
    if "openapi" in normalized:
        return "The agent exposes a local OpenAPI document and can call external OpenAPI endpoints through the configured base URL."
    if "install microcloud" in normalized or "configure microcloud" in normalized:
        return (
            "Use install_microcloud_stack to install the snap-based MicroCloud dependencies, "
            "configure_single_node to bootstrap a single-node cluster, and configure_multi_node "
            "with a host argument to add another node."
        )
    if "tool" in normalized:
        tools = ", ".join(sorted(health["tools"].keys()))
        return f"Available tool channels include: {tools}."
    return (
        "I can report health, install and configure MicroCloud, plan and run workflows, "
        "notify Mattermost, use OIDC/OAuth2, call external OpenAPI endpoints, and expose a streaming chat API."
    )
