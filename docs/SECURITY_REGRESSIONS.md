# Security Regression Ledger

Every security-relevant defect or design hardening must leave behind a permanent regression test. A change is not considered closed until its test is referenced here.

| Property protected | Regression evidence |
|---|---|
| Anonymous fence submission is rejected | `tests/conformance/test_fence_contract.py` |
| Tenant-scoped handoffs cannot cross tenant boundaries | `tests/conformance/test_fence_contract.py` |
| Audit-chain tampering is detectable | `tests/conformance/test_fence_contract.py` |
| Idempotency keys are bound to payload content | `tests/conformance/test_fence_contract.py` |
| Malformed Bus wire fails closed | `tests/bus/test_protocol_v02.py` |
| Random unknown Bus wire keys fail closed | `tests/bus/test_protocol_properties_hypothesis.py` |
| Unsupported wire versions are rejected | `tests/bus/test_protocol_properties_hypothesis.py` |
| Guard remains fail-closed when unavailable | `tests/conformance/test_failure_injection.py` |
| Quality fail-open requires explicit configuration | `tests/conformance/test_failure_injection.py` |
| Bus fail-open requires explicit configuration | `tests/conformance/test_failure_injection.py` |
| Workload trust domains and proxy assertions fail closed | `tests/guard/test_workload_identity_unit.py` |
| Oversized requests are rejected before application handling | `tests/conformance/test_fence_contract.py` |
| Adversarial behavioral regressions remain detected | `tests/guard/test_adversarial_regressions.py` |
| Security configuration rejects unsafe production defaults | `tests/guard/test_config.py` |
| Release tag/version mismatch cannot publish | `tests/core/test_release_preflight.py` |

## Maintenance rule

When a security issue is discovered, add the reproducer as a test first, fix the implementation second, then add the stable test path to this ledger. `scripts/security_regression_check.py` verifies that ledger references do not silently rot.
