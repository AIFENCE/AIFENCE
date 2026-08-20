# SPDX-License-Identifier: AGPL-3.0-or-later
"""Fast deterministic AIFENCE admission-quality gate.

This module is intentionally *not* the full AIFENCE Quality 2.0 runtime.  It is
the synchronous admission gate used by ``/v1/fence/submit``: bounded,
deterministic checks that are safe to execute in the request path.  The larger
``quality/`` runtime plans family-native evidence and validation workflows and
is exposed separately as the deep-quality capability.

Every admission finding has a stable machine-readable identifier.  Human text
may evolve; automation should key on ``finding_id``/``capability_id`` instead.
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
Severity = Literal["info", "low", "medium", "high", "critical"]

ADMISSION_EVALUATOR_VERSION = "1.0"
ADMISSION_PROFILE = "admission/default-v1"

_PLACEHOLDER_PATTERN = re.compile(
    r"\b(TODO|TBD|FIXME|XXX|PLACEHOLDER|LOREM IPSUM|INSERT[ _]|CHANGEME)\b",
    re.IGNORECASE,
)
_EMPTY_LINK_PATTERN = re.compile(
    r'''href\s*=\s*["'](?:\s*|#|javascript:void\(0\))["']''',
    re.IGNORECASE,
)
_EMPTY_MD_LINK_PATTERN = re.compile(r"\]\(\s*\)")
_HEADING_OR_TAG = re.compile(
    r"(^#{1,6}\s)|(<h[1-6][\s>])|(<section|<article|<main)",
    re.IGNORECASE | re.MULTILINE,
)
_CLAIM_NUMBER = re.compile(
    r"(?<![\w.])(?:\$\s?)?\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\b\d{2,}\b"
)


def _normalize_number(value: str) -> str:
    return value.replace(",", "").replace("$", "").strip()


def _ungrounded_numbers(text: str, sources: Sequence[str]) -> list[str]:
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
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
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
                    f"{key}/{v}"
                    if not v.startswith("<root>")
                    else f"{key}: {v.split(': ', 1)[-1]}"
                    for v in _structural_violations(document[key], subschema)
                )
    return violations


@dataclass(frozen=True)
class QualityCheck:
    finding_id: str
    check: str
    capability_id: str
    status: CheckStatus
    weight: int
    detail: str
    mandatory: bool = False
    backed_by: tuple[str, ...] = ()
    severity: Severity = "info"
    remediation: str = ""
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "finding_id": self.finding_id,
            "check": self.check,
            "capability_id": self.capability_id,
            "status": self.status,
            "severity": self.severity,
            "weight": self.weight,
            "mandatory": self.mandatory,
            "detail": self.detail,
            "remediation": self.remediation,
            "evidence": list(self.evidence),
            "backed_by": list(self.backed_by),
        }


@dataclass
class QualityDecision:
    passed: bool
    outcome: Outcome
    score: int
    checks: list[QualityCheck] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    mode: str = "admission"
    profile: str = ADMISSION_PROFILE
    evaluator_version: str = ADMISSION_EVALUATOR_VERSION

    def to_dict(self) -> dict[str, object]:
        findings = [c.to_dict() for c in self.checks if c.status != "pass"]
        return {
            "passed": self.passed,
            "outcome": self.outcome,
            "score": self.score,
            "mode": self.mode,
            "profile": self.profile,
            "evaluator_version": self.evaluator_version,
            "violations": self.violations,
            "findings": findings,
            # ``checks`` remains for backwards compatibility and includes passes.
            "checks": [c.to_dict() for c in self.checks],
        }


class QualityGate:
    """Run bounded admission controls and score an artifact from 0 to 100."""

    def __init__(self, min_score: int = 70, profile: str = ADMISSION_PROFILE) -> None:
        self.min_score = min_score
        self.profile = profile

    def evaluate(
        self,
        artifact: str,
        content_type: str = "text/plain",
        *,
        schema: dict[str, Any] | None = None,
        sources: Sequence[str] | None = None,
    ) -> QualityDecision:
        checks: list[QualityCheck] = []
        text = artifact or ""
        stripped = text.strip()
        is_markup = content_type in {"text/html", "text/markdown"} or "html" in content_type
        is_json = "json" in content_type

        checks.append(
            self._check(
                "AQ-COMPLETE-001",
                "completeness",
                "controls.capability.completeness-ledger",
                status="fail" if not stripped else "pass",
                weight=40,
                mandatory=True,
                severity="critical" if not stripped else "info",
                detail="artifact is empty" if not stripped else "artifact has content",
                remediation="Provide the complete artifact before submitting it to the fence.",
                evidence=("artifact.trimmed_length=0",) if not stripped else (),
            )
        )

        placeholders = sorted({m.group(0).upper() for m in _PLACEHOLDER_PATTERN.finditer(text)})
        checks.append(
            self._check(
                "AQ-TEMPLATE-001",
                "anti_template",
                "controls.capability.anti-template-heuristics",
                status="fail" if placeholders else "pass",
                weight=25,
                mandatory=True,
                severity="high" if placeholders else "info",
                detail=(
                    f"unresolved placeholders: {', '.join(placeholders)}"
                    if placeholders
                    else "no placeholder tokens"
                ),
                remediation="Replace unresolved template markers with final content.",
                evidence=tuple(placeholders),
            )
        )

        length = len(stripped)
        status: CheckStatus = "pass" if length >= 120 else "warn" if length >= 20 else "fail"
        checks.append(
            self._check(
                "AQ-ANSWER-001",
                "answerability",
                "controls.capability.answerability-design",
                status=status,
                weight=15,
                severity="medium" if status == "fail" else "low" if status == "warn" else "info",
                detail=f"{length} characters of substance",
                remediation="Add enough task-relevant substance for the receiver to act on the result.",
                evidence=(f"artifact.trimmed_length={length}",),
            )
        )

        if is_markup:
            empty_links = len(_EMPTY_LINK_PATTERN.findall(text)) + len(_EMPTY_MD_LINK_PATTERN.findall(text))
            checks.append(
                self._check(
                    "AQ-LINK-001",
                    "link_integrity",
                    "controls.capability.artifact-link-integrity",
                    status="fail" if empty_links else "pass",
                    weight=10,
                    severity="medium" if empty_links else "info",
                    detail=(
                        f"{empty_links} empty/placeholder link(s)" if empty_links else "no empty links"
                    ),
                    remediation="Replace empty links with valid destinations or remove the inactive affordance.",
                    evidence=(f"empty_links={empty_links}",) if empty_links else (),
                )
            )
            has_structure = bool(_HEADING_OR_TAG.search(text))
            checks.append(
                self._check(
                    "AQ-STRUCTURE-001",
                    "structure",
                    "controls.capability.structure",
                    status="pass" if has_structure else "warn",
                    weight=10,
                    severity="low" if not has_structure else "info",
                    detail="structural landmarks present" if has_structure else "no headings/landmarks found",
                    remediation="Add meaningful headings or semantic landmarks for non-trivial markup.",
                )
            )

        parsed: Any = None
        json_error: str | None = None
        if is_json:
            try:
                parsed = json.loads(stripped) if stripped else None
            except json.JSONDecodeError as exc:
                json_error = f"line {exc.lineno} column {exc.colno}: {exc.msg}"
            checks.append(
                self._check(
                    "AQ-JSON-001",
                    "json_validity",
                    "controls.capability.artifact-format-constraints",
                    status="fail" if json_error else "pass",
                    weight=35,
                    mandatory=True,
                    severity="critical" if json_error else "info",
                    detail=f"invalid JSON ({json_error})" if json_error else "valid JSON",
                    remediation="Emit syntactically valid JSON matching the declared content type.",
                    evidence=(json_error,) if json_error else (),
                )
            )

        if schema is not None and parsed is not None:
            violations = _schema_violations(parsed, schema)
            checks.append(
                self._check(
                    "AQ-SCHEMA-001",
                    "schema_conformance",
                    "controls.capability.artifact-contract-completeness",
                    status="fail" if violations else "pass",
                    weight=25,
                    mandatory=True,
                    severity="critical" if violations else "info",
                    detail="; ".join(violations[:5]) if violations else "conforms to the supplied schema",
                    remediation="Correct the structured output so it conforms to the supplied JSON Schema.",
                    evidence=tuple(violations[:10]),
                )
            )

        if sources:
            unsupported = _ungrounded_numbers(text, sources)
            fabricated = len(unsupported) > 2
            status = "fail" if fabricated else "warn" if unsupported else "pass"
            checks.append(
                self._check(
                    "AQ-GROUND-001",
                    "grounding",
                    "controls.capability.truth-boundaries",
                    status=status,
                    weight=20,
                    mandatory=fabricated,
                    severity="high" if fabricated else "medium" if unsupported else "info",
                    detail=(
                        f"{len(unsupported)} numeric claim(s) absent from sources: "
                        + ", ".join(unsupported[:5])
                        if unsupported
                        else "all numeric claims appear in the sources"
                    ),
                    remediation="Remove unsupported figures or provide source material containing the claims.",
                    evidence=tuple(unsupported[:10]),
                )
            )

        return self._decide(checks)

    def _check(
        self,
        finding_id: str,
        name: str,
        capability_id: str,
        *,
        status: CheckStatus,
        weight: int,
        detail: str,
        mandatory: bool = False,
        severity: Severity = "info",
        remediation: str = "",
        evidence: tuple[str, ...] = (),
    ) -> QualityCheck:
        backing = controls_by_capability(capability_id)
        return QualityCheck(
            finding_id=finding_id,
            check=name,
            capability_id=capability_id,
            status=status,
            weight=weight,
            detail=detail,
            mandatory=mandatory,
            backed_by=tuple(c.control_id for c in backing[:5]),
            severity=severity,
            remediation=remediation,
            evidence=evidence,
        )

    def _decide(self, checks: list[QualityCheck]) -> QualityDecision:
        total_weight = sum(c.weight for c in checks) or 1
        earned = 0
        violations: list[str] = []
        hard_fail = False
        for check in checks:
            if check.status == "pass":
                earned += check.weight
            elif check.status == "warn":
                earned += check.weight // 2
            if check.status == "fail":
                violations.append(f"{check.check}: {check.detail}")
                if check.mandatory:
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
        return QualityDecision(
            passed=passed,
            outcome=outcome,
            score=score,
            checks=checks,
            violations=violations,
            profile=self.profile,
        )
