# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import asyncio
import base64
import hashlib
import ipaddress
import json
import secrets
from collections.abc import Generator
from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .auth import AuthContext, authenticate
from .db import set_tenant_context
from .errors import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DependencyUnavailableError,
    NotFoundError,
)
from .metrics import BROKER_CALLS, DECISIONS, metrics_response
from .models import AgentProtocolRegistration, Execution, SigningPublicKey, Tenant
from .network import ValidatedEndpoint, pin_validated_target
from .schemas import (
    A2ATaskRequest,
    AgentRegistration,
    AgentResponse,
    APIKeyCreate,
    APIKeyCreated,
    APIKeySummary,
    ApprovalDecisionIn,
    ApprovalResponse,
    ArtifactResponse,
    AuditAnchorBatchRequest,
    AuditAnchorQuorumResponse,
    AuditAnchorRequest,
    AuditAnchorResponse,
    AuditCheckpointResponse,
    AuditVerificationResponse,
    BrokerResponse,
    BudgetReservationRequest,
    BudgetReservationResponse,
    BudgetSettlementRequest,
    CapabilityConsumeRequest,
    CapabilityIssueRequest,
    CapabilityResponse,
    CapabilityVerification,
    DecisionRequest,
    DecisionResponse,
    DelegationGrantCreate,
    DelegationGrantResponse,
    DispatchRunResponse,
    EventIngest,
    EventResponse,
    ExecutionReconcileRequest,
    ExecutionRecoveryResponse,
    ExecutionResponse,
    IncidentCreate,
    IncidentResponse,
    IncidentStatusUpdate,
    LegalHoldCreate,
    LegalHoldResponse,
    MCPToolCallRequest,
    MemoryRecordResponse,
    MemoryStatusUpdate,
    MemoryWriteRequest,
    OperatorPostureResponse,
    PolicyBundleIn,
    PolicyBundleResponse,
    PolicyCanaryRequest,
    PolicyDiffRequest,
    PolicyDiffResponse,
    PolicySimulationRequest,
    PolicySimulationResponse,
    PolicyValidationRequest,
    PolicyValidationResponse,
    ProtocolManifestVersionResponse,
    ProtocolRegistrationCreate,
    ProtocolRegistrationResponse,
    ProviderInvokeRequest,
    ProviderRegistration,
    ProviderResponse,
    RuntimeBudgetCreate,
    RuntimeBudgetResponse,
    StatusUpdate,
    TenantLifecycleJobResponse,
    TenantLifecycleReconcileRequest,
    TenantLifecycleRequest,
    ToolExecuteRequest,
    ToolRegistration,
    ToolResponse,
    WorkloadIdentityBindingCreate,
    WorkloadIdentityBindingResponse,
)
from .workload_identity import (
    authenticate_workload,
    extract_workload_assertion,
    request_from_trusted_proxy,
)

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False, scheme_name="AgentDanceBearer")


def get_session(request: Request) -> Generator[Session, None, None]:
    session = request.app.state.session_factory()
    session.info["service"] = request.app.state.service
    session.info["audit_checkpoint_interval"] = request.app.state.settings.audit_checkpoint_interval
    try:
        yield session
    finally:
        session.close()


def get_auth(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthContext:
    settings = request.app.state.settings
    if credentials is not None and credentials.scheme.lower() == "bearer":
        token = credentials.credentials.strip()
        auth = authenticate(session, token, settings.accepted_peppers())
    elif settings.workload_auth_enabled:
        assertion = extract_workload_assertion(request, settings)
        if assertion is None:
            raise AuthenticationError("a Bearer API key or trusted SPIFFE workload identity is required")
        auth = authenticate_workload(session, assertion, settings)
        set_tenant_context(session, auth.tenant_id)
    else:
        raise AuthenticationError("a Bearer AGENTDANCE API key is required")
    request.app.state.rate_limiter.enforce_authenticated(
        tenant_id=auth.tenant_id,
        key_id=auth.key_id,
        path=request.url.path,
    )
    return auth


SessionDep = Annotated[Session, Depends(get_session)]
AuthDep = Annotated[AuthContext, Depends(get_auth)]


def _request_from_cidrs(request: Request, cidrs: tuple[str, ...]) -> bool:
    host = request.client.host if request.client is not None else ""
    if host == "testclient" and request.app.state.settings.environment == "test":
        host = "127.0.0.1"
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return any(address in ipaddress.ip_network(cidr, strict=False) for cidr in cidrs)


def require_internal(request: Request) -> None:
    settings = request.app.state.settings
    if not settings.internal_cidrs or not _request_from_cidrs(request, settings.internal_cidrs):
        raise NotFoundError("resource not found")


def get_operator_proxy_auth(request: Request, session: SessionDep) -> AuthContext:
    settings = request.app.state.settings
    if not settings.operator_console_enabled:
        raise NotFoundError("operator console is disabled")
    if not request_from_trusted_proxy(request, settings):
        raise AuthenticationError("operator identity must come from a trusted authentication proxy")
    tenant_id = request.headers.get(settings.operator_tenant_header, "").strip()
    identity = request.headers.get(settings.operator_identity_header, "").strip()
    groups = {
        value.strip()
        for value in request.headers.get(settings.operator_groups_header, "").replace(";", ",").split(",")
        if value.strip()
    }
    if not tenant_id or not identity:
        raise AuthenticationError("operator proxy omitted tenant or identity")
    if not groups.intersection(settings.operator_allowed_groups):
        raise AuthorizationError("operator is not in an authorized group")
    set_tenant_context(session, tenant_id)
    tenant = session.get(Tenant, tenant_id)
    if tenant is None or tenant.status != "active":
        raise AuthenticationError("operator tenant is inactive or unknown")
    return AuthContext(
        tenant_id=tenant_id,
        key_id=f"operator:{identity}",
        scopes=frozenset({"*"}),
        bound_principal_type="human",
        bound_principal_id=identity,
    )


OperatorAuthDep = Annotated[AuthContext, Depends(get_operator_proxy_auth)]


@router.get("/health/live", tags=["health"])
def live() -> dict[str, str]:
    return {"status": "live"}


@router.get("/health/ready", tags=["health"])
def ready(session: SessionDep) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "ready"}


@router.get("/internal/health/ready", include_in_schema=False)
def deep_ready(request: Request, session: SessionDep) -> dict[str, Any]:
    require_internal(request)
    session.execute(text("SELECT 1"))
    dependencies: dict[str, str] = {
        "database": "ready",
        "signing": "ready",
        "kms": "configured" if request.app.state.settings.kms_backend != "local" else "local",
        "artifact_store": request.app.state.settings.artifact_store_backend,
        "audit_anchor": request.app.state.settings.audit_anchor_backend,
        "dispatch": request.app.state.settings.dispatch_mode,
    }
    if request.app.state.settings.clamav_required:
        if not request.app.state.service.clamav.ping():
            raise ConflictError("required malware scanner is not ready")
        dependencies["clamav"] = "ready"
    else:
        dependencies["clamav"] = "optional"
    return {"status": "ready", "dependencies": dependencies}


@router.get("/internal/metrics", include_in_schema=False)
def metrics(request: Request) -> Response:
    require_internal(request)
    return metrics_response()


@router.get("/source", tags=["legal"], summary="Source and licensing information")
def source_information(request: Request) -> dict[str, Any]:
    settings = request.app.state.settings
    return {
        "service": "AGENTDANCE",
        "version": request.app.state.version,
        "server_license": "AGPL-3.0-only OR commercial",
        "sdk_license": "Apache-2.0",
        "source_code_url": settings.source_code_url,
        "commercial_license_url": settings.commercial_license_url,
        "licensing_document": f"{settings.source_code_url.rstrip('/')}/blob/main/LICENSING.md",
    }


@router.get("/.well-known/agentdance.json", include_in_schema=False)
def well_known(request: Request) -> dict[str, Any]:
    return {
        "service": "AGENTDANCE",
        "version": request.app.state.version,
        "server_license": "AGPL-3.0-only OR commercial",
        "sdk_license": "Apache-2.0",
        "source_code_url": request.app.state.settings.source_code_url,
        "commercial_license_url": request.app.state.settings.commercial_license_url,
        "decision_endpoint": f"{request.app.state.settings.public_base_url}/v1/decisions",
        "signing_key_id": request.app.state.signing_key.key_id,
        "signing_public_key_pem": request.app.state.signing_key.public_pem(),
        "event_spec": "agentdance.event.v1",
        "policy_spec": "agentdance.policy.v1",
    }


@router.get("/.well-known/agentdance-signing-keys.json", include_in_schema=False)
def signing_keys(session: SessionDep) -> dict[str, Any]:
    keys = list(session.scalars(select(SigningPublicKey).order_by(SigningPublicKey.created_at.asc())))
    return {
        "keys": [
            {
                "key_id": key.key_id,
                "algorithm": key.algorithm,
                "public_key_pem": key.public_pem,
                "active": key.active,
                "created_at": key.created_at.isoformat(),
                "retired_at": key.retired_at.isoformat() if key.retired_at else None,
            }
            for key in keys
        ]
    }


@router.post("/v1/api-keys", response_model=APIKeyCreated, tags=["identity"], status_code=201)
def create_api_key(body: APIKeyCreate, session: SessionDep, auth: AuthDep) -> APIKeyCreated:
    key, token = session.info["service"].create_api_key(
        session,
        auth,
        name=body.name,
        scopes=body.scopes,
        expires_at=body.expires_at,
        bound_agent_id=body.bound_agent_id,
        bound_workload_identity=body.bound_workload_identity,
        bound_instance_id=body.bound_instance_id,
        bound_principal_type=body.bound_principal_type,
        bound_principal_id=body.bound_principal_id,
    )
    summary = session.info["service"]._api_key_summary(key)
    return APIKeyCreated(**summary.model_dump(), api_key=token)


@router.get("/v1/api-keys", response_model=list[APIKeySummary], tags=["identity"])
def list_api_keys(
    session: SessionDep, auth: AuthDep, limit: int = Query(100, ge=1, le=5000), after_id: str | None = None
) -> list[APIKeySummary]:
    return session.info["service"].list_api_keys(session, auth, limit=limit, after_id=after_id)


@router.post("/v1/api-keys/{key_id}/revoke", response_model=APIKeySummary, tags=["identity"])
def revoke_api_key(
    key_id: str, body: StatusUpdate, session: SessionDep, auth: AuthDep
) -> APIKeySummary:
    return session.info["service"].revoke_api_key(session, auth, key_id, body.reason)


@router.post("/v1/agents/register", response_model=AgentResponse, tags=["agents"], status_code=201)
def register_agent(body: AgentRegistration, session: SessionDep, auth: AuthDep) -> AgentResponse:
    return session.info["service"].register_agent(session, auth, body)


@router.get("/v1/agents/{agent_id}", response_model=AgentResponse, tags=["agents"])
def get_agent(agent_id: str, session: SessionDep, auth: AuthDep) -> AgentResponse:
    return session.info["service"].get_agent(session, auth, agent_id)


@router.post("/v1/agents/{agent_id}/revoke", response_model=AgentResponse, tags=["agents"])
def revoke_agent(
    agent_id: str, body: StatusUpdate, session: SessionDep, auth: AuthDep
) -> AgentResponse:
    return session.info["service"].revoke_agent(session, auth, agent_id, body.reason)


@router.get("/v1/decisions/{decision_id}", response_model=DecisionResponse, tags=["decisions"])
def get_decision(decision_id: str, session: SessionDep, auth: AuthDep) -> DecisionResponse:
    return session.info["service"].get_decision(session, auth, decision_id)


@router.post("/v1/decisions", response_model=DecisionResponse, tags=["decisions"])
def decide(body: DecisionRequest, session: SessionDep, auth: AuthDep) -> DecisionResponse:
    result = session.info["service"].decide(session, auth, body)
    DECISIONS.labels(result.outcome).inc()
    return result


@router.post("/v1/events", response_model=EventResponse, tags=["events"], status_code=201)
def ingest_event(body: EventIngest, session: SessionDep, auth: AuthDep) -> EventResponse:
    return session.info["service"].ingest_event(session, auth, body)


@router.get("/v1/traces/{trace_id}", response_model=list[EventResponse], tags=["events"])
def get_trace(
    trace_id: str, session: SessionDep, auth: AuthDep,
    limit: int = Query(500, ge=1, le=5000),
    after_sequence: int | None = Query(None, ge=0),
) -> list[EventResponse]:
    return session.info["service"].get_trace(
        session, auth, trace_id, limit=limit, after_sequence=after_sequence
    )


@router.get("/v1/audit/verify", response_model=AuditVerificationResponse, tags=["audit"])
def verify_audit(session: SessionDep, auth: AuthDep) -> AuditVerificationResponse:
    return session.info["service"].verify_audit_chain(session, auth)


@router.get("/v1/audit/checkpoints", response_model=list[AuditCheckpointResponse], tags=["audit"])
def list_audit_checkpoints(
    session: SessionDep, auth: AuthDep, limit: int = Query(100, ge=1, le=5000),
    before_sequence: int | None = Query(None, ge=1),
) -> list[AuditCheckpointResponse]:
    return session.info["service"].list_audit_checkpoints(
        session, auth, limit=limit, before_sequence=before_sequence
    )


@router.get("/v1/policies", response_model=list[PolicyBundleResponse], tags=["policies"])
def list_policies(
    session: SessionDep, auth: AuthDep, limit: int = Query(100, ge=1, le=5000),
    after_id: str | None = None
) -> list[PolicyBundleResponse]:
    return session.info["service"].list_policies(session, auth, limit=limit, after_id=after_id)


@router.post("/v1/policies", response_model=PolicyBundleResponse, tags=["policies"], status_code=201)
def publish_policy(body: PolicyBundleIn, session: SessionDep, auth: AuthDep) -> PolicyBundleResponse:
    return session.info["service"].publish_policy(session, auth, body)


@router.post(
    "/v1/policies/{policy_id}/activate",
    response_model=PolicyBundleResponse,
    tags=["policies"],
)
def activate_policy(
    policy_id: str, body: StatusUpdate, session: SessionDep, auth: AuthDep
) -> PolicyBundleResponse:
    return session.info["service"].activate_policy(
        session, auth, policy_id, body.reason
    )


@router.get("/v1/approvals", response_model=list[ApprovalResponse], tags=["approvals"])
def list_approvals(
    session: SessionDep, auth: AuthDep, status: str | None = None,
    limit: int = Query(100, ge=1, le=5000), after_id: str | None = None,
) -> list[ApprovalResponse]:
    return session.info["service"].list_approvals(
        session, auth, status, limit=limit, after_id=after_id
    )


@router.get("/v1/approvals/{approval_id}", response_model=ApprovalResponse, tags=["approvals"])
def get_approval(approval_id: str, session: SessionDep, auth: AuthDep) -> ApprovalResponse:
    return session.info["service"].get_approval(session, auth, approval_id)


@router.post("/v1/approvals/{approval_id}/decision", response_model=ApprovalResponse, tags=["approvals"])
def decide_approval(
    approval_id: str,
    body: ApprovalDecisionIn,
    session: SessionDep,
    auth: AuthDep,
) -> ApprovalResponse:
    return session.info["service"].decide_approval(session, auth, approval_id, body)


@router.post("/v1/capabilities", response_model=CapabilityResponse, tags=["capabilities"], status_code=201)
def issue_capability(
    body: CapabilityIssueRequest, session: SessionDep, auth: AuthDep
) -> CapabilityResponse:
    return session.info["service"].issue_capability_token(session, auth, body)


@router.post("/v1/capabilities/consume", response_model=CapabilityVerification, tags=["capabilities"])
def consume_capability(
    body: CapabilityConsumeRequest, session: SessionDep, auth: AuthDep
) -> CapabilityVerification:
    return session.info["service"].consume_capability_token(session, auth, body)


@router.post(
    "/v1/capabilities/{capability_id}/revoke",
    response_model=CapabilityVerification,
    tags=["capabilities"],
)
def revoke_capability(
    capability_id: str, body: StatusUpdate, session: SessionDep, auth: AuthDep
) -> CapabilityVerification:
    return session.info["service"].revoke_capability(
        session, auth, capability_id, body.reason
    )


@router.get("/v1/artifacts/{artifact_id}", response_model=ArtifactResponse, tags=["artifacts"])
def get_artifact_metadata(
    artifact_id: str, session: SessionDep, auth: AuthDep
) -> ArtifactResponse:
    return session.info["service"].get_artifact_metadata(session, auth, artifact_id)


@router.post("/v1/artifacts/scan", response_model=ArtifactResponse, tags=["artifacts"], status_code=201)
async def scan_artifact(
    session: SessionDep,
    auth: AuthDep,
    trace_id: Annotated[str, Form(min_length=8, max_length=64)],
    artifact: Annotated[UploadFile, File()],
) -> ArtifactResponse:
    service = session.info["service"]
    content = await artifact.read(service.settings.max_artifact_bytes + 1)
    return service.scan_artifact(
        session,
        auth,
        trace_id=trace_id,
        filename=artifact.filename or "unnamed-artifact",
        media_type=artifact.content_type or "application/octet-stream",
        content=content,
    )


@router.get(
    "/v1/artifacts/{artifact_id}/content",
    tags=["artifacts"],
    responses={
        200: {
            "description": "Decrypted artifact content",
            "content": {"application/octet-stream": {"schema": {"type": "string", "format": "binary"}}},
            "headers": {
                "Digest": {"schema": {"type": "string"}},
                "Content-Disposition": {"schema": {"type": "string"}},
            },
        }
    },
)
def get_artifact(artifact_id: str, session: SessionDep, auth: AuthDep) -> Response:
    artifact, content = session.info["service"].get_artifact_content(session, auth, artifact_id)
    return Response(
        content=content,
        media_type=artifact.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{_safe_filename(artifact.filename)}"',
            "Digest": f"sha-256={base64.b64encode(bytes.fromhex(artifact.sha256)).decode()}",
        },
    )


@router.get("/v1/incidents", response_model=list[IncidentResponse], tags=["incidents"])
def list_incidents(
    session: SessionDep, auth: AuthDep, status: str | None = None,
    limit: int = Query(100, ge=1, le=5000), after_id: str | None = None,
) -> list[IncidentResponse]:
    return session.info["service"].list_incidents(
        session, auth, status, limit=limit, after_id=after_id
    )


@router.post("/v1/incidents", response_model=IncidentResponse, tags=["incidents"], status_code=201)
def create_incident(body: IncidentCreate, session: SessionDep, auth: AuthDep) -> IncidentResponse:
    return session.info["service"].create_incident(session, auth, body)


@router.get("/v1/incidents/{incident_id}", response_model=IncidentResponse, tags=["incidents"])
def get_incident(incident_id: str, session: SessionDep, auth: AuthDep) -> IncidentResponse:
    return session.info["service"].get_incident(session, auth, incident_id)


@router.post(
    "/v1/incidents/{incident_id}/status", response_model=IncidentResponse, tags=["incidents"]
)
def update_incident_status(
    incident_id: str, body: IncidentStatusUpdate, session: SessionDep, auth: AuthDep
) -> IncidentResponse:
    return session.info["service"].update_incident_status(
        session, auth, incident_id, body
    )


@router.get("/v1/providers", response_model=list[ProviderResponse], tags=["brokers"])
def list_providers(
    session: SessionDep, auth: AuthDep, limit: int = Query(100, ge=1, le=5000),
    after_id: str | None = None
) -> list[ProviderResponse]:
    return session.info["service"].list_providers(session, auth, limit=limit, after_id=after_id)


@router.post("/v1/providers", response_model=ProviderResponse, tags=["brokers"], status_code=201)
def register_provider(
    body: ProviderRegistration, session: SessionDep, auth: AuthDep
) -> ProviderResponse:
    return session.info["service"].register_provider(session, auth, body)


@router.post("/v1/providers/{provider_id}/revoke", response_model=ProviderResponse, tags=["brokers"])
def revoke_provider(
    provider_id: str, body: StatusUpdate, session: SessionDep, auth: AuthDep
) -> ProviderResponse:
    return session.info["service"].revoke_provider(session, auth, provider_id, body.reason)


@router.get("/v1/tools", response_model=list[ToolResponse], tags=["brokers"])
def list_tools(
    session: SessionDep, auth: AuthDep, limit: int = Query(100, ge=1, le=5000),
    after_id: str | None = None
) -> list[ToolResponse]:
    return session.info["service"].list_tools(session, auth, limit=limit, after_id=after_id)


@router.post("/v1/tools", response_model=ToolResponse, tags=["brokers"], status_code=201)
def register_tool(body: ToolRegistration, session: SessionDep, auth: AuthDep) -> ToolResponse:
    return session.info["service"].register_tool(session, auth, body)


@router.post("/v1/tools/{tool_id}/revoke", response_model=ToolResponse, tags=["brokers"])
def revoke_tool(
    tool_id: str, body: StatusUpdate, session: SessionDep, auth: AuthDep
) -> ToolResponse:
    return session.info["service"].revoke_tool(session, auth, tool_id, body.reason)


@router.post(
    "/v1/executions/recover-stale",
    response_model=ExecutionRecoveryResponse,
    tags=["executions"],
)
def recover_stale_executions(
    session: SessionDep, auth: AuthDep, limit: int = Query(100, ge=1, le=5000)
) -> ExecutionRecoveryResponse:
    return session.info["service"].recover_stale_executions(session, auth, limit=limit)


@router.get("/v1/executions", response_model=list[ExecutionResponse], tags=["executions"])
def list_executions(
    session: SessionDep,
    auth: AuthDep,
    state: str | None = Query(default=None, max_length=64),
    limit: int = Query(default=100, ge=1, le=1000),
    after_id: str | None = Query(default=None, max_length=64),
) -> list[ExecutionResponse]:
    return session.info["service"].list_executions(
        session, auth, state=state, limit=limit, after_id=after_id
    )


@router.get("/v1/executions/{execution_id}", response_model=ExecutionResponse, tags=["executions"])
def get_execution(execution_id: str, session: SessionDep, auth: AuthDep) -> ExecutionResponse:
    return session.info["service"].get_execution(session, auth, execution_id)


@router.post(
    "/v1/executions/{execution_id}/reconcile",
    response_model=ExecutionResponse,
    tags=["executions"],
)
def reconcile_execution(
    execution_id: str,
    body: ExecutionReconcileRequest,
    session: SessionDep,
    auth: AuthDep,
) -> ExecutionResponse:
    return session.info["service"].reconcile_execution(
        session, auth, execution_id,
        state=body.state, reason=body.reason,
        response_status_code=body.response_status_code,
        response_headers=body.response_headers, response_body=body.response_body,
    )


@router.post(
    "/v1/providers/{provider_id}/invoke",
    response_model=BrokerResponse,
    tags=["brokers"],
    status_code=200,
)
async def invoke_provider(
    provider_id: str,
    body: ProviderInvokeRequest,
    request: Request,
    session: SessionDep,
    auth: AuthDep,
) -> BrokerResponse:
    auth.require("providers:invoke")
    service = session.info["service"]
    provider = service.get_provider(session, auth.tenant_id, provider_id)
    if body.body.get("stream") is True:
        raise AuthorizationError("buffered enforcement forbids provider streaming")
    target, endpoint = service.validate_provider_path(provider, body.path)
    original_execution = {
        "method": "POST",
        "path": body.path,
        "body": body.body,
        "query": body.query,
    }
    actual_content = json.dumps(body.body, sort_keys=True, separators=(",", ":"))
    supplied_content = body.decision.security_context.content
    security = body.decision.security_context.model_copy(
        update={
            "network_destination": target,
            "content": (supplied_content + "\n" if supplied_content else "") + actual_content,
        }
    )
    action = body.decision.action.model_copy(
        update={
            "type": "model.request",
            "tool": provider.name,
            "operation": "invoke",
            "target": target,
            "arguments": original_execution,
            "external_effect": True,
        }
    )
    decision_request = body.decision.model_copy(update={"security_context": security, "action": action})
    result = service.decide(session, auth, decision_request)
    DECISIONS.labels(result.outcome).inc()
    if result.outcome not in {"allow", "allow_with_limits", "redact_or_transform"} or not result.enforcement_plan.executable:
        BROKER_CALLS.labels("provider", "blocked").inc()
        raise AuthorizationError(
            "provider invocation was blocked by AGENTDANCE",
            details={
                "decision_id": result.decision_id,
                "approval_id": result.approval_id,
                "outcome": result.outcome,
                "reasons": result.reasons,
            },
        )
    transformed_action = result.enforcement_plan.transformed_action
    transformed_execution = transformed_action.get("arguments")
    if not isinstance(transformed_execution, dict):
        raise AuthorizationError("enforcement plan did not produce an executable provider request")
    if transformed_execution.get("method") != "POST" or transformed_execution.get("path") != body.path:
        raise AuthorizationError("enforcement plan attempted to alter immutable provider routing fields")
    transformed_body = transformed_execution.get("body")
    transformed_query = transformed_execution.get("query", {})
    if not isinstance(transformed_body, dict) or not isinstance(transformed_query, dict):
        raise AuthorizationError("enforcement plan produced invalid provider body or query data")
    execution, should_dispatch = service.prepare_provider_execution(
        session,
        auth,
        provider=provider,
        decision_id=result.decision_id,
        trace_id=decision_request.trace_id,
        idempotency_key=body.idempotency_key,
        original_request=original_execution,
        transformed_request=transformed_execution,
        controls=[control.model_dump(mode="json") for control in result.enforcement_plan.controls],
    )
    if request.app.state.settings.dispatch_mode != "inline":
        return await _queued_or_wait(request, auth, execution)
    if not should_dispatch:
        if execution.state == "succeeded":
            return _broker_response_from_execution(execution)
        raise ConflictError(
            "execution is already in progress or requires reconciliation",
            details={"execution_id": execution.id, "state": execution.state},
        )
    try:
        response = await _forward_json(
            request,
            target,
            endpoint=endpoint,
            method="POST",
            body=transformed_body,
            query={str(k): str(v) for k, v in transformed_query.items()},
            auth_header=provider.auth_header_name,
            auth_value=service.provider_auth(session, provider),
            upstream_idempotency_key=execution.upstream_idempotency_key,
            max_response_bytes=_control_response_limit(
                execution.controls_applied,
                request.app.state.settings.max_broker_response_bytes,
            ),
        )
    except (ConflictError, DependencyUnavailableError) as exc:
        service.finalize_execution_failure(
            session,
            auth,
            execution.id,
            error_code=exc.code,
            error_message=exc.message,
            outcome_unknown=True,
        )
        BROKER_CALLS.labels("provider", "failed").inc()
        raise
    except Exception as exc:
        service.finalize_execution_failure(
            session,
            auth,
            execution.id,
            error_code="unexpected_dispatch_failure",
            error_message=str(exc)[:4096] or type(exc).__name__,
            outcome_unknown=True,
        )
        BROKER_CALLS.labels("provider", "failed").inc()
        raise
    broker = _broker_response(response, result.decision_id, execution.id, "succeeded")
    service.finalize_execution_success(
        session,
        auth,
        execution.id,
        status_code=response.status_code,
        headers=broker.headers,
        body=broker.body,
        response_hash=hashlib.sha256(response.content).hexdigest(),
    )
    BROKER_CALLS.labels("provider", str(response.status_code)).inc()
    return broker

@router.post(
    "/v1/tools/{tool_id}/execute",
    response_model=BrokerResponse,
    tags=["brokers"],
    status_code=200,
)
async def execute_tool(
    tool_id: str,
    body: ToolExecuteRequest,
    request: Request,
    session: SessionDep,
    auth: AuthDep,
) -> BrokerResponse:
    service = session.info["service"]
    tool = service.get_tool(session, auth.tenant_id, tool_id)
    target, endpoint = service.validate_tool_call(tool, body.operation, body.method, body.path)
    execution_request = {
        "method": body.method,
        "path": body.path,
        "body": body.body,
        "query": body.query,
    }
    execution, should_dispatch = service.prepare_tool_execution(
        session,
        auth,
        tool=tool,
        token=body.capability_token,
        agent_id=body.agent_id,
        trace_id=body.trace_id,
        operation=body.operation,
        resource=body.resource,
        execution_request=execution_request,
        idempotency_key=body.idempotency_key,
    )
    if request.app.state.settings.dispatch_mode != "inline":
        return await _queued_or_wait(request, auth, execution)
    if not should_dispatch:
        if execution.state == "succeeded":
            return _broker_response_from_execution(execution)
        raise ConflictError(
            "execution is already in progress or requires reconciliation",
            details={"execution_id": execution.id, "state": execution.state},
        )
    try:
        response = await _forward_json(
            request,
            target,
            endpoint=endpoint,
            method=body.method,
            body=body.body,
            query=body.query,
            auth_header=tool.auth_header_name,
            auth_value=service.tool_auth(session, tool),
            upstream_idempotency_key=execution.upstream_idempotency_key,
            max_response_bytes=_control_response_limit(
                execution.controls_applied,
                request.app.state.settings.max_broker_response_bytes,
            ),
        )
    except (ConflictError, DependencyUnavailableError) as exc:
        service.finalize_execution_failure(
            session,
            auth,
            execution.id,
            error_code=exc.code,
            error_message=exc.message,
            outcome_unknown=body.method != "GET" and isinstance(exc, DependencyUnavailableError),
        )
        BROKER_CALLS.labels("tool", "failed").inc()
        raise
    except Exception as exc:
        service.finalize_execution_failure(
            session,
            auth,
            execution.id,
            error_code="unexpected_dispatch_failure",
            error_message=str(exc)[:4096] or type(exc).__name__,
            outcome_unknown=body.method not in {"GET", "HEAD"},
        )
        BROKER_CALLS.labels("tool", "failed").inc()
        raise
    broker = _broker_response(response, None, execution.id, "succeeded")
    service.finalize_execution_success(
        session,
        auth,
        execution.id,
        status_code=response.status_code,
        headers=broker.headers,
        body=broker.body,
        response_hash=hashlib.sha256(response.content).hexdigest(),
    )
    BROKER_CALLS.labels("tool", str(response.status_code)).inc()
    return broker

async def _queued_or_wait(
    request: Request, auth: AuthContext, execution: Execution
) -> BrokerResponse | JSONResponse:
    settings = request.app.state.settings
    if settings.dispatch_mode == "hybrid":
        deadline = asyncio.get_running_loop().time() + settings.dispatch_wait_seconds
        while asyncio.get_running_loop().time() < deadline:
            await asyncio.sleep(min(0.05, max(settings.dispatch_wait_seconds / 20.0, 0.01)))
            with request.app.state.session_factory() as polling_session:
                set_tenant_context(polling_session, auth.tenant_id)
                current = polling_session.scalar(
                    select(Execution).where(
                        Execution.tenant_id == auth.tenant_id,
                        Execution.id == execution.id,
                    )
                )
                if current is None:
                    raise NotFoundError("queued execution disappeared")
                if current.state == "succeeded":
                    return _broker_response_from_execution(current)
                if current.state in {"failed", "outcome_unknown"}:
                    raise ConflictError(
                        "queued execution requires operator attention",
                        details={"execution_id": current.id, "state": current.state},
                    )
    queued = BrokerResponse(
        status_code=202,
        headers={"location": f"/v1/executions/{execution.id}"},
        body={
            "accepted": True,
            "execution_id": execution.id,
            "state": execution.state,
            "poll": f"/v1/executions/{execution.id}",
        },
        decision_id=execution.decision_id,
        execution_id=execution.id,
        execution_state=execution.state,
    )
    return JSONResponse(
        status_code=202,
        headers={"Location": f"/v1/executions/{execution.id}"},
        content=jsonable_encoder(queued),
    )


@router.post("/v1/workload-identities", response_model=WorkloadIdentityBindingResponse,
             status_code=201, tags=["workload-identity"])
def create_workload_identity(body: WorkloadIdentityBindingCreate, request: Request,
                             session: SessionDep, auth: AuthDep) -> WorkloadIdentityBindingResponse:
    return request.app.state.advanced.create_workload_binding(session, auth, body)


@router.get("/v1/workload-identities", response_model=list[WorkloadIdentityBindingResponse],
            tags=["workload-identity"])
def list_workload_identities(request: Request, session: SessionDep,
                             auth: AuthDep) -> list[WorkloadIdentityBindingResponse]:
    return request.app.state.advanced.list_workload_bindings(session, auth)


@router.post("/v1/workload-identities/{binding_id}/revoke",
             response_model=WorkloadIdentityBindingResponse, tags=["workload-identity"])
def revoke_workload_identity(binding_id: str, body: StatusUpdate, request: Request,
                             session: SessionDep, auth: AuthDep) -> WorkloadIdentityBindingResponse:
    return request.app.state.advanced.revoke_workload_binding(session, auth, binding_id, body.reason)


@router.post("/v1/policies/validate", response_model=PolicyValidationResponse, tags=["policies"])
def validate_policy(body: PolicyValidationRequest, request: Request, auth: AuthDep) -> PolicyValidationResponse:
    return request.app.state.advanced.validate_policy(auth, body.document)


@router.post("/v1/policies/simulate", response_model=PolicySimulationResponse, tags=["policies"])
def simulate_policy(body: PolicySimulationRequest, request: Request, session: SessionDep,
                    auth: AuthDep) -> PolicySimulationResponse:
    return request.app.state.advanced.simulate_policy(session, auth, body)


@router.post("/v1/policies/diff", response_model=PolicyDiffResponse, tags=["policies"])
def diff_policy(body: PolicyDiffRequest, request: Request, session: SessionDep,
                auth: AuthDep) -> PolicyDiffResponse:
    return request.app.state.advanced.diff_policy(session, auth, body)


@router.post("/v1/policies/{policy_id}/replay", response_model=PolicySimulationResponse,
             tags=["policies"])
def replay_policy(policy_id: str, request: Request, session: SessionDep, auth: AuthDep,
                  limit: int = Query(default=100, ge=1, le=1000)) -> PolicySimulationResponse:
    return request.app.state.advanced.replay_policy(session, auth, policy_id, limit)


@router.post("/v1/policies/{policy_id}/canary", response_model=PolicyBundleResponse,
             tags=["policies"])
def canary_policy(policy_id: str, body: PolicyCanaryRequest, request: Request,
                  session: SessionDep, auth: AuthDep) -> PolicyBundleResponse:
    return request.app.state.advanced.set_policy_rollout(
        session, auth, policy_id, "canary", body.percentage, body.reason
    )


@router.post("/v1/policies/{policy_id}/shadow", response_model=PolicyBundleResponse,
             tags=["policies"])
def shadow_policy(policy_id: str, body: StatusUpdate, request: Request,
                  session: SessionDep, auth: AuthDep) -> PolicyBundleResponse:
    return request.app.state.advanced.set_policy_rollout(
        session, auth, policy_id, "shadow", 0, body.reason
    )


@router.post("/v1/policies/{policy_id}/rollback", response_model=PolicyBundleResponse,
             tags=["policies"])
def rollback_policy(policy_id: str, body: StatusUpdate, request: Request,
                    session: SessionDep, auth: AuthDep) -> PolicyBundleResponse:
    return request.app.state.advanced.rollback_policy(session, auth, policy_id, body.reason)


@router.post("/v1/audit/anchors", response_model=AuditAnchorResponse, status_code=201,
             tags=["audit"])
def anchor_audit(body: AuditAnchorRequest, request: Request, session: SessionDep,
                 auth: AuthDep) -> AuditAnchorResponse:
    return request.app.state.advanced.anchor_audit(session, auth, body.destination)


@router.post("/v1/audit/anchors/batch", response_model=AuditAnchorQuorumResponse,
             status_code=202, tags=["audit"])
def anchor_audit_batch(body: AuditAnchorBatchRequest, request: Request, session: SessionDep,
                       auth: AuthDep) -> AuditAnchorQuorumResponse:
    return request.app.state.advanced.anchor_audit_batch(
        session, auth, destinations=body.destinations, required_quorum=body.required_quorum
    )


@router.get("/v1/audit/anchors/quorum", response_model=AuditAnchorQuorumResponse,
            tags=["audit"])
def audit_anchor_quorum(request: Request, session: SessionDep, auth: AuthDep,
                        sequence: int | None = Query(default=None, ge=0),
                        required_quorum: int | None = Query(default=None, ge=1, le=16)
                        ) -> AuditAnchorQuorumResponse:
    return request.app.state.advanced.audit_anchor_quorum(
        session, auth, sequence=sequence, required_quorum=required_quorum
    )


@router.post("/v1/audit/anchors/{anchor_id}/verify", response_model=AuditAnchorResponse,
             tags=["audit"])
def verify_audit_anchor(anchor_id: str, request: Request, session: SessionDep,
                        auth: AuthDep) -> AuditAnchorResponse:
    return request.app.state.advanced.verify_anchor(session, auth, anchor_id)


@router.post("/v1/memory", response_model=MemoryRecordResponse, status_code=201,
             tags=["memory"])
def write_memory(body: MemoryWriteRequest, request: Request, session: SessionDep,
                 auth: AuthDep) -> MemoryRecordResponse:
    return request.app.state.advanced.write_memory(session, auth, body)


@router.get("/v1/memory/{memory_id}", response_model=MemoryRecordResponse, tags=["memory"])
def read_memory(memory_id: str, request: Request, session: SessionDep,
                auth: AuthDep, include_content: bool = Query(default=False)) -> MemoryRecordResponse:
    return request.app.state.advanced.read_memory(session, auth, memory_id, include_content)


@router.post("/v1/memory/{memory_id}/status", response_model=MemoryRecordResponse,
             tags=["memory"])
def update_memory_status(memory_id: str, body: MemoryStatusUpdate, request: Request,
                         session: SessionDep, auth: AuthDep) -> MemoryRecordResponse:
    return request.app.state.advanced.update_memory_status(session, auth, memory_id, body)


@router.post("/v1/delegations", response_model=DelegationGrantResponse, status_code=201,
             tags=["delegations"])
def create_delegation(body: DelegationGrantCreate, request: Request, session: SessionDep,
                      auth: AuthDep) -> DelegationGrantResponse:
    return request.app.state.advanced.create_delegation(session, auth, body)


@router.post("/v1/delegations/{grant_id}/revoke", response_model=DelegationGrantResponse,
             tags=["delegations"])
def revoke_delegation(grant_id: str, body: StatusUpdate, request: Request,
                      session: SessionDep, auth: AuthDep) -> DelegationGrantResponse:
    return request.app.state.advanced.revoke_delegation(session, auth, grant_id, body.reason)


@router.post("/v1/budgets", response_model=RuntimeBudgetResponse, status_code=201,
             tags=["budgets"])
def create_budget(body: RuntimeBudgetCreate, request: Request, session: SessionDep,
                  auth: AuthDep) -> RuntimeBudgetResponse:
    return request.app.state.advanced.create_budget(session, auth, body)


@router.post("/v1/budgets/{budget_id}/reserve", response_model=BudgetReservationResponse,
             status_code=201, tags=["budgets"])
def reserve_budget(budget_id: str, body: BudgetReservationRequest, request: Request,
                   session: SessionDep, auth: AuthDep) -> BudgetReservationResponse:
    return request.app.state.advanced.reserve_budget(session, auth, budget_id, body)


@router.post("/v1/budget-reservations/{reservation_id}/settle",
             response_model=BudgetReservationResponse, tags=["budgets"])
def settle_budget(reservation_id: str, body: BudgetSettlementRequest, request: Request,
                  session: SessionDep, auth: AuthDep) -> BudgetReservationResponse:
    return request.app.state.advanced.settle_budget(session, auth, reservation_id, body)


@router.post("/v1/tenant/lifecycle", response_model=TenantLifecycleJobResponse,
             status_code=202, tags=["tenant-lifecycle"])
def tenant_lifecycle(body: TenantLifecycleRequest, request: Request, session: SessionDep,
                     auth: AuthDep) -> TenantLifecycleJobResponse:
    return request.app.state.advanced.tenant_lifecycle(session, auth, body)


@router.get("/v1/tenant/lifecycle/{job_id}", response_model=TenantLifecycleJobResponse,
            tags=["tenant-lifecycle"])
def get_tenant_lifecycle(job_id: str, request: Request, session: SessionDep,
                         auth: AuthDep) -> TenantLifecycleJobResponse:
    return request.app.state.advanced.get_lifecycle_job(session, auth, job_id)


@router.get("/v1/tenant/lifecycle/{job_id}/content", tags=["tenant-lifecycle"])
def download_tenant_export(job_id: str, request: Request, session: SessionDep,
                           auth: AuthDep) -> Response:
    evidence, content = request.app.state.advanced.get_lifecycle_export(session, auth, job_id)
    return Response(
        content=content, media_type=evidence.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="tenant-export-{job_id}.zip"',
            "Digest": f"sha-256={base64.b64encode(bytes.fromhex(evidence.sha256)).decode()}",
            "Cache-Control": "no-store",
        },
    )


@router.post("/v1/tenant/lifecycle/{job_id}/reconcile",
             response_model=TenantLifecycleJobResponse, tags=["tenant-lifecycle"])
def reconcile_tenant_lifecycle(job_id: str, body: TenantLifecycleReconcileRequest,
                               request: Request, session: SessionDep,
                               auth: AuthDep) -> TenantLifecycleJobResponse:
    return request.app.state.advanced.reconcile_lifecycle_job(
        session, auth, job_id, resolution=body.resolution, reason=body.reason,
        destruction_receipt=body.destruction_receipt,
    )


@router.post("/v1/tenant/legal-holds", response_model=LegalHoldResponse,
             status_code=201, tags=["tenant-lifecycle"])
def create_legal_hold(body: LegalHoldCreate, request: Request, session: SessionDep,
                      auth: AuthDep) -> LegalHoldResponse:
    return request.app.state.advanced.create_legal_hold(session, auth, body)


@router.get("/v1/tenant/legal-holds", response_model=list[LegalHoldResponse],
            tags=["tenant-lifecycle"])
def list_legal_holds(request: Request, session: SessionDep,
                     auth: AuthDep) -> list[LegalHoldResponse]:
    return request.app.state.advanced.list_legal_holds(session, auth)


@router.post("/v1/tenant/legal-holds/{hold_id}/release", response_model=LegalHoldResponse,
             tags=["tenant-lifecycle"])
def release_legal_hold(hold_id: str, body: StatusUpdate, request: Request,
                       session: SessionDep, auth: AuthDep) -> LegalHoldResponse:
    return request.app.state.advanced.release_legal_hold(session, auth, hold_id, body.reason)


@router.post("/v1/protocols", response_model=ProtocolRegistrationResponse,
             status_code=201, tags=["protocols"])
def register_protocol(body: ProtocolRegistrationCreate, request: Request,
                      session: SessionDep, auth: AuthDep) -> ProtocolRegistrationResponse:
    return request.app.state.advanced.register_protocol(session, auth, body)


@router.get("/v1/protocols/{registration_id}/manifest-versions",
            response_model=list[ProtocolManifestVersionResponse], tags=["protocols"])
def list_protocol_manifest_versions(registration_id: str, request: Request,
                                    session: SessionDep, auth: AuthDep) -> list[ProtocolManifestVersionResponse]:
    return request.app.state.advanced.list_protocol_manifest_versions(
        session, auth, registration_id
    )


@router.post("/v1/protocols/a2a/{registration_id}/authorize", tags=["protocols"])
def authorize_a2a(registration_id: str, body: A2ATaskRequest, request: Request,
                  session: SessionDep, auth: AuthDep) -> dict[str, Any]:
    return request.app.state.advanced.authorize_a2a_task(
        session, auth, registration_id, body
    )


@router.post("/v1/protocols/mcp/{registration_id}/tools/call",
             response_model=BrokerResponse, tags=["protocols"])
async def call_mcp_tool(registration_id: str, body: MCPToolCallRequest, request: Request,
                        session: SessionDep, auth: AuthDep) -> BrokerResponse | JSONResponse:
    auth.require("protocols:invoke")
    registration = session.scalar(
        select(AgentProtocolRegistration).where(
            AgentProtocolRegistration.tenant_id == auth.tenant_id,
            AgentProtocolRegistration.id == registration_id,
            AgentProtocolRegistration.protocol == "mcp",
            AgentProtocolRegistration.status == "active",
        )
    )
    if registration is None:
        raise NotFoundError("MCP registration does not exist")
    tools = registration.manifest.get("tools", [])
    if not isinstance(tools, list):
        raise ConflictError("MCP manifest tool catalog is invalid")
    descriptor = next(
        (item for item in tools if isinstance(item, dict) and item.get("name") == body.tool_name),
        None,
    )
    if descriptor is None:
        raise AuthorizationError("MCP tool is not present in the pinned manifest")
    operation = str(descriptor.get("operation", body.tool_name))
    resource = str(descriptor.get("resource", f"mcp:{registration.external_id}:{body.tool_name}"))

    # Preserve compatibility with explicitly brokered legacy MCP descriptors, but native
    # MCP registrations require no AGENTDANCE-specific routing metadata.
    tool_id = descriptor.get("agentdance_tool_id")
    path = descriptor.get("path")
    if isinstance(tool_id, str) and tool_id and isinstance(path, str) and path:
        tool_request = ToolExecuteRequest(
            capability_token=body.capability_token, trace_id=body.trace_id,
            agent_id=body.agent_id, operation=operation, resource=resource, path=path,
            method=str(descriptor.get("method", "POST")).upper(), body=body.arguments,
            query={}, idempotency_key=body.idempotency_key,
        )
        return await execute_tool(tool_id, tool_request, request, session, auth)

    rpc_body = {
        "jsonrpc": "2.0", "id": body.idempotency_key, "method": "tools/call",
        "params": {"name": body.tool_name, "arguments": body.arguments},
    }
    execution, replayed = request.app.state.service.prepare_protocol_execution(
        session, auth, registration=registration, token=body.capability_token,
        agent_id=body.agent_id, trace_id=body.trace_id, operation=operation,
        resource=resource,
        execution_request={
            "path": "", "method": "POST", "body": rpc_body, "query": {},
            "idempotency_key": body.idempotency_key,
        },
        idempotency_key=body.idempotency_key,
    )
    if replayed and execution.state == "succeeded":
        return _broker_response_from_execution(execution)
    return await _queued_or_wait(request, auth, execution)


@router.post("/v1/dispatch/run", response_model=DispatchRunResponse, tags=["dispatch"])
async def run_dispatcher(request: Request, auth: AuthDep,
                         limit: int = Query(default=20, ge=1, le=1000)) -> DispatchRunResponse:
    auth.require("dispatch:run")
    result = await request.app.state.dispatcher.run_once(limit=limit)
    return DispatchRunResponse(
        worker_id=request.app.state.dispatcher.worker_id,
        claimed=result.claimed,
        succeeded=result.succeeded,
        retried=result.retried,
        failed=result.failed,
        outcome_unknown=result.outcome_unknown,
        dead_lettered=result.dead_lettered,
        execution_ids=list(result.execution_ids),
    )


@router.get("/v1/operator/posture", response_model=OperatorPostureResponse, tags=["operator"])
def operator_posture(request: Request, session: SessionDep, auth: AuthDep) -> OperatorPostureResponse:
    return request.app.state.advanced.operator_posture(session, auth)


@router.get("/operator/api/posture", response_model=OperatorPostureResponse, include_in_schema=False)
def operator_proxy_posture(request: Request, session: SessionDep, auth: OperatorAuthDep) -> OperatorPostureResponse:
    return request.app.state.advanced.operator_posture(session, auth)


@router.get("/operator/api/incidents", response_model=list[IncidentResponse], include_in_schema=False)
def operator_proxy_incidents(session: SessionDep, auth: OperatorAuthDep) -> list[IncidentResponse]:
    return session.info["service"].list_incidents(session, auth, None, limit=100, after_id=None)


@router.get("/operator/api/approvals", response_model=list[ApprovalResponse], include_in_schema=False)
def operator_proxy_approvals(session: SessionDep, auth: OperatorAuthDep) -> list[ApprovalResponse]:
    return session.info["service"].list_approvals(session, auth, None, limit=100, after_id=None)


@router.get("/operator/api/executions", response_model=list[ExecutionResponse], include_in_schema=False)
def operator_proxy_executions(session: SessionDep, auth: OperatorAuthDep) -> list[ExecutionResponse]:
    return session.info["service"].list_executions(session, auth, state=None, limit=100, after_id=None)


@router.get("/operator/api/policies", response_model=list[PolicyBundleResponse], include_in_schema=False)
def operator_proxy_policies(session: SessionDep, auth: OperatorAuthDep) -> list[PolicyBundleResponse]:
    return session.info["service"].list_policies(session, auth, limit=100, after_id=None)


@router.get("/operator", include_in_schema=False, response_class=HTMLResponse)
def operator_console(request: Request, _auth: OperatorAuthDep) -> HTMLResponse:
    nonce = secrets.token_urlsafe(24)
    request.state.csp_nonce = nonce
    html = """<!doctype html><html><head><meta charset='utf-8'><title>AGENTDANCE Operator</title>
<meta name='viewport' content='width=device-width,initial-scale=1'><style nonce='__NONCE__'>
body{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;background:#101216;color:#eef}
button{font:inherit;padding:.65rem;margin:.25rem;border-radius:.35rem;border:1px solid #667;background:#191d24;color:#eef}
pre{white-space:pre-wrap;background:#191d24;padding:1rem;border-radius:.5rem;min-height:20rem}.row{display:flex;gap:.5rem;flex-wrap:wrap}
</style></head><body><h1>AGENTDANCE Operator Console</h1>
<p>Authenticated by the configured OIDC identity proxy. No API key is accepted or stored by this page.</p>
<div class='row'><button id='load' type='button'>Refresh posture</button></div>
<pre id='out'>Loading…</pre><script nonce='__NONCE__'>
async function get(path){const r=await fetch(path,{credentials:'same-origin',headers:{Accept:'application/json'}});const t=await r.text();let v;try{v=JSON.parse(t)}catch{v=t}return {status:r.status,body:v}}
async function loadData(){const paths=['/operator/api/posture','/operator/api/incidents','/operator/api/approvals','/operator/api/executions','/operator/api/policies'];const rows=[];for(const p of paths)rows.push([p,await get(p)]);document.getElementById('out').textContent=JSON.stringify(Object.fromEntries(rows),null,2)}
document.getElementById('load').addEventListener('click',loadData);loadData();
</script></body></html>""".replace("__NONCE__", nonce)
    return HTMLResponse(html)



async def _forward_json(
    request: Request,
    target: str,
    *,
    endpoint: ValidatedEndpoint,
    method: str,
    body: object,
    query: dict[str, str],
    auth_header: str,
    auth_value: str,
    upstream_idempotency_key: str,
    max_response_bytes: int | None = None,
) -> httpx.Response:
    settings = request.app.state.settings
    response_limit = min(
        settings.max_broker_response_bytes,
        max_response_bytes or settings.max_broker_response_bytes,
    )
    pinned_target, host_header, request_extensions = pin_validated_target(target, endpoint)
    headers = {
        auth_header: auth_value,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"AGENTDANCE/{request.app.state.version}",
        "X-Agentdance-Request-ID": request.state.request_id,
        "X-Agentdance-Execution-ID": upstream_idempotency_key.removeprefix("agentdance-"),
        "Idempotency-Key": upstream_idempotency_key,
    }
    headers["Host"] = host_header
    client: httpx.AsyncClient = request.app.state.http_client
    try:
        async with client.stream(
            method, pinned_target, json=body, params=query, headers=headers,
            extensions=request_extensions,
        ) as upstream:
            chunks: list[bytes] = []
            total = 0
            async for chunk in upstream.aiter_bytes():
                total += len(chunk)
                if total > response_limit:
                    raise ConflictError(
                        "broker response exceeds the configured size limit"
                    )
                chunks.append(chunk)
            return httpx.Response(
                upstream.status_code,
                headers=upstream.headers,
                content=b"".join(chunks),
                request=upstream.request,
                extensions=upstream.extensions,
            )
    except httpx.RequestError as exc:
        raise DependencyUnavailableError("broker upstream request failed") from exc


def _control_response_limit(controls: list[dict[str, Any]], configured_limit: int) -> int:
    limits = [configured_limit]
    for control in controls:
        if control.get("type") != "max_response_bytes" or control.get("status") != "applied":
            continue
        value = control.get("parameters", {}).get("value")
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            raise AuthorizationError("max_response_bytes enforcement control is invalid")
        if parsed < 1:
            raise AuthorizationError("max_response_bytes enforcement control is invalid")
        limits.append(parsed)
    return min(limits)


def _broker_response(
    response: httpx.Response,
    decision_id: str | None,
    execution_id: str = "untracked",
    execution_state: str = "succeeded",
) -> BrokerResponse:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body: Any = response.json()
        except json.JSONDecodeError:
            body = {"encoding": "base64", "data": base64.b64encode(response.content).decode()}
    elif content_type.startswith("text/"):
        body = response.text
    else:
        body = {"encoding": "base64", "data": base64.b64encode(response.content).decode()}
    headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower() in {"content-type", "x-request-id", "retry-after", "request-id"}
    }
    return BrokerResponse(
        status_code=response.status_code,
        headers=headers,
        body=body,
        decision_id=decision_id,
        execution_id=execution_id,
        execution_state=execution_state,
    )


def _broker_response_from_execution(execution: Execution) -> BrokerResponse:
    if execution.state != "succeeded" or execution.response_status_code is None:
        raise ConflictError(
            "execution does not have a reusable successful response",
            details={"execution_id": execution.id, "state": execution.state},
        )
    return BrokerResponse(
        status_code=execution.response_status_code,
        headers=execution.response_headers or {},
        body=execution.response_body,
        decision_id=execution.decision_id,
        execution_id=execution.id,
        execution_state=execution.state,
    )

def _json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()


def _safe_filename(value: str) -> str:
    return "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_", "."})[:255] or "artifact"
