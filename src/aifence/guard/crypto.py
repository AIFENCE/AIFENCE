# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_object(value: object) -> str:
    return sha256_hex(canonical_json(value))


def api_key_digest(pepper: bytes, secret: str) -> str:
    return hmac.new(pepper, secret.encode("utf-8"), hashlib.sha256).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    key_id = "key_" + secrets.token_urlsafe(12).replace("-", "").replace("_", "")
    secret = secrets.token_urlsafe(32)
    return key_id, secret, f"adk_{key_id}.{secret}"


def parse_api_key(token: str) -> tuple[str, str]:
    if not token.startswith("adk_key_") or "." not in token:
        raise ValueError("invalid AIFENCE API key format")
    left, secret = token.split(".", 1)
    key_id = left.removeprefix("adk_")
    if not key_id or len(secret) < 32:
        raise ValueError("invalid AIFENCE API key format")
    return key_id, secret


class SigningProvider(Protocol):
    key_id: str
    public_key: Ed25519PublicKey
    def sign(self, data: bytes) -> str: ...
    def verify(self, data: bytes, signature: str) -> bool: ...
    def issue_token(self, claims: dict[str, Any], *, headers: dict[str, Any] | None = None,
                    lifetime_seconds: int | None = None) -> str: ...
    def verify_token(self, token: str, *, audience: str | None = None,
                     required: tuple[str, ...] = ("iss", "iat", "exp")) -> dict[str, Any]: ...
    def issue_receipt(self, claims: dict[str, Any], lifetime_seconds: int = 300) -> str: ...
    def verify_receipt(self, token: str, *, audience: str | None = None) -> dict[str, Any]: ...
    def public_pem(self) -> str: ...


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


class SigningKey:
    def __init__(
        self,
        private_key: Ed25519PrivateKey | None,
        public_key: Ed25519PublicKey,
        key_id: str,
    ) -> None:
        self.private_key = private_key
        self.public_key = public_key
        self.key_id = key_id

    @classmethod
    def load(cls, private_file: str, public_file: str, key_id: str) -> SigningKey:
        private_key: Ed25519PrivateKey | None = None
        if private_file and Path(private_file).is_file():
            loaded = serialization.load_pem_private_key(Path(private_file).read_bytes(), password=None)
            if not isinstance(loaded, Ed25519PrivateKey):
                raise TypeError("signing private key is not Ed25519")
            private_key = loaded
        if public_file and Path(public_file).is_file():
            loaded_public = serialization.load_pem_public_key(Path(public_file).read_bytes())
            if not isinstance(loaded_public, Ed25519PublicKey):
                raise TypeError("signing public key is not Ed25519")
            public_key = loaded_public
        elif private_key is not None:
            public_key = private_key.public_key()
        else:
            raise FileNotFoundError("no signing key is available")
        return cls(private_key, public_key, key_id)

    @classmethod
    def ephemeral_for_tests(cls) -> SigningKey:
        private = Ed25519PrivateKey.generate()
        return cls(private, private.public_key(), "test-signing-key")

    def sign(self, data: bytes) -> str:
        if self.private_key is None:
            raise RuntimeError("private signing key is unavailable")
        return base64.urlsafe_b64encode(self.private_key.sign(data)).rstrip(b"=").decode("ascii")

    def verify(self, data: bytes, signature: str) -> bool:
        try:
            padding = "=" * (-len(signature) % 4)
            raw = base64.urlsafe_b64decode(signature + padding)
            self.public_key.verify(raw, data)
            return True
        except Exception:
            return False

    def issue_token(self, claims: dict[str, Any], *, headers: dict[str, Any] | None = None,
                    lifetime_seconds: int | None = None) -> str:
        if self.private_key is None:
            raise RuntimeError("private signing key is unavailable")
        now = datetime.now(UTC)
        payload = dict(claims)
        payload.setdefault("iss", "aifence")
        payload.setdefault("iat", int(now.timestamp()))
        if lifetime_seconds is not None:
            payload.setdefault("exp", int(now.timestamp()) + lifetime_seconds)
        token_headers = {"kid": self.key_id, **(headers or {})}
        return jwt.encode(payload, self.private_key, algorithm="EdDSA", headers=token_headers)

    def verify_token(self, token: str, *, audience: str | None = None,
                     required: tuple[str, ...] = ("iss", "iat", "exp")) -> dict[str, Any]:
        options: dict[str, Any] = {"require": list(required)}
        kwargs: dict[str, Any] = {"algorithms": ["EdDSA"], "options": options, "issuer": "aifence"}
        if audience:
            kwargs["audience"] = audience
        else:
            kwargs["options"] = {**options, "verify_aud": False}
        return jwt.decode(token, self.public_key, **kwargs)

    def issue_receipt(self, claims: dict[str, Any], lifetime_seconds: int = 300) -> str:
        return self.issue_token(claims, lifetime_seconds=lifetime_seconds)

    def verify_receipt(self, token: str, *, audience: str | None = None) -> dict[str, Any]:
        return self.verify_token(token, audience=audience)

    def public_pem(self) -> str:
        return self.public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")


class VaultTransitSigningKey:
    """Non-exportable Ed25519 signer backed by Vault Transit."""

    def __init__(self, *, address: str, token: str, mount: str, key_name: str, key_id: str) -> None:
        if not address.startswith("https://") or not token or not key_name:
            raise ValueError("Vault signing requires HTTPS, a token, and a key name")
        import httpx
        self.address = address.rstrip("/")
        self.mount = mount.strip("/")
        self.key_name = key_name
        self.key_id = key_id
        self.client = httpx.Client(timeout=30, verify=True, follow_redirects=False, trust_env=False)
        self.headers = {"X-Vault-Token": token}
        response = self.client.get(
            f"{self.address}/v1/{self.mount}/keys/{self.key_name}", headers=self.headers
        )
        response.raise_for_status()
        data = response.json().get("data", {})
        latest = str(data.get("latest_version", ""))
        key_doc = data.get("keys", {}).get(latest, {})
        public_pem = key_doc.get("public_key")
        if not isinstance(public_pem, str):
            raise RuntimeError("Vault Transit signing key does not expose an Ed25519 public key")
        loaded = serialization.load_pem_public_key(public_pem.encode("utf-8"))
        if not isinstance(loaded, Ed25519PublicKey):
            raise TypeError("Vault Transit signing key must be Ed25519")
        self.public_key = loaded
        self._public_pem = public_pem

    def sign(self, data: bytes) -> str:
        response = self.client.post(
            f"{self.address}/v1/{self.mount}/sign/{self.key_name}",
            headers=self.headers,
            json={"input": base64.b64encode(data).decode("ascii"), "prehashed": False},
        )
        response.raise_for_status()
        signature = response.json().get("data", {}).get("signature")
        if not isinstance(signature, str) or signature.count(":") < 2:
            raise RuntimeError("Vault Transit returned an invalid signature")
        raw = base64.b64decode(signature.rsplit(":", 1)[1], validate=True)
        return _b64url(raw)

    def verify(self, data: bytes, signature: str) -> bool:
        try:
            self.public_key.verify(_b64url_decode(signature), data)
            return True
        except Exception:
            return False

    def issue_token(self, claims: dict[str, Any], *, headers: dict[str, Any] | None = None,
                    lifetime_seconds: int | None = None) -> str:
        now = datetime.now(UTC)
        header = {"alg": "EdDSA", "typ": "JWT", "kid": self.key_id, **(headers or {})}
        payload = dict(claims)
        payload.setdefault("iss", "aifence")
        payload.setdefault("iat", int(now.timestamp()))
        if lifetime_seconds is not None:
            payload.setdefault("exp", int(now.timestamp()) + lifetime_seconds)
        signing_input = f"{_b64url(canonical_json(header))}.{_b64url(canonical_json(payload))}"
        return f"{signing_input}.{self.sign(signing_input.encode('ascii'))}"

    def verify_token(self, token: str, *, audience: str | None = None,
                     required: tuple[str, ...] = ("iss", "iat", "exp")) -> dict[str, Any]:
        options: dict[str, Any] = {"require": list(required)}
        kwargs: dict[str, Any] = {"algorithms": ["EdDSA"], "options": options, "issuer": "aifence"}
        if audience:
            kwargs["audience"] = audience
        else:
            kwargs["options"] = {**options, "verify_aud": False}
        return jwt.decode(token, self.public_key, **kwargs)

    def issue_receipt(self, claims: dict[str, Any], lifetime_seconds: int = 300) -> str:
        return self.issue_token(claims, lifetime_seconds=lifetime_seconds)

    def verify_receipt(self, token: str, *, audience: str | None = None) -> dict[str, Any]:
        return self.verify_token(token, audience=audience)

    def public_pem(self) -> str:
        return self._public_pem


def build_signing_provider(settings: Any) -> SigningProvider:
    if settings.signing_backend == "local":
        return SigningKey.load(
            settings.signing_private_key_file, settings.signing_public_key_file, settings.signing_key_id
        )
    if settings.signing_backend == "vault":
        return VaultTransitSigningKey(
            address=settings.signing_vault_address or settings.vault_address,
            token=settings.signing_vault_token or settings.vault_token,
            mount=settings.signing_vault_mount,
            key_name=settings.signing_vault_key_name,
            key_id=settings.signing_key_id,
        )
    raise ValueError("unsupported signing backend")


def generate_key_files(directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    private_path = directory / "signing-private.pem"
    public_path = directory / "signing-public.pem"
    if private_path.exists() or public_path.exists():
        raise FileExistsError("refusing to overwrite an existing signing key")
    private = Ed25519PrivateKey.generate()
    private_bytes = private.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_bytes = private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    private_path.write_bytes(private_bytes)
    os.chmod(private_path, 0o600)
    public_path.write_bytes(public_bytes)
    os.chmod(public_path, 0o644)
    return private_path, public_path


class EnvelopeCipher:
    VERSION = b"AD02"
    LEGACY_VERSION = b"AD01"

    def __init__(
        self,
        master_key: bytes | None = None,
        *,
        active_key_id: str = "master-v1",
        keyring: dict[str, bytes] | None = None,
    ) -> None:
        material = dict(keyring or {})
        if master_key is not None:
            material.setdefault(active_key_id, master_key)
        if not material or active_key_id not in material:
            raise ValueError("active encryption key must be present in the keyring")
        encoded_id = active_key_id.encode("utf-8")
        if not encoded_id or len(encoded_id) > 255:
            raise ValueError("active encryption key id must contain 1 to 255 UTF-8 bytes")
        for key_id, key in material.items():
            if not key_id or len(key_id.encode("utf-8")) > 255:
                raise ValueError("encryption key ids must contain 1 to 255 UTF-8 bytes")
            if len(key) != 32:
                raise ValueError("every master key must be 32 bytes")
        self.active_key_id = active_key_id
        self._keys = {key_id: AESGCM(key) for key_id, key in material.items()}

    def encrypt(self, plaintext: bytes, *, context: bytes) -> bytes:
        key_id = self.active_key_id.encode("utf-8")
        nonce = os.urandom(12)
        header = self.VERSION + bytes([len(key_id)]) + key_id + nonce
        return header + self._keys[self.active_key_id].encrypt(nonce, plaintext, context + header[:-12])

    def envelope_key_id(self, ciphertext: bytes) -> str | None:
        if ciphertext.startswith(self.VERSION) and len(ciphertext) >= 6:
            key_id_length = ciphertext[4]
            if key_id_length == 0 or len(ciphertext) < 5 + key_id_length:
                raise ValueError("invalid encrypted envelope")
            try:
                return ciphertext[5:5 + key_id_length].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError("invalid encrypted envelope key identifier") from exc
        if ciphertext.startswith(self.LEGACY_VERSION):
            return None
        raise ValueError("invalid encrypted envelope")

    def decrypt(self, ciphertext: bytes, *, context: bytes) -> bytes:
        if ciphertext.startswith(self.VERSION):
            if len(ciphertext) < 4 + 1 + 1 + 12 + 16:
                raise ValueError("invalid encrypted envelope")
            key_id_length = ciphertext[4]
            key_start = 5
            nonce_start = key_start + key_id_length
            if key_id_length == 0 or len(ciphertext) < nonce_start + 12 + 16:
                raise ValueError("invalid encrypted envelope")
            try:
                key_id = ciphertext[key_start:nonce_start].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError("invalid encrypted envelope key identifier") from exc
            aead = self._keys.get(key_id)
            if aead is None:
                raise ValueError(f"encrypted envelope requires unavailable key id {key_id}")
            nonce = ciphertext[nonce_start:nonce_start + 12]
            header_without_nonce = ciphertext[:nonce_start]
            return aead.decrypt(nonce, ciphertext[nonce_start + 12:], context + header_without_nonce)
        if ciphertext.startswith(self.LEGACY_VERSION):
            if len(ciphertext) < 4 + 12 + 16:
                raise ValueError("invalid encrypted envelope")
            nonce = ciphertext[4:16]
            errors: list[Exception] = []
            for aead in self._keys.values():
                try:
                    return aead.decrypt(nonce, ciphertext[16:], context)
                except Exception as exc:
                    errors.append(exc)
            raise ValueError("legacy encrypted envelope cannot be decrypted by the configured keyring") from errors[-1]
        raise ValueError("invalid encrypted envelope")
