# SPDX-License-Identifier: AGPL-3.0-or-later
"""Content-derived data classes, so enforcement does not rely on self-declaration."""
from __future__ import annotations

import pytest

from aifence.guard.content_classes import classify
from aifence.guard.detectors import calculate_risk, run_detectors
from aifence.guard.policy import PolicyEngine, load_baseline_policy
from aifence.guard.schemas import DecisionRequest

CARD_AND_SSN = "Customer card 4111 1111 1111 1111, SSN 123-45-6789 on file."
CLEAN = "Revenue grew 12 percent this quarter across every region we serve."


# --- classifier precision: it feeds a deny path, so false positives matter ---

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("card 4111 1111 1111 1111", "financial"),
        ("SSN 123-45-6789", "government_id"),
        ("AKIAIOSFODNN7EXAMPLE", "credential"),
        ('api_key = "sk_live_abcdefghij1234567890"', "credential"),
        ("-----BEGIN RSA PRIVATE KEY-----", "secret"),
        ("contact jane@example.com", "personal_data"),
        ("patient diagnosis recorded with ICD-10 code", "health"),
    ],
)
def test_classifier_detects_sensitive_content(text: str, expected: str) -> None:
    assert expected in classify(text)


@pytest.mark.parametrize(
    "text",
    [
        CLEAN,
        "order number 4111111111111112 shipped",     # fails the Luhn check
        "ref 666-45-6789",                            # structurally invalid SSN area
        "The commit hash abcdefghij1234567890 was reverted.",  # no assignment context
        "",
    ],
)
def test_classifier_ignores_benign_content(text: str) -> None:
    assert classify(text) == {}


def test_classifier_never_returns_matched_values() -> None:
    result = classify(CARD_AND_SSN)
    rendered = repr(result)
    assert "4111" not in rendered and "123-45-6789" not in rendered


# --- enforcement: observed classes drive the existing rules ---

def _request(content: str, declared: list[str], destination: str) -> DecisionRequest:
    return DecisionRequest.model_validate(
        {
            "trace_id": "trc_test_00000001",
            "principal": {"type": "human", "id": "user-1", "authorization_context": []},
            "agent": {
                "id": "agt_1", "instance_id": "i1", "version": "1.0.0",
                "workload_identity": "spiffe://t/a", "model": "p/m", "instruction_hash": "a" * 64,
            },
            "objective": {"declared_goal": "send", "approved_scope": [], "delegation_depth": 0},
            "action": {
                "type": "tool.call", "tool": "http.post", "operation": "send",
                "target": destination, "arguments": {}, "external_effect": True,
            },
            "security_context": {
                "data_classes": declared, "environment": "production",
                "content": content, "network_destination": destination,
            },
        }
    )


def _categories(request: DecisionRequest) -> set[str]:
    return {finding.category for finding in run_detectors(request, None)}


def test_undeclared_sensitive_content_is_flagged() -> None:
    categories = _categories(_request(CARD_AND_SSN, [], "https://paste.example.com"))
    assert "data.undeclared_sensitive" in categories


def test_undeclared_content_still_triggers_exfiltration() -> None:
    """The core win: under-declaring must not evade the exfiltration rule."""
    categories = _categories(_request(CARD_AND_SSN, [], "https://paste.example.com"))
    assert "data.exfiltration" in categories


def test_declared_sensitive_content_is_not_reported_as_undeclared() -> None:
    categories = _categories(
        _request(CARD_AND_SSN, ["financial", "government_id"], "https://paste.example.com")
    )
    assert "data.undeclared_sensitive" not in categories
    assert "data.exfiltration" in categories


def test_private_destination_does_not_trigger_exfiltration() -> None:
    categories = _categories(_request(CARD_AND_SSN, [], "https://10.0.0.5/internal"))
    assert "data.exfiltration" not in categories


def test_clean_content_raises_no_data_findings() -> None:
    categories = _categories(_request(CLEAN, [], "https://paste.example.com"))
    assert not {c for c in categories if c.startswith("data.")}


def test_credentials_in_content_are_secret_exposure() -> None:
    categories = _categories(
        _request("api_key = 'sk_live_abcdefghij1234567890'", [], "https://10.0.0.5/x")
    )
    assert "data.secret_exposure" in categories


def test_baseline_policy_redacts_undeclared_sensitive_content() -> None:
    engine = PolicyEngine(load_baseline_policy())
    request = _request(CARD_AND_SSN, [], "https://10.0.0.5/internal")
    findings = run_detectors(request, None)
    result = engine.evaluate(request.model_dump(), findings, calculate_risk(request, findings))
    assert "baseline:undeclared-sensitive-content" in result.matched_rule
    assert result.constraints.get("redact_secrets") is True
