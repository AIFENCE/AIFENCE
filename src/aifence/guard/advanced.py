# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import fnmatch
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from .audit import append_event, verify_tenant_chain
from .audit_anchor import build_anchor_backend, build_anchor_envelope
from .auth import KNOWN_SCOPES, AuthContext
from .crypto import hash_object
from .detectors import calculate_risk, run_detectors
from .errors import AuthorizationError, ConflictError, NotFoundError, PolicyError
from .ids import new_id
from .metrics import (
    AUDIT_ANCHOR_EVENTS,
    BUDGET_EVENTS,
    DELEGATION_EVENTS,
    MEMORY_EVENTS,
    POLICY_ROLLOUT_EVENTS,
    PROTOCOL_EVENTS,
    TENANT_LIFECYCLE_EVENTS,
)
from .models import (
    A2ATaskAuthorization,
    Agent,
    AgentProtocolRegistration,
    Approval,
    AuditAnchor,
    AuditAnchorClaim,
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
    RuntimeBudget,
    Tenant,
    TenantKeyRoute,
    TenantLifecycleJob,
    WorkloadIdentityBinding,
)
from .network import validate_endpoint
from .policy import PolicyEngine, validate_policy_document
from .protocols import discover_protocol_manifest
from .schemas import (
    A2ATaskRequest,
    AuditAnchorQuorumResponse,
    AuditAnchorResponse,
    BudgetReservationRequest,
    BudgetReservationResponse,
    BudgetSettlementRequest,
    DelegationGrantCreate,
    DelegationGrantResponse,
    Finding,
    LegalHoldCreate,
    LegalHoldResponse,
    MemoryRecordResponse,
    MemoryStatusUpdate,
    MemoryWriteRequest,
    OperatorPostureResponse,
    PolicyDiffRequest,
    PolicyDiffResponse,
    PolicySimulationCaseResult,
    PolicySimulationRequest,
    PolicySimulationResponse,
    PolicyValidationResponse,
    ProtocolManifestVersionResponse,
    ProtocolRegistrationCreate,
    ProtocolRegistrationResponse,
    RuntimeBudgetCreate,
    RuntimeBudgetResponse,
    TenantLifecycleJobResponse,
    TenantLifecycleRequest,
    WorkloadIdentityBindingCreate,
    WorkloadIdentityBindingResponse,
)
from .workload_identity import parse_spiffe_id

_NUMERIC_BUDGET_KEYS = {"steps", "tool_calls", "model_tokens", "elapsed_seconds", "amount_usd",
                        "delegations", "messages", "artifacts", "network_bytes"}


class AdvancedOperations:
    def __init__(self, service: Any) -> None:
        self.service = service
        self.settings = service.settings

    def create_workload_binding(self, session: Session, auth: AuthContext,
                                body: WorkloadIdentityBindingCreate) -> WorkloadIdentityBindingResponse:
        auth.require("workloads:write")
        spiffe_id, trust_domain = parse_spiffe_id(body.spiffe_id)
        if self.settings.workload_trust_domains and trust_domain not in self.settings.workload_trust_domains:
            raise AuthorizationError("SPIFFE trust domain is not configured")
        agent = session.scalar(select(Agent).where(Agent.tenant_id == auth.tenant_id, Agent.id == body.agent_id))
        if agent is None or agent.status != "active":
            raise NotFoundError("agent does not exist or is inactive")
        if agent.workload_identity != spiffe_id:
            raise ConflictError("SPIFFE ID must match the immutable agent manifest")
        unknown = set(body.scopes) - KNOWN_SCOPES - {"*"}
        if unknown:
            raise ConflictError("workload binding contains unknown scopes", details={"unknown_scopes": sorted(unknown)})
        if "*" not in auth.scopes and not set(body.scopes).issubset(auth.scopes):
            raise AuthorizationError("workload binding cannot delegate scopes the caller lacks")
        row = WorkloadIdentityBinding(
            id=new_id("wli"), tenant_id=auth.tenant_id, spiffe_id=spiffe_id,
            agent_id=agent.id, instance_pattern=body.instance_pattern,
            principal_type=body.principal_type, principal_id=body.principal_id,
            scopes=sorted(set(body.scopes)), trust_domain=trust_domain,
            status="active", created_by_key_id=auth.key_id,
        )
        session.add(row)
        append_event(session, self.service.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                     trace_id=new_id("trc"), parent_event_id=None, event_type="workload_identity.registered",
                     payload={"binding_id": row.id, "spiffe_id": spiffe_id, "agent_id": agent.id, "scopes": row.scopes})
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ConflictError("SPIFFE identity is already registered") from exc
        return self._workload_response(row)

    def list_workload_bindings(self, session: Session, auth: AuthContext) -> list[WorkloadIdentityBindingResponse]:
        auth.require("workloads:read")
        rows = session.scalars(select(WorkloadIdentityBinding).where(
            WorkloadIdentityBinding.tenant_id == auth.tenant_id
        ).order_by(WorkloadIdentityBinding.created_at.desc()).limit(self.settings.max_page_size))
        return [self._workload_response(row) for row in rows]

    def revoke_workload_binding(self, session: Session, auth: AuthContext, binding_id: str,
                                reason: str) -> WorkloadIdentityBindingResponse:
        auth.require("workloads:write")
        row = session.scalar(select(WorkloadIdentityBinding).where(
            WorkloadIdentityBinding.tenant_id == auth.tenant_id, WorkloadIdentityBinding.id == binding_id))
        if row is None: raise NotFoundError("workload identity binding not found")
        row.status = "revoked"; row.revoked_at = datetime.now(UTC)
        append_event(session, self.service.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                     trace_id=new_id("trc"), parent_event_id=None, event_type="workload_identity.revoked",
                     payload={"binding_id": row.id, "reason": reason, "revoked_by": auth.key_id})
        session.commit(); return self._workload_response(row)

    def validate_policy(self, auth: AuthContext, document: dict[str, Any]) -> PolicyValidationResponse:
        auth.require("policies:read")
        errors: list[str] = []; warnings: list[str] = []
        try: validate_policy_document(document)
        except PolicyError as exc: errors.append(exc.message)
        rules = document.get("rules", []) if isinstance(document, dict) else []
        tests = document.get("tests", []) if isinstance(document, dict) else []
        if not tests: warnings.append("policy bundle has no embedded regression tests")
        if isinstance(rules, list) and not any(isinstance(r, dict) and r.get("effect", {}).get("outcome") == "deny" for r in rules):
            warnings.append("policy has no explicit deny rule")
        return PolicyValidationResponse(valid=not errors, document_hash=hash_object(document),
            rule_count=len(rules) if isinstance(rules, list) else 0,
            test_count=len(tests) if isinstance(tests, list) else 0, errors=errors, warnings=warnings)

    def simulate_policy(self, session: Session, auth: AuthContext,
                        body: PolicySimulationRequest) -> PolicySimulationResponse:
        validation = self.validate_policy(auth, body.document)
        if not validation.valid:
            raise PolicyError("policy simulation rejected invalid document", details={"errors": validation.errors})
        engine = PolicyEngine(self.service.policy_engine.baseline)
        results: list[PolicySimulationCaseResult] = []; counts: dict[str, int] = {}; passed = 0
        for case in body.cases:
            agent = session.scalar(select(Agent).where(Agent.tenant_id == auth.tenant_id,
                (Agent.id == case.request.agent.id) | (Agent.external_id == case.request.agent.id)))
            findings = run_detectors(case.request, agent); risk = calculate_risk(case.request, findings)
            evaluated = engine.evaluate(case.request.model_dump(mode="json"), findings, risk, body.document)
            expected = None if not case.expected_outcomes else evaluated.outcome in case.expected_outcomes
            passed += expected is not False; counts[evaluated.outcome] = counts.get(evaluated.outcome, 0) + 1
            results.append(PolicySimulationCaseResult(name=case.name, outcome=evaluated.outcome,
                risk_score=risk, matched_rule=evaluated.matched_rule, reasons=evaluated.reasons,
                constraints=evaluated.constraints, expected=expected))
        return PolicySimulationResponse(document_hash=validation.document_hash, total=len(results), passed=passed,
            failed=len(results)-passed, outcome_counts=counts, results=results)

    def diff_policy(self, session: Session, auth: AuthContext, body: PolicyDiffRequest) -> PolicyDiffResponse:
        current_validation = self.validate_policy(auth, body.current_document)
        proposed_validation = self.validate_policy(auth, body.proposed_document)
        if not current_validation.valid or not proposed_validation.valid:
            raise PolicyError(
                "policy diff rejected invalid document",
                details={
                    "current_errors": current_validation.errors,
                    "proposed_errors": proposed_validation.errors,
                },
            )

        def rule_map(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
            return {
                str(rule["id"]): rule
                for rule in document.get("rules", [])
                if isinstance(rule, dict) and isinstance(rule.get("id"), str)
            }

        current_rules = rule_map(body.current_document)
        proposed_rules = rule_map(body.proposed_document)
        added = sorted(set(proposed_rules) - set(current_rules))
        removed = sorted(set(current_rules) - set(proposed_rules))
        changed = sorted(
            rule_id
            for rule_id in set(current_rules) & set(proposed_rules)
            if hash_object(current_rules[rule_id]) != hash_object(proposed_rules[rule_id])
        )
        outcome_delta: dict[str, int] = {}
        changed_cases: list[dict[str, Any]] = []
        if body.cases:
            current = self.simulate_policy(
                session,
                auth,
                PolicySimulationRequest(document=body.current_document, cases=body.cases),
            )
            proposed = self.simulate_policy(
                session,
                auth,
                PolicySimulationRequest(document=body.proposed_document, cases=body.cases),
            )
            names = {result.name: result for result in current.results}
            for proposed_result in proposed.results:
                current_result = names[proposed_result.name]
                if current_result.outcome != proposed_result.outcome or current_result.constraints != proposed_result.constraints:
                    changed_cases.append(
                        {
                            "name": proposed_result.name,
                            "current_outcome": current_result.outcome,
                            "proposed_outcome": proposed_result.outcome,
                            "current_constraints": current_result.constraints,
                            "proposed_constraints": proposed_result.constraints,
                        }
                    )
                outcome_delta[proposed_result.outcome] = outcome_delta.get(proposed_result.outcome, 0) + 1
                outcome_delta[current_result.outcome] = outcome_delta.get(current_result.outcome, 0) - 1
            outcome_delta = {key: value for key, value in sorted(outcome_delta.items()) if value}
        return PolicyDiffResponse(
            current_hash=current_validation.document_hash,
            proposed_hash=proposed_validation.document_hash,
            added_rules=added,
            removed_rules=removed,
            changed_rules=changed,
            default_changed=hash_object(body.current_document.get("default"))
            != hash_object(body.proposed_document.get("default")),
            outcome_delta=outcome_delta,
            changed_cases=changed_cases,
            current_validation=current_validation,
            proposed_validation=proposed_validation,
        )

    def replay_policy(self, session: Session, auth: AuthContext, policy_id: str,
                      limit: int = 100) -> PolicySimulationResponse:
        auth.require("policies:read")
        row = session.scalar(select(PolicyBundle).where(PolicyBundle.tenant_id == auth.tenant_id, PolicyBundle.id == policy_id))
        if row is None: raise NotFoundError("policy bundle not found")
        decisions = list(session.scalars(select(Decision).where(Decision.tenant_id == auth.tenant_id)
                                         .order_by(Decision.created_at.desc()).limit(min(limit, 1000))))
        engine = PolicyEngine(self.service.policy_engine.baseline); results=[]; counts={}; passed=0
        for decision in decisions:
            findings = [Finding.model_validate(item) for item in decision.findings]
            evaluated = engine.evaluate(decision.request_json, findings, decision.risk_score, row.document)
            expected = evaluated.outcome == decision.outcome; passed += expected
            counts[evaluated.outcome] = counts.get(evaluated.outcome, 0) + 1
            results.append(PolicySimulationCaseResult(name=decision.id, outcome=evaluated.outcome,
                risk_score=decision.risk_score, matched_rule=evaluated.matched_rule,
                reasons=evaluated.reasons, constraints=evaluated.constraints, expected=expected))
        return PolicySimulationResponse(document_hash=row.document_hash, total=len(results), passed=passed,
            failed=len(results)-passed, outcome_counts=counts, results=results)

    def set_policy_rollout(self, session: Session, auth: AuthContext, policy_id: str,
                           mode: str, percentage: int, reason: str):
        auth.require("policies:activate")
        if mode not in {"canary", "shadow"}: raise ConflictError("unsupported rollout mode")
        stmt = select(PolicyBundle).where(
            PolicyBundle.tenant_id == auth.tenant_id, PolicyBundle.id == policy_id
        )
        if session.bind and session.bind.dialect.name == "postgresql": stmt = stmt.with_for_update()
        row = session.scalar(stmt)
        if row is None: raise NotFoundError("policy bundle not found")
        if row.created_by_key_id == auth.key_id:
            raise AuthorizationError("a policy publisher cannot start rollout of the same policy")
        if mode == "canary":
            other = session.scalar(select(PolicyBundle.id).where(
                PolicyBundle.tenant_id == auth.tenant_id,
                PolicyBundle.rollout_mode == "canary",
                PolicyBundle.id != row.id,
            ))
            if other is not None:
                raise ConflictError("another canary rollout is already active")
        validation = self.validate_policy(auth, row.document)
        if not validation.valid: raise PolicyError("invalid policy cannot enter rollout")
        if not row.rollout_salt:
            import secrets
            row.rollout_salt = secrets.token_hex(16)
        row.rollout_mode = mode; row.canary_percentage = percentage if mode == "canary" else 0
        row.validation_report = validation.model_dump(mode="json")
        append_event(session, self.service.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                     trace_id=new_id("trc"), parent_event_id=None, event_type=f"policy.{mode}_started",
                     payload={"policy_id": row.id, "percentage": row.canary_percentage, "reason": reason, "by": auth.key_id})
        session.commit(); POLICY_ROLLOUT_EVENTS.labels(mode).inc(); return self.service._policy_response(row)

    def rollback_policy(self, session: Session, auth: AuthContext, policy_id: str, reason: str):
        auth.require("policies:activate")
        target = session.scalar(select(PolicyBundle).where(PolicyBundle.tenant_id == auth.tenant_id, PolicyBundle.id == policy_id))
        if target is None: raise NotFoundError("rollback target policy not found")
        current = session.scalar(select(PolicyBundle).where(PolicyBundle.tenant_id == auth.tenant_id, PolicyBundle.active.is_(True)))
        if current and current.id != target.id:
            current.active=False; current.rollout_mode="rolled_back"; current.canary_percentage=0
        target.active=True; target.rollout_mode="active"; target.canary_percentage=100
        target.activated_at=datetime.now(UTC); target.activated_by_key_id=auth.key_id; target.activation_reason=reason
        append_event(session, self.service.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                     trace_id=new_id("trc"), parent_event_id=None, event_type="policy.rolled_back",
                     payload={"policy_id": target.id, "replaced_policy_id": current.id if current else None, "reason": reason})
        session.commit(); POLICY_ROLLOUT_EVENTS.labels("rollback").inc(); return self.service._policy_response(target)

    def anchor_audit(self, session: Session, auth: AuthContext, destination: str) -> AuditAnchorResponse:
        return self.anchor_audit_batch(
            session, auth, destinations=[destination], required_quorum=1
        ).anchors[0]

    def anchor_audit_batch(
        self, session: Session, auth: AuthContext, *, destinations: list[str],
        required_quorum: int,
    ) -> AuditAnchorQuorumResponse:
        auth.require("audit:anchor")
        normalized = list(dict.fromkeys(destination.strip() for destination in destinations if destination.strip()))
        if not normalized or len(normalized) > 16:
            raise ConflictError("one to sixteen unique audit destinations are required")
        if required_quorum < 1 or required_quorum > len(normalized):
            raise ConflictError("audit anchor quorum exceeds the destination count")
        configured = set(self.settings.audit_anchor_destinations)
        if configured and not set(normalized).issubset(configured):
            raise AuthorizationError(
                "audit anchor destination is not configured",
                details={"unknown": sorted(set(normalized) - configured)},
            )
        verification = verify_tenant_chain(session, self.service.signing_key, auth.tenant_id)
        if not verification.get("valid"):
            raise ConflictError("audit chain must verify before anchoring", details=verification)
        if session.bind and session.bind.dialect.name == "postgresql":
            session.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:scope, 0))"),
                {"scope": f"anchor-batch:{auth.tenant_id}"},
            )
        latest = session.scalar(
            select(Event).where(Event.tenant_id == auth.tenant_id)
            .order_by(Event.sequence.desc()).limit(1)
        )
        sequence = latest.sequence if latest else 0
        chain_head = latest.event_hash if latest else "0" * 64
        now = datetime.now(UTC)
        rows: list[AuditAnchor] = []
        claims: list[AuditAnchorClaim] = []
        for destination in normalized:
            existing = session.scalar(select(AuditAnchor).where(
                AuditAnchor.tenant_id == auth.tenant_id,
                AuditAnchor.sequence == sequence,
                AuditAnchor.destination == destination,
            ))
            if existing is not None:
                rows.append(existing)
                continue
            in_flight = session.scalar(select(AuditAnchor).where(
                AuditAnchor.tenant_id == auth.tenant_id,
                AuditAnchor.destination == destination,
                AuditAnchor.status.in_(["pending", "delivering"]),
            ).limit(1))
            if in_flight is not None:
                raise ConflictError(
                    "an audit anchor for this destination is already in flight",
                    details={"anchor_id": in_flight.id, "destination": destination},
                )
            previous = session.scalar(select(AuditAnchor).where(
                AuditAnchor.tenant_id == auth.tenant_id,
                AuditAnchor.destination == destination,
                AuditAnchor.status == "verified",
            ).order_by(AuditAnchor.sequence.desc(), AuditAnchor.anchored_at.desc()).limit(1))
            previous_receipt_id = None
            if previous is not None:
                backend_receipt = previous.receipt.get("backend", {})
                if isinstance(backend_receipt, dict) and isinstance(backend_receipt.get("receipt_id"), str):
                    previous_receipt_id = str(backend_receipt["receipt_id"])
            envelope = build_anchor_envelope(
                self.service.signing_key, tenant_id=auth.tenant_id, sequence=sequence,
                chain_head=chain_head, destination=destination,
                previous_receipt_id=previous_receipt_id,
            )
            row = AuditAnchor(
                id=new_id("anc"), tenant_id=auth.tenant_id, sequence=sequence,
                chain_head=chain_head, destination=destination, envelope=envelope,
                receipt={}, receipt_hash=hash_object({}), status="pending",
                max_attempts=self.settings.anchor_max_attempts, available_at=now,
                previous_anchor_id=previous.id if previous else None,
            )
            claim = AuditAnchorClaim(
                anchor_id=row.id, tenant_id=auth.tenant_id, destination=destination,
                status="pending", max_attempts=self.settings.anchor_max_attempts,
                available_at=now,
            )
            session.add_all([row, claim]); rows.append(row); claims.append(claim)
        if claims:
            append_event(
                session, self.service.signing_key, event_id=new_id("evt"),
                tenant_id=auth.tenant_id, trace_id=new_id("trc"), parent_event_id=None,
                event_type="audit.anchor_batch_queued",
                payload={
                    "anchor_ids": [row.id for row in rows], "sequence": sequence,
                    "chain_head": chain_head, "destinations": normalized,
                    "required_quorum": required_quorum,
                },
            )
            session.commit()
        if self.settings.environment in {"development", "test"}:
            for row in rows:
                if row.status == "verified":
                    continue
                backend = build_anchor_backend(self.settings, row.destination)
                receipt = backend.publish(row.envelope)
                if not backend.verify(row.envelope, receipt):
                    raise RuntimeError("anchor read-back verification failed")
                combined = {"envelope": row.envelope, "backend": receipt}
                row.receipt = combined; row.receipt_hash = hash_object(combined)
                row.status = "verified"; row.verified_at = datetime.now(UTC)
                claim = session.get(AuditAnchorClaim, row.id)
                if claim is not None:
                    claim.status = "processed"; claim.processed_at = row.verified_at
                AUDIT_ANCHOR_EVENTS.labels(row.status, row.destination).inc()
            session.commit()
        responses = [self._anchor_response(row) for row in rows]
        verified_count = sum(row.status == "verified" for row in rows)
        return AuditAnchorQuorumResponse(
            sequence=sequence, chain_head=chain_head, required_quorum=required_quorum,
            verified_count=verified_count, satisfied=verified_count >= required_quorum,
            anchors=responses,
        )

    def audit_anchor_quorum(
        self, session: Session, auth: AuthContext, *, sequence: int | None = None,
        required_quorum: int | None = None,
    ) -> AuditAnchorQuorumResponse:
        auth.require("audit:verify")
        if sequence is None:
            sequence = session.scalar(select(func.max(AuditAnchor.sequence)).where(
                AuditAnchor.tenant_id == auth.tenant_id
            ))
        if sequence is None:
            raise NotFoundError("no audit anchors exist")
        rows = list(session.scalars(select(AuditAnchor).where(
            AuditAnchor.tenant_id == auth.tenant_id, AuditAnchor.sequence == sequence,
        ).order_by(AuditAnchor.destination)))
        if not rows:
            raise NotFoundError("audit anchor quorum does not exist")
        quorum = required_quorum or self.settings.audit_anchor_required_quorum
        verified_count = sum(row.status == "verified" for row in rows)
        return AuditAnchorQuorumResponse(
            sequence=sequence, chain_head=rows[0].chain_head, required_quorum=quorum,
            verified_count=verified_count, satisfied=verified_count >= quorum,
            anchors=[self._anchor_response(row) for row in rows],
        )

    def verify_anchor(self, session: Session, auth: AuthContext, anchor_id: str) -> AuditAnchorResponse:
        auth.require("audit:verify")
        row = session.scalar(select(AuditAnchor).where(
            AuditAnchor.tenant_id == auth.tenant_id, AuditAnchor.id == anchor_id))
        if row is None:
            raise NotFoundError("audit anchor not found")
        if row.status in {"pending", "delivering"}:
            raise ConflictError("audit anchor has not completed delivery",
                                details={"anchor_id": row.id, "status": row.status})
        envelope = row.envelope or row.receipt.get("envelope", {})
        receipt = row.receipt.get("backend", {})
        valid = isinstance(envelope, dict) and isinstance(receipt, dict) and             build_anchor_backend(self.settings, row.destination).verify(envelope, receipt)
        row.status = "verified" if valid else "invalid"
        row.verified_at = datetime.now(UTC); session.commit()
        if not valid:
            raise ConflictError("audit anchor verification failed")
        return self._anchor_response(row)

    def write_memory(self, session: Session, auth: AuthContext, body: MemoryWriteRequest) -> MemoryRecordResponse:
        auth.require("memory:write")
        agent = session.scalar(select(Agent).where(Agent.tenant_id == auth.tenant_id, Agent.id == body.agent_id, Agent.status == "active"))
        if agent is None: raise NotFoundError("memory writer agent is not active")
        version = (session.scalar(select(func.max(MemoryRecord.version)).where(
            MemoryRecord.tenant_id == auth.tenant_id, MemoryRecord.external_id == body.external_id)) or 0) + 1
        signals = self._memory_poisoning_signals(body.content, body.provenance)
        trust = min(body.trust_score, 30) if signals else body.trust_score
        status = "quarantined" if signals else "active"; record_id = new_id("mem")
        encrypted = self.service.tenant_crypto.encrypt(session, auth.tenant_id, body.content.encode(), context=f"memory:{auth.tenant_id}:{record_id}".encode())
        provenance = {**body.provenance, "writer_key_id": auth.key_id, "signals": signals,
                      "provenance_hash": hash_object(body.provenance)}
        row = MemoryRecord(id=record_id, tenant_id=auth.tenant_id, external_id=body.external_id,
            version=version, agent_id=body.agent_id, trace_id=body.trace_id, source_uri=body.source_uri,
            source_type=body.source_type, content_hash=hash_object({"content": body.content}),
            encrypted_content=encrypted, provenance=provenance, data_classes=body.data_classes,
            trust_score=trust, status=status, expires_at=body.expires_at)
        session.add(row)
        append_event(session, self.service.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                     trace_id=body.trace_id, parent_event_id=None, event_type="memory.written",
                     payload={"memory_id": row.id, "content_hash": row.content_hash, "status": status, "signals": signals})
        session.commit(); MEMORY_EVENTS.labels("write", row.status).inc(); return self._memory_response(row, None)

    def read_memory(self, session: Session, auth: AuthContext, memory_id: str,
                    include_content: bool = True) -> MemoryRecordResponse:
        auth.require("memory:read")
        row = session.scalar(select(MemoryRecord).where(MemoryRecord.tenant_id == auth.tenant_id, MemoryRecord.id == memory_id))
        if row is None: raise NotFoundError("memory record not found")
        now = datetime.now(UTC)
        if row.expires_at and (row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)) <= now:
            row.status = "expired"
        if row.status != "active" and "memory:quarantine" not in auth.scopes and "*" not in auth.scopes:
            raise AuthorizationError("memory record is not active")
        content = None
        if include_content:
            content = self.service.tenant_crypto.decrypt(
                session, auth.tenant_id, row.encrypted_content,
                context=f"memory:{auth.tenant_id}:{row.id}".encode()).decode()
        return self._memory_response(row, content)

    def update_memory_status(self, session: Session, auth: AuthContext, memory_id: str,
                             body: MemoryStatusUpdate) -> MemoryRecordResponse:
        auth.require("memory:quarantine")
        row = session.scalar(select(MemoryRecord).where(MemoryRecord.tenant_id == auth.tenant_id, MemoryRecord.id == memory_id))
        if row is None: raise NotFoundError("memory record not found")
        row.status = body.status
        append_event(session, self.service.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                     trace_id=row.trace_id, parent_event_id=None, event_type="memory.status_changed",
                     payload={"memory_id": row.id, "status": body.status, "reason": body.reason, "by": auth.key_id})
        session.commit(); MEMORY_EVENTS.labels("status_update", row.status).inc(); return self._memory_response(row, None)

    def create_delegation(self, session: Session, auth: AuthContext,
                          body: DelegationGrantCreate) -> DelegationGrantResponse:
        auth.require("delegations:write")
        now = datetime.now(UTC); expiry = body.expires_at if body.expires_at.tzinfo else body.expires_at.replace(tzinfo=UTC)
        if expiry <= now: raise ConflictError("delegation expiration must be in the future")
        for agent_id in (body.parent_agent_id, body.child_agent_id):
            if session.scalar(select(Agent.id).where(Agent.tenant_id == auth.tenant_id, Agent.id == agent_id, Agent.status == "active")) is None:
                raise NotFoundError(f"delegation agent {agent_id} is not active")
        parent = None
        if body.parent_grant_id:
            parent = session.scalar(select(DelegationGrant).where(DelegationGrant.tenant_id == auth.tenant_id,
                DelegationGrant.id == body.parent_grant_id, DelegationGrant.status == "active"))
            if parent is None: raise NotFoundError("parent delegation grant is not active")
            self._assert_attenuated(parent, body)
            parent_expiry = parent.expires_at if parent.expires_at.tzinfo else parent.expires_at.replace(tzinfo=UTC)
            if expiry > parent_expiry: raise AuthorizationError("child delegation cannot outlive its parent")
            siblings = session.scalar(select(func.count()).select_from(DelegationGrant).where(
                DelegationGrant.tenant_id == auth.tenant_id, DelegationGrant.parent_grant_id == parent.id,
                DelegationGrant.status == "active")) or 0
            if siblings >= parent.max_fanout: raise AuthorizationError("parent delegation fan-out limit is exhausted")
        document = body.model_dump(mode="json")
        document["expires_at"] = expiry.isoformat()
        grant_hash = hash_object(document)
        persistence = dict(document)
        persistence.pop("expires_at", None)
        row = DelegationGrant(id=new_id("dlg"), tenant_id=auth.tenant_id, **persistence, expires_at=expiry,
            grant_hash=grant_hash, signature=self.service.signing_key.sign(bytes.fromhex(grant_hash)),
            status="active", created_by_key_id=auth.key_id)
        session.add(row)
        append_event(session, self.service.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                     trace_id=body.trace_id, parent_event_id=None, event_type="delegation.created",
                     payload={"grant_id": row.id, "parent_agent_id": body.parent_agent_id,
                              "child_agent_id": body.child_agent_id, "grant_hash": grant_hash})
        session.commit(); DELEGATION_EVENTS.labels("created").inc(); return self._delegation_response(row)

    def revoke_delegation(self, session: Session, auth: AuthContext, grant_id: str,
                          reason: str) -> DelegationGrantResponse:
        auth.require("delegations:revoke")
        row = session.scalar(select(DelegationGrant).where(DelegationGrant.tenant_id == auth.tenant_id, DelegationGrant.id == grant_id))
        if row is None: raise NotFoundError("delegation grant not found")
        now=datetime.now(UTC); queue=[row]; revoked=[]
        while queue:
            current=queue.pop(); current.status="revoked"; current.revoked_at=now; revoked.append(current.id)
            authorizations=list(session.scalars(select(A2ATaskAuthorization).where(
                A2ATaskAuthorization.tenant_id==auth.tenant_id,
                A2ATaskAuthorization.delegation_grant_id==current.id,
                A2ATaskAuthorization.status=="authorized")))
            for authorization in authorizations:
                authorization.status="revoked"; authorization.revoked_at=now
            queue.extend(session.scalars(select(DelegationGrant).where(DelegationGrant.tenant_id == auth.tenant_id,
                DelegationGrant.parent_grant_id == current.id, DelegationGrant.status == "active")))
        append_event(session, self.service.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                     trace_id=row.trace_id, parent_event_id=None, event_type="delegation.revoked",
                     payload={"grant_id": row.id, "grants_revoked": revoked, "reason": reason})
        session.commit(); DELEGATION_EVENTS.labels("revoked").inc(); return self._delegation_response(row)

    def create_budget(self, session: Session, auth: AuthContext, body: RuntimeBudgetCreate) -> RuntimeBudgetResponse:
        auth.require("budgets:write"); limits=self._normalized_amounts(body.limits)
        row=RuntimeBudget(id=new_id("bdg"), tenant_id=auth.tenant_id, scope_type=body.scope_type,
                          scope_id=body.scope_id, limits=limits, consumed={}, reserved={}, status="active")
        session.add(row)
        try: session.commit()
        except IntegrityError as exc:
            session.rollback(); raise ConflictError("a budget already exists for this scope") from exc
        BUDGET_EVENTS.labels("created").inc(); return self._budget_response(row)

    def reserve_budget(self, session: Session, auth: AuthContext, budget_id: str,
                       body: BudgetReservationRequest) -> BudgetReservationResponse:
        auth.require("budgets:reserve"); amounts=self._normalized_amounts(body.amounts)
        existing=session.scalar(select(BudgetReservation).where(BudgetReservation.tenant_id==auth.tenant_id,
                                                                  BudgetReservation.idempotency_key==body.idempotency_key))
        if existing:
            if existing.budget_id != budget_id or existing.amounts != amounts:
                raise ConflictError("budget idempotency key was used for another reservation")
            return self._reservation_response(existing)
        stmt=select(RuntimeBudget).where(RuntimeBudget.tenant_id==auth.tenant_id, RuntimeBudget.id==budget_id)
        if session.bind and session.bind.dialect.name=="postgresql": stmt=stmt.with_for_update()
        budget=session.scalar(stmt)
        if budget is None or budget.status!="active": raise NotFoundError("runtime budget is not active")
        consumed=self._decimal_map(budget.consumed); reserved=self._decimal_map(budget.reserved); limits=self._decimal_map(budget.limits)
        requested=self._decimal_map(amounts)
        exceeded={k:{"limit":str(limits.get(k)),"requested_total":str(consumed.get(k,Decimal("0"))+reserved.get(k,Decimal("0"))+v)}
                  for k,v in requested.items() if k not in limits or consumed.get(k,Decimal("0"))+reserved.get(k,Decimal("0"))+v>limits[k]}
        if exceeded: raise AuthorizationError("runtime budget would be exceeded", details={"exceeded":exceeded})
        for k,v in requested.items(): reserved[k]=reserved.get(k,Decimal("0"))+v
        budget.reserved=self._serialize_decimal_map(reserved); budget.version+=1; budget.updated_at=datetime.now(UTC)
        row=BudgetReservation(id=new_id("rsv"), tenant_id=auth.tenant_id, budget_id=budget.id,
            trace_id=body.trace_id, idempotency_key=body.idempotency_key, amounts=amounts,
            status="reserved", expires_at=datetime.now(UTC)+timedelta(seconds=body.lifetime_seconds))
        session.add(row); append_event(session,self.service.signing_key,event_id=new_id("evt"),tenant_id=auth.tenant_id,
            trace_id=body.trace_id,parent_event_id=None,event_type="budget.reserved",
            payload={"budget_id":budget.id,"reservation_id":row.id,"amounts":amounts})
        session.commit(); BUDGET_EVENTS.labels("reserved").inc(); return self._reservation_response(row)

    def settle_budget(self, session: Session, auth: AuthContext, reservation_id: str,
                      body: BudgetSettlementRequest) -> BudgetReservationResponse:
        auth.require("budgets:reserve")
        stmt=select(BudgetReservation).where(
            BudgetReservation.tenant_id==auth.tenant_id, BudgetReservation.id==reservation_id
        )
        if session.bind and session.bind.dialect.name=="postgresql": stmt=stmt.with_for_update()
        reservation=session.scalar(stmt)
        if reservation is None: raise NotFoundError("budget reservation not found")
        if reservation.status!="reserved": return self._reservation_response(reservation)
        now=datetime.now(UTC)
        expiry=reservation.expires_at if reservation.expires_at.tzinfo else reservation.expires_at.replace(tzinfo=UTC)
        if expiry<=now:
            raise ConflictError("expired budget reservations cannot be settled")
        budget_stmt=select(RuntimeBudget).where(
            RuntimeBudget.tenant_id==auth.tenant_id, RuntimeBudget.id==reservation.budget_id
        )
        if session.bind and session.bind.dialect.name=="postgresql": budget_stmt=budget_stmt.with_for_update()
        budget=session.scalar(budget_stmt)
        if budget is None or budget.status!="active": raise NotFoundError("runtime budget is not active")
        reserved=self._decimal_map(budget.reserved); consumed=self._decimal_map(budget.consumed); limits=self._decimal_map(budget.limits)
        reservation_amounts=self._decimal_map(reservation.amounts)
        for k,v in reservation_amounts.items(): reserved[k]=max(Decimal("0"),reserved.get(k,Decimal("0"))-v)
        if body.action=="commit":
            actual=self._decimal_map(self._normalized_amounts(body.actual_amounts or reservation.amounts))
            over_reservation={k:{"reserved":str(reservation_amounts.get(k,Decimal("0"))),"actual":str(v)}
                              for k,v in actual.items() if v>reservation_amounts.get(k,Decimal("0"))}
            if over_reservation:
                raise AuthorizationError("actual usage exceeds the reserved authority",details={"exceeded":over_reservation})
            exceeded={k:{"limit":str(limits.get(k)),"actual_total":str(consumed.get(k,Decimal("0"))+v)}
                      for k,v in actual.items() if k not in limits or consumed.get(k,Decimal("0"))+v>limits[k]}
            if exceeded:
                raise AuthorizationError("runtime budget would be exceeded during settlement",details={"exceeded":exceeded})
            for k,v in actual.items(): consumed[k]=consumed.get(k,Decimal("0"))+v
            reservation.status="committed"
        else:
            reservation.status="released"
        budget.reserved=self._serialize_decimal_map(reserved); budget.consumed=self._serialize_decimal_map(consumed)
        budget.version+=1; budget.updated_at=now
        reservation.settled_at=now
        append_event(session,self.service.signing_key,event_id=new_id("evt"),tenant_id=auth.tenant_id,
            trace_id=reservation.trace_id,parent_event_id=None,event_type="budget.settled",
            payload={"budget_id":budget.id,"reservation_id":reservation.id,"action":body.action,"reason":body.reason})
        session.commit(); BUDGET_EVENTS.labels(body.action).inc(); return self._reservation_response(reservation)

    def tenant_lifecycle(self, session: Session, auth: AuthContext,
                         body: TenantLifecycleRequest) -> TenantLifecycleJobResponse:
        auth.require("tenants:lifecycle")
        tenant = session.get(Tenant, auth.tenant_id)
        if tenant is None:
            raise NotFoundError("tenant not found")
        idempotency_key = body.idempotency_key or hash_object({
            "action": body.action, "parameters": body.parameters, "reason": body.reason,
        })[:64]
        existing = session.scalar(select(TenantLifecycleJob).where(
            TenantLifecycleJob.tenant_id == auth.tenant_id,
            TenantLifecycleJob.idempotency_key == idempotency_key,
        ))
        if existing is not None:
            if existing.job_type != body.action:
                raise ConflictError("tenant lifecycle idempotency key was reused")
            return self._job_response(existing)
        now = datetime.now(UTC)
        parameters = {**body.parameters, "reason": body.reason}
        immediate = body.action in {"suspend", "resume"}
        status = "completed" if immediate else "pending"
        job = TenantLifecycleJob(
            id=new_id("job"), tenant_id=auth.tenant_id, job_type=body.action,
            idempotency_key=idempotency_key, status=status, parameters=parameters,
            result={}, requested_by_key_id=auth.key_id, priority=body.priority,
            max_attempts=self.settings.lifecycle_max_attempts, available_at=now,
            completed_at=now if immediate else None,
        )
        session.add(job)
        if body.action == "suspend":
            tenant.status = "suspended"; tenant.suspended_at = now
            job.result = {"tenant_status": tenant.status}
        elif body.action == "resume":
            tenant.status = "active"; tenant.suspended_at = None
            job.result = {"tenant_status": tenant.status}
        else:
            if body.action == "delete":
                tenant.status = "deletion_pending"; tenant.deletion_requested_at = now
            elif body.action == "crypto_erase":
                tenant.status = "crypto_erase_pending"; tenant.deletion_requested_at = now
                if not self.settings.tenant_key_destroy_enabled:
                    # Development compatibility only. Production rejects this configuration.
                    job.status = "pending_external"
                    job.result = {
                        "required_action": "enable the lifecycle worker with a tenant-dedicated KMS key route",
                        "tenant_key_backend": self.settings.tenant_key_backend,
                    }
            if job.status == "pending":
                session.add(LifecycleClaim(
                    job_id=job.id, tenant_id=auth.tenant_id, job_type=body.action,
                    status="pending", priority=body.priority,
                    max_attempts=self.settings.lifecycle_max_attempts, available_at=now,
                ))
        append_event(session, self.service.signing_key, event_id=new_id("evt"),
                     tenant_id=auth.tenant_id, trace_id=new_id("trc"), parent_event_id=None,
                     event_type="tenant.lifecycle_requested",
                     payload={"job_id": job.id, "action": body.action,
                              "status": job.status, "reason": body.reason})
        session.commit()
        if body.action == "export" and self.settings.environment in {"development", "test"}:
            import asyncio

            from .lifecycle import TenantLifecycleWorker
            worker = TenantLifecycleWorker(
                session_factory=sessionmaker(bind=session.get_bind(), class_=Session,
                                               expire_on_commit=False, future=True),
                service=self.service, worker_id="inline-lifecycle",
            )
            asyncio.run(worker.run_once(limit=1))
            session.expire_all()
            job = session.scalar(select(TenantLifecycleJob).where(
                TenantLifecycleJob.tenant_id == auth.tenant_id,
                TenantLifecycleJob.id == job.id,
            )) or job
        TENANT_LIFECYCLE_EVENTS.labels(body.action, job.status).inc()
        return self._job_response(job)

    def get_lifecycle_job(self, session: Session, auth: AuthContext,
                          job_id: str) -> TenantLifecycleJobResponse:
        auth.require("tenants:lifecycle")
        job = session.scalar(select(TenantLifecycleJob).where(
            TenantLifecycleJob.tenant_id == auth.tenant_id,
            TenantLifecycleJob.id == job_id,
        ))
        if job is None:
            raise NotFoundError("tenant lifecycle job not found")
        return self._job_response(job)

    def reconcile_lifecycle_job(self, session: Session, auth: AuthContext, job_id: str,
                                *, resolution: str, reason: str,
                                destruction_receipt: dict[str, Any]) -> TenantLifecycleJobResponse:
        auth.require("tenants:lifecycle")
        statement = select(TenantLifecycleJob).where(
            TenantLifecycleJob.tenant_id == auth.tenant_id,
            TenantLifecycleJob.id == job_id,
        )
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update()
        job = session.scalar(statement)
        if job is None:
            raise NotFoundError("tenant lifecycle job not found")
        if job.status != "outcome_unknown" or job.job_type != "crypto_erase":
            raise ConflictError("lifecycle job does not require destructive reconciliation")
        now = datetime.now(UTC)
        if resolution == "confirmed_destroyed":
            route = session.get(TenantKeyRoute, auth.tenant_id)
            if route is not None:
                route.status = "destroyed"; route.wrapped_local_key = None
                route.destroyed_at = now; route.destruction_receipt = destruction_receipt
            tenant = session.get(Tenant, auth.tenant_id)
            if tenant is not None:
                tenant.status = "crypto_erased"; tenant.crypto_erased_at = now
            job.status = "completed"; job.completed_at = now
            job.result = {"destruction_receipt": destruction_receipt,
                          "reconciled_by": auth.key_id, "reason": reason}
            job.reconciliation_status = "resolved"
        else:
            job.status = "pending"; job.available_at = now
            job.external_effect_started_at = None; job.reconciliation_status = "not_required"
            claim = session.get(LifecycleClaim, job.id)
            if claim is None:
                claim = LifecycleClaim(job_id=job.id, tenant_id=auth.tenant_id,
                    job_type=job.job_type, status="pending", max_attempts=job.max_attempts,
                    available_at=now)
                session.add(claim)
            else:
                claim.status = "pending"; claim.available_at = now; claim.processed_at = None
        append_event(session, self.service.signing_key, event_id=new_id("evt"),
                     tenant_id=auth.tenant_id, trace_id=new_id("trc"), parent_event_id=None,
                     event_type="tenant.lifecycle_reconciled",
                     payload={"job_id": job.id, "resolution": resolution,
                              "reason": reason, "by": auth.key_id})
        session.commit()
        return self._job_response(job)

    def get_lifecycle_export(self, session: Session, auth: AuthContext,
                             job_id: str) -> tuple[EvidenceObject, bytes]:
        auth.require("tenants:lifecycle")
        job = session.scalar(select(TenantLifecycleJob).where(
            TenantLifecycleJob.tenant_id == auth.tenant_id,
            TenantLifecycleJob.id == job_id,
            TenantLifecycleJob.job_type == "export",
        ))
        if job is None or job.status != "completed":
            raise NotFoundError("completed tenant export not found")
        evidence_id = job.result.get("evidence_object_id")
        evidence = session.scalar(select(EvidenceObject).where(
            EvidenceObject.tenant_id == auth.tenant_id,
            EvidenceObject.id == evidence_id,
        ))
        if evidence is None:
            raise NotFoundError("tenant export evidence object not found")
        encrypted = self.service.artifact_store.get(evidence.storage_key)
        plaintext = self.service.tenant_crypto.decrypt(
            session, auth.tenant_id, encrypted,
            context=f"tenant-export:{auth.tenant_id}:{job.id}:{evidence.sha256}".encode(),
        )
        if hash_object({"sha256": __import__("hashlib").sha256(plaintext).hexdigest()}) != hash_object({"sha256": evidence.sha256}):
            raise ConflictError("tenant export evidence hash does not match metadata")
        return evidence, plaintext

    def create_legal_hold(self, session: Session, auth: AuthContext,
                          body: LegalHoldCreate) -> LegalHoldResponse:
        auth.require("tenants:lifecycle")
        if body.expires_at is not None:
            expiry = body.expires_at if body.expires_at.tzinfo else body.expires_at.replace(tzinfo=UTC)
            if expiry <= datetime.now(UTC):
                raise ConflictError("legal hold expiration must be in the future")
        row = LegalHold(
            id=new_id("hld"), tenant_id=auth.tenant_id, scope=body.scope,
            reason=body.reason, status="active", created_by_key_id=auth.key_id,
            expires_at=body.expires_at,
        )
        session.add(row)
        append_event(session, self.service.signing_key, event_id=new_id("evt"),
                     tenant_id=auth.tenant_id, trace_id=new_id("trc"), parent_event_id=None,
                     event_type="tenant.legal_hold_created",
                     payload={"hold_id": row.id, "scope": row.scope, "reason": row.reason})
        session.commit()
        return self._legal_hold_response(row)

    def list_legal_holds(self, session: Session, auth: AuthContext) -> list[LegalHoldResponse]:
        auth.require("tenants:lifecycle")
        rows = session.scalars(select(LegalHold).where(
            LegalHold.tenant_id == auth.tenant_id,
        ).order_by(LegalHold.created_at.desc()).limit(self.settings.max_page_size))
        return [self._legal_hold_response(row) for row in rows]

    def release_legal_hold(self, session: Session, auth: AuthContext, hold_id: str,
                           reason: str) -> LegalHoldResponse:
        auth.require("tenants:lifecycle")
        row = session.scalar(select(LegalHold).where(
            LegalHold.tenant_id == auth.tenant_id, LegalHold.id == hold_id))
        if row is None:
            raise NotFoundError("legal hold not found")
        if row.status != "active":
            raise ConflictError("legal hold is not active")
        row.status = "released"; row.released_at = datetime.now(UTC)
        row.release_reason = reason
        append_event(session, self.service.signing_key, event_id=new_id("evt"),
                     tenant_id=auth.tenant_id, trace_id=new_id("trc"), parent_event_id=None,
                     event_type="tenant.legal_hold_released",
                     payload={"hold_id": row.id, "reason": reason, "by": auth.key_id})
        session.commit()
        return self._legal_hold_response(row)

    def operator_posture(self, session: Session, auth: AuthContext) -> OperatorPostureResponse:
        auth.require("audit:verify")
        tenant = session.get(Tenant, auth.tenant_id)
        if tenant is None:
            raise NotFoundError("tenant not found")
        active_policy = session.scalar(
            select(PolicyBundle).where(
                PolicyBundle.tenant_id == auth.tenant_id,
                PolicyBundle.active.is_(True),
            )
        )

        def grouped(model: Any, field: Any) -> dict[str, int]:
            rows = session.execute(
                select(field, func.count()).where(model.tenant_id == auth.tenant_id).group_by(field)
            ).all()
            return {str(name): int(count) for name, count in rows}

        execution_states = grouped(Execution, Execution.state)
        outbox_states = grouped(OutboxMessage, OutboxMessage.status)
        memory_states = grouped(MemoryRecord, MemoryRecord.status)
        latest_audit = int(
            session.scalar(
                select(func.max(Event.sequence)).where(Event.tenant_id == auth.tenant_id)
            )
            or 0
        )
        latest_anchor = int(
            session.scalar(
                select(func.max(AuditAnchor.sequence)).where(AuditAnchor.tenant_id == auth.tenant_id)
            )
            or 0
        )
        return OperatorPostureResponse(
            tenant_id=auth.tenant_id,
            tenant_status=tenant.status,
            active_policy_id=active_policy.id if active_policy else None,
            active_policy_version=active_policy.version if active_policy else None,
            active_agents=int(session.scalar(select(func.count()).select_from(Agent).where(Agent.tenant_id == auth.tenant_id, Agent.status == "active")) or 0),
            open_incidents=int(session.scalar(select(func.count()).select_from(Incident).where(Incident.tenant_id == auth.tenant_id, Incident.status.in_(["open", "investigating", "contained"]))) or 0),
            pending_approvals=int(session.scalar(select(func.count()).select_from(Approval).where(Approval.tenant_id == auth.tenant_id, Approval.status == "pending")) or 0),
            active_capabilities=int(session.scalar(select(func.count()).select_from(Capability).where(Capability.tenant_id == auth.tenant_id, Capability.status == "active")) or 0),
            execution_states=execution_states,
            outbox_states=outbox_states,
            memory_states=memory_states,
            active_delegations=int(session.scalar(select(func.count()).select_from(DelegationGrant).where(DelegationGrant.tenant_id == auth.tenant_id, DelegationGrant.status == "active")) or 0),
            active_protocols=int(session.scalar(select(func.count()).select_from(AgentProtocolRegistration).where(AgentProtocolRegistration.tenant_id == auth.tenant_id, AgentProtocolRegistration.status == "active")) or 0),
            latest_audit_sequence=latest_audit,
            latest_anchor_sequence=latest_anchor,
            generated_at=datetime.now(UTC),
        )

    def register_protocol(self, session: Session, auth: AuthContext,
                          body: ProtocolRegistrationCreate) -> ProtocolRegistrationResponse:
        auth.require("protocols:write")
        if body.agent_id and session.scalar(select(Agent.id).where(
                Agent.tenant_id == auth.tenant_id, Agent.id == body.agent_id,
                Agent.status == "active")) is None:
            raise NotFoundError("protocol agent is not active")
        allowlist = self.settings.tool_allowed_hosts if body.protocol == "mcp" else self.settings.provider_allowed_hosts
        endpoint = validate_endpoint(
            body.endpoint, allowed_hosts=allowlist, network_zone="public",
            require_resolution=self.settings.environment == "production",
            resolution_timeout_seconds=self.settings.dns_resolution_timeout_seconds,
        )
        if bool(body.auth_header_name) != bool(body.auth_value):
            raise ConflictError("protocol authentication must include both header name and value")
        manifest = body.manifest
        protocol_version = body.protocol_version
        verification: dict[str, Any] = {"source": "submitted"}
        source = "submitted"
        if body.discover:
            manifest, protocol_version, verification = discover_protocol_manifest(
                protocol=body.protocol, endpoint=endpoint.canonical_url,
                auth_header_name=body.auth_header_name, auth_value=body.auth_value,
                proxy_url=self.settings.egress_proxy_url,
                max_response_bytes=self.settings.max_broker_response_bytes,
                validated_endpoint=endpoint,
            )
            source = "native-discovery"
        if not manifest:
            raise ConflictError("protocol registration requires a manifest or native discovery")
        manifest_hash = hash_object(manifest)
        statement = select(AgentProtocolRegistration).where(
            AgentProtocolRegistration.tenant_id == auth.tenant_id,
            AgentProtocolRegistration.protocol == body.protocol,
            AgentProtocolRegistration.external_id == body.external_id,
        )
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update()
        row = session.scalar(statement)
        now = datetime.now(UTC)
        if row is None:
            registration_id = new_id("prt")
            encrypted_auth = None
            if body.auth_value:
                encrypted_auth = self.service.tenant_crypto.encrypt(
                    session, auth.tenant_id, body.auth_value.encode(),
                    context=f"{auth.tenant_id}:{registration_id}:protocol".encode())
            row = AgentProtocolRegistration(
                id=registration_id, tenant_id=auth.tenant_id, protocol=body.protocol,
                protocol_version=protocol_version, external_id=body.external_id,
                agent_id=body.agent_id, endpoint=endpoint.canonical_url,
                auth_header_name=body.auth_header_name,
                encrypted_auth_value=encrypted_auth,
                manifest=manifest, manifest_hash=manifest_hash,
                current_manifest_version=1, status="active",
                created_by_key_id=auth.key_id, created_at=now, updated_at=now,
            )
            session.add(row); version = 1; event_type = "protocol.registered"
        else:
            if row.status != "active":
                raise ConflictError("protocol registration is inactive")
            if row.endpoint != endpoint.canonical_url or row.agent_id != body.agent_id:
                raise ConflictError("protocol identity and endpoint are immutable; register a new external id")
            if row.manifest_hash == manifest_hash:
                return self._protocol_response(row)
            version = row.current_manifest_version + 1
            row.protocol_version = protocol_version; row.manifest = manifest
            row.manifest_hash = manifest_hash; row.current_manifest_version = version
            row.updated_at = now; event_type = "protocol.manifest_changed"
        session.add(ProtocolManifestVersion(
            id=new_id("pmv"), tenant_id=auth.tenant_id, registration_id=row.id,
            version=version, protocol_version=protocol_version,
            manifest=manifest, manifest_hash=manifest_hash, source=source,
            verification=verification, created_by_key_id=auth.key_id,
        ))
        append_event(session, self.service.signing_key, event_id=new_id("evt"),
                     tenant_id=auth.tenant_id, trace_id=new_id("trc"), parent_event_id=None,
                     event_type=event_type,
                     payload={"registration_id": row.id, "protocol": body.protocol,
                              "manifest_hash": manifest_hash, "manifest_version": version,
                              "source": source})
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback(); raise ConflictError("protocol registration raced with another update") from exc
        PROTOCOL_EVENTS.labels(body.protocol, "registered").inc()
        return self._protocol_response(row)

    def list_protocol_manifest_versions(self, session: Session, auth: AuthContext,
                                        registration_id: str) -> list[ProtocolManifestVersionResponse]:
        auth.require("protocols:read")
        rows = session.scalars(select(ProtocolManifestVersion).where(
            ProtocolManifestVersion.tenant_id == auth.tenant_id,
            ProtocolManifestVersion.registration_id == registration_id,
        ).order_by(ProtocolManifestVersion.version.desc()).limit(self.settings.max_page_size))
        return [ProtocolManifestVersionResponse(
            id=row.id, registration_id=row.registration_id, version=row.version,
            protocol_version=row.protocol_version, manifest=row.manifest,
            manifest_hash=row.manifest_hash, source=row.source,
            verification=row.verification, created_at=row.created_at,
        ) for row in rows]

    def authorize_a2a_task(self, session: Session, auth: AuthContext, registration_id: str,
                           body: A2ATaskRequest) -> dict[str,Any]:
        auth.require("protocols:invoke")
        registration=session.scalar(select(AgentProtocolRegistration).where(
            AgentProtocolRegistration.tenant_id==auth.tenant_id,
            AgentProtocolRegistration.id==registration_id,
            AgentProtocolRegistration.protocol=="a2a",
            AgentProtocolRegistration.status=="active"))
        if registration is None:
            raise AuthorizationError("A2A registration is inactive")
        request_document=body.model_dump(mode="json")
        request_hash=hash_object(request_document)
        existing=session.scalar(select(A2ATaskAuthorization).where(
            A2ATaskAuthorization.tenant_id==auth.tenant_id,
            A2ATaskAuthorization.idempotency_key==body.idempotency_key))
        if existing is not None:
            if existing.registration_id!=registration_id or existing.request_hash!=request_hash:
                raise ConflictError("A2A idempotency key was used for a different task")
            return {"authorized":existing.status in {"authorized", "queued"},"task_id":existing.task_id,
                    "message_hash":hash_object({"message":body.message,"artifacts":body.artifacts}),
                    "endpoint":registration.endpoint,"receipt":existing.authorization_receipt,
                    "execution_id": existing.execution_id}
        grant_stmt=select(DelegationGrant).where(
            DelegationGrant.tenant_id==auth.tenant_id,
            DelegationGrant.id==body.delegation_grant_id,
            DelegationGrant.status=="active")
        if session.bind and session.bind.dialect.name=="postgresql":
            grant_stmt=grant_stmt.with_for_update()
        grant=session.scalar(grant_stmt)
        if grant is None:
            raise AuthorizationError("A2A delegation is inactive")
        now=datetime.now(UTC); expiry=grant.expires_at if grant.expires_at.tzinfo else grant.expires_at.replace(tzinfo=UTC)
        if expiry<=now: raise AuthorizationError("A2A delegation grant has expired")
        if registration.agent_id and registration.agent_id!=grant.child_agent_id:
            raise AuthorizationError("A2A target is not the delegated child agent")
        if body.trace_id!=grant.trace_id:
            raise AuthorizationError("A2A task trace is not bound to the delegation")
        if body.objective is not None and body.objective!=grant.objective:
            raise AuthorizationError("A2A task objective is outside the delegation")
        requested_tool=body.tool or body.operation
        if requested_tool and requested_tool not in set(grant.allowed_tools):
            raise AuthorizationError("A2A task tool is outside the delegation")
        if body.resource and not any(fnmatch.fnmatchcase(body.resource,pattern) for pattern in grant.resource_patterns):
            raise AuthorizationError("A2A task resource is outside the delegation")
        if not set(body.data_classes).issubset(set(grant.allowed_data_classes)):
            raise AuthorizationError("A2A task data classes are outside the delegation")
        if grant.consumed_fanout+1>grant.max_fanout:
            raise AuthorizationError("A2A delegation fan-out budget is exhausted")
        if body.delegation_depth>grant.max_depth:
            raise AuthorizationError("A2A task depth exceeds the delegation")
        requested_budget=self._decimal_map(self._normalized_amounts(
            {**body.budget_amounts,"messages":Decimal(str(body.budget_amounts.get("messages",0)))+Decimal("1"),
             "steps":Decimal(str(body.budget_amounts.get("steps",0)))+Decimal(str(body.step_count))}
        ))
        limits=self._decimal_map(grant.budget_limits)
        consumed=self._decimal_map(grant.consumed_budget)
        exceeded={key:{"limit":str(limits.get(key)),"requested_total":str(consumed.get(key,Decimal("0"))+value)}
                  for key,value in requested_budget.items()
                  if key in limits and consumed.get(key,Decimal("0"))+value>limits[key]}
        # Dimensions omitted from a grant are unconstrained; explicitly configured limits are mandatory.
        if exceeded:
            raise AuthorizationError("A2A task exceeds delegated runtime budget",details={"exceeded":exceeded})
        grant.consumed_fanout+=1
        grant.consumed_steps+=body.step_count
        for key,value in requested_budget.items():
            consumed[key]=consumed.get(key,Decimal("0"))+value
        grant.consumed_budget=self._serialize_decimal_map(consumed)
        message_hash=hash_object({"task_id":body.task_id,"message":body.message,"artifacts":body.artifacts})
        receipt=self.service.signing_key.issue_receipt({"aud":"aifence-a2a-task","sub":body.task_id,
            "tenant_id":auth.tenant_id,"trace_id":body.trace_id,"delegation_grant_id":grant.id,
            "parent_agent_id":grant.parent_agent_id,"child_agent_id":grant.child_agent_id,
            "registration_id":registration.id,"message_hash":message_hash,"request_hash":request_hash},
            lifetime_seconds=min(300,max(5,int((expiry-now).total_seconds()))))
        authorization=A2ATaskAuthorization(id=new_id("a2a"),tenant_id=auth.tenant_id,
            registration_id=registration.id,delegation_grant_id=grant.id,trace_id=body.trace_id,
            task_id=body.task_id,idempotency_key=body.idempotency_key,request_hash=request_hash,
            authorization_receipt=receipt,status="authorized")
        session.add(authorization)
        execution_id = None
        if body.dispatch:
            execution_request = {
                "method": "POST", "path": "/", "query": {},
                "body": {"taskId": body.task_id, "message": body.message,
                         "artifacts": body.artifacts, "objective": body.objective,
                         "delegationReceipt": receipt},
            }
            execution, _ = self.service.prepare_protocol_execution(
                session, auth, registration=registration, token=None,
                agent_id=grant.parent_agent_id, trace_id=body.trace_id,
                operation=body.operation or body.tool or "tasks/send",
                resource=body.resource or f"a2a:{registration.external_id}:{body.task_id}",
                execution_request=execution_request,
                idempotency_key=f"a2a:{body.idempotency_key}", authority_receipt=receipt,
            )
            authorization.execution_id = execution.id; authorization.status = "queued"
            execution_id = execution.id
        append_event(session,self.service.signing_key,event_id=new_id("evt"),tenant_id=auth.tenant_id,
            trace_id=body.trace_id,parent_event_id=None,event_type="a2a.task_authorized",
            payload={"authorization_id":authorization.id,"registration_id":registration.id,"grant_id":grant.id,
                     "task_id":body.task_id,"message_hash":message_hash,"request_hash":request_hash,
                     "execution_id": execution_id})
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback(); raise ConflictError("A2A task authorization raced with another request") from exc
        PROTOCOL_EVENTS.labels("a2a", "authorized").inc(); return {"authorized":True,"task_id":body.task_id,
            "message_hash":message_hash,"endpoint":registration.endpoint,"receipt":receipt,
            "execution_id": execution_id}

    def _anchor_backend(self, destination: str):
        try:
            return build_anchor_backend(self.settings, destination)
        except ValueError as exc:
            raise ConflictError("unsupported audit anchor destination") from exc
    @staticmethod
    def _memory_poisoning_signals(content:str,provenance:dict[str,Any])->list[str]:
        lowered=content.lower(); signals=[]
        for token,name in (("ignore previous instructions","instruction_override"),("do not trust","trust_manipulation"),("system prompt","system_prompt_reference"),("disable security","security_evasion")):
            if token in lowered: signals.append(name)
        if not provenance.get("source_hash") and not provenance.get("signature"): signals.append("unsigned_source")
        return signals
    @staticmethod
    def _assert_attenuated(parent:DelegationGrant,child:DelegationGrantCreate)->None:
        checks=[(set(child.allowed_tools).issubset(set(parent.allowed_tools)),"tools"),
            (set(child.allowed_data_classes).issubset(set(parent.allowed_data_classes)),"data_classes"),
            (all(any(fnmatch.fnmatchcase(item,pattern) for pattern in parent.resource_patterns) for item in child.resource_patterns),"resources"),
            (child.max_depth<parent.max_depth,"depth"),(child.max_fanout<=parent.max_fanout,"fanout")]
        failed=[name for valid,name in checks if not valid]
        for k,v in child.budget_limits.items():
            if k not in parent.budget_limits or float(v)>float(parent.budget_limits[k]): failed.append(f"budget:{k}")
        if failed: raise AuthorizationError("child delegation is not strictly attenuated",details={"failed":failed})
    @staticmethod
    def _normalized_amounts(values:dict[str,int|float|str])->dict[str,str]:
        if not values: raise ConflictError("at least one budget amount is required")
        unknown=set(values)-_NUMERIC_BUDGET_KEYS
        if unknown: raise ConflictError("budget contains unknown dimensions",details={"unknown":sorted(unknown)})
        result:dict[str,str]={}
        for key,value in values.items():
            try:
                amount=Decimal(str(value))
            except (InvalidOperation,ValueError) as exc:
                raise ConflictError("budget amounts must be decimal numbers") from exc
            if not amount.is_finite() or amount<0:
                raise ConflictError("budget amounts must be finite and non-negative")
            result[key]=format(amount.normalize(),"f")
        return result

    @staticmethod
    def _decimal_map(values:dict[str,object])->dict[str,Decimal]:
        try:
            return {str(key):Decimal(str(value)) for key,value in values.items()}
        except (InvalidOperation,ValueError) as exc:
            raise ConflictError("stored budget values are invalid") from exc

    @staticmethod
    def _serialize_decimal_map(values:dict[str,Decimal])->dict[str,str]:
        return {key:format(value.normalize(),"f") for key,value in values.items()}
    @staticmethod
    def _workload_response(r): return WorkloadIdentityBindingResponse(id=r.id,spiffe_id=r.spiffe_id,agent_id=r.agent_id,instance_pattern=r.instance_pattern,principal_type=r.principal_type,principal_id=r.principal_id,scopes=r.scopes,trust_domain=r.trust_domain,status=r.status,created_at=r.created_at,revoked_at=r.revoked_at)
    @staticmethod
    def _anchor_response(r): return AuditAnchorResponse(id=r.id,sequence=r.sequence,chain_head=r.chain_head,destination=r.destination,receipt=r.receipt,receipt_hash=r.receipt_hash,status=r.status,anchored_at=r.anchored_at,verified_at=r.verified_at)
    @staticmethod
    def _memory_response(r,content): return MemoryRecordResponse(id=r.id,external_id=r.external_id,version=r.version,agent_id=r.agent_id,trace_id=r.trace_id,source_uri=r.source_uri,source_type=r.source_type,content_hash=r.content_hash,provenance=r.provenance,data_classes=r.data_classes,trust_score=r.trust_score,status=r.status,expires_at=r.expires_at,created_at=r.created_at,content=content)
    @staticmethod
    def _delegation_response(r): return DelegationGrantResponse(id=r.id,parent_agent_id=r.parent_agent_id,child_agent_id=r.child_agent_id,parent_grant_id=r.parent_grant_id,trace_id=r.trace_id,objective=r.objective,allowed_tools=r.allowed_tools,allowed_data_classes=r.allowed_data_classes,resource_patterns=r.resource_patterns,max_depth=r.max_depth,max_fanout=r.max_fanout,budget_limits=r.budget_limits,expires_at=r.expires_at,grant_hash=r.grant_hash,signature=r.signature,status=r.status,created_at=r.created_at,revoked_at=r.revoked_at)
    @staticmethod
    def _budget_response(r): return RuntimeBudgetResponse(id=r.id,scope_type=r.scope_type,scope_id=r.scope_id,limits=r.limits,consumed=r.consumed,reserved=r.reserved,status=r.status,version=r.version,created_at=r.created_at,updated_at=r.updated_at)
    @staticmethod
    def _reservation_response(r): return BudgetReservationResponse(id=r.id,budget_id=r.budget_id,trace_id=r.trace_id,idempotency_key=r.idempotency_key,amounts=r.amounts,status=r.status,expires_at=r.expires_at,created_at=r.created_at,settled_at=r.settled_at)
    @staticmethod
    def _job_response(r): return TenantLifecycleJobResponse(id=r.id,job_type=r.job_type,idempotency_key=r.idempotency_key,status=r.status,parameters=r.parameters,result=r.result,result_storage_key=r.result_storage_key,attempt_count=r.attempt_count,fencing_token=r.fencing_token,reconciliation_status=r.reconciliation_status,last_error=r.last_error,created_at=r.created_at,updated_at=r.updated_at,completed_at=r.completed_at)
    @staticmethod
    def _protocol_response(r): return ProtocolRegistrationResponse(id=r.id,protocol=r.protocol,external_id=r.external_id,agent_id=r.agent_id,endpoint=r.endpoint,protocol_version=r.protocol_version,manifest=r.manifest,manifest_hash=r.manifest_hash,current_manifest_version=r.current_manifest_version,status=r.status,created_at=r.created_at,updated_at=r.updated_at)
    @staticmethod
    def _legal_hold_response(r): return LegalHoldResponse(id=r.id,scope=r.scope,reason=r.reason,expires_at=r.expires_at,status=r.status,created_at=r.created_at,released_at=r.released_at,release_reason=r.release_reason)
