# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Outcome = Literal[
    "allow",
    "allow_with_limits",
    "redact_or_transform",
    "require_approval",
    "deny",
    "quarantine_and_terminate",
]
Severity = Literal["info", "low", "medium", "high", "critical"]


class APIKeyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=255)
    scopes: list[str] = Field(min_length=1, max_length=256)
    expires_at: datetime | None = None
    bound_agent_id: str | None = Field(default=None, max_length=64)
    bound_workload_identity: str | None = Field(default=None, max_length=1024)
    bound_instance_id: str | None = Field(default=None, max_length=255)
    bound_principal_type: Literal["human", "service", "agent"] | None = None
    bound_principal_id: str | None = Field(default=None, max_length=255)


class APIKeySummary(BaseModel):
    id: str
    name: str
    scopes: list[str]
    status: str
    expires_at: datetime | None
    last_used_at: datetime | None
    bound_agent_id: str | None = None
    bound_workload_identity: str | None = None
    bound_instance_id: str | None = None
    bound_principal_type: str | None = None
    bound_principal_id: str | None = None
    created_at: datetime


class APIKeyCreated(APIKeySummary):
    api_key: str


class StatusUpdate(BaseModel):
    reason: str = Field(min_length=3, max_length=4096)


class IncidentStatusUpdate(BaseModel):
    status: Literal["open", "investigating", "contained", "resolved", "false_positive"]
    reason: str = Field(min_length=3, max_length=4096)


class Principal(BaseModel):
    type: Literal["human", "service", "agent"]
    id: str = Field(min_length=1, max_length=255)
    authorization_context: list[str] = Field(default_factory=list, max_length=128)


class AgentContext(BaseModel):
    id: str = Field(min_length=1, max_length=255)
    instance_id: str = Field(min_length=1, max_length=255)
    version: str = Field(min_length=1, max_length=128)
    workload_identity: str = Field(min_length=1, max_length=1024)
    model: str = Field(min_length=1, max_length=512)
    instruction_hash: str = Field(min_length=16, max_length=128)


class Objective(BaseModel):
    declared_goal: str = Field(min_length=1, max_length=4096)
    approved_scope: list[str] = Field(default_factory=list, max_length=512)
    delegation_depth: int = Field(default=0, ge=0, le=32)


class Action(BaseModel):
    type: str = Field(min_length=1, max_length=128)
    tool: str | None = Field(default=None, max_length=512)
    operation: str = Field(min_length=1, max_length=255)
    target: str | None = Field(default=None, max_length=2048)
    arguments: dict[str, Any] = Field(default_factory=dict)
    destructive: bool = False
    reversible: bool = True
    external_effect: bool = False
    amount_usd: float | None = Field(default=None, ge=0, le=1_000_000_000)


class SecurityContext(BaseModel):
    data_classes: list[str] = Field(default_factory=list, max_length=128)
    credential_scope: list[str] = Field(default_factory=list, max_length=128)
    network_destination: str | None = Field(default=None, max_length=2048)
    environment: Literal["development", "test", "staging", "production"] = "production"
    content: str | None = Field(default=None, max_length=1_000_000)
    agent_claim: str | None = Field(default=None, max_length=8192)
    observed_facts: list[str] = Field(default_factory=list, max_length=128)
    labels: dict[str, str] = Field(default_factory=dict)


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    trace_id: str = Field(min_length=8, max_length=64)
    parent_event_id: str | None = Field(default=None, max_length=64)
    principal: Principal
    agent: AgentContext
    objective: Objective
    action: Action
    security_context: SecurityContext
    approval_id: str | None = Field(default=None, max_length=64)
    idempotency_key: str | None = Field(default=None, max_length=128)


class Finding(BaseModel):
    detector: str
    category: str
    severity: Severity
    confidence: float = Field(ge=0, le=1)
    evidence: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class EnforcementControl(BaseModel):
    type: str = Field(min_length=1, max_length=128)
    required: bool = True
    parameters: dict[str, Any] = Field(default_factory=dict)
    status: Literal["planned", "applied", "not_applicable", "failed"] = "planned"
    evidence: dict[str, Any] = Field(default_factory=dict)


class EnforcementPlan(BaseModel):
    version: Literal["aifence.enforcement.v1"] = "aifence.enforcement.v1"
    original_request_hash: str
    transformed_request_hash: str
    transformed_action: dict[str, Any]
    controls: list[EnforcementControl]
    executable: bool


class DecisionResponse(BaseModel):
    decision_id: str
    trace_id: str
    outcome: Outcome
    risk_score: int = Field(ge=0, le=100)
    reasons: list[str]
    constraints: dict[str, Any]
    enforcement_plan: EnforcementPlan
    findings: list[Finding]
    policy_version: str
    approval_id: str | None = None
    receipt: str
    expires_at: datetime


class AgentRegistration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    external_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    version: str = Field(min_length=1, max_length=128)
    workload_identity: str = Field(min_length=1, max_length=1024)
    model: str = Field(min_length=1, max_length=512)
    instruction_hash: str = Field(min_length=16, max_length=128)
    deployment_digest: str | None = Field(default=None, max_length=255)
    allowed_tools: list[str] = Field(default_factory=list, max_length=512)
    allowed_data_classes: list[str] = Field(default_factory=list, max_length=128)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(AgentRegistration):
    id: str
    manifest_hash: str
    status: str
    created_at: datetime


class EventIngest(BaseModel):
    trace_id: str = Field(min_length=8, max_length=64)
    parent_event_id: str | None = Field(default=None, max_length=64)
    event_type: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any]


class EventResponse(BaseModel):
    id: str
    trace_id: str
    sequence: int
    event_type: str
    payload: dict[str, Any]
    previous_hash: str
    event_hash: str
    signature: str
    key_id: str
    created_at: datetime


class PolicyBundleIn(BaseModel):
    version: str = Field(min_length=1, max_length=128)
    document: dict[str, Any]
    activate: bool = False


class PolicyBundleResponse(BaseModel):
    id: str
    version: str
    document_hash: str
    active: bool
    created_by_key_id: str
    created_at: datetime
    activated_at: datetime | None
    activated_by_key_id: str | None
    activation_reason: str | None
    rollout_mode: str = "inactive"
    canary_percentage: int = 0
    validation_report: dict[str, Any] = Field(default_factory=dict)
    supersedes_policy_id: str | None = None


class ApprovalDecisionIn(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str = Field(min_length=3, max_length=4096)


class ApprovalVoteResponse(BaseModel):
    key_id: str
    decision: Literal["approved", "rejected"]
    reason: str
    created_at: datetime


class ApprovalResponse(BaseModel):
    id: str
    trace_id: str
    decision_id: str
    status: str
    request_hash: str
    required_approvals: int
    approval_count: int
    votes: list[ApprovalVoteResponse] = Field(default_factory=list)
    decision_reason: str | None
    created_at: datetime
    decided_at: datetime | None
    expires_at: datetime


class CapabilityIssueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision_id: str = Field(min_length=8, max_length=64)
    lifetime_seconds: int = Field(default=60, ge=5, le=300)
    max_uses: int | None = Field(default=None, ge=1, le=1000)


class CapabilityResponse(BaseModel):
    capability_id: str
    token: str
    expires_at: datetime
    max_uses: int
    constraints: dict[str, Any]
    required_execution: dict[str, Any]


class CapabilityConsumeRequest(BaseModel):
    token: str = Field(min_length=64, max_length=8192)
    agent_id: str = Field(min_length=1, max_length=255)
    trace_id: str = Field(min_length=8, max_length=64)
    tool: str = Field(min_length=1, max_length=512)
    operation: str = Field(min_length=1, max_length=255)
    resource: str = Field(min_length=1, max_length=2048)
    execution: dict[str, Any]


class CapabilityVerification(BaseModel):
    valid: bool
    capability_id: str | None = None
    remaining_uses: int = 0
    constraints: dict[str, Any] = Field(default_factory=dict)


_HTTP_TOKEN = re.compile(r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")
_FORBIDDEN_AUTH_HEADERS = {
    "connection", "content-length", "expect", "host", "proxy-authenticate",
    "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade",
    "x-aifence-request-id",
}

def _validate_auth_header(value: str) -> str:
    if not _HTTP_TOKEN.fullmatch(value) or value.lower() in _FORBIDDEN_AUTH_HEADERS:
        raise ValueError("auth_header_name is invalid or security-sensitive")
    return value

def _validate_auth_value(value: str) -> str:
    if any(character in value for character in ("\r", "\n", "\x00")):
        raise ValueError("auth_value contains prohibited control characters")
    return value

def _validate_path_pattern(value: str) -> str:
    if not value.startswith("/") or "\\" in value or "\x00" in value:
        raise ValueError("broker path patterns must be absolute URL paths")
    if ".." in value.split("/"):
        raise ValueError("broker path patterns cannot contain traversal segments")
    return value

class ProviderRegistration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=255)
    base_url: str = Field(min_length=8, max_length=2048)
    auth_header_name: str = Field(default="Authorization", min_length=1, max_length=255)
    auth_value: str = Field(min_length=1, max_length=4096)
    allowed_paths: list[str] = Field(min_length=1, max_length=128)
    network_zone: Literal["public", "private"] = "public"

    @field_validator("base_url")
    @classmethod
    def https_only(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("provider base_url must use HTTPS")
        return value.rstrip("/")

    @field_validator("auth_header_name")
    @classmethod
    def safe_auth_header(cls, value: str) -> str:
        return _validate_auth_header(value)

    @field_validator("auth_value")
    @classmethod
    def safe_auth_value(cls, value: str) -> str:
        return _validate_auth_value(value)

    @field_validator("allowed_paths")
    @classmethod
    def safe_allowed_paths(cls, values: list[str]) -> list[str]:
        return [_validate_path_pattern(value) for value in values]


class ToolRegistration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=255)
    base_url: str = Field(min_length=8, max_length=2048)
    auth_header_name: str = Field(default="Authorization", min_length=1, max_length=255)
    auth_value: str = Field(min_length=1, max_length=4096)
    allowed_operations: dict[str, Any]
    network_zone: Literal["public", "private"] = "public"

    @field_validator("base_url")
    @classmethod
    def https_only(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("tool base_url must use HTTPS")
        return value.rstrip("/")

    @field_validator("auth_header_name")
    @classmethod
    def safe_auth_header(cls, value: str) -> str:
        return _validate_auth_header(value)

    @field_validator("auth_value")
    @classmethod
    def safe_auth_value(cls, value: str) -> str:
        return _validate_auth_value(value)


class AuditVerificationResponse(BaseModel):
    valid: bool
    events: int | None = None
    head_hash: str | None = None
    event_id: str | None = None
    checkpoint_id: str | None = None
    reason: str | None = None


class AuditCheckpointResponse(BaseModel):
    id: str
    sequence: int
    head_hash: str
    signature: str
    key_id: str
    created_at: datetime


class IncidentCreate(BaseModel):
    trace_id: str = Field(min_length=8, max_length=64)
    severity: Severity
    category: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=512)
    description: str = Field(min_length=1, max_length=8192)
    evidence: list[dict[str, Any]] = Field(default_factory=list, max_length=256)


class IncidentResponse(IncidentCreate):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

class ProviderResponse(BaseModel):
    id: str
    name: str
    base_url: str
    allowed_paths: list[str]
    network_zone: str
    resolved_addresses: list[str]
    status: str
    created_at: datetime


class ProviderInvokeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: DecisionRequest
    path: str = Field(min_length=1, max_length=1024)
    body: dict[str, Any]
    query: dict[str, str] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=8, max_length=128)


class BrokerResponse(BaseModel):
    status_code: int
    headers: dict[str, str]
    body: Any
    decision_id: str | None = None
    execution_id: str
    execution_state: str


class ToolResponse(BaseModel):
    id: str
    name: str
    base_url: str
    allowed_operations: dict[str, Any]
    network_zone: str
    resolved_addresses: list[str]
    status: str
    created_at: datetime


class ToolExecuteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    capability_token: str = Field(min_length=64, max_length=8192)
    trace_id: str = Field(min_length=8, max_length=64)
    agent_id: str = Field(min_length=1, max_length=255)
    operation: str = Field(min_length=1, max_length=255)
    resource: str = Field(min_length=1, max_length=2048)
    path: str = Field(min_length=1, max_length=1024)
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    body: dict[str, Any] | list[Any] | None = None
    query: dict[str, str] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=8, max_length=128)


class ExecutionResponse(BaseModel):
    id: str
    trace_id: str
    broker_type: str
    broker_id: str
    decision_id: str | None
    capability_id: str | None
    idempotency_key: str
    request_hash: str
    transformed_request_hash: str
    controls_applied: list[dict[str, Any]]
    state: str
    attempt_count: int
    upstream_idempotency_key: str
    response_status_code: int | None
    response_headers: dict[str, str] | None
    response_body: Any | None
    response_hash: str | None
    last_error_code: str | None
    reconciliation_status: str
    lease_expires_at: datetime | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class ExecutionRecoveryResponse(BaseModel):
    recovered: int
    execution_ids: list[str]


class ExecutionReconcileRequest(BaseModel):
    state: Literal["succeeded", "failed"]
    reason: str = Field(min_length=3, max_length=4096)
    response_status_code: int | None = Field(default=None, ge=100, le=599)
    response_headers: dict[str, str] | None = None
    response_body: Any | None = None


class ArtifactResponse(BaseModel):
    id: str
    trace_id: str
    filename: str
    media_type: str
    size_bytes: int
    sha256: str
    scan_status: str
    scan_result: dict[str, Any]
    quarantined: bool
    created_at: datetime
    expires_at: datetime


class WorkloadIdentityBindingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    spiffe_id: str = Field(pattern=r"^spiffe://[^/]+/.+", max_length=1024)
    agent_id: str = Field(min_length=1, max_length=64)
    instance_pattern: str | None = Field(default=None, max_length=255)
    principal_type: Literal["human", "service", "agent"] = "agent"
    principal_id: str = Field(min_length=1, max_length=255)
    scopes: list[str] = Field(min_length=1, max_length=256)


class WorkloadIdentityBindingResponse(WorkloadIdentityBindingCreate):
    id: str
    trust_domain: str
    status: str
    created_at: datetime
    revoked_at: datetime | None


class PolicyValidationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document: dict[str, Any]


class PolicyValidationResponse(BaseModel):
    valid: bool
    document_hash: str
    rule_count: int
    test_count: int
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PolicySimulationCase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=255)
    request: DecisionRequest
    expected_outcomes: list[str] = Field(default_factory=list, max_length=6)


class PolicySimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document: dict[str, Any]
    cases: list[PolicySimulationCase] = Field(min_length=1, max_length=1000)


class PolicySimulationCaseResult(BaseModel):
    name: str
    outcome: str
    risk_score: int
    matched_rule: str
    reasons: list[str]
    constraints: dict[str, Any]
    expected: bool | None


class PolicySimulationResponse(BaseModel):
    document_hash: str
    total: int
    passed: int
    failed: int
    outcome_counts: dict[str, int]
    results: list[PolicySimulationCaseResult]


class PolicyDiffRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_document: dict[str, Any]
    proposed_document: dict[str, Any]
    cases: list[PolicySimulationCase] = Field(default_factory=list, max_length=1000)


class PolicyDiffResponse(BaseModel):
    current_hash: str
    proposed_hash: str
    added_rules: list[str]
    removed_rules: list[str]
    changed_rules: list[str]
    default_changed: bool
    outcome_delta: dict[str, int]
    changed_cases: list[dict[str, Any]]
    current_validation: PolicyValidationResponse
    proposed_validation: PolicyValidationResponse


class PolicyCanaryRequest(BaseModel):
    percentage: int = Field(ge=1, le=100)
    reason: str = Field(min_length=3, max_length=4096)


class AuditAnchorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destination: Literal["file", "webhook"]


class AuditAnchorBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destinations: list[str] = Field(min_length=1, max_length=16)
    required_quorum: int = Field(default=1, ge=1, le=16)


class AuditAnchorQuorumResponse(BaseModel):
    sequence: int
    chain_head: str
    required_quorum: int
    verified_count: int
    satisfied: bool
    anchors: list[AuditAnchorResponse]


class AuditAnchorResponse(BaseModel):
    id: str
    sequence: int
    chain_head: str
    destination: str
    receipt: dict[str, Any]
    receipt_hash: str
    status: str
    anchored_at: datetime
    verified_at: datetime | None


class MemoryWriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    external_id: str = Field(min_length=1, max_length=255)
    agent_id: str = Field(min_length=1, max_length=64)
    trace_id: str = Field(min_length=8, max_length=64)
    source_uri: str = Field(min_length=1, max_length=2048)
    source_type: Literal["human", "agent", "tool", "retrieval", "file", "web", "system"]
    content: str = Field(min_length=1, max_length=1_000_000)
    provenance: dict[str, Any] = Field(default_factory=dict)
    data_classes: list[str] = Field(default_factory=list, max_length=128)
    trust_score: int = Field(default=50, ge=0, le=100)
    expires_at: datetime | None = None


class MemoryRecordResponse(BaseModel):
    id: str
    external_id: str
    version: int
    agent_id: str
    trace_id: str
    source_uri: str
    source_type: str
    content_hash: str
    provenance: dict[str, Any]
    data_classes: list[str]
    trust_score: int
    status: str
    expires_at: datetime | None
    created_at: datetime
    content: str | None = None


class MemoryStatusUpdate(BaseModel):
    status: Literal["active", "quarantined", "expired", "deleted"]
    reason: str = Field(min_length=3, max_length=4096)


class DelegationGrantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    parent_agent_id: str = Field(min_length=1, max_length=64)
    child_agent_id: str = Field(min_length=1, max_length=64)
    parent_grant_id: str | None = Field(default=None, max_length=64)
    trace_id: str = Field(min_length=8, max_length=64)
    objective: str = Field(min_length=1, max_length=8192)
    allowed_tools: list[str] = Field(default_factory=list, max_length=512)
    allowed_data_classes: list[str] = Field(default_factory=list, max_length=128)
    resource_patterns: list[str] = Field(default_factory=list, max_length=512)
    max_depth: int = Field(default=0, ge=0, le=32)
    max_fanout: int = Field(default=1, ge=1, le=128)
    budget_limits: dict[str, int | float] = Field(default_factory=dict)
    expires_at: datetime


class DelegationGrantResponse(DelegationGrantCreate):
    id: str
    grant_hash: str
    signature: str
    status: str
    created_at: datetime
    revoked_at: datetime | None


class RuntimeBudgetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scope_type: Literal["tenant", "agent", "trace", "delegation"]
    scope_id: str = Field(min_length=1, max_length=255)
    limits: dict[str, int | float]


class RuntimeBudgetResponse(RuntimeBudgetCreate):
    id: str
    consumed: dict[str, int | float]
    reserved: dict[str, int | float]
    status: str
    version: int
    created_at: datetime
    updated_at: datetime


class BudgetReservationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    trace_id: str = Field(min_length=8, max_length=64)
    idempotency_key: str = Field(min_length=8, max_length=128)
    amounts: dict[str, int | float]
    lifetime_seconds: int = Field(default=300, ge=5, le=86_400)


class BudgetReservationResponse(BaseModel):
    id: str
    budget_id: str
    trace_id: str
    idempotency_key: str
    amounts: dict[str, int | float]
    status: str
    expires_at: datetime
    created_at: datetime
    settled_at: datetime | None


class BudgetSettlementRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["commit", "release"]
    actual_amounts: dict[str, int | float] | None = None
    reason: str = Field(min_length=3, max_length=4096)


class TenantLifecycleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["suspend", "resume", "export", "delete", "crypto_erase"]
    reason: str = Field(min_length=3, max_length=4096)
    parameters: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=128)
    priority: int = Field(default=100, ge=0, le=1000)


class TenantLifecycleJobResponse(BaseModel):
    id: str
    job_type: str
    idempotency_key: str
    status: str
    parameters: dict[str, Any]
    result: dict[str, Any]
    result_storage_key: str | None = None
    attempt_count: int = 0
    fencing_token: int = 0
    reconciliation_status: str = "not_required"
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class TenantLifecycleReconcileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resolution: Literal["confirmed_destroyed", "confirmed_not_destroyed"]
    reason: str = Field(min_length=3, max_length=4096)
    destruction_receipt: dict[str, Any] = Field(default_factory=dict)


class LegalHoldCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scope: str = Field(default="tenant", min_length=1, max_length=64)
    reason: str = Field(min_length=3, max_length=4096)
    expires_at: datetime | None = None


class LegalHoldResponse(LegalHoldCreate):
    id: str
    status: str
    created_at: datetime
    released_at: datetime | None
    release_reason: str | None


class EvidenceObjectResponse(BaseModel):
    id: str
    namespace: str
    external_id: str
    media_type: str
    size_bytes: int
    sha256: str
    immutable: bool
    metadata: dict[str, Any]
    created_at: datetime
    expires_at: datetime | None


class ProtocolRegistrationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    protocol: Literal["mcp", "a2a"]
    external_id: str = Field(min_length=1, max_length=512)
    agent_id: str | None = Field(default=None, max_length=64)
    endpoint: str = Field(min_length=8, max_length=2048)
    protocol_version: str = Field(default="unknown", min_length=1, max_length=64)
    manifest: dict[str, Any] = Field(default_factory=dict)
    discover: bool = False
    auth_header_name: str | None = Field(default=None, min_length=1, max_length=255)
    auth_value: str | None = Field(default=None, min_length=1, max_length=4096)


class ProtocolRegistrationResponse(BaseModel):
    id: str
    protocol: str
    external_id: str
    agent_id: str | None
    endpoint: str
    protocol_version: str
    manifest: dict[str, Any]
    manifest_hash: str
    current_manifest_version: int
    status: str
    created_at: datetime
    updated_at: datetime


class ProtocolManifestVersionResponse(BaseModel):
    id: str
    registration_id: str
    version: int
    protocol_version: str
    manifest: dict[str, Any]
    manifest_hash: str
    source: str
    verification: dict[str, Any]
    created_at: datetime


class MCPToolCallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    capability_token: str = Field(min_length=64, max_length=8192)
    agent_id: str = Field(min_length=1, max_length=64)
    trace_id: str = Field(min_length=8, max_length=64)
    tool_name: str = Field(min_length=1, max_length=255)
    arguments: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=8, max_length=128)


class A2ATaskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    delegation_grant_id: str = Field(min_length=1, max_length=64)
    trace_id: str = Field(min_length=8, max_length=64)
    task_id: str = Field(min_length=1, max_length=255)
    objective: str | None = Field(default=None, min_length=1, max_length=4096)
    tool: str | None = Field(default=None, min_length=1, max_length=512)
    operation: str | None = Field(default=None, min_length=1, max_length=255)
    resource: str | None = Field(default=None, min_length=1, max_length=2048)
    data_classes: list[str] = Field(default_factory=list, max_length=128)
    delegation_depth: int = Field(default=0, ge=0, le=32)
    step_count: int = Field(default=1, ge=1, le=100000)
    budget_amounts: dict[str, int | float] = Field(default_factory=dict)
    message: dict[str, Any]
    artifacts: list[dict[str, Any]] = Field(default_factory=list, max_length=128)
    idempotency_key: str = Field(min_length=8, max_length=128)
    dispatch: bool = False


class OperatorPostureResponse(BaseModel):
    tenant_id: str
    tenant_status: str
    active_policy_id: str | None
    active_policy_version: str | None
    active_agents: int
    open_incidents: int
    pending_approvals: int
    active_capabilities: int
    execution_states: dict[str, int]
    outbox_states: dict[str, int]
    memory_states: dict[str, int]
    active_delegations: int
    active_protocols: int
    latest_audit_sequence: int
    latest_anchor_sequence: int
    generated_at: datetime


class DispatchRunResponse(BaseModel):
    worker_id: str
    claimed: int
    succeeded: int
    retried: int
    failed: int
    outcome_unknown: int
    dead_lettered: int
    execution_ids: list[str]
