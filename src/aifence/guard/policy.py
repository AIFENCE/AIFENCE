# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import PolicyError
from .schemas import Finding, Outcome

_ALLOWED_OUTCOMES: tuple[Outcome, ...] = (
    "allow",
    "allow_with_limits",
    "redact_or_transform",
    "require_approval",
    "deny",
    "quarantine_and_terminate",
)
_OUTCOME_RANK = {outcome: index for index, outcome in enumerate(_ALLOWED_OUTCOMES)}
_ALLOWED_DOCUMENT_KEYS = {"spec_version", "version", "default", "rules", "tests", "metadata"}
_ALLOWED_RULE_KEYS = {"id", "priority", "description", "match", "effect", "mandatory"}
_ALLOWED_EFFECT_KEYS = {"outcome", "reasons", "constraints"}
_ALLOWED_MATCH_KEYS = {
    "action_types",
    "tools",
    "operations",
    "targets",
    "environment",
    "destinations",
    "detector_categories",
    "finding_severities",
    "detectors",
    "data_classes",
    "credential_scopes",
    "principal_types",
    "principal_ids",
    "agent_ids",
    "workload_identities",
    "models",
    "approved_scope",
    "labels",
    "min_risk",
    "max_risk",
    "destructive",
    "reversible",
    "external_effect",
    "amount_gte",
    "amount_lte",
    "delegation_depth_gte",
    "delegation_depth_lte",
}
_PATTERN_MATCH_KEYS = {
    "action_types",
    "tools",
    "operations",
    "targets",
    "environment",
    "destinations",
    "detector_categories",
    "finding_severities",
    "detectors",
    "data_classes",
    "credential_scopes",
    "principal_types",
    "principal_ids",
    "agent_ids",
    "workload_identities",
    "models",
    "approved_scope",
}
_BOOLEAN_MATCH_KEYS = {"destructive", "reversible", "external_effect"}
_NUMBER_MATCH_KEYS = {
    "min_risk",
    "max_risk",
    "amount_gte",
    "amount_lte",
    "delegation_depth_gte",
    "delegation_depth_lte",
}
_MINIMUM_CONSTRAINTS = {
    "approval_ttl_seconds",
    "capability_ttl_seconds",
    "max_amount_usd",
    "max_capability_uses",
    "max_messages",
    "max_records",
    "max_recipients",
    "max_response_bytes",
}
_OR_CONSTRAINTS = {
    "bind_amount",
    "buffered_response_required",
    "dual_control",
    "isolate_untrusted_content",
    "open_incident",
    "quarantine_artifact",
    "read_only",
    "redact_secrets",
    "require_reregistration",
    "retry_after_dependency_recovery",
    "revoke_capabilities",
    "revoke_exposed_credentials",
    "sandbox_required",
    "terminate_descendants",
}
_AND_CONSTRAINTS = {"issue_capability"}
_INTERSECTION_CONSTRAINTS = {
    "allowed_destinations",
    "allowed_recipients",
    "allowed_resources",
}
_UNION_CONSTRAINTS = {"required_controls"}


@dataclass(frozen=True)
class PolicyResult:
    outcome: Outcome
    reasons: list[str]
    constraints: dict[str, Any]
    policy_version: str
    matched_rule: str


@dataclass(frozen=True)
class _DocumentResult:
    outcome: Outcome
    reasons: list[str]
    constraints: dict[str, Any]
    matched_rules: list[str]


def load_baseline_policy(path: str | Path | None = None) -> dict[str, Any]:
    if path is not None:
        configured = Path(path)
        if not configured.is_file():
            raise PolicyError(f"configured policy file does not exist: {configured}")
        document = json.loads(configured.read_text())
        validate_policy_document(document)
        return document
    package_file = Path(__file__).with_name("baseline_policy.json")
    if package_file.is_file():
        return json.loads(package_file.read_text())
    repository_file = Path(__file__).parents[2] / "policies" / "baseline.json"
    return json.loads(repository_file.read_text())


def validate_policy_document(document: dict[str, Any]) -> None:
    if not isinstance(document, dict):
        raise PolicyError("policy document must be an object")
    unknown_document_keys = set(document) - _ALLOWED_DOCUMENT_KEYS
    if unknown_document_keys:
        raise PolicyError(
            "policy document contains unsupported fields",
            details={"fields": sorted(unknown_document_keys)},
        )
    if document.get("spec_version") != "agentdance.policy.v1":
        raise PolicyError("policy spec_version must be agentdance.policy.v1")
    version = document.get("version")
    if not isinstance(version, str) or not version or len(version) > 128:
        raise PolicyError("policy version must be a non-empty string of at most 128 characters")
    _validate_effect(document.get("default"), "policy default")
    rules = document.get("rules")
    if not isinstance(rules, list) or len(rules) > 1000:
        raise PolicyError("policy rules must be an array with at most 1000 entries")
    ids: set[str] = set()
    custom_constraints: dict[str, Any] = {}
    _record_custom_constraints(document["default"].get("constraints", {}), custom_constraints)
    tests = document.get("tests", [])
    if not isinstance(tests, list) or len(tests) > 1000:
        raise PolicyError("policy tests must be an array with at most 1000 entries")
    for index, case in enumerate(tests):
        if not isinstance(case, dict) or set(case) - {"name", "request", "findings", "risk_score", "expected_outcomes"}:
            raise PolicyError(f"policy test at index {index} has unsupported fields")
        if not isinstance(case.get("name"), str) or not case["name"]:
            raise PolicyError(f"policy test at index {index} requires a name")
        if not isinstance(case.get("request"), dict):
            raise PolicyError(f"policy test {case['name']} requires a request object")
        expected = case.get("expected_outcomes")
        if not isinstance(expected, list) or not expected or any(item not in _ALLOWED_OUTCOMES for item in expected):
            raise PolicyError(f"policy test {case['name']} has invalid expected_outcomes")
        findings = case.get("findings", [])
        if not isinstance(findings, list):
            raise PolicyError(f"policy test {case['name']} findings must be an array")
        risk = case.get("risk_score", 0)
        if isinstance(risk, bool) or not isinstance(risk, int) or not 0 <= risk <= 100:
            raise PolicyError(f"policy test {case['name']} risk_score must be 0 through 100")
    metadata = document.get("metadata", {})
    if not isinstance(metadata, dict):
        raise PolicyError("policy metadata must be an object")
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise PolicyError(f"policy rule at index {index} must be an object")
        unknown_rule_keys = set(rule) - _ALLOWED_RULE_KEYS
        if unknown_rule_keys:
            raise PolicyError(
                f"policy rule at index {index} contains unsupported fields",
                details={"fields": sorted(unknown_rule_keys)},
            )
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id or len(rule_id) > 128:
            raise PolicyError(f"policy rule at index {index} has an invalid id")
        if rule_id in ids:
            raise PolicyError(f"duplicate policy rule id: {rule_id}")
        ids.add(rule_id)
        priority = rule.get("priority")
        if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 10000:
            raise PolicyError(f"policy rule {rule_id} has an invalid priority")
        description = rule.get("description")
        if description is not None and (
            not isinstance(description, str) or not description or len(description) > 2048
        ):
            raise PolicyError(f"policy rule {rule_id} has an invalid description")
        mandatory = rule.get("mandatory")
        if mandatory is not None and not isinstance(mandatory, bool):
            raise PolicyError(f"policy rule {rule_id} mandatory must be boolean")
        _validate_match(rule.get("match", {}), rule_id)
        _validate_effect(rule.get("effect"), f"policy rule {rule_id}")
        _record_custom_constraints(rule["effect"].get("constraints", {}), custom_constraints)


def _validate_match(match: Any, rule_id: str) -> None:
    if not isinstance(match, dict):
        raise PolicyError(f"policy rule {rule_id} match must be an object")
    unknown = set(match) - _ALLOWED_MATCH_KEYS
    if unknown:
        raise PolicyError(
            f"policy rule {rule_id} contains unsupported match predicates",
            details={"predicates": sorted(unknown)},
        )
    for key in _PATTERN_MATCH_KEYS.intersection(match):
        value = match[key]
        if (
            not isinstance(value, list)
            or not value
            or len(value) > 512
            or not all(isinstance(item, str) and item and len(item) <= 2048 for item in value)
        ):
            raise PolicyError(f"policy rule {rule_id} predicate {key} must be non-empty strings")
    for key in _BOOLEAN_MATCH_KEYS.intersection(match):
        if not isinstance(match[key], bool):
            raise PolicyError(f"policy rule {rule_id} predicate {key} must be boolean")
    for key in _NUMBER_MATCH_KEYS.intersection(match):
        value = match[key]
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise PolicyError(f"policy rule {rule_id} predicate {key} must be numeric")
    labels = match.get("labels")
    if labels is not None and (
        not isinstance(labels, dict)
        or len(labels) > 128
        or not all(
            isinstance(key, str)
            and key
            and len(key) <= 255
            and isinstance(value, str)
            and value
            and len(value) <= 2048
            for key, value in labels.items()
        )
    ):
        raise PolicyError(f"policy rule {rule_id} labels must map non-empty strings to patterns")
    if "min_risk" in match and not 0 <= float(match["min_risk"]) <= 100:
        raise PolicyError(f"policy rule {rule_id} min_risk must be between 0 and 100")
    if "max_risk" in match and not 0 <= float(match["max_risk"]) <= 100:
        raise PolicyError(f"policy rule {rule_id} max_risk must be between 0 and 100")
    if "min_risk" in match and "max_risk" in match and match["min_risk"] > match["max_risk"]:
        raise PolicyError(f"policy rule {rule_id} risk range is inverted")
    if "amount_gte" in match and float(match["amount_gte"]) < 0:
        raise PolicyError(f"policy rule {rule_id} amount_gte cannot be negative")
    if "amount_lte" in match and float(match["amount_lte"]) < 0:
        raise PolicyError(f"policy rule {rule_id} amount_lte cannot be negative")
    if "amount_gte" in match and "amount_lte" in match and match["amount_gte"] > match["amount_lte"]:
        raise PolicyError(f"policy rule {rule_id} amount range is inverted")
    for key in ("delegation_depth_gte", "delegation_depth_lte"):
        if key in match and (not isinstance(match[key], int) or match[key] < 0 or match[key] > 32):
            raise PolicyError(f"policy rule {rule_id} {key} must be an integer from 0 through 32")
    if (
        "delegation_depth_gte" in match
        and "delegation_depth_lte" in match
        and match["delegation_depth_gte"] > match["delegation_depth_lte"]
    ):
        raise PolicyError(f"policy rule {rule_id} delegation depth range is inverted")


def _validate_effect(effect: Any, location: str) -> None:
    if not isinstance(effect, dict):
        raise PolicyError(f"{location} effect must be an object")
    unknown = set(effect) - _ALLOWED_EFFECT_KEYS
    if unknown:
        raise PolicyError(
            f"{location} effect contains unsupported fields",
            details={"fields": sorted(unknown)},
        )
    if effect.get("outcome") not in _OUTCOME_RANK:
        raise PolicyError(f"{location} outcome is invalid")
    reasons = effect.get("reasons", [])
    if (
        not isinstance(reasons, list)
        or len(reasons) > 128
        or not all(isinstance(reason, str) and reason and len(reason) <= 2048 for reason in reasons)
    ):
        raise PolicyError(f"{location} reasons must be non-empty strings")
    constraints = effect.get("constraints", {})
    if not isinstance(constraints, dict) or len(constraints) > 128:
        raise PolicyError(f"{location} constraints must be an object with at most 128 entries")
    for key, value in constraints.items():
        _validate_constraint(key, value, location)


def _validate_constraint(key: Any, value: Any, location: str) -> None:
    if not isinstance(key, str) or not key or len(key) > 128:
        raise PolicyError(f"{location} contains an invalid constraint name")
    if key in _MINIMUM_CONSTRAINTS:
        if isinstance(value, bool) or not isinstance(value, int | float) or value < 0:
            raise PolicyError(f"{location} constraint {key} must be a non-negative number")
        if key in {
            "approval_ttl_seconds",
            "capability_ttl_seconds",
            "max_capability_uses",
            "max_messages",
            "max_records",
            "max_recipients",
            "max_response_bytes",
        } and not isinstance(value, int):
            raise PolicyError(f"{location} constraint {key} must be an integer")
        if key == "max_capability_uses" and not 1 <= value <= 100:
            raise PolicyError("max_capability_uses must be from 1 through 100")
        if key == "capability_ttl_seconds" and not 5 <= value <= 300:
            raise PolicyError("capability_ttl_seconds must be from 5 through 300")
        if key == "approval_ttl_seconds" and not 5 <= value <= 86400:
            raise PolicyError("approval_ttl_seconds must be from 5 through 86400")
        return
    if key in _OR_CONSTRAINTS or key in _AND_CONSTRAINTS:
        if not isinstance(value, bool):
            raise PolicyError(f"{location} constraint {key} must be boolean")
        return
    if key in _INTERSECTION_CONSTRAINTS or key in _UNION_CONSTRAINTS:
        if (
            not isinstance(value, list)
            or len(value) > 512
            or not all(isinstance(item, str) and item and len(item) <= 2048 for item in value)
        ):
            raise PolicyError(f"{location} constraint {key} must be an array of non-empty strings")
        return
    if not key.startswith(("x-", "x_")):
        raise PolicyError(
            f"{location} contains unsupported constraint {key}; custom constraints require x- or x_ prefix"
        )
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise PolicyError(f"{location} custom constraint {key} is not valid JSON") from exc


def _record_custom_constraints(constraints: dict[str, Any], observed: dict[str, Any]) -> None:
    for key, value in constraints.items():
        if not key.startswith(("x-", "x_")):
            continue
        if key in observed and observed[key] != value:
            raise PolicyError(
                f"custom constraint {key} must have one invariant value within a policy document"
            )
        observed[key] = value


class PolicyEngine:
    def __init__(self, baseline: dict[str, Any] | None = None) -> None:
        self.baseline = baseline or load_baseline_policy()
        validate_policy_document(self.baseline)

    def evaluate(
        self,
        input_document: dict[str, Any],
        findings: list[Finding],
        risk_score: int,
        tenant_policy: dict[str, Any] | None = None,
    ) -> PolicyResult:
        if tenant_policy is not None:
            validate_policy_document(tenant_policy)
        context = self._context(input_document, findings, risk_score)
        baseline_result = self._evaluate_document(self.baseline, context, "baseline")
        results = [baseline_result]
        version = self.baseline["version"]
        if tenant_policy is not None:
            results.append(self._evaluate_document(tenant_policy, context, "tenant"))
            version = f"{version}+{tenant_policy['version']}"

        outcome = max((result.outcome for result in results), key=_OUTCOME_RANK.__getitem__)
        reasons: list[str] = []
        constraints: dict[str, Any] = {}
        matched_rules: list[str] = []
        for result in results:
            for reason in result.reasons:
                if reason not in reasons:
                    reasons.append(reason)
            constraints = _merge_constraints(constraints, result.constraints)
            matched_rules.extend(result.matched_rules)
        return PolicyResult(
            outcome=outcome,
            reasons=reasons,
            constraints=constraints,
            policy_version=version,
            matched_rule=",".join(matched_rules),
        )

    def _evaluate_document(
        self,
        document: dict[str, Any],
        context: dict[str, Any],
        source: str,
    ) -> _DocumentResult:
        matched = [
            rule
            for rule in sorted(document["rules"], key=lambda item: (-item["priority"], item["id"]))
            if self._matches(rule.get("match", {}), context)
        ]
        if not matched:
            default = document["default"]
            return _DocumentResult(
                outcome=default["outcome"],
                reasons=list(default.get("reasons", [])),
                constraints=dict(default.get("constraints", {})),
                matched_rules=[f"{source}:default"],
            )
        outcome = max(
            (rule["effect"]["outcome"] for rule in matched),
            key=_OUTCOME_RANK.__getitem__,
        )
        reasons: list[str] = []
        constraints: dict[str, Any] = {}
        ids: list[str] = []
        for rule in matched:
            ids.append(f"{source}:{rule['id']}")
            for reason in rule["effect"].get("reasons", []):
                if reason not in reasons:
                    reasons.append(reason)
            constraints = _merge_constraints(constraints, rule["effect"].get("constraints", {}))
        return _DocumentResult(outcome, reasons, constraints, ids)

    @staticmethod
    def _context(
        input_document: dict[str, Any], findings: list[Finding], risk_score: int
    ) -> dict[str, Any]:
        return {
            **input_document,
            "finding_categories": {finding.category for finding in findings},
            "finding_severities": {finding.severity for finding in findings},
            "detectors": {finding.detector for finding in findings},
            "risk_score": risk_score,
        }

    def _matches(self, match: dict[str, Any], context: dict[str, Any]) -> bool:
        action = context["action"]
        security = context["security_context"]
        principal = context.get("principal", {"type": "", "id": ""})
        agent = context.get(
            "agent",
            {"id": "", "workload_identity": "", "model": ""},
        )
        objective = context.get("objective", {"approved_scope": [], "delegation_depth": 0})
        pattern_fields: tuple[tuple[str, str], ...] = (
            ("action_types", str(action["type"])),
            ("tools", str(action.get("tool") or "")),
            ("operations", str(action["operation"])),
            ("targets", str(action.get("target") or "")),
            ("environment", str(security["environment"])),
            ("destinations", str(security.get("network_destination") or "")),
            ("principal_types", str(principal["type"])),
            ("principal_ids", str(principal["id"])),
            ("agent_ids", str(agent["id"])),
            ("workload_identities", str(agent["workload_identity"])),
            ("models", str(agent["model"])),
        )
        for key, value in pattern_fields:
            if key in match and not self._glob_any(value, match[key]):
                return False
        set_fields: tuple[tuple[str, set[str]], ...] = (
            ("detector_categories", context["finding_categories"]),
            ("finding_severities", context["finding_severities"]),
            ("detectors", context["detectors"]),
            ("data_classes", set(security.get("data_classes", []))),
            ("credential_scopes", set(security.get("credential_scope", []))),
            ("approved_scope", set(objective.get("approved_scope", []))),
        )
        for key, values in set_fields:
            if key in match and not self._patterns_intersect(values, match[key]):
                return False
        labels = security.get("labels", {})
        for key, pattern in match.get("labels", {}).items():
            if key not in labels or not fnmatch.fnmatchcase(str(labels[key]).lower(), pattern.lower()):
                return False
        if "min_risk" in match and context["risk_score"] < float(match["min_risk"]):
            return False
        if "max_risk" in match and context["risk_score"] > float(match["max_risk"]):
            return False
        for key in _BOOLEAN_MATCH_KEYS:
            if key in match and bool(action.get(key)) != match[key]:
                return False
        amount = action.get("amount_usd")
        if "amount_gte" in match and (amount is None or float(amount) < float(match["amount_gte"])):
            return False
        if "amount_lte" in match and (amount is None or float(amount) > float(match["amount_lte"])):
            return False
        delegation_depth = int(objective.get("delegation_depth", 0))
        if "delegation_depth_gte" in match and delegation_depth < match["delegation_depth_gte"]:
            return False
        if "delegation_depth_lte" in match and delegation_depth > match["delegation_depth_lte"]:
            return False
        return True

    @staticmethod
    def _glob_any(value: str, patterns: list[str]) -> bool:
        return any(fnmatch.fnmatchcase(value.lower(), pattern.lower()) for pattern in patterns)

    @classmethod
    def _patterns_intersect(cls, values: set[str], patterns: list[str]) -> bool:
        return any(cls._glob_any(value, patterns) for value in values)


def _merge_constraints(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for key, value in incoming.items():
        if key not in merged:
            merged[key] = value
            continue
        current = merged[key]
        if current == value:
            continue
        if key in _MINIMUM_CONSTRAINTS:
            merged[key] = min(current, value)
        elif key in _OR_CONSTRAINTS:
            merged[key] = bool(current) or bool(value)
        elif key in _AND_CONSTRAINTS:
            merged[key] = bool(current) and bool(value)
        elif key in _INTERSECTION_CONSTRAINTS:
            allowed = set(value)
            merged[key] = [item for item in current if item in allowed]
        elif key in _UNION_CONSTRAINTS:
            merged[key] = list(dict.fromkeys([*current, *value]))
        else:
            raise PolicyError(
                f"conflicting invariant custom constraint {key}",
                details={"existing": current, "incoming": value},
            )
    return merged


def run_embedded_policy_tests(baseline: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    """Execute policy-owned regression tests before publication or activation."""
    validate_policy_document(document)
    engine = PolicyEngine(baseline)
    results: list[dict[str, Any]] = []
    for case in document.get("tests", []):
        findings = [Finding.model_validate(item) for item in case.get("findings", [])]
        evaluated = engine.evaluate(case["request"], findings, int(case.get("risk_score", 0)), document)
        passed = evaluated.outcome in case["expected_outcomes"]
        results.append({"name": case["name"], "passed": passed, "outcome": evaluated.outcome,
                        "expected_outcomes": case["expected_outcomes"], "matched_rule": evaluated.matched_rule})
    passed_count = sum(bool(item["passed"]) for item in results)
    return {"valid": True, "tests_total": len(results), "tests_passed": passed_count == len(results),
            "passed": passed_count, "failed": len(results)-passed_count, "results": results}
