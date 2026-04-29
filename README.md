# Canonical MicroCloud Agent

This repository contains a runnable local operator agent for Canonical MicroCloud environments.

What is real in this repository:

- executable Python CLI under `src/microcloud_agent/`
- deterministic workflow planning and execution
- approval-gated mutating operations
- real subprocess execution for `microcloud`, `lxc`, `ansible`, `ansible-inventory`, and `terraform`
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
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Testcontainers integration test

```bash
cd /Users/apple/canonical-microcloud-agent
PYTHONPATH=src python3 -m unittest tests.test_testcontainers_integration -v
```

This test starts a real Alpine container with `testcontainers` and verifies the agent can execute the remote `lxc list --format json` path through the configured transport wrapper.

## Mutating workflows

Mutating operations require an approval token:

```bash
MICROCLOUD_AGENT_APPROVAL=approved PYTHONPATH=src python3 -m microcloud_agent run upgrade_cluster --environment staging
```

Without that token, the agent refuses to execute mutating steps.
