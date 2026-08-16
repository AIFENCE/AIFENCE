# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Concept(Base):
    __tablename__ = "concepts"
    __table_args__ = (
        UniqueConstraint("codebook", "canonical", name="uq_concept_codebook_canonical"),
        Index("ix_concepts_codebook_count", "codebook", "seen_count"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codebook: Mapped[str] = mapped_column(String(128), index=True)
    canonical: Mapped[str] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(Text, default="")
    embedding_space: Mapped[str] = mapped_column(String(256), default="hash:v1:96", index=True)
    vector: Mapped[list[float]] = mapped_column(JSON, default=list)
    lsh_bucket: Mapped[str] = mapped_column(String(32), default="", index=True)
    seen_count: Mapped[int] = mapped_column(Integer, default=1)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[str] = mapped_column(String(32), default="active")
    version: Mapped[int] = mapped_column(Integer, default=1)
    semantic_hash: Mapped[str] = mapped_column(String(64), default="")
    replacement_id: Mapped[int | None] = mapped_column(ForeignKey("concepts.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    @property
    def code(self) -> str:
        return f"C{self.id:08X}"


class ConceptAlias(Base):
    __tablename__ = "concept_aliases"
    __table_args__ = (UniqueConstraint("codebook", "alias", name="uq_concept_alias"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codebook: Mapped[str] = mapped_column(String(128), index=True)
    alias: Mapped[str] = mapped_column(String(512))
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (UniqueConstraint("codebook", "canonical", name="uq_candidate_cb_canonical"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codebook: Mapped[str] = mapped_column(String(128), index=True)
    canonical: Mapped[str] = mapped_column(String(512))
    seen_count: Mapped[int] = mapped_column(Integer, default=1)
    estimated_savings_bytes: Mapped[int] = mapped_column(Integer, default=0)
    max_neighbor_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class PatternCandidate(Base):
    __tablename__ = "pattern_candidates"
    __table_args__ = (
        UniqueConstraint("codebook", "signature", name="uq_pattern_candidate_signature"),
        Index("ix_pattern_candidate_rank", "codebook", "occurrence_count", "estimated_savings_bytes"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codebook: Mapped[str] = mapped_column(String(128), index=True)
    signature: Mapped[str] = mapped_column(String(64), index=True)
    canonical: Mapped[str] = mapped_column(Text)
    composition: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    relation_structure: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    estimated_savings_bytes: Mapped[int] = mapped_column(Integer, default=0)
    semantic_variance: Mapped[float] = mapped_column(Float, default=0.0)
    slot_samples: Mapped[list[str]] = mapped_column(JSON, default=list)
    trust_scope: Mapped[str] = mapped_column(String(32), default="session", index=True)
    source_diversity: Mapped[int] = mapped_column(Integer, default=0)
    dominant_source_share: Mapped[float] = mapped_column(Float, default=1.0)
    trust_score: Mapped[float] = mapped_column(Float, default=0.0)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class PatternSourceEvidence(Base):
    __tablename__ = "pattern_source_evidence"
    __table_args__ = (
        UniqueConstraint("codebook", "signature", "source_hash", name="uq_pattern_source_evidence"),
        Index("ix_pattern_source_signature", "codebook", "signature"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codebook: Mapped[str] = mapped_column(String(128), index=True)
    signature: Mapped[str] = mapped_column(String(64), index=True)
    source_hash: Mapped[str] = mapped_column(String(64), index=True)
    trust_score: Mapped[float] = mapped_column(Float, default=0.5)
    observation_count: Mapped[int] = mapped_column(Integer, default=1)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class LearnedPattern(Base):
    __tablename__ = "learned_patterns"
    __table_args__ = (
        UniqueConstraint("codebook", "signature", name="uq_learned_pattern_signature"),
        UniqueConstraint("concept_id", name="uq_learned_pattern_concept"),
        Index("ix_learned_pattern_status", "codebook", "status", "occurrence_count"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codebook: Mapped[str] = mapped_column(String(128), index=True)
    signature: Mapped[str] = mapped_column(String(64), index=True)
    canonical: Mapped[str] = mapped_column(Text)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), index=True)
    composition: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    relation_structure: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    embedding_space: Mapped[str] = mapped_column(String(256), default="hash:v1:96", index=True)
    vector: Mapped[list[float]] = mapped_column(JSON, default=list)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    estimated_savings_bytes: Mapped[int] = mapped_column(Integer, default=0)
    semantic_variance: Mapped[float] = mapped_column(Float, default=0.0)
    slot_samples: Mapped[list[str]] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[str] = mapped_column(String(32), default="shadow", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    shadow_samples: Mapped[int] = mapped_column(Integer, default=0)
    shadow_success_sum: Mapped[float] = mapped_column(Float, default=0.0)
    task_success_count: Mapped[int] = mapped_column(Integer, default=0)
    task_success_sum: Mapped[float] = mapped_column(Float, default=0.0)
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    utility_score: Mapped[float] = mapped_column(Float, default=0.0)
    ambiguity_score: Mapped[float] = mapped_column(Float, default=0.0)
    interoperability_score: Mapped[float] = mapped_column(Float, default=1.0)
    calibrated_reliability: Mapped[float] = mapped_column(Float, default=1.0)
    trust_scope: Mapped[str] = mapped_column(String(32), default="session", index=True)
    source_diversity: Mapped[int] = mapped_column(Integer, default=0)
    dominant_source_share: Mapped[float] = mapped_column(Float, default=1.0)
    trust_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cooling_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    @property
    def pattern_id(self) -> str:
        return f"G{self.id:08X}"

    @property
    def task_utility(self) -> float | None:
        if self.task_success_count <= 0:
            return None
        return self.task_success_sum / self.task_success_count

    @property
    def shadow_success_rate(self) -> float | None:
        if self.shadow_samples <= 0:
            return None
        return self.shadow_success_sum / self.shadow_samples


class CalibrationBucket(Base):
    __tablename__ = "calibration_buckets"
    __table_args__ = (
        UniqueConstraint("workspace", "receiver", "model", "task_family", "bucket", name="uq_calibration_bucket"),
        Index("ix_calibration_lookup", "workspace", "receiver", "model", "task_family"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    receiver: Mapped[str] = mapped_column(String(128), default="*", index=True)
    model: Mapped[str] = mapped_column(String(256), default="*", index=True)
    task_family: Mapped[str] = mapped_column(String(128), default="*", index=True)
    bucket: Mapped[int] = mapped_column(Integer)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    predicted_sum: Mapped[float] = mapped_column(Float, default=0.0)
    observed_sum: Mapped[float] = mapped_column(Float, default=0.0)
    squared_error_sum: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Reference(Base):
    __tablename__ = "references"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    media_type: Mapped[str] = mapped_column(String(128), default="application/json")
    payload: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    byte_size: Mapped[int] = mapped_column(Integer)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    owner: Mapped[str | None] = mapped_column(String(128), nullable=True)
    acl: Mapped[list[str]] = mapped_column(JSON, default=list)
    tier: Mapped[str] = mapped_column(String(16), default="warm", index=True)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SharedState(Base):
    __tablename__ = "shared_states"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    payload: Mapped[Any] = mapped_column(JSON)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("shared_states.id"), nullable=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    created_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ReceiverKnowledge(Base):
    __tablename__ = "receiver_knowledge"
    __table_args__ = (UniqueConstraint("workspace", "receiver", name="uq_receiver_knowledge"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    receiver: Mapped[str] = mapped_column(String(128), index=True)
    current_state: Mapped[str | None] = mapped_column(String(80), nullable=True)
    capabilities: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ReceiverKnowledgeItem(Base):
    __tablename__ = "receiver_knowledge_items"
    __table_args__ = (
        UniqueConstraint("workspace", "receiver", "kind", "value", name="uq_receiver_knowledge_item"),
        Index("ix_receiver_item_lookup", "workspace", "receiver", "kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    receiver: Mapped[str] = mapped_column(String(128), index=True)
    kind: Mapped[str] = mapped_column(String(16), index=True)
    value: Mapped[str] = mapped_column(String(128), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    stale_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SemanticCache(Base):
    __tablename__ = "semantic_cache"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    packet: Mapped[dict[str, Any]] = mapped_column(JSON)
    decisions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    codebook_fingerprint: Mapped[str] = mapped_column(String(64), default="")
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MessageAudit(Base):
    __tablename__ = "message_audit"
    __table_args__ = (
        Index("ix_message_sender_receiver", "sender", "receiver"),
        Index("ix_message_run_created", "run_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    packet_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    run_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    sender: Mapped[str | None] = mapped_column(String(128), nullable=True)
    receiver: Mapped[str | None] = mapped_column(String(128), nullable=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    strategy: Mapped[str] = mapped_column(String(64), default="semantic")
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    input_bytes: Mapped[int] = mapped_column(Integer)
    output_bytes: Mapped[int] = mapped_column(Integer)
    estimated_tokens: Mapped[int] = mapped_column(Integer, default=0)
    budget_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    atom_count: Mapped[int] = mapped_column(Integer)
    ref_count: Mapped[int] = mapped_column(Integer)
    packet: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    decisions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    task_success: Mapped[float | None] = mapped_column(Float, nullable=True)
    semantic_loss_score: Mapped[float] = mapped_column(Float, default=0.0)
    original_token_estimate: Mapped[int] = mapped_column(Integer, default=0)
    receiver_known_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    pattern_count: Mapped[int] = mapped_column(Integer, default=0)
    ref_bytes_avoided: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class BusMessage(Base):
    __tablename__ = "bus_messages"
    __table_args__ = (
        Index("ix_bus_receiver_status_priority", "workspace", "receiver", "status", "priority"),
        Index("ix_bus_partition_order", "workspace", "partition_key", "ordering_key", "sequence_no"),
        Index("ix_bus_run_created", "run_id", "created_at"),
        UniqueConstraint("workspace", "idempotency_key", name="uq_bus_idempotency"),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    packet_id: Mapped[str] = mapped_column(String(64), index=True)
    sender: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    receiver: Mapped[str] = mapped_column(String(128), index=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    run_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    partition_key: Mapped[str] = mapped_column(String(128), default="default", index=True)
    ordering_key: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    sequence_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    wire: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    strategy: Mapped[str] = mapped_column(String(64), default="semantic")
    estimated_tokens: Mapped[int] = mapped_column(Integer, default=0)
    wire_bytes: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class PatternEdge(Base):
    __tablename__ = "pattern_edges"
    __table_args__ = (
        UniqueConstraint("parent_pattern_id", "child_pattern_id", "position", name="uq_pattern_edge"),
        Index("ix_pattern_edge_parent", "parent_pattern_id", "position"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_pattern_id: Mapped[int] = mapped_column(ForeignKey("learned_patterns.id"), index=True)
    child_pattern_id: Mapped[int] = mapped_column(ForeignKey("learned_patterns.id"), index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PatternReceiverMetric(Base):
    __tablename__ = "pattern_receiver_metrics"
    __table_args__ = (
        UniqueConstraint("pattern_id", "workspace", "receiver", "model", name="uq_pattern_receiver_metric"),
        Index("ix_pattern_receiver_lookup", "workspace", "receiver", "model"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern_id: Mapped[int] = mapped_column(ForeignKey("learned_patterns.id"), index=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    receiver: Mapped[str] = mapped_column(String(128), default="*", index=True)
    model: Mapped[str] = mapped_column(String(256), default="*", index=True)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    full_success_sum: Mapped[float] = mapped_column(Float, default=0.0)
    compressed_success_sum: Mapped[float] = mapped_column(Float, default=0.0)
    fidelity_sum: Mapped[float] = mapped_column(Float, default=0.0)
    exact_equivalence_count: Mapped[int] = mapped_column(Integer, default=0)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ReferenceGrant(Base):
    __tablename__ = "reference_grants"
    __table_args__ = (
        UniqueConstraint("ref_id", "workspace", "owner", name="uq_reference_grant_owner"),
        Index("ix_reference_grant_lookup", "workspace", "ref_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ref_id: Mapped[str] = mapped_column(ForeignKey("references.id"), index=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    owner: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    acl: Mapped[list[str]] = mapped_column(JSON, default=list)
    allowed_paths: Mapped[list[str]] = mapped_column(JSON, default=list)
    tier: Mapped[str] = mapped_column(String(16), default="warm", index=True)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    sensitivity: Mapped[list[str]] = mapped_column(JSON, default=list)
    version: Mapped[int] = mapped_column(Integer, default=1)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SemanticFact(Base):
    __tablename__ = "semantic_facts"
    __table_args__ = (
        Index("ix_fact_subject_predicate", "workspace", "subject", "predicate", "status"),
        Index("ix_fact_source", "workspace", "source"),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    subject: Mapped[str] = mapped_column(String(256), index=True)
    predicate: Mapped[str] = mapped_column(String(256), index=True)
    object: Mapped[Any] = mapped_column(JSON)
    epistemic_type: Mapped[str] = mapped_column(String(32), default="fact", index=True)
    source: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    sensitivity: Mapped[list[str]] = mapped_column(JSON, default=list)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class FactDependency(Base):
    __tablename__ = "fact_dependencies"
    __table_args__ = (
        UniqueConstraint("parent_fact_id", "child_fact_id", name="uq_fact_dependency"),
        Index("ix_fact_dependency_parent", "parent_fact_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_fact_id: Mapped[str] = mapped_column(ForeignKey("semantic_facts.id"), index=True)
    child_fact_id: Mapped[str] = mapped_column(ForeignKey("semantic_facts.id"), index=True)
    relation: Mapped[str] = mapped_column(String(64), default="derived_from")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Contradiction(Base):
    __tablename__ = "contradictions"
    __table_args__ = (
        UniqueConstraint("left_fact_id", "right_fact_id", name="uq_contradiction_pair"),
        Index("ix_contradiction_status", "workspace", "status"),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    left_fact_id: Mapped[str] = mapped_column(ForeignKey("semantic_facts.id"), index=True)
    right_fact_id: Mapped[str] = mapped_column(ForeignKey("semantic_facts.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="open", index=True)
    resolution: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        Index("ix_subscription_workspace_agent", "workspace", "agent", "active"),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    agent: Mapped[str] = mapped_column(String(128), index=True)
    concepts: Mapped[list[str]] = mapped_column(JSON, default=list)
    filters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    min_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AgentCapability(Base):
    __tablename__ = "agent_capabilities"
    __table_args__ = (
        UniqueConstraint("workspace", "agent", name="uq_agent_capability"),
        Index("ix_agent_capability_available", "workspace", "available"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    agent: Mapped[str] = mapped_column(String(128), index=True)
    capabilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    authority: Mapped[list[str]] = mapped_column(JSON, default=list)
    cost_score: Mapped[float] = mapped_column(Float, default=1.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    details: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class FederationPeer(Base):
    __tablename__ = "federation_peers"
    __table_args__ = (UniqueConstraint("workspace", "name", name="uq_federation_peer"),)

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    base_url: Mapped[str] = mapped_column(String(2048))
    public_key_b64: Mapped[str] = mapped_column(Text, default="")
    allowed_namespaces: Mapped[list[str]] = mapped_column(JSON, default=list)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    details: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class ModelIdentity(Base):
    __tablename__ = "model_identities"
    __table_args__ = (
        UniqueConstraint("workspace", "receiver", "identity_hash", name="uq_model_identity"),
        Index("ix_model_identity_active", "workspace", "receiver", "active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    receiver: Mapped[str] = mapped_column(String(128), index=True)
    provider: Mapped[str] = mapped_column(String(128), default="unknown")
    model: Mapped[str] = mapped_column(String(256), default="unknown")
    model_version: Mapped[str] = mapped_column(String(128), default="unknown")
    runtime: Mapped[str] = mapped_column(String(128), default="unknown")
    runtime_version: Mapped[str] = mapped_column(String(128), default="unknown")
    config_hash: Mapped[str] = mapped_column(String(64), default="")
    identity_hash: Mapped[str] = mapped_column(String(64), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PatternValidationEvidence(Base):
    __tablename__ = "pattern_validation_evidence"
    __table_args__ = (
        Index("ix_pattern_validation_pattern_split", "pattern_id", "split", "created_at"),
        Index("ix_pattern_validation_receiver_model", "workspace", "receiver", "model_identity_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern_id: Mapped[int] = mapped_column(ForeignKey("learned_patterns.id"), index=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    split: Mapped[str] = mapped_column(String(16), default="holdout", index=True)
    receiver: Mapped[str] = mapped_column(String(128), default="*", index=True)
    model_identity_hash: Mapped[str] = mapped_column(String(64), default="*", index=True)
    task_family: Mapped[str] = mapped_column(String(128), default="*", index=True)
    full_success: Mapped[float] = mapped_column(Float, default=0.0)
    compressed_success: Mapped[float] = mapped_column(Float, default=0.0)
    fidelity: Mapped[float] = mapped_column(Float, default=0.0)
    source_hash: Mapped[str] = mapped_column(String(64), default="", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ReliabilityWindow(Base):
    __tablename__ = "reliability_windows"
    __table_args__ = (
        UniqueConstraint("workspace", "receiver", "model_identity_hash", "pattern_id", "task_family", "window_start", name="uq_reliability_window"),
        Index("ix_reliability_drift", "workspace", "receiver", "model_identity_hash", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    receiver: Mapped[str] = mapped_column(String(128), index=True)
    model_identity_hash: Mapped[str] = mapped_column(String(64), index=True)
    pattern_id: Mapped[int | None] = mapped_column(ForeignKey("learned_patterns.id"), nullable=True, index=True)
    task_family: Mapped[str] = mapped_column(String(128), default="*", index=True)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    fidelity_sum: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(16), default="stable", index=True)
    drift_score: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class CodebookRelease(Base):
    __tablename__ = "codebook_releases"
    __table_args__ = (
        UniqueConstraint("namespace", "release", name="uq_codebook_release"),
        Index("ix_codebook_release_active", "namespace", "status", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    namespace: Mapped[str] = mapped_column(String(128), index=True)
    release: Mapped[str] = mapped_column(String(128), index=True)
    merkle_root: Mapped[str] = mapped_column(String(64), index=True)
    manifest: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    key_id: Mapped[str] = mapped_column(String(128), default="")
    signature: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class StateCheckpoint(Base):
    __tablename__ = "state_checkpoints"
    __table_args__ = (
        UniqueConstraint("workspace", "state_id", name="uq_state_checkpoint_state"),
        Index("ix_state_checkpoint_workspace_created", "workspace", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    state_id: Mapped[str] = mapped_column(ForeignKey("shared_states.id"), index=True)
    revision: Mapped[int] = mapped_column(Integer)
    payload_hash: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("workspace", "operation", "key", name="uq_idempotency_record"),
        Index("ix_idempotency_expiry", "expires_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    operation: Mapped[str] = mapped_column(String(128), index=True)
    key: Mapped[str] = mapped_column(String(128), index=True)
    request_hash: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)


class QuotaCounter(Base):
    __tablename__ = "quota_counters"
    __table_args__ = (
        UniqueConstraint("workspace", "resource", "window_start", name="uq_quota_counter"),
        Index("ix_quota_workspace_resource", "workspace", "resource", "window_start"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    resource: Mapped[str] = mapped_column(String(64), index=True)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class OrderingCounter(Base):
    __tablename__ = "ordering_counters"
    __table_args__ = (UniqueConstraint("workspace", "ordering_key", name="uq_ordering_counter"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    ordering_key: Mapped[str] = mapped_column(String(128), index=True)
    sequence_no: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class InformationFlowLabel(Base):
    __tablename__ = "information_flow_labels"
    __table_args__ = (
        UniqueConstraint("workspace", "object_kind", "object_id", "label", name="uq_information_flow_label"),
        Index("ix_information_flow_object", "workspace", "object_kind", "object_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace: Mapped[str] = mapped_column(String(128), default="default", index=True)
    object_kind: Mapped[str] = mapped_column(String(32), index=True)
    object_id: Mapped[str] = mapped_column(String(128), index=True)
    label: Mapped[str] = mapped_column(String(64), index=True)
    source_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

