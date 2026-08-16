# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import base64
import hashlib
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db_models import CodebookRelease
from .merkle import CodebookMerkle
from .protocol_spec import canonical_msgpack_bytes


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


class CodebookReleaseStore:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.merkle = CodebookMerkle(db)

    def create(self, namespace: str, release: str, private_key_b64: str, key_id: str = "default") -> CodebookRelease:
        manifest = self.merkle.manifest(namespace)
        existing = self.db.scalar(
            select(CodebookRelease).where(CodebookRelease.namespace == namespace, CodebookRelease.release == release)
        )
        if existing is not None:
            if existing.merkle_root != manifest.root:
                raise ValueError("release label already exists for a different codebook state")
            return existing
        payload = {
            "namespace": namespace,
            "release": release,
            "merkle_root": manifest.root,
            "partitions": manifest.partitions,
            "entries": manifest.entries,
        }
        signature = Ed25519PrivateKey.from_private_bytes(_decode(private_key_b64)).sign(canonical_msgpack_bytes(payload))
        ident = "CBR" + hashlib.sha256(canonical_msgpack_bytes(payload)).hexdigest()[:40]
        item = CodebookRelease(
            id=ident,
            namespace=namespace,
            release=release,
            merkle_root=manifest.root,
            manifest=payload,
            key_id=key_id,
            signature=_encode(signature),
            status="active",
        )
        for old in self.db.scalars(select(CodebookRelease).where(CodebookRelease.namespace == namespace, CodebookRelease.status == "active")):
            old.status = "superseded"
        self.db.add(item)
        self.db.flush()
        return item

    @staticmethod
    def verify(item: CodebookRelease | dict[str, Any], public_key_b64: str) -> bool:
        manifest = item.manifest if isinstance(item, CodebookRelease) else dict(item["manifest"])
        signature = item.signature if isinstance(item, CodebookRelease) else str(item["signature"])
        try:
            Ed25519PublicKey.from_public_bytes(_decode(public_key_b64)).verify(
                _decode(signature), canonical_msgpack_bytes(manifest)
            )
            return True
        except Exception:
            return False
