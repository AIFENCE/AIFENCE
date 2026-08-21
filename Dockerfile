# AIFENCE unified control plane image.

FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1

WORKDIR /build

# Build/install the production dependency tree into an isolated prefix.
# Build tooling and pip remain in this disposable stage.
COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip \
    && python -m pip install --prefix=/install ".[postgres,otel,s3]"


FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Pull Debian security updates into the final runtime image.
# Remove packaging/build tooling after the OS update; AIFENCE does not
# require pip, setuptools, or wheel at runtime.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip uninstall -y setuptools wheel \
    && python -m pip uninstall -y pip \
    && rm -rf /root/.cache

# Copy only the installed runtime tree from the disposable builder.
COPY --from=builder /install /usr/local

# Migrations + config live alongside the installed package.
COPY alembic.ini ./
COPY alembic ./alembic

# Non-root runtime.
RUN useradd --system --uid 10001 aifence \
    && chown -R aifence /app

USER aifence

EXPOSE 8080

CMD ["aifence-api"]