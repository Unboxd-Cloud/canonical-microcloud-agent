# Canonical MicroCloud Agent

This repository contains a runnable local operator agent for Canonical MicroCloud environments.

Additional documentation:

- [Setup Guide](docs/operations/setup.md)
- [Usage and Testing](docs/operations/usage-and-testing.md)
- [Agent Spec](docs/agent/microcloud-agent-spec.md)
- [Runtime Boundary](docs/architecture/runtime-boundary.md)
- [Approval Model](docs/operations/approval-model.md)
- [Next.js Chat UI Template](ui/nextjs-chat-template)

What is real in this repository:

- executable Python CLI under `src/microcloud_agent/`
- deterministic workflow planning and execution
- approval-gated mutating operations
- real subprocess execution for `microcloud`, `lxc`, `ansible`, `ansible-inventory`, and `terraform`
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

## Environment variables

Use environment variables to point the agent at real binaries and your MicroCloud server:

```bash
export REMOTE_EXEC_PREFIX=ssh
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
export PLAYWRIGHT_BIN=playwright
export CANVAS_BIN=canvas
export OIDC_ISSUER_URL=https://issuer.example.com
export OAUTH2_CLIENT_ID=your-client-id
export OAUTH2_CLIENT_SECRET=your-client-secret
export OPENAPI_BASE_URL=https://api.example.com
export MATTERMOST_WEBHOOK_URL=https://mattermost.example/hooks/your-webhook
```

When `MICROCLOUD_SSH_TARGET` is set, MicroCloud commands execute remotely through `ssh`.
When `LXC_SSH_TARGET` is set, LXC commands execute remotely through `ssh`. If `LXC_SSH_TARGET` is unset, it falls back to `MICROCLOUD_SSH_TARGET`.

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
PYTHONPATH=src python3 -m microcloud_agent serve --host 127.0.0.1 --port 8765
PYTHONPATH=src python3 -m microcloud_agent chat "what workflows do you support?"
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Testcontainers integration test

```bash
cd /Users/apple/canonical-microcloud-agent
PYTHONPATH=src python3 -m unittest tests.test_testcontainers_integration -v
```

This test starts a real Alpine container with `testcontainers` and verifies the agent can execute the remote `lxc list --format json` path through the configured transport wrapper.

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

## Mutating workflows

Mutating operations require an approval token:

```bash
MICROCLOUD_AGENT_APPROVAL=approved PYTHONPATH=src python3 -m microcloud_agent run upgrade_cluster --environment staging
```

Without that token, the agent refuses to execute mutating steps.

## Available workflows

- `assess_health`
- `bootstrap_cluster`
- `upgrade_cluster`
- `assess_operator_tooling`
