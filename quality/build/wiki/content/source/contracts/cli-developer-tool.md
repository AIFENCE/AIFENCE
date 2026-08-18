<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ARTIFACT_CONTRACT
Contract: CLI / Developer Tool
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# CLI / Developer Tool Production Contract
<!-- id: contract.artifact.cli-developer-tool -->

## Command Model
Resolve primary jobs, command hierarchy, arguments/options, defaults, configuration, stdin/stdout/stderr behavior, exit codes, and discoverability through help.

## Safety & Failure Contract
Destructive actions require explicitness and recovery where possible. Validate inputs, preserve deterministic errors, avoid leaking secrets, and make network/auth failures actionable.

## Automation Contract
Commands intended for scripts must support stable machine-readable output or documented parsing boundaries, predictable exit codes, and non-interactive operation where appropriate.

## Installation & Portability
Define supported runtimes/OSes, install/update path, configuration locations, environment variables, and dependency assumptions.

## Evidence
Test help, happy path, invalid input, missing config, permission failure, network failure, destructive confirmation, stdout/stderr separation, and representative platform behavior.
