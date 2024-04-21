ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bookworm as base

ENV \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONWARNINGS="ignore::DeprecationWarning" \
    PATH="/root/.cargo/bin:$PATH"

RUN --mount=type=cache,target=/var/cache/apt \
    set -ex \
    # Upgrade the package index and install security upgrades
    && apt update \
    && apt upgrade -y \
    && apt install -y curl \
    # Clean up
    && apt autoremove -y \
    && apt clean -y \
    && rm -rf /var/lib/apt/lists/*

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh


FROM base as dependencies

WORKDIR /app
RUN uv venv
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    --mount=type=cache,target=/root/.cache/uv \
    uv pip sync requirements.txt


FROM python:${PYTHON_VERSION}-slim

WORKDIR /app
ENV \
    LANG=ru_RU.UTF-8 \
    LC_ALL=ru_RU.UTF-8 \
    PYTHONPATH="/app:${PYTHONPATH}" \
    PATH="/app/.venv/bin:$PATH"
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser

COPY --from=dependencies /app/.venv /app/.venv
COPY . .

RUN mkdir -p /app/little_turtle/images
RUN chown -R appuser:appgroup /app

USER appuser

CMD python little_turtle/main.py
# Run infinite loop to keep container running
#CMD tail -f /dev/null