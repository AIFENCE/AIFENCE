# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import uuid
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from .codebook import Codebook
from .config import Settings
from .db_models import FederationPeer
from .patterns import PatternStore
from .signing import sign_wire, verify_wire


class FederationStore:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.codebook = Codebook(db, settings)
        self.patterns = PatternStore(db, settings, self.codebook)

    def register_peer(
        self,
        *,
        workspace: str,
        name: str,
        base_url: str,
        public_key_b64: str,
        allowed_namespaces: list[str],
        enabled: bool = True,
    ) -> FederationPeer:
        if self.settings.env.lower() == "production" and not base_url.lower().startswith("https://"):
            raise ValueError("federation peers must use https in production")
        item = self.db.scalar(select(FederationPeer).where(FederationPeer.workspace == workspace, FederationPeer.name == name))
        if item is None:
            item = FederationPeer(id="PEER" + uuid.uuid4().hex, workspace=workspace, name=name, base_url=base_url)
            self.db.add(item)
        item.base_url = base_url.rstrip("/")
        item.public_key_b64 = public_key_b64
        item.allowed_namespaces = sorted(set(allowed_namespaces))
        item.enabled = enabled
        self.db.flush()
        return item

    def export_bundle(self, namespace: str, *, source: str = "local") -> dict[str, Any]:
        concepts = [
            {
                "canonical": c.canonical,
                "description": c.description,
                "status": c.status,
                "version": c.version,
                "semantic_hash": c.semantic_hash,
            }
            for c in self.codebook.all(namespace, include_deprecated=False)
        ]
        patterns = [self.patterns.response(p) for p in self.patterns.list(namespace, status="active") if p.codebook == namespace]
        bundle: dict[str, Any] = {
            "type": "sage-federation/0.2",
            "source": source,
            "namespace": namespace,
            "concepts": concepts,
            "patterns": patterns,
        }
        if self.settings.packet_signing_private_key is not None:
            bundle["g"] = sign_wire(bundle, self.settings.packet_signing_private_key.get_secret_value(), key_id=self.settings.packet_signing_key_id)
        return bundle

    def _namespace_allowed(self, peer: FederationPeer, namespace: str) -> bool:
        return any(namespace == allowed or namespace.startswith(allowed + ".") for allowed in peer.allowed_namespaces)

    def import_bundle(self, bundle: dict[str, Any], *, workspace: str = "default") -> dict[str, int]:
        if bundle.get("type") != "sage-federation/0.2":
            raise ValueError("unsupported federation bundle")
        source = str(bundle.get("source", ""))
        namespace = str(bundle.get("namespace", ""))
        peer = self.db.scalar(select(FederationPeer).where(FederationPeer.workspace == workspace, FederationPeer.name == source, FederationPeer.enabled.is_(True)))
        if peer is None:
            raise PermissionError("unknown or disabled federation peer")
        if not self._namespace_allowed(peer, namespace):
            raise PermissionError("peer is not allowed to publish this namespace")
        if peer.public_key_b64 and not verify_wire(bundle, peer.public_key_b64):
            raise PermissionError("invalid federation signature")
        concepts = 0
        for raw in bundle.get("concepts", []):
            if not isinstance(raw, dict) or not raw.get("canonical"):
                continue
            self.codebook.register(namespace, str(raw["canonical"]), str(raw.get("description", "")))
            concepts += 1
        patterns = 0
        for raw in bundle.get("patterns", []):
            if not isinstance(raw, dict) or not isinstance(raw.get("composition"), list):
                continue
            item = self.patterns.observe(namespace, list(raw["composition"]), relation_structure={**dict(raw.get("relation_structure") or {}), "federated_from": source})
            if item is not None:
                patterns += 1
        self.db.flush()
        return {"concepts_imported": concepts, "patterns_observed": patterns}

    def fetch(self, peer_name: str, namespace: str, *, workspace: str = "default") -> dict[str, int]:
        peer = self.db.scalar(select(FederationPeer).where(FederationPeer.workspace == workspace, FederationPeer.name == peer_name, FederationPeer.enabled.is_(True)))
        if peer is None:
            raise KeyError(peer_name)
        if not self._namespace_allowed(peer, namespace):
            raise PermissionError("namespace not allowed for peer")
        with httpx.Client(timeout=self.settings.federation_timeout_seconds) as client:
            response = client.get(f"{peer.base_url}/v1/federation/export/{namespace}")
            response.raise_for_status()
            bundle = response.json()
        return self.import_bundle(bundle, workspace=workspace)
