# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

JsonValue = Any
MemoryTier = Literal["hot", "warm", "cold"]
FallbackMode = Literal["natural_language", "literal", "reference"]
EpistemicType = Literal["fact", "observation", "inference", "hypothesis", "prediction", "preference", "instruction", "constraint"]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _default_fallback_modes() -> list[FallbackMode]:
    return ["natural_language", "literal", "reference"]


class Provenance(BaseModel):
    source_ids: list[str] = Field(default_factory=list)
    observed_at: str = Field(default_factory=_now_iso)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    derivation: str = "direct"
    producer: str | None = None


class Atom(BaseModel):
    code: str | None = None
    cv: int | None = None
    literal: JsonValue | None = None
    has_literal: bool = False
    path: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    epistemic_type: EpistemicType = "fact"


class TraceContext(BaseModel):
    traceparent: str = Field(pattern=r"^[0-9a-f]{2}-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$", max_length=55)
    tracestate: str | None = Field(default=None, max_length=512)


class Packet(BaseModel):
    v: str = "sage/0.2"
    id: str | None = None
    cb: str
    sender: str | None = None
    receiver: str | None = None
    act: str = "report"
    atoms: list[Atom] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)
    base: str | None = None
    delta: JsonValue | None = None
    prov: Provenance = Field(default_factory=Provenance)
    meta: dict[str, JsonValue] = Field(default_factory=dict)
    signature: dict[str, JsonValue] | None = None
    trace: TraceContext | None = None


class Budget(BaseModel):
    max_tokens: int | None = Field(default=None, gt=0)
    max_bytes: int | None = Field(default=None, gt=0)


class EncodeRequest(BaseModel):
    content: JsonValue
    sender: str | None = None
    receiver: str | None = None
    act: str = "report"
    codebook: str | None = None
    base_state: str | None = None
    receiver_known_codes: set[str] = Field(default_factory=set)
    auto_learn: bool = True
    inline_limit: int | None = None
    budget: Budget | None = None
    provenance: Provenance | None = None
    trace: TraceContext | None = None
    workspace: str = "default"
    run_id: str | None = None
    fallback_mode: FallbackMode = "natural_language"
    use_receiver_knowledge: bool = True
    use_cache: bool = True
    record_learning: bool = True
    use_patterns: bool = True
    receiver_model: str | None = None
    task_family: str = "*"
    source_trust: float = Field(default=1.0, ge=0.0, le=1.0)
    learning_scope: Literal["session", "project", "workspace", "domain", "federation"] = "session"
    semantic_loss_max: float = Field(default=0.0, ge=0.0, le=1.0)


class SendRequest(EncodeRequest):
    """Primary transport request. Same payload as encode, but receiver knowledge is automatic."""


class TransportResponse(BaseModel):
    packet_id: str
    wire: dict[str, JsonValue]
    strategy: str
    estimated_tokens: int
    output_bytes: int
    cache_hit: bool = False


class TransportReceiveRequest(BaseModel):
    wire: dict[str, JsonValue]
    receiver: str | None = None
    workspace: str = "default"
    resolve_refs: bool = False
    acknowledge: bool = True




class HandoffRequest(BaseModel):
    content: JsonValue | None = None
    refs: list[str] = Field(default_factory=list)
    receiver: str = Field(min_length=1, max_length=128)
    sender: str | None = Field(default=None, max_length=128)
    act: str = "handoff"
    workspace: str = "default"
    run_id: str | None = None
    correlation_id: str | None = None
    priority: int = Field(default=0, ge=-1000, le=1000)
    ttl_seconds: int | None = Field(default=None, gt=0)
    budget_tokens: int | None = Field(default=None, gt=0)
    source_ids: list[str] = Field(default_factory=list)
    idempotency_key: str | None = Field(default=None, max_length=128)
    partition_key: str | None = Field(default=None, max_length=128)
    ordering_key: str | None = Field(default=None, max_length=128)


class BusMessageResponse(BaseModel):
    message_id: str
    packet_id: str
    sender: str | None = None
    receiver: str
    workspace: str
    run_id: str | None = None
    correlation_id: str | None = None
    idempotency_key: str | None = None
    partition_key: str = "default"
    ordering_key: str | None = None
    sequence_no: int | None = None
    priority: int
    status: str
    wire: dict[str, JsonValue]
    strategy: str
    estimated_tokens: int
    wire_bytes: int
    expires_at: str | None = None
    created_at: str


class BusAckRequest(BaseModel):
    receiver: str = Field(min_length=1, max_length=128)
    workspace: str = "default"


class BusContextItem(BaseModel):
    message_id: str
    packet_id: str
    sender: str | None = None
    receiver: str
    workspace: str
    run_id: str | None = None
    correlation_id: str | None = None
    act: str
    concepts: list[dict[str, JsonValue]]
    literals: list[dict[str, JsonValue]]
    references: list[dict[str, JsonValue]]
    provenance: Provenance
    base_state: JsonValue | None = None
    delta: JsonValue | None = None
    resolved_state: JsonValue | None = None
    strategy: str
    estimated_tokens: int
    wire_bytes: int


class BusBatchAckRequest(BaseModel):
    message_ids: list[str] = Field(min_length=1, max_length=100)
    receiver: str = Field(min_length=1, max_length=128)
    workspace: str = "default"


class A2APackRequest(BaseModel):
    wire: dict[str, JsonValue]


class A2AUnpackRequest(BaseModel):
    part: dict[str, JsonValue]


class A2AMessagePackRequest(BaseModel):
    wire: dict[str, JsonValue]
    message_id: str | None = None
    role: Literal["ROLE_USER", "ROLE_AGENT", "ROLE_UNSPECIFIED"] = "ROLE_USER"
    context_id: str | None = None
    task_id: str | None = None
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class A2AMessageUnpackRequest(BaseModel):
    message: dict[str, JsonValue]


class IntegrationProfile(BaseModel):
    id: str
    display_name: str
    native_plugin: bool
    supports_mcp: bool
    supports_a2a: bool
    recommended_surface: str
    notes: list[str] = Field(default_factory=list)


class IntegrationConfigResponse(BaseModel):
    platform: str
    profile: IntegrationProfile
    files: dict[str, str] = Field(default_factory=dict)
    commands: list[str] = Field(default_factory=list)
    config: dict[str, JsonValue] = Field(default_factory=dict)


class EncodeResponse(BaseModel):
    packet: Packet
    wire_json: str
    wire_msgpack_b64: str
    input_bytes: int
    output_bytes_json: int
    output_bytes_msgpack: int
    estimated_tokens: int
    budget_tokens: int | None = None
    compression_ratio_json: float
    compression_ratio_msgpack: float
    strategy: str = "semantic"
    cache_hit: bool = False


class DecodeRequest(BaseModel):
    packet: Packet
    resolve_refs: bool = False
    receiver: str | None = None
    workspace: str = "default"


class ReceiveRequest(DecodeRequest):
    acknowledge: bool = True


class DecodeResponse(BaseModel):
    act: str
    concepts: list[dict[str, JsonValue]]
    literals: list[dict[str, JsonValue]]
    references: list[dict[str, JsonValue]]
    provenance: Provenance
    base_state: JsonValue | None = None
    delta: JsonValue | None = None
    resolved_state: JsonValue | None = None


class StoreRequest(BaseModel):
    value: JsonValue
    media_type: str = "application/json"
    workspace: str = "default"
    owner: str | None = None
    acl: list[str] = Field(default_factory=list)
    allowed_paths: list[str] = Field(default_factory=list)
    tier: MemoryTier = "warm"
    ttl_seconds: int | None = Field(default=None, gt=0)
    encrypt: bool = False
    provenance: Provenance | None = None
    sensitivity: list[str] = Field(default_factory=list)


class StoreResponse(BaseModel):
    ref: str
    byte_size: int
    tier: MemoryTier = "warm"
    encrypted: bool = False
    expires_at: str | None = None


class ResolveRequest(BaseModel):
    ref: str
    actor: str | None = None
    workspace: str = "default"
    fields: list[str] = Field(default_factory=list)


class RefGrantRequest(BaseModel):
    actor: str | None = None
    workspace: str = "default"
    grantee: str | None = None
    acl: list[str] = Field(default_factory=list)
    allowed_paths: list[str] = Field(default_factory=list)
    tier: MemoryTier = "warm"
    ttl_seconds: int | None = Field(default=None, gt=0)


class RefPolicyRequest(BaseModel):
    actor: str | None = None
    workspace: str = "default"
    tier: MemoryTier | None = None
    ttl_seconds: int | None = Field(default=None, gt=0)
    invalidate: bool = False


class StateCreateRequest(BaseModel):
    value: JsonValue
    workspace: str = "default"
    created_by: str | None = None
    provenance: Provenance | None = None


class StatePatchRequest(BaseModel):
    base: str
    value: JsonValue
    mode: Literal["target", "patch"] = "target"
    workspace: str = "default"
    created_by: str | None = None
    provenance: Provenance | None = None


class StateResponse(BaseModel):
    state: str
    revision: int
    value: JsonValue
    parent: str | None = None
    delta: JsonValue | None = None
    provenance: dict[str, JsonValue] = Field(default_factory=dict)


class ConceptRegisterRequest(BaseModel):
    canonical: str
    description: str = ""
    codebook: str | None = None
    aliases: list[str] = Field(default_factory=list)


class ConceptDeprecateRequest(BaseModel):
    replacement_code: str | None = None


class ConceptAliasRequest(BaseModel):
    alias: str


class ConceptResponse(BaseModel):
    code: str
    codebook: str
    canonical: str
    description: str
    seen_count: int
    confidence: float
    version: int = 1
    status: str = "active"
    replacement_code: str | None = None


class PatternObserveRequest(BaseModel):
    content: JsonValue
    codebook: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    source_trust: float = Field(default=0.5, ge=0.0, le=1.0)
    trust_scope: Literal["session", "project", "workspace", "domain", "federation"] = "session"


class PatternStatusRequest(BaseModel):
    status: Literal["shadow", "validated", "active", "cooling", "deprecated", "retired"]


class PatternCandidateResponse(BaseModel):
    codebook: str
    signature: str
    canonical: str
    composition: list[dict[str, JsonValue]]
    relation_structure: dict[str, JsonValue]
    occurrence_count: int
    estimated_savings_bytes: int
    semantic_variance: float
    trust_scope: str = "session"
    source_diversity: int = 0
    dominant_source_share: float = 1.0
    trust_score: float = 0.0


class PatternResponse(BaseModel):
    pattern_id: str
    concept_code: str | None = None
    concept_version: int | None = None
    codebook: str
    signature: str
    canonical: str
    composition: list[dict[str, JsonValue]]
    relation_structure: dict[str, JsonValue]
    occurrence_count: int
    estimated_savings_bytes: int
    semantic_variance: float
    confidence: float
    status: str
    version: int
    shadow_samples: int
    shadow_success_rate: float | None = None
    task_utility: float | None = None
    utility_score: float = 0.0
    ambiguity_score: float = 0.0
    interoperability_score: float = 1.0
    calibrated_reliability: float = 1.0
    trust_scope: str = "session"
    source_diversity: int = 0
    dominant_source_share: float = 1.0
    trust_score: float = 0.0
    use_count: int = 0
    last_used_at: str | None = None
    children: list[str] = Field(default_factory=list)


class LatentPacket(BaseModel):
    v: str = "sage-latent/0.2"
    space: str
    dims: int = Field(gt=0, le=262144)
    scale: float = Field(gt=0)
    data_b64: str
    checksum: str


class LatentPackRequest(BaseModel):
    vector: list[float] = Field(min_length=1, max_length=262144)
    space: str


class LatentUnpackRequest(BaseModel):
    packet: LatentPacket


class Capabilities(BaseModel):
    protocol_versions: list[str] = Field(default_factory=lambda: ["sage/0.2"])
    codebooks: list[str] = Field(default_factory=list)
    max_packet_bytes: int = Field(default=8192, gt=0)
    supports_refs: bool = True
    supports_deltas: bool = True
    supports_patterns: bool = True
    latent_spaces: list[str] = Field(default_factory=list)
    fallback_modes: list[FallbackMode] = Field(default_factory=_default_fallback_modes)


class NegotiateRequest(BaseModel):
    codebook: str | None = None
    known_codes: set[str] = Field(default_factory=set)
    known_patterns: set[str] = Field(default_factory=set)
    capabilities: Capabilities = Field(default_factory=Capabilities)
    receiver: str | None = None
    workspace: str = "default"


class NegotiateResponse(BaseModel):
    protocol_version: str
    codebook: str
    codebook_chain: list[str]
    embedding_space: str
    missing_codes: list[ConceptResponse]
    missing_patterns: list[PatternResponse] = Field(default_factory=list)
    fingerprint: str
    negotiated: Capabilities


class ExplainResponse(BaseModel):
    packet_id: str
    strategy: str
    decisions: list[dict[str, JsonValue]]
    provenance: dict[str, JsonValue]
    cache_hit: bool
    input_bytes: int
    output_bytes: int
    estimated_tokens: int
    budget_tokens: int | None = None


class FeedbackRequest(BaseModel):
    task_success: float = Field(ge=0.0, le=1.0)


class EvalCase(BaseModel):
    content: JsonValue
    receiver: str = "eval-receiver"
    expected_facts: list[str] = Field(default_factory=list)


class EvalRequest(BaseModel):
    cases: list[EvalCase] = Field(min_length=1, max_length=1000)
    budget_tokens: int = Field(default=1200, gt=0)
    workspace: str = "eval"


class NativeTokenGateRequest(BaseModel):
    eval_score: float = Field(ge=0.0, le=1.0)


class NativeTokenGateResponse(BaseModel):
    allowed: bool
    required_score: float
    reason: str


class ReplayResponse(BaseModel):
    run_id: str
    packets: list[dict[str, JsonValue]]


class TokenizerSpec(BaseModel):
    kind: Literal["estimate", "tiktoken", "http"] = "estimate"
    model: str | None = None
    encoding: str | None = None
    endpoint: str | None = None
    timeout_seconds: float = Field(default=10.0, gt=0, le=120)
    chars_per_token: float = Field(default=4.0, gt=0)

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith(("http://", "https://")):
            raise ValueError("endpoint must be http(s)")
        return value


class PriceProfile(BaseModel):
    currency: str = "USD"
    input_per_million: float = Field(default=0.0, ge=0.0)
    output_per_million: float = Field(default=0.0, ge=0.0)


class EconomicsBenchmarkRequest(BaseModel):
    content: JsonValue
    raw_history: JsonValue | None = None
    summarized_history: JsonValue | None = None
    rag: JsonValue | None = None
    receiver: str = "benchmark-receiver"
    workspace: str = "benchmark"
    budget_tokens: int = Field(default=1200, gt=0)
    tokenizer: TokenizerSpec = Field(default_factory=TokenizerSpec)
    price: PriceProfile = Field(default_factory=PriceProfile)
    task_success: dict[str, float] = Field(default_factory=dict)

    @field_validator("task_success")
    @classmethod
    def validate_task_success(cls, value: dict[str, float]) -> dict[str, float]:
        for strategy, score in value.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"task_success[{strategy}] must be in [0,1]")
        return value


class EconomicsObservation(BaseModel):
    strategy: str = Field(min_length=1, max_length=128)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(default=0, ge=0)
    task_success: float | None = Field(default=None, ge=0.0, le=1.0)
    latency_ms: float | None = Field(default=None, ge=0.0)
    retrievals: int | None = Field(default=None, ge=0)
    wire_bytes: int | None = Field(default=None, ge=0)
    infrastructure_cost_usd: float = Field(default=0.0, ge=0.0)
    retrieval_cost_usd: float = Field(default=0.0, ge=0.0)
    retry_cost_usd: float = Field(default=0.0, ge=0.0)
    provider_cost_usd: float | None = Field(default=None, ge=0.0)
    provider: str | None = None
    model: str | None = None


class ObservedEconomicsRequest(BaseModel):
    observations: list[EconomicsObservation] = Field(min_length=1, max_length=10000)
    price: PriceProfile = Field(default_factory=PriceProfile)


class CounterfactualPatternRequest(BaseModel):
    full_success: float = Field(ge=0.0, le=1.0)
    compressed_success: float = Field(ge=0.0, le=1.0)
    semantic_fidelity: float = Field(ge=0.0, le=1.0)
    receiver: str = "*"
    model: str = "*"
    task_family: str = "*"
    workspace: str = "default"
    validation_id: str = Field(min_length=1, max_length=256)


class CalibrationRecordRequest(BaseModel):
    predicted: float = Field(ge=0.0, le=1.0)
    observed: float = Field(ge=0.0, le=1.0)
    receiver: str = "*"
    model: str = "*"
    task_family: str = "*"
    workspace: str = "default"


class CalibrationResponse(BaseModel):
    sample_count: int
    expected_calibration_error: float
    brier_score: float
    calibrated_probability: float


class FactPutRequest(BaseModel):
    subject: str
    predicate: str
    object: JsonValue
    epistemic_type: EpistemicType = "fact"
    source: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    workspace: str = "default"
    depends_on: list[str] = Field(default_factory=list)
    provenance: Provenance | None = None
    sensitivity: list[str] = Field(default_factory=list)


class FactResponse(BaseModel):
    id: str
    subject: str
    predicate: str
    object: JsonValue
    epistemic_type: EpistemicType
    source: str | None = None
    confidence: float
    status: str
    sensitivity: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)


class FactInvalidateRequest(BaseModel):
    workspace: str = "default"
    reason: str = "source_changed"


class SubscriptionRequest(BaseModel):
    agent: str
    workspace: str = "default"
    concepts: list[str] = Field(default_factory=list)
    filters: dict[str, JsonValue] = Field(default_factory=dict)
    min_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class PublishRequest(BaseModel):
    content: JsonValue
    sender: str | None = None
    workspace: str = "default"
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class AgentCapabilityRequest(BaseModel):
    agent: str
    workspace: str = "default"
    capabilities: list[str] = Field(default_factory=list)
    authority: list[str] = Field(default_factory=list)
    cost_score: float = Field(default=1.0, ge=0.0)
    latency_ms: float = Field(default=0.0, ge=0.0)
    available: bool = True
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class RouteRequest(BaseModel):
    content: JsonValue
    workspace: str = "default"
    capability: str | None = None
    authority: str | None = None
    sender: str | None = None


class FederationPeerRequest(BaseModel):
    name: str
    base_url: str
    public_key_b64: str = ""
    allowed_namespaces: list[str] = Field(default_factory=list)
    workspace: str = "default"
    enabled: bool = True


class FederationImportRequest(BaseModel):
    bundle: dict[str, JsonValue]
    workspace: str = "default"


class InspectorResponse(BaseModel):
    packet_id: str
    workspace: str = "default"
    sender: str | None = None
    receiver: str | None = None
    original_bytes: int
    sent_bytes: int
    estimated_original_tokens: int
    estimated_sent_tokens: int
    receiver_known_ratio: float
    semantic_loss_score: float
    patterns: list[dict[str, JsonValue]] = Field(default_factory=list)
    refs: list[dict[str, JsonValue]] = Field(default_factory=list)
    waterfall: dict[str, JsonValue] = Field(default_factory=dict)
    decisions: list[dict[str, JsonValue]] = Field(default_factory=list)


class ContradictionResolveRequest(BaseModel):
    winner_fact_id: str
    workspace: str = "default"
    note: str = ""

class ModelIdentityRequest(BaseModel):
    receiver: str = Field(min_length=1, max_length=128)
    workspace: str = "default"
    provider: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=256)
    model_version: str = Field(min_length=1, max_length=128)
    runtime: str = Field(min_length=1, max_length=128)
    runtime_version: str = Field(min_length=1, max_length=128)
    configuration: dict[str, JsonValue] = Field(default_factory=dict)


class ModelIdentityResponse(BaseModel):
    receiver: str
    workspace: str
    provider: str
    model: str
    model_version: str
    runtime: str
    runtime_version: str
    config_hash: str
    identity_hash: str
    active: bool


class MerkleSyncRequest(BaseModel):
    namespace: str = Field(min_length=1, max_length=128)
    remote: dict[str, JsonValue] = Field(default_factory=dict)


class CodebookReleaseRequest(BaseModel):
    namespace: str = Field(min_length=1, max_length=128)
    release: str = Field(min_length=1, max_length=128)


class CheckpointResponse(BaseModel):
    checkpoint_id: str
    state_id: str
    revision: int
    payload_hash: str


class ReliabilityResponse(BaseModel):
    status: str
    samples: int
    fidelity: float | None = None
    drift_score: float = 0.0
    window_start: str | None = None

