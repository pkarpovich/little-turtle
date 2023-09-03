ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim-bookworm as base

ENV \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.5.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PYTHONWARNINGS="ignore::DeprecationWarning"

RUN set -ex \
    # Create a non-root user
    && addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser \
    # Upgrade the package index and install security upgrades
    && apt-get update \
    && apt-get install -y locales \
    && sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && apt-get upgrade -y \
    # Install dependencies \
    && pip install --upgrade pip \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

FROM base as builder

RUN pip install poetry==${POETRY_VERSION}

WORKDIR /app
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry config virtualenvs.create false
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-dev --no-root
RUN poetry export -f requirements.txt --output requirements.txt


FROM base as runtime

ENV PYTHONPATH="/app:${PYTHONPATH}"

WORKDIR /app

COPY . .
COPY --from=builder /app/requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
     pip install -r requirements.txt

RUN chown -R appuser:appgroup /app

USER appuser

CMD python little_turtle/main.py