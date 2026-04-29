from __future__ import annotations

import json
from base64 import b64encode
from typing import Any, Callable
from urllib import parse, request

from .config import (
    oauth2_client_id,
    oauth2_client_secret,
    oauth2_scope,
    oidc_issuer_url,
    openapi_timeout_seconds,
)


class OIDCClient:
    def __init__(
        self,
        issuer_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        scope: str | None = None,
        timeout: float | None = None,
        opener: Callable[..., Any] | None = None,
    ) -> None:
        self.issuer_url = (issuer_url or oidc_issuer_url()).rstrip("/")
        self.client_id = client_id if client_id is not None else oauth2_client_id()
        self.client_secret = client_secret if client_secret is not None else oauth2_client_secret()
        self.scope = scope if scope is not None else oauth2_scope()
        self.timeout = timeout if timeout is not None else openapi_timeout_seconds()
        self.opener = opener or request.urlopen

    def configured(self) -> bool:
        return bool(self.issuer_url and self.client_id and self.client_secret)

    def discovery_document(self) -> dict[str, Any]:
        if not self.issuer_url:
            raise RuntimeError("OIDC issuer URL is not configured.")
        url = f"{self.issuer_url}/.well-known/openid-configuration"
        req = request.Request(url, headers={"Accept": "application/json"}, method="GET")
        with self.opener(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def client_credentials_token(self) -> dict[str, Any]:
        if not self.configured():
            raise RuntimeError("OIDC/OAuth2 client credentials are not fully configured.")

        discovery = self.discovery_document()
        token_endpoint = discovery["token_endpoint"]
        form = {"grant_type": "client_credentials"}
        if self.scope:
            form["scope"] = self.scope
        body = parse.urlencode(form).encode("utf-8")
        basic = b64encode(f"{self.client_id}:{self.client_secret}".encode("utf-8")).decode("ascii")
        req = request.Request(
            token_endpoint,
            data=body,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {basic}",
            },
            method="POST",
        )
        with self.opener(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))
