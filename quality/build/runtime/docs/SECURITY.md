# Runtime Security Model

- Core retrieval is read-only and path allow-listed; traversal is rejected.
- MCP planning/retrieval/compiler tools are read-only.
- Validation invokes only vendored AIFENCE validator scripts with explicit targets.
- Runtime does not accept arbitrary shell commands.
- Project installer only merges known MCP/skill namespaces and backs up pre-existing JSON before mutation.
- Global/home mutation is intentionally not automated in Runtime 1.0.
- HTTP binds to loopback by default and rejects non-loopback binding unless explicitly enabled. Remote enablement is not authentication.
- UI has no external scripts, fonts, images, or network dependencies.
- Treat any local MCP server/plugin as executable code and review before enabling it in an agent host.
