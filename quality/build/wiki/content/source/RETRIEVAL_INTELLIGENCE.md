<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: RETRIEVAL_INTELLIGENCE
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Capability Retrieval Intelligence
<!-- id: retrieval-intelligence.root -->

Purpose: make stable-ID capability sections the Runtime's primary retrieval unit. `activeModules` remains a compatibility/debug view, not permission to preload entire Markdown files.

# Retrieval Unit
<!-- id: retrieval-intelligence.unit -->

For an active capability, Runtime returns: capability name; `capability_id`; domain; shard path; exact stable section; applicable phase; activation reason; dependency; and estimated retrieval size. Retrieve the stable section first. Retrieve a whole source module only when several independently required stable sections make section-level retrieval less efficient or a module explicitly has no stable sectional address.

# Phase Compiler
<!-- id: retrieval-intelligence.phases -->

Plans are divided into these execution phases where applicable:

1. classification
2. contract
3. feature-compilation
4. creative-direction
5. structural-fingerprint
6. component-compilation
7. implementation
8. render-inspection
9. critics
10. repair
11. acceptance

A phase exposes only its capability bundles, contracts, exact reference sections, unresolved blockers, and evidence targets. Later phases are not automatically retrieved early.

# Retrieval Budget
<!-- id: retrieval-intelligence.budget -->

Every plan reports estimated stable-section characters/token-equivalents and a whole-module comparison estimate. The acceptance goal is bounded retrieval: the default capability plan should be materially smaller than blindly loading the corresponding active modules. If the stable-section plan exceeds the configured budget, prioritize P0 capabilities, task-critical P1 capabilities, unresolved blockers, and direct dependencies.

# Generated Capability Shards
<!-- id: retrieval-intelligence.generated-shards -->

The build emits generated `capability-shards/` files from canonical control-shard stable sections. These are derived artifacts only. Canonical truth remains `source/controls/*.md` plus the registry. Generated shards MUST contain source provenance and stable IDs and MUST be reproducible byte-for-byte from canonical source.

# Retrieval Handoff
<!-- id: retrieval-intelligence.handoff -->

Execution should consume `phases[].retrievalActions` or `activeCapabilities`, not `activeModules`, unless explicitly debugging the router. This protects context quality as AIFENCE grows.
