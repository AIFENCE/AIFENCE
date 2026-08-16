# MCP Server

## Local stdio
```bash
biziq mcp --stdio
```

## Local Streamable HTTP
```bash
biziq mcp --http --host 127.0.0.1 --port 3888
```
Endpoint: `/mcp`. Runtime refuses non-loopback binds unless `BIZIQ_ALLOW_REMOTE_HTTP=1` is explicitly set. That switch is not authentication; remote deployment still requires HTTPS, authentication/authorization, origin/host policy, rate limits, and deployment hardening.

## Tools
- `biziq_initialize`
- `biziq_plan`
- `biziq_get_sections`
- `biziq_get_control`
- `biziq_get_artifact_contract`
- `biziq_get_profile`
- `biziq_compile_feature`
- `biziq_compile_component`
- `biziq_compile_operation`
- `biziq_validate`
- `biziq_status`

## Resources
`biziq://readme`, `biziq://control-index`, `biziq://control-manifest`, eight artifact-contract resources, and `ui://biziq/status`.

## UI fallback
`biziq_plan` and `biziq_status` carry MCP Apps UI metadata. Hosts without MCP Apps still receive complete text/structured results.
