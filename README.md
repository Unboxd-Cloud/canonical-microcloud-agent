# Canonical MicroCloud Agent

This repository contains a runnable local operator agent for Canonical MicroCloud environments.

Additional documentation:

- [Setup Guide](docs/operations/setup.md)
- [Usage and Testing](docs/operations/usage-and-testing.md)
- [Feature Reference](docs/operations/features.md)
- [API Reference](docs/api/reference.md)
- [Docker Deployment](docs/operations/docker-deployment.md)
- [Agent Spec](docs/agent/microcloud-agent-spec.md)
- [Runtime Boundary](docs/architecture/runtime-boundary.md)
- [Approval Model](docs/operations/approval-model.md)
- [Static Landing Page](website/index.html)
- [Next.js Chat UI Template](ui/nextjs-chat-template)

What is real in this repository:

- executable Python CLI under `src/microcloud_agent/`
- Agent Kernel runtime bridge for chat and API serving
- deterministic workflow planning and execution
- approval-gated mutating operations
- real subprocess execution for `microcloud`, `lxc`, `ansible`, `ansible-inventory`, and `terraform`
- env-configurable host operator bridges for `ssh`, VPN, DNS, reverse proxy, Docker cleanup, and computer-use
- OpenAPI-serving local HTTP API
- streaming chat over CLI and HTTP
- OIDC discovery and OAuth2 client-credentials support
- external OpenAPI request channel
- Mattermost notification channel
- Next.js chat template UI
- local validation with `unittest`

What is not assumed:

- the target CLIs are installed on this machine
- production credentials or cluster access exist locally

The agent handles that explicitly by reporting tool availability and failing with actionable errors when the runtime dependencies are absent.

## Runtime modes

This repository supports three real runtime shapes:

- direct local CLI and HTTP mode via `python3 -m microcloud_agent ...`
- Agent Kernel API mode via `python3 -m microcloud_agent.agentkernel_app`
- containerized deployment via the hardened `Dockerfile`

The direct CLI is the simplest operator path.
The Agent Kernel entrypoint is the preferred long-running API runtime.
The container image is the preferred publish and deployment artifact.

## Environment variables

Use environment variables to point the agent at real binaries and your MicroCloud server:

```bash
export REMOTE_EXEC_PREFIX=ssh
export PRIVILEGE_EXEC_PREFIX=sudo
export OPERATOR_SSH_TARGET=user@your-microcloud-server
export MICROCLOUD_SSH_TARGET=user@your-microcloud-server
export MICROCLOUD_BIN=/snap/bin/microcloud
export LXC_SSH_TARGET=user@your-microcloud-server
export LXC_BIN=lxc
export ANSIBLE_BIN=ansible
export ANSIBLE_INVENTORY_BIN=ansible-inventory
export ANSIBLE_PLAYBOOK_BIN=ansible-playbook
export TERRAFORM_BIN=terraform
export GITHUB_BIN=gh
export VSCODE_BIN=code
export DOCKER_BIN=docker
export SNAP_BIN=snap
export SSH_BIN=ssh
export COMPUTERUSE_BIN=computer-use
export VPN_BIN=tailscale
export DNS_BIN=resolvectl
export DIG_BIN=dig
export REVERSEPROXY_BIN=nginx
export REVERSEPROXY_MODE=caddy
export REVERSEPROXY_CONFIG_PATH=/etc/nginx/nginx.conf
export CADDY_BIN=caddy
export CADDYFILE_PATH=/etc/caddy/Caddyfile
export PLAYWRIGHT_BIN=playwright
export CANVAS_BIN=canvas
export OIDC_ISSUER_URL=https://issuer.example.com
export OAUTH2_CLIENT_ID=your-client-id
export OAUTH2_CLIENT_SECRET=your-client-secret
export OPENAPI_BASE_URL=https://api.example.com
export MATTERMOST_WEBHOOK_URL=https://mattermost.example/hooks/your-webhook
export AK_API__HOST=0.0.0.0
export AK_API__PORT=8000
export AGENTKERNEL_AGENT_NAME=microcloud-operator
export AGENTKERNEL_DEFAULT_ENVIRONMENT=lab
export AGENTKERNEL_DEFAULT_INVENTORY=ansible/inventories/lab/hosts.ini
export AGENTKERNEL_DEFAULT_TERRAFORM_DIR=terraform/environments/lab
```

When `MICROCLOUD_SSH_TARGET` is set, MicroCloud commands execute remotely through `ssh`.
When `LXC_SSH_TARGET` is set, LXC commands execute remotely through `ssh`. If `LXC_SSH_TARGET` is unset, it falls back to `MICROCLOUD_SSH_TARGET`.
When `OPERATOR_SSH_TARGET` is set, Docker, Snap, VPN, DNS, reverse-proxy, and computer-use commands execute on that remote host instead of inside the container or local runtime.
When `PRIVILEGE_EXEC_PREFIX` is set, mutating host commands are prefixed with that executable, for example `sudo`.

If you use Tailscale SSH, set:

```bash
export REMOTE_EXEC_PREFIX="tailscale ssh"
export MICROCLOUD_SSH_TARGET=user@your-tailnet-host
export LXC_SSH_TARGET=user@your-tailnet-host
```

## Quick start

```bash
cd /Users/apple/canonical-microcloud-agent
PYTHONPATH=src python3 -m microcloud_agent health
PYTHONPATH=src python3 -m microcloud_agent plan assess_health --environment lab
PYTHONPATH=src python3 -m microcloud_agent run assess_health --environment lab
PYTHONPATH=src python3 -m microcloud_agent plan configure_multi_node --environment lab --host node-2
PYTHONPATH=src python3 -m microcloud_agent serve --host 127.0.0.1 --port 8765
PYTHONPATH=src python3 -m microcloud_agent chat "what workflows do you support?"
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Agent Kernel mode

Run the long-lived API runtime locally with:

```bash
cd /Users/apple/canonical-microcloud-agent
python3 -m venv .venv
. .venv/bin/activate
pip install .[agent-kernel]
AK_API__HOST=127.0.0.1 AK_API__PORT=8010 python -m microcloud_agent.agentkernel_app
```

Useful endpoints in this mode:

- `GET /health`
- `GET /api/v1/agents`
- `POST /api/v1/chat`
- `GET /custom/health`
- `POST /custom/plan`
- `POST /custom/run`
- `POST /custom/chat`
- `POST /custom/chat/stream`

Example:

```bash
curl http://127.0.0.1:8010/api/v1/agents
curl http://127.0.0.1:8010/custom/health
```

## Systemd deployment

A ready-to-install unit is provided at:

- `deploy/systemd/canonical-microcloud-agent-kernel.service`
- `deploy/systemd/canonical-microcloud-agent.env.example`

Typical install flow on a host:

```bash
cp deploy/systemd/canonical-microcloud-agent-kernel.service /etc/systemd/system/
cp deploy/systemd/canonical-microcloud-agent.env.example /etc/canonical-microcloud-agent.env
systemctl daemon-reload
systemctl enable --now canonical-microcloud-agent-kernel
systemctl status canonical-microcloud-agent-kernel
```

The service reads overrides from `/etc/canonical-microcloud-agent.env`.

## Testcontainers integration test

```bash
cd /Users/apple/canonical-microcloud-agent
PYTHONPATH=src python3 -m unittest tests.test_testcontainers_integration -v
```

This test starts a real Alpine container with `testcontainers` and verifies the agent can execute the remote `lxc list --format json` path through the configured transport wrapper.

## Docker image

The container artifact is intended for publication and deployment.

Local build:

```bash
docker build -t canonical-microcloud-agent:test .
```

Local run:

```bash
docker run --rm -p 8000:8000 \
  -e AK_API__HOST=0.0.0.0 \
  -e AK_API__PORT=8000 \
  canonical-microcloud-agent:test
```

For host-operator deployment, prefer the checked-in Docker Compose bundle in `deploy/docker/`.
That contract assumes the container serves the API and reaches the real MicroCloud host over SSH, rather than trying to run `snap` and `microcloud` directly inside the container.

Quick start:

```bash
cd deploy/docker
cp host-operator.env.example host-operator.env
mkdir -p ssh
# place your private key at deploy/docker/ssh/id_ed25519
# optionally install deploy/docker/canonical-microcloud-agent-operator.sudoers.example on the target host
docker compose -f docker-compose.host-operator.yml up -d --build
docker compose -f docker-compose.host-operator.yml port caddy 80
```

The bundled Caddy sidecar uses an auto-assigned host port:

- no fixed binding to host `80` or `443`
- deployment will not fail because those ports are already in use
- inspect the assigned port with `docker compose port caddy 80`

For privileged host workflows, the checked-in env example defaults `PRIVILEGE_EXEC_PREFIX=sudo`. Pair that with the scoped sudoers example at `deploy/docker/canonical-microcloud-agent-operator.sudoers.example` so remote operator commands do not block on password prompts.

Image properties:

- multi-stage build
- non-root runtime user
- bundled `openssh-client` for remote host execution
- OCI image labels
- `pip check` during build
- container `HEALTHCHECK`
- reduced build context via `.dockerignore`

## Docker Hub publishing

The repository now includes a GitHub Actions workflow at `.github/workflows/publish-docker.yml`.

To enable Docker Hub publishing, set:

- repository variable `DOCKERHUB_REPOSITORY`
- secret `DOCKERHUB_USERNAME`
- secret `DOCKERHUB_TOKEN`

`DOCKERHUB_REPOSITORY` should be the full Docker Hub repository name, for example:

```text
unboxdcloudplatform/canonical-microcloud-agent
```

Workflow behavior:

- pull requests build and test the image, but do not push
- pushes to `main` push to Docker Hub when the variable and secrets are configured
- `workflow_dispatch` can force a push with the `push_image` input

Tags produced by the workflow include:

- `latest` on the default branch
- branch tags
- Git tags
- `sha-<commit>`

## Mutating workflows

Mutating operations require an approval token:

```bash
MICROCLOUD_AGENT_APPROVAL=approved PYTHONPATH=src python3 -m microcloud_agent run upgrade_cluster --environment staging
```

Without that token, the agent refuses to execute mutating steps.

Examples of mutating host workflows:

- `install_microcloud_stack`
- `configure_single_node`
- `configure_multi_node --host <node-name>`
- `docker_prune_everything`

## Available workflows

- `assess_health`
- `bootstrap_cluster`
- `upgrade_cluster`
- `assess_operator_tooling`
- `install_microcloud_stack`
- `configure_single_node`
- `configure_multi_node`
- `docker_prune_everything`
