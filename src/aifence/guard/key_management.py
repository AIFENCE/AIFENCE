# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from datetime import UTC
from typing import Protocol

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class KeyWrapProvider(Protocol):
    key_id: str
    def wrap(self, plaintext_key: bytes, *, context: bytes) -> bytes: ...
    def unwrap(self, wrapped_key: bytes, *, context: bytes) -> bytes: ...
    def destroy(self, *, reason: str) -> dict[str, str]: ...


@dataclass
class AWSKMSProvider:
    key_id: str
    region: str | None = None
    def _client(self):
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("AWS KMS support requires the boto3 package") from exc
        return boto3.client("kms", region_name=self.region)
    def wrap(self, plaintext_key: bytes, *, context: bytes) -> bytes:
        result = self._client().encrypt(KeyId=self.key_id, Plaintext=plaintext_key,
            EncryptionContext={"agentdance_context": base64.urlsafe_b64encode(context).decode()})
        return bytes(result["CiphertextBlob"])
    def unwrap(self, wrapped_key: bytes, *, context: bytes) -> bytes:
        result = self._client().decrypt(KeyId=self.key_id, CiphertextBlob=wrapped_key,
            EncryptionContext={"agentdance_context": base64.urlsafe_b64encode(context).decode()})
        return bytes(result["Plaintext"])
    def destroy(self, *, reason: str) -> dict[str, str]:
        from datetime import datetime
        result = self._client().schedule_key_deletion(KeyId=self.key_id, PendingWindowInDays=7)
        return {"backend": "aws", "key_id": self.key_id,
                "requested_at": datetime.now(UTC).isoformat(),
                "deletion_date": str(result.get("DeletionDate", "")), "reason": reason}


@dataclass
class GCPKMSProvider:
    key_id: str
    def _client(self):
        try:
            from google.cloud import kms_v1
        except ImportError as exc:
            raise RuntimeError("GCP KMS support requires the google-cloud-kms package") from exc
        return kms_v1.KeyManagementServiceClient()
    def wrap(self, plaintext_key: bytes, *, context: bytes) -> bytes:
        return bytes(self._client().encrypt(request={"name": self.key_id, "plaintext": plaintext_key,
            "additional_authenticated_data": context}).ciphertext)
    def unwrap(self, wrapped_key: bytes, *, context: bytes) -> bytes:
        return bytes(self._client().decrypt(request={"name": self.key_id, "ciphertext": wrapped_key,
            "additional_authenticated_data": context}).plaintext)
    def destroy(self, *, reason: str) -> dict[str, str]:
        from datetime import datetime
        result = self._client().destroy_crypto_key_version(request={"name": self.key_id})
        return {"backend": "gcp", "key_id": self.key_id,
                "requested_at": datetime.now(UTC).isoformat(),
                "state": str(getattr(result, "state", "DESTROY_SCHEDULED")), "reason": reason}


@dataclass
class AzureKeyVaultProvider:
    key_id: str
    def _client(self):
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.keys.crypto import CryptographyClient
        except ImportError as exc:
            raise RuntimeError(
                "Azure Key Vault support requires azure-identity and azure-keyvault-keys"
            ) from exc
        return CryptographyClient(self.key_id, DefaultAzureCredential())
    def wrap(self, plaintext_key: bytes, *, context: bytes) -> bytes:
        from azure.keyvault.keys.crypto import KeyWrapAlgorithm
        return bytes(self._client().wrap_key(KeyWrapAlgorithm.rsa_oaep_256, plaintext_key).encrypted_key)
    def unwrap(self, wrapped_key: bytes, *, context: bytes) -> bytes:
        from azure.keyvault.keys.crypto import KeyWrapAlgorithm
        return bytes(self._client().unwrap_key(KeyWrapAlgorithm.rsa_oaep_256, wrapped_key).key)
    def destroy(self, *, reason: str) -> dict[str, str]:
        from datetime import datetime
        from urllib.parse import urlparse
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.keys import KeyClient
        except ImportError as exc:
            raise RuntimeError(
                "Azure Key Vault support requires azure-identity and azure-keyvault-keys"
            ) from exc
        parsed = urlparse(self.key_id)
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.scheme != "https" or len(parts) < 2 or parts[0] != "keys":
            raise ValueError("Azure tenant key identifier must be a canonical Key Vault key URI")
        vault_url = f"{parsed.scheme}://{parsed.netloc}"
        poller = KeyClient(vault_url=vault_url, credential=DefaultAzureCredential()).begin_delete_key(parts[1])
        result = poller.result()
        return {"backend": "azure", "key_id": self.key_id,
                "requested_at": datetime.now(UTC).isoformat(),
                "recovery_id": str(getattr(result, "recovery_id", "")), "reason": reason}


@dataclass
class VaultTransitProvider:
    key_id: str
    address: str
    token: str
    mount: str = "transit"
    proxy_url: str = ""
    def __post_init__(self) -> None:
        if not self.address.startswith("https://") or not self.token:
            raise ValueError("Vault Transit requires HTTPS and a token")
        self.client = httpx.Client(
            timeout=30, verify=True, follow_redirects=False, trust_env=False,
            proxy=self.proxy_url or None,
        )
    @property
    def base(self) -> str:
        return f"{self.address.rstrip('/')}/v1/{self.mount.strip('/')}"
    def wrap(self, plaintext_key: bytes, *, context: bytes) -> bytes:
        response = self.client.post(f"{self.base}/encrypt/{self.key_id}", headers={"X-Vault-Token": self.token},
            json={"plaintext": base64.b64encode(plaintext_key).decode(), "context": base64.b64encode(context).decode()})
        response.raise_for_status()
        return response.json()["data"]["ciphertext"].encode()
    def unwrap(self, wrapped_key: bytes, *, context: bytes) -> bytes:
        response = self.client.post(f"{self.base}/decrypt/{self.key_id}", headers={"X-Vault-Token": self.token},
            json={"ciphertext": wrapped_key.decode(), "context": base64.b64encode(context).decode()})
        response.raise_for_status()
        return base64.b64decode(response.json()["data"]["plaintext"], validate=True)
    def destroy(self, *, reason: str) -> dict[str, str]:
        from datetime import datetime
        headers = {"X-Vault-Token": self.token}
        self.client.post(
            f"{self.base}/keys/{self.key_id}/config", headers=headers,
            json={"deletion_allowed": True},
        ).raise_for_status()
        self.client.delete(f"{self.base}/keys/{self.key_id}", headers=headers).raise_for_status()
        return {"backend": "vault", "key_id": self.key_id,
                "destroyed_at": datetime.now(UTC).isoformat(), "reason": reason}


class ManagedEnvelopeCipher:
    """Envelope encryption with immutable, allowlisted KMS key routing.

    Ciphertext key identifiers are never written into provider objects. Historical
    key providers must be explicitly configured, preventing attacker-controlled
    envelopes from selecting arbitrary KMS resources through the runtime IAM role.
    """

    VERSION = b"ADK3"

    def __init__(
        self,
        provider: KeyWrapProvider | None = None,
        *,
        providers: dict[str, KeyWrapProvider] | None = None,
        active_key_id: str | None = None,
    ) -> None:
        if provider is not None and providers is not None:
            raise ValueError("provide either provider or providers, not both")
        if provider is not None:
            providers = {provider.key_id: provider}
            active_key_id = provider.key_id
        if not providers:
            raise ValueError("at least one managed key provider is required")
        selected = active_key_id or next(iter(providers))
        if selected not in providers:
            raise ValueError("active managed key identifier is not configured")
        normalized: dict[str, KeyWrapProvider] = {}
        for key_id, configured in providers.items():
            if not key_id or len(key_id.encode("utf-8")) > 65535:
                raise ValueError("managed encryption key identifier is outside the supported range")
            if configured.key_id != key_id:
                raise ValueError("managed key provider identifier mismatch")
            normalized[key_id] = configured
        self._providers = dict(normalized)
        self.active_key_id = selected

    @property
    def provider(self) -> KeyWrapProvider:
        """Compatibility accessor for the immutable active provider."""
        return self._providers[self.active_key_id]

    @property
    def approved_key_ids(self) -> frozenset[str]:
        return frozenset(self._providers)

    def encrypt(self, plaintext: bytes, *, context: bytes) -> bytes:
        data_key = os.urandom(32)
        provider = self._providers[self.active_key_id]
        wrapped = provider.wrap(data_key, context=context)
        key_id = self.active_key_id.encode("utf-8")
        if len(wrapped) > 0xFFFFFF:
            raise ValueError("wrapped data key is outside the supported range")
        nonce = os.urandom(12)
        header = (
            self.VERSION
            + len(key_id).to_bytes(2, "big")
            + key_id
            + len(wrapped).to_bytes(3, "big")
            + wrapped
            + nonce
        )
        return header + AESGCM(data_key).encrypt(nonce, plaintext, context + header[:-12])

    def decrypt(self, ciphertext: bytes, *, context: bytes) -> bytes:
        if not ciphertext.startswith(self.VERSION) or len(ciphertext) < 21:
            raise ValueError("unsupported managed encrypted envelope")
        offset = 4
        key_len = int.from_bytes(ciphertext[offset:offset + 2], "big")
        offset += 2
        if key_len < 1 or offset + key_len + 3 + 12 + 16 > len(ciphertext):
            raise ValueError("managed encrypted envelope is truncated")
        try:
            key_id = ciphertext[offset:offset + key_len].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("managed encrypted envelope has an invalid key identifier") from exc
        offset += key_len
        provider = self._providers.get(key_id)
        if provider is None:
            raise ValueError("managed encrypted envelope references an unapproved key identifier")
        wrapped_len = int.from_bytes(ciphertext[offset:offset + 3], "big")
        offset += 3
        if wrapped_len < 1 or offset + wrapped_len + 12 + 16 > len(ciphertext):
            raise ValueError("managed encrypted envelope has an invalid wrapped-key length")
        wrapped = ciphertext[offset:offset + wrapped_len]
        offset += wrapped_len
        nonce = ciphertext[offset:offset + 12]
        offset += 12
        data_key = provider.unwrap(wrapped, context=context)
        if len(data_key) != 32:
            raise ValueError("managed key provider returned an invalid data key")
        return AESGCM(data_key).decrypt(
            nonce, ciphertext[offset:], context + ciphertext[:offset - 12]
        )

    def envelope_key_id(self, ciphertext: bytes) -> str | None:
        if not ciphertext.startswith(self.VERSION) or len(ciphertext) < 6:
            return None
        length = int.from_bytes(ciphertext[4:6], "big")
        if length < 1 or 6 + length > len(ciphertext):
            return None
        try:
            return ciphertext[6:6 + length].decode("utf-8")
        except UnicodeDecodeError:
            return None

    def needs_reencryption(self, ciphertext: bytes) -> bool:
        return self.envelope_key_id(ciphertext) != self.active_key_id


def _provider_for(settings, key_id: str, *, backend: str | None = None) -> KeyWrapProvider:
    selected_backend = backend or settings.kms_backend
    if selected_backend == "aws":
        return AWSKMSProvider(key_id, settings.extra.get("aws_region"))
    if selected_backend == "gcp":
        return GCPKMSProvider(key_id)
    if selected_backend == "azure":
        return AzureKeyVaultProvider(key_id)
    if selected_backend == "vault":
        return VaultTransitProvider(
            key_id, settings.vault_address, settings.vault_token, settings.vault_transit_mount,
            settings.egress_proxy_url,
        )
    raise ValueError("managed cipher requires aws, gcp, azure, or vault KMS backend")


def build_managed_cipher(settings):
    key_ids = (settings.kms_key_id, *settings.kms_decryption_key_ids)
    unique_ids = tuple(dict.fromkeys(key_id for key_id in key_ids if key_id))
    providers = {key_id: _provider_for(settings, key_id) for key_id in unique_ids}
    return ManagedEnvelopeCipher(providers=providers, active_key_id=settings.kms_key_id)
