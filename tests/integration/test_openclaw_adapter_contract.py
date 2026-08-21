from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPENCLAW = ROOT / "integrations" / "openclaw"


def test_openclaw_adapter_compiles_against_real_peer_contract() -> None:
    source = (OPENCLAW / "src" / "index.ts").read_text(encoding="utf-8")

    assert not (OPENCLAW / "src" / "openclaw-plugin-sdk.d.ts").exists()
    assert 'from "openclaw/plugin-sdk/core"' in source
    assert 'OpenClawPluginApi' in source
    assert 'OpenClawPluginToolContext' in source
    assert source.count('async execute(_id: string, params: unknown)') == 3

    for tool_name in ("aifence_bus_handoff", "aifence_bus_poll", "aifence_bus_ack"):
        assert f'{{ name: "{tool_name}" }}' in source
