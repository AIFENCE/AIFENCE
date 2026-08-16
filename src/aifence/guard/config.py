# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import ipaddress
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


def _secret_value(value_name: str, file_name: str, default: str = "") -> str:
    direct = os.getenv(value_name)
    if direct is not None:
        return direct
    path = os.getenv(file_name)
    if path:
        return Path(path).read_text(encoding="utf-8").strip()
    return default


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return default if raw is None else int(raw)


def _csv(name: str, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    raw = os.getenv(name)
    if not raw:
        return default
    return tuple(x.strip() for x in raw.split(",") if x.strip())


@dataclass(frozen=True)
class Settings:
    environment: str = "development"
    runtime_role: str = "control-plane"
    bind_host: str = "0.0.0.0"
    bind_port: int = 8080
    public_base_url: str = "http://localhost:8080"
    source_code_url: str = "https://github.com/agentdance/agentdance"
    commercial_license_url: str = "https://github.com/agentdance/agentdance/blob/main/COMMERCIAL-LICENSE.md"
    database_url: str = "sqlite+pysqlite:///./agentdance.db"
    db_pool_size: int = 20
    db_max_overflow: int = 20
    auto_create_schema: bool = True
    signing_private_key_file: str = "./secrets/signing-private.pem"
    signing_public_key_file: str = "./secrets/signing-public.pem"
    signing_key_id: str = "agentdance-signing-v1"
    signing_backend: str = "local"
    signing_vault_address: str = ""
    signing_vault_token: str = ""
    signing_vault_mount: str = "transit"
    signing_vault_key_name: str = "agentdance-signing"
    master_key_b64: str = ""
    master_key_id: str = "master-v1"
    master_keyring_json: str = ""
    api_key_pepper: str = ""
    api_key_pepper_id: str = "pepper-v1"
    api_key_pepperring_json: str = ""
    tls_cert_file: str = ""
    tls_key_file: str = ""
    tls_client_ca_file: str = ""
    require_mtls: bool = False
    trusted_proxy_cidrs: tuple[str, ...] = ()
    internal_cidrs: tuple[str, ...] = ()
    allowed_origins: tuple[str, ...] = ()
    docs_enabled: bool = True
    max_request_bytes: int = 2 * 1024 * 1024
    max_artifact_bytes: int = 10 * 1024 * 1024
    max_broker_response_bytes: int = 4 * 1024 * 1024
    request_timeout_seconds: int = 30
    proxy_timeout_seconds: int = 60
    dns_resolution_timeout_seconds: int = 3
    egress_proxy_url: str = ""
    clamav_host: str = "127.0.0.1"
    clamav_port: int = 3310
    clamav_required: bool = False
    clamav_timeout_seconds: int = 20
    rate_limit_per_minute: int = 600
    audit_retention_days: int = 2555
    artifact_retention_days: int = 30
    artifact_store_path: str = "./data/artifacts"
    artifact_store_backend: str = "file"
    artifact_s3_endpoint: str = ""
    artifact_s3_bucket: str = ""
    artifact_s3_region: str = "us-east-1"
    artifact_s3_access_key: str = ""
    artifact_s3_secret_key: str = ""
    artifact_s3_prefix: str = "agentdance"
    artifact_s3_kms_key_id: str = ""
    artifact_s3_object_lock_days: int = 0
    artifact_s3_delete_enabled: bool = False
    audit_checkpoint_interval: int = 1000
    audit_anchor_backend: str = "file"
    audit_anchor_directory: str = "./data/audit-anchors"
    audit_anchor_webhook_url: str = ""
    audit_anchor_webhook_token: str = ""
    audit_anchor_webhook_verify_url: str = ""
    audit_anchor_webhook_public_key_file: str = ""
    audit_anchor_webhook_key_ids: tuple[str, ...] = ()
    max_page_size: int = 500
    execution_lease_seconds: int = 120
    dispatch_mode: str = "inline"
    dispatch_wait_seconds: float = 3.0
    worker_batch_size: int = 20
    worker_concurrency: int = 8
    worker_lease_renewal_seconds: int = 30
    worker_poll_milliseconds: int = 500
    worker_max_attempts: int = 5
    worker_retry_base_seconds: int = 2
    workload_auth_enabled: bool = False
    workload_trust_domains: tuple[str, ...] = ()
    workload_identity_header: str = "X-Forwarded-Client-Cert"
    workload_identity_direct_header: str = "X-SPIFFE-ID"
    policy_rollout_secret: str = ""
    kms_backend: str = "local"
    kms_key_id: str = ""
    kms_decryption_key_ids: tuple[str, ...] = ()
    tenant_key_backend: str = "local"
    tenant_kms_key_template: str = ""
    tenant_key_destroy_enabled: bool = False
    lifecycle_lease_seconds: int = 300
    lifecycle_poll_milliseconds: int = 1000
    lifecycle_batch_size: int = 10
    lifecycle_max_attempts: int = 5
    anchor_lease_seconds: int = 120
    anchor_poll_milliseconds: int = 1000
    anchor_batch_size: int = 20
    anchor_max_attempts: int = 8
    audit_anchor_required_quorum: int = 1
    audit_anchor_destinations: tuple[str, ...] = ()
    vault_address: str = ""
    vault_token: str = ""
    vault_transit_mount: str = "transit"
    operator_console_enabled: bool = False
    operator_tenant_header: str = "X-Agentdance-Tenant-ID"
    operator_identity_header: str = "X-Auth-Request-Email"
    operator_groups_header: str = "X-Auth-Request-Groups"
    operator_allowed_groups: tuple[str, ...] = ("agentdance-operators",)
    otel_service_name: str = "agentdance"
    otel_exporter_otlp_endpoint: str = ""
    log_level: str = "INFO"
    policy_file: str = ""
    provider_allowed_hosts: tuple[str, ...] = ()
    tool_allowed_hosts: tuple[str, ...] = ()
    shutdown_grace_seconds: int = 30
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> Settings:
        # Accept the unified AIFENCE_GUARD_ prefix, bridging to the historical
        # AGENTDANCE_ names this loader reads. Legacy AGENTDANCE_ still works.
        from ..core.env import apply_legacy_prefix

        apply_legacy_prefix("AIFENCE_GUARD_", "AGENTDANCE_")
        extra_file = os.getenv("AGENTDANCE_EXTRA_JSON_FILE", "").strip()
        if extra_file:
            try:
                extra_raw = Path(extra_file).read_text()
            except OSError as exc:
                raise ValueError("AGENTDANCE_EXTRA_JSON_FILE must reference a readable file") from exc
        else:
            extra_raw = os.getenv("AGENTDANCE_EXTRA_JSON", "{}")
        try:
            extra = json.loads(extra_raw)
        except json.JSONDecodeError as exc:
            raise ValueError("AGENTDANCE_EXTRA_JSON must be valid JSON") from exc
        if not isinstance(extra, dict):
            raise ValueError("AGENTDANCE_EXTRA_JSON must contain a JSON object")
        settings = cls(
            environment=os.getenv("AGENTDANCE_ENVIRONMENT", "development").lower(),
            runtime_role=os.getenv("AGENTDANCE_RUNTIME_ROLE", "control-plane").lower(),
            bind_host=os.getenv("AGENTDANCE_BIND_HOST", "0.0.0.0"),
            bind_port=_int("AGENTDANCE_BIND_PORT", 8080),
            public_base_url=os.getenv("AGENTDANCE_PUBLIC_BASE_URL", "http://localhost:8080"),
            source_code_url=os.getenv("AGENTDANCE_SOURCE_CODE_URL", "https://github.com/agentdance/agentdance"),
            commercial_license_url=os.getenv("AGENTDANCE_COMMERCIAL_LICENSE_URL", "https://github.com/agentdance/agentdance/blob/main/COMMERCIAL-LICENSE.md"),
            database_url=_secret_value(
                "AGENTDANCE_DATABASE_URL", "AGENTDANCE_DATABASE_URL_FILE",
                "sqlite+pysqlite:///./agentdance.db"
            ),
            db_pool_size=_int("AGENTDANCE_DB_POOL_SIZE", 20),
            db_max_overflow=_int("AGENTDANCE_DB_MAX_OVERFLOW", 20),
            auto_create_schema=_bool("AGENTDANCE_AUTO_CREATE_SCHEMA", True),
            signing_private_key_file=os.getenv(
                "AGENTDANCE_SIGNING_PRIVATE_KEY_FILE", "./secrets/signing-private.pem"
            ),
            signing_public_key_file=os.getenv(
                "AGENTDANCE_SIGNING_PUBLIC_KEY_FILE", "./secrets/signing-public.pem"
            ),
            signing_key_id=os.getenv("AGENTDANCE_SIGNING_KEY_ID", "agentdance-signing-v1"),
            signing_backend=os.getenv("AGENTDANCE_SIGNING_BACKEND", "local").lower(),
            signing_vault_address=os.getenv("AGENTDANCE_SIGNING_VAULT_ADDRESS", ""),
            signing_vault_token=_secret_value("AGENTDANCE_SIGNING_VAULT_TOKEN", "AGENTDANCE_SIGNING_VAULT_TOKEN_FILE"),
            signing_vault_mount=os.getenv("AGENTDANCE_SIGNING_VAULT_MOUNT", "transit"),
            signing_vault_key_name=os.getenv("AGENTDANCE_SIGNING_VAULT_KEY_NAME", "agentdance-signing"),
            master_key_b64=_secret_value(
                "AGENTDANCE_MASTER_KEY_B64", "AGENTDANCE_MASTER_KEY_B64_FILE"
            ),
            master_key_id=os.getenv("AGENTDANCE_MASTER_KEY_ID", "master-v1"),
            master_keyring_json=_secret_value(
                "AGENTDANCE_MASTER_KEYRING_JSON", "AGENTDANCE_MASTER_KEYRING_JSON_FILE"
            ),
            api_key_pepper=_secret_value(
                "AGENTDANCE_API_KEY_PEPPER", "AGENTDANCE_API_KEY_PEPPER_FILE"
            ),
            api_key_pepper_id=os.getenv("AGENTDANCE_API_KEY_PEPPER_ID", "pepper-v1"),
            api_key_pepperring_json=_secret_value(
                "AGENTDANCE_API_KEY_PEPPERRING_JSON",
                "AGENTDANCE_API_KEY_PEPPERRING_JSON_FILE",
            ),
            tls_cert_file=os.getenv("AGENTDANCE_TLS_CERT_FILE", ""),
            tls_key_file=os.getenv("AGENTDANCE_TLS_KEY_FILE", ""),
            tls_client_ca_file=os.getenv("AGENTDANCE_TLS_CLIENT_CA_FILE", ""),
            require_mtls=_bool("AGENTDANCE_REQUIRE_MTLS", False),
            trusted_proxy_cidrs=_csv("AGENTDANCE_TRUSTED_PROXY_CIDRS"),
            internal_cidrs=_csv("AGENTDANCE_INTERNAL_CIDRS"),
            allowed_origins=_csv("AGENTDANCE_ALLOWED_ORIGINS"),
            docs_enabled=_bool("AGENTDANCE_DOCS_ENABLED", True),
            max_request_bytes=_int("AGENTDANCE_MAX_REQUEST_BYTES", 2 * 1024 * 1024),
            max_artifact_bytes=_int("AGENTDANCE_MAX_ARTIFACT_BYTES", 10 * 1024 * 1024),
            max_broker_response_bytes=_int("AGENTDANCE_MAX_BROKER_RESPONSE_BYTES", 4 * 1024 * 1024),
            request_timeout_seconds=_int("AGENTDANCE_REQUEST_TIMEOUT_SECONDS", 30),
            proxy_timeout_seconds=_int("AGENTDANCE_PROXY_TIMEOUT_SECONDS", 60),
            dns_resolution_timeout_seconds=_int("AGENTDANCE_DNS_RESOLUTION_TIMEOUT_SECONDS", 3),
            egress_proxy_url=os.getenv("AGENTDANCE_EGRESS_PROXY_URL", ""),
            clamav_host=os.getenv("AGENTDANCE_CLAMAV_HOST", "127.0.0.1"),
            clamav_port=_int("AGENTDANCE_CLAMAV_PORT", 3310),
            clamav_required=_bool("AGENTDANCE_CLAMAV_REQUIRED", False),
            clamav_timeout_seconds=_int("AGENTDANCE_CLAMAV_TIMEOUT_SECONDS", 20),
            rate_limit_per_minute=_int("AGENTDANCE_RATE_LIMIT_PER_MINUTE", 600),
            audit_retention_days=_int("AGENTDANCE_AUDIT_RETENTION_DAYS", 2555),
            artifact_retention_days=_int("AGENTDANCE_ARTIFACT_RETENTION_DAYS", 30),
            artifact_store_path=os.getenv("AGENTDANCE_ARTIFACT_STORE_PATH", "./data/artifacts"),
            artifact_store_backend=os.getenv("AGENTDANCE_ARTIFACT_STORE_BACKEND", "file").lower(),
            artifact_s3_endpoint=os.getenv("AGENTDANCE_ARTIFACT_S3_ENDPOINT", ""),
            artifact_s3_bucket=os.getenv("AGENTDANCE_ARTIFACT_S3_BUCKET", ""),
            artifact_s3_region=os.getenv("AGENTDANCE_ARTIFACT_S3_REGION", "us-east-1"),
            artifact_s3_access_key=_secret_value("AGENTDANCE_ARTIFACT_S3_ACCESS_KEY", "AGENTDANCE_ARTIFACT_S3_ACCESS_KEY_FILE"),
            artifact_s3_secret_key=_secret_value("AGENTDANCE_ARTIFACT_S3_SECRET_KEY", "AGENTDANCE_ARTIFACT_S3_SECRET_KEY_FILE"),
            artifact_s3_prefix=os.getenv("AGENTDANCE_ARTIFACT_S3_PREFIX", "agentdance"),
            artifact_s3_kms_key_id=os.getenv("AGENTDANCE_ARTIFACT_S3_KMS_KEY_ID", ""),
            artifact_s3_object_lock_days=_int("AGENTDANCE_ARTIFACT_S3_OBJECT_LOCK_DAYS", 0),
            artifact_s3_delete_enabled=_bool("AGENTDANCE_ARTIFACT_S3_DELETE_ENABLED", False),
            audit_checkpoint_interval=_int("AGENTDANCE_AUDIT_CHECKPOINT_INTERVAL", 1000),
            audit_anchor_backend=os.getenv("AGENTDANCE_AUDIT_ANCHOR_BACKEND", "file").lower(),
            audit_anchor_directory=os.getenv("AGENTDANCE_AUDIT_ANCHOR_DIRECTORY", "./data/audit-anchors"),
            audit_anchor_webhook_url=os.getenv("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_URL", ""),
            audit_anchor_webhook_token=_secret_value("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_TOKEN", "AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_TOKEN_FILE"),
            audit_anchor_webhook_verify_url=os.getenv("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_VERIFY_URL", ""),
            audit_anchor_webhook_public_key_file=os.getenv("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_PUBLIC_KEY_FILE", ""),
            audit_anchor_webhook_key_ids=_csv("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_KEY_IDS"),
            max_page_size=_int("AGENTDANCE_MAX_PAGE_SIZE", 500),
            execution_lease_seconds=_int("AGENTDANCE_EXECUTION_LEASE_SECONDS", 120),
            dispatch_mode=os.getenv("AGENTDANCE_DISPATCH_MODE", "inline").lower(),
            dispatch_wait_seconds=float(os.getenv("AGENTDANCE_DISPATCH_WAIT_SECONDS", "3")),
            worker_batch_size=_int("AGENTDANCE_WORKER_BATCH_SIZE", 20),
            worker_concurrency=_int("AGENTDANCE_WORKER_CONCURRENCY", 8),
            worker_lease_renewal_seconds=_int("AGENTDANCE_WORKER_LEASE_RENEWAL_SECONDS", 30),
            worker_poll_milliseconds=_int("AGENTDANCE_WORKER_POLL_MILLISECONDS", 500),
            worker_max_attempts=_int("AGENTDANCE_WORKER_MAX_ATTEMPTS", 5),
            worker_retry_base_seconds=_int("AGENTDANCE_WORKER_RETRY_BASE_SECONDS", 2),
            workload_auth_enabled=_bool("AGENTDANCE_WORKLOAD_AUTH_ENABLED", False),
            workload_trust_domains=_csv("AGENTDANCE_WORKLOAD_TRUST_DOMAINS"),
            workload_identity_header=os.getenv("AGENTDANCE_WORKLOAD_IDENTITY_HEADER", "X-Forwarded-Client-Cert"),
            workload_identity_direct_header=os.getenv("AGENTDANCE_WORKLOAD_IDENTITY_DIRECT_HEADER", "X-SPIFFE-ID"),
            policy_rollout_secret=_secret_value("AGENTDANCE_POLICY_ROLLOUT_SECRET", "AGENTDANCE_POLICY_ROLLOUT_SECRET_FILE"),
            kms_backend=os.getenv("AGENTDANCE_KMS_BACKEND", "local").lower(),
            kms_key_id=os.getenv("AGENTDANCE_KMS_KEY_ID", ""),
            kms_decryption_key_ids=_csv("AGENTDANCE_KMS_DECRYPTION_KEY_IDS"),
            tenant_key_backend=os.getenv("AGENTDANCE_TENANT_KEY_BACKEND", os.getenv("AGENTDANCE_KMS_BACKEND", "local")).lower(),
            tenant_kms_key_template=os.getenv("AGENTDANCE_TENANT_KMS_KEY_TEMPLATE", ""),
            tenant_key_destroy_enabled=_bool("AGENTDANCE_TENANT_KEY_DESTROY_ENABLED", False),
            lifecycle_lease_seconds=_int("AGENTDANCE_LIFECYCLE_LEASE_SECONDS", 300),
            lifecycle_poll_milliseconds=_int("AGENTDANCE_LIFECYCLE_POLL_MILLISECONDS", 1000),
            lifecycle_batch_size=_int("AGENTDANCE_LIFECYCLE_BATCH_SIZE", 10),
            lifecycle_max_attempts=_int("AGENTDANCE_LIFECYCLE_MAX_ATTEMPTS", 5),
            anchor_lease_seconds=_int("AGENTDANCE_ANCHOR_LEASE_SECONDS", 120),
            anchor_poll_milliseconds=_int("AGENTDANCE_ANCHOR_POLL_MILLISECONDS", 1000),
            anchor_batch_size=_int("AGENTDANCE_ANCHOR_BATCH_SIZE", 20),
            anchor_max_attempts=_int("AGENTDANCE_ANCHOR_MAX_ATTEMPTS", 8),
            audit_anchor_required_quorum=_int("AGENTDANCE_AUDIT_ANCHOR_REQUIRED_QUORUM", 1),
            audit_anchor_destinations=_csv("AGENTDANCE_AUDIT_ANCHOR_DESTINATIONS"),
            vault_address=os.getenv("AGENTDANCE_VAULT_ADDRESS", ""),
            vault_token=_secret_value("AGENTDANCE_VAULT_TOKEN", "AGENTDANCE_VAULT_TOKEN_FILE"),
            vault_transit_mount=os.getenv("AGENTDANCE_VAULT_TRANSIT_MOUNT", "transit"),
            operator_console_enabled=_bool("AGENTDANCE_OPERATOR_CONSOLE_ENABLED", False),
            operator_tenant_header=os.getenv("AGENTDANCE_OPERATOR_TENANT_HEADER", "X-Agentdance-Tenant-ID"),
            operator_identity_header=os.getenv("AGENTDANCE_OPERATOR_IDENTITY_HEADER", "X-Auth-Request-Email"),
            operator_groups_header=os.getenv("AGENTDANCE_OPERATOR_GROUPS_HEADER", "X-Auth-Request-Groups"),
            operator_allowed_groups=_csv("AGENTDANCE_OPERATOR_ALLOWED_GROUPS", ("agentdance-operators",)),
            otel_service_name=os.getenv("AGENTDANCE_OTEL_SERVICE_NAME", "agentdance"),
            otel_exporter_otlp_endpoint=os.getenv(
                "AGENTDANCE_OTEL_EXPORTER_OTLP_ENDPOINT", ""
            ),
            log_level=os.getenv("AGENTDANCE_LOG_LEVEL", "INFO").upper(),
            policy_file=os.getenv("AGENTDANCE_POLICY_FILE", ""),
            provider_allowed_hosts=_csv("AGENTDANCE_PROVIDER_ALLOWED_HOSTS"),
            tool_allowed_hosts=_csv("AGENTDANCE_TOOL_ALLOWED_HOSTS"),
            shutdown_grace_seconds=_int("AGENTDANCE_SHUTDOWN_GRACE_SECONDS", 30),
            extra=extra,
        )
        settings.validate()
        return settings

    @staticmethod
    def _decode_master_key(value: str, label: str) -> bytes:
        try:
            key = base64.b64decode(value, validate=True)
        except Exception as exc:
            raise ValueError(f"{label} must be standard base64") from exc
        if len(key) != 32:
            raise ValueError(f"{label} must decode to exactly 32 bytes")
        return key

    def encryption_keyring(self) -> tuple[str, dict[str, bytes]]:
        active_id = self.master_key_id.strip()
        if not active_id or len(active_id.encode("utf-8")) > 255:
            raise ValueError("AGENTDANCE_MASTER_KEY_ID must contain 1 to 255 UTF-8 bytes")
        keys: dict[str, bytes] = {}
        if self.master_keyring_json:
            try:
                document = json.loads(self.master_keyring_json)
            except json.JSONDecodeError as exc:
                raise ValueError("AGENTDANCE_MASTER_KEYRING_JSON must be valid JSON") from exc
            if not isinstance(document, dict) or not document:
                raise ValueError("AGENTDANCE_MASTER_KEYRING_JSON must be a non-empty object")
            for key_id, encoded in document.items():
                if not isinstance(key_id, str) or not key_id or len(key_id.encode("utf-8")) > 255:
                    raise ValueError("master keyring identifiers must contain 1 to 255 UTF-8 bytes")
                if not isinstance(encoded, str):
                    raise ValueError("master keyring values must be base64 strings")
                keys[key_id] = self._decode_master_key(encoded, f"master key {key_id}")
        if self.master_key_b64:
            decoded = self._decode_master_key(self.master_key_b64, "AGENTDANCE_MASTER_KEY_B64")
            existing = keys.get(active_id)
            if existing is not None and existing != decoded:
                raise ValueError("active master key conflicts with the same keyring identifier")
            keys[active_id] = decoded
        if not keys:
            if self.environment == "production":
                raise ValueError("an AGENTDANCE master encryption key is required in production")
            keys[active_id] = bytes.fromhex("1f" * 32)
        if active_id not in keys:
            raise ValueError("AGENTDANCE_MASTER_KEY_ID is not present in the configured keyring")
        return active_id, keys

    def master_key(self) -> bytes:
        active_id, keys = self.encryption_keyring()
        return keys[active_id]

    def peppers(self) -> tuple[str, dict[str, bytes]]:
        active_id = self.api_key_pepper_id.strip()
        if not active_id or len(active_id.encode("utf-8")) > 255:
            raise ValueError("AGENTDANCE_API_KEY_PEPPER_ID must contain 1 to 255 UTF-8 bytes")
        values: dict[str, bytes] = {}
        if self.api_key_pepperring_json:
            try:
                document = json.loads(self.api_key_pepperring_json)
            except json.JSONDecodeError as exc:
                raise ValueError("AGENTDANCE_API_KEY_PEPPERRING_JSON must be valid JSON") from exc
            if not isinstance(document, dict) or not document:
                raise ValueError("AGENTDANCE_API_KEY_PEPPERRING_JSON must be a non-empty object")
            for pepper_id, value in document.items():
                if not isinstance(pepper_id, str) or not pepper_id:
                    raise ValueError("API key pepper identifiers must be non-empty strings")
                if not isinstance(value, str) or len(value.encode("utf-8")) < 32:
                    raise ValueError("every API key pepper must contain at least 32 bytes")
                values[pepper_id] = value.encode("utf-8")
        if self.api_key_pepper:
            encoded = self.api_key_pepper.encode("utf-8")
            if len(encoded) < 32:
                raise ValueError("AGENTDANCE_API_KEY_PEPPER must contain at least 32 bytes")
            existing = values.get(active_id)
            if existing is not None and existing != encoded:
                raise ValueError("active API key pepper conflicts with its pepperring value")
            values[active_id] = encoded
        if not values:
            if self.environment == "production":
                raise ValueError("an AGENTDANCE API key pepper is required in production")
            values[active_id] = b"development-only-pepper-change-before-production"
        if active_id not in values:
            raise ValueError("AGENTDANCE_API_KEY_PEPPER_ID is not present in the configured pepperring")
        return active_id, values

    def pepper(self) -> bytes:
        active_id, values = self.peppers()
        return values[active_id]

    def accepted_peppers(self) -> tuple[bytes, ...]:
        active_id, values = self.peppers()
        return (values[active_id], *(value for key_id, value in values.items() if key_id != active_id))

    def validate(self) -> None:
        if self.environment not in {"development", "test", "staging", "production"}:
            raise ValueError("AGENTDANCE_ENVIRONMENT has an unsupported value")
        if self.runtime_role not in {"control-plane", "dispatcher", "lifecycle", "anchor", "migration", "maintenance"}:
            raise ValueError("AGENTDANCE_RUNTIME_ROLE has an unsupported value")
        if self.bind_port < 1 or self.bind_port > 65535:
            raise ValueError("AGENTDANCE_BIND_PORT must be between 1 and 65535")
        for label, value in (("AGENTDANCE_SOURCE_CODE_URL", self.source_code_url), ("AGENTDANCE_COMMERCIAL_LICENSE_URL", self.commercial_license_url)):
            parsed = urlparse(value)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(f"{label} must be an absolute HTTP(S) URL")
        if self.max_request_bytes < 1024:
            raise ValueError("AGENTDANCE_MAX_REQUEST_BYTES is too small")
        if self.max_artifact_bytes < 1024:
            raise ValueError("AGENTDANCE_MAX_ARTIFACT_BYTES is too small")
        if self.max_broker_response_bytes < 1024:
            raise ValueError("AGENTDANCE_MAX_BROKER_RESPONSE_BYTES is too small")
        if self.audit_checkpoint_interval < 1:
            raise ValueError("AGENTDANCE_AUDIT_CHECKPOINT_INTERVAL must be positive")
        if not 1 <= self.max_page_size <= 5000:
            raise ValueError("AGENTDANCE_MAX_PAGE_SIZE is outside the supported range")
        if not 30 <= self.execution_lease_seconds <= 3600:
            raise ValueError("AGENTDANCE_EXECUTION_LEASE_SECONDS must be between 30 and 3600")
        if self.db_pool_size < 1 or self.db_max_overflow < 0:
            raise ValueError("database pool settings are invalid")
        if not 1 <= self.rate_limit_per_minute <= 1_000_000:
            raise ValueError("AGENTDANCE_RATE_LIMIT_PER_MINUTE is outside the supported range")
        if not 1 <= self.proxy_timeout_seconds <= 600:
            raise ValueError("AGENTDANCE_PROXY_TIMEOUT_SECONDS is outside the supported range")
        if not 1 <= self.dns_resolution_timeout_seconds <= 30:
            raise ValueError("AGENTDANCE_DNS_RESOLUTION_TIMEOUT_SECONDS is outside the supported range")
        if self.audit_retention_days < 1 or self.artifact_retention_days < 1:
            raise ValueError("retention periods must be positive")
        if self.dispatch_mode not in {"inline", "async", "hybrid"}:
            raise ValueError("AGENTDANCE_DISPATCH_MODE must be inline, async, or hybrid")
        if not 1 <= self.worker_batch_size <= 1000 or not 1 <= self.worker_max_attempts <= 100:
            raise ValueError("worker batch or retry settings are outside the supported range")
        if not 1 <= self.worker_concurrency <= 256:
            raise ValueError("AGENTDANCE_WORKER_CONCURRENCY must be between 1 and 256")
        if not 5 <= self.worker_lease_renewal_seconds < self.execution_lease_seconds:
            raise ValueError("lease renewal must be at least 5 seconds and shorter than the execution lease")
        if not 50 <= self.worker_poll_milliseconds <= 60_000:
            raise ValueError("worker polling interval is outside the supported range")
        if self.kms_backend not in {"local", "aws", "gcp", "azure", "vault"}:
            raise ValueError("AGENTDANCE_KMS_BACKEND is unsupported")
        if self.tenant_key_backend not in {"local", "aws", "gcp", "azure", "vault"}:
            raise ValueError("AGENTDANCE_TENANT_KEY_BACKEND is unsupported")
        if not 30 <= self.lifecycle_lease_seconds <= 7200 or not 1 <= self.lifecycle_batch_size <= 100:
            raise ValueError("tenant lifecycle worker settings are outside the supported range")
        if not 30 <= self.anchor_lease_seconds <= 3600 or not 1 <= self.anchor_batch_size <= 1000:
            raise ValueError("audit anchor worker settings are outside the supported range")
        if self.audit_anchor_required_quorum < 1:
            raise ValueError("audit anchor quorum must be positive")
        if self.signing_backend not in {"local", "vault"}:
            raise ValueError("AGENTDANCE_SIGNING_BACKEND is unsupported")
        if self.artifact_store_backend not in {"file", "s3"}:
            raise ValueError("AGENTDANCE_ARTIFACT_STORE_BACKEND is unsupported")
        if self.audit_anchor_backend not in {"file", "webhook"}:
            raise ValueError("AGENTDANCE_AUDIT_ANCHOR_BACKEND is unsupported")
        for label, cidrs in (
            ("AGENTDANCE_TRUSTED_PROXY_CIDRS", self.trusted_proxy_cidrs),
            ("AGENTDANCE_INTERNAL_CIDRS", self.internal_cidrs),
        ):
            for cidr in cidrs:
                try:
                    ipaddress.ip_network(cidr, strict=False)
                except ValueError as exc:
                    raise ValueError(f"{label} contains invalid CIDR: {cidr}") from exc
        if self.operator_console_enabled:
            if not self.trusted_proxy_cidrs:
                raise ValueError("operator console requires trusted proxy CIDRs")
            if not self.operator_allowed_groups:
                raise ValueError("operator console requires at least one allowed group")
            for header in (self.operator_tenant_header, self.operator_identity_header, self.operator_groups_header):
                if not header or "\n" in header or "\r" in header:
                    raise ValueError("operator proxy header names are invalid")
        if self.environment == "production" and self.runtime_role in {"lifecycle", "anchor"}:
            failures: list[str] = []
            if not self.database_url.startswith("postgresql+psycopg://"):
                failures.append(f"{self.runtime_role} worker requires PostgreSQL")
            db_query = parse_qs(urlparse(self.database_url).query)
            if db_query.get("sslmode", [""])[0].lower() != "verify-full":
                failures.append(f"{self.runtime_role} worker PostgreSQL requires sslmode=verify-full")
            if self.auto_create_schema:
                failures.append(f"{self.runtime_role} worker cannot auto-create schema")
            if not self.internal_cidrs:
                failures.append("AGENTDANCE_INTERNAL_CIDRS is required")
            if self.signing_backend == "local":
                failures.append(f"{self.runtime_role} worker requires non-exportable signing")
            if self.runtime_role == "lifecycle":
                if self.artifact_store_backend != "s3":
                    failures.append("lifecycle worker requires S3 evidence storage")
                if self.tenant_key_backend == "local" or "{tenant_id}" not in self.tenant_kms_key_template:
                    failures.append("lifecycle worker requires a tenant-dedicated external KMS key template")
                if not self.tenant_key_destroy_enabled:
                    failures.append("lifecycle worker requires explicit tenant key destruction enablement")
            if self.runtime_role == "anchor":
                if self.audit_anchor_backend != "webhook":
                    failures.append("anchor worker requires independent webhook destinations")
                if not self.audit_anchor_destinations:
                    failures.append("anchor worker requires named audit anchor destinations")
                if self.audit_anchor_required_quorum > len(self.audit_anchor_destinations):
                    failures.append("anchor quorum exceeds configured destinations")
            if failures:
                raise ValueError(f"invalid {self.runtime_role} configuration: " + "; ".join(failures))
            return

        if self.environment == "production" and self.runtime_role == "dispatcher":
            failures: list[str] = []
            if not self.internal_cidrs:
                failures.append("AGENTDANCE_INTERNAL_CIDRS is required")
            if not self.database_url.startswith("postgresql+psycopg://"):
                failures.append("dispatcher requires PostgreSQL")
            db_query = parse_qs(urlparse(self.database_url).query)
            if db_query.get("sslmode", [""])[0].lower() != "verify-full":
                failures.append("dispatcher PostgreSQL requires sslmode=verify-full")
            if self.auto_create_schema:
                failures.append("dispatcher cannot auto-create schema")
            if self.dispatch_mode != "async":
                failures.append("dispatcher runtime requires async dispatch mode")
            if self.kms_backend == "local" or not self.kms_key_id:
                failures.append("dispatcher requires an external KMS")
            if self.signing_backend == "local":
                failures.append("dispatcher requires a non-exportable signing backend")
            signing_vault_url = urlparse(self.signing_vault_address or self.vault_address)
            if (signing_vault_url.scheme.lower() != "https" or not signing_vault_url.hostname
                    or signing_vault_url.username is not None or signing_vault_url.password is not None
                    or signing_vault_url.query or signing_vault_url.fragment):
                failures.append("dispatcher Vault signing address must be canonical HTTPS")
            if not (self.signing_vault_token or self.vault_token):
                failures.append("dispatcher Vault signing requires a token")
            proxy_url = urlparse(self.egress_proxy_url)
            if (proxy_url.scheme.lower() not in {"http", "https"} or not proxy_url.hostname
                    or proxy_url.username is not None or proxy_url.password is not None
                    or proxy_url.query or proxy_url.fragment):
                failures.append("dispatcher requires a canonical controlled egress proxy URL")
            if any(pattern in {"*", "*.*"} for pattern in (*self.provider_allowed_hosts, *self.tool_allowed_hosts)):
                failures.append("dispatcher host allowlists cannot contain global wildcards")
            if failures:
                raise ValueError("invalid dispatcher configuration: " + "; ".join(failures))
            return

        if self.environment == "production":
            failures: list[str] = []
            if not self.internal_cidrs:
                failures.append("AGENTDANCE_INTERNAL_CIDRS is required")
            if not self.database_url.startswith("postgresql+psycopg://"):
                failures.append("production requires PostgreSQL through postgresql+psycopg://")
            db_query = parse_qs(urlparse(self.database_url).query)
            sslmode = db_query.get("sslmode", [""])[0].lower()
            if sslmode != "verify-full":
                failures.append("production PostgreSQL requires sslmode=verify-full")
            if self.auto_create_schema:
                failures.append("AGENTDANCE_AUTO_CREATE_SCHEMA must be false")
            public_url = urlparse(self.public_base_url)
            if (
                public_url.scheme.lower() != "https"
                or not public_url.hostname
                or public_url.username is not None
                or public_url.password is not None
                or public_url.query
                or public_url.fragment
            ):
                failures.append(
                    "AGENTDANCE_PUBLIC_BASE_URL must be a canonical HTTPS origin without credentials, query, or fragment"
                )
            for label, value in (
                ("AGENTDANCE_TLS_CERT_FILE", self.tls_cert_file),
                ("AGENTDANCE_TLS_KEY_FILE", self.tls_key_file),
            ):
                if not value or not Path(value).is_file():
                    failures.append(f"{label} must reference a readable file")
            if self.signing_backend == "local":
                failures.append("production requires a non-exportable signing backend")
            else:
                signing_vault_url = urlparse(self.signing_vault_address or self.vault_address)
                if (signing_vault_url.scheme.lower() != "https" or not signing_vault_url.hostname
                        or signing_vault_url.username is not None or signing_vault_url.password is not None
                        or signing_vault_url.query or signing_vault_url.fragment):
                    failures.append("Vault signing requires a canonical HTTPS address")
                if not (self.signing_vault_token or self.vault_token):
                    failures.append("Vault signing requires a token")
                if not self.signing_vault_key_name:
                    failures.append("Vault signing requires a key name")
            if not self.require_mtls:
                failures.append("AGENTDANCE_REQUIRE_MTLS must be true in production")
            if not self.tls_client_ca_file or not Path(self.tls_client_ca_file).is_file():
                failures.append("production mTLS requires AGENTDANCE_TLS_CLIENT_CA_FILE")
            if not Path(self.artifact_store_path).is_absolute():
                failures.append("AGENTDANCE_ARTIFACT_STORE_PATH must be absolute")
            proxy_url = urlparse(self.egress_proxy_url)
            if (
                proxy_url.scheme.lower() not in {"http", "https"}
                or not proxy_url.hostname
                or proxy_url.username is not None
                or proxy_url.password is not None
                or proxy_url.query
                or proxy_url.fragment
            ):
                failures.append(
                    "AGENTDANCE_EGRESS_PROXY_URL must be an HTTP(S) proxy URL without embedded credentials, query, or fragment"
                )
            if not self.clamav_required:
                failures.append("AGENTDANCE_CLAMAV_REQUIRED must be true")
            if "*" in self.allowed_origins:
                failures.append("wildcard CORS is prohibited")
            if self.docs_enabled:
                failures.append("interactive API docs must be disabled")
            for label, patterns in (
                ("AGENTDANCE_PROVIDER_ALLOWED_HOSTS", self.provider_allowed_hosts),
                ("AGENTDANCE_TOOL_ALLOWED_HOSTS", self.tool_allowed_hosts),
            ):
                if any(pattern in {"*", "*.*"} for pattern in patterns):
                    failures.append(f"{label} cannot contain a global wildcard")
            if self.policy_file and not Path(self.policy_file).is_file():
                failures.append("AGENTDANCE_POLICY_FILE must reference a readable file")
            if self.dispatch_mode == "inline":
                failures.append("production requires async or hybrid durable dispatch")
            if not self.workload_auth_enabled or not self.workload_trust_domains:
                failures.append("production requires SPIFFE workload authentication and trust domains")
            if not self.trusted_proxy_cidrs:
                failures.append("production workload authentication requires AGENTDANCE_TRUSTED_PROXY_CIDRS")
            if self.kms_backend == "local" or not self.kms_key_id:
                failures.append("production requires a configured external KMS backend")
            if self.tenant_key_backend == "local" or "{tenant_id}" not in self.tenant_kms_key_template:
                failures.append("production requires tenant-dedicated external KMS key routing")
            if not self.tenant_key_destroy_enabled:
                failures.append("production requires explicit tenant key destruction enablement")
            if not self.policy_rollout_secret or len(self.policy_rollout_secret.encode("utf-8")) < 32:
                failures.append("AGENTDANCE_POLICY_ROLLOUT_SECRET must contain at least 32 bytes")
            if self.audit_anchor_backend == "file":
                failures.append("production requires an independent webhook audit anchor backend")
            else:
                anchor_url = urlparse(self.audit_anchor_webhook_url)
                if (anchor_url.scheme.lower() != "https" or not anchor_url.hostname
                        or anchor_url.username is not None or anchor_url.password is not None
                        or anchor_url.query or anchor_url.fragment):
                    failures.append("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_URL must be a canonical HTTPS URL")
                if len(self.audit_anchor_webhook_token.encode("utf-8")) < 32:
                    failures.append("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_TOKEN must contain at least 32 bytes")
                verify_url = urlparse(self.audit_anchor_webhook_verify_url)
                if (verify_url.scheme.lower() != "https" or not verify_url.hostname
                        or verify_url.username is not None or verify_url.password is not None
                        or verify_url.query or verify_url.fragment or "{" in verify_url.path or "}" in verify_url.path):
                    failures.append("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_VERIFY_URL must be canonical HTTPS")
                if not self.audit_anchor_webhook_public_key_file or not Path(self.audit_anchor_webhook_public_key_file).is_file():
                    failures.append("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_PUBLIC_KEY_FILE must reference a readable key")
                if not self.audit_anchor_webhook_key_ids:
                    failures.append("AGENTDANCE_AUDIT_ANCHOR_WEBHOOK_KEY_IDS must allow at least one receipt key")
            if self.artifact_store_backend != "s3":
                failures.append("production requires S3-compatible external artifact storage")
            else:
                s3_url = urlparse(self.artifact_s3_endpoint)
                if (s3_url.scheme.lower() != "https" or not s3_url.hostname
                        or s3_url.username is not None or s3_url.password is not None
                        or s3_url.query or s3_url.fragment):
                    failures.append("AGENTDANCE_ARTIFACT_S3_ENDPOINT must be a canonical HTTPS origin")
                if not self.artifact_s3_bucket:
                    failures.append("S3 artifact storage requires AGENTDANCE_ARTIFACT_S3_BUCKET")
                if bool(self.artifact_s3_access_key) != bool(self.artifact_s3_secret_key):
                    failures.append("S3 static credentials must be provided as a complete pair")
                if not self.artifact_s3_kms_key_id:
                    failures.append("production S3 artifact storage requires AGENTDANCE_ARTIFACT_S3_KMS_KEY_ID")
                if self.artifact_s3_delete_enabled:
                    failures.append("production S3 artifact deletion must be disabled for immutable evidence")
            if self.kms_backend == "vault":
                vault_url = urlparse(self.vault_address)
                if (vault_url.scheme.lower() != "https" or not vault_url.hostname
                        or vault_url.username is not None or vault_url.password is not None
                        or vault_url.query or vault_url.fragment):
                    failures.append("AGENTDANCE_VAULT_ADDRESS must be a canonical HTTPS origin")
                if not self.vault_token:
                    failures.append("Vault KMS requires AGENTDANCE_VAULT_TOKEN")
            try:
                if self.kms_backend == "local":
                    self.encryption_keyring()
                self.peppers()
            except ValueError as exc:
                failures.append(str(exc))
            if failures:
                raise ValueError("invalid production configuration: " + "; ".join(failures))
