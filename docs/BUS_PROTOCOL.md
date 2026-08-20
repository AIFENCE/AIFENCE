# Bus Protocol Compatibility

The AIFENCE Bus implementation version and the Bus wire protocol version are different contracts. Cross-language compatibility is governed by `aifence/0.2` / wire version `2` and the packaged TCK under `src/aifence/bus/tck/`.

## Rules

- Every wire packet is validated as wire v2 before expansion.
- Canonical JSON, canonical MessagePack and SHA-256 digests must match the shared vectors.
- Invalid vectors must be rejected.
- Required implementations are declared by `src/aifence/bus/tck/implementations.json`.
- CI runs the Python TCK plus deterministic malformed-wire mutation tests and the required JavaScript/Go implementations against the same central vector file.
- Adapter-local copies that are shipped for standalone use must remain byte-identical to the central vectors.

Protocol changes require a new protocol/wire version or an explicitly backward-compatible TCK change. Implementation package version bumps alone do not redefine the wire contract.
