# MCP Server

## Local stdio
```bash
aifence mcp --stdio
```

## Local Streamable HTTP
```bash
aifence mcp --http --host 127.0.0.1 --port 3888
```
Endpoint: `/mcp`. Runtime refuses non-loopback binds unless `AIFENCE_ALLOW_REMOTE_HTTP=1` is explicitly set. That switch is not authentication; remote deployment still requires HTTPS, authentication/authorization, origin/host policy, rate limits, and deployment hardening.

## Tools
- `aifence_quality_initialize`
- `aifence_quality_plan`
- `aifence_quality_get_sections`
- `aifence_quality_get_control`
- `aifence_quality_get_artifact_contract`
- `aifence_quality_get_profile`
- `aifence_quality_compile_feature`
- `aifence_quality_compile_component`
- `aifence_quality_compile_operation`
- `aifence_quality_validate`
- `aifence_quality_status`

## Resources
`aifence://readme`, `aifence://control-index`, `aifence://control-manifest`, eight artifact-contract resources, and `ui://aifence/status`.

## UI fallback
`aifence_quality_plan` and `aifence_quality_status` carry MCP Apps UI metadata. Hosts without MCP Apps still receive complete text/structured results.
