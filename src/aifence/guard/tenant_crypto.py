# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any, Protocol

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import select
from sqlalchemy.orm import Session

from .key_management import KeyWrapProvider, _provider_for
from .models import TenantKeyRoute


class RootCipher(Protocol):
    active_key_id: str
    def encrypt(self, plaintext: bytes, *, context: bytes) -> bytes: ...
    def decrypt(self, ciphertext: bytes, *, context: bytes) -> bytes: ...


class TenantCryptography:
    """Per-tenant cryptographic routing with destroyable external key authority.

    Production envelopes are wrapped directly by a tenant-dedicated KMS key derived
    from an administrator-controlled template. The ciphertext never chooses a key:
    the database route is authoritative and the embedded identifier must match it.
    Development may use a locally wrapped tenant KEK, but production configuration
    rejects that mode for cryptographic-erasure claims.
    """

    VERSION = b"ADTC1"

    def __init__(self, root_cipher: RootCipher, settings: Any) -> None:
        self.root_cipher = root_cipher
        self.settings = settings
        self.backend = settings.tenant_key_backend
        self.key_template = settings.tenant_kms_key_template

    def ensure_route(self, session: Session, tenant_id: str) -> TenantKeyRoute:
        statement = select(TenantKeyRoute).where(TenantKeyRoute.tenant_id == tenant_id)
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update()
        route = session.scalar(statement)
        if route is not None:
            if route.status == "destroyed":
                raise PermissionError("tenant cryptographic route has been destroyed")
            return route
        now = datetime.now(UTC)
        if self.backend == "local":
            raw = os.urandom(32)
            key_id = f"local-tenant:{tenant_id}:v1"
            wrapped = self.root_cipher.encrypt(raw, context=f"tenant-kek:{tenant_id}:1".encode())
        else:
            if "{tenant_id}" not in self.key_template:
                raise ValueError("tenant KMS key template must contain {tenant_id}")
            key_id = self.key_template.format(tenant_id=tenant_id)
            wrapped = None
        route = TenantKeyRoute(
            tenant_id=tenant_id,
            backend=self.backend,
            key_id=key_id,
            historical_key_ids=[],
            wrapped_local_key=wrapped,
            status="active",
            version=1,
            created_at=now,
        )
        session.add(route)
        session.flush()
        return route

    def encrypt(self, session: Session, tenant_id: str, plaintext: bytes, *, context: bytes) -> bytes:
        route = self.ensure_route(session, tenant_id)
        data_key = os.urandom(32)
        wrapped = self._wrap(route, data_key, context=context)
        key_id = route.key_id.encode("utf-8")
        if len(key_id) > 65535 or len(wrapped) > 0xFFFFFF:
            raise ValueError("tenant key envelope metadata exceeds the supported size")
        nonce = os.urandom(12)
        header = (
            self.VERSION
            + route.version.to_bytes(4, "big")
            + len(key_id).to_bytes(2, "big")
            + key_id
            + len(wrapped).to_bytes(3, "big")
            + wrapped
            + nonce
        )
        aad = context + header[:-12]
        return header + AESGCM(data_key).encrypt(nonce, plaintext, aad)

    def decrypt(self, session: Session, tenant_id: str, ciphertext: bytes, *, context: bytes) -> bytes:
        if not ciphertext.startswith(self.VERSION):
            return self.root_cipher.decrypt(ciphertext, context=context)
        route = session.get(TenantKeyRoute, tenant_id)
        if route is None or route.status == "destroyed":
            raise PermissionError("tenant cryptographic route is unavailable")
        offset = len(self.VERSION)
        if len(ciphertext) < offset + 4 + 2 + 3 + 12 + 16:
            raise ValueError("tenant encrypted envelope is truncated")
        version = int.from_bytes(ciphertext[offset:offset + 4], "big"); offset += 4
        key_len = int.from_bytes(ciphertext[offset:offset + 2], "big"); offset += 2
        if key_len < 1 or offset + key_len + 3 + 12 + 16 > len(ciphertext):
            raise ValueError("tenant encrypted envelope has an invalid key identifier")
        key_id = ciphertext[offset:offset + key_len].decode("utf-8"); offset += key_len
        approved = {route.key_id, *route.historical_key_ids}
        if key_id not in approved:
            raise PermissionError("tenant encrypted envelope references an unapproved key route")
        wrapped_len = int.from_bytes(ciphertext[offset:offset + 3], "big"); offset += 3
        if wrapped_len < 1 or offset + wrapped_len + 12 + 16 > len(ciphertext):
            raise ValueError("tenant encrypted envelope has an invalid wrapped-key length")
        wrapped = ciphertext[offset:offset + wrapped_len]; offset += wrapped_len
        nonce = ciphertext[offset:offset + 12]; offset += 12
        data_key = self._unwrap(route, key_id, wrapped, context=context, version=version)
        return AESGCM(data_key).decrypt(nonce, ciphertext[offset:], context + ciphertext[:offset - 12])

    def is_tenant_envelope(self, ciphertext: bytes) -> bool:
        return ciphertext.startswith(self.VERSION)

    def envelope_key_id(self, ciphertext: bytes) -> str | None:
        if not ciphertext.startswith(self.VERSION):
            return None
        offset = len(self.VERSION) + 4
        if len(ciphertext) < offset + 2:
            return None
        key_len = int.from_bytes(ciphertext[offset:offset + 2], "big")
        offset += 2
        if key_len < 1 or offset + key_len > len(ciphertext):
            return None
        try:
            return ciphertext[offset:offset + key_len].decode("utf-8")
        except UnicodeDecodeError:
            return None

    def rotate_route(self, session: Session, tenant_id: str, *, new_key_id: str) -> TenantKeyRoute:
        if self.backend == "local":
            raise ValueError("tenant key route rotation requires an external KMS backend")
        normalized = new_key_id.strip()
        if not normalized or len(normalized) > 2048:
            raise ValueError("new tenant KMS key identifier is invalid")
        statement = select(TenantKeyRoute).where(TenantKeyRoute.tenant_id == tenant_id)
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update()
        route = session.scalar(statement)
        if route is None:
            route = self.ensure_route(session, tenant_id)
        if route.status != "active":
            raise PermissionError("tenant cryptographic route is not active")
        if route.backend != self.backend:
            raise ValueError("tenant key backend cannot change during route rotation")
        if route.key_id == normalized:
            return route
        historical = [key for key in route.historical_key_ids if key != normalized]
        if route.key_id not in historical:
            historical.append(route.key_id)
        route.historical_key_ids = historical
        route.key_id = normalized
        route.version += 1
        route.rotated_at = datetime.now(UTC)
        session.flush()
        return route

    def retire_historical_key(
        self, session: Session, tenant_id: str, *, key_id: str
    ) -> TenantKeyRoute:
        statement = select(TenantKeyRoute).where(TenantKeyRoute.tenant_id == tenant_id)
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update()
        route = session.scalar(statement)
        if route is None or route.status != "active":
            raise PermissionError("tenant cryptographic route is unavailable")
        if key_id == route.key_id:
            raise ValueError("the active tenant key cannot be retired")
        if key_id not in route.historical_key_ids:
            raise ValueError("tenant key is not an approved historical route")
        route.historical_key_ids = [value for value in route.historical_key_ids if value != key_id]
        session.flush()
        return route

    def destroy(self, session: Session, tenant_id: str, *, reason: str) -> dict[str, Any]:
        statement = select(TenantKeyRoute).where(TenantKeyRoute.tenant_id == tenant_id)
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update()
        route = session.scalar(statement)
        if route is None:
            route = self.ensure_route(session, tenant_id)
        if route.status == "destroyed":
            return dict(route.destruction_receipt)
        route.status = "destruction_pending"
        route.destruction_requested_at = datetime.now(UTC)
        session.flush()
        receipt = self._destroy_external(route, reason=reason)
        route.status = "destroyed"
        route.destroyed_at = datetime.now(UTC)
        route.wrapped_local_key = None
        route.destruction_receipt = receipt
        return receipt

    def _provider(self, key_id: str, *, backend: str | None = None) -> KeyWrapProvider:
        return _provider_for(self.settings, key_id, backend=backend or self.backend)

    def _local_kek(self, route: TenantKeyRoute) -> bytes:
        if route.wrapped_local_key is None:
            raise PermissionError("tenant local key material has been destroyed")
        return self.root_cipher.decrypt(
            route.wrapped_local_key,
            context=f"tenant-kek:{route.tenant_id}:{route.version}".encode(),
        )

    def _wrap(self, route: TenantKeyRoute, data_key: bytes, *, context: bytes) -> bytes:
        if route.backend == "local":
            nonce = os.urandom(12)
            return nonce + AESGCM(self._local_kek(route)).encrypt(nonce, data_key, context)
        return self._provider(route.key_id, backend=route.backend).wrap(data_key, context=context)

    def _unwrap(self, route: TenantKeyRoute, key_id: str, wrapped: bytes, *, context: bytes,
                version: int) -> bytes:
        if route.backend == "local":
            if key_id != route.key_id or version != route.version:
                raise PermissionError("historical local tenant keys are not retained")
            nonce, body = wrapped[:12], wrapped[12:]
            return AESGCM(self._local_kek(route)).decrypt(nonce, body, context)
        return self._provider(key_id, backend=route.backend).unwrap(wrapped, context=context)

    def _destroy_external(self, route: TenantKeyRoute, *, reason: str) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        if route.backend == "local":
            return {"backend": "local", "key_id": route.key_id, "destroyed_at": now,
                    "reason": reason, "assurance": "development-only"}
        key_ids = tuple(dict.fromkeys((route.key_id, *route.historical_key_ids)))
        receipts = [
            dict(self._provider(key_id, backend=route.backend).destroy(reason=reason))
            for key_id in key_ids
        ]
        primary = dict(receipts[0])
        primary["destroyed_key_ids"] = list(key_ids)
        primary["historical_key_receipts"] = receipts[1:]
        return primary
