FROM python:3.12.1-alpine3.18 AS base

FROM base AS builder

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  PATH="$PATH:/runtime/bin" \
  PYTHONPATH="$PYTHONPATH:/runtime/lib/python3.11/site-packages" \
  # Versions:
  POETRY_VERSION=1.5.1

# System deps:
RUN apk add build-base unzip wget python3-dev libffi-dev
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /src

# Generate requirements and install *all* dependencies.
COPY pyproject.toml poetry.lock /src/
RUN poetry export --dev --without-hashes --no-interaction --no-ansi -f requirements.txt -o requirements.txt
RUN pip install --prefix=/runtime --force-reinstall -r requirements.txt

FROM base AS runtime
COPY --from=builder /runtime /usr/local
COPY ./gocardless_membership_exporter /app/gocardless_membership_exporter
WORKDIR /app
CMD ["python", "-m", "gocardless_membership_exporter"]