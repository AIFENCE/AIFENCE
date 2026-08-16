# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import base64
import math
import uuid
from typing import Any, cast

from sqlalchemy.orm import Session

from . import context_accounting
from .cache import CacheStore, cache_key
from .codebook import Codebook
from .compiler import compile_content
from .config import Settings
from .db_models import Concept, MessageAudit
from .knowledge import KnowledgeStore
from .patterns import PatternStore
from .references import ReferenceAccessError, ReferenceExpiredError, ReferenceStore, canonical_bytes
from .reliability import ModelIdentityStore
from .schemas import (
    Atom,
    DecodeResponse,
    EncodeRequest,
    EncodeResponse,
    FallbackMode,
    Packet,
    Provenance,
)
from .semantic_safety import assess_unit
from .signing import sign_wire
from .state import StateStore, apply_patch, diff
from .telemetry import Telemetry
from .wire_codec import WireCodec


class SageCodec:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.codebook = Codebook(db, settings)
        self.patterns = PatternStore(db, settings, self.codebook)
        self.refs = ReferenceStore(db, settings)
        self.states = StateStore(db, settings)
        self.knowledge = KnowledgeStore(db)
        self.cache = CacheStore(db, settings.semantic_cache_ttl_seconds)
        self.telemetry = Telemetry(settings)
        self.wire_codec = WireCodec(settings)
        self.accounting = context_accounting.collector(False)
        self._report_history = context_accounting.ContextReportHistory()

    def _budget_bytes(self, request: EncodeRequest) -> tuple[int, int | None]:
        token_budget = request.budget.max_tokens if request.budget and request.budget.max_tokens else self.settings.default_token_budget
        byte_budget = min(self.settings.max_packet_bytes, int(token_budget * self.settings.chars_per_token_estimate))
        if request.budget and request.budget.max_bytes:
            byte_budget = min(byte_budget, request.budget.max_bytes)
        return byte_budget, token_budget

    def _provenance(self, request: EncodeRequest) -> Provenance:
        if request.provenance is not None:
            prov = request.provenance.model_copy(deep=True)
            if prov.producer is None:
                prov.producer = request.sender
            return prov
        return Provenance(producer=request.sender, derivation="direct")

    def _wire(self, packet: Packet) -> tuple[str, bytes]:
        return self.wire_codec.wire(packet)

    def _packet_id(self) -> str:
        return "P" + uuid.uuid4().hex

    def _begin_accounting(self) -> context_accounting.ContextAccounting:
        """Start a fresh per-exchange recorder (shared no-op when disabled).

        The recorder is call-local: it is deliberately NOT stored on the
        instance, so overlapping encode/decode calls on a shared codec
        cannot clobber each other's accounting. Completed reports are
        published thread-safely via ``_publish_report``.
        """
        return context_accounting.collector(self.settings.context_accounting_enabled)

    def _publish_report(self, report: context_accounting.ContextReport) -> None:
        """Thread-safely publish a completed exchange's report snapshot."""
        self._report_history.publish(report)

    def context_report(self) -> context_accounting.ContextReport | None:
        """Snapshot of the most recently COMPLETED exchange, or None when
        accounting is disabled or no exchange has completed yet."""
        return self._report_history.most_recent()

    def context_reports(self, limit: int = 10) -> list[context_accounting.ContextReport]:
        """The last ``limit`` completed per-exchange reports, most recent first.

        Empty when accounting is disabled. Each entry is an immutable
        snapshot, so overlapping encode/decode calls cannot clobber or
        corrupt a completed report.
        """
        return self._report_history.recent(limit)

    def compact(self, packet: Packet) -> dict[str, Any]:
        return self.wire_codec.compact(packet)

    def expand(self, payload: dict[str, Any]) -> Packet:
        return self.wire_codec.expand(payload)

    def _semantic_packet(self, request: EncodeRequest, codebook_name: str, provenance: Provenance, decisions: list[dict[str, Any]], *, allow_patterns: bool = True) -> Packet:
        packet = Packet(
            cb=codebook_name,
            sender=request.sender,
            receiver=request.receiver,
            act=request.act,
            prov=provenance,
            trace=request.trace,
        )
        units = compile_content(request.content)
        bounded_units = units[: self.settings.max_message_atoms]

        if request.auto_learn and request.record_learning:
            sources = [request.sender] if request.sender else []
            try:
                promoted = self.patterns.observe_units(
                    codebook_name,
                    bounded_units,
                    source_ids=sources,
                    trust_score=request.source_trust,
                    trust_scope=request.learning_scope,
                    workspace=request.workspace,
                )
            except Exception as exc:
                promoted = []
                decisions.append({"action": "optional_subsystem_fallback", "subsystem": "pattern_learning", "error": type(exc).__name__})
            for pattern in promoted:
                promoted_concept = self.db.get(Concept, pattern.concept_id)
                decisions.append({
                    "action": "pattern_promoted_to_shadow",
                    "pattern_id": pattern.pattern_id,
                    "canonical": pattern.canonical,
                    "concept_code": promoted_concept.code if promoted_concept is not None else None,
                })

        seen_shadow: set[str] = set()
        try:
            shadow_matches = self.patterns.shadow_matches(codebook_name, bounded_units)
        except Exception as exc:
            shadow_matches = []
            decisions.append({"action": "optional_subsystem_fallback", "subsystem": "pattern_shadow", "error": type(exc).__name__})
        for match in shadow_matches:
            if match.pattern.pattern_id in seen_shadow:
                continue
            seen_shadow.add(match.pattern.pattern_id)
            decisions.append({
                "action": "pattern_shadow_match",
                "pattern_id": match.pattern.pattern_id,
                "canonical": match.pattern.canonical,
                "span": [match.start, match.end],
                "estimated_savings_bytes": match.pattern.estimated_savings_bytes,
            })

        try:
            available_active = self.patterns.active_matches(codebook_name, bounded_units, receiver=request.receiver, model=request.receiver_model, workspace=request.workspace, task_family=request.task_family)
        except Exception as exc:
            available_active = []
            decisions.append({"action": "optional_subsystem_fallback", "subsystem": "pattern_matching", "error": type(exc).__name__})
        if allow_patterns:
            active = {match.start: match for match in available_active}
        else:
            active = {}
            if available_active:
                decisions.append({"action": "patterns_disabled_receiver", "reason": "receiver_capability"})

        def append_unit(unit: Any) -> None:
            risk = assess_unit(unit)
            try:
                match = self.codebook.match(codebook_name, unit.canonical, observe=request.record_learning)
                concept = match.concept
            except Exception as exc:
                match = None
                concept = None
                decisions.append({"action": "optional_subsystem_fallback", "subsystem": "semantic_match", "error": type(exc).__name__, "path": unit.path})
            if concept is None and request.auto_learn:
                try:
                    concept = self.codebook.observe_candidate(codebook_name, unit.canonical)
                except Exception as exc:
                    concept = None
                    decisions.append({"action": "optional_subsystem_fallback", "subsystem": "concept_learning", "error": type(exc).__name__, "path": unit.path})
            if concept:
                score = max(match.similarity if match is not None else 0.0, concept.confidence)
                if self.settings.semantic_firewall_enabled and risk.critical and (match.similarity if match is not None else 0.0) < self.settings.critical_semantic_threshold:
                    decisions.append({"action": "semantic_firewall", "path": unit.path, "risk": risk.score, "reasons": list(risk.reasons), "decision": "preserve_literal"})
                    packet.atoms.append(Atom(literal=unit.literal if unit.has_literal else (unit.surface or unit.canonical.replace("_", " ")), has_literal=True, path=unit.path, epistemic_type=risk.epistemic_type))
                    return
                preserve_surface = (
                    not unit.has_literal
                    and unit.surface is not None
                    and (match.similarity if match is not None else 0.0) < self.settings.semantic_lossless_threshold
                )
                decisions.append({
                    "action": "semantic_code",
                    "path": unit.path,
                    "canonical": unit.canonical,
                    "code": concept.code,
                    "version": concept.version,
                    "similarity": round(score, 6),
                    "surface_preserved": preserve_surface,
                })
                packet.atoms.append(
                    Atom(
                        code=concept.code,
                        cv=concept.version,
                        literal=unit.surface if preserve_surface else unit.literal,
                        has_literal=preserve_surface or unit.has_literal,
                        path=unit.path,
                        confidence=score,
                        epistemic_type=risk.epistemic_type,
                    )
                )
            elif unit.has_literal:
                decisions.append({"action": "literal", "path": unit.path, "reason": "task_specific_value"})
                packet.atoms.append(Atom(literal=unit.literal, has_literal=True, path=unit.path, epistemic_type=risk.epistemic_type))
            else:
                literal = (unit.surface or unit.canonical.replace("_", " ")) if request.fallback_mode == "natural_language" else unit.canonical
                decisions.append({
                    "action": "fallback_literal",
                    "path": unit.path,
                    "reason": "unknown_or_ambiguous_concept",
                    "mode": request.fallback_mode,
                })
                packet.atoms.append(Atom(literal=literal, has_literal=True, path=unit.path, epistemic_type=risk.epistemic_type))

        index = 0
        while index < len(bounded_units):
            pattern_match = active.get(index)
            if pattern_match is not None:
                pattern = pattern_match.pattern
                concept = self.db.get(Concept, pattern.concept_id)
                if concept is not None and concept.status == "active":
                    bindings = pattern_match.bindings
                    decisions.append({
                        "action": "pattern_code",
                        "pattern_id": pattern.pattern_id,
                        "canonical": pattern.canonical,
                        "code": concept.code,
                        "version": concept.version,
                        "span": [pattern_match.start, pattern_match.end],
                        "bindings": len(bindings),
                        "estimated_savings_bytes": pattern.estimated_savings_bytes,
                    })
                    try:
                        self.patterns.mark_used(pattern)
                    except Exception as exc:
                        decisions.append({"action": "optional_subsystem_fallback", "subsystem": "pattern_usage", "error": type(exc).__name__})
                    packet.atoms.append(
                        Atom(
                            code=concept.code,
                            cv=concept.version,
                            literal=bindings if bindings else None,
                            has_literal=bool(bindings),
                            path=bounded_units[index].path,
                            confidence=min(pattern.confidence, pattern.calibrated_reliability),
                            epistemic_type="fact",
                        )
                    )
                    index = pattern_match.end
                    continue
            append_unit(bounded_units[index])
            index += 1

        if len(units) > self.settings.max_message_atoms:
            decisions.append({"action": "fallback_reference", "reason": "atom_limit", "units": len(units)})
            packet.atoms = []
        if isinstance(request.content, (dict, list)):
            state = self.states.create(
                request.content,
                workspace=request.workspace,
                created_by=request.sender,
                provenance=provenance.model_dump(),
            )
            packet.meta["state"] = state.id
            packet.meta["revision"] = state.revision
            decisions.append({"action": "state_checkpoint", "state": state.id})
        return packet


    def _reference_packet(self, request: EncodeRequest, codebook_name: str, provenance: Provenance, decisions: list[dict[str, Any]]) -> Packet:
        acl = [request.receiver] if request.receiver else []
        item = self.refs.put(
            request.content,
            workspace=request.workspace,
            owner=request.sender,
            acl=acl,
            tier="hot",
            encrypt=bool(self.settings.ref_encryption_key),
            provenance=provenance.model_dump(),
        )
        grant = self.refs.grant_metadata(item.id, actor=request.sender, workspace=request.workspace)
        decisions.append({"action": "reference", "ref": item.id, "reason": "size_or_budget", "tier": grant.tier})
        meta: dict[str, Any] = {"memory_tier": grant.tier}
        if isinstance(request.content, (dict, list)):
            state = self.states.create(
                request.content,
                workspace=request.workspace,
                created_by=request.sender,
                provenance=provenance.model_dump(),
            )
            meta.update({"state": state.id, "revision": state.revision})
            decisions.append({"action": "state_checkpoint", "state": state.id})
        return Packet(
            cb=codebook_name,
            sender=request.sender,
            receiver=request.receiver,
            act=request.act,
            refs=[item.id],
            prov=provenance,
            meta=meta,
            trace=request.trace,
        )

    def _delta_packet(self, request: EncodeRequest, base_id: str, codebook_name: str, provenance: Provenance, decisions: list[dict[str, Any]]) -> Packet | None:
        base = self.states.get(base_id, workspace=request.workspace)
        if base is None:
            return None
        patch = diff(base.payload, request.content)
        target_state = self.states.create(
            request.content,
            parent_id=base.id,
            workspace=request.workspace,
            created_by=request.sender,
            provenance=provenance.model_dump(),
        )
        decisions.append({"action": "delta", "base": base.id, "state": target_state.id, "operations": len(patch)})
        return Packet(
            cb=codebook_name,
            sender=request.sender,
            receiver=request.receiver,
            act=request.act,
            base=base.id,
            delta=patch,
            prov=provenance,
            meta={"state": target_state.id, "revision": target_state.revision},
            trace=request.trace,
        )

    def encode(self, request: EncodeRequest) -> EncodeResponse:
        codebook_name = request.codebook or self.settings.codebook
        if request.receiver and not request.receiver_model:
            identity = ModelIdentityStore(self.db).active(request.workspace, request.receiver)
            if identity is not None:
                request.receiver_model = identity.identity_hash
        input_raw = canonical_bytes(request.content)
        if len(input_raw) > self.settings.max_input_bytes:
            raise ValueError(f"payload exceeds max_input_bytes={self.settings.max_input_bytes}")
        accounting = self._begin_accounting()
        provenance = self._provenance(request)
        byte_budget, token_budget = self._budget_bytes(request)
        decisions: list[dict[str, Any]] = [
            {"action": "budget", "max_bytes": byte_budget, "max_tokens": token_budget},
            {"action": "provenance", "sources": provenance.source_ids, "confidence": provenance.confidence},
        ]
        knowledge = self.knowledge.get(request.receiver, request.workspace) if request.use_receiver_knowledge else None
        known_codes = set(request.receiver_known_codes)
        if knowledge:
            known_codes.update(self.knowledge.known_codes(request.receiver, request.workspace))
            decisions.append({
                "action": "receiver_model",
                "receiver": request.receiver,
                "known_codes": len(self.knowledge.known_codes(request.receiver, request.workspace)),
                "known_refs": len(self.knowledge.known_refs(request.receiver, request.workspace)),
                "current_state": knowledge.current_state,
            })
        request.receiver_known_codes = known_codes
        if knowledge and knowledge.capabilities:
            cap_bytes = knowledge.capabilities.get("max_packet_bytes")
            if isinstance(cap_bytes, int) and cap_bytes > 0:
                byte_budget = min(byte_budget, cap_bytes)
                decisions[0] = {"action": "budget", "max_bytes": byte_budget, "max_tokens": token_budget}
            fallback_modes = knowledge.capabilities.get("fallback_modes") or []
            if fallback_modes and request.fallback_mode not in fallback_modes:
                request.fallback_mode = cast(FallbackMode, "natural_language" if "natural_language" in fallback_modes else str(fallback_modes[0]))
                decisions.append({"action": "fallback_negotiated", "mode": request.fallback_mode})
        cb_fingerprint = self.codebook.fingerprint(codebook_name)
        if accounting.enabled:
            accounting.record_codebook_fingerprint(cb_fingerprint)
        cache_descriptor = {
            "content": request.content,
            "sender": request.sender,
            "receiver": request.receiver,
            "receiver_model": request.receiver_model,
            "task_family": request.task_family,
            "act": request.act,
            "codebook": codebook_name,
            "base": request.base_state,
            "knowledge": self.knowledge.fingerprint(request.receiver, request.workspace),
            "budget": byte_budget,
            "fallback": request.fallback_mode,
            "workspace": request.workspace,
            "cb": cb_fingerprint,
        }
        key = cache_key(cache_descriptor)
        cache_hit = False
        strategy = "semantic"
        packet: Packet | None = None
        if self.settings.semantic_cache_enabled and request.use_cache:
            try:
                cached = self.cache.get(key, cb_fingerprint)
            except Exception as exc:
                cached = None
                decisions.append({"action": "optional_subsystem_fallback", "subsystem": "semantic_cache_read", "error": type(exc).__name__})
            if cached is not None:
                candidate = Packet.model_validate(cached.packet)
                cache_valid = True
                for ref_id in candidate.refs:
                    try:
                        if self.refs.get(ref_id, actor=request.receiver, workspace=request.workspace) is None:
                            cache_valid = False
                            break
                    except (ReferenceAccessError, ReferenceExpiredError):
                        cache_valid = False
                        break
                if cache_valid:
                    packet = candidate
                    packet.id = None
                    strategy = str(packet.meta.get("strategy", "semantic"))
                    decisions = list(cached.decisions) + [{"action": "semantic_cache_hit", "key": key[:16]}]
                    cache_hit = True
                else:
                    decisions.append({"action": "semantic_cache_bypass", "reason": "stale_or_inaccessible_ref"})

        if packet is None:
            base_id = request.base_state
            caps = knowledge.capabilities if knowledge else {}
            if base_id is None and knowledge and isinstance(request.content, (dict, list)):
                base_id = knowledge.current_state
            supports_deltas = caps.get("supports_deltas", True)
            if base_id and supports_deltas and isinstance(request.content, (dict, list)):
                delta_packet = self._delta_packet(request, base_id, codebook_name, provenance, decisions)
                if delta_packet is not None:
                    delta_json, _ = self._wire(delta_packet)
                    explicit_base = request.base_state is not None
                    if len(delta_json.encode()) <= byte_budget and (explicit_base or len(delta_json.encode()) < len(input_raw)):
                        packet = delta_packet
                        strategy = "delta"
                    else:
                        decisions.append({"action": "reject_delta", "reason": "not_smaller_or_over_budget"})

            if packet is None:
                inline_limit = request.inline_limit or self.settings.max_inline_bytes
                supports_refs = caps.get("supports_refs", True)
                if supports_refs and (len(input_raw) > inline_limit or len(input_raw) > byte_budget):
                    packet = self._reference_packet(request, codebook_name, provenance, decisions)
                    strategy = "reference"
                else:
                    packet = self._semantic_packet(
                        request,
                        codebook_name,
                        provenance,
                        decisions,
                        allow_patterns=request.use_patterns and bool(caps.get("supports_patterns", True)),
                    )
                    strategy = "semantic"
                    semantic_json, _ = self._wire(packet)
                    if (not packet.atoms or len(semantic_json.encode()) > byte_budget) and supports_refs:
                        packet = self._reference_packet(request, codebook_name, provenance, decisions)
                        strategy = "reference"

            cacheable = strategy in {"reference", "delta"} or all(atom.code is not None for atom in packet.atoms)
            if self.settings.semantic_cache_enabled and request.use_cache and cacheable:
                cache_packet = packet.model_dump(exclude_none=True)
                cache_packet.pop("id", None)
                try:
                    self.cache.put(key, cache_packet, decisions, cb_fingerprint)
                except Exception as exc:
                    decisions.append({"action": "optional_subsystem_fallback", "subsystem": "semantic_cache_write", "error": type(exc).__name__})

        packet.id = self._packet_id()
        packet.meta.setdefault("strategy", strategy)
        packet.meta.setdefault("codebook_fingerprint", cb_fingerprint)
        packet.meta.setdefault("receiver_known_code_count", len(known_codes))
        if self.settings.packet_signing_private_key is not None:
            unsigned = self.wire_codec.compact(packet)
            unsigned.pop("g", None)
            packet.signature = sign_wire(unsigned, self.settings.packet_signing_private_key.get_secret_value(), key_id=self.settings.packet_signing_key_id)
            decisions.append({"action": "packet_signed", "key_id": self.settings.packet_signing_key_id})
        json_wire, msgpack_wire = self._wire(packet)
        out_json = len(json_wire.encode())
        out_msgpack = len(msgpack_wire)
        estimated_tokens = math.ceil(out_json / self.settings.chars_per_token_estimate)
        if out_json > byte_budget:
            packet.meta["budget_exceeded"] = True
            decisions.append({"action": "budget_exceeded", "bytes": out_json, "limit": byte_budget, "reason": "lossless_fallback_required"})
            json_wire, msgpack_wire = self._wire(packet)
            out_json, out_msgpack = len(json_wire.encode()), len(msgpack_wire)
            estimated_tokens = math.ceil(out_json / self.settings.chars_per_token_estimate)

        if accounting.enabled:
            accounting.record_exchange(packet.id, strategy)
            accounting.record_wire_bytes(out_json, out_msgpack)
            accounting.record_model_tokens(
                context_accounting.estimate_tokens(json_wire, self.settings.chars_per_token_estimate)
            )
            if strategy in ("reference", "delta") or (strategy == "semantic" and isinstance(request.content, (dict, list))):
                accounting.record_stored_bytes(len(input_raw))
            for decision in decisions:
                if decision.get("action") == "fallback_literal":
                    accounting.record_fallback(str(decision.get("literal") or ""))
                elif decision.get("action") == "pattern_promoted_to_shadow":
                    accounting.record_pattern_definition(str(decision.get("canonical") or ""))

        semantic_loss = max([max(0.0, 1.0 - float(d.get("similarity", 1.0))) for d in decisions if d.get("action") == "semantic_code" and not d.get("surface_preserved") ] or [0.0])
        used_codes = {a.code for a in packet.atoms if a.code}
        known_ratio = (len(used_codes & known_codes) / len(used_codes)) if used_codes else 0.0
        if accounting.enabled and used_codes:
            missing = used_codes - known_codes
            if missing:
                try:
                    for code in sorted(missing):
                        concept = self.codebook.get_by_code(code)
                        if concept is not None and concept.canonical:
                            accounting.record_codebook_definition(code, concept.canonical)
                except Exception:
                    # accounting is additive: never let a definition lookup break encode
                    pass
        pattern_count = sum(1 for d in decisions if d.get("action") == "pattern_code")
        ref_bytes_avoided = len(input_raw) if strategy == "reference" else 0
        audit = MessageAudit(
            packet_id=packet.id,
            run_id=request.run_id,
            sender=request.sender,
            receiver=request.receiver,
            workspace=request.workspace,
            strategy=strategy,
            cache_hit=cache_hit,
            input_bytes=len(input_raw),
            output_bytes=out_msgpack,
            estimated_tokens=estimated_tokens,
            budget_tokens=token_budget,
            atom_count=len(packet.atoms),
            ref_count=len(packet.refs),
            packet=packet.model_dump(exclude_none=True),
            decisions=decisions,
            provenance=provenance.model_dump(),
            semantic_loss_score=semantic_loss,
            original_token_estimate=math.ceil(len(input_raw) / self.settings.chars_per_token_estimate),
            receiver_known_ratio=known_ratio,
            pattern_count=pattern_count,
            ref_bytes_avoided=ref_bytes_avoided,
        )
        self.db.add(audit)
        self.db.commit()
        with self.telemetry.span(
            "encode",
            strategy=strategy,
            sender=request.sender,
            receiver=request.receiver,
            packet_bytes=out_msgpack,
            semantic_loss_score=semantic_loss,
            receiver_known_ratio=known_ratio,
            traceparent=request.trace.traceparent if request.trace else None,
            tracestate=request.trace.tracestate if request.trace else None,
        ):
            self.telemetry.add("packet.bytes", out_msgpack, strategy=strategy)
            self.telemetry.add("original.tokens", audit.original_token_estimate, strategy=strategy)
            self.telemetry.add("sent.tokens", estimated_tokens, strategy=strategy)
            self.telemetry.add("semantic_loss.score", semantic_loss, strategy=strategy)
            self.telemetry.add("receiver_known.ratio", known_ratio, strategy=strategy)
            if pattern_count:
                self.telemetry.add("pattern.count", pattern_count, strategy=strategy)
            if ref_bytes_avoided:
                self.telemetry.add("ref.bytes_avoided", ref_bytes_avoided, strategy=strategy)
        if accounting.enabled:
            self._publish_report(accounting.snapshot())
        return EncodeResponse(
            packet=packet,
            wire_json=json_wire,
            wire_msgpack_b64=base64.b64encode(msgpack_wire).decode(),
            input_bytes=len(input_raw),
            output_bytes_json=out_json,
            output_bytes_msgpack=out_msgpack,
            estimated_tokens=estimated_tokens,
            budget_tokens=token_budget,
            compression_ratio_json=(len(input_raw) / out_json) if out_json else 0.0,
            compression_ratio_msgpack=(len(input_raw) / out_msgpack) if out_msgpack else 0.0,
            strategy=strategy,
            cache_hit=cache_hit,
        )

    def decode(
        self,
        packet: Packet,
        resolve_refs: bool = False,
        *,
        receiver: str | None = None,
        workspace: str = "default",
        acknowledge: bool = False,
    ) -> DecodeResponse:
        accounting = self._begin_accounting()
        if accounting.enabled:
            accounting.record_exchange(packet.id, packet.meta.get("strategy"))
        concepts: list[dict[str, Any]] = []
        literals: list[dict[str, Any]] = []
        for atom in packet.atoms:
            if atom.code:
                concept = self.codebook.get_by_code(atom.code)
                decoded_concept: dict[str, Any] = {
                    "code": atom.code,
                    "version": atom.cv,
                    "canonical": concept.canonical if concept else None,
                    "description": concept.description if concept else None,
                    "literal": atom.literal,
                    "path": atom.path,
                    "confidence": atom.confidence,
                    "status": concept.status if concept else "unknown",
                    "epistemic_type": atom.epistemic_type,
                }
                if concept is not None:
                    pattern = self.patterns.by_concept_id(concept.id)
                    if pattern is not None:
                        decoded_concept["pattern"] = {
                            "pattern_id": pattern.pattern_id,
                            "canonical": pattern.canonical,
                            "status": pattern.status,
                            "version": pattern.version,
                            "composition": pattern.composition,
                            "bindings": atom.literal if atom.has_literal else [],
                        }
                concepts.append(decoded_concept)
                if accounting.enabled:
                    accounting.record_decoding_text(decoded_concept.get("canonical") or "", decoded_concept.get("literal"))
                    if concept is None:
                        accounting.record_fallback(str(atom.code))
            else:
                literals.append({"literal": atom.literal, "path": atom.path, "epistemic_type": atom.epistemic_type})
                if accounting.enabled:
                    accounting.record_decoding_text("", atom.literal)
        references: list[dict[str, Any]] = []
        actor = receiver or packet.receiver
        for ref_id in packet.refs:
            try:
                item = self.refs.get(ref_id, actor=actor, workspace=workspace)
                if accounting.enabled and item is not None:
                    accounting.record_reference_fetch(item.byte_size)
                grant = self.refs.grant_metadata(ref_id, actor=actor, workspace=workspace) if item else None
                references.append({
                    "ref": ref_id,
                    "media_type": item.media_type if item else None,
                    "byte_size": item.byte_size if item else None,
                    "tier": grant.tier if grant else None,
                    "provenance": grant.provenance if grant else None,
                    "value": self.refs.resolve(ref_id, actor=actor, workspace=workspace) if (item and resolve_refs) else None,
                })
            except (ReferenceAccessError, ReferenceExpiredError) as exc:
                references.append({"ref": ref_id, "error": str(exc), "value": None})
        base_payload = None
        resolved_state = None
        if packet.base:
            state = self.states.get(packet.base, workspace=workspace)
            base_payload = state.payload if state else None
            if state is not None and packet.delta is not None:
                resolved_state = apply_patch(state.payload, packet.delta)
        if acknowledge and actor:
            self.knowledge.acknowledge(actor, packet, workspace)
            self.db.commit()
        if accounting.enabled:
            self._publish_report(accounting.snapshot())
        return DecodeResponse(
            act=packet.act,
            concepts=concepts,
            literals=literals,
            references=references,
            provenance=packet.prov,
            base_state=base_payload,
            delta=packet.delta,
            resolved_state=resolved_state,
        )
