# SAGE Protocol 0.2 — Frozen Core

Status: **Frozen for the 0.2.x line**. SAGE 0.2 is the first deployable protocol baseline. Writers and readers MUST use wire version `2`; other wire versions are invalid.

SAGE is a semantic payload and shared-context protocol. It does **not** define agent task lifecycle, tool execution, model inference, or transport. A2A, MCP, HTTP, queues, sockets, and framework-native adapters may carry SAGE without changing its semantics.

## Normative objects

The normative JSON Schemas are in `spec/schemas/` and are packaged with the Python distribution. The frozen objects are:

- `Packet`: readable semantic packet model.
- `Wire`: compact transport form for a packet.
- `Ref`: content-addressed memory reference metadata.
- `State`: immutable state snapshot metadata.
- `Delta`: lossless JSON-Patch-style transition (`add`, `remove`, `replace`).
- `Concept`: versioned semantic codebook entry.
- `Pattern`: higher-order semantic template bound to a concept code, with lifecycle and confidence metadata.
- `Capability`: protocol/codebook/capability negotiation state.
- `Provenance`: source IDs, observation time, confidence, derivation, producer.
- `Ack`: durable delivery acknowledgement/nacknowledgement.
- `Error`: portable error object.

## Wire v2

Wire v2 uses compact keys. The field names below are frozen for 0.2.x:

| Key | Meaning |
|---|---|
| `v` | wire version, integer `2` |
| `c` | codebook namespace |
| `a` | act/intention |
| `i` | packet ID |
| `s` | sender |
| `r` | receiver |
| `x` | semantic atoms |
| `R` | references |
| `b` | base state ID |
| `d` | delta |
| `p` | provenance |
| `m` | protocol metadata |
| `g` | optional packet signature object (`alg`, `kid`, `sig`) |
| `z` | optional W3C trace context (`p` traceparent, `s` tracestate) |

Atom keys are `c` (concept code), `v` (concept version), `l` (literal), `h` (literal-presence marker), `p` (path), `q` (confidence), and `e` (epistemic type). `h=1` is required when a literal is intentionally JSON `null`, so absence and explicit null remain distinguishable. `e` distinguishes facts/observations/inferences/hypotheses/predictions/preferences/instructions/constraints; omitted `e` means `fact`.

Unknown top-level and atom fields are invalid in wire v2. New optional fields require a new wire version.

## Canonical encoding

Canonical encoding exists for hashing, signatures, test vectors, caches, and cross-language conformance.

1. Objects MUST use string keys.
2. Object keys are recursively sorted lexicographically by Unicode code point.
3. Arrays retain order.
4. NaN and infinities are forbidden.
5. Canonical JSON is UTF-8, unescaped Unicode where JSON permits it, no insignificant whitespace, and no NaN/Infinity. Canonical JSON is a normalized readable representation, not the cross-runtime identity primitive for floating-point text.
6. Canonical MessagePack uses the same recursively sorted structure, `bin` for bytes, UTF-8 strings, and 64-bit floats.
7. A canonical SAGE digest is `sha256:` followed by the SHA-256 hex digest of canonical MessagePack bytes. Canonical MessagePack bytes and this digest are the cross-runtime protocol identity.

The Python reference functions are `canonical_json_bytes`, `canonical_msgpack_bytes`, and `canonical_digest` in `sage_plugin.protocol_spec`.

An optional protobuf binding is published at `spec/sage-v0.2.proto`. Protobuf field numbers are frozen for the 0.2.x line, but protobuf bytes are **not** canonical SAGE bytes and MUST NOT be used for the SAGE canonical digest; canonical MessagePack remains the digest source.


## Trace context

Wire v2 MAY carry W3C Trace Context in `z`. `z.p` is a validated `traceparent`; `z.s` is optional `tracestate`. Trace context is diagnostic metadata and MUST NOT be used for authentication or authorization. Canonical encoding, signatures, and TCK vectors include the trace object when present.

## Compatibility and negotiation

The protocol identifier is `sage/0.2` and the wire version is integer `2`. SAGE 0.2 is the initial protocol baseline; peers that do not support it fail negotiation rather than translating between protocol generations.

Peers negotiate the highest mutually supported SAGE protocol, codebook namespace/fingerprint, max packet size, ref/delta support, fallback modes, and latent spaces. If no common protocol exists, communication MUST fall back outside SAGE or fail explicitly; a peer MUST NOT assign meaning to an undefined semantic code.

## Higher-order patterns

SAGE pattern learning composes recurring semantic units into exact templates. A pattern definition contains a stable signature, ordered component composition, relation/path structure, lifecycle state, confidence, and the ordinary concept code used on the wire. Dynamic literal values are represented as typed slots and are carried as atom bindings, so pattern compression remains lossless.

Pattern lifecycle is `candidate → shadow → validated → active`; active patterns may move through `cooling`, `deprecated`, or `retired`. Shadow patterns MUST NOT alter live packet semantics. Task feedback may move a shadow pattern to `validated`, but production activation requires counterfactual full-vs-compressed evidence by default. Active patterns are transmitted through normal atoms, so the wire protocol does not require a special pattern field. Patterns MAY compose other patterns as a directed graph while retaining a lossless flattened composition for wire matching and fallback.

The normative pattern definition schema is `spec/schemas/pattern-v0.2.schema.json`. Pattern candidates and learning statistics are runtime persistence objects, not wire objects.


## Semantic safety and epistemics

SAGE compression MUST fail open when preservation cannot be demonstrated. Critical semantics such as negation, quantities, identity, authorization, deadlines, environment names, and constraints receive stricter preservation thresholds. Unknown or ambiguous concepts MUST carry a literal or reference fallback. An implementation MUST NOT convert a hypothesis, prediction, preference, instruction, or constraint into an unqualified fact while compressing.

Contradictory facts MAY coexist. Implementations that maintain semantic memory SHOULD preserve provenance/confidence for both sides, represent the conflict explicitly, and causally invalidate derived facts when a dependency becomes stale. These memory rules do not change wire v2 syntax.

## Content-addressed references and selective disclosure

Reference identity is content-derived: the reference implementation uses `sage:sha256:<64 lowercase hex digits>` over canonical content bytes. Authorization, TTL, memory tier, provenance, and allowed field paths are grants attached to the content object and are not part of its identity. The same content therefore has one ref identity while different workspaces/agents may hold different grants. Zero-copy forwarding grants access to the existing object instead of duplicating its payload.

## Packet signatures

Wire v2 may carry `g`, an Ed25519 signature object with `alg`, `kid`, and URL-safe-base64 `sig`. The signature covers canonical MessagePack bytes of the entire wire object with `g` removed. A receiver configured to require signatures MUST reject unsigned packets and MUST reject verification failures. Transport/authentication and replay/idempotency policy remain deployment concerns; SAGE durable delivery uses message IDs and at-least-once semantics.

## A2A binding

A2A 1.0 owns peer-agent discovery, task lifecycle, streaming, cancellation, and delivery semantics. SAGE is carried as an A2A `DataPart`:

```json
{
  "data": {
    "sageProtocol": "sage/0.2",
    "wire": {"v": 2, "c": "global", "a": "handoff", "p": {}}
  },
  "mediaType": "application/vnd.sage.packet+json"
}
```

Agents advertise SAGE through an A2A extension URI. A SAGE-enabled AgentCard still includes A2A 1.0's required `defaultInputModes`, `defaultOutputModes`, and `skills`; the reference helper advertises the SAGE media type and a semantic-handoff skill. SAGE does not redefine A2A `Task`, `Message`, `Artifact`, streaming, or cancellation.

## MCP binding

MCP is an adapter for tools/context access. SAGE core MUST NOT depend on MCP types, sessions, task lifecycle, or SDK behavior. The MCP adapter exposes SAGE operations (`send`, `receive`, memory, bus, explain, eval) and may be replaced without altering SAGE wire semantics.

## Delivery and idempotency

The SAGE durable bus is at-least-once. Consumers MUST use `message_id`/correlation IDs for idempotent side effects. Receiver knowledge is advanced only on ACK, never on claim/pull alone.

## Conformance

An implementation claiming `sage/0.2` conformance MUST pass the TCK vectors in `tck/vectors/core.json`, including canonical MessagePack, digest identity, structural JSON validation, schema rejection, and A2A DataPart round-trip tests. The reference conformance command may additionally run deterministic malformed-wire mutations; those are supplemental hardening checks and do not change the frozen vector set.
