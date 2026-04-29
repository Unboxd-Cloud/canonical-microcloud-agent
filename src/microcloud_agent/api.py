from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .adapters import Context
from .service import AgentService


def openapi_document() -> dict[str, Any]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Canonical MicroCloud Agent API", "version": "0.1.0"},
        "paths": {
            "/health": {"get": {"responses": {"200": {"description": "Health payload"}}}},
            "/plan": {"post": {"responses": {"200": {"description": "Workflow plan"}}}},
            "/run": {"post": {"responses": {"200": {"description": "Workflow execution"}}}},
            "/notify": {"post": {"responses": {"200": {"description": "Mattermost notification result"}}}},
            "/chat": {"post": {"responses": {"200": {"description": "Chat response"}}}},
            "/chat/stream": {"post": {"responses": {"200": {"description": "Streaming chat response"}}}},
            "/openid-configuration": {
                "get": {"responses": {"200": {"description": "OIDC discovery document"}}}
            },
            "/oauth2/token": {"post": {"responses": {"200": {"description": "OAuth2 access token"}}}},
            "/openapi/request": {
                "post": {"responses": {"200": {"description": "External OpenAPI request result"}}}
            },
        },
    }


def build_handler(service: AgentService) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            return json.loads(raw.decode("utf-8"))

        def _send_event_stream(self, chunks: list[str]) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            for chunk in chunks:
                payload = json.dumps({"delta": chunk}).encode("utf-8")
                self.wfile.write(b"data: " + payload + b"\n\n")
                self.wfile.flush()
            self.wfile.write(b"data: {\"done\": true}\n\n")
            self.wfile.flush()

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send(200, service.health())
                return
            if self.path == "/openapi.json":
                self._send(200, openapi_document())
                return
            if self.path == "/openid-configuration":
                self._send(200, service.oidc_discovery())
                return
            self._send(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            try:
                payload = self._read_json()
                if self.path == "/plan":
                    context = Context(**payload["context"])
                    self._send(200, service.plan(payload["workflow"], context))
                    return
                if self.path == "/run":
                    context = Context(**payload["context"])
                    self._send(200, service.run(payload["workflow"], context))
                    return
                if self.path == "/notify":
                    self._send(200, service.notify(payload["message"], payload.get("channel")))
                    return
                if self.path == "/chat":
                    self._send(200, service.chat(payload["message"]))
                    return
                if self.path == "/chat/stream":
                    self._send_event_stream(service.stream_chat(payload["message"]))
                    return
                if self.path == "/oauth2/token":
                    self._send(200, service.oauth2_client_credentials())
                    return
                if self.path == "/openapi/request":
                    self._send(
                        200,
                        service.openapi_request(
                            method=payload["method"],
                            path=payload["path"],
                            query=payload.get("query"),
                            headers=payload.get("headers"),
                            json_body=payload.get("json_body"),
                        ),
                    )
                    return
                self._send(404, {"error": "not found"})
            except Exception as exc:  # noqa: BLE001
                self._send(400, {"error": str(exc)})

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return Handler


def serve(host: str, port: int, service: AgentService) -> None:
    server = ThreadingHTTPServer((host, port), build_handler(service))
    try:
        server.serve_forever()
    finally:
        server.server_close()
