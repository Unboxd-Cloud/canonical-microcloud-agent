#!/usr/bin/env bash

set -euo pipefail

IMAGE="${AGENT_IMAGE:-unboxdcloudplatform/canonical-microcloud-agent:latest}"
GOAL="${1:-install and manage MicroCloud on this machine}"

exec docker run --rm -it \
  -e MICROCLOUD_AGENT_MEMORY_PATH=/tmp/memory.json \
  "${IMAGE}" \
  microcloud-agent consult-setup "${GOAL}"
