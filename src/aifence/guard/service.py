# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .artifact_analysis import analyze_artifact
from .artifact_store import ArtifactStore, FileArtifactStore
from .audit import append_event, verify_tenant_chain
from .auth import KNOWN_SCOPES, AuthContext
from .capabilities import bound_action, consume_capability, issue_capability
from .clamav import ClamAVClient
from .config import Settings
from .crypto import EnvelopeCipher, SigningProvider, api_key_digest, generate_api_key, hash_object
from .db import set_tenant_context
from .detectors import calculate_risk, run_detectors
from .enforcement import build_enforcement_plan, mark_control_applied
from .errors import AuthorizationError, ConflictError, DependencyUnavailableError, NotFoundError
from .ids import new_id
from .metrics import APPROVAL_EVENTS, CAPABILITY_EVENTS, CONTROL_APPLICATIONS, EXECUTION_TRANSITIONS
from .models import (
    Agent,
    AgentProtocolRegistration,
    APIKey,
    Approval,
    ApprovalVote,
    Artifact,
    AuditCheckpoint,
    Capability,
    Decision,
    DispatchClaim,
    Event,
    Execution,
    Incident,
    MemoryRecord,
    OutboxMessage,
    PolicyBundle,
    Provider,
    Tenant,
    TenantKeyRoute,
    Tool,
)
from .network import ValidatedEndpoint, safe_join, validate_endpoint
from .policy import PolicyEngine, run_embedded_policy_tests, validate_policy_document
from .schemas import (
    AgentRegistration,
    AgentResponse,
    APIKeySummary,
    ApprovalDecisionIn,
    ApprovalResponse,
    ApprovalVoteResponse,
    ArtifactResponse,
    AuditCheckpointResponse,
    AuditVerificationResponse,
    CapabilityConsumeRequest,
    CapabilityIssueRequest,
    CapabilityResponse,
    CapabilityVerification,
    DecisionRequest,
    DecisionResponse,
    EventIngest,
    EventResponse,
    ExecutionRecoveryResponse,
    ExecutionResponse,
    Finding,
    IncidentCreate,
    IncidentResponse,
    IncidentStatusUpdate,
    PolicyBundleIn,
    PolicyBundleResponse,
    ProviderRegistration,
    ProviderResponse,
    ToolRegistration,
    ToolResponse,
)
from .tenant_crypto import TenantCryptography


class AifenceService:
    def __init__(
        self,
        settings: Settings,
        signing_key: SigningProvider,
        cipher: EnvelopeCipher,
        policy_engine: PolicyEngine,
        clamav: ClamAVClient,
        artifact_store: ArtifactStore | None = None,
        tenant_crypto: TenantCryptography | None = None,
    ) -> None:
        self.settings = settings
        self.signing_key = signing_key
        self.cipher = cipher
        self.policy_engine = policy_engine
        self.clamav = clamav
        self.artifact_store = artifact_store or FileArtifactStore(settings.artifact_store_path)
        self.tenant_crypto = tenant_crypto or TenantCryptography(cipher, settings)

    def create_tenant_and_key(
        self, session: Session, *, tenant_name: str, key_name: str, scopes: list[str]
    ) -> tuple[Tenant, APIKey, str]:
        tenant = Tenant(id=new_id("ten"), name=tenant_name, status="active")
        set_tenant_context(session, tenant.id)
        key_id, secret, token = generate_api_key()
        api_key = APIKey(
            id=key_id,
            tenant_id=tenant.id,
            name=key_name,
            secret_digest=api_key_digest(self.settings.pepper(), secret),
            scopes=scopes,
            status="active",
        )
        session.add(tenant)
        session.flush()
        session.add(api_key)
        append_event(
            session, self.signing_key, event_id=new_id("evt"), tenant_id=tenant.id,
            trace_id=new_id("trc"), parent_event_id=None, event_type="tenant.bootstrapped",
            payload={
                "tenant_id": tenant.id, "tenant_name": tenant.name,
                "initial_key_id": api_key.id, "initial_key_name": api_key.name,
                "scopes": api_key.scopes,
            },
        )
        session.commit()
        return tenant, api_key, token

    def create_api_key(
        self,
        session: Session,
        auth: AuthContext,
        *,
        name: str,
        scopes: list[str],
        expires_at: datetime | None = None,
        bound_agent_id: str | None = None,
        bound_workload_identity: str | None = None,
        bound_instance_id: str | None = None,
        bound_principal_type: str | None = None,
        bound_principal_id: str | None = None,
    ) -> tuple[APIKey, str]:
        auth.require("keys:write")
        requested_scopes = frozenset(scopes)
        unknown_scopes = requested_scopes - KNOWN_SCOPES - {"*"}
        if unknown_scopes:
            raise AuthorizationError(
                "API key requested unknown scopes",
                details={"unknown_scopes": sorted(unknown_scopes)},
            )
        if "*" not in auth.scopes and not requested_scopes.issubset(auth.scopes):
            raise AuthorizationError("API keys cannot delegate scopes they do not possess")
        now = datetime.now(UTC)
        normalized_expiry = expires_at
        if normalized_expiry and normalized_expiry.tzinfo is None:
            normalized_expiry = normalized_expiry.replace(tzinfo=UTC)
        if normalized_expiry and normalized_expiry <= now:
            raise ConflictError("API key expiration must be in the future")
        parent_expiry = auth.expires_at
        if parent_expiry and parent_expiry.tzinfo is None:
            parent_expiry = parent_expiry.replace(tzinfo=UTC)
        if parent_expiry and (normalized_expiry is None or normalized_expiry > parent_expiry):
            raise AuthorizationError("delegated API keys cannot outlive the creating key")

        bindings = {
            "bound_agent_id": bound_agent_id,
            "bound_workload_identity": bound_workload_identity,
            "bound_instance_id": bound_instance_id,
            "bound_principal_type": bound_principal_type,
            "bound_principal_id": bound_principal_id,
        }
        parent_bindings = {
            "bound_agent_id": auth.bound_agent_id,
            "bound_workload_identity": auth.bound_workload_identity,
            "bound_instance_id": auth.bound_instance_id,
            "bound_principal_type": auth.bound_principal_type,
            "bound_principal_id": auth.bound_principal_id,
        }
        for field_name, parent_value in parent_bindings.items():
            if parent_value is not None:
                if bindings[field_name] is None:
                    bindings[field_name] = parent_value
                elif bindings[field_name] != parent_value:
                    raise AuthorizationError("delegated API keys cannot broaden identity bindings")
        if (bindings["bound_principal_type"] is None) != (bindings["bound_principal_id"] is None):
            raise ConflictError("principal type and principal id bindings must be supplied together")
        if bindings["bound_agent_id"]:
            agent = session.scalar(
                select(Agent).where(
                    Agent.tenant_id == auth.tenant_id,
                    Agent.id == bindings["bound_agent_id"],
                    Agent.status == "active",
                )
            )
            if agent is None:
                raise NotFoundError("bound agent does not exist or is inactive")
            if bindings["bound_workload_identity"] is None:
                bindings["bound_workload_identity"] = agent.workload_identity
            elif bindings["bound_workload_identity"] != agent.workload_identity:
                raise AuthorizationError("API key workload binding does not match the registered agent")
        key_id, secret, token = generate_api_key()
        api_key = APIKey(
            id=key_id,
            tenant_id=auth.tenant_id,
            name=name,
            secret_digest=api_key_digest(self.settings.pepper(), secret),
            scopes=sorted(requested_scopes),
            status="active",
            expires_at=normalized_expiry,
            created_by_key_id=auth.key_id,
            **bindings,
        )
        session.add(api_key)
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=new_id("trc"),
            parent_event_id=None,
            event_type="api_key.created",
            payload={
                "key_id": api_key.id,
                "name": api_key.name,
                "scopes": api_key.scopes,
                "expires_at": normalized_expiry.isoformat() if normalized_expiry else None,
                "identity_bindings": bindings,
                "created_by_key_id": auth.key_id,
            },
        )
        session.commit()
        return api_key, token

    def register_agent(
        self, session: Session, auth: AuthContext, registration: AgentRegistration
    ) -> AgentResponse:
        auth.require("agents:write")
        manifest = registration.model_dump(mode="json")
        manifest["allowed_tools"] = sorted(set(registration.allowed_tools))
        manifest["allowed_data_classes"] = sorted(set(registration.allowed_data_classes))
        manifest_hash = hash_object(manifest)
        existing = session.scalar(
            select(Agent).where(
                Agent.tenant_id == auth.tenant_id,
                Agent.external_id == registration.external_id,
            )
        )
        if existing:
            if existing.manifest_hash != manifest_hash:
                raise ConflictError(
                    "agent manifests are immutable; register a new external_id for a changed build",
                    details={"existing_agent_id": existing.id, "existing_manifest_hash": existing.manifest_hash},
                )
            return self._agent_response(existing)
        now = datetime.now(UTC)
        agent = Agent(
            id=new_id("agt"),
            tenant_id=auth.tenant_id,
            external_id=registration.external_id,
            name=registration.name,
            version=registration.version,
            workload_identity=registration.workload_identity,
            model=registration.model,
            instruction_hash=registration.instruction_hash,
            deployment_digest=registration.deployment_digest,
            manifest_hash=manifest_hash,
            allowed_tools=manifest["allowed_tools"],
            allowed_data_classes=manifest["allowed_data_classes"],
            metadata_json=registration.metadata,
            status="active",
            created_by_key_id=auth.key_id,
            created_at=now,
            updated_at=now,
        )
        session.add(agent)
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=new_id("trc"),
            parent_event_id=None,
            event_type="agent.registered",
            payload={
                "agent_id": agent.id,
                "external_id": agent.external_id,
                "version": agent.version,
                "instruction_hash": agent.instruction_hash,
                "workload_identity": agent.workload_identity,
                "model": agent.model,
                "deployment_digest": agent.deployment_digest,
                "manifest_hash": manifest_hash,
                "key_id": auth.key_id,
            },
        )
        session.commit()
        return self._agent_response(agent)

    def get_agent(self, session: Session, auth: AuthContext, agent_id: str) -> AgentResponse:
        auth.require("agents:read")
        agent = session.scalar(
            select(Agent).where(Agent.tenant_id == auth.tenant_id, Agent.id == agent_id)
        )
        if not agent:
            raise NotFoundError("agent does not exist")
        return self._agent_response(agent)

    def decide(
        self, session: Session, auth: AuthContext, request: DecisionRequest
    ) -> DecisionResponse:
        auth.require("decisions:write")
        if "*" not in auth.scopes:
            required_bindings = {
                "agent_id": auth.bound_agent_id,
                "workload_identity": auth.bound_workload_identity,
                "instance_id": auth.bound_instance_id,
                "principal_type": auth.bound_principal_type,
                "principal_id": auth.bound_principal_id,
            }
            missing = sorted(name for name, value in required_bindings.items() if value is None)
            if missing:
                raise AuthorizationError(
                    "runtime decision keys must be fully bound to authenticated identity",
                    details={"missing_bindings": missing},
                )
        agent = session.scalar(
            select(Agent).where(
                Agent.tenant_id == auth.tenant_id,
                or_(Agent.id == request.agent.id, Agent.external_id == request.agent.id),
            )
        )
        if agent is None:
            raise AuthorizationError("decision references an unregistered agent")
        auth.assert_decision_identity(
            agent_id=agent.id,
            workload_identity=request.agent.workload_identity,
            instance_id=request.agent.instance_id,
            principal_type=request.principal.type,
            principal_id=request.principal.id,
        )
        mismatches = [
            field
            for field, registered, supplied in (
                ("version", agent.version, request.agent.version),
                ("workload_identity", agent.workload_identity, request.agent.workload_identity),
                ("model", agent.model, request.agent.model),
                ("instruction_hash", agent.instruction_hash, request.agent.instruction_hash),
            )
            if registered != supplied
        ]
        if mismatches:
            raise AuthorizationError(
                "running agent identity does not match its immutable registered manifest",
                details={"agent_id": agent.id, "mismatches": mismatches},
            )

        request_document = request.model_dump(mode="json")
        request_document["agent"]["id"] = agent.id
        request_document["approval_id"] = None
        request_document["idempotency_key"] = None
        request_hash = hash_object(request_document)
        if request.idempotency_key:
            existing = session.scalar(
                select(Decision).where(
                    Decision.tenant_id == auth.tenant_id,
                    Decision.idempotency_key == request.idempotency_key,
                )
            )
            if existing:
                if existing.request_hash != request_hash:
                    raise ConflictError("idempotency key was already used for a different request")
                return self._decision_response(existing)

        findings = run_detectors(request, agent)
        risk_score = calculate_risk(request, findings)
        active_policy_row = session.scalar(
            select(PolicyBundle).where(
                PolicyBundle.tenant_id == auth.tenant_id,
                PolicyBundle.active.is_(True),
            )
        )
        selected_policy_row = active_policy_row
        canary_policy_row = session.scalar(
            select(PolicyBundle)
            .where(
                PolicyBundle.tenant_id == auth.tenant_id,
                PolicyBundle.rollout_mode == "canary",
                PolicyBundle.canary_percentage > 0,
            )
            .order_by(PolicyBundle.created_at.desc(), PolicyBundle.id.desc())
        )
        if canary_policy_row is not None:
            rollout_secret = self.settings.policy_rollout_secret or self.settings.api_key_pepper
            if not rollout_secret:
                rollout_secret = self.signing_key.public_pem()
            stable_subject = "|".join(
                (
                    auth.tenant_id,
                    request.agent.id,
                    auth.bound_principal_id or request.principal.id,
                    canary_policy_row.id,
                    canary_policy_row.rollout_salt or canary_policy_row.document_hash,
                )
            ).encode("utf-8")
            digest = hmac.new(
                rollout_secret.encode("utf-8"), stable_subject, hashlib.sha256
            ).digest()
            rollout_bucket = int.from_bytes(digest[:8], "big") % 100
            if rollout_bucket < canary_policy_row.canary_percentage:
                selected_policy_row = canary_policy_row
        tenant_policy = selected_policy_row.document if selected_policy_row else None
        policy = self.policy_engine.evaluate(request_document, findings, risk_score, tenant_policy)
        shadow_results: list[dict[str, Any]] = []
        shadow_rows = list(
            session.scalars(
                select(PolicyBundle)
                .where(
                    PolicyBundle.tenant_id == auth.tenant_id,
                    PolicyBundle.rollout_mode == "shadow",
                )
                .order_by(PolicyBundle.created_at.desc(), PolicyBundle.id.desc())
                .limit(5)
            )
        )
        for shadow in shadow_rows:
            shadow_result = self.policy_engine.evaluate(
                request_document, findings, risk_score, shadow.document
            )
            shadow_results.append(
                {
                    "policy_id": shadow.id,
                    "policy_version": shadow_result.policy_version,
                    "outcome": shadow_result.outcome,
                    "matched_rule": shadow_result.matched_rule,
                    "constraints_hash": hash_object(shadow_result.constraints),
                }
            )
        outcome = policy.outcome
        reasons = list(policy.reasons)
        constraints = dict(policy.constraints)

        approved = False
        approval: Approval | None = None
        if request.approval_id:
            approval = self._validate_approval(session, auth.tenant_id, request.approval_id, request_hash)
            approved = True
            if outcome == "require_approval":
                outcome = "allow_with_limits"
                reasons = ["The configured independent approval quorum authorized this exact action"] + reasons
                constraints["approval_id"] = approval.id
                votes = list(
                    session.scalars(
                        select(ApprovalVote).where(
                            ApprovalVote.tenant_id == auth.tenant_id,
                            ApprovalVote.approval_id == approval.id,
                            ApprovalVote.decision == "approved",
                        )
                    )
                )
                constraints["approved_by_key_id"] = sorted(vote.key_id for vote in votes)
                constraints.setdefault("max_capability_uses", 1)

        enforcement_plan = build_enforcement_plan(
            request_document,
            outcome=outcome,
            constraints=constraints,
            runtime_attestation=agent.metadata_json,
        )
        if outcome in {"allow", "allow_with_limits", "redact_or_transform"} and not enforcement_plan["executable"]:
            outcome = "deny"
            reasons = ["A mandatory policy control could not be applied; enforcement failed closed"] + reasons
            enforcement_plan = build_enforcement_plan(
                request_document,
                outcome=outcome,
                constraints=constraints,
                runtime_attestation=agent.metadata_json,
            )

        for control in enforcement_plan.get("controls", []):
            CONTROL_APPLICATIONS.labels(
                str(control.get("type", "unknown")), str(control.get("status", "unknown"))
            ).inc()

        decision_id = new_id("dec")
        expires_at = datetime.now(UTC) + timedelta(minutes=5)
        approval_id: str | None = approval.id if approved and approval else None
        if outcome == "require_approval":
            approval_id = new_id("apr")

        receipt = self.signing_key.issue_receipt(
            {
                "aud": "aifence-decision",
                "sub": decision_id,
                "tenant_id": auth.tenant_id,
                "trace_id": request.trace_id,
                "agent_id": agent.id,
                "agent_manifest_hash": agent.manifest_hash,
                "principal_type": request.principal.type,
                "principal_id": request.principal.id,
                "request_hash": request_hash,
                "transformed_request_hash": enforcement_plan["transformed_request_hash"],
                "outcome": outcome,
                "risk_score": risk_score,
                "policy_version": policy.policy_version,
                "approval_id": approval_id,
                "constraints_hash": hash_object(constraints),
                "enforcement_plan_hash": hash_object(enforcement_plan),
            },
            lifetime_seconds=300,
        )
        decision = Decision(
            id=decision_id,
            tenant_id=auth.tenant_id,
            trace_id=request.trace_id,
            agent_id=agent.id,
            request_hash=request_hash,
            request_json=request_document,
            outcome=outcome,
            risk_score=risk_score,
            reasons=reasons,
            constraints=constraints,
            enforcement_plan=enforcement_plan,
            findings=[f.model_dump(mode="json") for f in findings],
            policy_version=policy.policy_version,
            receipt=receipt,
            approval_id=approval_id,
            idempotency_key=request.idempotency_key,
            expires_at=expires_at,
        )
        session.add(decision)
        session.flush()

        if outcome == "require_approval" and approval_id:
            ttl = int(constraints.get("approval_ttl_seconds", 900))
            required_approvals = 2 if bool(constraints.get("dual_control")) else 1
            approval = Approval(
                id=approval_id,
                tenant_id=auth.tenant_id,
                trace_id=request.trace_id,
                decision_id=decision.id,
                request_hash=request_hash,
                requested_by_key_id=auth.key_id,
                status="pending",
                request_json=request_document,
                required_approvals=required_approvals,
                approval_count=0,
                created_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(seconds=ttl),
            )
            session.add(approval)

        event = append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=request.trace_id,
            parent_event_id=request.parent_event_id,
            event_type="decision.evaluated",
            payload={
                "decision_id": decision.id,
                "agent_id": agent.id,
                "agent_manifest_hash": agent.manifest_hash,
                "principal": {"type": request.principal.type, "id": request.principal.id},
                "request_hash": request_hash,
                "transformed_request_hash": enforcement_plan["transformed_request_hash"],
                "outcome": outcome,
                "risk_score": risk_score,
                "reasons": reasons,
                "constraints": constraints,
                "enforcement_plan": enforcement_plan,
                "findings": decision.findings,
                "policy_version": policy.policy_version,
                "selected_policy_id": selected_policy_row.id if selected_policy_row else None,
                "rollout_mode": selected_policy_row.rollout_mode if selected_policy_row else "baseline",
                "matched_rule": policy.matched_rule,
                "shadow_results": shadow_results,
                "approval_id": approval_id,
                "requested_by_key_id": auth.key_id,
            },
        )

        mark_control_applied(
            enforcement_plan,
            "audit",
            {"event_id": event.id, "event_hash": event.event_hash, "sequence": event.sequence},
        )
        decision.enforcement_plan = enforcement_plan

        if outcome in {"deny", "quarantine_and_terminate"} or any(f.severity == "critical" for f in findings):
            severity = "critical" if outcome == "quarantine_and_terminate" else "high"
            session.add(
                Incident(
                    id=new_id("inc"),
                    tenant_id=auth.tenant_id,
                    trace_id=request.trace_id,
                    severity=severity,
                    category="agent_security_decision",
                    title=f"AIFENCE enforced {outcome}",
                    description="The enforcement pipeline identified a prohibited or high-risk action.",
                    status="open",
                    evidence=[
                        {"event_id": event.id, "decision_id": decision.id, "request_hash": request_hash},
                        *decision.findings,
                    ],
                )
            )
        self._apply_post_decision_controls(session, auth, agent, request, decision)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            if request.idempotency_key:
                existing = session.scalar(
                    select(Decision).where(
                        Decision.tenant_id == auth.tenant_id,
                        Decision.idempotency_key == request.idempotency_key,
                    )
                )
                if existing:
                    if existing.request_hash != request_hash:
                        raise ConflictError("idempotency key was concurrently used for a different request") from exc
                    return self._decision_response(existing)
            raise ConflictError("decision could not be persisted") from exc
        return self._decision_response(decision)

    def _apply_post_decision_controls(
        self,
        session: Session,
        auth: AuthContext,
        agent: Agent,
        request: DecisionRequest,
        decision: Decision,
    ) -> None:
        constraints = decision.constraints
        plan = decision.enforcement_plan
        if decision.outcome == "quarantine_and_terminate" or bool(constraints.get("terminate_descendants")):
            agent.status = "quarantined"
            agent.revoked_by_key_id = auth.key_id
            agent.revocation_reason = "quarantine_and_terminate policy outcome"
            agent.updated_at = datetime.now(UTC)
            # Descendants are represented through immutable manifest metadata.
            changed = True
            terminated_ids = {agent.id}
            while changed:
                changed = False
                candidates = list(
                    session.scalars(
                        select(Agent).where(Agent.tenant_id == auth.tenant_id, Agent.status == "active")
                    )
                )
                for candidate in candidates:
                    parent = candidate.metadata_json.get("parent_agent_id")
                    if parent in terminated_ids:
                        candidate.status = "quarantined"
                        candidate.revoked_by_key_id = auth.key_id
                        candidate.revocation_reason = f"ancestor {parent} was quarantined"
                        candidate.updated_at = datetime.now(UTC)
                        terminated_ids.add(candidate.id)
                        changed = True
            mark_control_applied(plan, "terminate_descendants", {"terminated_agent_ids": sorted(terminated_ids)})
        if decision.outcome == "quarantine_and_terminate" or bool(constraints.get("revoke_capabilities")):
            result = session.execute(
                update(Capability)
                .where(
                    Capability.tenant_id == auth.tenant_id,
                    Capability.agent_id == agent.id,
                    Capability.status == "active",
                )
                .values(status="revoked")
            )
            mark_control_applied(plan, "revoke_capabilities", {"revoked": result.rowcount or 0})
        if bool(constraints.get("require_reregistration")):
            agent.status = "suspended"
            agent.revoked_by_key_id = auth.key_id
            agent.revocation_reason = "registered runtime integrity no longer matches"
            agent.updated_at = datetime.now(UTC)
            mark_control_applied(plan, "require_reregistration", {"agent_id": agent.id})
        if bool(constraints.get("revoke_exposed_credentials")):
            key = session.get(APIKey, auth.key_id)
            if key is not None:
                key.status = "compromised"
                mark_control_applied(plan, "revoke_exposed_credentials", {"revoked_key_id": auth.key_id})
        if bool(constraints.get("open_incident")):
            incident = Incident(
                id=new_id("inc"),
                tenant_id=auth.tenant_id,
                trace_id=request.trace_id,
                severity="high",
                category="policy_required_incident",
                title="Policy-required AIFENCE incident",
                description="An active policy required an incident for this decision.",
                status="open",
                evidence=[{"decision_id": decision.id, "request_hash": decision.request_hash}],
            )
            session.add(incident)
            mark_control_applied(plan, "open_incident", {"incident_id": incident.id})
        if bool(constraints.get("quarantine_artifact")) and request.action.target:
            artifact_id = request.action.target.removeprefix("artifact:")
            artifact = session.scalar(
                select(Artifact).where(
                    Artifact.tenant_id == auth.tenant_id,
                    Artifact.id == artifact_id,
                )
            )
            if artifact is not None:
                artifact.quarantined = True
                mark_control_applied(plan, "quarantine_artifact", {"artifact_id": artifact.id})
        decision.enforcement_plan = plan

    def ingest_event(
        self, session: Session, auth: AuthContext, event_in: EventIngest
    ) -> EventResponse:
        auth.require("events:write")
        event = append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=event_in.trace_id,
            parent_event_id=event_in.parent_event_id,
            event_type=event_in.event_type,
            payload={**event_in.payload, "ingested_by_key_id": auth.key_id},
        )
        session.commit()
        return self._event_response(event)

    def get_trace(
        self, session: Session, auth: AuthContext, trace_id: str,
        *, limit: int = 500, after_sequence: int | None = None,
    ) -> list[EventResponse]:
        auth.require("events:read")
        page_size = min(max(limit, 1), self.settings.max_page_size)
        statement = select(Event).where(
            Event.tenant_id == auth.tenant_id, Event.trace_id == trace_id
        )
        if after_sequence is not None:
            statement = statement.where(Event.sequence > after_sequence)
        events = session.scalars(
            statement.order_by(Event.sequence.asc()).limit(page_size)
        )
        return [self._event_response(event) for event in events]

    def verify_audit_chain(
        self, session: Session, auth: AuthContext
    ) -> AuditVerificationResponse:
        auth.require("audit:verify")
        return AuditVerificationResponse(**verify_tenant_chain(session, self.signing_key, auth.tenant_id))

    def list_audit_checkpoints(
        self, session: Session, auth: AuthContext, *, limit: int = 100,
        before_sequence: int | None = None,
    ) -> list[AuditCheckpointResponse]:
        auth.require("audit:read")
        limit = min(max(limit, 1), self.settings.max_page_size)
        statement = select(AuditCheckpoint).where(AuditCheckpoint.tenant_id == auth.tenant_id)
        if before_sequence is not None:
            statement = statement.where(AuditCheckpoint.sequence < before_sequence)
        rows = list(session.scalars(
            statement.order_by(AuditCheckpoint.sequence.desc()).limit(limit)
        ))
        return [AuditCheckpointResponse(
            id=row.id, sequence=row.sequence, head_hash=row.head_hash,
            signature=row.signature, key_id=row.key_id, created_at=row.created_at
        ) for row in rows]

    def publish_policy(
        self, session: Session, auth: AuthContext, bundle_in: PolicyBundleIn
    ) -> PolicyBundleResponse:
        auth.require("policies:write")
        if bundle_in.activate:
            raise ConflictError(
                "policy publication and activation are separate operations"
            )
        validate_policy_document(bundle_in.document)
        if bundle_in.document.get("version") != bundle_in.version:
            raise ConflictError("request version must equal document version")
        validation_report = run_embedded_policy_tests(
            self.policy_engine.baseline, bundle_in.document
        )
        if not bool(validation_report.get("valid")):
            raise ConflictError(
                "policy embedded tests failed",
                details={"validation_report": validation_report},
            )
        document_hash = hash_object(bundle_in.document)
        bundle = PolicyBundle(
            id=new_id("pol"),
            tenant_id=auth.tenant_id,
            version=bundle_in.version,
            document=bundle_in.document,
            document_hash=document_hash,
            active=False,
            created_by_key_id=auth.key_id,
            activated_at=None,
            activated_by_key_id=None,
            activation_reason=None,
            rollout_mode="inactive",
            canary_percentage=0,
            rollout_salt=secrets.token_hex(16),
            validation_report=validation_report,
            supersedes_policy_id=None,
        )
        session.add(bundle)
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=new_id("trc"),
            parent_event_id=None,
            event_type="policy.published",
            payload={
                "policy_id": bundle.id,
                "version": bundle.version,
                "document_hash": document_hash,
                "active": False,
                "validation_report": validation_report,
                "published_by_key_id": auth.key_id,
            },
        )
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ConflictError("policy version already exists") from exc
        return self._policy_response(bundle)

    def activate_policy(
        self,
        session: Session,
        auth: AuthContext,
        policy_id: str,
        reason: str,
    ) -> PolicyBundleResponse:
        auth.require("policies:activate")
        stmt = select(PolicyBundle).where(
            PolicyBundle.tenant_id == auth.tenant_id,
            PolicyBundle.id == policy_id,
        )
        if session.bind and session.bind.dialect.name == "postgresql":
            stmt = stmt.with_for_update()
        bundle = session.scalar(stmt)
        if bundle is None:
            raise NotFoundError("policy does not exist")
        tenant_lock = select(Tenant).where(Tenant.id == auth.tenant_id)
        if session.bind and session.bind.dialect.name == "postgresql":
            tenant_lock = tenant_lock.with_for_update()
        if session.scalar(tenant_lock) is None:
            raise NotFoundError("tenant does not exist")
        if bundle.created_by_key_id == auth.key_id:
            raise AuthorizationError("a policy publisher cannot activate the same policy")
        if bundle.active:
            raise ConflictError("policy is already active")
        validation_report = bundle.validation_report or run_embedded_policy_tests(
            self.policy_engine.baseline, bundle.document
        )
        if not bool(validation_report.get("valid")):
            raise ConflictError(
                "policy cannot be activated because validation failed",
                details={"validation_report": validation_report},
            )
        previous_active = session.scalar(
            select(PolicyBundle).where(
                PolicyBundle.tenant_id == auth.tenant_id,
                PolicyBundle.active.is_(True),
            )
        )
        session.execute(
            update(PolicyBundle)
            .where(
                PolicyBundle.tenant_id == auth.tenant_id,
                PolicyBundle.active.is_(True),
            )
            .values(active=False, rollout_mode="inactive", canary_percentage=0)
        )
        bundle.active = True
        bundle.rollout_mode = "active"
        bundle.canary_percentage = 100
        bundle.validation_report = validation_report
        bundle.supersedes_policy_id = previous_active.id if previous_active else None
        bundle.activated_at = datetime.now(UTC)
        bundle.activated_by_key_id = auth.key_id
        bundle.activation_reason = reason
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=new_id("trc"),
            parent_event_id=None,
            event_type="policy.activated",
            payload={
                "policy_id": bundle.id,
                "version": bundle.version,
                "document_hash": bundle.document_hash,
                "published_by_key_id": bundle.created_by_key_id,
                "activated_by_key_id": auth.key_id,
                "reason": reason,
                "supersedes_policy_id": bundle.supersedes_policy_id,
                "validation_report": validation_report,
            },
        )
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ConflictError("another policy activation won the concurrent update") from exc
        return self._policy_response(bundle)

    def get_approval(
        self, session: Session, auth: AuthContext, approval_id: str
    ) -> ApprovalResponse:
        auth.require("approvals:read")
        approval = session.scalar(
            select(Approval).where(
                Approval.tenant_id == auth.tenant_id, Approval.id == approval_id
            )
        )
        if not approval:
            raise NotFoundError("approval does not exist")
        return self._approval_response(session, approval)

    def decide_approval(
        self,
        session: Session,
        auth: AuthContext,
        approval_id: str,
        body: ApprovalDecisionIn,
    ) -> ApprovalResponse:
        auth.require("approvals:write")
        stmt = select(Approval).where(
            Approval.tenant_id == auth.tenant_id,
            Approval.id == approval_id,
        )
        if session.bind and session.bind.dialect.name == "postgresql":
            stmt = stmt.with_for_update()
        approval = session.scalar(stmt)
        if not approval:
            raise NotFoundError("approval does not exist")
        now = datetime.now(UTC)
        expires = approval.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        if approval.status not in {"pending", "partially_approved"}:
            raise ConflictError("approval has already been decided")
        if expires <= now:
            approval.status = "expired"
            session.commit()
            raise ConflictError("approval has expired")
        if approval.requested_by_key_id == auth.key_id:
            raise AuthorizationError("the requesting API key cannot approve its own action")
        existing_vote = session.scalar(
            select(ApprovalVote).where(
                ApprovalVote.tenant_id == auth.tenant_id,
                ApprovalVote.approval_id == approval.id,
                ApprovalVote.key_id == auth.key_id,
            )
        )
        if existing_vote is not None:
            raise ConflictError("this API key has already voted on the approval")
        vote = ApprovalVote(
            id=new_id("apv"),
            tenant_id=auth.tenant_id,
            approval_id=approval.id,
            key_id=auth.key_id,
            decision=body.decision,
            reason=body.reason,
            created_at=now,
        )
        session.add(vote)
        if body.decision == "rejected":
            approval.status = "rejected"
            approval.decision_reason = body.reason
            approval.decided_by_key_id = auth.key_id
            approval.decided_at = now
        else:
            approval.approval_count += 1
            if approval.approval_count >= approval.required_approvals:
                approval.status = "approved"
                approval.decision_reason = "Required independent approval quorum reached"
                approval.decided_by_key_id = auth.key_id
                approval.decided_at = now
            else:
                approval.status = "partially_approved"
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=approval.trace_id,
            parent_event_id=None,
            event_type="approval.vote_recorded",
            payload={
                "approval_id": approval.id,
                "decision_id": approval.decision_id,
                "vote": body.decision,
                "reason": body.reason,
                "voter_key_id": auth.key_id,
                "approval_count": approval.approval_count,
                "required_approvals": approval.required_approvals,
                "status": approval.status,
            },
        )
        session.commit()
        APPROVAL_EVENTS.labels(approval.status).inc()
        return self._approval_response(session, approval)

    def issue_capability_token(
        self,
        session: Session,
        auth: AuthContext,
        body: CapabilityIssueRequest,
    ) -> CapabilityResponse:
        auth.require("capabilities:issue")
        decision = session.scalar(
            select(Decision).where(
                Decision.tenant_id == auth.tenant_id, Decision.id == body.decision_id
            )
        )
        if not decision:
            raise NotFoundError("decision does not exist")
        capability, token = issue_capability(
            session,
            self.signing_key,
            tenant_id=auth.tenant_id,
            decision=decision,
            lifetime_seconds=body.lifetime_seconds,
            requested_max_uses=body.max_uses,
        )
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=decision.trace_id,
            parent_event_id=None,
            event_type="capability.issued",
            payload={
                "capability_id": capability.id,
                "decision_id": decision.id,
                "request_hash": capability.request_hash,
                "arguments_hash": capability.arguments_hash,
                "tool": capability.tool,
                "operation": capability.operation,
                "resources": capability.resources,
                "max_uses": capability.max_uses,
                "expires_at": capability.expires_at.isoformat(),
            },
        )
        session.commit()
        CAPABILITY_EVENTS.labels("issued").inc()
        _, _, _, required_execution = bound_action(decision)
        return CapabilityResponse(
            capability_id=capability.id,
            token=token,
            expires_at=capability.expires_at,
            max_uses=capability.max_uses,
            constraints=capability.constraints,
            required_execution=required_execution,
        )

    def consume_capability_token(
        self,
        session: Session,
        auth: AuthContext,
        body: CapabilityConsumeRequest,
    ) -> CapabilityVerification:
        auth.require("capabilities:consume")
        capability = consume_capability(
            session,
            self.signing_key,
            tenant_id=auth.tenant_id,
            token=body.token,
            agent_id=body.agent_id,
            trace_id=body.trace_id,
            tool=body.tool,
            operation=body.operation,
            resource=body.resource,
            execution=body.execution,
        )
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=capability.trace_id,
            parent_event_id=None,
            event_type="capability.consumed",
            payload={
                "capability_id": capability.id,
                "tool": body.tool,
                "operation": body.operation,
                "resource": body.resource,
                "use_count": capability.use_count,
                "max_uses": capability.max_uses,
                "status": capability.status,
            },
        )
        session.commit()
        CAPABILITY_EVENTS.labels("consumed").inc()
        return CapabilityVerification(
            valid=True,
            capability_id=capability.id,
            remaining_uses=max(0, capability.max_uses - capability.use_count),
            constraints=capability.constraints,
        )

    def scan_artifact(
        self,
        session: Session,
        auth: AuthContext,
        *,
        trace_id: str,
        filename: str,
        media_type: str,
        content: bytes,
    ) -> ArtifactResponse:
        auth.require("artifacts:write")
        if len(content) > self.settings.max_artifact_bytes:
            raise ConflictError("artifact exceeds the configured size limit")
        sha256 = hashlib.sha256(content).hexdigest()
        analysis = analyze_artifact(
            content,
            declared_media_type=media_type,
            max_uncompressed_bytes=self.settings.max_artifact_bytes * 10,
        )
        try:
            scan = self.clamav.scan(content)
        except (TimeoutError, OSError) as exc:
            if self.settings.clamav_required:
                raise DependencyUnavailableError("malware scanner is unavailable") from exc
            scan = None
        if scan is None:
            scan_status = "unavailable"
            scan_result = {"status": "unavailable"}
            quarantined = True
            event_type = "artifact.scan_unavailable"
        elif scan.status == "infected":
            scan_status = "infected"
            scan_result = {"status": scan.status, "signature": scan.signature, "raw": scan.raw}
            quarantined = True
            event_type = "artifact.malware_detected"
        elif scan.status == "clean":
            scan_status = "clean"
            scan_result = {"status": scan.status, "raw": scan.raw}
            quarantined = False
            event_type = "artifact.clean"
        else:
            scan_status = "error"
            scan_result = {"status": scan.status, "raw": scan.raw}
            quarantined = True
            event_type = "artifact.scan_error"
        scan_result["content_analysis"] = {
            "detected_type": analysis.detected_type,
            "findings": analysis.findings,
        }
        if not analysis.safe_to_release:
            scan_status = "unsafe"
            quarantined = True
            event_type = "artifact.unsafe_content_detected"
        artifact_id = new_id("art")
        context = f"{auth.tenant_id}:{artifact_id}:{sha256}".encode()
        encrypted = self.tenant_crypto.encrypt(session, auth.tenant_id, content, context=context)
        now = datetime.now(UTC)
        artifact = Artifact(
            id=artifact_id,
            tenant_id=auth.tenant_id,
            trace_id=trace_id,
            filename=filename,
            media_type=media_type,
            size_bytes=len(content),
            sha256=sha256,
            encrypted_blob=None,
            storage_key=self.artifact_store.put(auth.tenant_id, artifact_id, encrypted),
            scan_status=scan_status,
            scan_result=scan_result,
            quarantined=quarantined,
            created_at=now,
            expires_at=now + timedelta(days=self.settings.artifact_retention_days),
        )
        session.add(artifact)
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=trace_id,
            parent_event_id=None,
            event_type=event_type,
            payload={
                "artifact_id": artifact.id,
                "filename": filename,
                "media_type": media_type,
                "size_bytes": len(content),
                "sha256": sha256,
                "scan_status": scan_status,
                "quarantined": quarantined,
                "scan_result": scan_result,
            },
        )
        if quarantined:
            session.add(
                Incident(
                    id=new_id("inc"),
                    tenant_id=auth.tenant_id,
                    trace_id=trace_id,
                    severity="critical" if scan_status == "infected" else "high",
                    category="malware" if scan_status == "infected" else "artifact_scan_failure",
                    title="Artifact quarantined by AIFENCE",
                    description="The artifact was not released because its malware scan did not produce a clean result.",
                    status="open",
                    evidence=[{"artifact_id": artifact.id, "sha256": sha256, **scan_result}],
                )
            )
        session.commit()
        return self._artifact_response(artifact)

    def get_artifact_content(
        self, session: Session, auth: AuthContext, artifact_id: str
    ) -> tuple[Artifact, bytes]:
        auth.require("artifacts:read")
        artifact = session.scalar(
            select(Artifact).where(
                Artifact.tenant_id == auth.tenant_id, Artifact.id == artifact_id
            )
        )
        if not artifact:
            raise NotFoundError("artifact does not exist")
        if artifact.quarantined and "artifacts:quarantine:read" not in auth.scopes and "*" not in auth.scopes:
            raise AuthorizationError("quarantined artifacts require a dedicated read scope")
        context = f"{auth.tenant_id}:{artifact.id}:{artifact.sha256}".encode()
        encrypted = (
            self.artifact_store.get(artifact.storage_key)
            if artifact.storage_key
            else artifact.encrypted_blob
        )
        if encrypted is None:
            raise DependencyUnavailableError("artifact content is unavailable")
        return artifact, self.tenant_crypto.decrypt(session, auth.tenant_id, encrypted, context=context)

    def create_incident(
        self, session: Session, auth: AuthContext, body: IncidentCreate
    ) -> IncidentResponse:
        auth.require("incidents:write")
        incident = Incident(
            id=new_id("inc"),
            tenant_id=auth.tenant_id,
            trace_id=body.trace_id,
            severity=body.severity,
            category=body.category,
            title=body.title,
            description=body.description,
            status="open",
            evidence=body.evidence,
        )
        session.add(incident)
        session.commit()
        return self._incident_response(incident)

    def get_incident(
        self, session: Session, auth: AuthContext, incident_id: str
    ) -> IncidentResponse:
        auth.require("incidents:read")
        incident = session.scalar(
            select(Incident).where(
                Incident.tenant_id == auth.tenant_id, Incident.id == incident_id
            )
        )
        if not incident:
            raise NotFoundError("incident does not exist")
        return self._incident_response(incident)

    def register_provider(
        self, session: Session, auth: AuthContext, body: ProviderRegistration
    ) -> ProviderResponse:
        auth.require("providers:write")
        if body.network_zone == "private":
            auth.require("brokers:private")
        endpoint = validate_endpoint(
            body.base_url,
            allowed_hosts=self.settings.provider_allowed_hosts,
            network_zone=body.network_zone,
            require_resolution=self.settings.environment in {"staging", "production"},
            resolution_timeout_seconds=self.settings.dns_resolution_timeout_seconds,
        )
        provider_id = new_id("prv")
        encrypted = self.tenant_crypto.encrypt(
            session, auth.tenant_id, body.auth_value.encode(),
            context=f"{auth.tenant_id}:{provider_id}:provider".encode(),
        )
        provider = Provider(
            id=provider_id,
            tenant_id=auth.tenant_id,
            name=body.name,
            base_url=endpoint.canonical_url,
            auth_header_name=body.auth_header_name,
            encrypted_auth_value=encrypted,
            allowed_paths=body.allowed_paths,
            network_zone=body.network_zone,
            resolved_addresses=list(endpoint.resolved_addresses),
            status="active",
        )
        session.add(provider)
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=new_id("trc"),
            parent_event_id=None,
            event_type="provider.registered",
            payload={
                "provider_id": provider.id,
                "name": provider.name,
                "base_url": provider.base_url,
                "network_zone": provider.network_zone,
                "resolved_addresses": provider.resolved_addresses,
                "allowed_paths": provider.allowed_paths,
                "registered_by_key_id": auth.key_id,
            },
        )
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ConflictError("provider name already exists") from exc
        return self._provider_response(provider)

    def register_tool(
        self, session: Session, auth: AuthContext, body: ToolRegistration
    ) -> ToolResponse:
        auth.require("tools:write")
        if body.network_zone == "private":
            auth.require("brokers:private")
        endpoint = validate_endpoint(
            body.base_url,
            allowed_hosts=self.settings.tool_allowed_hosts,
            network_zone=body.network_zone,
            require_resolution=self.settings.environment in {"staging", "production"},
            resolution_timeout_seconds=self.settings.dns_resolution_timeout_seconds,
        )
        self._validate_tool_operations(body.allowed_operations)
        tool_id = new_id("tol")
        encrypted = self.tenant_crypto.encrypt(
            session, auth.tenant_id, body.auth_value.encode(),
            context=f"{auth.tenant_id}:{tool_id}:tool".encode(),
        )
        tool = Tool(
            id=tool_id,
            tenant_id=auth.tenant_id,
            name=body.name,
            base_url=endpoint.canonical_url,
            auth_header_name=body.auth_header_name,
            encrypted_auth_value=encrypted,
            allowed_operations=body.allowed_operations,
            network_zone=body.network_zone,
            resolved_addresses=list(endpoint.resolved_addresses),
            status="active",
        )
        session.add(tool)
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=new_id("trc"),
            parent_event_id=None,
            event_type="tool.registered",
            payload={
                "tool_id": tool.id,
                "name": tool.name,
                "base_url": tool.base_url,
                "network_zone": tool.network_zone,
                "resolved_addresses": tool.resolved_addresses,
                "allowed_operations": tool.allowed_operations,
                "registered_by_key_id": auth.key_id,
            },
        )
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ConflictError("tool name already exists") from exc
        return self._tool_response(tool)

    def provider_auth(self, session: Session, provider: Provider) -> str:
        return self.tenant_crypto.decrypt(
            session, provider.tenant_id, provider.encrypted_auth_value,
            context=f"{provider.tenant_id}:{provider.id}:provider".encode(),
        ).decode()

    def tool_auth(self, session: Session, tool: Tool) -> str:
        return self.tenant_crypto.decrypt(
            session, tool.tenant_id, tool.encrypted_auth_value,
            context=f"{tool.tenant_id}:{tool.id}:tool".encode(),
        ).decode()

    def get_provider(self, session: Session, tenant_id: str, provider_id: str) -> Provider:
        provider = session.scalar(
            select(Provider).where(
                Provider.tenant_id == tenant_id, Provider.id == provider_id, Provider.status == "active"
            )
        )
        if not provider:
            raise NotFoundError("provider does not exist or is inactive")
        return provider

    def get_tool(self, session: Session, tenant_id: str, tool_id: str) -> Tool:
        tool = session.scalar(
            select(Tool).where(
                Tool.tenant_id == tenant_id, Tool.id == tool_id, Tool.status == "active"
            )
        )
        if not tool:
            raise NotFoundError("tool does not exist or is inactive")
        return tool

    def validate_provider_path(
        self, provider: Provider, path: str
    ) -> tuple[str, ValidatedEndpoint]:
        endpoint = validate_endpoint(
            provider.base_url,
            allowed_hosts=self.settings.provider_allowed_hosts,
            network_zone=provider.network_zone,
            require_resolution=self.settings.environment in {"staging", "production"},
            resolution_timeout_seconds=self.settings.dns_resolution_timeout_seconds,
        )
        if provider.resolved_addresses and set(endpoint.resolved_addresses) != set(provider.resolved_addresses):
            raise AuthorizationError("provider DNS resolution changed since registration")
        return safe_join(provider.base_url, path, provider.allowed_paths), endpoint

    def validate_tool_call(
        self, tool: Tool, operation: str, method: str, path: str
    ) -> tuple[str, ValidatedEndpoint]:
        endpoint = validate_endpoint(
            tool.base_url,
            allowed_hosts=self.settings.tool_allowed_hosts,
            network_zone=tool.network_zone,
            require_resolution=self.settings.environment in {"staging", "production"},
            resolution_timeout_seconds=self.settings.dns_resolution_timeout_seconds,
        )
        if tool.resolved_addresses and set(endpoint.resolved_addresses) != set(tool.resolved_addresses):
            raise AuthorizationError("tool DNS resolution changed since registration")
        rule = tool.allowed_operations.get(operation)
        if not isinstance(rule, dict):
            raise AuthorizationError("tool operation is not registered")
        allowed_method = str(rule.get("method", "")).upper()
        allowed_paths = rule.get("paths")
        if method.upper() != allowed_method or not isinstance(allowed_paths, list):
            raise AuthorizationError("tool method is not permitted for this operation")
        return safe_join(tool.base_url, path, allowed_paths), endpoint

    def consume_tool_capability(
        self,
        session: Session,
        auth: AuthContext,
        *,
        token: str,
        agent_id: str,
        trace_id: str,
        tool_name: str,
        operation: str,
        resource: str,
        execution: dict[str, Any],
    ) -> Capability:
        auth.require("tools:execute")
        capability = consume_capability(
            session,
            self.signing_key,
            tenant_id=auth.tenant_id,
            token=token,
            agent_id=agent_id,
            trace_id=trace_id,
            tool=tool_name,
            operation=operation,
            resource=resource,
            execution=execution,
        )
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=capability.trace_id,
            parent_event_id=None,
            event_type="tool.execution_authorized",
            payload={
                "capability_id": capability.id,
                "tool": tool_name,
                "operation": operation,
                "resource": resource,
                "use_count": capability.use_count,
            },
        )
        session.commit()
        return capability

    def audit_broker_result(
        self,
        session: Session,
        auth: AuthContext,
        *,
        trace_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=trace_id,
            parent_event_id=None,
            event_type=event_type,
            payload=payload,
        )
        session.commit()

    def prepare_provider_execution(
        self,
        session: Session,
        auth: AuthContext,
        *,
        provider: Provider,
        decision_id: str,
        trace_id: str,
        idempotency_key: str,
        original_request: dict[str, Any],
        transformed_request: dict[str, Any],
        controls: list[dict[str, Any]],
    ) -> tuple[Execution, bool]:
        auth.require("providers:invoke")
        decision = session.scalar(
            select(Decision).where(
                Decision.tenant_id == auth.tenant_id,
                Decision.id == decision_id,
            )
        )
        if decision is None or decision.trace_id != trace_id:
            raise AuthorizationError("provider execution is not bound to an active decision")
        if decision.outcome not in {"allow", "allow_with_limits", "redact_or_transform"}:
            raise AuthorizationError("provider execution decision does not permit dispatch")
        if not decision.enforcement_plan.get("executable", False):
            raise AuthorizationError("provider enforcement plan is not executable")
        return self._prepare_execution_record(
            session,
            auth,
            broker_type="provider",
            broker_id=provider.id,
            trace_id=trace_id,
            decision_id=decision.id,
            capability_id=None,
            idempotency_key=idempotency_key,
            original_request=original_request,
            transformed_request=transformed_request,
            controls=controls,
        )

    def prepare_tool_execution(
        self,
        session: Session,
        auth: AuthContext,
        *,
        tool: Tool,
        token: str,
        agent_id: str,
        trace_id: str,
        operation: str,
        resource: str,
        execution_request: dict[str, Any],
        idempotency_key: str,
    ) -> tuple[Execution, bool]:
        auth.require("tools:execute")
        request_hash = hash_object(execution_request)
        existing = session.scalar(
            select(Execution).where(
                Execution.tenant_id == auth.tenant_id,
                Execution.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            if existing.request_hash != request_hash or existing.broker_id != tool.id:
                raise ConflictError("execution idempotency key was used for another request")
            if existing.state in {"succeeded", "dispatching", "outcome_unknown"}:
                return existing, False
            existing.state = "dispatching"
            existing.attempt_count += 1
            existing.updated_at = datetime.now(UTC)
            existing.lease_expires_at = existing.updated_at + timedelta(seconds=self.settings.execution_lease_seconds)
            append_event(
                session,
                self.signing_key,
                event_id=new_id("evt"),
                tenant_id=auth.tenant_id,
                trace_id=trace_id,
                parent_event_id=None,
                event_type="execution.redispatching",
                payload={"execution_id": existing.id, "attempt": existing.attempt_count},
            )
            session.commit()
            return existing, True
        capability = consume_capability(
            session,
            self.signing_key,
            tenant_id=auth.tenant_id,
            token=token,
            agent_id=agent_id,
            trace_id=trace_id,
            tool=tool.name,
            operation=operation,
            resource=resource,
            execution=execution_request,
        )
        decision = session.scalar(
            select(Decision).where(
                Decision.tenant_id == auth.tenant_id,
                Decision.id == capability.decision_id,
            )
        )
        if decision is None:
            raise AuthorizationError("capability decision no longer exists")
        controls = list(decision.enforcement_plan.get("controls", []))
        controls.append(
            {
                "type": "capability_binding",
                "required": True,
                "status": "applied",
                "parameters": {},
                "evidence": {
                    "capability_id": capability.id,
                    "use_count": capability.use_count,
                    "max_uses": capability.max_uses,
                    "operation": execution_request.get("operation"),
                    "resource": execution_request.get("resource"),
                },
            }
        )
        return self._prepare_execution_record(
            session,
            auth,
            broker_type="tool",
            broker_id=tool.id,
            trace_id=trace_id,
            decision_id=capability.decision_id,
            capability_id=capability.id,
            idempotency_key=idempotency_key,
            original_request=execution_request,
            transformed_request=execution_request,
            controls=controls,
        )

    def protocol_auth(self, session: Session, registration: AgentProtocolRegistration) -> tuple[str | None, str | None]:
        if registration.encrypted_auth_value is None:
            return registration.auth_header_name, None
        value = self.tenant_crypto.decrypt(
            session, registration.tenant_id, registration.encrypted_auth_value,
            context=f"{registration.tenant_id}:{registration.id}:protocol".encode(),
        ).decode()
        return registration.auth_header_name, value

    def prepare_protocol_execution(
        self, session: Session, auth: AuthContext, *, registration: AgentProtocolRegistration,
        token: str | None, agent_id: str, trace_id: str, operation: str, resource: str,
        execution_request: dict[str, Any], idempotency_key: str,
        authority_receipt: str | None = None,
    ) -> tuple[Execution, bool]:
        auth.require("protocols:invoke")
        controls: list[dict[str, Any]] = []
        capability_id: str | None = None
        decision_id: str | None = None
        if token is not None:
            capability = consume_capability(
                session, self.signing_key, tenant_id=auth.tenant_id, token=token,
                agent_id=agent_id, trace_id=trace_id,
                tool=f"{registration.protocol}:{registration.external_id}",
                operation=operation, resource=resource, execution=execution_request,
            )
            capability_id = capability.id; decision_id = capability.decision_id
            controls.append({
                "type": "capability_binding", "required": True, "status": "applied",
                "parameters": {}, "evidence": {"capability_id": capability.id,
                "registration_id": registration.id, "operation": operation,
                "resource": resource},
            })
        elif authority_receipt is not None:
            controls.append({
                "type": "delegation_authority", "required": True, "status": "applied",
                "parameters": {}, "evidence": {"receipt_hash": hash_object({"receipt": authority_receipt}),
                "registration_id": registration.id, "operation": operation,
                "resource": resource},
            })
        else:
            raise AuthorizationError("protocol execution requires capability or delegation authority")
        return self._prepare_execution_record(
            session, auth, broker_type=registration.protocol, broker_id=registration.id,
            trace_id=trace_id, decision_id=decision_id, capability_id=capability_id,
            idempotency_key=idempotency_key, original_request=execution_request,
            transformed_request=execution_request, controls=controls,
        )

    def _prepare_execution_record(
        self,
        session: Session,
        auth: AuthContext,
        *,
        broker_type: str,
        broker_id: str,
        trace_id: str,
        decision_id: str | None,
        capability_id: str | None,
        idempotency_key: str,
        original_request: dict[str, Any],
        transformed_request: dict[str, Any],
        controls: list[dict[str, Any]],
    ) -> tuple[Execution, bool]:
        request_hash = hash_object(original_request)
        transformed_hash = hash_object(transformed_request)
        inline_dispatch = self.settings.dispatch_mode == "inline"
        now = datetime.now(UTC)
        existing = session.scalar(
            select(Execution).where(
                Execution.tenant_id == auth.tenant_id,
                Execution.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            if (
                existing.request_hash != request_hash
                or existing.transformed_request_hash != transformed_hash
                or existing.broker_type != broker_type
                or existing.broker_id != broker_id
            ):
                raise ConflictError("execution idempotency key was used for another request")
            if existing.state in {"succeeded", "dispatching", "authorized", "outcome_unknown"}:
                return existing, False
            if existing.attempt_count >= existing.max_attempts:
                return existing, False
            existing.state = "dispatching" if inline_dispatch else "authorized"
            existing.updated_at = now
            existing.next_attempt_at = now
            existing.lease_owner = "inline" if inline_dispatch else None
            existing.lease_expires_at = (
                now + timedelta(seconds=self.settings.execution_lease_seconds)
                if inline_dispatch
                else None
            )
            if inline_dispatch:
                existing.attempt_count += 1
            outbox = session.scalar(
                select(OutboxMessage).where(
                    OutboxMessage.tenant_id == auth.tenant_id,
                    OutboxMessage.aggregate_type == "execution",
                    OutboxMessage.aggregate_id == existing.id,
                    OutboxMessage.status.in_(["pending", "retry", "leased"]),
                )
            )
            if outbox is None and not inline_dispatch:
                outbox = OutboxMessage(
                    id=new_id("obx"),
                    tenant_id=auth.tenant_id,
                    aggregate_type="execution",
                    aggregate_id=existing.id,
                    message_type="broker.dispatch",
                    payload={
                        "execution_id": existing.id,
                        "broker_type": broker_type,
                        "broker_id": broker_id,
                        "request_hash": transformed_hash,
                    },
                    status="pending",
                    attempts=existing.attempt_count,
                    max_attempts=existing.max_attempts,
                    priority=existing.priority,
                    created_at=now,
                    available_at=now,
                )
                session.add(outbox)
            if not inline_dispatch and outbox is not None:
                claim = session.get(DispatchClaim, outbox.id)
                if claim is None:
                    session.add(
                        DispatchClaim(
                            outbox_id=outbox.id,
                            tenant_id=auth.tenant_id,
                            priority=outbox.priority,
                            status="pending",
                            attempts=outbox.attempts,
                            max_attempts=outbox.max_attempts,
                            available_at=outbox.available_at,
                            created_at=now,
                        )
                    )
                else:
                    claim.status = "pending"
                    claim.available_at = now
                    claim.lease_owner = None
                    claim.lease_expires_at = None
            append_event(
                session,
                self.signing_key,
                event_id=new_id("evt"),
                tenant_id=auth.tenant_id,
                trace_id=trace_id,
                parent_event_id=None,
                event_type="execution.dispatching" if inline_dispatch else "execution.requeued",
                payload={
                    "execution_id": existing.id,
                    "attempt_count": existing.attempt_count,
                    "dispatch_mode": self.settings.dispatch_mode,
                },
            )
            session.commit()
            return existing, True

        execution_id = new_id("exe")
        execution = Execution(
            id=execution_id,
            tenant_id=auth.tenant_id,
            trace_id=trace_id,
            broker_type=broker_type,
            broker_id=broker_id,
            decision_id=decision_id,
            capability_id=capability_id,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            transformed_request_hash=transformed_hash,
            request_json=transformed_request,
            controls_applied=controls,
            state="dispatching" if inline_dispatch else "authorized",
            attempt_count=1 if inline_dispatch else 0,
            max_attempts=self.settings.worker_max_attempts,
            priority=100,
            lease_owner="inline" if inline_dispatch else None,
            next_attempt_at=now,
            upstream_idempotency_key=f"aifence-{execution_id}",
            reconciliation_status="not_required",
            lease_expires_at=(
                now + timedelta(seconds=self.settings.execution_lease_seconds)
                if inline_dispatch
                else None
            ),
            created_at=now,
            updated_at=now,
        )
        session.add(execution)
        outbox = OutboxMessage(
            id=new_id("obx"),
            tenant_id=auth.tenant_id,
            aggregate_type="execution",
            aggregate_id=execution.id,
            message_type="broker.dispatch",
            payload={
                "execution_id": execution.id,
                "broker_type": broker_type,
                "broker_id": broker_id,
                "request_hash": transformed_hash,
            },
            status="pending",
            attempts=0,
            max_attempts=self.settings.worker_max_attempts,
            priority=execution.priority,
            created_at=now,
            available_at=now,
        )
        session.add(outbox)
        if not inline_dispatch:
            session.add(
                DispatchClaim(
                    outbox_id=outbox.id,
                    tenant_id=auth.tenant_id,
                    priority=outbox.priority,
                    status="pending",
                    attempts=0,
                    max_attempts=outbox.max_attempts,
                    available_at=now,
                    created_at=now,
                )
            )
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=trace_id,
            parent_event_id=None,
            event_type="execution.dispatching" if inline_dispatch else "execution.queued",
            payload={
                "execution_id": execution.id,
                "broker_type": broker_type,
                "broker_id": broker_id,
                "decision_id": decision_id,
                "capability_id": capability_id,
                "request_hash": request_hash,
                "transformed_request_hash": transformed_hash,
                "upstream_idempotency_key": execution.upstream_idempotency_key,
                "controls_applied": controls,
                "dispatch_mode": self.settings.dispatch_mode,
            },
        )
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            concurrent = session.scalar(
                select(Execution).where(
                    Execution.tenant_id == auth.tenant_id,
                    Execution.idempotency_key == idempotency_key,
                )
            )
            if concurrent is not None and concurrent.request_hash == request_hash:
                return concurrent, False
            raise ConflictError("execution could not be prepared atomically") from exc
        return execution, True

    def finalize_execution_success(
        self,
        session: Session,
        auth: AuthContext,
        execution_id: str,
        *,
        status_code: int,
        headers: dict[str, str],
        body: Any,
        response_hash: str,
        expected_fencing_token: int | None = None,
    ) -> Execution:
        execution = self._locked_execution(session, auth.tenant_id, execution_id)
        if expected_fencing_token is not None and execution.fencing_token != expected_fencing_token:
            raise ConflictError("dispatcher fencing token is stale")
        if execution.state == "succeeded":
            return execution
        if execution.state != "dispatching":
            raise ConflictError("execution is not awaiting an upstream result")
        now = datetime.now(UTC)
        previous_state = execution.state
        execution.state = "succeeded"
        execution.response_status_code = status_code
        execution.response_headers = headers
        execution.response_body = body
        execution.response_hash = response_hash
        execution.updated_at = now
        execution.completed_at = now
        execution.reconciliation_status = "not_required"
        execution.lease_owner = None
        execution.lease_expires_at = None
        self._mark_outbox_processed(session, execution.id, now, expected_fencing_token=expected_fencing_token)
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=execution.trace_id,
            parent_event_id=None,
            event_type="execution.succeeded",
            payload={
                "execution_id": execution.id,
                "status_code": status_code,
                "response_hash": response_hash,
                "attempt_count": execution.attempt_count,
            },
        )
        session.commit()
        EXECUTION_TRANSITIONS.labels(previous_state, "succeeded").inc()
        return execution

    def finalize_execution_failure(
        self,
        session: Session,
        auth: AuthContext,
        execution_id: str,
        *,
        error_code: str,
        error_message: str,
        outcome_unknown: bool,
        expected_fencing_token: int | None = None,
    ) -> Execution:
        execution = self._locked_execution(session, auth.tenant_id, execution_id)
        if expected_fencing_token is not None and execution.fencing_token != expected_fencing_token:
            raise ConflictError("dispatcher fencing token is stale")
        if execution.state == "succeeded":
            return execution
        now = datetime.now(UTC)
        previous_state = execution.state
        execution.state = "outcome_unknown" if outcome_unknown else "failed"
        execution.last_error_code = error_code
        execution.last_error_message = error_message[:4096]
        execution.updated_at = now
        execution.completed_at = now if not outcome_unknown else None
        execution.reconciliation_status = "required" if outcome_unknown else "not_required"
        execution.lease_expires_at = None
        execution.lease_owner = None
        self._mark_outbox_processed(session, execution.id, now, expected_fencing_token=expected_fencing_token)
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=execution.trace_id,
            parent_event_id=None,
            event_type="execution.outcome_unknown" if outcome_unknown else "execution.failed",
            payload={
                "execution_id": execution.id,
                "error_code": error_code,
                "attempt_count": execution.attempt_count,
                "reconciliation_status": execution.reconciliation_status,
            },
        )
        session.commit()
        EXECUTION_TRANSITIONS.labels(previous_state, execution.state).inc()
        return execution

    def recover_stale_executions(
        self, session: Session, auth: AuthContext, *, limit: int = 100
    ) -> ExecutionRecoveryResponse:
        auth.require("executions:reconcile")
        now = datetime.now(UTC)
        limit = min(max(limit, 1), self.settings.max_page_size)
        statement = (
            select(Execution)
            .where(
                Execution.tenant_id == auth.tenant_id,
                Execution.state == "dispatching",
                Execution.lease_expires_at.is_not(None),
                Execution.lease_expires_at <= now,
            )
            .order_by(Execution.lease_expires_at.asc())
            .limit(limit)
        )
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update(skip_locked=True)
        rows = list(session.scalars(statement))
        for execution in rows:
            execution.state = "outcome_unknown"
            execution.reconciliation_status = "required"
            execution.last_error_code = "execution_lease_expired"
            execution.last_error_message = "dispatcher lease expired before a durable result was recorded"
            execution.updated_at = now
            execution.lease_expires_at = None
            self._mark_outbox_processed(session, execution.id, now)
            append_event(
                session, self.signing_key, event_id=new_id("evt"),
                tenant_id=auth.tenant_id, trace_id=execution.trace_id,
                parent_event_id=None, event_type="execution.outcome_unknown",
                payload={
                    "execution_id": execution.id,
                    "reason": "dispatcher_lease_expired",
                    "attempt_count": execution.attempt_count,
                },
            )
        session.commit()
        return ExecutionRecoveryResponse(
            recovered=len(rows), execution_ids=[row.id for row in rows]
        )

    def list_executions(
        self,
        session: Session,
        auth: AuthContext,
        *,
        state: str | None = None,
        limit: int = 100,
        after_id: str | None = None,
    ) -> list[ExecutionResponse]:
        auth.require("executions:read")
        statement = select(Execution).where(Execution.tenant_id == auth.tenant_id)
        if state:
            statement = statement.where(Execution.state == state)
        rows = self._created_page(
            session,
            model=Execution,
            tenant_id=auth.tenant_id,
            statement=statement,
            limit=limit,
            after_id=after_id,
        )
        return [self._execution_response(row) for row in rows]

    def get_execution(
        self, session: Session, auth: AuthContext, execution_id: str
    ) -> ExecutionResponse:
        auth.require("executions:read")
        execution = session.scalar(
            select(Execution).where(
                Execution.tenant_id == auth.tenant_id,
                Execution.id == execution_id,
            )
        )
        if execution is None:
            raise NotFoundError("execution does not exist")
        return self._execution_response(execution)

    def reconcile_execution(
        self,
        session: Session,
        auth: AuthContext,
        execution_id: str,
        *,
        state: str,
        reason: str,
        response_status_code: int | None,
        response_headers: dict[str, str] | None,
        response_body: Any,
    ) -> ExecutionResponse:
        auth.require("executions:reconcile")
        execution = self._locked_execution(session, auth.tenant_id, execution_id)
        if execution.state != "outcome_unknown":
            raise ConflictError("only outcome-unknown executions require reconciliation")
        now = datetime.now(UTC)
        execution.state = state
        execution.reconciliation_status = "reconciled"
        execution.last_error_message = reason
        execution.response_status_code = response_status_code
        execution.response_headers = response_headers
        execution.response_body = response_body
        execution.response_hash = hash_object(response_body) if response_body is not None else None
        execution.updated_at = now
        execution.completed_at = now
        execution.lease_expires_at = None
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=auth.tenant_id,
            trace_id=execution.trace_id,
            parent_event_id=None,
            event_type="execution.reconciled",
            payload={
                "execution_id": execution.id,
                "state": state,
                "reason": reason,
                "reconciled_by_key_id": auth.key_id,
            },
        )
        session.commit()
        return self._execution_response(execution)

    @staticmethod
    def _locked_execution(session: Session, tenant_id: str, execution_id: str) -> Execution:
        statement = select(Execution).where(
            Execution.tenant_id == tenant_id,
            Execution.id == execution_id,
        )
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update()
        execution = session.scalar(statement)
        if execution is None:
            raise NotFoundError("execution does not exist")
        return execution

    def _created_page(
        self,
        session: Session,
        *,
        model: type[Any],
        tenant_id: str,
        statement: Any,
        limit: int,
        after_id: str | None,
    ) -> list[Any]:
        page_size = min(max(limit, 1), self.settings.max_page_size)
        if after_id:
            cursor = session.scalar(
                select(model).where(model.tenant_id == tenant_id, model.id == after_id)
            )
            if cursor is None:
                raise NotFoundError("pagination cursor does not exist")
            statement = statement.where(
                or_(
                    model.created_at < cursor.created_at,
                    (model.created_at == cursor.created_at) & (model.id < cursor.id),
                )
            )
        return list(
            session.scalars(
                statement.order_by(model.created_at.desc(), model.id.desc()).limit(page_size)
            )
        )

    @staticmethod
    def _mark_outbox_processed(
        session: Session, execution_id: str, now: datetime, *, expected_fencing_token: int | None = None
    ) -> None:
        messages = list(
            session.scalars(
                select(OutboxMessage).where(
                    OutboxMessage.aggregate_type == "execution",
                    OutboxMessage.aggregate_id == execution_id,
                    OutboxMessage.status.in_(["pending", "retry", "leased"]),
                )
            )
        )
        for message in messages:
            if expected_fencing_token is not None and message.fencing_token != expected_fencing_token:
                raise ConflictError("outbox fencing token is stale")
            message.status = "processed"
            message.lease_owner = None
            message.lease_expires_at = None
            message.last_error = None
            message.processed_at = now
            claim = session.get(DispatchClaim, message.id)
            if claim is not None:
                if expected_fencing_token is not None and claim.fencing_token != expected_fencing_token:
                    raise ConflictError("dispatch claim fencing token is stale")
                claim.status = "processed"
                claim.lease_owner = None
                claim.lease_expires_at = None
                claim.processed_at = now

    def list_api_keys(
        self, session: Session, auth: AuthContext, *, limit: int = 100,
        after_id: str | None = None,
    ) -> list[APIKeySummary]:
        auth.require("keys:read")
        rows = self._created_page(
            session, model=APIKey, tenant_id=auth.tenant_id,
            statement=select(APIKey).where(APIKey.tenant_id == auth.tenant_id),
            limit=limit, after_id=after_id,
        )
        return [self._api_key_summary(row) for row in rows]

    def revoke_api_key(
        self, session: Session, auth: AuthContext, key_id: str, reason: str
    ) -> APIKeySummary:
        auth.require("keys:write")
        key = session.scalar(select(APIKey).where(
            APIKey.tenant_id == auth.tenant_id, APIKey.id == key_id
        ))
        if not key:
            raise NotFoundError("API key does not exist")
        if key.status != "revoked":
            key.status = "revoked"
            append_event(
                session, self.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                trace_id=new_id("trc"), parent_event_id=None, event_type="api_key.revoked",
                payload={
                    "key_id": key.id, "name": key.name, "reason": reason,
                    "revoked_by_key_id": auth.key_id,
                },
            )
            session.commit()
        return self._api_key_summary(key)

    def revoke_agent(
        self, session: Session, auth: AuthContext, agent_id: str, reason: str
    ) -> AgentResponse:
        auth.require("agents:write")
        agent = session.scalar(select(Agent).where(
            Agent.tenant_id == auth.tenant_id, Agent.id == agent_id
        ))
        if not agent:
            raise NotFoundError("agent does not exist")
        if agent.status != "revoked":
            agent.status = "revoked"
            agent.updated_at = datetime.now(UTC)
            session.execute(update(Capability).where(
                Capability.tenant_id == auth.tenant_id,
                Capability.agent_id == agent.id,
                Capability.status == "active",
            ).values(status="revoked"))
            append_event(
                session, self.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
                trace_id=new_id("trc"), parent_event_id=None, event_type="agent.revoked",
                payload={
                    "agent_id": agent.id, "external_id": agent.external_id, "reason": reason,
                    "revoked_by_key_id": auth.key_id,
                },
            )
            session.commit()
        return self._agent_response(agent)

    def get_decision(
        self, session: Session, auth: AuthContext, decision_id: str
    ) -> DecisionResponse:
        auth.require("decisions:read")
        decision = session.scalar(select(Decision).where(
            Decision.tenant_id == auth.tenant_id, Decision.id == decision_id
        ))
        if not decision:
            raise NotFoundError("decision does not exist")
        return self._decision_response(decision)

    def list_policies(
        self, session: Session, auth: AuthContext, *, limit: int = 100,
        after_id: str | None = None,
    ) -> list[PolicyBundleResponse]:
        auth.require("policies:read")
        rows = self._created_page(
            session, model=PolicyBundle, tenant_id=auth.tenant_id,
            statement=select(PolicyBundle).where(PolicyBundle.tenant_id == auth.tenant_id),
            limit=limit, after_id=after_id,
        )
        return [self._policy_response(row) for row in rows]

    def list_approvals(
        self, session: Session, auth: AuthContext, status: str | None = None,
        *, limit: int = 100, after_id: str | None = None,
    ) -> list[ApprovalResponse]:
        auth.require("approvals:read")
        statement = select(Approval).where(Approval.tenant_id == auth.tenant_id)
        if status:
            statement = statement.where(Approval.status == status)
        rows = self._created_page(
            session, model=Approval, tenant_id=auth.tenant_id, statement=statement,
            limit=limit, after_id=after_id,
        )
        return [self._approval_response(session, row) for row in rows]

    def revoke_capability(
        self, session: Session, auth: AuthContext, capability_id: str, reason: str
    ) -> CapabilityVerification:
        auth.require("capabilities:revoke")
        capability = session.scalar(select(Capability).where(
            Capability.tenant_id == auth.tenant_id, Capability.id == capability_id
        ))
        if not capability:
            raise NotFoundError("capability does not exist")
        capability.status = "revoked"
        append_event(
            session, self.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
            trace_id=capability.trace_id, parent_event_id=None, event_type="capability.revoked",
            payload={
                "capability_id": capability.id, "reason": reason,
                "revoked_by_key_id": auth.key_id,
            },
        )
        session.commit()
        CAPABILITY_EVENTS.labels("revoked").inc()
        return CapabilityVerification(
            valid=False, capability_id=capability.id, remaining_uses=0,
            constraints=capability.constraints
        )

    def get_artifact_metadata(
        self, session: Session, auth: AuthContext, artifact_id: str
    ) -> ArtifactResponse:
        auth.require("artifacts:read")
        artifact = session.scalar(select(Artifact).where(
            Artifact.tenant_id == auth.tenant_id, Artifact.id == artifact_id
        ))
        if not artifact:
            raise NotFoundError("artifact does not exist")
        return self._artifact_response(artifact)

    def list_incidents(
        self, session: Session, auth: AuthContext, status: str | None = None,
        *, limit: int = 100, after_id: str | None = None,
    ) -> list[IncidentResponse]:
        auth.require("incidents:read")
        statement = select(Incident).where(Incident.tenant_id == auth.tenant_id)
        if status:
            statement = statement.where(Incident.status == status)
        rows = self._created_page(
            session, model=Incident, tenant_id=auth.tenant_id, statement=statement,
            limit=limit, after_id=after_id,
        )
        return [self._incident_response(row) for row in rows]

    def update_incident_status(
        self, session: Session, auth: AuthContext, incident_id: str,
        body: IncidentStatusUpdate,
    ) -> IncidentResponse:
        auth.require("incidents:write")
        incident = session.scalar(select(Incident).where(
            Incident.tenant_id == auth.tenant_id, Incident.id == incident_id
        ))
        if not incident:
            raise NotFoundError("incident does not exist")
        previous = incident.status
        incident.status = body.status
        incident.updated_at = datetime.now(UTC)
        append_event(
            session, self.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
            trace_id=incident.trace_id, parent_event_id=None, event_type="incident.status_changed",
            payload={
                "incident_id": incident.id, "previous_status": previous,
                "status": incident.status, "reason": body.reason,
                "changed_by_key_id": auth.key_id,
            },
        )
        session.commit()
        return self._incident_response(incident)

    def list_providers(
        self, session: Session, auth: AuthContext, *, limit: int = 100,
        after_id: str | None = None,
    ) -> list[ProviderResponse]:
        auth.require("providers:read")
        rows = self._created_page(
            session, model=Provider, tenant_id=auth.tenant_id,
            statement=select(Provider).where(Provider.tenant_id == auth.tenant_id),
            limit=limit, after_id=after_id,
        )
        return [self._provider_response(row) for row in rows]

    def revoke_provider(
        self, session: Session, auth: AuthContext, provider_id: str, reason: str
    ) -> ProviderResponse:
        auth.require("providers:write")
        provider = session.scalar(select(Provider).where(
            Provider.tenant_id == auth.tenant_id, Provider.id == provider_id
        ))
        if not provider:
            raise NotFoundError("provider does not exist")
        provider.status = "revoked"
        append_event(
            session, self.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
            trace_id=new_id("trc"), parent_event_id=None, event_type="provider.revoked",
            payload={
                "provider_id": provider.id, "reason": reason,
                "revoked_by_key_id": auth.key_id,
            },
        )
        session.commit()
        return self._provider_response(provider)

    def list_tools(
        self, session: Session, auth: AuthContext, *, limit: int = 100,
        after_id: str | None = None,
    ) -> list[ToolResponse]:
        auth.require("tools:read")
        rows = self._created_page(
            session, model=Tool, tenant_id=auth.tenant_id,
            statement=select(Tool).where(Tool.tenant_id == auth.tenant_id),
            limit=limit, after_id=after_id,
        )
        return [self._tool_response(row) for row in rows]

    def revoke_tool(
        self, session: Session, auth: AuthContext, tool_id: str, reason: str
    ) -> ToolResponse:
        auth.require("tools:write")
        tool = session.scalar(select(Tool).where(
            Tool.tenant_id == auth.tenant_id, Tool.id == tool_id
        ))
        if not tool:
            raise NotFoundError("tool does not exist")
        tool.status = "revoked"
        session.execute(update(Capability).where(
            Capability.tenant_id == auth.tenant_id,
            Capability.tool == tool.name,
            Capability.status == "active",
        ).values(status="revoked"))
        append_event(
            session, self.signing_key, event_id=new_id("evt"), tenant_id=auth.tenant_id,
            trace_id=new_id("trc"), parent_event_id=None, event_type="tool.revoked",
            payload={
                "tool_id": tool.id, "reason": reason,
                "revoked_by_key_id": auth.key_id,
            },
        )
        session.commit()
        return self._tool_response(tool)

    def reencrypt_stored_secrets(
        self, session: Session, *, tenant_id: str | None = None, batch_size: int = 500
    ) -> dict[str, int]:
        if batch_size < 1 or batch_size > 5000:
            raise ValueError("batch_size must be between 1 and 5000")
        is_postgresql = bool(session.bind and session.bind.dialect.name == "postgresql")
        if is_postgresql and tenant_id is None:
            raise ValueError("tenant_id is required for PostgreSQL re-encryption under forced RLS")
        if tenant_id is not None:
            set_tenant_context(session, tenant_id)
        counts = {"memory": 0, "artifacts": 0, "providers": 0, "tools": 0, "protocols": 0}
        tenant_counts: dict[str, int] = {}
        tenant_category_counts: dict[str, dict[str, int]] = {}
        specifications = (
            (MemoryRecord, "encrypted_content", "memory",
             lambda row: f"memory:{row.tenant_id}:{row.id}".encode()),
            (Artifact, "encrypted_blob", "artifacts",
             lambda row: f"{row.tenant_id}:{row.id}:{row.sha256}".encode()),
            (Provider, "encrypted_auth_value", "providers",
             lambda row: f"{row.tenant_id}:{row.id}:provider".encode()),
            (Tool, "encrypted_auth_value", "tools",
             lambda row: f"{row.tenant_id}:{row.id}:tool".encode()),
            (AgentProtocolRegistration, "encrypted_auth_value", "protocols",
             lambda row: f"{row.tenant_id}:{row.id}:protocol".encode()),
        )
        for model, field_name, label, context_factory in specifications:
            last_id = ""
            while True:
                statement = select(model).where(model.id > last_id)
                if tenant_id is not None:
                    statement = statement.where(model.tenant_id == tenant_id)
                rows = list(session.scalars(statement.order_by(model.id.asc()).limit(batch_size)))
                if not rows:
                    break
                for row in rows:
                    last_id = row.id
                    if isinstance(row, Artifact) and row.storage_key:
                        encrypted = self.artifact_store.get(row.storage_key)
                    else:
                        encrypted = getattr(row, field_name)
                    if encrypted is None:
                        continue
                    route = session.get(TenantKeyRoute, row.tenant_id)
                    tenant_envelope = self.tenant_crypto.is_tenant_envelope(encrypted)
                    if tenant_envelope:
                        if route is None or self.tenant_crypto.envelope_key_id(encrypted) == route.key_id:
                            continue
                        plaintext = self.tenant_crypto.decrypt(
                            session, row.tenant_id, encrypted, context=context_factory(row)
                        )
                    else:
                        plaintext = self.cipher.decrypt(encrypted, context=context_factory(row))
                    context = context_factory(row)
                    rotated = self.tenant_crypto.encrypt(
                        session, row.tenant_id, plaintext, context=context
                    )
                    if isinstance(row, Artifact) and row.storage_key:
                        migration_object_id = (
                            f"{row.id}_tk_{hashlib.sha256(rotated).hexdigest()[:12]}"
                        )
                        row.storage_key = self.artifact_store.put(
                            row.tenant_id, migration_object_id, rotated
                        )
                    else:
                        setattr(row, field_name, rotated)
                    counts[label] += 1
                    tenant_counts[row.tenant_id] = tenant_counts.get(row.tenant_id, 0) + 1
                    category_counts = tenant_category_counts.setdefault(
                        row.tenant_id,
                        {"memory": 0, "artifacts": 0, "providers": 0, "tools": 0, "protocols": 0},
                    )
                    category_counts[label] += 1
                session.commit()
        for affected_tenant_id, count in tenant_counts.items():
            set_tenant_context(session, affected_tenant_id)
            route = session.get(TenantKeyRoute, affected_tenant_id)
            append_event(
                session, self.signing_key, event_id=new_id("evt"),
                tenant_id=affected_tenant_id, trace_id=new_id("trc"), parent_event_id=None,
                event_type="encryption.reencrypted",
                payload={
                    "active_key_id": route.key_id if route else "tenant-scoped",
                    "records_reencrypted": count,
                    "category_counts": tenant_category_counts[affected_tenant_id],
                },
            )
        session.commit()
        return counts

    def tenant_key_inventory(
        self, session: Session, *, tenant_id: str, batch_size: int = 500
    ) -> dict[str, int]:
        if batch_size < 1 or batch_size > 5000:
            raise ValueError("batch_size must be between 1 and 5000")
        set_tenant_context(session, tenant_id)
        inventory: dict[str, int] = {}
        specifications = (
            (MemoryRecord, "encrypted_content"),
            (Artifact, "encrypted_blob"),
            (Provider, "encrypted_auth_value"),
            (Tool, "encrypted_auth_value"),
            (AgentProtocolRegistration, "encrypted_auth_value"),
        )
        for model, field_name in specifications:
            last_id = ""
            while True:
                rows = list(session.scalars(
                    select(model).where(model.tenant_id == tenant_id, model.id > last_id)
                    .order_by(model.id.asc()).limit(batch_size)
                ))
                if not rows:
                    break
                for row in rows:
                    last_id = row.id
                    if isinstance(row, Artifact) and row.storage_key:
                        encrypted = self.artifact_store.get(row.storage_key)
                    else:
                        encrypted = getattr(row, field_name)
                    if not encrypted:
                        continue
                    key_id = self.tenant_crypto.envelope_key_id(encrypted)
                    if key_id is not None:
                        inventory[key_id] = inventory.get(key_id, 0) + 1
        return inventory

    def rotate_tenant_key(
        self, session: Session, *, tenant_id: str, new_key_id: str, batch_size: int = 500
    ) -> dict[str, Any]:
        set_tenant_context(session, tenant_id)
        route = self.tenant_crypto.rotate_route(session, tenant_id, new_key_id=new_key_id)
        append_event(
            session, self.signing_key, event_id=new_id("evt"), tenant_id=tenant_id,
            trace_id=new_id("trc"), parent_event_id=None, event_type="tenant.key_route_rotated",
            payload={
                "active_key_id": route.key_id, "route_version": route.version,
                "historical_key_ids": list(route.historical_key_ids),
            },
        )
        session.commit()
        counts = self.reencrypt_stored_secrets(
            session, tenant_id=tenant_id, batch_size=batch_size
        )
        return {
            "tenant_id": tenant_id, "active_key_id": route.key_id,
            "route_version": route.version, "historical_key_ids": list(route.historical_key_ids),
            "reencrypted": counts, "inventory": self.tenant_key_inventory(
                session, tenant_id=tenant_id, batch_size=batch_size
            ),
        }

    def retire_tenant_key(
        self, session: Session, *, tenant_id: str, key_id: str, batch_size: int = 500
    ) -> dict[str, Any]:
        set_tenant_context(session, tenant_id)
        inventory = self.tenant_key_inventory(
            session, tenant_id=tenant_id, batch_size=batch_size
        )
        references = inventory.get(key_id, 0)
        if references:
            raise ConflictError(
                "tenant key still has encrypted-record references",
                details={"key_id": key_id, "references": references},
            )
        route = self.tenant_crypto.retire_historical_key(session, tenant_id, key_id=key_id)
        append_event(
            session, self.signing_key, event_id=new_id("evt"), tenant_id=tenant_id,
            trace_id=new_id("trc"), parent_event_id=None, event_type="tenant.key_route_retired",
            payload={"retired_key_id": key_id, "active_key_id": route.key_id},
        )
        session.commit()
        return {
            "tenant_id": tenant_id, "active_key_id": route.key_id,
            "retired_key_id": key_id, "historical_key_ids": list(route.historical_key_ids),
            "inventory": inventory,
        }

    def prune_expired_artifacts(
        self, session: Session, *, tenant_id: str | None = None, batch_size: int = 500
    ) -> dict[str, int]:
        if batch_size < 1 or batch_size > 5000:
            raise ValueError("batch_size must be between 1 and 5000")
        now = datetime.now(UTC)
        tenant_counts: dict[str, int] = {}
        total = 0
        while True:
            statement = select(Artifact).where(Artifact.expires_at <= now)
            if tenant_id is not None:
                statement = statement.where(Artifact.tenant_id == tenant_id)
            rows = list(session.scalars(
                statement.order_by(Artifact.id.asc()).limit(batch_size)
            ))
            if not rows:
                break
            for row in rows:
                tenant_counts[row.tenant_id] = tenant_counts.get(row.tenant_id, 0) + 1
                total += 1
                if row.storage_key:
                    self.artifact_store.delete(row.storage_key)
                session.delete(row)
            session.commit()
        for tenant_id, count in tenant_counts.items():
            append_event(
                session, self.signing_key, event_id=new_id("evt"), tenant_id=tenant_id,
                trace_id=new_id("trc"), parent_event_id=None, event_type="artifact.retention_pruned",
                payload={"deleted_artifacts": count, "cutoff": now.isoformat()},
            )
        session.commit()
        return {"artifacts_deleted": total, "tenants_affected": len(tenant_counts)}

    def _validate_approval(
        self, session: Session, tenant_id: str, approval_id: str, request_hash: str
    ) -> Approval:
        stmt = select(Approval).where(
            Approval.tenant_id == tenant_id,
            Approval.id == approval_id,
        )
        if session.bind and session.bind.dialect.name == "postgresql":
            stmt = stmt.with_for_update()
        approval = session.scalar(stmt)
        if not approval:
            raise AuthorizationError("approval does not exist")
        expires = approval.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        if (
            approval.status != "approved"
            or approval.approval_count < approval.required_approvals
            or expires <= datetime.now(UTC)
        ):
            raise AuthorizationError("approval quorum is not active")
        if approval.request_hash != request_hash:
            raise AuthorizationError("approval is not bound to this exact action")
        approval.status = "consumed"
        voters = list(
            session.scalars(
                select(ApprovalVote).where(
                    ApprovalVote.tenant_id == tenant_id,
                    ApprovalVote.approval_id == approval.id,
                    ApprovalVote.decision == "approved",
                )
            )
        )
        append_event(
            session,
            self.signing_key,
            event_id=new_id("evt"),
            tenant_id=tenant_id,
            trace_id=approval.trace_id,
            parent_event_id=None,
            event_type="approval.consumed",
            payload={
                "approval_id": approval.id,
                "decision_id": approval.decision_id,
                "request_hash": request_hash,
                "approved_by_key_ids": sorted(vote.key_id for vote in voters),
                "required_approvals": approval.required_approvals,
            },
        )
        return approval

    def _safe_join(self, base_url: str, path: str, allowed_patterns: list[str]) -> str:
        return safe_join(base_url, path, allowed_patterns)

    @staticmethod
    def _validate_external_url(url: str, allowed_hosts: tuple[str, ...]) -> None:
        host = __import__("urllib.parse", fromlist=["urlsplit"]).urlsplit(url).hostname or ""
        zone = "private" if host in {"localhost", "127.0.0.1", "::1"} else "public"
        validate_endpoint(
            url,
            allowed_hosts=allowed_hosts,
            network_zone=zone,
            require_resolution=False,
        )

    @staticmethod
    def _validate_tool_operations(operations: dict[str, Any]) -> None:
        if not operations or len(operations) > 256:
            raise ConflictError("tool must define between 1 and 256 operations")
        for name, rule in operations.items():
            if not isinstance(name, str) or not name or not isinstance(rule, dict):
                raise ConflictError("tool operation definitions are invalid")
            if str(rule.get("method", "")).upper() not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                raise ConflictError(f"tool operation {name} has an invalid method")
            paths = rule.get("paths")
            if not isinstance(paths, list) or not paths or len(paths) > 128:
                raise ConflictError(f"tool operation {name} must define allowed paths")
            if not all(
                isinstance(path, str)
                and path.startswith("/")
                and "\\" not in path
                and "\x00" not in path
                and ".." not in path.split("/")
                for path in paths
            ):
                raise ConflictError(
                    f"tool operation {name} contains an unsafe allowed path"
                )

    @staticmethod
    def _policy_response(bundle: PolicyBundle) -> PolicyBundleResponse:
        return PolicyBundleResponse(
            id=bundle.id,
            version=bundle.version,
            document_hash=bundle.document_hash,
            active=bundle.active,
            created_by_key_id=bundle.created_by_key_id,
            created_at=bundle.created_at,
            activated_at=bundle.activated_at,
            activated_by_key_id=bundle.activated_by_key_id,
            activation_reason=bundle.activation_reason,
            rollout_mode=bundle.rollout_mode,
            canary_percentage=bundle.canary_percentage,
            validation_report=bundle.validation_report,
            supersedes_policy_id=bundle.supersedes_policy_id,
        )

    @staticmethod
    def _api_key_summary(key: APIKey) -> APIKeySummary:
        return APIKeySummary(
            id=key.id,
            name=key.name,
            scopes=key.scopes,
            status=key.status,
            expires_at=key.expires_at,
            last_used_at=key.last_used_at,
            bound_agent_id=key.bound_agent_id,
            bound_workload_identity=key.bound_workload_identity,
            bound_instance_id=key.bound_instance_id,
            bound_principal_type=key.bound_principal_type,
            bound_principal_id=key.bound_principal_id,
            created_at=key.created_at,
        )

    @staticmethod
    def _agent_response(agent: Agent) -> AgentResponse:
        return AgentResponse(
            id=agent.id,
            external_id=agent.external_id,
            name=agent.name,
            version=agent.version,
            workload_identity=agent.workload_identity,
            model=agent.model,
            instruction_hash=agent.instruction_hash,
            deployment_digest=agent.deployment_digest,
            manifest_hash=agent.manifest_hash,
            allowed_tools=agent.allowed_tools,
            allowed_data_classes=agent.allowed_data_classes,
            metadata=agent.metadata_json,
            status=agent.status,
            created_at=agent.created_at,
        )

    @staticmethod
    def _event_response(event: Event) -> EventResponse:
        return EventResponse(
            id=event.id,
            trace_id=event.trace_id,
            sequence=event.sequence,
            event_type=event.event_type,
            payload=event.payload,
            previous_hash=event.previous_hash,
            event_hash=event.event_hash,
            signature=event.signature,
            key_id=event.key_id,
            created_at=event.created_at,
        )

    @staticmethod
    def _approval_response(session: Session, approval: Approval) -> ApprovalResponse:
        votes = list(
            session.scalars(
                select(ApprovalVote).where(
                    ApprovalVote.tenant_id == approval.tenant_id,
                    ApprovalVote.approval_id == approval.id,
                ).order_by(ApprovalVote.created_at.asc())
            )
        )
        return ApprovalResponse(
            id=approval.id,
            trace_id=approval.trace_id,
            decision_id=approval.decision_id,
            status=approval.status,
            request_hash=approval.request_hash,
            required_approvals=approval.required_approvals,
            approval_count=approval.approval_count,
            votes=[
                ApprovalVoteResponse(
                    key_id=vote.key_id,
                    decision=vote.decision,  # type: ignore[arg-type]
                    reason=vote.reason,
                    created_at=vote.created_at,
                )
                for vote in votes
            ],
            decision_reason=approval.decision_reason,
            created_at=approval.created_at,
            decided_at=approval.decided_at,
            expires_at=approval.expires_at,
        )

    @staticmethod
    def _decision_response(decision: Decision) -> DecisionResponse:
        created = decision.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        return DecisionResponse(
            decision_id=decision.id,
            trace_id=decision.trace_id,
            outcome=decision.outcome,  # type: ignore[arg-type]
            risk_score=decision.risk_score,
            reasons=decision.reasons,
            constraints=decision.constraints,
            enforcement_plan=decision.enforcement_plan,
            findings=[Finding.model_validate(x) for x in decision.findings],
            policy_version=decision.policy_version,
            approval_id=decision.approval_id,
            receipt=decision.receipt,
            expires_at=decision.expires_at,
        )

    @staticmethod
    def _execution_response(execution: Execution) -> ExecutionResponse:
        return ExecutionResponse(
            id=execution.id,
            trace_id=execution.trace_id,
            broker_type=execution.broker_type,
            broker_id=execution.broker_id,
            decision_id=execution.decision_id,
            capability_id=execution.capability_id,
            idempotency_key=execution.idempotency_key,
            request_hash=execution.request_hash,
            transformed_request_hash=execution.transformed_request_hash,
            controls_applied=execution.controls_applied,
            state=execution.state,
            attempt_count=execution.attempt_count,
            upstream_idempotency_key=execution.upstream_idempotency_key,
            response_status_code=execution.response_status_code,
            response_headers=execution.response_headers,
            response_body=execution.response_body,
            response_hash=execution.response_hash,
            last_error_code=execution.last_error_code,
            reconciliation_status=execution.reconciliation_status,
            lease_expires_at=execution.lease_expires_at,
            created_at=execution.created_at,
            updated_at=execution.updated_at,
            completed_at=execution.completed_at,
        )

    @staticmethod
    def _artifact_response(artifact: Artifact) -> ArtifactResponse:
        return ArtifactResponse(
            id=artifact.id,
            trace_id=artifact.trace_id,
            filename=artifact.filename,
            media_type=artifact.media_type,
            size_bytes=artifact.size_bytes,
            sha256=artifact.sha256,
            scan_status=artifact.scan_status,
            scan_result=artifact.scan_result,
            quarantined=artifact.quarantined,
            created_at=artifact.created_at,
            expires_at=artifact.expires_at,
        )

    @staticmethod
    def _incident_response(incident: Incident) -> IncidentResponse:
        return IncidentResponse(
            id=incident.id,
            trace_id=incident.trace_id,
            severity=incident.severity,  # type: ignore[arg-type]
            category=incident.category,
            title=incident.title,
            description=incident.description,
            evidence=incident.evidence,
            status=incident.status,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
        )

    @staticmethod
    def _provider_response(provider: Provider) -> ProviderResponse:
        return ProviderResponse(
            id=provider.id,
            name=provider.name,
            base_url=provider.base_url,
            allowed_paths=provider.allowed_paths,
            network_zone=provider.network_zone,
            resolved_addresses=provider.resolved_addresses,
            status=provider.status,
            created_at=provider.created_at,
        )

    @staticmethod
    def _tool_response(tool: Tool) -> ToolResponse:
        return ToolResponse(
            id=tool.id,
            name=tool.name,
            base_url=tool.base_url,
            allowed_operations=tool.allowed_operations,
            network_zone=tool.network_zone,
            resolved_addresses=tool.resolved_addresses,
            status=tool.status,
            created_at=tool.created_at,
        )
