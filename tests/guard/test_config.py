# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from aifence.guard.config import Settings
from aifence.guard.errors import AuthorizationError
from aifence.guard.service import AifenceService


def test_production_configuration_rejects_insecure_database(tmp_path: Path) -> None:
    private = tmp_path / "private.pem"
    public = tmp_path / "public.pem"
    cert = tmp_path / "tls.crt"
    key = tmp_path / "tls.key"
    for path in (private, public, cert, key):
        path.write_text("present")
    settings = Settings(
        environment="production",
        database_url="postgresql+psycopg://db/aifence?sslmode=require",
        auto_create_schema=False,
        public_base_url="https://security.example",
        signing_private_key_file=str(private),
        signing_public_key_file=str(public),
        tls_cert_file=str(cert),
        tls_key_file=str(key),
        master_key_b64=base64.b64encode(bytes.fromhex("11" * 32)).decode(),
        api_key_pepper="p" * 48,
        clamav_required=True,
        docs_enabled=False,
    )
    with pytest.raises(ValueError, match="sslmode=verify-full"):
        settings.validate()


def test_private_broker_endpoint_requires_explicit_allowlist() -> None:
    with pytest.raises(AuthorizationError):
        AifenceService._validate_external_url("https://localhost", ())
    AifenceService._validate_external_url("https://localhost", ("localhost",))


def test_master_keyring_and_pepperring_rotation() -> None:
    old_key = base64.b64encode(bytes.fromhex("11" * 32)).decode()
    new_key = base64.b64encode(bytes.fromhex("22" * 32)).decode()
    settings = Settings(
        environment="test",
        master_key_id="master-v2",
        master_keyring_json=(
            '{"master-v1":"' + old_key + '","master-v2":"' + new_key + '"}'
        ),
        api_key_pepper_id="pepper-v2",
        api_key_pepperring_json='{"pepper-v1":"' + "a" * 48 + '","pepper-v2":"' + "b" * 48 + '"}',
    )
    active, keys = settings.encryption_keyring()
    assert active == "master-v2"
    assert set(keys) == {"master-v1", "master-v2"}
    peppers = settings.accepted_peppers()
    assert peppers[0] == b"b" * 48
    assert b"a" * 48 in peppers


def test_settings_from_env_parses_hardening_fields(monkeypatch, tmp_path) -> None:
    from aifence.guard.config import Settings

    monkeypatch.setenv("AIFENCE_GUARD_ENVIRONMENT", "test")
    monkeypatch.setenv("AIFENCE_GUARD_DATABASE_URL", f"sqlite+pysqlite:///{tmp_path / 'env.db'}")
    monkeypatch.setenv("AIFENCE_GUARD_PROVIDER_ALLOWED_HOSTS", "api.example.com,*.models.example")
    monkeypatch.setenv("AIFENCE_GUARD_TOOL_ALLOWED_HOSTS", "tools.example.com")
    monkeypatch.setenv("AIFENCE_GUARD_DNS_RESOLUTION_TIMEOUT_SECONDS", "4")
    monkeypatch.setenv("AIFENCE_GUARD_MAX_BROKER_RESPONSE_BYTES", "8192")
    monkeypatch.setenv("AIFENCE_GUARD_MAX_PAGE_SIZE", "125")
    monkeypatch.setenv("AIFENCE_GUARD_EXECUTION_LEASE_SECONDS", "90")
    monkeypatch.setenv("AIFENCE_GUARD_ARTIFACT_STORE_PATH", str(tmp_path / "artifacts"))
    monkeypatch.setenv("AIFENCE_GUARD_EXTRA_JSON", '{"deployment":"ci"}')

    settings = Settings.from_env()
    assert settings.environment == "test"
    assert settings.provider_allowed_hosts == ("api.example.com", "*.models.example")
    assert settings.tool_allowed_hosts == ("tools.example.com",)
    assert settings.dns_resolution_timeout_seconds == 4
    assert settings.max_broker_response_bytes == 8192
    assert settings.max_page_size == 125
    assert settings.execution_lease_seconds == 90
    assert settings.extra == {"deployment": "ci"}

    monkeypatch.setenv("AIFENCE_GUARD_EXTRA_JSON", "not-json")
    with pytest.raises(ValueError, match="must be valid JSON"):
        Settings.from_env()


def test_invalid_trusted_proxy_cidr_is_rejected() -> None:
    with pytest.raises(ValueError, match="TRUSTED_PROXY_CIDRS"):
        Settings(environment="test", trusted_proxy_cidrs=("not-a-network",)).validate()


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="uses POSIX-absolute paths (e.g. /var/lib/...) that are not absolute on Windows; validated on Linux CI",
)
def test_external_kms_does_not_require_local_master_key(tmp_path: Path) -> None:
    files = []
    for name in ("signing-private.pem", "signing-public.pem", "tls.crt", "tls.key", "client-ca.crt"):
        path = tmp_path / name
        path.write_text("present")
        files.append(path)
    anchor_public = tmp_path / "anchor-public.pem"
    anchor_public.write_bytes(Ed25519PrivateKey.generate().public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    settings = Settings(
        environment="production",
        database_url="postgresql+psycopg://db/aifence?sslmode=verify-full",
        auto_create_schema=False,
        public_base_url="https://security.example",
        signing_private_key_file=str(files[0]),
        signing_public_key_file=str(files[1]),
        tls_cert_file=str(files[2]),
        tls_key_file=str(files[3]),
        tls_client_ca_file=str(files[4]),
        require_mtls=True,
        trusted_proxy_cidrs=("10.0.0.0/8",),
        internal_cidrs=("10.0.0.0/8",),
        api_key_pepper="p" * 48,
        clamav_required=True,
        docs_enabled=False,
        egress_proxy_url="https://egress.example",
        dispatch_mode="async",
        workload_auth_enabled=True,
        workload_trust_domains=("example.org",),
        signing_backend="vault",
        signing_vault_address="https://vault.example",
        signing_vault_token="s" * 48,
        signing_vault_key_name="aifence-signing",
        policy_rollout_secret="r" * 48,
        kms_backend="aws",
        kms_key_id="arn:aws:kms:us-east-1:123456789012:key/example",
        tenant_key_backend="aws",
        tenant_kms_key_template="arn:aws:kms:us-east-1:123456789012:key/tenant-{tenant_id}",
        tenant_key_destroy_enabled=True,
        audit_anchor_backend="webhook",
        audit_anchor_webhook_url="https://evidence.example/anchors",
        audit_anchor_webhook_verify_url="https://evidence.example/receipts",
        audit_anchor_webhook_public_key_file=str(anchor_public),
        audit_anchor_webhook_key_ids=("anchor-key-v1",),
        audit_anchor_webhook_token="a" * 48,
        artifact_store_backend="s3",
        artifact_store_path="/var/lib/aifence/artifacts",
        artifact_s3_endpoint="https://objects.example",
        artifact_s3_bucket="aifence",
        artifact_s3_kms_key_id="arn:aws:kms:us-east-1:123456789012:key/artifacts",
        artifact_s3_access_key="access",
        artifact_s3_secret_key="secret",
    )
    settings.validate()
