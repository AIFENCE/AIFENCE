# Runtime & Integrations

Runtime **2.0.0** exposes BizIQ Core **1.8.8** through a portable Skill, CLI, MCP server, local UI, and platform adapters.

## Runtime responsibilities

- classify production requests and resolve artifact contracts;
- resolve independent operating/product/design/halo/risk profiles;
- retrieve bounded source sections instead of preloading the control plane;
- expose stable control, contract, profile, compiler, validation, and status operations;
- preserve Core authority: generated adapters never override `source/`.

## Generated integrations

The build produces adapters for Claude, Gemini, VS Code/Copilot, Cursor, OpenAI/Codex, and a generic Skill/MCP integration. All adapters are generated from the same Runtime and Skill source rather than maintained as independent BizIQ forks.

## Core relationship

Inside this repository Runtime reads `source/` directly. Standalone Runtime release archives vendor that same tree as `core/` and verify it through `CORE_LOCK.json`.
