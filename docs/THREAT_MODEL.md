# AIFENCE Threat Model

## Security objective

AIFENCE prevents an AI agent or integration from converting untrusted/generated work into an unauthorized or unaudited downstream action, and prevents semantic handoff state from crossing tenant or protocol boundaries without enforcement.

## Trust boundaries

1. **Caller -> composed API:** API keys/mTLS establish caller identity; request size and host/origin controls constrain ingress.
2. **Quality -> Guard:** passing admission quality does not grant authority. Guard independently evaluates action, principal, environment and risk.
3. **Guard -> Bus:** only Guard outcomes explicitly permitted by the fence can create a handoff.
4. **Tenant -> tenant:** fence Bus workspaces are tenant-specific and identity state is tenant-scoped.
5. **Wire -> implementation:** Bus wire v2 is validated against a frozen protocol/TCK contract.
6. **Runtime -> evidence:** audit events are hash chained and signed; artifact contents are not copied into fence-completion audit payloads.

## Priority threats and controls

| Threat | Primary control | Regression/conformance coverage |
| --- | --- | --- |
| Anonymous fence use | Shared Guard-backed identity dependency | `tests/conformance/test_fence_contract.py` |
| Cross-tenant message access | Tenant-specific Bus workspace | `tests/conformance/test_fence_contract.py` |
| Policy bypass/confused deputy | Guard is a mandatory fail-closed stage | integration + red-team suites |
| Ambiguous denial handling | Stable Guard reason codes and matched rule | Guard policy/service tests |
| Low-quality/generated placeholder work entering action path | Admission Quality stable findings | Quality/fence tests |
| Idempotency replay with changed content | Sender/receiver/payload digest binding | Bus + conformance tests |
| Malformed/tampered semantic wire | Frozen schema + TCK + mutation suite | `aifence.bus.conformance --fuzz` |
| Audit tampering | Per-tenant hash chain + signatures/checkpoints | Guard audit tests + fence conformance |
| Oversized request/resource abuse | Streaming-aware request-size middleware | core/integration tests |
| Unsafe production defaults | Startup configuration validation | core configuration tests |
| Secret leakage through metrics | Metrics private by default + bearer auth | core application tests |
| Source/package drift | release, registry and package checks in CI | `scripts/*_check.py` |

## Out of scope / residual risk

AIFENCE cannot prove that external tools, models or downstream agents behave correctly after authorized execution. It governs the boundary and evidence around those interactions. Operators must still protect infrastructure credentials, configure tenant policy correctly, secure the backing database/KMS, and evaluate model-specific prompt/tool risks.
