# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .compiler import normalize
from .config import Settings
from .db_models import Candidate, Concept, ConceptAlias
from .embeddings import (
    EmbeddingProvider,
    HashEmbeddingProvider,
    OpenAICompatibleEmbeddingProvider,
    cosine,
)


def lsh_bucket(vector: list[float], bits: int) -> str:
    if not vector:
        return "0" * ((bits + 3) // 4)
    signs = 0
    width = len(vector)
    for bit in range(bits):
        total = 0.0
        index = bit
        while index < width:
            total += vector[index]
            index += bits
        if total >= 0.0:
            signs |= 1 << bit
    return f"{signs:0{(bits + 3) // 4}x}"


def lsh_neighbors(bucket: str, bits: int, hamming: int) -> list[str]:
    value = int(bucket, 16) if bucket else 0
    values = {value}
    if hamming >= 1:
        values.update(value ^ (1 << i) for i in range(bits))
    if hamming >= 2:
        values.update(value ^ (1 << i) ^ (1 << j) for i in range(bits) for j in range(i + 1, bits))
    width = (bits + 3) // 4
    return [f"{item:0{width}x}" for item in sorted(values)]


@dataclass(frozen=True)
class Match:
    concept: Concept | None
    similarity: float


class Codebook:
    def __init__(self, db: Session, settings: Settings, embedder: EmbeddingProvider | None = None) -> None:
        self.db = db
        self.settings = settings
        if embedder is not None:
            self.embedder = embedder
        elif settings.embedding_provider.lower() in {"openai", "openai_compatible"}:
            self.embedder = OpenAICompatibleEmbeddingProvider(
                api_url=settings.embedding_api_url,
                api_key=settings.embedding_api_key.get_secret_value() if settings.embedding_api_key else "",
                model=settings.embedding_model,
                timeout_seconds=settings.embedding_timeout_seconds,
            )
        else:
            self.embedder = HashEmbeddingProvider()
        self.embedding_space = (
            f"openai-compatible:{settings.embedding_api_url.rstrip('/')}:{settings.embedding_model}"
            if settings.embedding_provider.lower() in {"openai", "openai_compatible"}
            else "hash:v1:96"
        )
        self._all_cache: dict[tuple[str, bool, bool], list[Concept]] = {}
        self._chain_cache: dict[tuple[str, bool, bool], list[Concept]] = {}

    def namespace_chain(self, codebook: str) -> list[str]:
        chain = [self.settings.core_codebook]
        if codebook == self.settings.core_codebook:
            return chain
        parts = [p for p in codebook.split(".") if p]
        for i in range(1, len(parts) + 1):
            name = ".".join(parts[:i])
            if name not in chain:
                chain.append(name)
        if codebook not in chain:
            chain.append(codebook)
        return chain

    def _invalidate_cache(self) -> None:
        self._all_cache.clear()
        self._chain_cache.clear()

    def all(self, codebook: str, *, compatible_only: bool = False, include_deprecated: bool = False) -> list[Concept]:
        key = (codebook, compatible_only, include_deprecated)
        cached = self._all_cache.get(key)
        if cached is not None:
            return cached
        stmt = select(Concept).where(Concept.codebook == codebook)
        if not include_deprecated:
            stmt = stmt.where(Concept.status == "active")
        if compatible_only:
            stmt = stmt.where(Concept.embedding_space == self.embedding_space)
        values = list(self.db.scalars(stmt))
        self._all_cache[key] = values
        return values

    def all_chain(self, codebook: str, *, compatible_only: bool = False, include_deprecated: bool = False) -> list[Concept]:
        key = (codebook, compatible_only, include_deprecated)
        cached = self._chain_cache.get(key)
        if cached is not None:
            return cached
        values = [
            concept
            for namespace in self.namespace_chain(codebook)
            for concept in self.all(namespace, compatible_only=compatible_only, include_deprecated=include_deprecated)
        ]
        self._chain_cache[key] = values
        return values

    def get_by_code(self, code: str) -> Concept | None:
        if not code.startswith("C"):
            return None
        try:
            concept_id = int(code[1:], 16)
        except ValueError:
            return None
        concept = self.db.get(Concept, concept_id)
        if concept and concept.status == "deprecated" and concept.replacement_id:
            return self.db.get(Concept, concept.replacement_id) or concept
        return concept

    def exact(self, codebook: str, canonical: str) -> Concept | None:
        canonical = normalize(canonical)
        stmt = select(Concept).where(Concept.codebook == codebook, Concept.canonical == canonical)
        concept = self.db.scalar(stmt)
        if concept:
            return self.get_by_code(concept.code)
        alias = self.db.scalar(
            select(ConceptAlias).where(ConceptAlias.codebook == codebook, ConceptAlias.alias == canonical)
        )
        return self.get_by_code(f"C{alias.concept_id:08X}") if alias else None

    def exact_chain(self, codebook: str, canonical: str) -> Concept | None:
        for namespace in reversed(self.namespace_chain(codebook)):
            concept = self.exact(namespace, canonical)
            if concept:
                return concept
        return None

    def _fuzzy_candidates(self, codebook: str, vector: list[float]) -> list[Concept]:
        namespaces = self.namespace_chain(codebook)
        total = int(
            self.db.scalar(
                select(func.count(Concept.id)).where(
                    Concept.codebook.in_(namespaces),
                    Concept.status == "active",
                    Concept.embedding_space == self.embedding_space,
                )
            )
            or 0
        )
        if total <= self.settings.semantic_fuzzy_scan_limit:
            return self.all_chain(codebook, compatible_only=True)
        bucket = lsh_bucket(vector, self.settings.semantic_lsh_bits)
        buckets = lsh_neighbors(bucket, self.settings.semantic_lsh_bits, self.settings.semantic_lsh_hamming)
        stmt = (
            select(Concept)
            .where(
                Concept.codebook.in_(namespaces),
                Concept.status == "active",
                Concept.embedding_space == self.embedding_space,
                Concept.lsh_bucket.in_(buckets),
            )
            .order_by(Concept.seen_count.desc(), Concept.id)
            .limit(self.settings.semantic_candidate_limit)
        )
        return list(self.db.scalars(stmt))

    def nearest_similarity(self, codebook: str, canonical: str) -> float:
        vector = self.embedder.embed(normalize(canonical))
        return max((cosine(vector, c.vector) for c in self._fuzzy_candidates(codebook, vector)), default=0.0)

    def match(self, codebook: str, canonical: str, *, observe: bool = True) -> Match:
        canonical = normalize(canonical)
        exact = self.exact_chain(codebook, canonical)
        if exact and exact.status == "active":
            if observe:
                exact.seen_count += 1
            return Match(exact, 1.0)
        vector = self.embedder.embed(canonical)
        best: Concept | None = None
        score = 0.0
        for concept in self._fuzzy_candidates(codebook, vector):
            current = cosine(vector, concept.vector)
            if current > score:
                best, score = concept, current
        if best and score >= self.settings.semantic_threshold:
            if observe:
                best.seen_count += 1
            return Match(best, score)
        return Match(None, score)

    def register(self, codebook: str, canonical: str, description: str = "", aliases: list[str] | None = None) -> Concept:
        canonical = normalize(canonical)
        if not canonical:
            raise ValueError("canonical concept cannot be empty")
        existing = self.exact(codebook, canonical)
        if existing:
            existing.seen_count += 1
            if description and not existing.description:
                existing.description = description
            for alias in aliases or []:
                self.add_alias(existing.code, alias)
            self._invalidate_cache()
            return existing
        semantic_hash = hashlib.sha256(f"{canonical}\0{description}".encode()).hexdigest()
        vector = self.embedder.embed(canonical + " " + description)
        concept = Concept(
            codebook=codebook,
            canonical=canonical,
            description=description,
            embedding_space=self.embedding_space,
            vector=vector,
            lsh_bucket=lsh_bucket(vector, self.settings.semantic_lsh_bits),
            semantic_hash=semantic_hash,
        )
        try:
            with self.db.begin_nested():
                self.db.add(concept)
                self.db.flush()
        except IntegrityError:
            existing = self.exact(codebook, canonical)
            if existing is None:
                raise
            existing.seen_count += 1
            return existing
        for alias in aliases or []:
            self.add_alias(concept.code, alias)
        self._invalidate_cache()
        return concept

    def add_alias(self, code: str, alias: str) -> ConceptAlias:
        concept = self.get_by_code(code)
        if concept is None:
            raise KeyError(code)
        normalized = normalize(alias)
        if not normalized:
            raise ValueError("alias cannot be empty")
        existing = self.db.scalar(
            select(ConceptAlias).where(ConceptAlias.codebook == concept.codebook, ConceptAlias.alias == normalized)
        )
        if existing:
            if existing.concept_id != concept.id:
                raise ValueError("alias already belongs to another concept")
            return existing
        item = ConceptAlias(codebook=concept.codebook, alias=normalized, concept_id=concept.id)
        self.db.add(item)
        self.db.flush()
        self._invalidate_cache()
        return item

    def deprecate(self, code: str, replacement_code: str | None = None) -> Concept:
        concept = self.get_by_code(code)
        if concept is None:
            raise KeyError(code)
        replacement = self.get_by_code(replacement_code) if replacement_code else None
        if replacement_code and replacement is None:
            raise KeyError(replacement_code)
        if replacement and replacement.id == concept.id:
            raise ValueError("replacement must differ from deprecated concept")
        concept.status = "deprecated"
        concept.version += 1
        concept.replacement_id = replacement.id if replacement else None
        self._invalidate_cache()
        return concept

    def observe_candidate(self, codebook: str, canonical: str) -> Concept | None:
        canonical = normalize(canonical)
        if not canonical:
            return None
        stmt = select(Candidate).where(Candidate.codebook == codebook, Candidate.canonical == canonical)
        candidate = self.db.scalar(stmt)
        neighbor = self.nearest_similarity(codebook, canonical)
        incremental_savings = max(0, len(canonical.encode()) - 10)
        if candidate is None:
            candidate = Candidate(
                codebook=codebook,
                canonical=canonical,
                seen_count=1,
                estimated_savings_bytes=incremental_savings,
                max_neighbor_similarity=neighbor,
            )
            try:
                with self.db.begin_nested():
                    self.db.add(candidate)
                    self.db.flush()
            except IntegrityError:
                candidate = self.db.scalar(stmt)
                if candidate is None:
                    raise
                candidate.seen_count += 1
                candidate.estimated_savings_bytes += incremental_savings
                candidate.max_neighbor_similarity = max(candidate.max_neighbor_similarity, neighbor)
        else:
            candidate.seen_count += 1
            candidate.estimated_savings_bytes += incremental_savings
            candidate.max_neighbor_similarity = max(candidate.max_neighbor_similarity, neighbor)
        promote = (
            candidate.seen_count >= self.settings.promotion_min_count
            and candidate.estimated_savings_bytes >= self.settings.promotion_min_savings_bytes
            and candidate.max_neighbor_similarity <= self.settings.promotion_max_neighbor_similarity
        )
        if promote:
            concept = self.register(codebook, canonical, "auto-promoted recurring semantic unit")
            self.db.delete(candidate)
            self.db.flush()
            return concept
        return None

    def fingerprint(self, codebook: str) -> str:
        values = [
            f"{c.code}:{c.version}:{c.status}:{c.canonical}:{c.replacement_id or ''}"
            for c in self.all_chain(codebook, include_deprecated=True)
        ]
        return hashlib.sha256("\n".join(sorted(values)).encode()).hexdigest()[:24]
