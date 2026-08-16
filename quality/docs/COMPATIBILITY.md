# BizIQ Runtime/Core Compatibility

BizIQ generated releases use an exact generated-core compatibility policy. A generated Runtime must execute against the Core revision recorded in its build metadata unless a later compatibility document explicitly permits another pairing.

| Runtime | Core | Policy |
|---|---|---|
| 1.1.1 | 1.7.1 | Exact generated core |
| 1.1.0 | 1.7 | Exact generated core |

Compatibility is recorded in `build/BUILD_PROVENANCE.json`, the generated runtime configuration, `dist/release-manifest.json`, and `dist/release-provenance.json`.
