# Quality Evaluation Modes

AIFENCE deliberately separates the synchronous fence admission decision from the deeper Quality 2.0 evaluation runtime.

## Admission

`POST /v1/fence/submit` and `POST /v1/quality/evaluate` use the deterministic **admission** evaluator. Its contract is bounded enough for a synchronous enforcement path. Responses identify:

- `mode: admission`
- the admission profile
- evaluator version
- stable finding IDs such as `AQ-COMPLETE-001`
- severity, evidence and remediation for failures

Admission answers: **is this artifact sufficiently complete and structurally sound to enter the governed action path?** It does not claim to execute the entire Quality 2.0 control corpus.

## Deep

The repository's `quality/` source pack is the broader Quality 2.0 runtime. `POST /v1/quality/deep/plan` bridges to its built runtime and returns the family-native evaluation/evidence plan. The deep runtime is generated from canonical source with `cd quality && npm run build` and is intentionally not treated as an implicit part of every fence submission.

Deep evaluation answers: **which full control families, validators and evidence requirements apply to this artifact or intent?**

Clients must branch on explicit mode/profile metadata rather than assuming all Quality controls were executed.
