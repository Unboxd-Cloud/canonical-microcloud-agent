FROM python:3.12-slim AS builder

ARG AGENTKERNEL_DEPENDENCY_SPEC="agentkernel[api]>=0.3.3"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

RUN python -m venv "$VIRTUAL_ENV" \
    && pip install --upgrade pip

COPY pyproject.toml README.md ./
COPY src ./src
COPY ansible ./ansible
COPY terraform ./terraform

RUN pip install "${AGENTKERNEL_DEPENDENCY_SPEC}" . \
    && pip check

FROM python:3.12-slim

ARG VERSION="0.1.0"
ARG VCS_REF="unknown"
ARG BUILD_DATE="unknown"

LABEL org.opencontainers.image.title="canonical-microcloud-agent" \
      org.opencontainers.image.description="Canonical MicroCloud agent packaged with Agent Kernel" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="https://github.com/unboxdcloudplatform/canonical-microcloud-agent"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    AK_API__HOST=0.0.0.0 \
    AK_API__PORT=8000

WORKDIR /app

RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /home/app app \
    && mkdir -p /app \
    && chown -R app:app /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app pyproject.toml README.md ./
COPY --from=builder --chown=app:app /app/src ./src
COPY --from=builder --chown=app:app /app/ansible ./ansible
COPY --from=builder --chown=app:app /app/terraform ./terraform

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["python", "-m", "microcloud_agent.agentkernel_app"]
