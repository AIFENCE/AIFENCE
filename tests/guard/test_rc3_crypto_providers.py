# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from aifence.guard.config import Settings
from aifence.guard.crypto import (
    SigningKey,
    VaultTransitSigningKey,
    build_signing_provider,
    generate_key_files,
)
from aifence.guard.key_management import (
    AWSKMSProvider,
    AzureKeyVaultProvider,
    GCPKMSProvider,
    VaultTransitProvider,
    build_managed_cipher,
)


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self._payload


def test_vault_transit_signer_issues_and_verifies_tokens(monkeypatch) -> None:
    private = Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")

    class FakeClient:
        def __init__(self, **kwargs) -> None:
            assert kwargs["verify"] is True
            assert kwargs["follow_redirects"] is False
            assert kwargs["trust_env"] is False

        def get(self, url: str, *, headers: dict[str, str]):
            assert url.endswith("/v1/transit/keys/aifence-signing")
            assert headers == {"X-Vault-Token": "vault-token"}
            return _Response({"data": {"latest_version": 2, "keys": {"2": {"public_key": public_pem}}}})

        def post(self, url: str, *, headers: dict[str, str], json: dict[str, object]):
            assert url.endswith("/v1/transit/sign/aifence-signing")
            assert headers == {"X-Vault-Token": "vault-token"}
            raw = base64.b64decode(str(json["input"]), validate=True)
            signature = base64.b64encode(private.sign(raw)).decode("ascii")
            return _Response({"data": {"signature": f"vault:v2:{signature}"}})

    monkeypatch.setattr("httpx.Client", FakeClient)
    signer = VaultTransitSigningKey(
        address="https://vault.example/",
        token="vault-token",
        mount="/transit/",
        key_name="aifence-signing",
        key_id="vault-signing-v2",
    )
    signature = signer.sign(b"message")
    assert signer.verify(b"message", signature)
    assert not signer.verify(b"tampered", signature)
    token = signer.issue_token(
        {"sub": "dec_1", "aud": "aifence-decision"},
        headers={"cty": "decision"},
        lifetime_seconds=60,
    )
    claims = signer.verify_token(token, audience="aifence-decision")
    assert claims["sub"] == "dec_1"
    receipt = signer.issue_receipt({"sub": "receipt_1", "aud": "aifence-receipt"})
    assert signer.verify_receipt(receipt, audience="aifence-receipt")["sub"] == "receipt_1"
    assert signer.public_pem() == public_pem

    with pytest.raises(ValueError, match="requires HTTPS"):
        VaultTransitSigningKey(
            address="http://vault.example",
            token="vault-token",
            mount="transit",
            key_name="aifence-signing",
            key_id="bad",
        )


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="asserts POSIX 0o600/0o644 file-mode bits, which Windows does not implement; validated on Linux CI",
)
def test_signing_provider_factory_and_key_file_lifecycle(tmp_path: Path, monkeypatch) -> None:
    private_file, public_file = generate_key_files(tmp_path / "keys")
    assert private_file.stat().st_mode & 0o777 == 0o600
    assert public_file.stat().st_mode & 0o777 == 0o644
    with pytest.raises(FileExistsError):
        generate_key_files(tmp_path / "keys")

    local = build_signing_provider(Settings(
        signing_backend="local",
        signing_private_key_file=str(private_file),
        signing_public_key_file=str(public_file),
        signing_key_id="local-v1",
    ))
    assert isinstance(local, SigningKey)
    assert local.verify(b"payload", local.sign(b"payload"))

    captured: dict[str, str] = {}

    class FakeVaultSigner:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    monkeypatch.setattr("aifence.guard.crypto.VaultTransitSigningKey", FakeVaultSigner)
    result = build_signing_provider(Settings(
        signing_backend="vault",
        signing_key_id="vault-v1",
        signing_vault_address="https://vault.example",
        signing_vault_token="token",
        signing_vault_mount="signing",
        signing_vault_key_name="aifence",
    ))
    assert isinstance(result, FakeVaultSigner)
    assert captured == {
        "address": "https://vault.example",
        "token": "token",
        "mount": "signing",
        "key_name": "aifence",
        "key_id": "vault-v1",
    }
    with pytest.raises(ValueError, match="unsupported signing backend"):
        build_signing_provider(Settings(signing_backend="unsupported"))


def test_cloud_kms_provider_adapters_use_authenticated_context(monkeypatch) -> None:
    context = b"tenant:artifact"
    plaintext = b"k" * 32

    class FakeAWSClient:
        def encrypt(self, **kwargs):
            assert kwargs["EncryptionContext"]["aifence_guard_context"] == base64.urlsafe_b64encode(context).decode()
            return {"CiphertextBlob": b"aws:" + kwargs["Plaintext"]}

        def decrypt(self, **kwargs):
            return {"Plaintext": kwargs["CiphertextBlob"].removeprefix(b"aws:")}

    boto3 = types.ModuleType("boto3")
    boto3.client = lambda service, region_name=None: FakeAWSClient()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "boto3", boto3)
    aws = AWSKMSProvider("arn:aws:kms:us-east-1:123:key/abc", "us-east-1")
    assert aws.unwrap(aws.wrap(plaintext, context=context), context=context) == plaintext

    class FakeGCPClient:
        def encrypt(self, *, request):
            assert request["additional_authenticated_data"] == context
            return SimpleNamespace(ciphertext=b"gcp:" + request["plaintext"])

        def decrypt(self, *, request):
            return SimpleNamespace(plaintext=request["ciphertext"].removeprefix(b"gcp:"))

    google = types.ModuleType("google")
    cloud = types.ModuleType("google.cloud")
    kms_v1 = types.ModuleType("google.cloud.kms_v1")
    kms_v1.KeyManagementServiceClient = FakeGCPClient  # type: ignore[attr-defined]
    cloud.kms_v1 = kms_v1  # type: ignore[attr-defined]
    google.cloud = cloud  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.cloud", cloud)
    monkeypatch.setitem(sys.modules, "google.cloud.kms_v1", kms_v1)
    gcp = GCPKMSProvider("projects/p/locations/l/keyRings/r/cryptoKeys/k")
    assert gcp.unwrap(gcp.wrap(plaintext, context=context), context=context) == plaintext

    class FakeAzureCrypto:
        def wrap_key(self, algorithm, key):
            assert algorithm == "rsa-oaep-256"
            return SimpleNamespace(encrypted_key=b"azure:" + key)

        def unwrap_key(self, algorithm, wrapped):
            assert algorithm == "rsa-oaep-256"
            return SimpleNamespace(key=wrapped.removeprefix(b"azure:"))

    azure = types.ModuleType("azure")
    identity = types.ModuleType("azure.identity")
    identity.DefaultAzureCredential = lambda: object()  # type: ignore[attr-defined]
    keyvault = types.ModuleType("azure.keyvault")
    keys = types.ModuleType("azure.keyvault.keys")
    crypto = types.ModuleType("azure.keyvault.keys.crypto")
    crypto.CryptographyClient = lambda key_id, credential: FakeAzureCrypto()  # type: ignore[attr-defined]
    crypto.KeyWrapAlgorithm = SimpleNamespace(rsa_oaep_256="rsa-oaep-256")  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "azure", azure)
    monkeypatch.setitem(sys.modules, "azure.identity", identity)
    monkeypatch.setitem(sys.modules, "azure.keyvault", keyvault)
    monkeypatch.setitem(sys.modules, "azure.keyvault.keys", keys)
    monkeypatch.setitem(sys.modules, "azure.keyvault.keys.crypto", crypto)
    azure_provider = AzureKeyVaultProvider("https://vault.example/keys/key/version")
    assert azure_provider.unwrap(
        azure_provider.wrap(plaintext, context=context), context=context
    ) == plaintext


def test_vault_kms_and_managed_cipher_factory(monkeypatch) -> None:
    wrapped_keys: dict[str, bytes] = {}

    class FakeClient:
        def __init__(self, **kwargs) -> None:
            assert kwargs["trust_env"] is False

        def post(self, url: str, *, headers: dict[str, str], json: dict[str, str]):
            assert headers == {"X-Vault-Token": "token"}
            if "/encrypt/" in url:
                key = base64.b64decode(json["plaintext"], validate=True)
                ciphertext = f"vault:v1:{base64.b64encode(key).decode()}"
                wrapped_keys[ciphertext] = key
                return _Response({"data": {"ciphertext": ciphertext}})
            key = wrapped_keys[json["ciphertext"]]
            return _Response({"data": {"plaintext": base64.b64encode(key).decode()}})

    monkeypatch.setattr("aifence.guard.key_management.httpx.Client", FakeClient)
    provider = VaultTransitProvider("active", "https://vault.example/", "token", "/transit/")
    assert provider.base == "https://vault.example/v1/transit"
    wrapped = provider.wrap(b"z" * 32, context=b"tenant")
    assert provider.unwrap(wrapped, context=b"tenant") == b"z" * 32
    with pytest.raises(ValueError, match="requires HTTPS"):
        VaultTransitProvider("bad", "http://vault.example", "token")

    settings = Settings(
        kms_backend="vault",
        kms_key_id="active",
        kms_decryption_key_ids=("historical", "active"),
        vault_address="https://vault.example",
        vault_token="token",
        vault_transit_mount="transit",
    )
    cipher = build_managed_cipher(settings)
    assert cipher.approved_key_ids == frozenset({"active", "historical"})
    encrypted = cipher.encrypt(b"secret", context=b"tenant:artifact")
    assert cipher.decrypt(encrypted, context=b"tenant:artifact") == b"secret"


def test_tenant_external_key_route_rotation_and_retirement(monkeypatch) -> None:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from aifence.guard.crypto import EnvelopeCipher
    from aifence.guard.db import Base
    from aifence.guard.tenant_crypto import TenantCryptography

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    settings = Settings(
        environment="test",
        tenant_key_backend="aws",
        tenant_kms_key_template="arn:aws:kms:us-east-1:123456789012:key/{tenant_id}",
    )
    root = EnvelopeCipher(active_key_id="root-v1", keyring={"root-v1": bytes.fromhex("11" * 32)})
    crypto = TenantCryptography(root, settings)
    wrapped_keys: dict[tuple[str, bytes], bytes] = {}
    destroyed: list[str] = []

    class FakeProvider:
        def __init__(self, key_id: str) -> None:
            self.key_id = key_id

        def wrap(self, plaintext_key: bytes, *, context: bytes) -> bytes:
            token = f"wrapped:{self.key_id}:{len(wrapped_keys)}".encode()
            wrapped_keys[(self.key_id, token)] = plaintext_key
            return token

        def unwrap(self, wrapped_key: bytes, *, context: bytes) -> bytes:
            del context
            return wrapped_keys[(self.key_id, wrapped_key)]

        def destroy(self, *, reason: str) -> dict[str, str]:
            destroyed.append(self.key_id)
            return {"backend": "aws", "key_id": self.key_id, "reason": reason}

    monkeypatch.setattr(
        crypto, "_provider", lambda key_id, backend=None: FakeProvider(key_id)
    )

    with Session(engine) as session:
        tenant_id = "ten_rotation_test"
        old_route = crypto.ensure_route(session, tenant_id)
        old_key_id = old_route.key_id
        old_ciphertext = crypto.encrypt(session, tenant_id, b"before", context=b"ctx")
        assert crypto.envelope_key_id(old_ciphertext) == old_key_id

        new_key_id = "arn:aws:kms:us-east-1:123456789012:key/rotated"
        route = crypto.rotate_route(session, tenant_id, new_key_id=new_key_id)
        assert route.key_id == new_key_id
        assert route.historical_key_ids == [old_key_id]
        assert crypto.decrypt(session, tenant_id, old_ciphertext, context=b"ctx") == b"before"

        new_ciphertext = crypto.encrypt(session, tenant_id, b"after", context=b"ctx")
        assert crypto.envelope_key_id(new_ciphertext) == new_key_id
        assert crypto.decrypt(session, tenant_id, new_ciphertext, context=b"ctx") == b"after"

        with pytest.raises(ValueError, match="active tenant key"):
            crypto.retire_historical_key(session, tenant_id, key_id=new_key_id)
        crypto.retire_historical_key(session, tenant_id, key_id=old_key_id)
        with pytest.raises(PermissionError, match="unapproved key route"):
            crypto.decrypt(session, tenant_id, old_ciphertext, context=b"ctx")

        second_key_id = "arn:aws:kms:us-east-1:123456789012:key/rotated-again"
        crypto.rotate_route(session, tenant_id, new_key_id=second_key_id)
        receipt = crypto.destroy(session, tenant_id, reason="qualification")
        assert receipt["destroyed_key_ids"] == [second_key_id, new_key_id]
        assert destroyed == [second_key_id, new_key_id]
        assert crypto.destroy(session, tenant_id, reason="repeat") == receipt

    engine.dispose()
