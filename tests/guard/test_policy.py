# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from aifence.guard.policy import PolicyEngine
from aifence.guard.schemas import Finding


def base_input() -> dict[str, object]:
    return {
        "action": {
            "type": "tool.call",
            "tool": "orders.read",
            "operation": "read",
            "destructive": False,
            "reversible": True,
            "external_effect": False,
            "amount_usd": None,
        },
        "security_context": {"environment": "production", "data_classes": ["customer"]},
    }


def test_read_only_low_risk_is_allowed() -> None:
    result = PolicyEngine().evaluate(base_input(), [], 10)
    assert result.outcome == "allow"


def test_tenant_policy_cannot_weaken_mandatory_control() -> None:
    finding = Finding(
        detector="secret-detector",
        category="data.secret_exposure",
        severity="critical",
        confidence=1,
        evidence="secret detected",
    )
    tenant_policy = {
        "spec_version": "agentdance.policy.v1",
        "version": "tenant-1",
        "default": {"outcome": "allow", "reasons": ["allow"], "constraints": {}},
        "rules": [],
    }
    result = PolicyEngine().evaluate(base_input(), [finding], 95, tenant_policy)
    assert result.outcome == "deny"


def test_all_matching_rules_are_composed_and_strictest_outcome_wins() -> None:
    request = base_input()
    request["action"] = {
        "type": "model.request",
        "tool": "provider.primary",
        "operation": "invoke",
        "destructive": False,
        "reversible": True,
        "external_effect": True,
        "amount_usd": None,
    }
    finding = Finding(
        detector="prompt-injection-detector",
        category="prompt_injection.detected",
        severity="high",
        confidence=0.98,
        evidence="untrusted instruction",
    )

    result = PolicyEngine().evaluate(request, [finding], 20)

    assert result.outcome == "deny"
    assert result.constraints["isolate_untrusted_content"] is True
    assert result.constraints["buffered_response_required"] is True
    assert result.constraints["redact_secrets"] is True
    assert "baseline:prompt-injection-with-external-effect" in result.matched_rule
    assert "baseline:model-provider-request" in result.matched_rule


def test_tenant_default_allow_cannot_weaken_baseline_default() -> None:
    request = base_input()
    request["action"] = {
        "type": "tool.call",
        "tool": "orders.update",
        "operation": "mutate",
        "destructive": False,
        "reversible": False,
        "external_effect": False,
        "amount_usd": None,
    }
    tenant_policy = {
        "spec_version": "agentdance.policy.v1",
        "version": "tenant-default-allow",
        "default": {"outcome": "allow", "reasons": ["tenant allow"], "constraints": {}},
        "rules": [],
    }

    result = PolicyEngine().evaluate(request, [], 10, tenant_policy)

    assert result.outcome == "require_approval"
    assert "baseline:default" in result.matched_rule
    assert "tenant:default" in result.matched_rule


def test_tenant_policy_can_tighten_baseline_allow() -> None:
    tenant_policy = {
        "spec_version": "agentdance.policy.v1",
        "version": "tenant-deny-reads",
        "default": {"outcome": "allow", "reasons": ["tenant default"], "constraints": {}},
        "rules": [
            {
                "id": "deny-customer-reads",
                "priority": 100,
                "match": {"operations": ["read"], "data_classes": ["customer"]},
                "effect": {
                    "outcome": "deny",
                    "reasons": ["tenant blocks customer reads"],
                    "constraints": {"issue_capability": False},
                },
            }
        ],
    }

    result = PolicyEngine().evaluate(base_input(), [], 10, tenant_policy)

    assert result.outcome == "deny"
    assert result.constraints["issue_capability"] is False
    assert "tenant:deny-customer-reads" in result.matched_rule


def test_matching_constraints_merge_by_security_semantics() -> None:
    baseline = {
        "spec_version": "agentdance.policy.v1",
        "version": "constraint-composition",
        "default": {"outcome": "deny", "reasons": ["default"], "constraints": {}},
        "rules": [
            {
                "id": "broad-limit",
                "priority": 20,
                "match": {"operations": ["read"]},
                "effect": {
                    "outcome": "allow_with_limits",
                    "reasons": ["broad"],
                    "constraints": {
                        "max_records": 100,
                        "allowed_destinations": ["api.internal", "archive.internal"],
                        "required_controls": ["audit"],
                    },
                },
            },
            {
                "id": "narrow-limit",
                "priority": 10,
                "match": {"data_classes": ["customer"]},
                "effect": {
                    "outcome": "allow_with_limits",
                    "reasons": ["narrow"],
                    "constraints": {
                        "max_records": 50,
                        "allowed_destinations": ["api.internal", "other.internal"],
                        "required_controls": ["redaction"],
                    },
                },
            },
        ],
    }

    result = PolicyEngine(baseline).evaluate(base_input(), [], 10)

    assert result.outcome == "allow_with_limits"
    assert result.constraints["max_records"] == 50
    assert result.constraints["allowed_destinations"] == ["api.internal"]
    assert result.constraints["required_controls"] == ["audit", "redaction"]


def test_unknown_match_predicate_is_rejected() -> None:
    from pytest import raises

    from aifence.guard.errors import PolicyError

    policy = {
        "spec_version": "agentdance.policy.v1",
        "version": "invalid",
        "default": {"outcome": "deny", "reasons": ["default"], "constraints": {}},
        "rules": [
            {
                "id": "inert-typo",
                "priority": 1,
                "match": {"operatons": ["read"]},
                "effect": {"outcome": "deny", "reasons": ["deny"], "constraints": {}},
            }
        ],
    }

    with raises(PolicyError, match="unsupported match predicates"):
        PolicyEngine(policy)
