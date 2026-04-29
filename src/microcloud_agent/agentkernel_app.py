from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .adapters import Context
from .agentkernel_bridge import SUPPORTED_WORKFLOWS, route_prompt
from .api import openapi_document
from .config import (
    agentkernel_agent_description,
    agentkernel_agent_name,
    agentkernel_default_environment,
    agentkernel_default_inventory,
    agentkernel_default_terraform_dir,
)
from .service import AgentService


def _require_agentkernel() -> tuple[Any, Any, Any, Any, Any, Any, Any, Any]:
    try:
        from agentkernel.api.handler import RESTRequestHandler
        from agentkernel.api.http import RESTAPI
        from agentkernel.core import Agent, AgentReplyText, AgentRequestText, Module, Runner, Session
    except ImportError as exc:  # pragma: no cover - exercised only in runtime environments
        raise RuntimeError(
            "agentkernel is required for this entrypoint. Install with "
            "`pip install .[agent-kernel]` or `pip install 'agentkernel[api]>=0.3.3'`."
        ) from exc
    return RESTRequestHandler, RESTAPI, Agent, AgentReplyText, AgentRequestText, Module, Runner, Session


@dataclass
class _AgentDefinition:
    name: str
    description: str


class _WorkflowRequest(BaseModel):
    workflow: str
    context: Context = Field(
        default_factory=lambda: Context(
            environment=agentkernel_default_environment(),
            inventory=agentkernel_default_inventory(),
            terraform_dir=agentkernel_default_terraform_dir(),
        )
    )


class _ChatRequest(BaseModel):
    message: str


class _NotifyRequest(BaseModel):
    message: str
    channel: str | None = None


class _OpenAPIRequest(BaseModel):
    method: str
    path: str
    query: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    json_body: object | None = None


def _build_custom_handler(service: AgentService) -> Any:
    RESTRequestHandler, *_ = _require_agentkernel()

    class CustomHandler(RESTRequestHandler):
        def get_router(self) -> APIRouter:
            router = APIRouter()

            @router.get("/health")
            def health() -> dict:
                return service.health()

            @router.get("/openapi.json")
            def spec() -> dict:
                return openapi_document()

            @router.get("/workflows")
            def workflows() -> dict:
                return {"workflows": list(SUPPORTED_WORKFLOWS)}

            @router.post("/plan")
            def plan(body: _WorkflowRequest) -> dict:
                return service.plan(body.workflow, body.context)

            @router.post("/run")
            def run(body: _WorkflowRequest) -> dict:
                return service.run(body.workflow, body.context)

            @router.post("/notify")
            def notify(body: _NotifyRequest) -> dict:
                return service.notify(body.message, channel=body.channel)

            @router.get("/openid-configuration")
            def oidc_discovery() -> dict:
                return service.oidc_discovery()

            @router.post("/oauth2/token")
            def oauth2_token() -> dict:
                return service.oauth2_client_credentials()

            @router.post("/openapi/request")
            def openapi_request(body: _OpenAPIRequest) -> dict:
                return service.openapi_request(
                    method=body.method,
                    path=body.path,
                    query=body.query,
                    headers=body.headers,
                    json_body=body.json_body,
                )

            @router.post("/chat")
            def chat(body: _ChatRequest) -> dict:
                return service.chat(body.message)

            @router.post("/chat/stream")
            def chat_stream(body: _ChatRequest) -> StreamingResponse:
                def emit() -> Any:
                    for chunk in service.stream_chat(body.message):
                        yield f"data: {json.dumps({'delta': chunk})}\n\n"
                    yield "data: {\"done\": true}\n\n"

                return StreamingResponse(emit(), media_type="text/event-stream")

            return router

    return CustomHandler()


def _build_module(service: AgentService) -> Any:
    _, _, Agent, AgentReplyText, AgentRequestText, Module, Runner, Session = _require_agentkernel()

    class MicroCloudRunner(Runner):
        def __init__(self) -> None:
            super().__init__("microcloud-agent-kernel-runner")

        async def run(self, agent: Any, session: Any, requests: list[Any]) -> Any:
            prompt = " ".join(
                request.text
                for request in requests
                if isinstance(request, AgentRequestText)
            ).strip()
            response = route_prompt(service, prompt)
            return AgentReplyText(text=response, prompt=prompt)

    class MicroCloudAgent(Agent):
        def __init__(self, definition: _AgentDefinition) -> None:
            self._description = definition.description
            super().__init__(definition.name, MicroCloudRunner())

        def get_description(self) -> str:
            return self._description

        def override_system_prompt(self, prompt: str) -> None:
            return None

        def attach_tool(self, tool: Any) -> None:
            return None

        def get_a2a_card(self) -> Any:
            return None

    class MicroCloudModule(Module):
        def __init__(self, definitions: list[_AgentDefinition]) -> None:
            super().__init__()
            self._definitions = definitions
            self.load(definitions)

        def load(self, agents: list[_AgentDefinition]) -> Any:
            return super().load(agents)

        def _wrap(self, agent: _AgentDefinition, agents: list[_AgentDefinition]) -> Any:
            return MicroCloudAgent(agent)

        def pre_hook(self, agent: Any, hooks: list[Any]) -> Any:
            wrapped = self.get_agent(agent.name)
            if wrapped is None:
                raise KeyError(f"Unknown agent '{agent.name}'.")
            wrapped.pre_hooks.extend(hooks)
            return self

        def post_hook(self, agent: Any, hooks: list[Any]) -> Any:
            wrapped = self.get_agent(agent.name)
            if wrapped is None:
                raise KeyError(f"Unknown agent '{agent.name}'.")
            wrapped.post_hooks.extend(hooks)
            return self

    return MicroCloudModule(
        [
            _AgentDefinition(
                name=agentkernel_agent_name(),
                description=agentkernel_agent_description(),
            )
        ]
    )


def main() -> int:
    _, RESTAPI, *_ = _require_agentkernel()
    service = AgentService()
    _build_module(service)
    RESTAPI.add(_build_custom_handler(service).get_router())
    RESTAPI.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
