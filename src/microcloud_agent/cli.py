from __future__ import annotations

import argparse
import json
import sys

from .adapters import Context
from .api import openapi_document, serve
from .service import AgentService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="microcloud-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health")
    subparsers.add_parser("openapi")

    for name in ("plan", "run"):
        sub = subparsers.add_parser(name)
        sub.add_argument("workflow")
        sub.add_argument("--environment", default="lab")
        sub.add_argument("--inventory", default="ansible/inventories/lab/hosts.ini")
        sub.add_argument("--terraform-dir", default="terraform/environments/lab")
        sub.add_argument("--mattermost", action="store_true")
        sub.add_argument("--mattermost-channel")

    notify = subparsers.add_parser("notify")
    notify.add_argument("message")
    notify.add_argument("--channel")

    oidc = subparsers.add_parser("oidc-discovery")
    oauth2 = subparsers.add_parser("oauth2-token")

    openapi_request = subparsers.add_parser("openapi-request")
    openapi_request.add_argument("method")
    openapi_request.add_argument("path")
    openapi_request.add_argument("--header", action="append", default=[])
    openapi_request.add_argument("--query", action="append", default=[])
    openapi_request.add_argument("--json")

    chat = subparsers.add_parser("chat")
    chat.add_argument("message")

    chat_stream = subparsers.add_parser("chat-stream")
    chat_stream.add_argument("message")

    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8765)

    return parser


def parse_key_values(items: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in items:
        key, _, value = item.partition("=")
        parsed[key] = value
    return parsed


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    service = AgentService()

    if args.command == "health":
        print(json.dumps(service.health(), indent=2))
        return 0

    if args.command == "openapi":
        print(json.dumps(openapi_document(), indent=2))
        return 0

    if args.command == "notify":
        print(json.dumps(service.notify(args.message, channel=args.channel), indent=2))
        return 0

    if args.command == "oidc-discovery":
        print(json.dumps(service.oidc_discovery(), indent=2))
        return 0

    if args.command == "oauth2-token":
        print(json.dumps(service.oauth2_client_credentials(), indent=2))
        return 0

    if args.command == "openapi-request":
        json_body = json.loads(args.json) if args.json else None
        payload = service.openapi_request(
            method=args.method,
            path=args.path,
            query=parse_key_values(args.query),
            headers=parse_key_values(args.header),
            json_body=json_body,
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "chat":
        print(json.dumps(service.chat(args.message), indent=2))
        return 0

    if args.command == "chat-stream":
        for chunk in service.stream_chat(args.message):
            sys.stdout.write(chunk)
            sys.stdout.flush()
        sys.stdout.write("\n")
        return 0

    if args.command == "serve":
        serve(args.host, args.port, service)
        return 0

    context = Context(
        environment=args.environment,
        inventory=args.inventory,
        terraform_dir=args.terraform_dir,
    )
    if args.command == "plan":
        payload = service.plan(args.workflow, context)
        if args.mattermost:
            payload["mattermost"] = service.notify_workflow(payload, channel=args.mattermost_channel)
        print(json.dumps(payload, indent=2))
        return 0

    payload = service.run(args.workflow, context)
    if args.mattermost:
        payload["mattermost"] = service.notify_workflow(payload, channel=args.mattermost_channel)
    print(json.dumps(payload, indent=2))
    return 0
