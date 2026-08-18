<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: RELEASE_PROVENANCE
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Release & CI Provenance
<!-- id: release-provenance.root -->

Purpose: make portability, dependency identity, generated-file provenance, and Core↔Runtime compatibility explicit release artifacts.

# CI Matrix
<!-- id: release-provenance.ci-matrix -->

Canonical CI runs validation/build/tests on Linux, Windows, and macOS using supported Node/Python versions. Platform-specific process-spawn and path tests remain mandatory. Release jobs consume the same validated source commit rather than rebuilding from an unverified branch state.

# Dependency & Action Provenance
<!-- id: release-provenance.dependencies -->

Runtime dependency versions are pinned. GitHub Actions SHOULD be pinned to immutable commit SHAs where practical, with human-readable version comments. Releases include a machine-readable provenance manifest containing Core revision, Runtime version, pack version, source-tree hash, build hash, supported compatibility range, Node/Python requirements, and generated archive hashes.

# Compatibility Matrix
<!-- id: release-provenance.compatibility -->

Runtime declares the exact Core revision it was generated from plus an explicit compatibility policy. A Runtime MUST fail verification when its lock expects a different canonical Core revision unless a declared compatibility range explicitly permits it.
