# API Reference

This document describes the HTTP API surfaces currently implemented in this repository.

There are two related runtime modes:

- direct HTTP mode from `python3 -m microcloud_agent serve`
- Agent Kernel mode from `python3 -m microcloud_agent.agentkernel_app`

## Base modes

### Direct HTTP mode

Default bind:

- host `127.0.0.1`
- port `8765`

### Agent Kernel mode

Configured with:

- `AK_API__HOST`
- `AK_API__PORT`

The Agent Kernel server exposes:

- core Agent Kernel routes such as `/api/v1/agents` and `/api/v1/chat`
- custom runtime routes under `/custom/*`

## Shared payload shapes

### Context

Used by planning and execution endpoints.

```json
{
  "environment": "lab",
  "inventory": "ansible/inventories/lab/hosts.ini",
  "terraform_dir": "terraform/environments/lab",
  "service": "",
  "host": ""
}
```

### Plan request

```json
{
  "workflow": "assess_health",
  "context": {
    "environment": "lab",
    "inventory": "ansible/inventories/lab/hosts.ini",
    "terraform_dir": "terraform/environments/lab"
  }
}
```

### Chat request

```json
{
  "message": "what workflows do you support?"
}
```

## Direct HTTP API

### `GET /health`

Returns:

- approval state
- resolved config values
- tool availability
- channel availability

Example:

```bash
curl http://127.0.0.1:8765/health
```

### `GET /openapi.json`

Returns the local OpenAPI document exposed by `openapi_document()`.

### `GET /openid-configuration`

Returns OIDC discovery information from the configured issuer.

### `POST /plan`

Plans a workflow without executing it.

Request:

```json
{
  "workflow": "assess_health",
  "context": {
    "environment": "lab",
    "inventory": "ansible/inventories/lab/hosts.ini",
    "terraform_dir": "terraform/environments/lab"
  }
}
```

Response shape:

```json
{
  "workflow": "assess_health",
  "context": {
    "environment": "lab",
    "inventory": "ansible/inventories/lab/hosts.ini",
    "terraform_dir": "terraform/environments/lab",
    "service": "",
    "host": ""
  },
  "steps": []
}
```

### `POST /run`

Executes a workflow.

Request:

```json
{
  "workflow": "assess_health",
  "context": {
    "environment": "lab",
    "inventory": "ansible/inventories/lab/hosts.ini",
    "terraform_dir": "terraform/environments/lab"
  }
}
```

Response shape:

```json
{
  "workflow": "assess_health",
  "context": {
    "environment": "lab",
    "inventory": "ansible/inventories/lab/hosts.ini",
    "terraform_dir": "terraform/environments/lab",
    "service": "",
    "host": ""
  },
  "results": []
}
```

For mutating operations, the process will fail unless `MICROCLOUD_AGENT_APPROVAL=approved` is set in the runtime environment.

### `POST /notify`

Sends a Mattermost message.

Request:

```json
{
  "message": "cluster assessment completed",
  "channel": "ops"
}
```

### `POST /chat`

Returns a synchronous JSON chat response.

Request:

```json
{
  "message": "show health status"
}
```

Response:

```json
{
  "message": "show health status",
  "response": "Agent health is available..."
}
```

### `POST /chat/stream`

Returns a Server-Sent Events stream.

Content type:

- `text/event-stream`

Event format:

```text
data: {"delta":"..."}

data: {"done": true}
```

### `POST /oauth2/token`

Requests an OAuth2 client-credentials token using configured issuer and client credentials.

### `POST /openapi/request`

Calls an upstream API via the configured OpenAPI base URL.

Request:

```json
{
  "method": "GET",
  "path": "/v1/status",
  "query": {
    "verbose": "true"
  },
  "headers": {
    "x-trace-id": "demo"
  }
}
```

## Agent Kernel API

In Agent Kernel mode, the runtime adds both native Agent Kernel routes and custom routes.

### Native Agent Kernel routes

#### `GET /health`

Basic Agent Kernel process health.

Example response:

```json
{
  "status": "ok"
}
```

#### `GET /api/v1/agents`

Lists registered Agent Kernel agents.

Example response:

```json
{
  "agents": ["microcloud-operator"]
}
```

#### `POST /api/v1/chat`

Runs the Agent Kernel registered agent.

Request:

```json
{
  "prompt": "health",
  "agent": "microcloud-operator",
  "session_id": "demo-session"
}
```

The bridge converts prompt patterns such as `health`, `workflows`, `plan ...`, and `run ...` into structured runtime operations.

### Custom Agent Kernel routes

These routes are mounted under `/custom`.

#### `GET /custom/health`

Returns the full runtime health payload from `AgentService.health()`.

#### `GET /custom/openapi.json`

Returns the runtime OpenAPI description.

#### `GET /custom/workflows`

Returns:

```json
{
  "workflows": [
    "assess_health",
    "bootstrap_cluster",
    "upgrade_cluster",
    "assess_operator_tooling"
  ]
}
```

#### `POST /custom/plan`

Same behavior as direct `POST /plan`.

#### `POST /custom/run`

Same behavior as direct `POST /run`.

#### `POST /custom/notify`

Same behavior as direct `POST /notify`.

#### `GET /custom/openid-configuration`

Same behavior as direct `GET /openid-configuration`.

#### `POST /custom/oauth2/token`

Same behavior as direct `POST /oauth2/token`.

#### `POST /custom/openapi/request`

Same behavior as direct `POST /openapi/request`.

#### `POST /custom/chat`

Same behavior as direct `POST /chat`.

#### `POST /custom/chat/stream`

Same behavior as direct `POST /chat/stream`.

## Error handling

### Direct HTTP mode

- not found routes return `404` with `{"error":"not found"}`
- request or execution errors return `400` with `{"error":"..."}` from the simple server wrapper

### Agent Kernel mode

- native Agent Kernel routes follow FastAPI and Agent Kernel error semantics
- custom routes inherit FastAPI validation behavior

## CLI equivalents

Most API operations have direct CLI equivalents:

- `health`
- `openapi`
- `plan`
- `run`
- `notify`
- `oidc-discovery`
- `oauth2-token`
- `openapi-request`
- `chat`
- `chat-stream`
- `serve`
