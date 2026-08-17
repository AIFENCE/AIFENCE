# SPDX-License-Identifier: AGPL-3.0-or-later
"""Application-level configuration shared across AIFENCE subsystems.

``CoreSettings`` holds only the concerns that the composed FastAPI application
itself needs — environment, database, HTTP surface, telemetry. Each subsystem
(``bus``, ``guard``, ``quality``) layers its own domain settings on top rather
than inflating this object; that split is what keeps one merged codebase
maintainable instead of collapsing ~150 guard-specific knobs into "core".

Environment variables use the ``AIFENCE_`` prefix. A small set of legacy
variable names is also accepted as a fallback so pre-existing deployments can
migrate without an immediate configuration rewrite.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from .env import env_bool, env_csv, env_int, env_secret, env_str

VALID_ENVIRONMENTS = {"development", "test", "staging", "production"}
VALID_RUNTIME_ROLES = {
    "control-plane",
    "dispatcher",
    "lifecycle",
    "anchor",
    "migration",
    "maintenance",
}


@dataclass(frozen=True)
class CoreSettings:
    """Cross-cutting settings for the composed AIFENCE application."""

    # Identity / lifecycle
    environment: str = "development"
    runtime_role: str = "control-plane"
    log_level: str = "INFO"

    # HTTP surface
    bind_host: str = "0.0.0.0"
    bind_port: int = 8080
    public_base_url: str = "http://localhost:8080"
    source_code_url: str = "https://github.com/NeuralBinary/AIFENCE"
    commercial_license_url: str = (
        "https://github.com/NeuralBinary/AIFENCE/blob/main/COMMERCIAL-LICENSE.md"
    )
    docs_enabled: bool = True
    allowed_origins: tuple[str, ...] = ()
    allowed_hosts: tuple[str, ...] = ()
    max_request_bytes: int = 2 * 1024 * 1024

    # Persistence
    database_url: str = "sqlite+pysqlite:///./aifence.db"
    db_pool_size: int = 20
    db_max_overflow: int = 20
    auto_create_schema: bool = True

    # Observability
    otel_service_name: str = "aifence"
    otel_exporter_otlp_endpoint: str = ""
    metrics_public: bool = False

    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> CoreSettings:
        settings = cls(
            environment=env_str(
                "AIFENCE_ENVIRONMENT", "development",
                legacy=("AGENTDANCE_ENVIRONMENT", "SAGE_ENV"),
            ).lower(),
            runtime_role=env_str(
                "AIFENCE_RUNTIME_ROLE", "control-plane",
                legacy=("AGENTDANCE_RUNTIME_ROLE",),
            ).lower(),
            log_level=env_str(
                "AIFENCE_LOG_LEVEL", "INFO", legacy=("AGENTDANCE_LOG_LEVEL",)
            ).upper(),
            bind_host=env_str("AIFENCE_BIND_HOST", "0.0.0.0", legacy=("AGENTDANCE_BIND_HOST",)),
            bind_port=env_int("AIFENCE_BIND_PORT", 8080, legacy=("AGENTDANCE_BIND_PORT",)),
            public_base_url=env_str(
                "AIFENCE_PUBLIC_BASE_URL", "http://localhost:8080",
                legacy=("AGENTDANCE_PUBLIC_BASE_URL",),
            ),
            source_code_url=env_str(
                "AIFENCE_SOURCE_CODE_URL", "https://github.com/NeuralBinary/AIFENCE",
                legacy=("AGENTDANCE_SOURCE_CODE_URL",),
            ),
            commercial_license_url=env_str(
                "AIFENCE_COMMERCIAL_LICENSE_URL",
                "https://github.com/NeuralBinary/AIFENCE/blob/main/COMMERCIAL-LICENSE.md",
                legacy=("AGENTDANCE_COMMERCIAL_LICENSE_URL",),
            ),
            docs_enabled=env_bool(
                "AIFENCE_DOCS_ENABLED", True,
                legacy=("AGENTDANCE_DOCS_ENABLED", "SAGE_DOCS_ENABLED"),
            ),
            allowed_origins=env_csv("AIFENCE_ALLOWED_ORIGINS", legacy=("AGENTDANCE_ALLOWED_ORIGINS",)),
            allowed_hosts=env_csv("AIFENCE_ALLOWED_HOSTS", legacy=("SAGE_ALLOWED_HOSTS",)),
            max_request_bytes=env_int(
                "AIFENCE_MAX_REQUEST_BYTES", 2 * 1024 * 1024,
                legacy=("AGENTDANCE_MAX_REQUEST_BYTES",),
            ),
            database_url=env_secret(
                "AIFENCE_DATABASE_URL", "sqlite+pysqlite:///./aifence.db",
                legacy=("AGENTDANCE_DATABASE_URL", "SAGE_DATABASE_URL"),
            ),
            db_pool_size=env_int("AIFENCE_DB_POOL_SIZE", 20, legacy=("AGENTDANCE_DB_POOL_SIZE", "SAGE_DB_POOL_SIZE")),
            db_max_overflow=env_int(
                "AIFENCE_DB_MAX_OVERFLOW", 20,
                legacy=("AGENTDANCE_DB_MAX_OVERFLOW", "SAGE_DB_MAX_OVERFLOW"),
            ),
            auto_create_schema=env_bool(
                "AIFENCE_AUTO_CREATE_SCHEMA", True,
                legacy=("AGENTDANCE_AUTO_CREATE_SCHEMA", "SAGE_AUTO_CREATE_SCHEMA"),
            ),
            otel_service_name=env_str(
                "AIFENCE_OTEL_SERVICE_NAME", "aifence", legacy=("AGENTDANCE_OTEL_SERVICE_NAME",)
            ),
            otel_exporter_otlp_endpoint=env_str(
                "AIFENCE_OTEL_EXPORTER_OTLP_ENDPOINT", "",
                legacy=("AGENTDANCE_OTEL_EXPORTER_OTLP_ENDPOINT",),
            ),
            metrics_public=env_bool("AIFENCE_METRICS_PUBLIC", False, legacy=("SAGE_METRICS_PUBLIC",)),
        )
        settings.validate()
        return settings

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    def validate(self) -> None:
        if self.environment not in VALID_ENVIRONMENTS:
            raise ValueError("AIFENCE_ENVIRONMENT has an unsupported value")
        if self.runtime_role not in VALID_RUNTIME_ROLES:
            raise ValueError("AIFENCE_RUNTIME_ROLE has an unsupported value")
        if not 1 <= self.bind_port <= 65535:
            raise ValueError("AIFENCE_BIND_PORT must be between 1 and 65535")
        if self.db_pool_size < 1 or self.db_max_overflow < 0:
            raise ValueError("database pool settings are invalid")
        if self.max_request_bytes < 1024:
            raise ValueError("AIFENCE_MAX_REQUEST_BYTES is too small")
        for label, value in (
            ("AIFENCE_SOURCE_CODE_URL", self.source_code_url),
            ("AIFENCE_COMMERCIAL_LICENSE_URL", self.commercial_license_url),
        ):
            parsed = urlparse(value)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(f"{label} must be an absolute HTTP(S) URL")
