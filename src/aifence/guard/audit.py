# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from sqlalchemy import Select, desc, select, text
from sqlalchemy.orm import Session

from .crypto import SigningProvider, canonical_json, sha256_hex
from .models import AuditCheckpoint, Event, SigningPublicKey

ZERO_HASH = "0" * 64


def append_event(
    session: Session,
    signing_key: SigningProvider,
    *,
    event_id: str,
    tenant_id: str,
    trace_id: str,
    parent_event_id: str | None,
    event_type: str,
    payload: dict[str, Any],
) -> Event:
    if session.bind and session.bind.dialect.name == "postgresql":
        session.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:tenant, 0))"), {"tenant": tenant_id})
    latest_stmt: Select[tuple[Event]] = (
        select(Event)
        .where(Event.tenant_id == tenant_id)
        .order_by(desc(Event.sequence))
        .limit(1)
    )
    if session.bind and session.bind.dialect.name == "postgresql":
        latest_stmt = latest_stmt.with_for_update()
    latest = session.scalar(latest_stmt)
    sequence = 1 if latest is None else latest.sequence + 1
    previous_hash = ZERO_HASH if latest is None else latest.event_hash
    created_at = datetime.now(UTC)
    envelope = {
        "id": event_id,
        "tenant_id": tenant_id,
        "trace_id": trace_id,
        "parent_event_id": parent_event_id,
        "sequence": sequence,
        "event_type": event_type,
        "payload": payload,
        "previous_hash": previous_hash,
        "key_id": signing_key.key_id,
        "created_at": created_at.isoformat(),
    }
    event_hash = sha256_hex(bytes.fromhex(previous_hash) + canonical_json(envelope))
    signature = signing_key.sign(bytes.fromhex(event_hash))
    event = Event(
        id=event_id,
        tenant_id=tenant_id,
        trace_id=trace_id,
        parent_event_id=parent_event_id,
        sequence=sequence,
        event_type=event_type,
        payload=payload,
        previous_hash=previous_hash,
        event_hash=event_hash,
        signature=signature,
        key_id=signing_key.key_id,
        created_at=created_at,
    )
    session.add(event)
    session.flush()
    interval = int(session.info.get("audit_checkpoint_interval", 1000))
    if interval > 0 and sequence % interval == 0:
        checkpoint_envelope = {
            "tenant_id": tenant_id,
            "sequence": sequence,
            "head_hash": event_hash,
            "key_id": signing_key.key_id,
        }
        checkpoint = AuditCheckpoint(
            id=f"chk_{event_id.removeprefix('evt_')}",
            tenant_id=tenant_id,
            sequence=sequence,
            head_hash=event_hash,
            signature=signing_key.sign(canonical_json(checkpoint_envelope)),
            key_id=signing_key.key_id,
            created_at=created_at,
        )
        session.add(checkpoint)
        session.flush()
    return event


def verify_tenant_chain(session: Session, signing_key: SigningProvider, tenant_id: str) -> dict[str, Any]:
    keyring: dict[str, Ed25519PublicKey] = {signing_key.key_id: signing_key.public_key}
    for record in session.scalars(select(SigningPublicKey)):
        loaded = serialization.load_pem_public_key(record.public_pem.encode())
        if isinstance(loaded, Ed25519PublicKey):
            keyring[record.key_id] = loaded
    events = session.scalars(
        select(Event).where(Event.tenant_id == tenant_id).order_by(Event.sequence.asc())
    ).yield_per(1000)
    previous_hash = ZERO_HASH
    expected_sequence = 1
    event_count = 0
    for event in events:
        event_count += 1
        if event.sequence != expected_sequence:
            return {"valid": False, "event_id": event.id, "reason": "sequence_gap"}
        if event.previous_hash != previous_hash:
            return {"valid": False, "event_id": event.id, "reason": "previous_hash_mismatch"}
        created = event.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        envelope = {
            "id": event.id,
            "tenant_id": event.tenant_id,
            "trace_id": event.trace_id,
            "parent_event_id": event.parent_event_id,
            "sequence": event.sequence,
            "event_type": event.event_type,
            "payload": event.payload,
            "previous_hash": event.previous_hash,
            "key_id": event.key_id,
            "created_at": created.isoformat(),
        }
        calculated = sha256_hex(bytes.fromhex(previous_hash) + canonical_json(envelope))
        if calculated != event.event_hash:
            return {"valid": False, "event_id": event.id, "reason": "event_hash_mismatch"}
        public_key = keyring.get(event.key_id)
        if public_key is None:
            return {"valid": False, "event_id": event.id, "reason": "signing_key_unknown"}
        try:
            import base64
            padding = "=" * (-len(event.signature) % 4)
            public_key.verify(base64.urlsafe_b64decode(event.signature + padding), bytes.fromhex(event.event_hash))
        except Exception:
            return {"valid": False, "event_id": event.id, "reason": "signature_invalid"}
        previous_hash = event.event_hash
        expected_sequence += 1
    checkpoints = session.scalars(
        select(AuditCheckpoint).where(AuditCheckpoint.tenant_id == tenant_id).order_by(AuditCheckpoint.sequence.asc())
    ).yield_per(1000)
    for checkpoint in checkpoints:
        event = session.scalar(select(Event).where(
            Event.tenant_id == tenant_id, Event.sequence == checkpoint.sequence
        ))
        if event is None or event.event_hash != checkpoint.head_hash:
            return {"valid": False, "checkpoint_id": checkpoint.id, "reason": "checkpoint_head_mismatch"}
        public_key = keyring.get(checkpoint.key_id)
        if public_key is None:
            return {"valid": False, "checkpoint_id": checkpoint.id, "reason": "checkpoint_key_unknown"}
        envelope = {
            "tenant_id": tenant_id,
            "sequence": checkpoint.sequence,
            "head_hash": checkpoint.head_hash,
            "key_id": checkpoint.key_id,
        }
        try:
            import base64
            padding = "=" * (-len(checkpoint.signature) % 4)
            public_key.verify(
                base64.urlsafe_b64decode(checkpoint.signature + padding),
                canonical_json(envelope),
            )
        except Exception:
            return {"valid": False, "checkpoint_id": checkpoint.id, "reason": "checkpoint_signature_invalid"}
    return {"valid": True, "events": event_count, "head_hash": previous_hash}


def export_tenant_audit(
    session: Session, signing_key: SigningProvider, tenant_id: str, output: Path
) -> dict[str, Any]:
    """Export a verified tenant audit stream and a signed detached manifest."""
    verification = verify_tenant_chain(session, signing_key, tenant_id)
    if not verification.get("valid"):
        raise ValueError(f"cannot export an invalid audit chain: {verification}")

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    digest = hashlib.sha256()
    event_count = 0
    checkpoint_count = 0
    with temporary.open("wb") as handle:
        for event in session.scalars(
            select(Event).where(Event.tenant_id == tenant_id).order_by(Event.sequence.asc())
        ).yield_per(1000):
            created = event.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=UTC)
            record = {
                "record_type": "event",
                "id": event.id,
                "tenant_id": event.tenant_id,
                "trace_id": event.trace_id,
                "parent_event_id": event.parent_event_id,
                "sequence": event.sequence,
                "event_type": event.event_type,
                "payload": event.payload,
                "previous_hash": event.previous_hash,
                "event_hash": event.event_hash,
                "signature": event.signature,
                "key_id": event.key_id,
                "created_at": created.isoformat(),
            }
            line = canonical_json(record) + b"\n"
            handle.write(line)
            digest.update(line)
            event_count += 1
        for checkpoint in session.scalars(
            select(AuditCheckpoint)
            .where(AuditCheckpoint.tenant_id == tenant_id)
            .order_by(AuditCheckpoint.sequence.asc())
        ).yield_per(1000):
            created = checkpoint.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=UTC)
            record = {
                "record_type": "checkpoint",
                "id": checkpoint.id,
                "tenant_id": checkpoint.tenant_id,
                "sequence": checkpoint.sequence,
                "head_hash": checkpoint.head_hash,
                "signature": checkpoint.signature,
                "key_id": checkpoint.key_id,
                "created_at": created.isoformat(),
            }
            line = canonical_json(record) + b"\n"
            handle.write(line)
            digest.update(line)
            checkpoint_count += 1
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, output)

    generated_at = datetime.now(UTC).isoformat()
    unsigned_manifest = {
        "format": "aifence.audit-export.v1",
        "tenant_id": tenant_id,
        "generated_at": generated_at,
        "archive": output.name,
        "sha256": digest.hexdigest(),
        "events": event_count,
        "checkpoints": checkpoint_count,
        "head_hash": verification.get("head_hash", ZERO_HASH),
        "key_id": signing_key.key_id,
    }
    manifest = {
        **unsigned_manifest,
        "signature": signing_key.sign(canonical_json(unsigned_manifest)),
    }
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {**manifest, "archive_path": str(output), "manifest_path": str(manifest_path)}
