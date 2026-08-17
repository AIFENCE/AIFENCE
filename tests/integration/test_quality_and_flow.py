# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 4: quality gate + the end-to-end fence flow (quality -> guard -> bus)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from aifence.app import create_app
from aifence.core.config import CoreSettings
from aifence.quality.gate import QualityGate

GOOD = (
    "# Quarterly Report\n\nRevenue grew 12% to $4.2M across all regions, driven by "
    "strong enterprise demand and improved retention across the customer base."
)


@pytest.fixture()
def client(tmp_path) -> TestClient:
    settings = CoreSettings(database_url=f"sqlite+pysqlite:///{tmp_path/'aifence.db'}")
    return TestClient(create_app(settings))


# --- gate unit behaviour ---

def test_gate_accepts_substantial_artifact() -> None:
    decision = QualityGate().evaluate(GOOD, "text/markdown")
    assert decision.passed is True
    assert decision.outcome == "accept"
    assert decision.score >= 70


def test_gate_rejects_placeholders() -> None:
    decision = QualityGate().evaluate("# Draft\n\nTODO: fill this in. Lorem ipsum.", "text/markdown")
    assert decision.passed is False
    assert decision.outcome == "reject"
    assert any("anti_template" in v for v in decision.violations)


def test_gate_rejects_empty() -> None:
    decision = QualityGate().evaluate("   ", "text/plain")
    assert decision.outcome == "reject"


# --- quality API ---

def test_quality_registry_endpoint(client: TestClient) -> None:
    body = client.get("/v1/quality/registry").json()
    assert body["loaded"] is True
    assert body["total_controls"] > 0


def test_quality_evaluate_endpoint(client: TestClient) -> None:
    r = client.post("/v1/quality/evaluate", json={"artifact": GOOD, "content_type": "text/markdown"})
    assert r.status_code == 200
    assert r.json()["passed"] is True


# --- the fence flow: three tiers as one ---

def test_fence_full_passthrough_delivers_claimable_handoff(client: TestClient) -> None:
    r = client.post(
        "/v1/fence/submit",
        json={
            "artifact": GOOD,
            "content_type": "text/markdown",
            "receiver": "analytics-agent",
            "action": {"operation": "read"},
            "risk_score": 10,
        },
    )
    body = r.json()
    assert body["allowed"] is True
    assert body["final_outcome"] == "handed_off"
    assert body["stages"]["quality"]["passed"] is True
    assert body["stages"]["guard"]["outcome"] == "allow"
    bus = body["stages"]["bus"]
    assert bus["delivered"] is True
    assert bus["message_id"].startswith("M")
    assert bus["content_ref"].startswith("aifence:sha256:")

    # End-to-end proof: the receiver can durably claim the delivered handoff.
    from aifence.bus.bus import SemanticBus
    from aifence.bus.config import get_settings

    app = client.app
    with app.state.session_factory() as db:
        claimed = SemanticBus(db, get_settings()).pull(receiver="analytics-agent", claim=True)
        db.commit()
    assert [m.id for m in claimed] == [bus["message_id"]]


def test_fence_blocked_at_quality(client: TestClient) -> None:
    r = client.post(
        "/v1/fence/submit",
        json={"artifact": "TODO placeholder", "action": {"operation": "read"}},
    )
    body = r.json()
    assert body["allowed"] is False
    assert body["final_outcome"] == "blocked_by_quality"
    assert "guard" not in body["stages"]  # flow stopped before enforcement


def test_fence_blocked_at_guard(client: TestClient) -> None:
    r = client.post(
        "/v1/fence/submit",
        json={
            "artifact": GOOD,
            "content_type": "text/markdown",
            "action": {"operation": "delete", "destructive": True},
            "risk_score": 80,
        },
    )
    body = r.json()
    assert body["allowed"] is False
    assert body["final_outcome"] == "blocked_by_guard"
    assert body["stages"]["quality"]["passed"] is True  # quality passed
    assert "bus" not in body["stages"]  # never reached transport
