# Failure Semantics

AIFENCE is an enforcement boundary. Failure behavior is therefore part of the security contract rather than an implementation detail.

| Component/failure | Default behavior | Rationale |
| --- | --- | --- |
| Quality admission timeout/unavailable | **fail closed** | Unvetted artifacts do not silently proceed |
| Guard timeout/unavailable/policy error | **always fail closed** | Authorization can never degrade into authorization-by-absence |
| Bus persistence/handoff failure | **fail closed** | A receipt must not claim delivery that was not durably committed |
| Fence audit append failure | **fail closed** | A governed fence decision without its audit event is incomplete |
| Optional telemetry exporter failure | **degraded** | Enforcement remains authoritative; telemetry transport must not become an availability dependency |
| Optional broker fan-out failure | **degraded/retry** | The database-backed Bus is the source of truth; brokers are accelerators |
| Database unavailable | **fail closed** | Identity, policy, audit and durable handoff state cannot be trusted |
| Signing/KMS material unavailable | **fail closed** for operations requiring signed evidence | Unsigned evidence must not be represented as verified evidence |
| Deep Quality runtime unavailable | **admission remains available** | Deep planning is an explicit mode, not an implicit admission dependency |

Only `quality` and `bus` may be explicitly configured as fence fail-open tiers for narrowly defined deployments. `guard` is rejected if named in `AIFENCE_FLOW_FAIL_OPEN_TIERS`.

## Receipt rule

A successful `handed_off` receipt means Quality admission passed, Guard permitted the action, the Bus handoff was durably created, and the fence completion audit event was appended. Optional telemetry or broker propagation is not part of that transactional success claim.
