# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 2: the guard subsystem composes into the AIFENCE app and shares core."""
from __future__ import annotations

from fastapi.testclient import TestClient

from aifence.core.db import Base


def test_guard_registered_as_subsystem(client: TestClient) -> None:
    body = client.get("/health/ready").json()
    assert "aifence.guard" in body["subsystems"]


def test_guard_mounted_under_guard_prefix(client: TestClient) -> None:
    assert client.get("/guard/health/ready").status_code == 200
    assert client.get("/guard/source").status_code == 200


def test_guard_models_attached_to_shared_base() -> None:
    # Guard's tables register on the one shared metadata, so a single schema
    # build (core lifespan) creates them alongside every other subsystem's.
    import aifence.guard.models  # noqa: F401  (import registers the models)

    table_names = set(Base.metadata.tables)
    assert any("audit" in name or "tenant" in name or "key" in name for name in table_names), (
        f"expected guard tables on the shared Base, saw: {sorted(table_names)[:10]}"
    )


def test_core_surface_still_served_alongside_guard(client: TestClient) -> None:
    assert client.get("/health/live").status_code == 200
    assert "aifence_http_requests_total" in client.get("/metrics").text
