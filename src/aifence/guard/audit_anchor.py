# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .crypto import SigningProvider, canonical_json, hash_object


class AnchorBackend(Protocol):
    name: str
    def publish(self, envelope: dict[str, Any]) -> dict[str, Any]: ...
    def verify(self, envelope: dict[str, Any], receipt: dict[str, Any]) -> bool: ...


@dataclass
class FileAnchorBackend:
    root: Path
    name: str = "file"
    def __post_init__(self) -> None:
        self.root = self.root.expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
    def publish(self, envelope: dict[str, Any]) -> dict[str, Any]:
        directory = self.root / str(envelope["tenant_id"])
        directory.mkdir(mode=0o700, exist_ok=True)
        target = directory / f"{int(envelope['sequence']):020d}.json"
        payload = canonical_json(envelope) + b"\n"
        if target.exists():
            if target.read_bytes() != payload:
                raise RuntimeError("conflicting audit anchor already exists")
        else:
            temporary = directory / f".{target.name}.{os.getpid()}.tmp"
            fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(payload); handle.flush(); os.fsync(handle.fileno())
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        return {"backend": self.name, "path": str(target), "sha256": hash_object(envelope),
                "stored_at": datetime.now(UTC).isoformat()}
    def verify(self, envelope: dict[str, Any], receipt: dict[str, Any]) -> bool:
        try:
            path = Path(str(receipt["path"])).resolve()
            return self.root in path.parents and json.loads(path.read_text()) == envelope and receipt.get("sha256") == hash_object(envelope)
        except Exception:
            return False


@dataclass
class WebhookAnchorBackend:
    url: str
    token: str
    verify_url: str
    public_key_file: str
    expected_key_ids: tuple[str, ...] = ()
    proxy_url: str = ""
    name: str = "webhook"

    def __post_init__(self) -> None:
        if not self.url.startswith("https://") or not self.verify_url.startswith("https://"):
            raise ValueError("audit anchor webhook publish and verify URLs must use HTTPS")
        loaded = serialization.load_pem_public_key(Path(self.public_key_file).read_bytes())
        if not isinstance(loaded, Ed25519PublicKey):
            raise TypeError("audit anchor receipt key must be Ed25519")
        self.public_key = loaded
        self._expected_key_ids = frozenset(self.expected_key_ids)
        self.client = httpx.Client(timeout=30, verify=True, follow_redirects=False, trust_env=False,
                                   proxy=self.proxy_url or None)

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    @staticmethod
    def _signed_receipt(document: dict[str, Any]) -> dict[str, Any]:
        required = {
            "receipt_id", "tenant_id", "sequence", "chain_head", "stored_at",
            "nonce", "key_id", "signature",
        }
        if not required.issubset(document):
            raise RuntimeError("audit anchor webhook returned an incomplete signed receipt")
        return {str(key): value for key, value in document.items()}

    def _verify_signature(self, receipt: dict[str, Any]) -> bool:
        if self._expected_key_ids and receipt.get("key_id") not in self._expected_key_ids:
            return False
        signature = receipt.get("signature")
        if not isinstance(signature, str):
            return False
        unsigned = {key: value for key, value in receipt.items() if key != "signature"}
        try:
            padding = "=" * (-len(signature) % 4)
            raw = base64.urlsafe_b64decode(signature + padding)
            self.public_key.verify(raw, canonical_json(unsigned))
            return True
        except Exception:
            return False

    @staticmethod
    def _matches_envelope(envelope: dict[str, Any], receipt: dict[str, Any]) -> bool:
        return (
            receipt.get("tenant_id") == envelope.get("tenant_id")
            and int(receipt.get("sequence", -1)) == int(envelope.get("sequence", -2))
            and receipt.get("chain_head") == envelope.get("chain_head")
            and receipt.get("nonce") == envelope.get("nonce")
            and receipt.get("previous_receipt_id") == envelope.get("previous_receipt_id")
            and isinstance(receipt.get("nonce"), str)
            and len(str(receipt.get("nonce"))) >= 16
        )

    def publish(self, envelope: dict[str, Any]) -> dict[str, Any]:
        response = self.client.post(self.url, content=canonical_json(envelope), headers=self._headers())
        response.raise_for_status()
        document = response.json()
        if not isinstance(document, dict):
            raise RuntimeError("audit anchor webhook did not return a receipt object")
        receipt = self._signed_receipt(document)
        if not self._matches_envelope(envelope, receipt) or not self._verify_signature(receipt):
            raise RuntimeError("audit anchor webhook returned an invalid signed receipt")
        return {"backend": self.name, **receipt}

    def verify(self, envelope: dict[str, Any], receipt: dict[str, Any]) -> bool:
        receipt_id = receipt.get("receipt_id")
        if not isinstance(receipt_id, str) or not receipt_id or len(receipt_id.encode("utf-8")) > 512:
            return False
        try:
            target = f"{self.verify_url.rstrip('/')}/{quote(receipt_id, safe='')}"
            response = self.client.get(target, headers=self._headers())
            response.raise_for_status()
            document = response.json()
            if not isinstance(document, dict):
                return False
            remote = self._signed_receipt(document)
            expected = {key: value for key, value in receipt.items() if key != "backend"}
            return (
                remote == expected
                and self._matches_envelope(envelope, remote)
                and self._verify_signature(remote)
            )
        except Exception:
            return False


def build_anchor_envelope(signing_key: SigningProvider, *, tenant_id: str, sequence: int,
                          chain_head: str, destination: str,
                          previous_receipt_id: str | None = None) -> dict[str, Any]:
    import secrets
    unsigned = {"format": "aifence.audit-anchor.v2", "tenant_id": tenant_id,
                "sequence": sequence, "chain_head": chain_head, "destination": destination,
                "nonce": secrets.token_urlsafe(24), "previous_receipt_id": previous_receipt_id,
                "key_id": signing_key.key_id, "anchored_at": datetime.now(UTC).isoformat()}
    return {**unsigned, "signature": signing_key.sign(canonical_json(unsigned))}


def build_anchor_backend(settings: Any, destination: str) -> AnchorBackend:
    """Build a named independent anchor destination from validated configuration."""
    configured = settings.extra.get("audit_anchor_destinations", {}) if isinstance(settings.extra, dict) else {}
    entry = configured.get(destination) if isinstance(configured, dict) else None
    if isinstance(entry, dict):
        backend = str(entry.get("backend", "webhook"))
        if backend == "file":
            return FileAnchorBackend(Path(str(entry.get("directory", settings.audit_anchor_directory))))
        if backend != "webhook":
            raise ValueError("unsupported named audit anchor backend")
        key_ids_raw = entry.get("key_ids", [])
        key_ids = tuple(str(value) for value in key_ids_raw) if isinstance(key_ids_raw, list) else ()
        return WebhookAnchorBackend(
            str(entry.get("url", "")), str(entry.get("token", "")),
            str(entry.get("verify_url", "")), str(entry.get("public_key_file", "")),
            key_ids, settings.egress_proxy_url, name=destination,
        )
    if destination == "file":
        return FileAnchorBackend(Path(settings.audit_anchor_directory))
    if destination in {"webhook", settings.audit_anchor_backend} or destination in settings.audit_anchor_destinations:
        return WebhookAnchorBackend(
            settings.audit_anchor_webhook_url, settings.audit_anchor_webhook_token,
            settings.audit_anchor_webhook_verify_url, settings.audit_anchor_webhook_public_key_file,
            settings.audit_anchor_webhook_key_ids, settings.egress_proxy_url, name=destination,
        )
    raise ValueError("unknown audit anchor destination")
