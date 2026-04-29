# Feature Reference

This document describes the real feature surface implemented in this repository.

## Core runtime

- Local Python CLI under `src/microcloud_agent/cli.py`
- Direct HTTP server under `src/microcloud_agent/api.py`
- Agent Kernel bridge under `src/microcloud_agent/agentkernel_app.py`
- Hardened Docker image build via `Dockerfile`
- Docker host-operator deployment bundle under `deploy/docker/`
- Systemd deployment template under `deploy/systemd/`

## Execution model

The agent is deterministic by design.

- Workflow planning returns the exact command steps that will be executed.
- Workflow execution runs those steps in order and stops on the first failing step.
- Mutating steps are blocked unless `MICROCLOUD_AGENT_APPROVAL=approved` is set.
- Tool availability is discovered at runtime from actual binaries on the host.

## Tool adapters

The runtime currently exposes these tool families:

- `microcloud`
- `lxc`
- `ansible`
- `ansible-inventory`
- `ansible-playbook`
- `terraform`
- `github`
- `vscode`
- `docker`
- `snap`
- `ssh`
- `computeruse`
- `vpn`
- `dns`
- `reverseproxy`
- `playwright`
- `canvas`

Each adapter resolves its binary from environment variables and reports availability through the health endpoint.

## Remote execution

The runtime can execute `microcloud`, `lxc`, and host-operator tooling either locally or remotely.

- Local mode runs the configured binary directly.
- Remote mode wraps the command with `REMOTE_EXEC_PREFIX`.
- `MICROCLOUD_SSH_TARGET` enables remote `microcloud`.
- `LXC_SSH_TARGET` enables remote `lxc`.
- If `LXC_SSH_TARGET` is unset, it falls back to `MICROCLOUD_SSH_TARGET`.
- `OPERATOR_SSH_TARGET` enables remote Docker, Snap, VPN, DNS, reverse-proxy, and computer-use commands.

Typical remote prefixes:

- `ssh`
- `tailscale ssh`

## Workflows

### `assess_health`

Purpose:
Validate operator visibility across inventory, cluster, containers, and Terraform.

Steps:

- Ansible inventory dump
- Ansible fact gathering
- `microcloud status`
- `lxc list --format json`
- `terraform validate`

### `bootstrap_cluster`

Purpose:
Perform preflight checks and initialize a MicroCloud cluster.

Steps:

- Ansible preflight playbook
- `terraform plan`
- `microcloud init`

This workflow is mutating.

### `upgrade_cluster`

Purpose:
Assess upgrade readiness before applying cluster changes.

Steps:

- Ansible inventory dump
- `microcloud status`
- `terraform plan`

### `assess_operator_tooling`

Purpose:
Check whether supporting operator tools are installed on the runtime host.

Steps:

- `gh auth status`
- `code --version`
- `ssh -V`
- `docker --version`
- `snap version`
- VPN status
- DNS status
- `dig -v`
- reverse-proxy validation
- computer-use version
- `playwright --version`
- `canvas --version`

### `install_microcloud_stack`

Purpose:
Install the snap-based MicroCloud host dependencies on the target host.

Steps:

- `snap install lxd --cohort=+`
- `snap install microceph --cohort=+`
- `snap install microovn --cohort=+`
- `snap install microcloud --cohort=+`
- `snap refresh ... --hold`

This workflow is mutating.

### `configure_single_node`

Purpose:
Prepare and bootstrap a single-node MicroCloud deployment.

Steps:

- Ansible inventory dump
- Ansible preflight playbook
- `microcloud init`
- `microcloud status`

This workflow is mutating.

### `configure_multi_node`

Purpose:
Add another node to an existing MicroCloud deployment.

Steps:

- Ansible inventory dump
- `microcloud status`
- `microcloud add <host>`
- `lxc list --format json`

This workflow is mutating and requires a `host` value in context.

### `docker_prune_everything`

Purpose:
Perform a full Docker cleanup on the target operator host.

Steps:

- `docker info`
- `docker system prune -a --volumes -f`

This workflow is mutating.

## Chat and interaction channels

The runtime supports both request-response and streaming interaction.

- CLI chat: `chat`
- CLI streaming chat: `chat-stream`
- HTTP chat: `POST /chat`
- HTTP streaming chat: `POST /chat/stream`
- Agent Kernel chat: `POST /api/v1/chat`
- Agent Kernel custom chat: `POST /custom/chat`

The current chat layer is capability-oriented. It answers questions about health, workflows, OIDC, OpenAPI, Mattermost, and tool availability.

## Notifications

Mattermost is supported as an outbound notification channel.

Capabilities:

- send a raw message
- send a formatted workflow summary
- configure default channel and username from environment variables

Required variables:

- `MATTERMOST_WEBHOOK_URL`
- optional `MATTERMOST_CHANNEL`
- optional `MATTERMOST_USERNAME`

## Identity and API federation

### OIDC

The runtime can expose discovery information from a configured issuer:

- `GET /openid-configuration`

### OAuth2

The runtime can request a client-credentials token:

- `POST /oauth2/token`

Required configuration:

- `OIDC_ISSUER_URL`
- `OAUTH2_CLIENT_ID`
- `OAUTH2_CLIENT_SECRET`
- optional `OAUTH2_SCOPE`

### External OpenAPI requests

The runtime can call an upstream API through a configured base URL:

- `POST /openapi/request`

Required configuration:

- `OPENAPI_BASE_URL`
- optional `OPENAPI_BEARER_TOKEN`
- optional `OPENAPI_TIMEOUT_SECONDS`

## Deployment features

### Agent Kernel mode

Provides:

- standard Agent Kernel agent listing at `/api/v1/agents`
- Agent Kernel chat at `/api/v1/chat`
- custom runtime routes under `/custom/*`

### Docker image

The container image currently includes:

- multi-stage build
- non-root runtime user
- `openssh-client` for remote operator execution
- OCI image labels
- `pip check` at build time
- Docker `HEALTHCHECK`
- reduced build context through `.dockerignore`

### Docker deployment bundle

The repository includes a Compose-based host-operator deployment bundle:

- `deploy/docker/docker-compose.host-operator.yml`
- `deploy/docker/host-operator.env.example`

It uses:

- the agent container for API/runtime
- a Caddy sidecar for reverse proxying
- auto-assigned host port publishing for Caddy so deployment does not fail when `80` or `443` are occupied

### GitHub Actions publishing

The repository includes Docker Hub publication automation in `.github/workflows/publish-docker.yml`.

Capabilities:

- test before image build
- multi-arch build for `amd64` and `arm64`
- SBOM generation
- provenance generation
- conditional Docker Hub push on configured branches or manual dispatch
