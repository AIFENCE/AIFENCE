# SAGE 0.2 Technology Compatibility Kit (TCK)

Run the reference implementation:

```bash
sage-tck
sage-tck --json
```

The same vectors live in `src/sage_plugin/tck/vectors/core.json` so installed SDKs can run them without the source checkout.

A conforming implementation must:

1. accept every `valid` vector;
2. reject every `invalid` vector;
3. preserve the parsed structure of `canonical_json`;
4. produce the exact `canonical_msgpack_hex`;
5. produce the exact `canonical_sha256` digest;
6. round-trip the wire object through the SAGE A2A 1.0 DataPart binding without changing it.

The TCK intentionally tests bytes, not only semantic equivalence. That catches map-ordering, float, null-presence, and extension-field drift across languages.
