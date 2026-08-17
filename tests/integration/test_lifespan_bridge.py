# SPDX-License-Identifier: AGPL-3.0-or-later
"""Mounted sub-applications must start and shut down with the composed app.

Starlette does not run a mounted sub-app's lifespan. Without the bridge in
``aifence.app.create_app``, a subsystem's own resources — HTTP clients, durable
workers, object-store and KMS clients — would leak on every restart.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from aifence.app import create_app
from aifence.core.config import CoreSettings


def _app(tmp_path):
    return create_app(CoreSettings(database_url=f"sqlite+pysqlite:///{tmp_path/'aifence.db'}"))


def test_guard_subapp_resources_close_on_shutdown(tmp_path) -> None:
    app = _app(tmp_path)
    guard = app.state.guard_app

    with TestClient(app) as client:
        assert client.get("/guard/health/ready").status_code == 200
        assert guard.state.http_client.is_closed is False, "client must be usable while running"

    assert guard.state.http_client.is_closed is True, "guard HTTP client leaked after shutdown"


def test_all_tiers_serve_within_the_bridged_lifespan(client: TestClient) -> None:
    # Uses the authenticated shared client: the quality tier is not public.
    assert client.get("/health/live").status_code == 200
    assert client.get("/guard/health/ready").status_code == 200
    assert client.get("/bus/health/live").status_code == 200
    assert client.get("/v1/quality/registry").status_code == 200


def test_shutdown_hook_failure_is_contained(tmp_path) -> None:
    """A failing subsystem hook is logged, not raised, so teardown continues."""
    import asyncio

    from aifence.app import _guarded

    async def boom() -> None:
        raise RuntimeError("subsystem teardown exploded")

    # Must not propagate: one bad hook cannot abort the rest of the teardown.
    asyncio.run(_guarded(boom)())
