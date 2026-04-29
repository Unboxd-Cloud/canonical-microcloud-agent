from __future__ import annotations

import argparse
import json

from .adapters import Context
from .service import AgentService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="microcloud-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health")

    for name in ("plan", "run"):
        sub = subparsers.add_parser(name)
        sub.add_argument("workflow")
        sub.add_argument("--environment", default="lab")
        sub.add_argument("--inventory", default="ansible/inventories/lab/hosts.ini")
        sub.add_argument("--terraform-dir", default="terraform/environments/lab")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    service = AgentService()

    if args.command == "health":
        print(json.dumps(service.health(), indent=2))
        return 0

    context = Context(
        environment=args.environment,
        inventory=args.inventory,
        terraform_dir=args.terraform_dir,
    )
    if args.command == "plan":
        print(json.dumps(service.plan(args.workflow, context), indent=2))
        return 0

    print(json.dumps(service.run(args.workflow, context), indent=2))
    return 0

