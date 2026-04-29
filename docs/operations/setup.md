# Setup Guide

## Local prerequisites

- Python 3.11 or newer
- Optional: `docker` for the integration test
- Optional: `tailscale` if you use Tailscale SSH for remote execution
- Optional: local `ansible` and `terraform` binaries if you want those paths to run from this machine

## Repository setup

```bash
cd /Users/apple/canonical-microcloud-agent
export PYTHONPATH=src
python3 -m microcloud_agent health
```

No package installation is required for the core CLI because it runs directly from `src/`.

## Remote execution setup

For a server that already has Canonical MicroCloud installed:

```bash
export REMOTE_EXEC_PREFIX=ssh
export MICROCLOUD_SSH_TARGET=user@your-microcloud-server
export MICROCLOUD_BIN=/snap/bin/microcloud
export LXC_SSH_TARGET=user@your-microcloud-server
export LXC_BIN=lxc
```

For Tailscale SSH:

```bash
export REMOTE_EXEC_PREFIX="tailscale ssh"
export MICROCLOUD_SSH_TARGET=user@your-tailnet-host
export LXC_SSH_TARGET=user@your-tailnet-host
export MICROCLOUD_BIN=/snap/bin/microcloud
```

## Optional local tool overrides

If Ansible or Terraform are not on the default `PATH`, set:

```bash
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
```

## OIDC / OAuth2 and OpenAPI configuration

Set these when the agent should authenticate through OIDC/OAuth2 or call an external OpenAPI endpoint:

```bash
export OIDC_ISSUER_URL=https://issuer.example.com
export OAUTH2_CLIENT_ID=your-client-id
export OAUTH2_CLIENT_SECRET=your-client-secret
export OAUTH2_SCOPE="openid profile"
export OPENAPI_BASE_URL=https://api.example.com
export OPENAPI_BEARER_TOKEN=your-access-token
```

## Approval gate

Mutating operations are blocked unless you set:

```bash
export MICROCLOUD_AGENT_APPROVAL=approved
```

Use that only for runs you intend to authorize.
