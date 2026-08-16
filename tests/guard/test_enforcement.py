# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from aifence.guard.enforcement import build_enforcement_plan


def request_document() -> dict[str, object]:
    return {
        "trace_id": "trc_enforcement_0001",
        "principal": {"type": "service", "id": "svc-1"},
        "agent": {"id": "agt-1"},
        "objective": {"declared_goal": "Read approved record", "approved_scope": ["record:42"]},
        "action": {
            "type": "tool.call",
            "tool": "records.read",
            "operation": "read",
            "target": "record:42",
            "arguments": {
                "method": "GET",
                "path": "/records/42",
                "query": {},
                "recipients": ["security@example.test"],
            },
            "amount_usd": 10,
            "destructive": False,
            "external_effect": False,
        },
        "security_context": {
            "network_destination": "https://api.example.test/records/42"
        },
    }


def test_all_declared_policy_controls_compile_to_enforcement() -> None:
    controls = {
        "allowed_destinations": ["api.example.test*"],
        "allowed_recipients": ["*@example.test"],
        "allowed_resources": ["record:*"],
        "max_amount_usd": 20,
        "max_records": 50,
        "max_response_bytes": 4096,
        "read_only": True,
        "sandbox_required": True,
        "redact_secrets": True,
        "required_controls": ["audit", "redaction", "sandbox"],
        "issue_capability": True,
    }
    plan = build_enforcement_plan(
        request_document(),
        outcome="allow_with_limits",
        constraints=controls,
        runtime_attestation={"sandbox_attestation": "verified"},
    )
    assert plan["executable"] is True
    by_type = {control["type"]: control for control in plan["controls"]}
    assert by_type["allowed_destinations"]["status"] == "applied"
    assert by_type["allowed_recipients"]["status"] == "applied"
    assert by_type["allowed_resources"]["status"] == "applied"
    assert by_type["max_amount_usd"]["status"] == "applied"
    assert by_type["max_response_bytes"]["parameters"]["value"] == 4096
    assert by_type["read_only"]["status"] == "applied"
    assert by_type["sandbox_required"]["status"] == "applied"
    assert by_type["required_controls"]["status"] == "applied"
    assert by_type["audit"]["status"] == "planned"
    assert plan["transformed_action"]["arguments"]["query"]["limit"] == "50"


def test_policy_controls_fail_closed_on_boundary_violation() -> None:
    document = request_document()
    document["action"]["operation"] = "delete"
    document["action"]["destructive"] = True
    plan = build_enforcement_plan(
        document,
        outcome="allow_with_limits",
        constraints={
            "allowed_destinations": ["other.example.test"],
            "allowed_recipients": ["finance@example.test"],
            "allowed_resources": ["record:7"],
            "max_amount_usd": 5,
            "read_only": True,
            "sandbox_required": True,
            "required_controls": ["unavailable-control"],
        },
        runtime_attestation={},
    )
    assert plan["executable"] is False
    failed = {
        control["type"]
        for control in plan["controls"]
        if control["status"] == "failed"
    }
    assert {
        "allowed_destinations",
        "allowed_recipients",
        "allowed_resources",
        "max_amount_usd",
        "read_only",
        "sandbox_required",
        "required_controls",
    }.issubset(failed)
