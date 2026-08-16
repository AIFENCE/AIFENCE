# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db_models import Concept, LearnedPattern
from .protocol_spec import canonical_msgpack_bytes


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _node(left: str, right: str) -> str:
    return _hash(bytes.fromhex(left) + bytes.fromhex(right))


def merkle_root(leaves: list[str]) -> str:
    if not leaves:
        return _hash(b"")
    level = list(leaves)
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [_node(level[index], level[index + 1]) for index in range(0, len(level), 2)]
    return level[0]


@dataclass(frozen=True)
class MerkleManifest:
    namespace: str
    root: str
    partitions: dict[str, str]
    entries: dict[str, str]


class CodebookMerkle:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _entries(self, namespace: str) -> list[tuple[str, dict[str, Any]]]:
        concepts = list(
            self.db.scalars(
                select(Concept).where(Concept.codebook == namespace, Concept.status.in_(["active", "validated", "shadow"]))
            )
        )
        patterns = list(
            self.db.scalars(
                select(LearnedPattern).where(LearnedPattern.codebook == namespace, LearnedPattern.status.in_(["active", "validated", "shadow"]))
            )
        )
        out: list[tuple[str, dict[str, Any]]] = []
        for concept in concepts:
            out.append((f"concept:{concept.code}", {
                "kind": "concept", "code": concept.code, "canonical": concept.canonical,
                "semantic_hash": concept.semantic_hash, "version": concept.version, "status": concept.status,
            }))
        for pattern in patterns:
            out.append((f"pattern:{pattern.pattern_id}", {
                "kind": "pattern", "pattern_id": pattern.pattern_id, "signature": pattern.signature,
                "version": pattern.version, "status": pattern.status, "composition": pattern.composition,
            }))
        return sorted(out, key=lambda row: row[0])

    def manifest(self, namespace: str, partition_prefix: int = 2) -> MerkleManifest:
        entries: dict[str, str] = {}
        partition_leaves: dict[str, list[str]] = {}
        for key, payload in self._entries(namespace):
            digest = _hash(canonical_msgpack_bytes(payload))
            entries[key] = digest
            prefix = digest[:partition_prefix]
            partition_leaves.setdefault(prefix, []).append(digest)
        partitions = {prefix: merkle_root(sorted(values)) for prefix, values in sorted(partition_leaves.items())}
        root_leaves = [_hash(prefix.encode() + bytes.fromhex(value)) for prefix, value in partitions.items()]
        return MerkleManifest(namespace=namespace, root=merkle_root(root_leaves), partitions=partitions, entries=entries)

    @staticmethod
    def diff(local: MerkleManifest, remote: dict[str, Any]) -> dict[str, Any]:
        if remote.get("root") == local.root:
            return {"equal": True, "changed_partitions": [], "entries": []}
        remote_partitions = dict(remote.get("partitions") or {})
        changed = sorted(
            prefix for prefix in set(local.partitions) | set(remote_partitions)
            if local.partitions.get(prefix) != remote_partitions.get(prefix)
        )
        remote_entries = dict(remote.get("entries") or {})
        prefix_len = len(next(iter(local.partitions), next(iter(remote_partitions), "")))
        if prefix_len < 1:
            prefix_len = 2
        entries = sorted(
            key for key, digest in local.entries.items()
            if digest != remote_entries.get(key) and digest[:prefix_len] in changed
        )
        removed = sorted(
            key for key in remote_entries
            if key not in local.entries and remote_entries[key][:prefix_len] in changed
        )
        return {"equal": False, "changed_partitions": changed, "entries": entries, "removed": removed}
