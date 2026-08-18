# SPDX-License-Identifier: AGPL-3.0-or-later
"""Indirect prompt injection: untrusted content ingested, then acted upon.

The injected text carries no keyword a matcher would recognise and the payload
is innocuous, so no single turn is remarkable. Only the *flow* — attacker-
controllable input, then a state change — reveals it, which is why this lives in
the cross-tier detector rather than in a per-request one.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from aifence.behavior import AgentWindows, ObservationWindow, behavioral_findings, untrusted_source

CLEAN_QUALITY: dict[str, object] = {"score": 90, "checks": [], "violations": []}


def _authenticated(app: FastAPI) -> TestClient:
    with app.state.session_factory() as session:
        _t, _k, secret = app.state.guard_app.state.service.create_tenant_and_key(
            session, tenant_name="Injection", key_name="k", scopes=["*"]
        )
    return TestClient(app, headers={"Authorization": f"Bearer {secret}"})


# --- taint identification ---

def test_public_read_with_content_is_untrusted() -> None:
    assert untrusted_source("read", "https://forum.example.net/t/1", True)


def test_private_read_is_trusted() -> None:
    # Internal services are not attacker-controllable.
    assert untrusted_source("read", "https://10.4.1.30/records", True) is None


def test_non_url_target_is_trusted() -> None:
    assert untrusted_source("read", "customer:5521", True) is None


def test_outbound_send_is_not_ingestion() -> None:
    # Posting *to* a public address does not import untrusted content.
    assert untrusted_source("send", "https://partner.example.net/hook", True) is None


def test_read_without_content_is_not_ingestion() -> None:
    assert untrusted_source("read", "https://forum.example.net/t/1", False) is None


# --- the signal ---

def _window_after_untrusted_read() -> ObservationWindow:
    window = ObservationWindow()
    window.record(
        operation="read",
        target="https://forum.example.net/thread/12",
        destination=None,
        quality=CLEAN_QUALITY,
        observed=set(),
        ingested_untrusted="https://forum.example.net/thread/12",
    )
    return window


def test_state_change_after_untrusted_ingestion_is_flagged() -> None:
    findings = behavioral_findings(
        operation="write", quality=CLEAN_QUALITY, window=_window_after_untrusted_read()
    )
    assert "integrity.untrusted_influence" in {f.category for f in findings}


def test_read_after_untrusted_ingestion_is_not_flagged() -> None:
    """Continuing to read is not acting on the content."""
    findings = behavioral_findings(
        operation="read", quality=CLEAN_QUALITY, window=_window_after_untrusted_read()
    )
    assert "integrity.untrusted_influence" not in {f.category for f in findings}


def test_state_change_without_prior_ingestion_is_not_flagged() -> None:
    window = ObservationWindow()
    window.record(
        operation="read", target="catalog:services", destination=None,
        quality=CLEAN_QUALITY, observed=set(),
    )
    findings = behavioral_findings(operation="write", quality=CLEAN_QUALITY, window=window)
    assert not findings


def test_finding_reports_the_source_not_the_content() -> None:
    findings = behavioral_findings(
        operation="send", quality=CLEAN_QUALITY, window=_window_after_untrusted_read()
    )
    finding = next(f for f in findings if f.category == "integrity.untrusted_influence")
    assert finding.attributes["sources"] == ["https://forum.example.net/thread/12"]


# --- per-agent windows ---

def test_windows_are_isolated_per_agent() -> None:
    windows = AgentWindows()
    windows.get("tenant:agent-a").turns_seen = 4
    assert windows.get("tenant:agent-a").turns_seen == 4
    assert windows.get("tenant:agent-b").turns_seen == 0


def test_windows_expire() -> None:
    windows = AgentWindows(ttl_seconds=0)
    windows.get("tenant:agent-a").turns_seen = 4
    assert windows.get("tenant:agent-a").turns_seen == 0, "an idle window must not persist forever"


# --- end to end through the live flow ---

def test_injection_is_caught_in_the_request_path(app: FastAPI) -> None:
    with _authenticated(app) as client:
        first = client.post(
            "/v1/fence/submit",
            json={
                "artifact": "Read the community thread for background on the reported defect.",
                "action": {
                    "operation": "read",
                    "tool": "http.get",
                    "target": "https://forum.example.net/thread/12",
                },
            },
        ).json()
        # Reading untrusted content is not itself suspicious.
        assert first["final_outcome"] == "handed_off"
        assert first["stages"]["guard"]["signals"] == []

        second = client.post(
            "/v1/fence/submit",
            json={
                "artifact": "Updated the ticket summary per the guidance in the thread.",
                "action": {"operation": "write", "tool": "wiki.write", "target": "wiki:ticket-4471"},
            },
        ).json()
        assert second["final_outcome"] == "blocked_by_guard"
        assert "integrity.untrusted_influence" in second["stages"]["guard"]["signals"]


def test_ordinary_write_is_unaffected(app: FastAPI) -> None:
    """No untrusted ingestion, no signal — the detector must not tax normal work."""
    with _authenticated(app) as client:
        body = client.post(
            "/v1/fence/submit",
            json={
                "artifact": "Documented the rollback procedure and the checks to run afterwards.",
                "action": {"operation": "read", "tool": "wiki.read", "target": "runbook:deploy"},
            },
        ).json()
        assert body["stages"]["guard"]["signals"] == []
