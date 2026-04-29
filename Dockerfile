FROM python:3.12-slim

ARG AGENTKERNEL_DEPENDENCY_SPEC="agentkernel[api]>=0.3.3"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    AK_API__HOST=0.0.0.0 \
    AK_API__PORT=8000

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY ansible ./ansible
COPY terraform ./terraform

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "${AGENTKERNEL_DEPENDENCY_SPEC}" .

EXPOSE 8000

CMD ["python", "-m", "microcloud_agent.agentkernel_app"]
