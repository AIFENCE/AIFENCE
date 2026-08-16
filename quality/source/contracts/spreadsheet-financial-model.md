<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ARTIFACT_CONTRACT
Contract: Spreadsheet / Financial Model
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Spreadsheet / Financial Model Production Contract
<!-- id: contract.artifact.spreadsheet-financial-model -->

## Model Purpose
Resolve decisions supported, time horizon, granularity, scenarios, assumptions, actuals, forecasts, currencies/units, and required outputs before building formulas.

## Formula & Lineage Contract
Inputs, calculations, outputs, and checks must be distinguishable. Formulas should be auditable, references intentional, units consistent, and hardcoded assumptions traceable.

## Scenario & Integrity Contract
Provide applicable base/upside/downside or user-defined scenarios, reconciliation checks, balance checks, error handling, circularity policy, and sensitivity logic.

## Presentation Contract
Use clear number formats, freeze panes, tables, hierarchy, summaries, and charts only where decision-useful. Do not decorate financial models like dashboards at the expense of auditability.

## Evidence
Recalculate, inspect formulas, verify totals and cross-sheet links, test scenario changes, check errors/blank handling, and confirm output files open without repair warnings.
