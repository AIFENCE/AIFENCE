# AIFENCE Runtime 1.0 Architecture

```text
AIFENCE Core {{CORE_REVISION}} (immutable, vendored, hash-locked)
          │
    CoreProvider
          │
 Parser ─ Classifier ─ Router
          │
    Runtime API
    ├─ CLI
    ├─ MCP tools/resources/prompt
    ├─ Agent Skill fallback
    ├─ Platform installers/adapters
    └─ MCP App / local status UI
```

## Single-source rule

Runtime adapters MUST NOT copy AIFENCE's control logic. The router parses the Core `README.md` creation router, `CONTROL_INDEX.md` activation bundles, `PROFILE_MATRIX.md`, contracts, stable IDs, and machine control registry. Heuristics are limited to classifying a user's natural-language request into Core-defined routes and surfacing ambiguity.

## Core immutability

`core/` is an exact Revision {{CORE_REVISION}} vendoring and `CORE_LOCK.json` hashes every file. Runtime changes do not rewrite Core. A future Core upgrade is a deliberate re-vendor operation followed by tests and a new Runtime release.

## Statelessness

MCP planning is request-scoped. No hidden prior-plan state is required for HTTP clients. This avoids cross-user leakage and makes horizontal deployment straightforward.

## Progressive disclosure

Skill metadata is small; the skill body activates only for relevant work; Runtime returns a retrieval plan; exact Core content is retrieved only when needed. This is intentionally the opposite of dumping 1,300 controls into every model context.
