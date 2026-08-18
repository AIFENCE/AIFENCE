# OpenAI / Codex adapter

## Codex / skills-compatible surfaces
Use the canonical Runtime skill at `.agents/skills/aifence/` (the Runtime installer can create it). Keep AIFENCE Core outside always-loaded instruction files; activate it progressively through the skill/runtime.

## OpenAI API remote MCP
Deploy `aifence mcp --http` behind HTTPS and appropriate authentication, then expose the remote MCP endpoint through the API's MCP tool configuration. Use allow-listed AIFENCE tools for least privilege. See `remote-mcp-example.mjs`.
