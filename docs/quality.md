---
title: Quality tier
summary: Scores AI-generated artifacts against production quality controls before anything else sees them.
infobox:
  Package: aifence.quality
  Mount: /v1/quality
  Control registry: quality/source/control_registry.csv
  Optional extra: quality (jsonschema)
---

The **quality tier** is the first gate in the [fence flow](fence-flow.md). It
scores an AI-generated artifact and decides whether it is fit to proceed. A
failing artifact is stopped before the [guard](guard.md) tier ever evaluates the
action, so effort is not spent enforcing policy on work that was never usable.

## Architecture

The canonical quality-control pack — standards, controls, schemas and profiles —
lives under the repository's top-level `quality/` directory and keeps its own
Node builder. The Python package `aifence.quality` is a *bridge*: it reads the
control registry and runs a fast, deterministic gate in process.

```text
quality/source/control_registry.csv   ~1,000 canonical controls
        │
        ▼
aifence.quality.controls              loader, capability lookup
        │
        ▼
aifence.quality.gate                  the in-process gate
```

Deep, family-native evaluation remains the job of the quality runtime under
`quality/`; the bridge implements the subset that can gate a request
synchronously.

## Checks

Each check carries a weight, and every check is attributed back to a canonical
control capability so a score can be traced to the standard that produced it.

| Check | Weight | Mandatory | What it catches |
| --- | ---: | --- | --- |
| `completeness` | 40 | yes | An empty artifact. |
| `anti_template` | 25 | yes | Unresolved `TODO`, `TBD`, `PLACEHOLDER`, `Lorem ipsum`. |
| `answerability` | 15 | no | Too little substance to be useful. |
| `link_integrity` | 10 | no | Empty or placeholder links in markup. |
| `structure` | 10 | no | Missing headings or landmarks in markup. |
| `json_validity` | 35 | yes | JSON artifacts that do not parse. |
| `schema_conformance` | 25 | yes | Output violating a supplied JSON Schema. |
| `grounding` | 20 | conditional | Numeric claims absent from the supplied sources. |

Markup checks run only for `text/html` and `text/markdown`; JSON checks only for
JSON content types; grounding only when `sources` are supplied.

## Outcomes

The gate produces one of three outcomes:

- **`accept`** — score meets the threshold and no mandatory check failed.
- **`revise`** — no mandatory failure, but the score is below `min_score`.
- **`reject`** — a mandatory check failed. Score is irrelevant.

This is why an artifact can score well and still be rejected: a single
unresolved placeholder is disqualifying regardless of how good the rest is.

## Schema conformance

When a JSON Schema is supplied, structured output is validated against it. With
the `quality` extra installed, full JSON Schema validation applies, including
constraints such as `minimum`. Without it, the gate falls back to a
required-property and type subset, so a missing contract field is still caught
rather than the check passing silently.

## Grounding

Given `sources`, the gate reports numeric claims in the artifact that appear
nowhere in the source material. It is a conservative signal and makes no claim
about prose accuracy — but an invented figure is the most common and most costly
fabrication in generated business artifacts, and unlike tone it is checkable.

Severity is tiered: a single unsourced figure is a warning, while a cluster
(more than two) fails the gate outright, because weighted scoring alone would
otherwise let a document full of invented numbers through.

```jsonc
// sources say 4.2M / 12% / 1500 accounts
"Revenue reached 9.9 million, up 87 percent, across 4200 accounts…"
// → grounding: 4 numeric claim(s) absent from sources → reject
```

## API

See the [API reference](api.md#quality) for request and response shapes.

| Endpoint | Purpose |
| --- | --- |
| `GET /v1/quality/registry` | Summary of the loaded control registry. |
| `GET /v1/quality/controls` | List controls, filterable by priority. |
| `POST /v1/quality/evaluate` | Run the gate over an artifact. |

All three require an authenticated API key; the quality tier is part of the
fence, not a public surface.
