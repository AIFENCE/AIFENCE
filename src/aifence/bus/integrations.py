# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from .schemas import IntegrationConfigResponse, IntegrationProfile

_PROFILES: dict[str, IntegrationProfile] = {
    "generic": IntegrationProfile(
        id="generic",
        display_name="Generic agent runtime",
        native_plugin=False,
        supports_mcp=True,
        supports_a2a=True,
        recommended_surface="REST/A2A + SageRuntime",
        notes=["Core SAGE protocol is vendor-neutral and does not require MCP."],
    ),
    "hermes": IntegrationProfile(
        id="hermes",
        display_name="Hermes Agent",
        native_plugin=True,
        supports_mcp=True,
        supports_a2a=True,
        recommended_surface="native Hermes plugin/hooks; MCP as fallback",
        notes=[
            "Hermes supports Python plugins, lifecycle hooks, context-engine plugins, and MCP.",
            "Use the native adapter when SAGE should be automatic rather than model-invoked.",
        ],
    ),
    "openclaw": IntegrationProfile(
        id="openclaw",
        display_name="OpenClaw",
        native_plugin=True,
        supports_mcp=True,
        supports_a2a=True,
        recommended_surface="native OpenClaw plugin hooks; MCP as fallback",
        notes=[
            "OpenClaw plugins can register tools and in-process agent/message hooks.",
            "The native adapter injects claimed SAGE context during turn preparation and acknowledges only successful runs.",
        ],
    ),
    "claude": IntegrationProfile(
        id="claude",
        display_name="Claude / Claude Code",
        native_plugin=False,
        supports_mcp=True,
        supports_a2a=True,
        recommended_surface="MCP connector or A2A peer wrapper",
        notes=[
            "Claude Code supports remote HTTP MCP servers; SAGE remains outside the model provider.",
            "Cross-agent delivery should use the SAGE bus/A2A layer rather than provider-specific prompts.",
        ],
    ),
    "openai": IntegrationProfile(
        id="openai",
        display_name="OpenAI / ChatGPT / Codex",
        native_plugin=False,
        supports_mcp=True,
        supports_a2a=True,
        recommended_surface="MCP app/plugin or A2A peer wrapper",
        notes=["OpenAI is an adapter target, not a dependency of the SAGE core."],
    ),
}


def profiles() -> list[IntegrationProfile]:
    return list(_PROFILES.values())


def profile(platform: str) -> IntegrationProfile:
    key = platform.lower().strip()
    try:
        return _PROFILES[key]
    except KeyError as exc:
        raise KeyError(f"unsupported integration platform: {platform}") from exc


def config_for(platform: str, base_url: str, agent_id: str, workspace: str = "default") -> IntegrationConfigResponse:
    p = profile(platform)
    base = base_url.rstrip("/")
    mcp_url = base + "/mcp"
    files: dict[str, str] = {}
    commands: list[str] = []
    config: dict[str, object] = {
        "sage_url": base,
        "agent_id": agent_id,
        "workspace": workspace,
        "mcp_url": mcp_url,
        "a2a_extension": "urn:uuid:f81af17b-cc6a-5cdf-8a0f-51116b2e6a8d",
    }
    if p.id == "hermes":
        config["remote_mcp_url"] = mcp_url
        files["env"] = f"SAGE_URL={base}\nSAGE_AGENT_ID={agent_id}\nSAGE_WORKSPACE={workspace}\n"
        commands = ['unzip sage-hermes-plugin-v0.2.7.zip -d "${HERMES_HOME:-$HOME/.hermes}/plugins"', "hermes plugins enable sage"]
    elif p.id == "openclaw":
        config["remote_mcp_url"] = mcp_url
        files["env"] = f"SAGE_URL={base}\nSAGE_AGENT_ID={agent_id}\nSAGE_WORKSPACE={workspace}\n"
        commands = ["openclaw plugins install npm-pack:./sage-agent-openclaw-sage-0.2.7.tgz", "openclaw plugins enable sage", "openclaw plugins inspect sage --runtime --json"]
    elif p.id == "claude":
        config["remote_mcp_url"] = mcp_url
        commands = [f"configure Claude/Claude Code with remote MCP server {mcp_url}"]
    elif p.id == "openai":
        config["remote_mcp_url"] = mcp_url
        commands = [f"configure the OpenAI client/app with the SAGE MCP endpoint {mcp_url}"]
    else:
        commands = ["pip install ./sage_agent_protocol-0.2.7-py3-none-any.whl", "use SageRuntime or POST /v1/bus/handoff"]
    return IntegrationConfigResponse(platform=p.id, profile=p, files=files, commands=commands, config=config)
