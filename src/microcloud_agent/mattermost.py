from __future__ import annotations

import json
from urllib import request

from .config import mattermost_default_channel, mattermost_username, mattermost_webhook_url


class MattermostNotifier:
    def __init__(self, webhook_url: str | None = None) -> None:
        self.webhook_url = webhook_url or mattermost_webhook_url()

    def configured(self) -> bool:
        return bool(self.webhook_url)

    def send(self, text: str, channel: str | None = None) -> dict:
        if not self.webhook_url:
            raise RuntimeError("Mattermost webhook is not configured.")

        payload = {
            "text": text,
            "username": mattermost_username(),
        }
        target_channel = channel or mattermost_default_channel()
        if target_channel:
            payload["channel"] = target_channel

        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.webhook_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8").strip()
            return {"status_code": response.status, "body": raw or "ok"}


def format_workflow_message(payload: dict) -> str:
    workflow = payload["workflow"]
    environment = payload["context"]["environment"]
    if "results" in payload:
        lines = [f"MicroCloud workflow `{workflow}` in `{environment}`"]
        for item in payload["results"]:
            result = item["result"]
            lines.append(
                f"- `{item['step']}`: {result['status']} ({result['tool']} {result['action']})"
            )
            if result["stderr"]:
                lines.append(f"  stderr: {result['stderr']}")
        return "\n".join(lines)

    lines = [f"MicroCloud plan `{workflow}` in `{environment}`"]
    for step in payload["steps"]:
        spec = step["spec"]
        lines.append(f"- `{step['name']}`: {' '.join(spec['argv'])}")
    return "\n".join(lines)
