from __future__ import annotations

import json
from typing import Any, Callable
from urllib import parse, request

from .config import openapi_base_url, openapi_bearer_token, openapi_timeout_seconds


class OpenAPIClient:
    def __init__(
        self,
        base_url: str | None = None,
        bearer_token: str | None = None,
        timeout: float | None = None,
        opener: Callable[..., Any] | None = None,
    ) -> None:
        self.base_url = (base_url or openapi_base_url()).rstrip("/")
        self.bearer_token = bearer_token if bearer_token is not None else openapi_bearer_token()
        self.timeout = timeout if timeout is not None else openapi_timeout_seconds()
        self.opener = opener or request.urlopen

    def configured(self) -> bool:
        return bool(self.base_url)

    def request(
        self,
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        json_body: Any | None = None,
    ) -> dict[str, Any]:
        if not self.base_url:
            raise RuntimeError("OpenAPI base URL is not configured.")

        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{normalized_path}"
        if query:
            url = f"{url}?{parse.urlencode(query)}"

        req_headers = {"Accept": "application/json", **(headers or {})}
        body = None
        if self.bearer_token:
            req_headers["Authorization"] = f"Bearer {self.bearer_token}"
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            req_headers["Content-Type"] = "application/json"

        req = request.Request(url, data=body, headers=req_headers, method=method.upper())
        with self.opener(req, timeout=self.timeout) as response:
            payload = response.read().decode("utf-8")
            try:
                parsed = json.loads(payload) if payload else None
            except json.JSONDecodeError:
                parsed = payload
            return {"status_code": response.status, "body": parsed}
