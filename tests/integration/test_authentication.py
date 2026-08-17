# SPDX-License-Identifier: AGPL-3.0-or-later
"""The fence and quality routers must not serve anonymous callers.

These routers are composed onto the application itself rather than mounted
inside the guard sub-app, so they do not inherit its router-level auth. Without
the shared identity dependency they were reachable unauthenticated, while
``/guard/*`` correctly returned 401.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

ARTIFACT = {
    "artifact": (
        "# Quarterly Report\n\nRevenue grew 12% to $4.2M across all regions, driven "
        "by strong enterprise demand and improved retention."
    ),
    "content_type": "text/markdown",
    "action": {"operation": "read"},
}

PROTECTED_GETS = ["/v1/quality/registry", "/v1/quality/controls"]


@pytest.mark.parametrize("path", PROTECTED_GETS)
def test_quality_reads_require_authentication(anon_client: TestClient, path: str) -> None:
    assert anon_client.get(path).status_code == 401


def test_quality_evaluate_requires_authentication(anon_client: TestClient) -> None:
    response = anon_client.post("/v1/quality/evaluate", json={"artifact": "x"})
    assert response.status_code == 401


def test_fence_submit_requires_authentication(anon_client: TestClient) -> None:
    response = anon_client.post("/v1/fence/submit", json=ARTIFACT)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_failed"


def test_fence_submit_rejects_invalid_credential(anon_client: TestClient) -> None:
    response = anon_client.post(
        "/v1/fence/submit", json=ARTIFACT, headers={"Authorization": "Bearer not-a-real-key"}
    )
    assert response.status_code == 401


def test_authenticated_submit_succeeds_and_records_tenant(client: TestClient) -> None:
    response = client.post("/v1/fence/submit", json=ARTIFACT)
    assert response.status_code == 200
    body = response.json()
    assert body["final_outcome"] == "handed_off"
    assert body["tenant_id"].startswith("ten_"), "receipt must attribute the submitting tenant"


def test_health_and_metrics_remain_public(anon_client: TestClient) -> None:
    # Operational endpoints stay reachable so probes and scrapers keep working.
    assert anon_client.get("/health/live").status_code == 200
    assert anon_client.get("/health/ready").status_code == 200
    assert anon_client.get("/metrics").status_code == 200
