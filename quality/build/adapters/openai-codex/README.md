# OpenAI / Codex adapter

## Codex / skills-compatible surfaces
Use the canonical Runtime skill at `.agents/skills/biziq/` (the Runtime installer can create it). Keep BizIQ Core outside always-loaded instruction files; activate it progressively through the skill/runtime.

## OpenAI API remote MCP
Deploy `biziq mcp --http` behind HTTPS and appropriate authentication, then expose the remote MCP endpoint through the API's MCP tool configuration. Use allow-listed BizIQ tools for least privilege. See `remote-mcp-example.mjs`.
