# Observability Contract

AIFENCE uses one request/correlation context across Quality, Guard and Bus. The fence response and audit stream are intended to let an operator reconstruct one governed transaction without correlating three unrelated systems manually.

## Canonical fence telemetry

Prometheus metrics include:

- `aifence_fence_stage_calls_total{tier,result,breaker_state}`
- `aifence_fence_stage_duration_seconds{tier}`
- `aifence_fence_outcomes_total{outcome,allowed}`

Existing subsystem metrics remain available for deeper diagnosis. `/metrics` is private by default; production private metrics require a bearer token of at least 32 bytes unless the operator deliberately enables public metrics.

## Audit linkage

Every completed fence flow appends a tamper-evident `fence.completed` Guard audit event. It records artifact digest rather than artifact contents and includes the final outcome plus Quality, Guard and Bus decision metadata. The API receipt exposes the resulting audit event ID, sequence, event hash and signing key ID.

## Operator reconstruction

For a request, retain the returned `request_id`. Use it with application logs/traces, the fence receipt, Guard audit records and Bus message metadata. A full successful path should be reconstructable as:

`request -> quality admission -> guard policy decision -> durable bus handoff -> fence.completed audit`

Telemetry export failures must not mutate policy outcomes. Audit persistence is different: audit append is part of the governed fence completion contract and fails closed.
