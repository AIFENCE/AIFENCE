# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass

from .compiler import SemanticUnit, normalize
from .schemas import EpistemicType

EPISTEMIC_TYPES: set[EpistemicType] = {
    "fact",
    "observation",
    "inference",
    "hypothesis",
    "prediction",
    "preference",
    "instruction",
    "constraint",
}

_CRITICAL_PATH_TERMS = {
    "id", "identity", "name", "email", "account", "user", "owner", "recipient",
    "amount", "price", "cost", "quantity", "count", "limit", "threshold", "deadline",
    "date", "time", "expires", "expiry", "production", "prod", "staging", "environment",
    "permission", "allowed", "denied", "deny", "delete", "must", "must_not", "required",
    "approved", "rejected", "status", "confidence", "version", "region",
}
_CRITICAL_TEXT_RE = re.compile(
    r"\b(?:not|never|no|must|must\s+not|may\s+not|cannot|approved|rejected|production|staging|"
    r"delete|deny|allow|before|after|until|deadline|expires?|\$?\d+(?:\.\d+)?)\b",
    re.I,
)
_EPISTEMIC_HINTS: dict[EpistemicType, set[str]] = {
    "observation": {"observed", "observation", "measured", "measurement"},
    "inference": {"inference", "derived", "conclusion", "because"},
    "hypothesis": {"hypothesis", "maybe", "possible", "suspect", "assumption"},
    "prediction": {"prediction", "forecast", "risk", "likely", "expected"},
    "preference": {"preference", "prefer", "want", "desired"},
    "instruction": {"instruction", "command", "request", "do", "execute"},
    "constraint": {"constraint", "must", "must_not", "required", "forbidden", "limit"},
}


@dataclass(frozen=True)
class SemanticRisk:
    score: float
    reasons: tuple[str, ...]
    epistemic_type: EpistemicType

    @property
    def critical(self) -> bool:
        return self.score >= 0.7


def infer_epistemic_type(path: str, canonical: str, surface: str | None = None) -> EpistemicType:
    text = normalize(" ".join(filter(None, [path, canonical, surface or ""])))
    terms = set(re.split(r"[_.:/-]+", text))
    for kind, hints in _EPISTEMIC_HINTS.items():
        if terms & hints:
            return kind
    return "fact"


def assess_unit(unit: SemanticUnit) -> SemanticRisk:
    reasons: list[str] = []
    score = 0.0
    path_terms = set(re.split(r"[.$\[\]_/:-]+", normalize(unit.path)))
    canonical_terms = set(re.split(r"[_.:/-]+", normalize(unit.canonical)))
    if (path_terms | canonical_terms) & _CRITICAL_PATH_TERMS:
        score += 0.45
        reasons.append("critical_field")
    if unit.has_literal:
        value = unit.literal
        if isinstance(value, bool) or value is None:
            score += 0.35
            reasons.append("boolean_or_null")
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            score += 0.45
            reasons.append("numeric_value")
        elif isinstance(value, str) and _CRITICAL_TEXT_RE.search(value):
            score += 0.4
            reasons.append("critical_text")
    if unit.surface and _CRITICAL_TEXT_RE.search(unit.surface):
        score += 0.5
        reasons.append("negation_permission_quantity_or_time")
    if any(term in {"id", "email", "account", "identity", "recipient", "owner"} for term in path_terms | canonical_terms):
        score += 0.35
        reasons.append("identity")
    return SemanticRisk(
        score=min(1.0, score),
        reasons=tuple(dict.fromkeys(reasons)),
        epistemic_type=infer_epistemic_type(unit.path, unit.canonical, unit.surface),
    )


def semantic_fingerprint(units: Iterable[SemanticUnit]) -> list[tuple[str, str, bool, str]]:
    out: list[tuple[str, str, bool, str]] = []
    for unit in units:
        literal = json.dumps(unit.literal, sort_keys=True, ensure_ascii=False, default=str) if unit.has_literal else ""
        out.append((unit.path, unit.canonical, unit.has_literal, literal))
    return out


def loss_score(original: Iterable[SemanticUnit], reconstructed: Iterable[SemanticUnit]) -> float:
    left = semantic_fingerprint(original)
    right = semantic_fingerprint(reconstructed)
    if left == right:
        return 0.0
    if not left:
        return 0.0 if not right else 1.0
    matched = sum(1 for item in left if item in right)
    return max(0.0, min(1.0, 1.0 - matched / len(left)))


def critical_loss(original: Iterable[SemanticUnit], reconstructed: Iterable[SemanticUnit]) -> bool:
    original_list = list(original)
    reconstructed_set = set(semantic_fingerprint(reconstructed))
    for unit in original_list:
        if assess_unit(unit).critical:
            fp = semantic_fingerprint([unit])[0]
            if fp not in reconstructed_set:
                return True
    return False
