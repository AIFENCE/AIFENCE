# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import builtins
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import case, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .calibration import CalibrationStore
from .codebook import Codebook
from .compiler import SemanticUnit
from .config import Settings
from .db_models import (
    Concept,
    LearnedPattern,
    PatternCandidate,
    PatternEdge,
    PatternReceiverMetric,
    PatternSourceEvidence,
)
from .pattern_policy import trust_ready
from .pattern_policy import utility_score as calculate_utility_score
from .pattern_structure import (
    _literal_type,
    _path_shape,
    canonical_label,
    composition_for,
    estimated_savings,
    pattern_signature,
    slot_fingerprint,
)
from .reliability import ReliabilityMonitor
from .resilience import QuotaManager


@dataclass(frozen=True)
class PatternMatch:
    pattern: LearnedPattern
    start: int
    end: int
    bindings: list[Any]


class PatternStore:
    """Persistent higher-order semantic pattern miner and lifecycle manager.

    Patterns are exact templates over compiled semantic units. Constant values are part
    of the template; dynamic values are represented as typed slots. A promoted pattern
    owns an ordinary Concept, so active patterns use the existing SAGE atom/code path.
    """

    def __init__(self, db: Session, settings: Settings, codebook: Codebook | None = None) -> None:
        self.db = db
        self.settings = settings
        self.codebook = codebook or Codebook(db, settings)
        self.calibration = CalibrationStore(db, settings.calibration_buckets, settings.calibration_min_samples)
        self.reliability = ReliabilityMonitor(db, settings)
        self.quotas = QuotaManager(db, settings)

    def _candidate_windows(
        self, units: builtins.list[SemanticUnit]
    ) -> builtins.list[builtins.list[SemanticUnit]]:
        if len(units) < self.settings.pattern_min_components:
            return []
        out: builtins.list[builtins.list[SemanticUnit]] = []
        max_len = min(self.settings.pattern_max_components, len(units))
        for size in range(max_len, self.settings.pattern_min_components - 1, -1):
            for start in range(0, len(units) - size + 1):
                out.append(units[start : start + size])
                if len(out) >= self.settings.pattern_max_observations_per_message:
                    return out
        return out

    def observe_units(
        self,
        codebook: str,
        units: builtins.list[SemanticUnit],
        *,
        source_ids: builtins.list[str] | None = None,
        trust_score: float = 0.5,
        trust_scope: str | None = None,
        workspace: str = "default",
    ) -> builtins.list[LearnedPattern]:
        if not self.settings.pattern_learning_enabled:
            return []
        promoted: builtins.list[LearnedPattern] = []
        seen_signatures: set[str] = set()
        for window in self._candidate_windows(units):
            composition = composition_for(
                window,
                allow_string_constants=self.settings.pattern_string_constants_enabled,
            )
            signature = pattern_signature(composition)
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            item = self.observe(
                codebook,
                composition,
                slot_fingerprint(window, composition),
                source_ids=source_ids,
                trust_score=trust_score,
                trust_scope=trust_scope,
                workspace=workspace,
            )
            if item is not None:
                promoted.append(item)
        if self.settings.pattern_recursive_learning_enabled:
            recursive = self._observe_recursive(
                codebook, units, source_ids=source_ids, trust_score=trust_score, trust_scope=trust_scope, workspace=workspace
            )
            if recursive is not None:
                promoted.append(recursive)
        return promoted

    def _observe_recursive(
        self,
        codebook: str,
        units: builtins.list[SemanticUnit],
        *,
        source_ids: builtins.list[str] | None = None,
        trust_score: float = 0.5,
        trust_scope: str | None = None,
        workspace: str = "default",
    ) -> LearnedPattern | None:
        matches = self.active_matches(codebook, units)
        if len(matches) < 2:
            return None
        matches = sorted(matches, key=lambda m: m.start)
        for left, right in zip(matches, matches[1:], strict=False):
            if left.end != right.start:
                continue
            span = units[left.start:right.end]
            composition = composition_for(span, allow_string_constants=self.settings.pattern_string_constants_enabled)
            children = [left.pattern.pattern_id, right.pattern.pattern_id]
            raw = json.dumps({"composition": composition, "children": children}, sort_keys=True, separators=(",", ":")).encode()
            signature = hashlib.sha256(raw).hexdigest()
            return self.observe(
                codebook, composition, slot_fingerprint(span, composition),
                relation_structure={"paths": [item.get("path") for item in composition], "children": children, "recursive": True},
                signature_override=signature,
                source_ids=source_ids,
                trust_score=trust_score,
                trust_scope=trust_scope,
                workspace=workspace,
            )
        return None

    @staticmethod
    def _source_hash(source_id: str) -> str:
        return hashlib.sha256(source_id.encode("utf-8")).hexdigest()

    def _record_source_evidence(
        self,
        codebook: str,
        signature: str,
        source_ids: builtins.list[str] | None,
        trust_score: float,
    ) -> tuple[int, float, float]:
        unique_sources = sorted({item.strip() for item in (source_ids or []) if item and item.strip()})
        if not unique_sources:
            unique_sources = ["anonymous"]
        trust_score = max(0.0, min(1.0, trust_score))
        dialect = self.db.get_bind().dialect.name
        table: Any = PatternSourceEvidence.__table__
        for source_id in unique_sources:
            source_hash = self._source_hash(source_id)
            values = {
                "codebook": codebook,
                "signature": signature,
                "source_hash": source_hash,
                "trust_score": trust_score,
                "observation_count": 1,
            }
            if dialect == "postgresql":
                from sqlalchemy.dialects.postgresql import insert as pg_insert

                pg_stmt = pg_insert(table).values(**values)
                pg_stmt = pg_stmt.on_conflict_do_update(
                    constraint="uq_pattern_source_evidence",
                    set_={
                        "observation_count": table.c.observation_count + 1,
                        "trust_score": case(
                            (
                                pg_stmt.excluded.trust_score > table.c.trust_score,
                                pg_stmt.excluded.trust_score,
                            ),
                            else_=table.c.trust_score,
                        ),
                    },
                )
                self.db.execute(pg_stmt)
            elif dialect == "sqlite":
                from sqlalchemy.dialects.sqlite import insert as sqlite_insert

                sqlite_stmt = sqlite_insert(table).values(**values)
                sqlite_stmt = sqlite_stmt.on_conflict_do_update(
                    index_elements=[table.c.codebook, table.c.signature, table.c.source_hash],
                    set_={
                        "observation_count": table.c.observation_count + 1,
                        "trust_score": case(
                            (
                                sqlite_stmt.excluded.trust_score > table.c.trust_score,
                                sqlite_stmt.excluded.trust_score,
                            ),
                            else_=table.c.trust_score,
                        ),
                    },
                )
                self.db.execute(sqlite_stmt)
            else:
                item = self.db.scalar(
                    select(PatternSourceEvidence).where(
                        PatternSourceEvidence.codebook == codebook,
                        PatternSourceEvidence.signature == signature,
                        PatternSourceEvidence.source_hash == source_hash,
                    )
                )
                if item is None:
                    item = PatternSourceEvidence(**values)
                    try:
                        with self.db.begin_nested():
                            self.db.add(item)
                            self.db.flush()
                    except IntegrityError:
                        item = self.db.scalar(
                            select(PatternSourceEvidence).where(
                                PatternSourceEvidence.codebook == codebook,
                                PatternSourceEvidence.signature == signature,
                                PatternSourceEvidence.source_hash == source_hash,
                            )
                        )
                        if item is None:
                            raise
                        item.observation_count += 1
                        item.trust_score = max(item.trust_score, trust_score)
                else:
                    item.observation_count += 1
                    item.trust_score = max(item.trust_score, trust_score)
        self.db.flush()
        rows = list(
            self.db.scalars(
                select(PatternSourceEvidence).where(
                    PatternSourceEvidence.codebook == codebook,
                    PatternSourceEvidence.signature == signature,
                )
            )
        )
        total = sum(row.observation_count for row in rows)
        dominant = max((row.observation_count for row in rows), default=0) / max(1, total)
        weighted_trust = (
            sum(row.trust_score * row.observation_count for row in rows) / total if total else 0.0
        )
        return len(rows), dominant, weighted_trust

    def _trust_ready(self, diversity: int, dominant_share: float, trust_score: float, scope: str = "session") -> bool:
        return trust_ready(self.settings, diversity, dominant_share, trust_score, scope)

    def observe(
        self,
        codebook: str,
        composition: builtins.list[dict[str, Any]],
        slot_sample: str | None = None,
        *,
        relation_structure: dict[str, Any] | None = None,
        signature_override: str | None = None,
        source_ids: builtins.list[str] | None = None,
        trust_score: float = 0.5,
        trust_scope: str | None = None,
        workspace: str = "default",
    ) -> LearnedPattern | None:
        if len(composition) < self.settings.pattern_min_components:
            return None
        self.quotas.consume(workspace, "pattern_observation", 1)
        signature = signature_override or pattern_signature(composition)
        scope = trust_scope or self.settings.pattern_default_trust_scope
        diversity, dominant_share, weighted_trust = self._record_source_evidence(
            codebook, signature, source_ids, trust_score
        )
        existing = self.db.scalar(
            select(LearnedPattern).where(
                LearnedPattern.codebook == codebook,
                LearnedPattern.signature == signature,
            )
        )
        if existing is not None:
            existing.occurrence_count += 1
            if slot_sample and slot_sample not in existing.slot_samples:
                existing.slot_samples = (list(existing.slot_samples) + [slot_sample])[-64:]
            if existing.occurrence_count > 1 and existing.slot_samples:
                existing.semantic_variance = min(
                    1.0,
                    (len(set(existing.slot_samples)) - 1) / (existing.occurrence_count - 1),
                )
            existing.source_diversity = diversity
            existing.dominant_source_share = dominant_share
            existing.trust_score = weighted_trust
            existing.trust_scope = scope
            return existing

        candidate_stmt = select(PatternCandidate).where(
            PatternCandidate.codebook == codebook,
            PatternCandidate.signature == signature,
        )
        savings = estimated_savings(composition)
        values = {
            "codebook": codebook,
            "signature": signature,
            "canonical": canonical_label(composition),
            "composition": composition,
            "relation_structure": relation_structure or {"paths": [item.get("path") for item in composition]},
            "occurrence_count": 1,
            "estimated_savings_bytes": savings,
            "slot_samples": [slot_sample] if slot_sample else [],
            "trust_scope": scope,
            "source_diversity": diversity,
            "dominant_source_share": dominant_share,
            "trust_score": weighted_trust,
        }
        dialect = self.db.get_bind().dialect.name
        table: Any = PatternCandidate.__table__
        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            pg_upsert = pg_insert(table).values(**values)
            pg_upsert = pg_upsert.on_conflict_do_update(
                constraint="uq_pattern_candidate_signature",
                set_={
                    "occurrence_count": table.c.occurrence_count + 1,
                    "estimated_savings_bytes": table.c.estimated_savings_bytes + savings,
                    "trust_scope": scope,
                    "source_diversity": diversity,
                    "dominant_source_share": dominant_share,
                    "trust_score": weighted_trust,
                },
            )
            self.db.execute(pg_upsert)
        elif dialect == "sqlite":
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            sqlite_upsert = sqlite_insert(table).values(**values)
            sqlite_upsert = sqlite_upsert.on_conflict_do_update(
                index_elements=[table.c.codebook, table.c.signature],
                set_={
                    "occurrence_count": table.c.occurrence_count + 1,
                    "estimated_savings_bytes": table.c.estimated_savings_bytes + savings,
                    "trust_scope": scope,
                    "source_diversity": diversity,
                    "dominant_source_share": dominant_share,
                    "trust_score": weighted_trust,
                },
            )
            self.db.execute(sqlite_upsert)
        else:
            candidate = self.db.scalar(candidate_stmt)
            if candidate is None:
                candidate = PatternCandidate(**values)
                try:
                    with self.db.begin_nested():
                        self.db.add(candidate)
                        self.db.flush()
                except IntegrityError:
                    candidate = self.db.scalar(candidate_stmt)
                    if candidate is None:
                        raise
                    candidate.occurrence_count += 1
                    candidate.estimated_savings_bytes += savings
            else:
                candidate.occurrence_count += 1
                candidate.estimated_savings_bytes += savings

        candidate = self.db.scalar(candidate_stmt.with_for_update())
        if candidate is None:
            existing = self.db.scalar(
                select(LearnedPattern).where(
                    LearnedPattern.codebook == codebook,
                    LearnedPattern.signature == signature,
                )
            )
            return existing
        concurrent_pattern = self.db.scalar(
            select(LearnedPattern).where(
                LearnedPattern.codebook == codebook,
                LearnedPattern.signature == signature,
            )
        )
        if concurrent_pattern is not None:
            self.db.delete(candidate)
            concurrent_pattern.occurrence_count += 1
            concurrent_pattern.source_diversity = diversity
            concurrent_pattern.dominant_source_share = dominant_share
            concurrent_pattern.trust_score = weighted_trust
            concurrent_pattern.trust_scope = scope
            self.db.flush()
            return concurrent_pattern

        if slot_sample and slot_sample not in candidate.slot_samples:
            candidate.slot_samples = (list(candidate.slot_samples) + [slot_sample])[-64:]
        if candidate.occurrence_count > 1 and candidate.slot_samples:
            candidate.semantic_variance = min(1.0, (len(set(candidate.slot_samples)) - 1) / (candidate.occurrence_count - 1))
        candidate.trust_scope = scope
        candidate.source_diversity = diversity
        candidate.dominant_source_share = dominant_share
        candidate.trust_score = weighted_trust

        candidate_score = math.log1p(candidate.occurrence_count) * (candidate.estimated_savings_bytes / 64.0) * max(0.05, 1.0 - candidate.semantic_variance)
        if self.settings.learning_mode != "managed":
            return None
        if (
            candidate.occurrence_count >= self.settings.pattern_candidate_min_count
            and candidate.estimated_savings_bytes >= self.settings.pattern_min_savings_bytes
            and candidate_score >= self.settings.pattern_utility_min_score
            and self._trust_ready(candidate.source_diversity, candidate.dominant_source_share, candidate.trust_score, candidate.trust_scope)
        ):
            return self._promote_candidate(candidate)
        return None

    def promote_ready_candidates(
        self, *, codebook: str | None = None, limit: int = 100
    ) -> builtins.list[LearnedPattern]:
        stmt = select(PatternCandidate).order_by(PatternCandidate.occurrence_count.desc(), PatternCandidate.estimated_savings_bytes.desc()).limit(max(1, min(limit, 1000)))
        if codebook is not None:
            stmt = stmt.where(PatternCandidate.codebook == codebook)
        promoted: builtins.list[LearnedPattern] = []
        for candidate in self.db.scalars(stmt.with_for_update(skip_locked=True)):
            score = math.log1p(candidate.occurrence_count) * (candidate.estimated_savings_bytes / 64.0) * max(0.05, 1.0 - candidate.semantic_variance)
            if (
                candidate.occurrence_count >= self.settings.pattern_candidate_min_count
                and candidate.estimated_savings_bytes >= self.settings.pattern_min_savings_bytes
                and score >= self.settings.pattern_utility_min_score
                and self._trust_ready(candidate.source_diversity, candidate.dominant_source_share, candidate.trust_score, candidate.trust_scope)
            ):
                promoted.append(self._promote_candidate(candidate))
        self.db.flush()
        return promoted

    def _promote_candidate(self, candidate: PatternCandidate) -> LearnedPattern:
        existing = self.db.scalar(
            select(LearnedPattern).where(
                LearnedPattern.codebook == candidate.codebook,
                LearnedPattern.signature == candidate.signature,
            )
        )
        if existing is not None:
            self.db.delete(candidate)
            self.db.flush()
            return existing

        concept_name = f"pattern_{candidate.signature[:20]}"
        concept = self.codebook.register(
            candidate.codebook,
            concept_name,
            f"higher-order semantic pattern: {candidate.canonical}",
        )
        pattern = LearnedPattern(
            codebook=candidate.codebook,
            signature=candidate.signature,
            canonical=candidate.canonical,
            concept_id=concept.id,
            composition=candidate.composition,
            relation_structure=candidate.relation_structure,
            embedding_space=self.codebook.embedding_space,
            vector=self.codebook.embedder.embed(candidate.canonical),
            occurrence_count=candidate.occurrence_count,
            estimated_savings_bytes=candidate.estimated_savings_bytes,
            semantic_variance=candidate.semantic_variance,
            slot_samples=list(candidate.slot_samples),
            confidence=1.0,
            status="shadow",
            ambiguity_score=candidate.semantic_variance,
            interoperability_score=1.0,
            calibrated_reliability=1.0,
            trust_scope=candidate.trust_scope,
            source_diversity=candidate.source_diversity,
            dominant_source_share=candidate.dominant_source_share,
            trust_score=candidate.trust_score,
        )
        try:
            with self.db.begin_nested():
                self.db.add(pattern)
                self.db.flush()
        except IntegrityError:
            existing = self.db.scalar(
                select(LearnedPattern).where(
                    LearnedPattern.codebook == candidate.codebook,
                    LearnedPattern.signature == candidate.signature,
                )
            )
            if existing is None:
                raise
            self.db.delete(candidate)
            self.db.flush()
            return existing

        concept.status = "shadow"
        children = list((candidate.relation_structure or {}).get("children") or [])
        for position, child_pattern_id in enumerate(children):
            child = self.get(str(child_pattern_id))
            if child is not None:
                self.db.add(PatternEdge(parent_pattern_id=pattern.id, child_pattern_id=child.id, position=position))
        self.db.delete(candidate)
        self.db.flush()
        return pattern

    def get(self, pattern_id: str) -> LearnedPattern | None:
        if not pattern_id.startswith("G"):
            return None
        try:
            ident = int(pattern_id[1:], 16)
        except ValueError:
            return None
        return self.db.get(LearnedPattern, ident)

    def by_concept_id(self, concept_id: int) -> LearnedPattern | None:
        return self.db.scalar(select(LearnedPattern).where(LearnedPattern.concept_id == concept_id))

    def list(
        self, codebook: str, *, status: str | None = None
    ) -> builtins.list[LearnedPattern]:
        namespaces = self.codebook.namespace_chain(codebook)
        stmt = select(LearnedPattern).where(LearnedPattern.codebook.in_(namespaces))
        if status:
            stmt = stmt.where(LearnedPattern.status == status)
        return list(self.db.scalars(stmt.order_by(LearnedPattern.id)))

    def candidates(self, codebook: str) -> builtins.list[PatternCandidate]:
        namespaces = self.codebook.namespace_chain(codebook)
        return list(
            self.db.scalars(
                select(PatternCandidate)
                .where(PatternCandidate.codebook.in_(namespaces))
                .order_by(PatternCandidate.occurrence_count.desc(), PatternCandidate.id)
            )
        )

    @staticmethod
    def _match_component(component: dict[str, Any], unit: SemanticUnit) -> tuple[bool, Any | None, bool]:
        if component.get("canonical") != unit.canonical:
            return False, None, False
        if component.get("path") != _path_shape(unit.path):
            return False, None, False
        if bool(component.get("has_literal")) != unit.has_literal:
            return False, None, False
        mode = component.get("literal_mode", "none")
        if mode == "constant":
            return unit.has_literal and unit.literal == component.get("literal"), None, False
        if mode == "slot":
            if not unit.has_literal or _literal_type(unit.literal) != component.get("literal_type"):
                return False, None, False
            return True, unit.literal, True
        return (not unit.has_literal), None, False

    def match_pattern_at(
        self, pattern: LearnedPattern, units: builtins.list[SemanticUnit], start: int
    ) -> PatternMatch | None:
        composition = list(pattern.composition or [])
        if start + len(composition) > len(units):
            return None
        bindings: builtins.list[Any] = []
        for offset, component in enumerate(composition):
            ok, binding, has_binding = self._match_component(component, units[start + offset])
            if not ok:
                return None
            if has_binding:
                bindings.append(binding)
        return PatternMatch(pattern=pattern, start=start, end=start + len(composition), bindings=bindings)

    def matches(
        self, codebook: str, units: builtins.list[SemanticUnit], *, statuses: set[str]
    ) -> builtins.list[PatternMatch]:
        patterns = [p for p in self.list(codebook) if p.status in statuses]
        patterns.sort(key=lambda p: (len(p.composition or []), p.estimated_savings_bytes), reverse=True)
        matches: builtins.list[PatternMatch] = []
        for start in range(len(units)):
            for pattern in patterns:
                match = self.match_pattern_at(pattern, units, start)
                if match is not None:
                    matches.append(match)
        return matches

    def active_matches(
        self,
        codebook: str,
        units: builtins.list[SemanticUnit],
        *,
        receiver: str | None = None,
        model: str | None = None,
        workspace: str = "default",
        task_family: str = "*",
    ) -> builtins.list[PatternMatch]:
        raw = self.matches(codebook, units, statuses={"active"})
        if receiver or model:
            raw = [m for m in raw if self.receiver_fidelity(m.pattern, receiver or "*", model or "*", workspace, task_family) >= self.settings.pattern_receiver_min_fidelity]
        raw.sort(key=lambda m: (m.start, -(m.end - m.start), -self.utility_score(m.pattern), -m.pattern.estimated_savings_bytes))
        selected: builtins.list[PatternMatch] = []
        occupied: set[int] = set()
        for match in raw:
            span = set(range(match.start, match.end))
            if span & occupied:
                continue
            selected.append(match)
            occupied.update(span)
        return selected

    def shadow_matches(
        self, codebook: str, units: builtins.list[SemanticUnit]
    ) -> builtins.list[PatternMatch]:
        return self.matches(codebook, units, statuses={"shadow", "validated"})

    def utility_score(self, pattern: LearnedPattern) -> float:
        score = calculate_utility_score(pattern)
        pattern.utility_score = score
        return score

    def receiver_metric(self, pattern: LearnedPattern, receiver: str, model: str, workspace: str) -> PatternReceiverMetric | None:
        return self.db.scalar(select(PatternReceiverMetric).where(
            PatternReceiverMetric.pattern_id == pattern.id,
            PatternReceiverMetric.workspace == workspace,
            PatternReceiverMetric.receiver == receiver,
            PatternReceiverMetric.model == model,
        ))

    def receiver_fidelity(
        self,
        pattern: LearnedPattern,
        receiver: str,
        model: str,
        workspace: str = "default",
        task_family: str = "*",
    ) -> float:
        exact = self.receiver_metric(pattern, receiver, model, workspace)
        fallback = self.receiver_metric(pattern, "*", "*", workspace)
        metric = exact or fallback
        raw = 1.0 if metric is None or metric.sample_count <= 0 else metric.fidelity_sum / metric.sample_count
        calibrated = self.calibration.calibrated_probability(
            raw, workspace=workspace, receiver=receiver, model=model, task_family=task_family
        )
        return min(raw, calibrated)

    def record_counterfactual(
        self, pattern_id: str, *, full_success: float, compressed_success: float, semantic_fidelity: float,
        receiver: str = "*", model: str = "*", task_family: str = "*", workspace: str = "default",
        validation_id: str = "",
    ) -> LearnedPattern:
        pattern = self.get(pattern_id)
        if pattern is None:
            raise KeyError(pattern_id)
        metric = self.receiver_metric(pattern, receiver, model, workspace)
        if metric is None:
            metric = PatternReceiverMetric(pattern_id=pattern.id, workspace=workspace, receiver=receiver, model=model)
            self.db.add(metric)
            self.db.flush()
        metric.sample_count += 1
        metric.full_success_sum += full_success
        metric.compressed_success_sum += compressed_success
        metric.fidelity_sum += semantic_fidelity
        if abs(full_success - compressed_success) <= 1e-9 and semantic_fidelity >= self.settings.pattern_counterfactual_min_fidelity:
            metric.exact_equivalence_count += 1
        metric.last_seen_at = datetime.now(UTC)
        equivalent = 1.0 if abs(full_success - compressed_success) <= 1e-9 and semantic_fidelity >= self.settings.pattern_counterfactual_min_fidelity else 0.0
        self.calibration.record(
            predicted=semantic_fidelity,
            observed=equivalent,
            workspace=workspace,
            receiver=receiver,
            model=model,
            task_family=task_family,
        )
        self.reliability.record_holdout(
            pattern=pattern, workspace=workspace, receiver=receiver, model_identity_hash=model,
            task_family=task_family, full_success=full_success, compressed_success=compressed_success, fidelity=semantic_fidelity,
            source_id=validation_id,
        )
        report = self.calibration.report(
            semantic_fidelity, workspace=workspace, receiver=receiver, model=model, task_family=task_family
        )
        pattern.calibrated_reliability = report.calibrated_probability
        all_metrics = list(self.db.scalars(select(PatternReceiverMetric).where(PatternReceiverMetric.pattern_id == pattern.id)))
        total = sum(m.sample_count for m in all_metrics)
        fidelity = sum(m.fidelity_sum for m in all_metrics) / total if total else 0.0
        pattern.interoperability_score = fidelity if total else 1.0
        pattern.utility_score = self.utility_score(pattern)
        if pattern.status in {"shadow", "validated"} and metric.sample_count >= self.settings.pattern_counterfactual_min_samples:
            avg_fidelity = metric.fidelity_sum / metric.sample_count
            full_avg = metric.full_success_sum / metric.sample_count
            compressed_avg = metric.compressed_success_sum / metric.sample_count
            if (
                avg_fidelity >= self.settings.pattern_counterfactual_min_fidelity
                and compressed_avg + 1e-9 >= full_avg
                and self._trust_ready(pattern.source_diversity, pattern.dominant_source_share, pattern.trust_score, pattern.trust_scope)
                and report.expected_calibration_error <= self.settings.calibration_max_ece
                and self.reliability.holdout_ready(
                    pattern, workspace=workspace, receiver=receiver, model_identity_hash=model, task_family=task_family
                )
            ):
                pattern.status = "active" if self.settings.pattern_auto_activate else "validated"
                pattern.version += 1
                concept = self.db.get(Concept, pattern.concept_id)
                if concept is not None:
                    concept.status = pattern.status
                    concept.version += 1
        self.db.flush()
        return pattern

    def mark_used(self, pattern: LearnedPattern) -> None:
        pattern.use_count += 1
        pattern.last_used_at = datetime.now(UTC)
        if pattern.status == "cooling":
            pattern.status = "active"
            pattern.cooling_since = None
            pattern.version += 1
        self.utility_score(pattern)

    def promote_namespace(self, pattern_id: str, target_codebook: str) -> LearnedPattern:
        source = self.get(pattern_id)
        if source is None:
            raise KeyError(pattern_id)
        if self.utility_score(source) < self.settings.pattern_namespace_promotion_min_utility:
            raise ValueError("pattern utility is below namespace promotion threshold")
        target_chain = self.codebook.namespace_chain(source.codebook)
        if target_codebook not in target_chain or target_codebook == source.codebook:
            raise ValueError("target must be a parent namespace in the codebook chain")
        signature = hashlib.sha256((source.signature + "\0" + target_codebook).encode()).hexdigest()
        existing = self.db.scalar(select(LearnedPattern).where(LearnedPattern.codebook == target_codebook, LearnedPattern.signature == signature))
        if existing is not None:
            return existing
        concept = self.codebook.register(target_codebook, f"pattern_{signature[:20]}", f"promoted pattern: {source.canonical}")
        promoted = LearnedPattern(
            codebook=target_codebook, signature=signature, canonical=source.canonical, concept_id=concept.id,
            composition=source.composition, relation_structure={**(source.relation_structure or {}), "promoted_from": source.pattern_id},
            embedding_space=source.embedding_space, vector=source.vector, occurrence_count=source.occurrence_count,
            estimated_savings_bytes=source.estimated_savings_bytes, semantic_variance=source.semantic_variance,
            slot_samples=source.slot_samples, confidence=source.confidence, status="shadow", ambiguity_score=source.ambiguity_score,
            interoperability_score=source.interoperability_score, utility_score=source.utility_score,
            calibrated_reliability=source.calibrated_reliability, trust_scope=target_codebook,
            source_diversity=source.source_diversity, dominant_source_share=source.dominant_source_share,
            trust_score=source.trust_score,
        )
        self.db.add(promoted)
        self.db.flush()
        concept.status = "shadow"
        return promoted

    def garbage_collect(self, codebook: str | None = None) -> dict[str, int]:
        now = datetime.now(UTC)
        cooling_cutoff = now - timedelta(days=self.settings.pattern_gc_cooling_days)
        retire_cutoff = now - timedelta(days=self.settings.pattern_gc_retire_days)
        stmt = select(LearnedPattern)
        if codebook:
            stmt = stmt.where(LearnedPattern.codebook.in_(self.codebook.namespace_chain(codebook)))
        cooling = retired = 0
        for pattern in self.db.scalars(stmt):
            last = pattern.last_used_at or pattern.updated_at or pattern.created_at
            if last.tzinfo is None:
                last = last.replace(tzinfo=UTC)
            if pattern.status == "active" and last < cooling_cutoff:
                pattern.status = "cooling"
                pattern.cooling_since = now
                pattern.version += 1
                cooling += 1
            elif pattern.status in {"cooling", "deprecated"} and last < retire_cutoff:
                pattern.status = "retired"
                pattern.version += 1
                retired += 1
            concept = self.db.get(Concept, pattern.concept_id)
            if concept is not None and concept.status != pattern.status:
                concept.status = pattern.status
                concept.version += 1
        self.db.flush()
        return {"patterns_cooling": cooling, "patterns_retired": retired}

    def record_feedback(
        self, decisions: builtins.list[dict[str, Any]], task_success: float
    ) -> builtins.list[LearnedPattern]:
        touched: builtins.list[LearnedPattern] = []
        seen: set[str] = set()
        for decision in decisions:
            pattern_id = decision.get("pattern_id")
            if not isinstance(pattern_id, str) or pattern_id in seen:
                continue
            if decision.get("action") not in {"pattern_shadow_match", "pattern_code"}:
                continue
            pattern = self.get(pattern_id)
            if pattern is None:
                continue
            seen.add(pattern_id)
            pattern.task_success_count += 1
            pattern.task_success_sum += task_success
            if decision.get("action") == "pattern_shadow_match" and pattern.status in {"shadow", "validated"}:
                pattern.shadow_samples += 1
                pattern.shadow_success_sum += task_success
                rate = pattern.shadow_success_rate or 0.0
                if pattern.shadow_samples >= self.settings.pattern_shadow_min_samples:
                    if rate >= self.settings.pattern_shadow_min_success:
                        pattern.status = "validated"
                        if self.settings.pattern_auto_activate and not self.settings.pattern_counterfactual_required:
                            pattern.status = "active"
                        concept = self.db.get(Concept, pattern.concept_id)
                        if concept is not None:
                            concept.status = pattern.status
                            concept.version += 1
                        pattern.version += 1
                    elif pattern.shadow_samples >= self.settings.pattern_shadow_min_samples * 2:
                        pattern.status = "retired"
                        concept = self.db.get(Concept, pattern.concept_id)
                        if concept is not None:
                            concept.status = "retired"
                            concept.version += 1
                        pattern.version += 1
            touched.append(pattern)
        self.db.flush()
        return touched

    def set_status(self, pattern_id: str, status: str) -> LearnedPattern:
        allowed = {"shadow", "validated", "active", "cooling", "deprecated", "retired"}
        if status not in allowed:
            raise ValueError(f"status must be one of: {', '.join(sorted(allowed))}")
        pattern = self.get(pattern_id)
        if pattern is None:
            raise KeyError(pattern_id)
        if status == "active" and not self._trust_ready(pattern.source_diversity, pattern.dominant_source_share, pattern.trust_score, pattern.trust_scope):
            raise ValueError("pattern trust evidence is insufficient for activation")
        if pattern.status != status:
            pattern.status = status
            pattern.version += 1
            concept = self.db.get(Concept, pattern.concept_id)
            if concept is not None:
                concept.status = status
                concept.version += 1
        return pattern

    def response(self, pattern: LearnedPattern) -> dict[str, Any]:
        concept = self.db.get(Concept, pattern.concept_id)
        return {
            "pattern_id": pattern.pattern_id,
            "concept_code": concept.code if concept else None,
            "concept_version": concept.version if concept else None,
            "codebook": pattern.codebook,
            "signature": pattern.signature,
            "canonical": pattern.canonical,
            "composition": pattern.composition,
            "relation_structure": pattern.relation_structure,
            "occurrence_count": pattern.occurrence_count,
            "estimated_savings_bytes": pattern.estimated_savings_bytes,
            "semantic_variance": pattern.semantic_variance,
            "confidence": pattern.confidence,
            "status": pattern.status,
            "version": pattern.version,
            "shadow_samples": pattern.shadow_samples,
            "shadow_success_rate": pattern.shadow_success_rate,
            "task_utility": pattern.task_utility,
            "utility_score": self.utility_score(pattern),
            "ambiguity_score": pattern.ambiguity_score,
            "interoperability_score": pattern.interoperability_score,
            "calibrated_reliability": pattern.calibrated_reliability,
            "trust_scope": pattern.trust_scope,
            "source_diversity": pattern.source_diversity,
            "dominant_source_share": pattern.dominant_source_share,
            "trust_score": pattern.trust_score,
            "use_count": pattern.use_count,
            "last_used_at": pattern.last_used_at.isoformat() if pattern.last_used_at else None,
            "children": list((pattern.relation_structure or {}).get("children") or []),
        }
