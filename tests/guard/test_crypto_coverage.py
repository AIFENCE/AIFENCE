from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import aifence.guard.crypto as crypto
from aifence.guard.crypto import EnvelopeCipher, SigningKey


def _pem_private(key: object) -> bytes:
    return key.private_bytes(  # type: ignore[union-attr]
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def _pem_public(key: object) -> bytes:
    return key.public_bytes(  # type: ignore[union-attr]
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def test_api_key_format_and_signing_key_load_variants(tmp_path: Path) -> None:
    key_id, secret, token = crypto.generate_api_key()
    assert crypto.parse_api_key(token) == (key_id, secret)
    with pytest.raises(ValueError, match="invalid AIFENCE API key format"):
        crypto.parse_api_key("adk_key_short.tiny")

    private = Ed25519PrivateKey.generate()
    private_file = tmp_path / "private.pem"
    public_file = tmp_path / "public.pem"
    private_file.write_bytes(_pem_private(private))
    public_file.write_bytes(_pem_public(private.public_key()))

    from_private = SigningKey.load(str(private_file), "", "private-only")
    assert from_private.verify(b"payload", from_private.sign(b"payload"))

    public_only = SigningKey.load("", str(public_file), "public-only")
    signature = from_private.sign(b"payload")
    assert public_only.verify(b"payload", signature)
    assert not public_only.verify(b"tampered", signature)
    assert not public_only.verify(b"payload", "not-base64!")
    with pytest.raises(RuntimeError, match="private signing key is unavailable"):
        public_only.sign(b"payload")
    with pytest.raises(RuntimeError, match="private signing key is unavailable"):
        public_only.issue_token({"sub": "x"})

    token_without_audience = from_private.issue_token({"sub": "x"}, lifetime_seconds=60)
    assert from_private.verify_token(token_without_audience)["sub"] == "x"
    assert "BEGIN PUBLIC KEY" in public_only.public_pem()

    with pytest.raises(FileNotFoundError, match="no signing key"):
        SigningKey.load("", "", "missing")


def test_signing_key_load_rejects_non_ed25519_material(tmp_path: Path) -> None:
    rsa_private = generate_private_key(public_exponent=65537, key_size=2048)
    private_file = tmp_path / "rsa-private.pem"
    public_file = tmp_path / "rsa-public.pem"
    private_file.write_bytes(_pem_private(rsa_private))
    public_file.write_bytes(_pem_public(rsa_private.public_key()))

    with pytest.raises(TypeError, match="private key is not Ed25519"):
        SigningKey.load(str(private_file), "", "bad-private")
    with pytest.raises(TypeError, match="public key is not Ed25519"):
        SigningKey.load("", str(public_file), "bad-public")


def test_generate_key_files_is_cross_platform_and_factory_uses_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    private_file, public_file = crypto.generate_key_files(tmp_path / "keys")
    signer = crypto.build_signing_provider(
        SimpleNamespace(
            signing_backend="local",
            signing_private_key_file=str(private_file),
            signing_public_key_file=str(public_file),
            signing_key_id="local-v1",
        )
    )
    assert signer.verify(b"message", signer.sign(b"message"))
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        crypto.generate_key_files(tmp_path / "keys")

    captured: dict[str, str] = {}

    class FakeVaultSigner:
        def __init__(self, **kwargs: str) -> None:
            captured.update(kwargs)

    monkeypatch.setattr(crypto, "VaultTransitSigningKey", FakeVaultSigner)
    result = crypto.build_signing_provider(
        SimpleNamespace(
            signing_backend="vault",
            signing_vault_address="https://vault.example",
            vault_address="",
            signing_vault_token="token",
            vault_token="",
            signing_vault_mount="transit",
            signing_vault_key_name="aifence",
            signing_key_id="vault-v1",
        )
    )
    assert isinstance(result, FakeVaultSigner)
    assert captured["address"] == "https://vault.example"
    with pytest.raises(ValueError, match="unsupported signing backend"):
        crypto.build_signing_provider(SimpleNamespace(signing_backend="unsupported"))


def test_envelope_cipher_rejects_invalid_keyrings_and_envelopes() -> None:
    key = b"k" * 32
    with pytest.raises(ValueError, match="active encryption key"):
        EnvelopeCipher()
    with pytest.raises(ValueError, match="active encryption key id"):
        EnvelopeCipher(key, active_key_id="")
    with pytest.raises(ValueError, match="encryption key ids"):
        EnvelopeCipher(active_key_id="ok", keyring={"ok": key, "": key})
    with pytest.raises(ValueError, match="every master key"):
        EnvelopeCipher(b"short")

    cipher = EnvelopeCipher(key)
    encrypted = cipher.encrypt(b"secret", context=b"ctx")
    assert cipher.envelope_key_id(encrypted) == "master-v1"

    with pytest.raises(ValueError, match="invalid encrypted envelope"):
        cipher.envelope_key_id(b"invalid")
    with pytest.raises(ValueError, match="invalid encrypted envelope"):
        cipher.envelope_key_id(b"AD02\x00")
    with pytest.raises(ValueError, match="key identifier"):
        cipher.envelope_key_id(b"AD02\x01\xff")
    with pytest.raises(ValueError, match="invalid encrypted envelope"):
        cipher.decrypt(b"AD02", context=b"ctx")
    with pytest.raises(ValueError, match="unavailable key id"):
        other = EnvelopeCipher(key, active_key_id="other")
        other.decrypt(encrypted, context=b"ctx")

    invalid_id = b"AD02\x01\xff" + b"n" * 12 + b"x" * 16
    with pytest.raises(ValueError, match="key identifier"):
        cipher.decrypt(invalid_id, context=b"ctx")
    with pytest.raises(ValueError, match="invalid encrypted envelope"):
        cipher.decrypt(b"not-an-envelope", context=b"ctx")


def test_legacy_envelope_reads_and_failures() -> None:
    key = b"l" * 32
    context = b"tenant:artifact"
    nonce = b"n" * 12
    payload = AESGCM(key).encrypt(nonce, b"legacy", context)
    legacy = EnvelopeCipher.LEGACY_VERSION + nonce + payload

    cipher = EnvelopeCipher(active_key_id="legacy-key", keyring={"legacy-key": key})
    assert cipher.envelope_key_id(legacy) is None
    assert cipher.decrypt(legacy, context=context) == b"legacy"

    with pytest.raises(ValueError, match="invalid encrypted envelope"):
        cipher.decrypt(EnvelopeCipher.LEGACY_VERSION + b"short", context=context)
    wrong = EnvelopeCipher(active_key_id="wrong", keyring={"wrong": b"w" * 32})
    with pytest.raises(ValueError, match="cannot be decrypted"):
        wrong.decrypt(legacy, context=context)
