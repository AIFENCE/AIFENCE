---
title: Bus tier
summary: The semantic communication runtime — carries minimum-sufficient state between agents.
infobox:
  Package: aifence.bus
  Mount: /bus
  Config prefix: AIFENCE_BUS_
  Protocol: sage/0.2, wire 2
  Transports: none · memory · Redis · Kafka · RabbitMQ
---

The **bus tier** is a vendor-neutral semantic communication runtime. It carries
the minimum state a downstream agent needs in order to act, rather than
re-sending whole conversations: content-addressed references, immutable deltas,
learned compositional patterns, provenance, and a model of what the receiver
already knows.

It is mounted as a sub-application at `/bus` and writes to the composed
application's shared database.

## Durable delivery

The bus is a durable, at-least-once, lease-based message bus:

```text
handoff ──▶ pending ──▶ claimed ──▶ acknowledged
                          │
                          └─▶ lease expiry ──▶ claimable again
```

A handoff is committed to the database before it is considered delivered.
Receiver knowledge advances only after acknowledgement, so a message that is
claimed but never acked is redelivered rather than lost.

## Semantic compression

Rather than compressing bytes, the bus compresses *meaning*, and its safety
rules are about what may not be compressed:

- Negation, amounts, identities, authorization, deadlines, environment markers,
  instructions and constraints take the strict preservation path.
- Unknown or ambiguous meaning is kept as a literal or a reference rather than
  being mapped to an uncertain semantic code.
- Large content is referenced (`aifence:sha256:…`) rather than copied.

Semantic memory distinguishes fact, observation, inference, hypothesis,
prediction, preference, instruction and constraint. Conflicting claims coexist
with provenance and confidence instead of overwriting each other, and dependency
edges let derived claims be invalidated transitively.

## Learned patterns

Recurring semantic structures are stored as candidates, then move through shadow
validation and counterfactual evaluation before becoming active. Decisions
account for frequency, estimated savings, stability, ambiguity, source trust and
diversity, holdout evidence, and receiver-specific fidelity. Patterns that drift
are suppressed for the affected receiver while remaining available where their
measured fidelity holds.

## Content-addressed references

Stored content uses a SHA-256 content identity. Authorization and lifetime are
separate grants, so identical bytes deduplicate without sharing authorization.
Grants support workspace and owner scope, agent ACLs, allowed field paths,
memory tier, TTL, provenance, and optional AES-GCM encryption at rest.
Forwarding a reference delegates policy without duplicating the object.

## Broker transports

By default the durable bus is the only carrier. Larger deployments can fan
committed handoffs out to a broker:

| Backend | Mechanism | Extra |
| --- | --- | --- |
| `none` | No fan-out (default) | — |
| `memory` | In-process, for tests | — |
| `redis` | Redis Stream (`XADD`), bounded | `redis` |
| `kafka` | Topic, keyed by receiver | `kafka` |
| `rabbitmq` | Durable topic exchange | `rabbitmq` |

Two invariants govern this:

1. **Publication follows the durable commit.** A broker outage cannot invent a
   delivery that was not persisted, and never rolls back the durable record.
2. **Events carry identity, not content.** Only message id, receiver, sender,
   workspace, correlation id and size are published; subscribers resolve content
   from the bus. A misconfigured topic therefore cannot leak semantic content.

A publish failure is reported in the receipt's `fanout` field rather than
failing the request or being reported as a success. An unknown backend name
fails at startup instead of silently disabling fan-out.

## Protocol and conformance

The bus reads and writes `sage/0.2`, wire version 2. Protocol identity is
canonical MessagePack plus SHA-256; JSON is a readable representation. A
language-neutral conformance kit of 13 normative vectors (6 valid, 7 invalid)
is consumed independently by Python, JavaScript and Go implementations.
