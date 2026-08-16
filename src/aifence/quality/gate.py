# SPDX-License-Identifier: AGPL-3.0-or-later
"""The AIFENCE quality gate.

A deterministic, dependency-free gate that runs concrete, checkable quality
controls over an AI-generated artifact and attributes each check back to a
canonical BizIQ capability. This is the fast in-process gate that fronts the
fence; deep, family-native evaluation is delegated to the BizIQ runtime under
``quality/`` and is out of scope for this bridge.

The gate returns one of three outcomes, mirroring how the fence treats it
downstream: ``accept`` (pass to guard), ``revise`` (soft-fail, quality too low),
or ``reject`` (hard-fail on a mandatory control).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

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

    def evaluate(self, artifact: str, content_type: str = "text/plain") -> QualityDecision:
        checks: list[QualityCheck] = []
        text = artifact or ""
        stripped = text.strip()
        is_markup = content_type in {"text/html", "text/markdown"} or "html" in content_type

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
