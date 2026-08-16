# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field

from .protocol_spec import SAGE_PROTOCOL
from .schemas import Atom, Capabilities, Provenance, TraceContext


class SpecModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProtocolPacket(SpecModel):
    v: Literal["sage/0.2"] = cast(Literal["sage/0.2"], SAGE_PROTOCOL)
    id: str | None = None
    cb: str
    sender: str | None = None
    receiver: str | None = None
    act: str = "report"
    atoms: list[Atom] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)
    base: str | None = None
    delta: list[dict[str, Any]] | None = None
    prov: Provenance = Field(default_factory=Provenance)
    meta: dict[str, Any] = Field(default_factory=dict)
    signature: dict[str, Any] | None = None
    trace: TraceContext | None = None


class ProtocolRef(SpecModel):
    ref: str
    media_type: str = "application/json"
    byte_size: int = Field(ge=0)
    digest: str
    tier: Literal["hot", "warm", "cold"] = "warm"
    expires_at: str | None = None
    provenance: Provenance = Field(default_factory=Provenance)


class ProtocolState(SpecModel):
    state: str
    revision: int = Field(ge=1)
    parent: str | None = None
    value_digest: str
    provenance: Provenance = Field(default_factory=Provenance)


class ProtocolDeltaOp(SpecModel):
    op: Literal["add", "remove", "replace"]
    path: str
    value: Any | None = None


class ProtocolDelta(SpecModel):
    base: str
    target: str | None = None
    ops: list[ProtocolDeltaOp]


class ProtocolConcept(SpecModel):
    code: str
    version: int = Field(ge=1)
    codebook: str
    canonical: str
    description: str = ""
    status: Literal["candidate", "shadow", "validated", "active", "cooling", "deprecated", "retired"] = "active"
    replacement_code: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ProtocolPattern(SpecModel):
    pattern_id: str
    concept_code: str
    concept_version: int = Field(ge=1)
    version: int = Field(ge=1)
    codebook: str
    signature: str
    canonical: str
    composition: list[dict[str, Any]]
    relation_structure: dict[str, Any] = Field(default_factory=dict)
    status: Literal["shadow", "validated", "active", "cooling", "deprecated", "retired"] = "shadow"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    occurrence_count: int = Field(default=0, ge=0)
    estimated_savings_bytes: int = Field(default=0, ge=0)
    semantic_variance: float = Field(default=0.0, ge=0.0, le=1.0)
    shadow_samples: int = Field(default=0, ge=0)
    shadow_success_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    task_utility: float | None = None
    utility_score: float = 0.0
    ambiguity_score: float = Field(default=0.0, ge=0.0)
    interoperability_score: float = Field(default=1.0, ge=0.0, le=1.0)
    calibrated_reliability: float = Field(default=1.0, ge=0.0, le=1.0)
    trust_scope: Literal["session", "project", "workspace", "domain", "federation"] = "session"
    source_diversity: int = Field(default=0, ge=0)
    dominant_source_share: float = Field(default=1.0, ge=0.0, le=1.0)
    trust_score: float = Field(default=0.0, ge=0.0, le=1.0)
    use_count: int = Field(default=0, ge=0)
    last_used_at: str | None = None
    children: list[str] = Field(default_factory=list)



class ProtocolCapability(SpecModel):
    protocol: Literal["sage/0.2"] = cast(Literal["sage/0.2"], SAGE_PROTOCOL)
    capabilities: Capabilities = Field(default_factory=Capabilities)
    codebook_fingerprints: dict[str, str] = Field(default_factory=dict)


class ProtocolAck(SpecModel):
    message_id: str
    packet_id: str
    receiver: str
    workspace: str = "default"
    status: Literal["acked", "nacked"]
    observed_at: str


class ProtocolError(SpecModel):
    code: str
    message: str
    retryable: bool = False
    packet_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


SPEC_MODELS: dict[str, type[BaseModel]] = {
    "packet": ProtocolPacket,
    "ref": ProtocolRef,
    "state": ProtocolState,
    "delta": ProtocolDelta,
    "concept": ProtocolConcept,
    "pattern": ProtocolPattern,
    "capability": ProtocolCapability,
    "provenance": Provenance,
    "ack": ProtocolAck,
    "error": ProtocolError,
}
