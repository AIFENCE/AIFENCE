# AIFENCE unified control plane image.
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install the package with the production-relevant extras.
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --upgrade pip && pip install ".[postgres,otel,s3]"

# Migrations + config live alongside the package.
COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 8080

# Non-root runtime.
RUN useradd --system --uid 10001 aifence && chown -R aifence /app
USER aifence

CMD ["aifence-api"]
