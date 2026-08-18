# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import asyncio
import hashlib
import io
import json
import logging
import os
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import delete, or_, select, text
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, sessionmaker

from .audit import append_event, verify_tenant_chain
from .db import set_tenant_context
from .ids import new_id
from .maintenance import run_tenant_maintenance
from .models import (
    A2ATaskAuthorization,
    Agent,
    AgentProtocolRegistration,
    APIKey,
    Approval,
    ApprovalVote,
    Artifact,
    AuditAnchor,
    BudgetReservation,
    Capability,
    Decision,
    DelegationGrant,
    Event,
    EvidenceObject,
    Execution,
    Incident,
    LegalHold,
    LifecycleClaim,
    MemoryRecord,
    OutboxMessage,
    PolicyBundle,
    ProtocolManifestVersion,
    Provider,
    RuntimeBudget,
    Tenant,
    TenantLifecycleJob,
    Tool,
    WorkloadIdentityBinding,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LifecycleRunResult:
    claimed: int = 0
    completed: int = 0
    retried: int = 0
    failed: int = 0
    outcome_unknown: int = 0
    job_ids: tuple[str, ...] = ()


class TenantLifecycleWorker:
    """Fenced lifecycle executor for exports, governed deletion, and key destruction."""

    def __init__(self, *, session_factory: sessionmaker[Session], service: Any,
                 worker_id: str | None = None) -> None:
        self.session_factory = session_factory
        self.service = service
        self.settings = service.settings
        self.worker_id = worker_id or f"lifecycle-{os.getpid()}-{new_id('wrk')}"
        self._closed = False

    async def close(self) -> None:
        self._closed = True

    async def run_forever(self) -> None:
        while not self._closed:
            result = await self.run_once(limit=self.settings.lifecycle_batch_size)
            if result.claimed == 0:
                await asyncio.sleep(self.settings.lifecycle_poll_milliseconds / 1000)

    async def run_once(self, *, limit: int | None = None) -> LifecycleRunResult:
        claims = self._claim(min(limit or self.settings.lifecycle_batch_size,
                                 self.settings.lifecycle_batch_size))
        if not claims:
            self._run_retention_sweep()
            return LifecycleRunResult()
        semaphore = asyncio.Semaphore(min(len(claims), max(1, self.settings.worker_concurrency)))

        async def process(claim: tuple[str, str, int]) -> str:
            async with semaphore:
                return await asyncio.to_thread(self._process_claim, *claim)

        states = await asyncio.gather(*(process(claim) for claim in claims))
        return LifecycleRunResult(
            claimed=len(claims),
            completed=sum(state == "completed" for state in states),
            retried=sum(state == "retry" for state in states),
            failed=sum(state == "failed" for state in states),
            outcome_unknown=sum(state == "outcome_unknown" for state in states),
            job_ids=tuple(claim[0] for claim in claims),
        )

    def _claim(self, limit: int) -> list[tuple[str, str, int]]:
        now = datetime.now(UTC)
        expires = now + timedelta(seconds=self.settings.lifecycle_lease_seconds)
        with self.session_factory() as session:
            if session.get_bind().dialect.name == "postgresql":
                rows = session.execute(
                    text(
                        "SELECT job_id, tenant_id, fencing_token FROM "
                        "aifence_guard_claim_lifecycle(:worker_id, :batch_size, :lease_seconds)"
                    ),
                    {
                        "worker_id": self.worker_id,
                        "batch_size": limit,
                        "lease_seconds": self.settings.lifecycle_lease_seconds,
                    },
                ).all()
                claimed: list[tuple[str, str, int]] = []
                for row in rows:
                    job_id, tenant_id, fence = str(row[0]), str(row[1]), int(row[2])
                    set_tenant_context(session, tenant_id)
                    claim = session.get(LifecycleClaim, job_id)
                    job = session.scalar(
                        select(TenantLifecycleJob).where(
                            TenantLifecycleJob.tenant_id == tenant_id,
                            TenantLifecycleJob.id == job_id,
                        )
                    )
                    if claim is None or job is None:
                        if claim is not None:
                            claim.status = "dead_lettered"
                            claim.processed_at = now
                        continue
                    job.status = "running"
                    job.lease_owner = self.worker_id
                    job.lease_expires_at = expires
                    job.fencing_token = fence
                    job.attempt_count = claim.attempts
                    job.updated_at = now
                    claimed.append((job_id, tenant_id, fence))
                session.commit()
                return claimed

            statement = (
                select(LifecycleClaim)
                .where(
                    or_(
                        LifecycleClaim.status.in_(["pending", "retry"]),
                        (LifecycleClaim.status == "leased")
                        & (LifecycleClaim.lease_expires_at <= now),
                    ),
                    LifecycleClaim.available_at <= now,
                    LifecycleClaim.attempts < LifecycleClaim.max_attempts,
                )
                .order_by(
                    LifecycleClaim.priority.asc(),
                    LifecycleClaim.available_at.asc(),
                    LifecycleClaim.created_at.asc(),
                    LifecycleClaim.job_id.asc(),
                )
                .limit(limit)
            )
            rows = list(session.scalars(statement))
            claimed = []
            for claim in rows:
                claim.status = "leased"
                claim.lease_owner = self.worker_id
                claim.lease_expires_at = expires
                claim.fencing_token += 1
                claim.attempts += 1
                set_tenant_context(session, claim.tenant_id)
                job = session.scalar(
                    select(TenantLifecycleJob).where(
                        TenantLifecycleJob.tenant_id == claim.tenant_id,
                        TenantLifecycleJob.id == claim.job_id,
                    )
                )
                if job is None:
                    claim.status = "dead_lettered"
                    claim.processed_at = now
                    continue
                job.status = "running"
                job.lease_owner = self.worker_id
                job.lease_expires_at = expires
                job.fencing_token = claim.fencing_token
                job.attempt_count = claim.attempts
                job.updated_at = now
                claimed.append((claim.job_id, claim.tenant_id, claim.fencing_token))
            session.commit()
            return claimed

    def _process_claim(self, job_id: str, tenant_id: str, fence: int) -> str:
        try:
            with self.session_factory() as session:
                set_tenant_context(session, tenant_id)
                job = self._locked_job(session, job_id, tenant_id, fence)
                if job.job_type == "export":
                    result = self._export_tenant(session, job)
                elif job.job_type == "delete":
                    result = self._delete_tenant(session, job)
                elif job.job_type == "crypto_erase":
                    result = self._crypto_erase(session, job)
                else:
                    raise ValueError(f"unsupported asynchronous lifecycle job: {job.job_type}")
                self._complete(session, job, fence, result)
                return "completed"
        except _RetryLater as exc:
            self._retry(job_id, tenant_id, fence, str(exc), exc.delay_seconds)
            return "retry"
        except Exception as exc:
            logger.exception("tenant lifecycle job failed", extra={"job_id": job_id})
            return self._fail(job_id, tenant_id, fence, exc)

    def _locked_job(self, session: Session, job_id: str, tenant_id: str,
                    fence: int) -> TenantLifecycleJob:
        statement = select(TenantLifecycleJob).where(
            TenantLifecycleJob.tenant_id == tenant_id,
            TenantLifecycleJob.id == job_id,
        )
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update()
        job = session.scalar(statement)
        if job is None:
            raise RuntimeError("lifecycle job disappeared")
        if job.lease_owner != self.worker_id or job.fencing_token != fence:
            raise RuntimeError("lifecycle lease is stale")
        return job

    def _complete(self, session: Session, job: TenantLifecycleJob, fence: int,
                  result: dict[str, Any]) -> None:
        now = datetime.now(UTC)
        claim = session.get(LifecycleClaim, job.id)
        if claim is None or claim.lease_owner != self.worker_id or claim.fencing_token != fence:
            raise RuntimeError("lifecycle completion fence is stale")
        job.status = "completed"; job.result = result; job.completed_at = now
        job.updated_at = now; job.lease_owner = None; job.lease_expires_at = None
        job.reconciliation_status = "not_required"
        claim.status = "processed"; claim.processed_at = now
        claim.lease_owner = None; claim.lease_expires_at = None
        append_event(session, self.service.signing_key, event_id=new_id("evt"),
                     tenant_id=job.tenant_id, trace_id=new_id("trc"), parent_event_id=None,
                     event_type="tenant.lifecycle_completed",
                     payload={"job_id": job.id, "job_type": job.job_type,
                              "result_hash": hashlib.sha256(json.dumps(result, sort_keys=True,
                              default=str, separators=(",", ":")).encode()).hexdigest()})
        session.commit()

    def _retry(self, job_id: str, tenant_id: str, fence: int, error: str,
               delay_seconds: int) -> None:
        with self.session_factory() as session:
            set_tenant_context(session, tenant_id)
            job = self._locked_job(session, job_id, tenant_id, fence)
            claim = session.get(LifecycleClaim, job_id)
            if claim is None or claim.fencing_token != fence:
                return
            available = datetime.now(UTC) + timedelta(seconds=max(1, delay_seconds))
            # A governed deferral is not a failed execution attempt. Returning the claim to
            # its prior attempt count prevents long legal holds or grace periods from
            # exhausting max_attempts while still bounding genuine failures in _fail().
            if claim.attempts > 0:
                claim.attempts -= 1
            job.attempt_count = claim.attempts
            job.status = "pending"; job.available_at = available; job.last_error = error[:4096]
            job.lease_owner = None; job.lease_expires_at = None; job.updated_at = datetime.now(UTC)
            claim.status = "retry"; claim.available_at = available; claim.lease_owner = None
            claim.lease_expires_at = None
            session.commit()

    def _fail(self, job_id: str, tenant_id: str, fence: int, exc: Exception) -> str:
        with self.session_factory() as session:
            set_tenant_context(session, tenant_id)
            try:
                job = self._locked_job(session, job_id, tenant_id, fence)
            except RuntimeError:
                return "failed"
            claim = session.get(LifecycleClaim, job_id)
            if claim is None or claim.fencing_token != fence:
                return "failed"
            destructive_unknown = job.job_type == "crypto_erase" and job.external_effect_started_at is not None
            exhausted = job.attempt_count >= job.max_attempts
            if destructive_unknown:
                state = "outcome_unknown"
                job.reconciliation_status = "required"
            elif not exhausted:
                delay = min(300, 2 ** min(job.attempt_count, 8))
                available = datetime.now(UTC) + timedelta(seconds=delay)
                job.status = "pending"; job.available_at = available
                claim.status = "retry"; claim.available_at = available
                state = "retry"
            else:
                job.status = "failed"; claim.status = "dead_lettered"; claim.processed_at = datetime.now(UTC)
                state = "failed"
            if destructive_unknown:
                job.status = "outcome_unknown"; claim.status = "outcome_unknown"; claim.processed_at = datetime.now(UTC)
            job.last_error = f"{type(exc).__name__}: {exc}"[:4096]
            job.lease_owner = None; job.lease_expires_at = None; job.updated_at = datetime.now(UTC)
            claim.lease_owner = None; claim.lease_expires_at = None
            session.commit()
            return state

    def _active_hold(self, session: Session, tenant_id: str) -> LegalHold | None:
        now = datetime.now(UTC)
        return session.scalar(select(LegalHold).where(
            LegalHold.tenant_id == tenant_id,
            LegalHold.status == "active",
            or_(LegalHold.expires_at.is_(None), LegalHold.expires_at > now),
        ).limit(1))

    def _export_tenant(self, session: Session, job: TenantLifecycleJob) -> dict[str, Any]:
        bundle = io.BytesIO()
        entries: dict[str, str] = {}
        with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6, strict_timestamps=True) as archive:
            for model in self._export_models():
                rows = list(session.scalars(select(model).where(model.tenant_id == job.tenant_id)))
                document = [self._safe_row(row) for row in rows]
                self._write_zip(archive, entries, f"records/{model.__tablename__}.json",
                                json.dumps(document, sort_keys=True, default=str,
                                           separators=(",", ":")).encode())
            tenant = session.get(Tenant, job.tenant_id)
            self._write_zip(archive, entries, "records/tenant.json",
                            json.dumps(self._safe_row(tenant), sort_keys=True, default=str,
                                       separators=(",", ":")).encode())
            memories = list(session.scalars(select(MemoryRecord).where(MemoryRecord.tenant_id == job.tenant_id)))
            for memory in memories:
                try:
                    content = self.service.tenant_crypto.decrypt(
                        session, job.tenant_id, memory.encrypted_content,
                        context=f"memory:{job.tenant_id}:{memory.id}".encode())
                except Exception as exc:
                    content = json.dumps({"unavailable": type(exc).__name__}).encode()
                self._write_zip(archive, entries, f"content/memory/{memory.id}.bin", content)
            artifacts = list(session.scalars(select(Artifact).where(Artifact.tenant_id == job.tenant_id)))
            for artifact in artifacts:
                try:
                    encrypted = self.service.artifact_store.get(artifact.storage_key) if artifact.storage_key else artifact.encrypted_blob
                    if encrypted is None:
                        raise FileNotFoundError("artifact ciphertext unavailable")
                    content = self.service.tenant_crypto.decrypt(
                        session, job.tenant_id, encrypted,
                        context=f"{job.tenant_id}:{artifact.id}:{artifact.sha256}".encode())
                except Exception as exc:
                    content = json.dumps({"unavailable": type(exc).__name__}).encode()
                self._write_zip(archive, entries, f"content/artifacts/{artifact.id}", content)
            verification = verify_tenant_chain(session, self.service.signing_key, job.tenant_id)
            manifest = {
                "format": "aifence.tenant-export.v1",
                "tenant_id": job.tenant_id,
                "job_id": job.id,
                "created_at": datetime.now(UTC).isoformat(),
                "entries": entries,
                "audit_verification": verification,
            }
            manifest_bytes = json.dumps(manifest, sort_keys=True, default=str,
                                        separators=(",", ":")).encode()
            archive.writestr("MANIFEST.json", manifest_bytes)
        plaintext = bundle.getvalue()
        digest = hashlib.sha256(plaintext).hexdigest()
        encrypted = self.service.tenant_crypto.encrypt(
            session, job.tenant_id, plaintext,
            context=f"tenant-export:{job.tenant_id}:{job.id}:{digest}".encode())
        storage_key = self.service.artifact_store.put_object(
            job.tenant_id, "tenant-exports", job.id, encrypted,
            metadata={"sha256": digest, "job-id": job.id},
        )
        evidence = EvidenceObject(
            id=new_id("evi"), tenant_id=job.tenant_id, namespace="tenant-exports",
            external_id=job.id, media_type="application/zip", size_bytes=len(plaintext),
            sha256=digest, storage_key=storage_key,
            metadata_json={"manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest()},
            immutable=True,
        )
        session.add(evidence); job.result_storage_key = storage_key
        return {"evidence_object_id": evidence.id, "storage_key": storage_key,
                "sha256": digest, "size_bytes": len(plaintext), "entry_count": len(entries),
                "audit_valid": bool(verification.get("valid")),
                "audit_verification": verification}

    def _delete_tenant(self, session: Session, job: TenantLifecycleJob) -> dict[str, Any]:
        hold = self._active_hold(session, job.tenant_id)
        if hold is not None:
            raise _RetryLater(f"tenant is protected by legal hold {hold.id}", 3600)
        tenant = session.get(Tenant, job.tenant_id)
        if tenant is None:
            raise RuntimeError("tenant disappeared")
        grace_days = max(0, int(job.parameters.get("grace_period_days", 30)))
        requested = tenant.deletion_requested_at or job.created_at
        if requested.tzinfo is None:
            requested = requested.replace(tzinfo=UTC)
        due = requested + timedelta(days=grace_days)
        if datetime.now(UTC) < due:
            raise _RetryLater("tenant deletion grace period has not elapsed",
                              max(60, int((due - datetime.now(UTC)).total_seconds())))
        deleted_objects = 0
        for artifact in list(session.scalars(select(Artifact).where(Artifact.tenant_id == job.tenant_id))):
            if artifact.storage_key:
                try:
                    self.service.artifact_store.delete(artifact.storage_key); deleted_objects += 1
                except FileNotFoundError:
                    pass
        for evidence in list(session.scalars(select(EvidenceObject).where(
                EvidenceObject.tenant_id == job.tenant_id,
                EvidenceObject.namespace != "deletion-certificates"))):
            try:
                self.service.artifact_store.delete(evidence.storage_key); deleted_objects += 1
            except FileNotFoundError:
                pass
        counts: dict[str, int] = {}
        for model in self._deletion_models():
            result = session.execute(delete(model).where(model.tenant_id == job.tenant_id))
            counts[model.__tablename__] = int(result.rowcount or 0)
        session.execute(delete(APIKey).where(APIKey.tenant_id == job.tenant_id,
                                             APIKey.id != job.requested_by_key_id))
        remaining = session.get(APIKey, job.requested_by_key_id)
        if remaining is not None:
            remaining.status = "lifecycle_only"
            remaining.scopes = ["tenants:lifecycle", "audit:read", "audit:verify"]
        tenant.status = "deleted"; tenant.deleted_at = datetime.now(UTC)
        certificate = {"tenant_id": job.tenant_id, "job_id": job.id,
                       "completed_at": tenant.deleted_at.isoformat(),
                       "deleted_records": counts, "deleted_objects": deleted_objects,
                       "audit_retained": True}
        return certificate

    def _crypto_erase(self, session: Session, job: TenantLifecycleJob) -> dict[str, Any]:
        hold = self._active_hold(session, job.tenant_id)
        if hold is not None:
            raise _RetryLater(f"tenant is protected by legal hold {hold.id}", 3600)
        if not self.settings.tenant_key_destroy_enabled:
            raise RuntimeError("tenant key destruction is disabled")
        migrated = self._migrate_legacy_ciphertexts(session, job.tenant_id)
        job.external_effect_started_at = datetime.now(UTC)
        session.commit()
        # Reacquire tenant context and lease after crossing the commit boundary.
        set_tenant_context(session, job.tenant_id)
        job = self._locked_job(session, job.id, job.tenant_id, job.fencing_token)
        receipt = self.service.tenant_crypto.destroy(
            session, job.tenant_id, reason=str(job.parameters.get("reason", "tenant crypto erasure")))
        tenant = session.get(Tenant, job.tenant_id)
        if tenant is not None:
            tenant.status = "crypto_erased"; tenant.crypto_erased_at = datetime.now(UTC)
        return {"migrated_records": migrated, "destruction_receipt": receipt,
                "irrecoverable_after": datetime.now(UTC).isoformat()}

    def _migrate_legacy_ciphertexts(self, session: Session, tenant_id: str) -> dict[str, int]:
        counts = {"memory": 0, "artifacts": 0, "providers": 0, "tools": 0, "protocols": 0}
        for row in session.scalars(select(MemoryRecord).where(MemoryRecord.tenant_id == tenant_id)):
            if not self.service.tenant_crypto.is_tenant_envelope(row.encrypted_content):
                context = f"memory:{tenant_id}:{row.id}".encode()
                plain = self.service.cipher.decrypt(row.encrypted_content, context=context)
                row.encrypted_content = self.service.tenant_crypto.encrypt(session, tenant_id, plain, context=context)
                counts["memory"] += 1
        for row in session.scalars(select(Artifact).where(Artifact.tenant_id == tenant_id)):
            encrypted = self.service.artifact_store.get(row.storage_key) if row.storage_key else row.encrypted_blob
            if encrypted is not None and not self.service.tenant_crypto.is_tenant_envelope(encrypted):
                context = f"{tenant_id}:{row.id}:{row.sha256}".encode()
                plain = self.service.cipher.decrypt(encrypted, context=context)
                rotated = self.service.tenant_crypto.encrypt(session, tenant_id, plain, context=context)
                if row.storage_key:
                    migration_object_id = f"{row.id}_tc_{hashlib.sha256(rotated).hexdigest()[:12]}"
                    row.storage_key = self.service.artifact_store.put(
                        tenant_id, migration_object_id, rotated
                    )
                else:
                    row.encrypted_blob = rotated
                counts["artifacts"] += 1
        for model, label, suffix in ((Provider, "providers", "provider"), (Tool, "tools", "tool")):
            for row in session.scalars(select(model).where(model.tenant_id == tenant_id)):
                encrypted = row.encrypted_auth_value
                if not self.service.tenant_crypto.is_tenant_envelope(encrypted):
                    context = f"{tenant_id}:{row.id}:{suffix}".encode()
                    plain = self.service.cipher.decrypt(encrypted, context=context)
                    row.encrypted_auth_value = self.service.tenant_crypto.encrypt(session, tenant_id, plain, context=context)
                    counts[label] += 1
        for row in session.scalars(select(AgentProtocolRegistration).where(
                AgentProtocolRegistration.tenant_id == tenant_id,
                AgentProtocolRegistration.encrypted_auth_value.is_not(None))):
            encrypted = row.encrypted_auth_value
            if encrypted is not None and not self.service.tenant_crypto.is_tenant_envelope(encrypted):
                context = f"{tenant_id}:{row.id}:protocol".encode()
                plain = self.service.cipher.decrypt(encrypted, context=context)
                row.encrypted_auth_value = self.service.tenant_crypto.encrypt(session, tenant_id, plain, context=context)
                counts["protocols"] += 1
        session.flush()
        return counts

    def _run_retention_sweep(self) -> None:
        with self.session_factory() as session:
            if session.get_bind().dialect.name == "postgresql":
                tenants = [
                    str(row[0])
                    for row in session.execute(
                        text("SELECT tenant_id FROM aifence_guard_list_maintenance_tenants(:limit)"),
                        {"limit": self.settings.lifecycle_batch_size},
                    ).all()
                ]
            else:
                tenants = list(session.scalars(select(Tenant.id).where(Tenant.status.in_([
                    "active", "suspended", "deletion_pending"
                ])).order_by(Tenant.id.asc()).limit(self.settings.lifecycle_batch_size)))
        for tenant_id in tenants:
            try:
                with self.session_factory() as session:
                    set_tenant_context(session, tenant_id)
                    if session.bind and session.bind.dialect.name == "postgresql":
                        locked = session.scalar(text(
                            "SELECT pg_try_advisory_xact_lock(hashtextextended(:tenant_id, 0))"
                        ), {"tenant_id": tenant_id})
                        if not locked:
                            continue
                    run_tenant_maintenance(session, self.service, tenant_id=tenant_id,
                                           batch_size=min(500, self.settings.max_page_size))
            except Exception:
                logger.exception("tenant retention sweep failed", extra={"tenant_id": tenant_id})

    @staticmethod
    def _write_zip(archive: zipfile.ZipFile, entries: dict[str, str], name: str,
                   content: bytes) -> None:
        if name.startswith("/") or ".." in name.split("/"):
            raise ValueError("unsafe export entry name")
        archive.writestr(name, content)
        entries[name] = hashlib.sha256(content).hexdigest()

    @staticmethod
    def _safe_row(row: Any) -> dict[str, Any]:
        if row is None:
            return {}
        excluded = {"secret_digest", "encrypted_auth_value", "encrypted_content",
                    "encrypted_blob", "wrapped_local_key"}
        result: dict[str, Any] = {}
        for column in inspect(row).mapper.column_attrs:
            name = column.key
            if name in excluded:
                continue
            value = getattr(row, name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = str(value)
            elif isinstance(value, bytes):
                value = {"omitted_binary_bytes": len(value)}
            result[name] = value
        return result

    @staticmethod
    def _export_models() -> tuple[Any, ...]:
        return (APIKey, Agent, PolicyBundle, Decision, Approval, ApprovalVote, Event,
                Incident, Artifact, Capability, Provider, Tool, Execution, OutboxMessage,
                WorkloadIdentityBinding, AuditAnchor, DelegationGrant, RuntimeBudget,
                BudgetReservation, A2ATaskAuthorization, TenantLifecycleJob,
                AgentProtocolRegistration, ProtocolManifestVersion, LegalHold, EvidenceObject)

    @staticmethod
    def _deletion_models() -> tuple[Any, ...]:
        return (A2ATaskAuthorization, ProtocolManifestVersion, AgentProtocolRegistration,
                BudgetReservation, RuntimeBudget, DelegationGrant, MemoryRecord,
                WorkloadIdentityBinding, OutboxMessage, Execution, Capability,
                ApprovalVote, Approval, Decision, Provider, Tool, Artifact, PolicyBundle, Agent)


class _RetryLater(RuntimeError):
    def __init__(self, message: str, delay_seconds: int) -> None:
        super().__init__(message)
        self.delay_seconds = delay_seconds
