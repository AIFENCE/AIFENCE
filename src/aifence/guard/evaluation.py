# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .detectors import calculate_risk, run_detectors
from .models import Agent
from .policy import PolicyEngine, validate_policy_document
from .schemas import DecisionRequest


@dataclass(frozen=True)
class EvaluationCaseResult:
    name: str
    passed: bool
    outcome: str
    risk_score: int
    matched_rule: str
    categories: list[str]
    expected_outcomes: list[str]
    expected_categories: list[str]
    expected_rules: list[str]
    failures: list[str]


@dataclass(frozen=True)
class EvaluationReport:
    corpus_version: str
    policy_version: str
    total: int
    passed: int
    failed: int
    pass_rate: float
    outcome_counts: dict[str, int]
    category_counts: dict[str, int]
    results: list[EvaluationCaseResult]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SecurityEvaluationRunner:
    def __init__(self, policy_engine: PolicyEngine) -> None:
        self.policy_engine = policy_engine

    def run_file(self, path: str | Path, *, policy_document: dict[str, Any] | None = None) -> EvaluationReport:
        document = json.loads(Path(path).read_text())
        return self.run(document, policy_document=policy_document)

    def run(self, corpus: dict[str, Any], *, policy_document: dict[str, Any] | None = None) -> EvaluationReport:
        if policy_document is not None:
            validate_policy_document(policy_document)
        cases = corpus.get("cases")
        if not isinstance(cases, list) or not cases:
            raise ValueError("evaluation corpus must contain at least one case")
        results: list[EvaluationCaseResult] = []
        outcomes: dict[str, int] = {}
        categories: dict[str, int] = {}
        for raw in cases:
            result = self._run_case(raw, policy_document)
            results.append(result)
            outcomes[result.outcome] = outcomes.get(result.outcome, 0) + 1
            for category in result.categories:
                categories[category] = categories.get(category, 0) + 1
        passed = sum(result.passed for result in results)
        selected_policy = policy_document or self.policy_engine.baseline
        policy_version = str(selected_policy.get("version", "unknown"))
        return EvaluationReport(
            corpus_version=str(corpus.get("version", "unknown")),
            policy_version=policy_version,
            total=len(results),
            passed=passed,
            failed=len(results) - passed,
            pass_rate=round(passed / len(results), 6),
            outcome_counts=outcomes,
            category_counts=categories,
            results=results,
        )

    def _run_case(
        self, raw: dict[str, Any], policy_document: dict[str, Any] | None
    ) -> EvaluationCaseResult:
        if not isinstance(raw, dict):
            raise ValueError("evaluation case must be an object")
        request = DecisionRequest.model_validate(raw["request"])
        manifest = raw.get("agent")
        agent = None if manifest is None else self._agent(request, manifest)
        findings = run_detectors(request, agent)
        risk_score = calculate_risk(request, findings)
        evaluated = self.policy_engine.evaluate(
            request.model_dump(mode="json"), findings, risk_score, policy_document
        )
        observed_categories = sorted({finding.category for finding in findings})
        expected_outcomes = [str(value) for value in raw.get("expected_outcomes", [])]
        expected_categories = [str(value) for value in raw.get("expected_categories", [])]
        expected_rules = [str(value) for value in raw.get("expected_rules", [])]
        failures: list[str] = []
        if expected_outcomes and evaluated.outcome not in expected_outcomes:
            failures.append(
                f"outcome {evaluated.outcome!r} not in expected {expected_outcomes!r}"
            )
        missing_categories = sorted(set(expected_categories) - set(observed_categories))
        if missing_categories:
            failures.append(f"missing detector categories: {missing_categories}")
        observed_rules = {
            part.strip().split(":", 1)[-1]
            for part in evaluated.matched_rule.split(",")
            if part.strip()
        }
        if expected_rules and not observed_rules.intersection(expected_rules):
            failures.append(
                f"matched rule {evaluated.matched_rule!r} not in expected {expected_rules!r}"
            )
        prohibited = sorted(set(raw.get("prohibited_categories", [])) & set(observed_categories))
        if prohibited:
            failures.append(f"unexpected detector categories: {prohibited}")
        return EvaluationCaseResult(
            name=str(raw.get("name", "unnamed")),
            passed=not failures,
            outcome=evaluated.outcome,
            risk_score=risk_score,
            matched_rule=evaluated.matched_rule,
            categories=observed_categories,
            expected_outcomes=expected_outcomes,
            expected_categories=expected_categories,
            expected_rules=expected_rules,
            failures=failures,
        )

    @staticmethod
    def _agent(request: DecisionRequest, manifest: dict[str, Any]) -> Agent:
        return Agent(
            id=str(manifest.get("id", request.agent.id)),
            tenant_id="evaluation",
            external_id=str(manifest.get("external_id", request.agent.id)),
            name=str(manifest.get("name", "Evaluation Agent")),
            version=str(manifest.get("version", request.agent.version)),
            workload_identity=str(
                manifest.get("workload_identity", request.agent.workload_identity)
            ),
            model=str(manifest.get("model", request.agent.model)),
            instruction_hash=str(
                manifest.get("instruction_hash", request.agent.instruction_hash)
            ),
            deployment_digest=manifest.get("deployment_digest"),
            manifest_hash="0" * 64,
            allowed_tools=list(manifest.get("allowed_tools", ["*"])),
            allowed_data_classes=list(
                manifest.get("allowed_data_classes", ["customer", "financial", "secret"])
            ),
            status=str(manifest.get("status", "active")),
            metadata_json=dict(manifest.get("metadata", {})),
            created_by_key_id="evaluation",
        )
