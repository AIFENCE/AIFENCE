from __future__ import annotations

import sys
import types
from typing import Any

import pytest

from aifence.bus import mcp_server
from aifence.bus.protocol_spec import AIFENCE_PROTOCOL, AIFENCE_WIRE_VERSION


class _FakeSettings:
    rebuilt = 0

    @classmethod
    def model_rebuild(cls) -> None:
        cls.rebuilt += 1


class _FakeMCP:
    last: _FakeMCP | None = None

    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name
        self.kwargs = kwargs
        self.tools: dict[str, Any] = {}
        self.runs: list[str] = []
        type(self).last = self

    def tool(self):  # type: ignore[no-untyped-def]
        def decorator(fn):  # type: ignore[no-untyped-def]
            self.tools[fn.__name__] = fn
            return fn

        return decorator

    def run(self, *, transport: str) -> None:
        self.runs.append(transport)


def _install_fake_mcp(monkeypatch: pytest.MonkeyPatch) -> None:
    mcp_pkg = types.ModuleType("mcp")
    server_pkg = types.ModuleType("mcp.server")
    fastmcp_pkg = types.ModuleType("mcp.server.fastmcp")
    fastmcp_server = types.ModuleType("mcp.server.fastmcp.server")
    fastmcp_pkg.FastMCP = _FakeMCP  # type: ignore[attr-defined]
    fastmcp_server.Settings = _FakeSettings  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mcp", mcp_pkg)
    monkeypatch.setitem(sys.modules, "mcp.server", server_pkg)
    monkeypatch.setitem(sys.modules, "mcp.server.fastmcp", fastmcp_pkg)
    monkeypatch.setitem(sys.modules, "mcp.server.fastmcp.server", fastmcp_server)


def test_build_server_registers_contract_and_pure_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_mcp(monkeypatch)
    server = mcp_server.build_server()
    assert isinstance(server, _FakeMCP)
    assert server.name == "AIFENCE"
    assert server.kwargs["stateless_http"] is True
    assert _FakeSettings.rebuilt >= 1
    assert len(server.tools) >= 35

    protocol = server.tools["aifence_bus_protocol_info"]()
    assert protocol["protocol"] == AIFENCE_PROTOCOL
    assert protocol["wire_version"] == AIFENCE_WIRE_VERSION

    tck = server.tools["aifence_bus_tck"]()
    assert tck["ok"] is True

    wire = {"v": 2, "c": "global", "a": "report", "p": {}}
    part = server.tools["aifence_bus_a2a_pack"](wire)
    assert server.tools["aifence_bus_a2a_unpack"](part)["wire"] == wire

    latent = server.tools["aifence_bus_pack_latent"]([0.1, -0.2, 0.3], "test-space")
    unpacked = server.tools["aifence_bus_unpack_latent"](latent)
    assert unpacked["space"] == "test-space"
    assert len(unpacked["vector"]) == 3

    conform = server.tools["aifence_bus_conform"](2)
    assert conform["ok"] is True
    assert conform["tck"]["ok"] is True
    assert conform["wire_fuzz"]["ok"] is True


def test_build_server_without_mcp_extra_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ["mcp", "mcp.server", "mcp.server.fastmcp", "mcp.server.fastmcp.server"]:
        monkeypatch.delitem(sys.modules, name, raising=False)
    # Force import resolution to fail even if the optional package happens to be installed.
    real_import = __import__

    def guarded_import(name: str, *args: Any, **kwargs: Any):
        if name.startswith("mcp"):
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded_import)
    with pytest.raises(RuntimeError, match="mcp.*extra"):
        mcp_server.build_server()


def test_run_refuses_unauthenticated_direct_mode_when_auth_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mcp_server, "get_settings", lambda: types.SimpleNamespace(auth_required=True))
    with pytest.raises(RuntimeError, match="no HTTP auth wrapper"):
        mcp_server.run()


def test_run_initializes_and_runs_streamable_http(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_mcp(monkeypatch)
    monkeypatch.setattr(mcp_server, "get_settings", lambda: types.SimpleNamespace(auth_required=False))
    initialized: list[bool] = []
    monkeypatch.setattr(mcp_server, "init_db", lambda: initialized.append(True))
    mcp_server.run()
    assert initialized == [True]
    assert _FakeMCP.last is not None
    assert _FakeMCP.last.runs == ["streamable-http"]
