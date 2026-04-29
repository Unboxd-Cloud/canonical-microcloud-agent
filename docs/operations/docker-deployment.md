# Docker Deployment

## Recommended model

For this agent, Docker should host the API runtime, not pretend to be the MicroCloud host.

The containerized contract is:

- the agent runs in Docker
- host-operator commands execute over `ssh` or `tailscale ssh`
- the target server keeps the real `microcloud`, `lxc`, `snap`, Docker, DNS, and reverse-proxy binaries

That avoids fragile bind-mount and privilege combinations for `snap` and host lifecycle control.

## Deployment bundle

Use:

- `deploy/docker/docker-compose.host-operator.yml`
- `deploy/docker/host-operator.env.example`

Typical setup:

```bash
cd deploy/docker
cp host-operator.env.example host-operator.env
mkdir -p ssh
chmod 700 ssh
# place your SSH private key at deploy/docker/ssh/id_ed25519
docker compose -f docker-compose.host-operator.yml up -d --build
docker compose -f docker-compose.host-operator.yml port caddy 80
```

## Reverse proxy

The bundle uses a Caddy sidecar.

Why Caddy here:

- the agent container only exposes port `8000` internally
- Caddy publishes an auto-assigned host port with `127.0.0.1::80`
- deployment does not fail when host ports `80` or `443` are already taken

To discover the assigned port:

```bash
docker compose -f docker-compose.host-operator.yml port caddy 80
```

## Key environment variables

- `REMOTE_EXEC_PREFIX`
- `OPERATOR_SSH_TARGET`
- `MICROCLOUD_SSH_TARGET`
- `LXC_SSH_TARGET`
- `REVERSEPROXY_MODE`
- `CADDY_BIN`
- `CADDYFILE_PATH`
- `MICROCLOUD_AGENT_APPROVAL`

Recommended defaults:

```bash
REMOTE_EXEC_PREFIX="ssh -i /run/agent-ssh/id_ed25519 -o StrictHostKeyChecking=accept-new"
OPERATOR_SSH_TARGET="ubuntu@your-microcloud-host"
MICROCLOUD_SSH_TARGET="ubuntu@your-microcloud-host"
LXC_SSH_TARGET="ubuntu@your-microcloud-host"
REVERSEPROXY_MODE="caddy"
```

## Approval boundary

Mutating workflows still require:

```bash
MICROCLOUD_AGENT_APPROVAL=approved
```

That includes workflows such as:

- `install_microcloud_stack`
- `configure_single_node`
- `configure_multi_node`
- `docker_prune_everything`

## Operational notes

- The image includes `openssh-client` so remote execution works in-container.
- If you want `tailscale ssh` instead of `ssh`, provide that binary in your image or build a derivative image that installs it.
- If the remote host uses Caddy, set `REVERSEPROXY_MODE=caddy`.
- If the remote host uses Nginx, set `REVERSEPROXY_MODE=nginx` and `REVERSEPROXY_CONFIG_PATH=/etc/nginx/nginx.conf`.
