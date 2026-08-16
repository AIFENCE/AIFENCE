# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings
from .db_models import Reference, ReferenceGrant
from .resilience import QuotaManager


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _extract_path(value: Any, path: str) -> Any:
    if path in {"", "$"}:
        return value
    current = value
    normalized = path[2:] if path.startswith("$.") else path.lstrip("/")
    parts = [p for p in normalized.replace("/", ".").split(".") if p]
    for part in parts:
        if isinstance(current, dict):
            current = current[part]
        elif isinstance(current, list):
            current = current[int(part)]
        else:
            raise KeyError(path)
    return current


def _path_allowed(requested: str, allowed: list[str]) -> bool:
    if not allowed:
        return True
    req = requested.removeprefix("$.").lstrip("/")
    for prefix in allowed:
        p = prefix.removeprefix("$.").lstrip("/")
        if req == p or req.startswith(p + ".") or req.startswith(p + "/"):
            return True
    return False


class ReferenceAccessError(PermissionError):
    pass


class ReferenceExpiredError(KeyError):
    pass


class ReferenceStore:
    """Content-addressed blob store with workspace/agent grants.

    Blob identity is global and derived only from canonical content. Authorization,
    lifetime, tier, and selective disclosure are grant metadata rather than part of
    object identity, so identical content deduplicates safely across handoffs.
    """

    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings

    def _key(self) -> bytes | None:
        if self.settings is None or self.settings.ref_encryption_key is None:
            return None
        return base64.urlsafe_b64decode(self.settings.ref_encryption_key.get_secret_value().encode())

    def _encrypt(self, data: bytes, ref_id: str) -> str:
        key = self._key()
        if key is None:
            raise ValueError("reference encryption requested but SAGE_REF_ENCRYPTION_KEY is unset")
        nonce = os.urandom(12)
        encrypted = AESGCM(key).encrypt(nonce, data, ref_id.encode())
        return base64.b64encode(nonce + encrypted).decode()

    def _decrypt(self, item: Reference) -> Any:
        if item.ciphertext is None:
            return item.payload
        key = self._key()
        if key is None:
            raise ReferenceAccessError("encrypted reference cannot be decrypted without configured key")
        blob = base64.b64decode(item.ciphertext)
        nonce, encrypted = blob[:12], blob[12:]
        raw = AESGCM(key).decrypt(nonce, encrypted, item.id.encode())
        return json.loads(raw)

    @staticmethod
    def content_id(data: bytes) -> str:
        return "sage:sha256:" + hashlib.sha256(data).hexdigest()

    def _grant_query(self, ref_id: str, workspace: str) -> Any:
        return select(ReferenceGrant).where(
            ReferenceGrant.ref_id == ref_id,
            ReferenceGrant.workspace == workspace,
            ReferenceGrant.invalidated_at.is_(None),
        )

    def _active_grants(self, ref_id: str, workspace: str) -> list[ReferenceGrant]:
        now = _utcnow()
        grants = list(self.db.scalars(self._grant_query(ref_id, workspace)))
        out: list[ReferenceGrant] = []
        for grant in grants:
            if grant.expires_at is not None:
                expiry = grant.expires_at.replace(tzinfo=grant.expires_at.tzinfo or UTC)
                if expiry <= now:
                    continue
            out.append(grant)
        return out

    def grant(
        self,
        ref_id: str,
        *,
        workspace: str = "default",
        owner: str | None = None,
        acl: list[str] | None = None,
        allowed_paths: list[str] | None = None,
        tier: str = "warm",
        ttl_seconds: int | None = None,
        provenance: dict[str, Any] | None = None,
        sensitivity: list[str] | None = None,
    ) -> ReferenceGrant:
        if self.db.get(Reference, ref_id) is None:
            raise KeyError(ref_id)
        if tier not in {"hot", "warm", "cold"}:
            raise ValueError("tier must be hot, warm, or cold")
        existing = self.db.scalar(
            select(ReferenceGrant).where(
                ReferenceGrant.ref_id == ref_id,
                ReferenceGrant.workspace == workspace,
                ReferenceGrant.owner == owner,
            )
        )
        ttl = ttl_seconds if ttl_seconds is not None else (self.settings.default_ref_ttl_seconds if self.settings else None)
        expires = _utcnow() + timedelta(seconds=ttl) if ttl else None
        if existing is not None:
            existing.acl = sorted(set(existing.acl) | set(acl or []))
            existing.allowed_paths = sorted(set(existing.allowed_paths) | set(allowed_paths or []))
            existing.tier = tier
            existing.expires_at = expires
            existing.invalidated_at = None
            if provenance:
                existing.provenance = provenance
            if sensitivity is not None:
                existing.sensitivity = sorted(set(sensitivity))
            existing.version += 1
            return existing
        item = ReferenceGrant(
            ref_id=ref_id,
            workspace=workspace,
            owner=owner,
            acl=sorted(set(acl or [])),
            allowed_paths=sorted(set(allowed_paths or [])),
            tier=tier,
            provenance=provenance or {},
            sensitivity=sorted(set(sensitivity or [])),
            expires_at=expires,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def put(
        self,
        value: Any,
        media_type: str = "application/json",
        *,
        workspace: str = "default",
        owner: str | None = None,
        acl: list[str] | None = None,
        allowed_paths: list[str] | None = None,
        tier: str = "warm",
        ttl_seconds: int | None = None,
        encrypt: bool = False,
        provenance: dict[str, Any] | None = None,
        sensitivity: list[str] | None = None,
    ) -> Reference:
        if tier not in {"hot", "warm", "cold"}:
            raise ValueError("tier must be hot, warm, or cold")
        data = canonical_bytes(value)
        if self.settings is not None:
            QuotaManager(self.db, self.settings).consume(workspace, "ref_bytes", len(data))
        if self.settings is not None and len(data) > self.settings.max_store_bytes:
            raise ValueError(f"payload exceeds max_store_bytes={self.settings.max_store_bytes}")
        encrypt = encrypt or bool(self.settings and self.settings.require_ref_encryption)
        ref_id = self.content_id(data)
        ref = self.db.get(Reference, ref_id)
        if ref is None:
            ref = Reference(
                id=ref_id,
                media_type=media_type,
                payload=None if encrypt else value,
                ciphertext=self._encrypt(data, ref_id) if encrypt else None,
                byte_size=len(data),
                workspace="*",
                owner=None,
                acl=[],
                tier=tier,
                provenance={"content_addressed": True},
                version=1,
                expires_at=None,
            )
            self.db.add(ref)
            self.db.flush()
        elif encrypt and ref.ciphertext is None:
            ref.ciphertext = self._encrypt(data, ref_id)
            ref.payload = None
        self.grant(
            ref_id,
            workspace=workspace,
            owner=owner,
            acl=acl,
            allowed_paths=allowed_paths,
            tier=tier,
            ttl_seconds=ttl_seconds,
            provenance=provenance,
            sensitivity=sensitivity,
        )
        return ref

    def _authorize(self, item: Reference, actor: str | None, workspace: str) -> ReferenceGrant:
        if item.invalidated_at is not None:
            raise ReferenceExpiredError("reference invalidated")
        if item.expires_at is not None:
            expiry = item.expires_at.replace(tzinfo=item.expires_at.tzinfo or UTC)
            if expiry <= _utcnow():
                raise ReferenceExpiredError("reference expired")
        grants = self._active_grants(item.id, workspace)
        if not grants:
            raise ReferenceExpiredError("reference has no active grant in workspace")
        for grant in grants:
            if grant.owner is None and not grant.acl:
                return grant
            if actor is not None and (actor == grant.owner or actor in grant.acl):
                return grant
        raise ReferenceAccessError("actor is not authorized for reference")

    def get(self, ref_id: str, *, actor: str | None = None, workspace: str = "default") -> Reference | None:
        item = self.db.get(Reference, ref_id)
        if item is None:
            return None
        self._authorize(item, actor, workspace)
        return item

    def value(self, item: Reference) -> Any:
        return self._decrypt(item)

    def resolve(
        self,
        ref_id: str,
        *,
        actor: str | None = None,
        workspace: str = "default",
        fields: list[str] | None = None,
    ) -> Any:
        item = self.db.get(Reference, ref_id)
        if item is None:
            raise KeyError(ref_id)
        grant = self._authorize(item, actor, workspace)
        value = self.value(item)
        requested = fields or []
        if not requested:
            if grant.allowed_paths:
                return {path: _extract_path(value, path) for path in grant.allowed_paths}
            return value
        for path in requested:
            if not _path_allowed(path, grant.allowed_paths):
                raise ReferenceAccessError(f"field not authorized: {path}")
        return {path: _extract_path(value, path) for path in requested}

    def policy(
        self,
        ref_id: str,
        *,
        actor: str | None,
        workspace: str,
        tier: str | None = None,
        ttl_seconds: int | None = None,
        invalidate: bool = False,
    ) -> Reference:
        item = self.db.get(Reference, ref_id)
        if item is None:
            raise KeyError(ref_id)
        grants = self._active_grants(ref_id, workspace)
        owned = [g for g in grants if g.owner == actor or (g.owner is None and actor is None)]
        if not owned:
            raise ReferenceAccessError("only the owner can change reference policy")
        for grant in owned:
            if tier is not None:
                if tier not in {"hot", "warm", "cold"}:
                    raise ValueError("tier must be hot, warm, or cold")
                grant.tier = tier
                item.tier = tier
            if ttl_seconds is not None:
                grant.expires_at = _utcnow() + timedelta(seconds=ttl_seconds)
            if invalidate:
                grant.invalidated_at = _utcnow()
        return item

    def grant_metadata(
        self,
        ref_id: str,
        *,
        actor: str | None,
        workspace: str,
        privileged: bool = False,
    ) -> ReferenceGrant:
        item = self.db.get(Reference, ref_id)
        if item is None:
            raise KeyError(ref_id)
        if not privileged:
            return self._authorize(item, actor, workspace)
        grants = self._active_grants(ref_id, workspace)
        owned = [grant for grant in grants if grant.owner == actor]
        if owned:
            return owned[0]
        if actor is None:
            unowned = [grant for grant in grants if grant.owner is None]
            if unowned:
                return unowned[0]
        raise ReferenceAccessError("reference grant not found for owner")
