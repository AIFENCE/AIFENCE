"""Deterministic multi-turn semantic-context compression benchmark (issue #16, stage 2).

This benchmark measures how twelve context-compression strategies (the RFC
variants) carry a fixed multi-turn conversation, using only deterministic,
observable data -- no model, no provider, no random numbers. It is the
companion to stage 1's context-accounting instrumentation
(``aifence.bus.context_accounting``): the AIFENCE variants run the REAL
``AifenceCodec`` with ``context_accounting_enabled=True`` and surface the
per-exchange ``ContextReport`` fields (codebook/pattern setup, decoding
volume, reference-fetch volume, fallbacks) so hidden decompression costs are
visible.

Run it with no arguments to print the four summary tables to stdout:

    uv run --with '.[dev,mcp]' python scripts/compression_benchmark.py

Pass ``--out <dir>`` to additionally write deterministic JSON and CSV
artifacts (``compression_benchmark.json`` / ``compression_benchmark.csv``)
into ``<dir>``.

Scenario
--------
RFC "Phoenix" fixture, fully embedded below (no external files):

* Phase 1 -- shared context transmitted once before the first update.
* Phase 2 -- five updates that mutate a project state (blocked by failing
  integration tests -> failures fixed -> a database-migration failure ->
  migration approved -> ready for production deployment).  Each update also
  carries an embedded ground-truth state dictionary.
* Phase 3 -- after each update a downstream task is scored against the
  embedded ground-truth answer key: five QA questions (is deployment
  allowed; what blocks it; which team acts next; was the migration
  approved; what changed since the previous update), state reconstruction
  (four state fields), constraint compliance (two Phase-1 constraints), and
  action selection.

Because the ground truth is embedded, task-performance scoring is fully
deterministic: a rule-based reader (``read_state``) extracts the predicted
state from each variant's reconstruction text and the answers are compared
exactly against the ground-truth key.  The reader is documented as a
"perfect-reader oracle": it isolates representation quality from model
quality.

The twelve RFC variants
-----------------------
Each variant encodes the same scenario and is measured with the same
metrics.  Variants 1-8 are plain serialization/string operations; variants
9-12 run the real ``AifenceCodec``:

 1.  full natural-language context every turn   -- receiver keeps everything
 2.  latest-only message                        -- receiver keeps only the
                                                 most recent message
 3.  minified JSON                              -- full history as a compact
                                                 JSON array
 4.  MesaifencePack                                -- same content, msgpack wire
 5.  conventional state snapshots               -- a key/value state dict
                                                 replaced each turn
 6.  conventional state deltas                  -- base snapshot + JSON-Patch
                                                 style operations
 7.  LLM summaries                              -- DETERMINISTIC extractive
                                                 stub (sentence precision);
                                                 no provider is ever required
 8.  retrieval of relevant prior messages       -- deterministic
                                                 keyword/recency selector
 9.  AIFENCE codebooks only                        -- real codec, semantic
                                                 packets, patterns disabled
 10. AIFENCE codebooks + learned patterns          -- real codec; a pattern is
                                                 learned in a warm-up
                                                 exchange and activated
 11. AIFENCE references + state deltas             -- real codec; Phase 1 as a
                                                 reference, updates as
                                                 state deltas
 12. full AIFENCE with ACKed receiver knowledge    -- real codec; state dicts
                                                 encoded semantically and
                                                 decoded with
                                                 ``acknowledge=True`` so the
                                                 receiver's codebook
                                                 knowledge accumulates

Provider policy
---------------
The benchmark never invokes an external provider.  A provider is considered
configured when ``AIFENCE_BUS_BENCH_LLM_PROVIDER`` is a non-empty environment
variable.  Any variant whose ``requires_provider`` flag is set is skipped
cleanly when no provider is configured and reported as
"not run, no provider" (mirroring the adapter-skip convention of
``scripts/model_matrix_benchmark.py``: provider numbers are never
fabricated).  No built-in variant currently requires a provider: variant 7
uses the deterministic extractive stub, so all twelve rows run with zero
configuration.

Metrics
-------
Efficiency (per exchange and cumulative): wire bytes (canonical JSON and
MesaifencePack), stored bytes (state/reference stores), model-facing input
tokens (tokens of the transmitted representation rendered as JSON text),
model-facing output tokens (tokens of the reconstructed context the
receiver must read), encode/decode latency (measured with
``time.perf_counter``, rounded to ms -- reported ONLY in the JSON detail
artifacts, never in the printed tables), reference-fetch volume
(bytes/count; ReferenceStore fetches only -- state-store resolves are not
instrumented separately), and a cumulative cost.  The cost model
is synthetic but deterministic and documented::

    cost_usd = wire_bytes_json * 0.0000005        # $0.50 / MB
             + model_output_tokens * 0.000002     # $2.00 / Mtok
             + reference_fetch_bytes * 0.0000002  # $0.20 / MB fetched

Task performance: QA accuracy (exact match on the five questions per turn),
state-reconstruction accuracy (four fields), constraint compliance (the two
Phase-1 constraints recoverable from the final reconstruction), action
accuracy (action derived from the reconstructed state), and task success
(the mean of those four).

Semantic fidelity -- per-fact-type preservation checks on the
reconstruction, each scored 0..1 and averaged:

* negation: per-turn stance of the "deployment allowed" fact (turns 1-4
  "not allowed", turn 5 "allowed").  Passes when the reconstruction
  expresses the expected stance ("ready for production deployment" /
  "deployment_allowed: true" for allowed; "blocked" / "not allowed" /
  "deployment_allowed: false" for not allowed).  A reconstruction that
  cannot express a stance (e.g. a message with no stance marker) fails.
* numeric: the numbers "three" (turn 1), "two" (turn 2), "one" (turn 3)
  must be recoverable from the corresponding turn's reconstruction.
* ownership: "the payment service is owned by the Commerce team" -- the
  final reconstruction must contain both "payment service" and
  "commerce team".
* temporal ordering: "blocked" (turn 1) must appear before "ready for
  production deployment" (turn 5) in the final reconstruction.
* changed-value: the final reconstruction must support recovering that the
  failing-test count changed (contains a "three"/3 and a "one"/1 or
  "two").
* contradiction: the migration-failure -> migration-approved transition
  must be recoverable ("migration" and "failure" and "approved" all
  present).
* critical-fact recall: the two Phase-1 constraints ("production
  deployments require all integration tests to pass"; "database migrations
  must be reviewed by the platform team") must survive into the final
  reconstruction.

All checks run on lowercase text with underscores normalized to spaces.

Amortization (vs the full-context baseline, variant 1): setup cost
(codebook + pattern setup bytes/tokens, 0 for plain variants), saving per
use (baseline total minus variant total, divided by the 6 conversation
turns), and break-even = ``ceil(setup_cost / max(saving_per_use, 1))``.
When the saving per use is non-positive the denominator clamps to 1 and the
break-even equals the setup cost -- interpret that as "does not break even";
compare with the saving column.  Two semantics notes: (1) the codebook-setup
component includes the ~24-byte codebook fingerprint re-sent on every
exchange, so the setup cost is partly recurring (AIFENCE break-even values are
therefore conservative); (2) a zero-setup/zero-saving variant prints
``break_even 0`` -- immediately at parity, nothing to amortize.

Determinism
-----------
* No RNG, no wall-clock time in the output; artifact metadata uses the
  fixed timestamp ``2026-08-01T00:00:00+00:00``.
* AIFENCE packet ids are pinned to sha256-derived ids per (variant, turn); the
  printed tables and artifacts never contain packet ids.
* The AIFENCE codec uses a fixed ``Provenance``, ``use_cache=False``,
  ``record_learning=False``, ``auto_learn=False`` (except the variant-10
  pattern warm-up), and an isolated SQLite database whose schema is reset
  per variant.  ``AIFENCE_BUS_DATABASE_URL`` must be set before the first
  ``aifence.bus`` import; the standalone entry point does this in
  ``main()`` before any lazy import, and deletes its scratch database on
  exit.
* Determinism: every printed table and the summary ``tables.*`` rows are
  byte-identical across runs. Measured encode/decode latency lives only in
  the JSON detail (``variants[*].turns[*].*_latency_ms`` and
  ``variants[*].efficiency.*_latency_ms_mean``); two runs' JSON artifacts
  are byte-identical once those ``*_latency_ms`` fields are dropped.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import statistics
import time
from pathlib import Path
from typing import Any

import msgpack

# ---------------------------------------------------------------------------
# Scenario (RFC Phoenix fixture, fully embedded)
# ---------------------------------------------------------------------------

SHARED_CONTEXT = (
    "Project Phoenix uses Python 3.12. "
    "Production deployments require all integration tests to pass. "
    "The payment service is owned by the Commerce team. "
    "Database migrations must be reviewed by the platform team."
)

UPDATES = [
    "Project Phoenix is blocked because three integration tests failed.",
    "The Commerce team fixed two failures.",
    "One database migration failure remains.",
    "The platform team approved the migration.",
    "Project Phoenix is ready for production deployment.",
]

STATE_DICTS = [
    {"project": "phoenix", "python_version": "3.12", "deployment_allowed": False, "failed_tests": 0, "migration_approved": False, "blocker": "none"},
    {"project": "phoenix", "python_version": "3.12", "deployment_allowed": False, "failed_tests": 3, "migration_approved": False, "blocker": "integration_tests"},
    {"project": "phoenix", "python_version": "3.12", "deployment_allowed": False, "failed_tests": 1, "migration_approved": False, "blocker": "integration_tests"},
    {"project": "phoenix", "python_version": "3.12", "deployment_allowed": False, "failed_tests": 1, "migration_approved": False, "blocker": "migration"},
    {"project": "phoenix", "python_version": "3.12", "deployment_allowed": False, "failed_tests": 1, "migration_approved": True, "blocker": "integration_tests"},
    {"project": "phoenix", "python_version": "3.12", "deployment_allowed": True, "failed_tests": 0, "migration_approved": True, "blocker": "none"},
]

#: Per-turn "what changed since the previous update?" markers.  A turn's
#: question is answered correctly when the reconstruction contains at least
#: one of that turn's markers (natural-language phrases and/or rendered
#: state forms).
CHANGE_MARKERS: dict[int, list[str]] = {
    1: ["three integration tests failed", "blocked", "blocker: integration_tests"],
    2: ["fixed two failures", "failed_tests: 1"],
    3: ["migration failure remains", "migration_failure", "blocker: migration"],
    4: ["approved the migration", "migration_approved"],
    5: ["ready for production deployment", "deployment_allowed"],
}

#: Synthetic but deterministic cost model (documented in the module docstring).
WIRE_COST_PER_BYTE_USD = 0.0000005
TOKEN_COST_PER_TOKEN_USD = 0.000002
REF_BYTE_COST_PER_BYTE_USD = 0.0000002

#: Fixed artifact timestamp (SOURCE_DATE_EPOCH-style).
FIXED_TIMESTAMP = "2026-08-01T00:00:00+00:00"

PROVIDER_ENV = "AIFENCE_BUS_BENCH_LLM_PROVIDER"
NO_PROVIDER_NOTE = "not run, no provider"

SUMMARY_PRECISION_THRESHOLD = 0.7
RETRIEVAL_MAX_RESULTS = 5

#: Vocabulary used by the deterministic extractive-summary stub (variant 7).
CRITICAL_TOKENS = frozenset(
    {
        "project", "phoenix", "python", "production", "deployments", "deployment",
        "integration", "tests", "test", "pass", "payment", "service", "owned",
        "commerce", "team", "database", "migrations", "migration", "reviewed",
        "review", "platform", "blocked", "because", "three", "failed", "failures",
        "failure", "fixed", "two", "one", "remains", "approved", "ready",
    }
)

#: Query keywords used by the deterministic retrieval selector (variant 8).
RETRIEVAL_KEYWORDS = frozenset(
    {
        "blocked", "failed", "failure", "approved", "migration", "integration",
        "commerce", "platform", "ready", "deployment", "payment", "reviewed",
        "review", "pass", "fixed", "remains", "three", "two", "one", "owned",
        "team", "test",
    }
)

_STATE_FIELDS = ("deployment_allowed", "failed_tests", "migration_approved", "blocker")
_RENDERED_RE = re.compile(r"\b(deployment_allowed|failed_tests|migration_approved|blocker)\s*:\s*([a-z0-9_.]+)")
_DIGIT_RE = re.compile(r"(?<!\d)(\d+)(?!\d)")
# Word-boundary matchers for the fidelity number/constraint checkers.
# The negative lookarounds also exclude hyphenated compounds ("thirty-three")
# and prefixed forms ("bypass", "threefold", "someone") so a CONTRADICTED or
# unrelated word cannot satisfy a preservation check.
_NUM_WORD_RE = {
    "three": re.compile(r"(?<![\w-])three(?![\w-])"),
    "two": re.compile(r"(?<![\w-])two(?![\w-])"),
    "one": re.compile(r"(?<![\w-])one(?![\w-])"),
}
_PASS_WORD_RE = re.compile(r"(?<![\w-])pass(?:es|ed|ing)?(?![\w-])")
# Sentence boundaries: ". " / "; " sequences, newlines, and the '","' separator
# that joins messages inside minified-JSON / msgpack reconstructions.
_SENTENCE_RE = re.compile(r"[.;]\s+|,\s*\"|\n+")


# ---------------------------------------------------------------------------
# Deterministic helpers
# ---------------------------------------------------------------------------


def _norm(text: str) -> str:
    """Lowercase text with underscores normalized to spaces."""
    return text.lower().replace("_", " ")


def _estimate_tokens(text: str) -> int:
    """Deterministic token estimate (same estimator the codec uses).

    Lazily imported so the standalone entry point can bind its scratch
    database URL before any ``aifence.bus`` import happens.
    """
    from aifence.bus.context_accounting import estimate_tokens

    return estimate_tokens(text)


def _ms_since(started: float) -> int:
    return int(round((time.perf_counter() - started) * 1000.0))


def break_even(setup_cost: float, saving_per_use: float) -> int:
    """Break-even point in uses: ``ceil(setup / max(saving, 1))``.

    A zero setup cost breaks even immediately (0 uses).  A non-positive
    saving clamps the denominator to 1 so the result equals the setup cost
    -- documented as "does not break even"; compare with the saving column.
    """
    return math.ceil(max(0.0, float(setup_cost)) / max(float(saving_per_use), 1.0))


def render_state_text(state: dict[str, Any]) -> str:
    """Deterministic 'key: value' rendering of a state dict (sorted keys)."""
    return "; ".join(f"{key}: {value}" for key, value in sorted(state.items()))


def read_state(text: str) -> dict[str, Any]:
    """Deterministic rule-based reader of a variant's reconstruction.

    Two forms are understood:

    * rendered state form -- ``deployment_allowed: false`` style key/value
      pairs (produced by the state-snapshot/delta variants and by AIFENCE
      state packets).  The MOST RECENT value for each field wins.
    * natural-language form -- the scenario's sentences, processed
      chronologically as a tiny state machine.

    Returns a dict with keys ``deployment_allowed``, ``failed_tests``,
    ``migration_approved``, ``blocker``; unknown values are ``None``.
    """
    if _RENDERED_RE.search(text.lower()):
        return _read_rendered_state(text.lower())
    return _read_natural_state(text)


def _read_rendered_state(text: str) -> dict[str, Any]:
    state: dict[str, Any] = {field: None for field in _STATE_FIELDS}
    for match in _RENDERED_RE.finditer(text):
        field, raw = match.group(1), match.group(2)
        state[field] = _parse_rendered_value(raw)
    return state


def _parse_rendered_value(raw: str) -> Any:
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw == "none":
        return "none"
    if raw.isdigit():
        return int(raw)
    return raw


def _read_natural_state(text: str) -> dict[str, Any]:
    tests_failing = False
    migration_failing = False
    migration_approved = False
    ready = False
    failed_tests: int | None = None
    for sentence in _SENTENCE_RE.split(text):
        s = _norm(sentence)
        if "ready for production deployment" in s:
            ready = True
            tests_failing = False
            failed_tests = 0
        if "all integration tests pass" in s:
            tests_failing = False
        if "integration test" in s and ("failed" in s or "failure" in s):
            tests_failing = True
        if "fixed" in s and "failures" in s:
            tests_failing = True
            if failed_tests is not None:
                failed_tests = max(0, failed_tests - 2)
        if "migration" in s:
            if "failure" in s:
                migration_failing = True
            if "approved" in s:
                migration_approved = True
                migration_failing = False
        if "three" in s and "integration tests failed" in s:
            failed_tests = 3
        if "one" in s and "integration test failed" in s:
            failed_tests = 1
        if "one" in s and "failure remains" in s and "migration" not in s:
            failed_tests = 1
    blocker: str | None
    if ready:
        blocker = "none"
    elif migration_failing:
        blocker = "migration"
    elif tests_failing:
        blocker = "integration_tests"
    else:
        blocker = None
    return {
        "deployment_allowed": ready,
        "failed_tests": failed_tests,
        "migration_approved": migration_approved,
        "blocker": blocker,
    }


def next_team(blocker: Any) -> str | None:
    return {"integration_tests": "commerce_team", "migration": "platform_team", "none": "none"}.get(blocker)


def action_for(next_team_value: Any) -> str | None:
    return {"commerce_team": "fix_integration_tests", "platform_team": "review_migration", "none": "deploy"}.get(next_team_value)


def extractive_summary(sentences: list[str], threshold: float = SUMMARY_PRECISION_THRESHOLD) -> list[str]:
    """Deterministic sentence-precision summarization stub (variant 7).

    A sentence is kept when the fraction of its tokens that belong to the
    fixed ``CRITICAL_TOKENS`` vocabulary is at least ``threshold``.  The
    kept sentences preserve their original order.
    """
    kept: list[str] = []
    for sentence in sentences:
        tokens = re.findall(r"[a-z0-9]+", sentence.lower())
        if not tokens:
            continue
        critical = sum(1 for token in tokens if token in CRITICAL_TOKENS)
        if critical / len(tokens) >= threshold:
            kept.append(sentence)
    return kept


def retrieval_select(messages: list[str], max_results: int = RETRIEVAL_MAX_RESULTS) -> list[str]:
    """Deterministic keyword/recency retrieval selector (variant 8).

    Messages containing at least one ``RETRIEVAL_KEYWORDS`` term are
    candidates; the most recent ``max_results`` candidates are kept (the
    latest message is always included), then returned in chronological
    order.
    """
    indices = {id(message): index for index, message in enumerate(messages)}
    matched = [message for message in messages if any(keyword in _norm(message) for keyword in RETRIEVAL_KEYWORDS)]
    latest = messages[-1] if messages else None
    if latest is not None and latest not in matched:
        matched = matched + [latest]
    selected = matched[-max_results:]
    selected.sort(key=lambda message: indices[id(message)])
    return selected


# ---------------------------------------------------------------------------
# Fidelity checks
# ---------------------------------------------------------------------------


def stance(text: str) -> str | None:
    t = _norm(text)
    # ``_norm`` maps underscores to spaces, so the rendered-state markers are
    # matched in their normalized form ("deployment allowed: true/false").
    if "ready for production deployment" in t or "deployment allowed: true" in t:
        return "allowed"
    if "blocked" in t or "not allowed" in t or "deployment allowed: false" in t:
        return "not_allowed"
    return None


def fidelity_negation(turn_texts: list[str]) -> float:
    """Stance of the deployment-allowed fact, per turn (5 instances)."""
    expected = ["not_allowed", "not_allowed", "not_allowed", "not_allowed", "allowed"]
    # strict=False: shorter inputs (e.g. empty) score 0.0 rather than raising
    correct = sum(1 for text, want in zip(turn_texts, expected, strict=False) if stance(text) == want)
    return correct / len(expected)


def _has_digit(text: str, digit: str) -> bool:
    """True when ``digit`` appears as a standalone number anywhere in ``text``."""
    return any(run == digit for run in _DIGIT_RE.findall(text))


def fidelity_numeric(turn_texts: list[str]) -> float:
    """Numbers 'three'/'two'/'one' recoverable from turns 1-3."""
    texts = [""] * 3
    for index, text in enumerate(turn_texts[:3]):
        texts[index] = _norm(text)
    t1, t2, t3 = texts
    ok1 = bool(_NUM_WORD_RE["three"].search(t1)) or _has_digit(t1, "3")
    ok2 = bool(_NUM_WORD_RE["two"].search(t2)) or _has_digit(t2, "2")
    ok3 = bool(_NUM_WORD_RE["one"].search(t3)) or _has_digit(t3, "1")
    return sum([ok1, ok2, ok3]) / 3


def fidelity_ownership(final_text: str) -> float:
    t = _norm(final_text)
    return 1.0 if ("payment service" in t and "commerce team" in t) else 0.0


def fidelity_ordering(final_text: str) -> float:
    t = _norm(final_text)
    earlier, later = "blocked", "ready for production deployment"
    if earlier in t and later in t:
        return 1.0 if t.index(earlier) < t.index(later) else 0.0
    return 0.0


def fidelity_changed_value(final_text: str) -> float:
    t = _norm(final_text)
    has_old = bool(_NUM_WORD_RE["three"].search(t)) or _has_digit(t, "3")
    has_new = bool(_NUM_WORD_RE["one"].search(t)) or bool(_NUM_WORD_RE["two"].search(t)) or _has_digit(t, "1")
    return 1.0 if (has_old and has_new) else 0.0


def fidelity_contradiction(final_text: str) -> float:
    """The migration-failure -> migration-approved transition must be
    recoverable: both markers present AND the failure precedes the approval
    (an approval followed by a later failure is the opposite transition)."""
    t = _norm(final_text)
    if "migration" not in t or "failure" not in t or "approved" not in t:
        return 0.0
    return 1.0 if t.index("failure") < t.index("approved") else 0.0


def fidelity_critical(final_text: str) -> float:
    """Two Phase-1 constraints must survive into the final reconstruction."""
    t = _norm(final_text)
    c1 = "production deployment" in t and "integration test" in t and bool(_PASS_WORD_RE.search(t))
    c2 = "migration" in t and "review" in t and "platform team" in t
    return (float(c1) + float(c2)) / 2.0


def fidelity_scores(turn_texts: list[str], final_text: str) -> dict[str, float]:
    return {
        "negation": fidelity_negation(turn_texts),
        "numeric": fidelity_numeric(turn_texts),
        "ownership": fidelity_ownership(final_text),
        "temporal_ordering": fidelity_ordering(final_text),
        "changed_value": fidelity_changed_value(final_text),
        "contradiction": fidelity_contradiction(final_text),
        "critical_fact_recall": fidelity_critical(final_text),
    }


# ---------------------------------------------------------------------------
# Ground truth and per-turn evaluation
# ---------------------------------------------------------------------------


def _yes_no(value: Any) -> str | None:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return None


def ground_truth_answers(turn_index: int) -> dict[str, Any]:
    ground = STATE_DICTS[turn_index]
    qa = {
        "is_deployment_allowed": _yes_no(ground["deployment_allowed"]),
        "blocker": ground["blocker"],
        "next_team": next_team(ground["blocker"]),
        "migration_approved": _yes_no(ground["migration_approved"]),
        "what_changed": True,
    }
    action = action_for(qa["next_team"])
    return {"qa": qa, "state": ground, "action": action}


def evaluate_turn(predicted: dict[str, Any], text: str, turn_index: int) -> dict[str, Any]:
    """Score one turn's reconstruction against the embedded answer key."""
    ground = ground_truth_answers(turn_index)
    qa = {
        "is_deployment_allowed": _yes_no(predicted["deployment_allowed"]),
        "blocker": predicted["blocker"],
        "next_team": next_team(predicted["blocker"]),
        "migration_approved": _yes_no(predicted["migration_approved"]),
        "what_changed": any(_norm(marker) in _norm(text) for marker in CHANGE_MARKERS[turn_index]),
    }
    qa_correct = sum(1 for key in ground["qa"] if qa[key] == ground["qa"][key])
    state_correct = sum(1 for field in _STATE_FIELDS if predicted[field] == ground["state"][field])
    action_correct = int(action_for(qa["next_team"]) == ground["action"])
    return {
        "qa_correct": qa_correct,
        "qa_total": len(ground["qa"]),
        "state_correct": state_correct,
        "state_total": len(_STATE_FIELDS),
        "action_correct": action_correct,
    }


def evaluate_reconstruction(turn_texts: list[str]) -> dict[str, Any]:
    """Aggregate task-performance metrics for one variant.

    ``turn_texts`` holds six texts (index 0 = the shared context; indices
    1..5 = the reconstruction after each update).  Constraint compliance is
    scored on the final reconstruction.  Empty or short inputs score the
    turns that exist (and 0.0 when none exist) rather than raising, so the
    function stays safe for direct unit use.
    """
    per_turn = [evaluate_turn(read_state(turn_texts[index]), turn_texts[index], index) for index in range(1, min(6, len(turn_texts)))]
    if not per_turn:
        return {
            "qa_accuracy": 0.0,
            "state_accuracy": 0.0,
            "constraint_compliance": 0.0,
            "action_accuracy": 0.0,
            "task_success": 0.0,
        }
    qa_accuracy = statistics.mean(item["qa_correct"] / item["qa_total"] for item in per_turn)
    state_accuracy = statistics.mean(item["state_correct"] / item["state_total"] for item in per_turn)
    action_accuracy = statistics.mean(item["action_correct"] for item in per_turn)
    final_text = _norm(turn_texts[min(5, len(turn_texts) - 1)])
    c1 = "production deployment" in final_text and "integration test" in final_text and bool(_PASS_WORD_RE.search(final_text))
    c2 = "migration" in final_text and "review" in final_text and "platform team" in final_text
    constraint_compliance = (float(c1) + float(c2)) / 2.0
    return {
        "qa_accuracy": qa_accuracy,
        "state_accuracy": state_accuracy,
        "constraint_compliance": constraint_compliance,
        "action_accuracy": action_accuracy,
        "task_success": statistics.mean([qa_accuracy, state_accuracy, constraint_compliance, action_accuracy]),
    }


# ---------------------------------------------------------------------------
# Plain variants (1-8)
# ---------------------------------------------------------------------------


def _messages() -> list[str]:
    return [SHARED_CONTEXT, *UPDATES]


def _state_delta_ops() -> list[list[dict[str, Any]]]:
    from aifence.bus.state import diff  # lazy: aifence.bus must not import at module level

    return [diff(STATE_DICTS[index], STATE_DICTS[index + 1]) for index in range(5)]


def _canonical_bytes(value: Any) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def _run_plain_variant(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Run a plain (non-AIFENCE) variant; returns per-exchange turn records."""
    turns: list[dict[str, Any]] = []
    for turn in range(6):
        started = time.perf_counter()
        representation = spec["repr_fn"](turn)
        wire_json = json.dumps(representation, separators=(",", ":"), ensure_ascii=False)
        wire_msgpack = msgpack.packb(representation)
        encode_ms = _ms_since(started)
        started = time.perf_counter()
        reconstruction = spec["recon_fn"](representation, turn)
        decode_ms = _ms_since(started)
        turns.append(
            {
                "turn": turn,
                "phase": "shared" if turn == 0 else "update",
                "wire_bytes_json": len(wire_json.encode("utf-8")),
                "wire_bytes_msgpack": len(wire_msgpack),
                "stored_bytes": spec["stored_fn"](turn),
                "model_input_tokens": _estimate_tokens(wire_json),
                "model_output_tokens": _estimate_tokens(reconstruction),
                "reference_fetch_bytes": 0,
                "reference_fetch_count": 0,
                "encode_latency_ms": encode_ms,
                "decode_latency_ms": decode_ms,
                "reconstruction": reconstruction,
                "note": "",
            }
        )
    return turns


def _plain_specs() -> list[dict[str, Any]]:
    messages = _messages()
    delta_ops = _state_delta_ops()

    def latest_repr(turn: int) -> list[str]:
        return [messages[turn]]

    def history_repr(turn: int) -> list[str]:
        return messages[: turn + 1]

    def json_recon(representation: Any, turn: int) -> str:
        return json.dumps(representation, separators=(",", ":"), ensure_ascii=False)

    def sentence_pool(turn: int) -> list[str]:
        out: list[str] = []
        for message in messages[: turn + 1]:
            out.extend(part.strip() for part in _SENTENCE_RE.split(message) if part.strip())
        return out

    def summary_repr(turn: int) -> list[str]:
        return extractive_summary(sentence_pool(turn))

    def retrieval_repr(turn: int) -> list[str]:
        return retrieval_select(messages[: turn + 1])

    def delta_repr(turn: int) -> dict[str, Any]:
        if turn == 0:
            return {"base": STATE_DICTS[0], "ops": []}
        return {"ops": [delta_ops[turn - 1]]}

    def delta_recon(representation: dict[str, Any], turn: int) -> str:
        parts = [render_state_text(STATE_DICTS[0])]
        for index in range(turn):
            parts.append(render_state_text(STATE_DICTS[index + 1]))
            parts.append(f"ops={json.dumps(delta_ops[index], separators=(',', ':'))}")
        return " ".join(parts)

    def zero_stored(turn: int) -> int:
        return 0

    def state_stored(turn: int) -> int:
        return _canonical_bytes(STATE_DICTS[turn])

    specs = [
        {
            "id": "v01",
            "name": "1. full natural-language context every turn",
            "repr_fn": history_repr,
            "recon_fn": lambda representation, turn: "\n".join(representation),
            "stored_fn": zero_stored,
        },
        {
            "id": "v02",
            "name": "2. latest-only message",
            "repr_fn": latest_repr,
            "recon_fn": lambda representation, turn: representation[0],
            "stored_fn": zero_stored,
        },
        {
            "id": "v03",
            "name": "3. minified JSON",
            "repr_fn": history_repr,
            "recon_fn": json_recon,
            "stored_fn": zero_stored,
        },
        {
            "id": "v04",
            "name": "4. MesaifencePack",
            "repr_fn": history_repr,
            "recon_fn": json_recon,
            "stored_fn": zero_stored,
        },
        {
            "id": "v05",
            "name": "5. conventional state snapshots",
            "repr_fn": lambda turn: STATE_DICTS[turn],
            "recon_fn": lambda representation, turn: render_state_text(representation),
            "stored_fn": state_stored,
        },
        {
            "id": "v06",
            "name": "6. conventional state deltas",
            "repr_fn": delta_repr,
            "recon_fn": delta_recon,
            "stored_fn": state_stored,
        },
        {
            "id": "v07",
            "name": "7. LLM summaries (deterministic extractive stub)",
            "repr_fn": summary_repr,
            "recon_fn": lambda representation, turn: " ".join(representation),
            "stored_fn": zero_stored,
        },
        {
            "id": "v08",
            "name": "8. retrieval of relevant prior messages",
            "repr_fn": retrieval_repr,
            "recon_fn": lambda representation, turn: " ".join(representation),
            "stored_fn": zero_stored,
        },
    ]
    return [{**spec, "plain": True} for spec in specs]


# ---------------------------------------------------------------------------
# AIFENCE variants (9-12)
# ---------------------------------------------------------------------------


def _pin_packet_id(codec: Any, variant_id: str, turn: Any) -> None:
    key = f"{variant_id}:{turn}"
    codec._packet_id = (lambda n=key: "P" + hashlib.sha256(n.encode()).hexdigest()[:32])  # type: ignore[method-assign]


def _reset_schema(db_module: Any) -> None:
    from sqlalchemy.orm import close_all_sessions

    close_all_sessions()
    db_module.Base.metadata.drop_all(db_module.engine)
    db_module.Base.metadata.create_all(db_module.engine)


def _aifence_request(
    content: Any,
    *,
    use_receiver_knowledge: bool = False,
    auto_learn: bool = False,
    record_learning: bool = False,
    use_patterns: bool = True,
    base_state: str | None = None,
    inline_limit: int | None = None,
) -> Any:
    from aifence.bus.schemas import EncodeRequest, Provenance

    return EncodeRequest(
        content=content,
        sender="alice",
        receiver="bob",
        provenance=Provenance(observed_at=FIXED_TIMESTAMP, producer="alice"),
        use_cache=False,
        use_receiver_knowledge=use_receiver_knowledge,
        record_learning=record_learning,
        auto_learn=auto_learn,
        use_patterns=use_patterns,
        base_state=base_state,
        inline_limit=inline_limit,
    )


def _render_decoded(decoded: Any, *, state_form: bool) -> str:
    """Render a AIFENCE decode result as reader-facing text.

    ``state_form`` renders dict-style concepts verbatim as
    ``canonical: literal`` (read by ``read_state``'s rendered parser);
    otherwise canonicals are normalized (underscores to spaces) so the
    natural-language parser can read them.
    """
    parts: list[str] = []
    for concept in decoded.concepts:
        canonical = concept.get("canonical") or ""
        literal = concept.get("literal")
        # A pattern atom decodes to the pattern's concept whose canonical is
        # only the pattern id; the receiver expands it via the pattern
        # definition carried by the packet, so render that definition.
        pattern_info = concept.get("pattern") or {}
        pattern_canonical = pattern_info.get("canonical") or ""
        if pattern_canonical:
            canonical = pattern_canonical
        if state_form:
            if canonical:
                parts.append(f"{canonical}: {literal}" if literal is not None else canonical)
            elif literal is not None:
                parts.append(str(literal))
        else:
            text = canonical.replace("_", " ")
            if literal is not None:
                parts.append(f"{text} {literal}" if text else str(literal))
            elif text:
                parts.append(text)
    for literal in decoded.literals:
        parts.append(str(literal.get("literal") or ""))
    return " ".join(part for part in parts if part)


def _aifence_report_aggregate(reports: list[Any]) -> dict[str, Any]:
    from collections import Counter

    merged = {
        "exchanges": 0,
        "wire_bytes_json": 0,
        "wire_bytes_msgpack": 0,
        "stored_bytes": 0,
        "model_tokens": 0,
        "codebook_setup_bytes": 0,
        "codebook_setup_tokens": 0,
        "codebook_definitions": 0,
        "pattern_setup_bytes": 0,
        "pattern_setup_tokens": 0,
        "pattern_definitions": 0,
        "decoding_bytes": 0,
        "decoding_tokens": 0,
        "reference_fetch_bytes": 0,
        "reference_fetch_count": 0,
        "fallback_bytes": 0,
        "fallback_tokens": 0,
        "fallback_count": 0,
        "strategies": Counter(),
    }
    for report in reports:
        for field in (
            "exchanges", "wire_bytes_json", "wire_bytes_msgpack", "stored_bytes", "model_tokens",
            "codebook_setup_bytes", "codebook_setup_tokens", "codebook_definitions",
            "pattern_setup_bytes", "pattern_setup_tokens", "pattern_definitions",
            "decoding_bytes", "decoding_tokens", "reference_fetch_bytes",
            "reference_fetch_count", "fallback_bytes", "fallback_tokens", "fallback_count",
        ):
            merged[field] += int(getattr(report, field, 0) or 0)
        if getattr(report, "strategy", None):
            merged["strategies"][str(report.strategy)] += 1
    return merged


def _run_aifence_variant(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Run a real-AifenceCodec variant against an isolated, per-run database."""
    from sqlalchemy import select

    from aifence.bus import db as db_module
    from aifence.bus.codec import AifenceCodec
    from aifence.bus.config import Settings
    from aifence.bus.db import SessionLocal
    from aifence.bus.db_models import LearnedPattern

    db_module.init_db()
    _reset_schema(db_module)
    settings = Settings(
        auth_required=False,
        database_url=os.environ.get("AIFENCE_BUS_DATABASE_URL", "sqlite://"),
        context_accounting_enabled=True,
        learning_mode="managed",
        **spec.get("settings", {}),
    )
    turns: list[dict[str, Any]] = []
    reconstruction = ""
    with SessionLocal() as db:
        codec = AifenceCodec(db, settings)
        for canonical in spec["codebook"]:
            codec.codebook.register("global", canonical)
        db.commit()

        warmup = spec.get("warmup")
        if warmup is not None:
            _pin_packet_id(codec, spec["id"], "warmup")
            encode_started = time.perf_counter()
            encoded = codec.encode(_aifence_request(warmup, auto_learn=True, record_learning=True))
            encode_ms = _ms_since(encode_started)
            encode_report = codec.context_report()
            turns.append(
                {
                    "turn": -1,
                    "phase": "pattern_warmup",
                    "wire_bytes_json": encode_report.wire_bytes_json,
                    "wire_bytes_msgpack": encode_report.wire_bytes_msgpack,
                    "stored_bytes": encode_report.stored_bytes,
                    "model_input_tokens": encode_report.model_tokens,
                    "model_output_tokens": 0,
                    "reference_fetch_bytes": 0,
                    "reference_fetch_count": 0,
                    "encode_latency_ms": encode_ms,
                    "decode_latency_ms": 0,
                    "reconstruction": "",
                    "note": "pattern learning warm-up exchange",
                    "aifence": _aifence_report_aggregate([encode_report]),
                }
            )
            pattern = db.scalar(select(LearnedPattern))
            if pattern is not None:
                codec.patterns.set_status(pattern.pattern_id, "active")
                db.commit()

        base_id: str | None = None
        for turn in range(6):
            _pin_packet_id(codec, spec["id"], turn)
            content = spec["content_fn"](turn)
            base_state = base_id if (turn > 0 and spec.get("chain_states")) else None
            inline_limit = spec.get("inline_limit") if turn == 0 else None
            request = _aifence_request(
                content,
                use_receiver_knowledge=spec.get("ack", False),
                use_patterns=spec.get("patterns", True),
                base_state=base_state,
                inline_limit=inline_limit,
            )
            encode_started = time.perf_counter()
            encoded = codec.encode(request)
            encode_ms = _ms_since(encode_started)
            encode_report = codec.context_report()
            decode_started = time.perf_counter()
            decoded = codec.decode(
                encoded.packet,
                resolve_refs=spec.get("resolve_refs", False),
                receiver="bob",
                acknowledge=spec.get("ack", False),
            )
            decode_ms = _ms_since(decode_started)
            decode_report = codec.context_report()
            piece = spec["render_fn"](decoded)
            reconstruction = f"{reconstruction} {piece}".strip()
            if spec.get("chain_states") and encoded.packet.meta.get("state"):
                base_id = str(encoded.packet.meta["state"])
            turns.append(
                {
                    "turn": turn,
                    "phase": "shared" if turn == 0 else "update",
                    "wire_bytes_json": encode_report.wire_bytes_json,
                    "wire_bytes_msgpack": encode_report.wire_bytes_msgpack,
                    "stored_bytes": encode_report.stored_bytes,
                    "model_input_tokens": encode_report.model_tokens,
                    "model_output_tokens": _estimate_tokens(reconstruction),
                    "reference_fetch_bytes": decode_report.reference_fetch_bytes,
                    "reference_fetch_count": decode_report.reference_fetch_count,
                    "encode_latency_ms": encode_ms,
                    "decode_latency_ms": decode_ms,
                    "reconstruction": reconstruction,
                    "note": f"aifence strategy: {encoded.strategy}",
                    "aifence": _aifence_report_aggregate([encode_report, decode_report]),
                }
            )
    return turns


def _render_state_aifence_piece(decoded: Any) -> str:
    parts: list[str] = []
    for reference in decoded.references:
        if reference.get("value") is not None:
            parts.append(render_state_text(reference["value"]))
    if decoded.resolved_state is not None:
        parts.append(render_state_text(decoded.resolved_state))
    return " ".join(parts)


def _aifence_specs() -> list[dict[str, Any]]:
    from aifence.bus.compiler import compile_content

    shared_clauses = [unit.canonical for unit in compile_content(SHARED_CONTEXT)]
    update_clauses: list[str] = []
    for update in UPDATES:
        update_clauses.extend(unit.canonical for unit in compile_content(update))
    clause_canonicals = sorted(set(shared_clauses + update_clauses))
    state_keys = sorted(STATE_DICTS[0])

    def text_content(turn: int) -> str:
        return SHARED_CONTEXT if turn == 0 else UPDATES[turn - 1]

    def state_content(turn: int) -> dict[str, Any]:
        return STATE_DICTS[turn]

    def decode_text(decoded: Any) -> str:
        return _render_decoded(decoded, state_form=False)

    def decode_state(decoded: Any) -> str:
        return _render_decoded(decoded, state_form=True)

    return [
        {
            "id": "v09",
            "name": "9. AIFENCE codebooks only",
            "codebook": clause_canonicals,
            "content_fn": text_content,
            "render_fn": decode_text,
            "patterns": False,
            "ack": False,
        },
        {
            "id": "v10",
            "name": "10. AIFENCE codebooks + learned patterns",
            "codebook": clause_canonicals,
            "content_fn": text_content,
            "render_fn": decode_text,
            "patterns": True,
            "ack": False,
            "warmup": SHARED_CONTEXT,
            "settings": {
                "pattern_candidate_min_count": 1,
                "pattern_trust_required": False,
                "pattern_max_observations_per_message": 1,
                "pattern_recursive_learning_enabled": False,
            },
        },
        {
            "id": "v11",
            "name": "11. AIFENCE references + state deltas",
            "codebook": [],
            "content_fn": state_content,
            "render_fn": _render_state_aifence_piece,
            "patterns": True,
            "ack": False,
            "resolve_refs": True,
            "chain_states": True,
            "inline_limit": 1,
        },
        {
            "id": "v12",
            "name": "12. full AIFENCE with ACKed receiver knowledge",
            "codebook": state_keys,
            "content_fn": state_content,
            "render_fn": decode_state,
            "patterns": True,
            "ack": True,
        },
    ]


# ---------------------------------------------------------------------------
# Aggregation, tables, artifacts
# ---------------------------------------------------------------------------


def _merge_aifence_aggregates(aggregates: list[dict[str, Any]]) -> dict[str, Any]:
    from collections import Counter

    merged: dict[str, Any] = {
        "exchanges": 0,
        "wire_bytes_json": 0,
        "wire_bytes_msgpack": 0,
        "stored_bytes": 0,
        "model_tokens": 0,
        "codebook_setup_bytes": 0,
        "codebook_setup_tokens": 0,
        "codebook_definitions": 0,
        "pattern_setup_bytes": 0,
        "pattern_setup_tokens": 0,
        "pattern_definitions": 0,
        "decoding_bytes": 0,
        "decoding_tokens": 0,
        "reference_fetch_bytes": 0,
        "reference_fetch_count": 0,
        "fallback_bytes": 0,
        "fallback_tokens": 0,
        "fallback_count": 0,
        "strategies": Counter(),
    }
    for aggregate in aggregates:
        for field in (
            "exchanges", "wire_bytes_json", "wire_bytes_msgpack", "stored_bytes", "model_tokens",
            "codebook_setup_bytes", "codebook_setup_tokens", "codebook_definitions",
            "pattern_setup_bytes", "pattern_setup_tokens", "pattern_definitions",
            "decoding_bytes", "decoding_tokens", "reference_fetch_bytes",
            "reference_fetch_count", "fallback_bytes", "fallback_tokens", "fallback_count",
        ):
            merged[field] += int(aggregate.get(field, 0) or 0)
        merged["strategies"].update(aggregate.get("strategies") or {})
    return merged


def _turn_cost(turn: dict[str, Any]) -> float:
    return (
        turn["wire_bytes_json"] * WIRE_COST_PER_BYTE_USD
        + turn["model_output_tokens"] * TOKEN_COST_PER_TOKEN_USD
        + turn["reference_fetch_bytes"] * REF_BYTE_COST_PER_BYTE_USD
    )


def _aggregate(turns: list[dict[str, Any]], aifence: dict[str, Any] | None) -> dict[str, Any]:
    total = {
        "exchanges": len(turns),
        "wire_bytes_json": sum(turn["wire_bytes_json"] for turn in turns),
        "wire_bytes_msgpack": sum(turn["wire_bytes_msgpack"] for turn in turns),
        "stored_bytes": sum(turn["stored_bytes"] for turn in turns),
        "model_input_tokens": sum(turn["model_input_tokens"] for turn in turns),
        "model_output_tokens": sum(turn["model_output_tokens"] for turn in turns),
        "reference_fetch_bytes": sum(turn["reference_fetch_bytes"] for turn in turns),
        "reference_fetch_count": sum(turn["reference_fetch_count"] for turn in turns),
        "cost_usd": sum(_turn_cost(turn) for turn in turns),
        "encode_latency_ms_mean": statistics.mean(turn["encode_latency_ms"] for turn in turns),
        "decode_latency_ms_mean": statistics.mean(turn["decode_latency_ms"] for turn in turns),
    }
    if aifence is not None:
        total["aifence"] = aifence
    return total


def _scenario_sha256() -> str:
    raw = json.dumps(
        {"shared": SHARED_CONTEXT, "updates": UPDATES, "state_dicts": STATE_DICTS},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def provider_available() -> bool:
    return bool(os.environ.get(PROVIDER_ENV, "").strip())


def variant_status(spec: dict[str, Any]) -> str:
    """'skipped' when the variant needs a provider and none is configured."""
    if spec.get("requires_provider", False) and not provider_available():
        return "skipped"
    return "ok"


def run_benchmark(out_dir: str | Path | None = None) -> dict[str, Any]:
    """Run all twelve variants and return the full results structure.

    When ``out_dir`` is given, writes ``compression_benchmark.json`` and
    ``compression_benchmark.csv`` into it.  Deterministic apart from the
    measured ``*_latency_ms`` fields.  No provider is required.
    """
    variant_rows: list[dict[str, Any]] = []
    baseline_wire: int | None = None
    baseline_output_tokens: int | None = None

    for spec in [*_plain_specs(), *_aifence_specs()]:
        variant_id: str = spec["id"]
        if variant_status(spec) == "skipped":
            variant_rows.append(
                {
                    "variant_id": variant_id,
                    "name": spec["name"],
                    "status": "skipped",
                    "note": NO_PROVIDER_NOTE,
                    "turns": [],
                    "efficiency": None,
                    "task_performance": None,
                    "semantic_fidelity": None,
                    "amortization": None,
                }
            )
            continue
        turns = _run_plain_variant(spec) if spec.get("plain", False) else _run_aifence_variant(spec)
        turn_texts = [turn["reconstruction"] for turn in turns if turn["turn"] >= 0]
        final_text = turn_texts[-1] if turn_texts else ""
        task_performance = evaluate_reconstruction(turn_texts)
        fidelity = fidelity_scores(turn_texts[1:], final_text)
        aifence_bus_aggregate = _merge_aifence_aggregates([turn["aifence"] for turn in turns if turn.get("aifence")]) if not spec.get("plain", False) else None
        efficiency = _aggregate(turns, aifence_bus_aggregate)
        if baseline_wire is None:
            baseline_wire = efficiency["wire_bytes_json"]
            baseline_output_tokens = efficiency["model_output_tokens"]
        saving_per_use_bytes = (baseline_wire - efficiency["wire_bytes_json"]) / 6.0
        saving_per_use_tokens = (baseline_output_tokens - efficiency["model_output_tokens"]) / 6.0
        aifence = efficiency.get("aifence")
        setup_bytes = (aifence["codebook_setup_bytes"] + aifence["pattern_setup_bytes"]) if aifence else 0
        setup_tokens = (aifence["codebook_setup_tokens"] + aifence["pattern_setup_tokens"]) if aifence else 0
        amortization = {
            "setup_cost_bytes": setup_bytes,
            "setup_cost_tokens": setup_tokens,
            "saving_per_use_bytes": saving_per_use_bytes,
            "saving_per_use_tokens": saving_per_use_tokens,
            "break_even_uses": break_even(setup_bytes, saving_per_use_bytes),
        }
        variant_rows.append(
            {
                "variant_id": variant_id,
                "name": spec["name"],
                "status": "ok",
                "note": "",
                "turns": turns,
                "efficiency": efficiency,
                "task_performance": task_performance,
                "semantic_fidelity": fidelity,
                "amortization": amortization,
            }
        )

    results: dict[str, Any] = {
        "schema": "aifence.compression_benchmark.v1",
        "generated_at": FIXED_TIMESTAMP,
        "scenario": {
            "name": "phoenix_rfc",
            "sha256": _scenario_sha256(),
            "shared_context": SHARED_CONTEXT,
            "updates": UPDATES,
            "state_dicts": STATE_DICTS,
            "change_markers": CHANGE_MARKERS,
        },
        "provider": {
            "configured": provider_available(),
            "env": PROVIDER_ENV,
            "note": "no provider is required; all twelve variants run deterministically",
        },
        "variants": variant_rows,
        "tables": _build_tables(variant_rows),
    }
    if out_dir is not None:
        _write_artifacts(Path(out_dir), results)
    return results


def _build_tables(variant_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    efficiency: list[dict[str, Any]] = []
    task_performance: list[dict[str, Any]] = []
    semantic_fidelity: list[dict[str, Any]] = []
    amortization: list[dict[str, Any]] = []
    for row in variant_rows:
        variant_id, name = row["variant_id"], row["name"]
        if row["status"] == "skipped":
            efficiency.append({"variant": f"{variant_id} {name}", "status": "skipped", "note": NO_PROVIDER_NOTE})
            task_performance.append({"variant": f"{variant_id} {name}", "status": "skipped", "note": NO_PROVIDER_NOTE})
            semantic_fidelity.append({"variant": f"{variant_id} {name}", "status": "skipped", "note": NO_PROVIDER_NOTE})
            amortization.append({"variant": f"{variant_id} {name}", "status": "skipped", "note": NO_PROVIDER_NOTE})
            continue
        eff = row["efficiency"]
        efficiency.append(
            {
                "variant": f"{variant_id} {name}",
                "wire_bytes_json": eff["wire_bytes_json"],
                "wire_bytes_msgpack": eff["wire_bytes_msgpack"],
                "stored_bytes": eff["stored_bytes"],
                "model_input_tokens": eff["model_input_tokens"],
                "model_output_tokens": eff["model_output_tokens"],
                "reference_fetch_bytes": eff["reference_fetch_bytes"],
                "reference_fetch_count": eff["reference_fetch_count"],
                "cost_usd": round(eff["cost_usd"], 6),
            }
        )
        perf = row["task_performance"]
        task_performance.append(
            {
                "variant": f"{variant_id} {name}",
                "qa_accuracy": round(perf["qa_accuracy"], 3),
                "state_accuracy": round(perf["state_accuracy"], 3),
                "constraint_compliance": round(perf["constraint_compliance"], 3),
                "action_accuracy": round(perf["action_accuracy"], 3),
                "task_success": round(perf["task_success"], 3),
            }
        )
        fid = row["semantic_fidelity"]
        semantic_fidelity.append(
            {
                "variant": f"{variant_id} {name}",
                "negation": round(fid["negation"], 3),
                "numeric": round(fid["numeric"], 3),
                "ownership": round(fid["ownership"], 3),
                "temporal_ordering": round(fid["temporal_ordering"], 3),
                "changed_value": round(fid["changed_value"], 3),
                "contradiction": round(fid["contradiction"], 3),
                "critical_fact_recall": round(fid["critical_fact_recall"], 3),
            }
        )
        am = row["amortization"]
        amortization.append(
            {
                "variant": f"{variant_id} {name}",
                "setup_cost_bytes": am["setup_cost_bytes"],
                "setup_cost_tokens": am["setup_cost_tokens"],
                "saving_per_use_bytes": round(am["saving_per_use_bytes"], 1),
                "saving_per_use_tokens": round(am["saving_per_use_tokens"], 1),
                "break_even_uses": am["break_even_uses"],
            }
        )
    return {
        "efficiency": efficiency,
        "task_performance": task_performance,
        "semantic_fidelity": semantic_fidelity,
        "amortization": amortization,
    }


def _write_artifacts(out_dir: Path, results: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "compression_benchmark.json").write_text(
        json.dumps(results, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    )
    csv_path = out_dir / "compression_benchmark.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["table", "variant_id", "metric", "value"])
        for table_name, rows in results["tables"].items():
            for row in rows:
                for key, value in row.items():
                    if key == "variant" or "latency" in key:
                        continue
                    writer.writerow([table_name, row["variant"], key, value])


def _fmt_table(title: str, headers: list[str], rows: list[list[Any]]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(str(cell)))
    line = "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)).rstrip()
    rule = "-" * len(line)
    out = [title, rule, line, rule]
    for row in rows:
        cells = [str(cell).ljust(widths[index]) for index, cell in enumerate(row)]
        out.append("  ".join(cells).rstrip())
    out.append(rule)
    return "\n".join(out)


def format_tables(results: dict[str, Any]) -> str:
    """Render the four ASCII summary tables."""
    sections: list[str] = []

    eff_headers = ["variant", "wire_json", "wire_msgpack", "stored", "in_tok", "out_tok", "ref_bytes", "ref_cnt", "cost_usd"]
    eff_rows: list[list[Any]] = []
    for row in results["tables"]["efficiency"]:
        if row.get("status") == "skipped":
            eff_rows.append([row["variant"], "-", "-", "-", "-", "-", "-", "-", "-", "-"])
            continue
        eff_rows.append(
            [
                row["variant"],
                row["wire_bytes_json"],
                row["wire_bytes_msgpack"],
                row["stored_bytes"],
                row["model_input_tokens"],
                row["model_output_tokens"],
                row["reference_fetch_bytes"],
                row["reference_fetch_count"],
                row["cost_usd"],
            ]
        )
    sections.append(_fmt_table("Efficiency (cumulative over the conversation)", eff_headers, eff_rows))

    perf_headers = ["variant", "qa_acc", "state_acc", "constraint", "action", "task_success"]
    perf_rows: list[list[Any]] = []
    for row in results["tables"]["task_performance"]:
        if row.get("status") == "skipped":
            perf_rows.append([row["variant"], "-", "-", "-", "-", "-"])
            continue
        perf_rows.append(
            [row["variant"], row["qa_accuracy"], row["state_accuracy"], row["constraint_compliance"], row["action_accuracy"], row["task_success"]]
        )
    sections.append(_fmt_table("Task performance (0..1; higher is better)", perf_headers, perf_rows))

    fid_headers = ["variant", "negation", "numeric", "ownership", "ordering", "changed", "contradiction", "critical"]
    fid_rows: list[list[Any]] = []
    for row in results["tables"]["semantic_fidelity"]:
        if row.get("status") == "skipped":
            fid_rows.append([row["variant"], "-", "-", "-", "-", "-", "-", "-"])
            continue
        fid_rows.append(
            [
                row["variant"],
                row["negation"],
                row["numeric"],
                row["ownership"],
                row["temporal_ordering"],
                row["changed_value"],
                row["contradiction"],
                row["critical_fact_recall"],
            ]
        )
    sections.append(_fmt_table("Semantic fidelity (0..1 per fact type)", fid_headers, fid_rows))

    am_headers = ["variant", "setup_bytes", "setup_tokens", "save_bytes/use", "save_tokens/use", "break_even"]
    am_rows: list[list[Any]] = []
    for row in results["tables"]["amortization"]:
        if row.get("status") == "skipped":
            am_rows.append([row["variant"], "-", "-", "-", "-", "-"])
            continue
        am_rows.append(
            [
                row["variant"],
                row["setup_cost_bytes"],
                row["setup_cost_tokens"],
                row["saving_per_use_bytes"],
                row["saving_per_use_tokens"],
                row["break_even_uses"],
            ]
        )
    sections.append(_fmt_table("Amortization vs full-context baseline (6 conversation turns)", am_headers, am_rows))

    skipped = [row for row in results["variants"] if row["status"] == "skipped"]
    if skipped:
        notes = [f"{row['variant_id']} {row['name']}: {row['note']}" for row in skipped]
        sections.append("Skipped variants:\n" + "\n".join(f"  - {note}" for note in notes))
    return "\n\n".join(sections)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic multi-turn semantic-context compression benchmark (issue #16, stage 2)."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="directory for compression_benchmark.json/.csv artifacts (default: stdout only)",
    )
    args = parser.parse_args(argv)

    # Bind an isolated scratch database BEFORE any aifence.bus import (db.py
    # creates the engine at import time).  The file lives outside the
    # worktree and is removed on exit.
    if args.out is not None:
        scratch_db = args.out / "aifence_bus_bench.db"
    else:
        scratch_db = Path.home() / ".aifence-bench" / "compression_benchmark.db"
    scratch_db.parent.mkdir(parents=True, exist_ok=True)
    os.environ["AIFENCE_BUS_DATABASE_URL"] = f"sqlite:///{scratch_db}"
    try:
        results = run_benchmark(out_dir=args.out)
        print(format_tables(results))
        if args.out is not None:
            print(f"\nArtifacts written to {args.out}")
        return 0
    finally:
        try:
            scratch_db.unlink(missing_ok=True)
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
