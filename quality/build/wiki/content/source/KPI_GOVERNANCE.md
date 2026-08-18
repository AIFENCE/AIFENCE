<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: KPI_GOVERNANCE
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# KPI Definition & Metric Governance
<!-- id: kpi-governance.root -->

Purpose: turn generic KPI names into reproducible operating measures with ownership, data provenance, interpretation, and action rules.

# KPI Definition Schema
<!-- id: kpi-governance.schema -->

For each material KPI, define:

```text
Metric ID
Name
Purpose / decision supported
Operational definition
Formula / calculation rule
Numerator / denominator when applicable
Unit
Population / scope
Inclusions
Exclusions
Time window
Source system(s)
Source fields / events when known
Metric owner
Data owner / steward when different
Calculation frequency
Review cadence
Leading / lagging / balancing classification
Segmentation needed for interpretation
Target / threshold
Target provenance
Alert / failure condition
Required response
Known data-quality risks
Gaming / perverse-incentive risk
Audit / reconciliation evidence
Version / effective date
```

# No Invented Targets
<!-- id: kpi-governance.no-invented-targets -->

Do not fabricate targets, SLAs, tolerances, benchmarks, staffing ratios, utilization targets, defect limits, financial thresholds, or regulatory limits.

When a useful target is unknown:

- label it `ORGANIZATION-SPECIFIC — NOT SUPPLIED`;
- optionally provide a method for establishing the target;
- do not turn an industry norm, model guess, or arbitrary percentage into policy.

# Formula Integrity
<!-- id: kpi-governance.formula-integrity -->

A KPI name without a calculation definition is incomplete when reproducibility matters.

Example pattern:

```text
First-Time Fix Rate
= eligible service jobs resolved without a qualifying repeat visit
  / all eligible completed service jobs
  × 100
```

The procedure must still define “eligible,” “resolved,” the repeat window, exclusions, and data source before the metric is considered production-ready.

# Metric Ownership
<!-- id: kpi-governance.ownership -->

Distinguish:

- **Metric Owner** — accountable for interpretation/action.
- **Data Owner/Steward** — accountable for source quality/definition.
- **Process Owner** — accountable for operational process performance.

One person may hold several roles in a small organization, but the responsibilities remain distinct.

# Metric System Quality
<!-- id: kpi-governance.system-quality -->

A healthy metric set balances outcomes and controls. Avoid optimizing a single metric that creates harmful behavior.

Examples of balancing pairs:

```text
Throughput ↔ quality/rework
Utilization ↔ response time / burnout risk
Conversion ↔ refund/cancellation/complaint rate
First-time fix ↔ safety/quality compliance
Deployment frequency ↔ change failure / recovery time
Collection rate ↔ dispute/error/customer harm
```

# KPI Evidence Gate
<!-- id: kpi-governance.evidence-gate -->

A KPI is operationally defined only when another competent person could reproduce the value from the specified sources without guessing material calculation rules.

# Machine Reproducibility States
<!-- id: kpi-governance.machine-reproducibility -->

Every KPI declares `calculation_state`:

- `DEFINED` — another competent person can reproduce the metric without guessing material rules. The machine schema therefore requires formula/calculation rule, population scope, source system(s), calculation frequency, review cadence, target provenance, audit/reconciliation evidence, and balancing-measure consideration.
- `UNRESOLVED` — the metric is useful conceptually but material calculation facts remain unknown. `open_unknowns` is mandatory and the KPI must not be presented as production-ready.

`target_provenance` uses controlled states: `ORGANIZATION_VERIFIED`, `EXTERNAL_VERIFIED`, `ORGANIZATION_SPECIFIC_NOT_SUPPLIED`, or `NOT_APPLICABLE`. When a target value is present, a corresponding `target_source` is required and the provenance cannot be a not-supplied/not-applicable state.
