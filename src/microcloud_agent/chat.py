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
            f"I checked the current agent state for you. Approval is set to {health['approval_granted']}. "
            f"Right now I can detect these configured tools: {', '.join(available) if available else 'none'}."
        )
    if "workflow" in normalized or "plan" in normalized:
        return f"I can help with these workflows: {', '.join(workflows)}."
    if "mattermost" in normalized:
        configured = health["config"]["mattermost_webhook_configured"]
        channel = health["config"]["mattermost_channel"] or "unset"
        return f"I checked the Mattermost settings. Webhook configured: {configured}. Default channel: {channel}."
    if "oidc" in normalized or "oauth" in normalized:
        return "OIDC and OAuth2 support are available here through discovery and client-credentials token retrieval."
    if "openapi" in normalized:
        return "The agent exposes a local OpenAPI document and can call external OpenAPI endpoints through the configured base URL."
    if "install" in normalized or "setup" in normalized or "bootstrap" in normalized:
        return (
            "I can inspect the host, suggest a suitable MicroCloud configuration, and ask only for the decisions "
            "that still need your input before any mutating step."
        )
    if "install microcloud" in normalized or "configure microcloud" in normalized:
        return (
            "A safe path is to start with a consultative setup pass, then use install_microcloud_stack to install "
            "the snap-based MicroCloud dependencies, configure_single_node to bootstrap a single-node cluster, "
            "and configure_multi_node with a host argument to add another node."
        )
    if "tool" in normalized:
        tools = ", ".join(sorted(health["tools"].keys()))
        return f"I currently know about these tool channels: {tools}."
    return (
        "I can help you figure out the right MicroCloud path for this host, report health, plan and run workflows, "
        "remember operator preferences, notify Mattermost, use OIDC/OAuth2, call external OpenAPI endpoints, "
        "and expose a streaming chat API."
    )
