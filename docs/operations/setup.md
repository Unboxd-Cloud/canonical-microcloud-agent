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
```

## Approval gate

Mutating operations are blocked unless you set:

```bash
export MICROCLOUD_AGENT_APPROVAL=approved
```

Use that only for runs you intend to authorize.
