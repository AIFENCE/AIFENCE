# Platform Adapters

Adapters are intentionally thin. They install/discover the same skill and point the host at the same MCP server.

| Platform | Skill | MCP | Packaged adapter |
|---|---|---|---|
| Generic Agent Skills | `.agents/skills/biziq` | host-specific | `adapters/generic` |
| Claude Code | bundled skill / `.claude/skills` | `.mcp.json` | Claude-format plugin |
| Gemini CLI | bundled extension skill / `.agents/skills` | `mcpServers` | `gemini-extension.json` |
| VS Code Copilot | `.agents/skills/biziq` | `.vscode/mcp.json` | config template |
| Cursor | MCP-first | `.cursor/mcp.json` | config template |
| OpenAI / Codex | `.agents/skills/biziq` where supported | remote MCP for API | example + skill installer |

The Runtime never claims platform support merely because a config file was generated. Run each host's native tool/skill discovery command after installation.
