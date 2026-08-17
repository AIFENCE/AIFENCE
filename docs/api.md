---
title: API reference
summary: Every HTTP endpoint the composed application serves, generated from its OpenAPI document.
infobox:
  Source: generated from /openapi.json
  Contract: OpenAPI 3.1
  Endpoints: 165
---

This page is generated from the live OpenAPI document by `npm run docs:api`, so
it cannot drift from the code. The authoritative contract is `/openapi.json`
when documentation is enabled.

## Fence flow

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/v1/fence/submit` | Run an artifact through the full quality→guard→bus fence |

## Quality

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/v1/quality/controls` | List quality controls |
| `POST` | `/v1/quality/evaluate` | Run the quality gate over an artifact |
| `GET` | `/v1/quality/registry` | Quality control registry summary |

## Console

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/v1/console/status` | Operational status across every fence tier |

## Guard

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/guard/health/live` | Live |
| `GET` | `/guard/health/ready` | Ready |
| `GET` | `/guard/source` | Source and licensing information |
| `POST` | `/guard/v1/agents/register` | Register Agent |
| `GET` | `/guard/v1/agents/{agent_id}` | Get Agent |
| `POST` | `/guard/v1/agents/{agent_id}/revoke` | Revoke Agent |
| `GET` | `/guard/v1/api-keys` | List Api Keys |
| `POST` | `/guard/v1/api-keys` | Create Api Key |
| `POST` | `/guard/v1/api-keys/{key_id}/revoke` | Revoke Api Key |
| `GET` | `/guard/v1/approvals` | List Approvals |
| `GET` | `/guard/v1/approvals/{approval_id}` | Get Approval |
| `POST` | `/guard/v1/approvals/{approval_id}/decision` | Decide Approval |
| `POST` | `/guard/v1/artifacts/scan` | Scan Artifact |
| `GET` | `/guard/v1/artifacts/{artifact_id}` | Get Artifact Metadata |
| `GET` | `/guard/v1/artifacts/{artifact_id}/content` | Get Artifact |
| `POST` | `/guard/v1/audit/anchors` | Anchor Audit |
| `POST` | `/guard/v1/audit/anchors/batch` | Anchor Audit Batch |
| `GET` | `/guard/v1/audit/anchors/quorum` | Audit Anchor Quorum |
| `POST` | `/guard/v1/audit/anchors/{anchor_id}/verify` | Verify Audit Anchor |
| `GET` | `/guard/v1/audit/checkpoints` | List Audit Checkpoints |
| `GET` | `/guard/v1/audit/verify` | Verify Audit |
| `POST` | `/guard/v1/budget-reservations/{reservation_id}/settle` | Settle Budget |
| `POST` | `/guard/v1/budgets` | Create Budget |
| `POST` | `/guard/v1/budgets/{budget_id}/reserve` | Reserve Budget |
| `POST` | `/guard/v1/capabilities` | Issue Capability |
| `POST` | `/guard/v1/capabilities/consume` | Consume Capability |
| `POST` | `/guard/v1/capabilities/{capability_id}/revoke` | Revoke Capability |
| `POST` | `/guard/v1/decisions` | Decide |
| `GET` | `/guard/v1/decisions/{decision_id}` | Get Decision |
| `POST` | `/guard/v1/delegations` | Create Delegation |
| `POST` | `/guard/v1/delegations/{grant_id}/revoke` | Revoke Delegation |
| `POST` | `/guard/v1/dispatch/run` | Run Dispatcher |
| `POST` | `/guard/v1/events` | Ingest Event |
| `GET` | `/guard/v1/executions` | List Executions |
| `POST` | `/guard/v1/executions/recover-stale` | Recover Stale Executions |
| `GET` | `/guard/v1/executions/{execution_id}` | Get Execution |
| `POST` | `/guard/v1/executions/{execution_id}/reconcile` | Reconcile Execution |
| `GET` | `/guard/v1/incidents` | List Incidents |
| `POST` | `/guard/v1/incidents` | Create Incident |
| `GET` | `/guard/v1/incidents/{incident_id}` | Get Incident |
| `POST` | `/guard/v1/incidents/{incident_id}/status` | Update Incident Status |
| `POST` | `/guard/v1/memory` | Write Memory |
| `GET` | `/guard/v1/memory/{memory_id}` | Read Memory |
| `POST` | `/guard/v1/memory/{memory_id}/status` | Update Memory Status |
| `GET` | `/guard/v1/operator/posture` | Operator Posture |
| `GET` | `/guard/v1/policies` | List Policies |
| `POST` | `/guard/v1/policies` | Publish Policy |
| `POST` | `/guard/v1/policies/diff` | Diff Policy |
| `POST` | `/guard/v1/policies/simulate` | Simulate Policy |
| `POST` | `/guard/v1/policies/validate` | Validate Policy |
| `POST` | `/guard/v1/policies/{policy_id}/activate` | Activate Policy |
| `POST` | `/guard/v1/policies/{policy_id}/canary` | Canary Policy |
| `POST` | `/guard/v1/policies/{policy_id}/replay` | Replay Policy |
| `POST` | `/guard/v1/policies/{policy_id}/rollback` | Rollback Policy |
| `POST` | `/guard/v1/policies/{policy_id}/shadow` | Shadow Policy |
| `POST` | `/guard/v1/protocols` | Register Protocol |
| `POST` | `/guard/v1/protocols/a2a/{registration_id}/authorize` | Authorize A2A |
| `POST` | `/guard/v1/protocols/mcp/{registration_id}/tools/call` | Call Mcp Tool |
| `GET` | `/guard/v1/protocols/{registration_id}/manifest-versions` | List Protocol Manifest Versions |
| `GET` | `/guard/v1/providers` | List Providers |
| `POST` | `/guard/v1/providers` | Register Provider |
| `POST` | `/guard/v1/providers/{provider_id}/invoke` | Invoke Provider |
| `POST` | `/guard/v1/providers/{provider_id}/revoke` | Revoke Provider |
| `GET` | `/guard/v1/tenant/legal-holds` | List Legal Holds |
| `POST` | `/guard/v1/tenant/legal-holds` | Create Legal Hold |
| `POST` | `/guard/v1/tenant/legal-holds/{hold_id}/release` | Release Legal Hold |
| `POST` | `/guard/v1/tenant/lifecycle` | Tenant Lifecycle |
| `GET` | `/guard/v1/tenant/lifecycle/{job_id}` | Get Tenant Lifecycle |
| `GET` | `/guard/v1/tenant/lifecycle/{job_id}/content` | Download Tenant Export |
| `POST` | `/guard/v1/tenant/lifecycle/{job_id}/reconcile` | Reconcile Tenant Lifecycle |
| `GET` | `/guard/v1/tools` | List Tools |
| `POST` | `/guard/v1/tools` | Register Tool |
| `POST` | `/guard/v1/tools/{tool_id}/execute` | Execute Tool |
| `POST` | `/guard/v1/tools/{tool_id}/revoke` | Revoke Tool |
| `GET` | `/guard/v1/traces/{trace_id}` | Get Trace |
| `GET` | `/guard/v1/workload-identities` | List Workload Identities |
| `POST` | `/guard/v1/workload-identities` | Create Workload Identity |
| `POST` | `/guard/v1/workload-identities/{binding_id}/revoke` | Revoke Workload Identity |

## Bus

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/bus/v1/a2a/agent-card` | A2A Agent Card |
| `GET` | `/bus/v1/a2a/extension` | A2A Extension |
| `POST` | `/bus/v1/a2a/message/pack` | A2A Message Pack |
| `POST` | `/bus/v1/a2a/message/unpack` | A2A Message Unpack |
| `POST` | `/bus/v1/a2a/pack` | A2A Pack |
| `POST` | `/bus/v1/a2a/unpack` | A2A Unpack |
| `POST` | `/bus/v1/benchmarks/economics` | Economics Benchmark |
| `POST` | `/bus/v1/benchmarks/economics/observed` | Economics Observed |
| `POST` | `/bus/v1/bus/ack-batch` | Bus Ack Batch |
| `GET` | `/bus/v1/bus/backpressure` | Bus Backpressure |
| `GET` | `/bus/v1/bus/context/{receiver}` | Bus Context |
| `POST` | `/bus/v1/bus/handoff` | Bus Handoff |
| `GET` | `/bus/v1/bus/pull/{receiver}` | Bus Pull |
| `POST` | `/bus/v1/bus/{message_id}/ack` | Bus Ack |
| `POST` | `/bus/v1/bus/{message_id}/nack` | Bus Nack |
| `GET` | `/bus/v1/calibration` | Calibration Report |
| `POST` | `/bus/v1/calibration/record` | Calibration Record |
| `POST` | `/bus/v1/codebooks/releases` | Codebook Release |
| `POST` | `/bus/v1/codebooks/sync` | Codebook Sync |
| `GET` | `/bus/v1/codebooks/{namespace}/merkle` | Codebook Merkle |
| `GET` | `/bus/v1/concepts` | List Concepts |
| `POST` | `/bus/v1/concepts` | Register Concept |
| `POST` | `/bus/v1/concepts/{code}/aliases` | Add Alias |
| `POST` | `/bus/v1/concepts/{code}/deprecate` | Deprecate Concept |
| `POST` | `/bus/v1/contradictions/{contradiction_id}/resolve` | Resolve Contradiction |
| `POST` | `/bus/v1/decode` | Decode |
| `POST` | `/bus/v1/encode` | Encode |
| `POST` | `/bus/v1/evals/run` | Eval Run |
| `GET` | `/bus/v1/explain/{packet_id}` | Explain |
| `POST` | `/bus/v1/facts` | Put Fact |
| `GET` | `/bus/v1/facts/{fact_id}` | Get Fact |
| `POST` | `/bus/v1/facts/{fact_id}/invalidate` | Invalidate Fact |
| `GET` | `/bus/v1/federation/export/{namespace}` | Federation Export |
| `POST` | `/bus/v1/federation/import` | Federation Import |
| `POST` | `/bus/v1/federation/peers` | Federation Peer |
| `POST` | `/bus/v1/feedback/{packet_id}` | Feedback |
| `GET` | `/bus/v1/inspect/run/{run_id}` | Inspect Run |
| `GET` | `/bus/v1/inspect/ui/{packet_id}` | Inspect Ui |
| `GET` | `/bus/v1/inspect/{packet_id}` | Inspect Packet |
| `GET` | `/bus/v1/integrations` | List Integrations |
| `GET` | `/bus/v1/integrations/{platform}` | Integration Config |
| `POST` | `/bus/v1/latent/pack` | Latent Pack |
| `POST` | `/bus/v1/latent/unpack` | Latent Unpack |
| `POST` | `/bus/v1/maintenance/cleanup` | Maintenance Cleanup |
| `POST` | `/bus/v1/native-token-gate` | Native Token Gate |
| `POST` | `/bus/v1/negotiate` | Negotiate |
| `GET` | `/bus/v1/patterns` | List Patterns |
| `GET` | `/bus/v1/patterns/candidates` | List Pattern Candidates |
| `POST` | `/bus/v1/patterns/gc` | Pattern Gc |
| `POST` | `/bus/v1/patterns/observe` | Observe Patterns |
| `GET` | `/bus/v1/patterns/{pattern_id}` | Get Pattern |
| `POST` | `/bus/v1/patterns/{pattern_id}/counterfactual` | Pattern Counterfactual |
| `POST` | `/bus/v1/patterns/{pattern_id}/promote-namespace` | Pattern Promote Namespace |
| `POST` | `/bus/v1/patterns/{pattern_id}/status` | Set Pattern Status |
| `GET` | `/bus/v1/protocol` | Protocol Info |
| `GET` | `/bus/v1/protocol/tck` | Protocol Tck |
| `POST` | `/bus/v1/protocol/validate` | Protocol Validate |
| `GET` | `/bus/v1/protocol/wire-schema` | Protocol Wire Schema |
| `POST` | `/bus/v1/publish` | Publish |
| `GET` | `/bus/v1/ready` | Ready |
| `POST` | `/bus/v1/receive` | Receive |
| `POST` | `/bus/v1/receivers/model-identity` | Receiver Model Identity |
| `GET` | `/bus/v1/receivers/{receiver}` | Receiver Knowledge |
| `GET` | `/bus/v1/receivers/{receiver}/reliability` | Receiver Reliability |
| `POST` | `/bus/v1/refs` | Store Ref |
| `POST` | `/bus/v1/refs/resolve` | Resolve Ref |
| `GET` | `/bus/v1/refs/{ref_id}` | Get Ref |
| `POST` | `/bus/v1/refs/{ref_id}/grant` | Ref Grant |
| `POST` | `/bus/v1/refs/{ref_id}/policy` | Ref Policy |
| `POST` | `/bus/v1/routing/agents` | Register Agent Capability |
| `POST` | `/bus/v1/routing/choose` | Route Choose |
| `POST` | `/bus/v1/routing/send` | Route Send |
| `GET` | `/bus/v1/runs/{run_id}/replay` | Replay |
| `POST` | `/bus/v1/send` | Send |
| `POST` | `/bus/v1/states` | Create State |
| `POST` | `/bus/v1/states/transition` | Transition |
| `GET` | `/bus/v1/states/{state_id}` | Get State |
| `POST` | `/bus/v1/states/{state_id}/checkpoint` | State Checkpoint |
| `GET` | `/bus/v1/states/{state_id}/lineage` | State Lineage |
| `POST` | `/bus/v1/subscriptions` | Subscribe |
| `POST` | `/bus/v1/transport/receive` | Transport Receive |
| `POST` | `/bus/v1/transport/send` | Transport Send |
