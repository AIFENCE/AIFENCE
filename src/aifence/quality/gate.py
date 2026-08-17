# SPDX-License-Identifier: AGPL-3.0-or-later
"""The AIFENCE quality gate.

A deterministic, dependency-free gate that runs concrete, checkable quality
controls over an AI-generated artifact and attributes each check back to a
canonical control capability. This is the fast in-process gate that fronts the
fence; deep, family-native evaluation is delegated to the quality-control
runtime under ``quality/`` and is out of scope for this bridge.

The gate returns one of three outcomes, mirroring how the fence treats it
downstream: ``accept`` (pass to guard), ``revise`` (soft-fail, quality too low),
or ``reject`` (hard-fail on a mandatory control).
"""
from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

from .controls import controls_by_capability

CheckStatus = Literal["pass", "warn", "fail"]
Outcome = Literal["accept", "revise", "reject"]

_PLACEHOLDER_PATTERN = re.compile(
    r"\b(TODO|TBD|FIXME|XXX|PLACEHOLDER|LOREM IPSUM|INSERT[ _]|CHANGEME)\b",
    re.IGNORECASE,
)
_EMPTY_LINK_PATTERN = re.compile(
    r"""href\s*=\s*["'](?:\s*|#|javascript:void\(0\))["']""",
    re.IGNORECASE,
)
_EMPTY_MD_LINK_PATTERN = re.compile(r"\]\(\s*\)")
_HEADING_OR_TAG = re.compile(r"(^#{1,6}\s)|(<h[1-6][\s>])|(<section|<article|<main)", re.IGNORECASE | re.MULTILINE)
#: Numbers that read as factual claims: money, percentages, and multi-digit
#: figures. Small bare integers are excluded — they are usually list indices,
#: version fragments, or ordinary prose rather than sourced claims.
_CLAIM_NUMBER = re.compile(r"(?<![\w.])(?:\$\s?)?\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\b\d{2,}\b")


def _normalize_number(value: str) -> str:
    return value.replace(",", "").replace("$", "").strip()


def _ungrounded_numbers(text: str, sources: Sequence[str]) -> list[str]:
    """Numeric claims in ``text`` that appear nowhere in ``sources``.

    A deliberately conservative groundedness signal: it proves nothing about
    prose accuracy, but an invented figure is the most common and most costly
    fabrication in generated business artifacts, and it is checkable.
    """
    haystack = " ".join(sources)
    normalized_haystack = _normalize_number(haystack)
    unsupported: list[str] = []
    for match in _CLAIM_NUMBER.finditer(text):
        raw = match.group(0)
        value = _normalize_number(raw)
        if not value:
            continue
        if value in normalized_haystack or raw in haystack:
            continue
        if value not in unsupported:
            unsupported.append(value)
    return unsupported


def _schema_violations(document: Any, schema: dict[str, Any]) -> list[str]:
    """Validate against JSON Schema, degrading to a structural subset.

    Full validation is used when ``jsonschema`` is installed (it ships with the
    quality pack's validators). Otherwise the required-property and type subset
    is enforced, so a missing contract field is still caught rather than the
    check silently passing.
    """
    try:
        import jsonschema
    except ImportError:
        return _structural_violations(document, schema)
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"{'/'.join(str(p) for p in error.path) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.path))
    ]


_JSON_TYPES: dict[str, type | tuple[type, ...]] = {
    "object": dict, "array": list, "string": str,
    "integer": int, "number": (int, float), "boolean": bool,
}


def _structural_violations(document: Any, schema: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    expected = schema.get("type")
    if isinstance(expected, str) and expected in _JSON_TYPES:
        if not isinstance(document, _JSON_TYPES[expected]) or (
            expected in {"integer", "number"} and isinstance(document, bool)
        ):
            return [f"<root>: expected {expected}"]
    if isinstance(document, dict):
        for key in schema.get("required", []):
            if key not in document:
                violations.append(f"{key}: required property is missing")
        for key, subschema in (schema.get("properties") or {}).items():
            if key in document and isinstance(subschema, dict):
                violations.extend(
                    f"{key}/{v}" if not v.startswith("<root>") else f"{key}: {v.split(': ', 1)[-1]}"
                    for v in _structural_violations(document[key], subschema)
                )
    return violations


@dataclass(frozen=True)
class QualityCheck:
    check: str
    capability_id: str
    status: CheckStatus
    weight: int
    detail: str
    mandatory: bool = False
    backed_by: tuple[str, ...] = ()


@dataclass
class QualityDecision:
    passed: bool
    outcome: Outcome
    score: int
    checks: list[QualityCheck] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "outcome": self.outcome,
            "score": self.score,
            "violations": self.violations,
            "checks": [
                {
                    "check": c.check,
                    "capability_id": c.capability_id,
                    "status": c.status,
                    "weight": c.weight,
                    "mandatory": c.mandatory,
                    "detail": c.detail,
                    "backed_by": list(c.backed_by),
                }
                for c in self.checks
            ],
        }


class QualityGate:
    """Runs the concrete quality controls and scores an artifact 0–100."""

    def __init__(self, min_score: int = 70) -> None:
        self.min_score = min_score

    def evaluate(
        self,
        artifact: str,
        content_type: str = "text/plain",
        *,
        schema: dict[str, Any] | None = None,
        sources: Sequence[str] | None = None,
    ) -> QualityDecision:
        """Score an artifact.

        ``schema`` enables JSON Schema conformance checking for structured
        output; ``sources`` enables grounding — numeric claims that appear
        nowhere in the supplied source material are reported as unsupported.
        """
        checks: list[QualityCheck] = []
        text = artifact or ""
        stripped = text.strip()
        is_markup = content_type in {"text/html", "text/markdown"} or "html" in content_type
        is_json = "json" in content_type

        # 1) Completeness — mandatory: an empty artifact fails hard.
        checks.append(
            self._check(
                "completeness",
                "controls.capability.completeness-ledger",
                status="fail" if not stripped else "pass",
                weight=40,
                mandatory=True,
                detail="artifact is empty" if not stripped else "artifact has content",
            )
        )

        # 2) Anti-template — mandatory: unresolved placeholders fail hard.
        placeholders = sorted({m.group(0).upper() for m in _PLACEHOLDER_PATTERN.finditer(text)})
        checks.append(
            self._check(
                "anti_template",
                "controls.capability.anti-template-heuristics",
                status="fail" if placeholders else "pass",
                weight=25,
                mandatory=True,
                detail=f"unresolved placeholders: {', '.join(placeholders)}" if placeholders else "no placeholder tokens",
            )
        )

        # 3) Answerability — enough substance to be useful.
        length = len(stripped)
        checks.append(
            self._check(
                "answerability",
                "controls.capability.answerability-design",
                status="pass" if length >= 120 else "warn" if length >= 20 else "fail",
                weight=15,
                detail=f"{length} characters of substance",
            )
        )

        # 4) Link integrity — only meaningful for markup artifacts.
        if is_markup:
            empty_links = len(_EMPTY_LINK_PATTERN.findall(text)) + len(_EMPTY_MD_LINK_PATTERN.findall(text))
            checks.append(
                self._check(
                    "link_integrity",
                    "controls.capability.artifact-link-integrity",
                    status="fail" if empty_links else "pass",
                    weight=10,
                    detail=f"{empty_links} empty/placeholder link(s)" if empty_links else "no empty links",
                )
            )
            # 5) Structure — headings/landmarks present.
            has_structure = bool(_HEADING_OR_TAG.search(text))
            checks.append(
                self._check(
                    "structure",
                    "controls.capability.structure",
                    status="pass" if has_structure else "warn",
                    weight=10,
                    detail="structural landmarks present" if has_structure else "no headings/landmarks found",
                )
            )

        # 6) Structured output must actually parse — mandatory for JSON artifacts.
        parsed: Any = None
        if is_json:
            try:
                parsed = json.loads(stripped) if stripped else None
                json_error = None
            except json.JSONDecodeError as exc:
                json_error = f"line {exc.lineno} column {exc.colno}: {exc.msg}"
            checks.append(
                self._check(
                    "json_validity",
                    "controls.capability.artifact-format-constraints",
                    status="fail" if json_error else "pass",
                    weight=35,
                    mandatory=True,
                    detail=f"invalid JSON ({json_error})" if json_error else "valid JSON",
                )
            )

        # 7) Schema conformance, when the caller supplies a contract.
        if schema is not None and parsed is not None:
            violations = _schema_violations(parsed, schema)
            checks.append(
                self._check(
                    "schema_conformance",
                    "controls.capability.artifact-contract-completeness",
                    status="fail" if violations else "pass",
                    weight=25,
                    mandatory=True,
                    detail="; ".join(violations[:5]) if violations else "conforms to the supplied schema",
                )
            )

        # 8) Grounding — numeric claims must be traceable to the source material.
        if sources:
            unsupported = _ungrounded_numbers(text, sources)
            # One stray figure is a warning; a cluster of unsourced numbers is
            # fabrication, and weighted scoring alone would let it through.
            fabricated = len(unsupported) > 2
            checks.append(
                self._check(
                    "grounding",
                    "controls.capability.truth-boundaries",
                    status="fail" if fabricated else "warn" if unsupported else "pass",
                    weight=20,
                    mandatory=fabricated,
                    detail=(
                        f"{len(unsupported)} numeric claim(s) absent from sources: "
                        + ", ".join(unsupported[:5])
                        if unsupported
                        else "all numeric claims appear in the sources"
                    ),
                )
            )

        return self._decide(checks)

    def _check(
        self,
        name: str,
        capability_id: str,
        *,
        status: CheckStatus,
        weight: int,
        detail: str,
        mandatory: bool = False,
    ) -> QualityCheck:
        backing = controls_by_capability(capability_id)
        return QualityCheck(
            check=name,
            capability_id=capability_id,
            status=status,
            weight=weight,
            detail=detail,
            mandatory=mandatory,
            backed_by=tuple(c.control_id for c in backing[:5]),
        )

    def _decide(self, checks: list[QualityCheck]) -> QualityDecision:
        total_weight = sum(c.weight for c in checks) or 1
        earned = 0
        violations: list[str] = []
        hard_fail = False
        for c in checks:
            if c.status == "pass":
                earned += c.weight
            elif c.status == "warn":
                earned += c.weight // 2
            if c.status == "fail":
                violations.append(f"{c.check}: {c.detail}")
                if c.mandatory:
                    hard_fail = True
        score = round(100 * earned / total_weight)
        if hard_fail:
            outcome: Outcome = "reject"
            passed = False
        elif score >= self.min_score:
            outcome = "accept"
            passed = True
        else:
            outcome = "revise"
            passed = False
        return QualityDecision(passed=passed, outcome=outcome, score=score, checks=checks, violations=violations)
