# AIFENCE Version Model

AIFENCE is a platform composed of independently versioned implementation and protocol surfaces. A single number is intentionally not used to imply that every component has identical compatibility semantics.

| Surface | Current version | Compatibility meaning |
| --- | --- | --- |
| AIFENCE platform | `0.1.0` | Monorepo/application release version |
| Guard implementation | `1.0.0rc5` | Guard API and implementation release |
| Bus implementation | `0.2.7` | Semantic Bus implementation release |
| Quality runtime | `2.0.0` | Canonical Quality source/runtime release |
| Official SDK line | `1.0.0rc5` | Python/TypeScript client compatibility line |
| Bus protocol | `aifence/0.2` | Cross-language semantic handoff protocol |
| Bus wire version | `2` | Frozen wire-envelope schema version |

The executable source of truth for the platform inventory is `src/aifence/versions.py`. Protocol compatibility is governed by TCK vectors, not by comparing implementation package versions.

## Release rule

A platform release may contain component versions that differ. A release is valid only when CI proves that all required SDKs/adapters conform to the Bus protocol and that the version inventory matches package metadata.
