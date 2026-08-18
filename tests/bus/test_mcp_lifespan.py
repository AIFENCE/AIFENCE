"""Regression tests for GitHub issue #11.

The MCP SDK's ``StreamableHTTPSessionManager.run()`` may only be entered once
per FastMCP instance. AIFENCE therefore builds a fresh FastMCP on every lifespan
startup (see ``src/aifence/bus/main.py``: the ``lifespan`` context manager and
the delegating ``_MCPMount`` at ``/mcp``), so repeated app startups in a
single process — e.g. one ``TestClient`` per test — no longer raise
``RuntimeError: StreamableHTTPSessionManager .run() can only be called once
per instance``.
"""

import pytest
from fastapi.testclient import TestClient

from aifence.bus.main import app


def _mcp_importable() -> bool:
    try:
        import mcp  # noqa: F401

        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(not _mcp_importable(), reason="mcp extra not installed")


def test_repeated_app_startups_with_mcp_installed():
    """Two full lifespan cycles in one process must both succeed."""
    for _ in range(2):
        with TestClient(app) as client:
            body = client.get("/health/live")
            assert body.status_code == 200
            assert body.json()["mcp"] is True


def test_mcp_endpoint_routes_without_crashing():
    """GET /mcp must route to the MCP transport (4xx/2xx), never a 500."""
    with TestClient(app) as client:
        response = client.get("/mcp")
        assert response.status_code < 500
        assert response.status_code not in (500,)
