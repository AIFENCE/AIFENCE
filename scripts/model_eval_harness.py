"""Opt-in model evaluation harness (issue #16, stage 3).

This script runs the stage-2 compression benchmark's receivers on real model
runtimes through external adapter commands, measuring COLD and WARM receivers
separately.  It is opt-in: with no ``--adapters`` config (or when
``SAGE_BENCH_LLM_PROVIDER`` is unset) it prints ``not run, no provider`` and
exits 0 -- provider numbers are never fabricated (mirroring
``scripts/compression_benchmark.py`` and ``scripts/model_matrix_benchmark.py``).

Design
------
A NEW script that REUSES the stage-2 benchmark
(``scripts/compression_benchmark.py``) instead of mutating it.  The stage-2
benchmark stays byte-deterministic and its determinism tests pass unchanged;
the harness loads it as a module (same importlib pattern the tests use) and
consumes its deterministic per-variant per-turn records (wire bytes,
reconstructions), its scenario fixture (``SHARED_CONTEXT``/``UPDATES``/
``STATE_DICTS``/``CHANGE_MARKERS``), its ground-truth answer key
(``ground_truth_answers``) and its deterministic token estimator.  The
harness itself never calls a model and never fabricates results: every
``task_success``/token/cost figure comes from the adapter's JSON reply.

Adapter convention (mirrors ``scripts/model_matrix_benchmark.py``)
-----------------------------------------------------------------
An adapters JSON config maps ``model_identity -> spec``::

    {
      "acme-gpt-4o": {
        "family": "acme",
        "version": "gpt-4o-2026-05",
        "codebook_version": "global:1",      # optional, default "global:1"
        "command": ["python", "-c", "..."]   # argv; JSON on stdin, JSON on stdout
      },
      "nebula-sonnet": {
        "family": "nebula",
        "version": "sonnet-2026-07",
        "command": [...]
      }
    }

The harness invokes each ``command`` with a compact-JSON payload on stdin
(``separators=(",", ":")``, exactly like ``_invoke`` in
``model_matrix_benchmark.py``) and expects JSON on stdout.  Required reply
fields (model_matrix's full contract is the floor): ``task_success``,
``input_tokens``, ``output_tokens``, ``provider_cost_usd``.  Optional:
``infrastructure_cost_usd``, ``retrieval_cost_usd``, ``retry_cost_usd``,
``cost_usd`` (else the sum of the cost components), ``latency_ms``,
``retrievals``, ``tool_calls``, ``retries``, ``semantic_loss``,
``reconstruction`` (text the receiver produced; used by the harness-side
critical-fact-recall scoring) and ``critical_fact_recall`` (adapter-reported;
preferred over the harness-side score).

Payload contract (per exchange): ``protocol: "sage/0.2"``,
``benchmark: "compression_benchmark:phoenix_rfc"``, ``variant`` /
``variant_name``, ``turn`` / ``phase``, ``receiver_state`` (``"cold"`` =
fresh receiver with no prior state; ``"warm"`` = receiver prior established
from the shared-context phase, e.g. codebook/patterns ACKed), ``receiver_prior``
(ACKed shared context for warm, ``null`` for cold), ``decoder_configuration``
(one of the RFC's three modes), ``symbolic_examples`` (whether the model saw
symbolic-format examples; when true an ``examples`` list with a sample packet
+ its meaning is included), ``representation`` (the symbolic wire form:
the stage-2 reconstruction for plain variants, a deterministic symbolic
packet rendering for SAGE variants), ``wire_bytes``, ``model_facing_text``
(the text the model is asked to consume), ``content`` (the message/state the
sender conveyed), ``expected`` (the per-turn ground-truth answer key) and
``change_markers``.

Sealed mode (issue #22, stage 1 -- ``--sealed``, default OFF)
-------------------------------------------------------------
With ``--sealed`` the adapter boundary is SPLIT: the payload carries ONLY the
identity fields (``protocol``, ``benchmark``, ``variant``, ``variant_name``,
``turn``, ``phase``, ``receiver_state``, ``decoder_configuration``,
``wire_bytes``, ``symbolic_examples`` -- always ``false`` in sealed mode) plus
``task`` (a deterministic per-variant instruction: the state variants
v05/v06/v11/v12 ask for the current state --
``deployment_allowed``/``failed_tests``/``migration_approved``/``blocker`` --
plus what changed; the text variants ask for a summary of the latest update
plus what changed), ``model_facing_packet`` and ``allowed_decoder_metadata``
(``codebook_version`` from the adapter config or ``global:1``,
``receiver_state``, ``decoder_configuration``).  NEVER sent: ``content``,
``expected``, ``change_markers``, ``receiver_prior``, ``examples`` or any raw
source text -- the model runner cannot see evaluator-only knowledge.  The
adapter replies with a ``task_response`` text plus tokens/cost;
``task_success`` and ``critical_fact_recall`` are scored DETERMINISTICALLY by
the harness from that text (``cb.read_state`` + ``cb.evaluate_turn`` per-turn
ratios + ``cb.fidelity_critical``) -- adapter-reported scores are ignored in
sealed mode.  ``--sealed`` cannot be combined with ``--with-examples``
(example meanings are evaluator-side decoder knowledge).  Sealed artifacts
carry a top-level ``evaluation_boundary: "sealed"`` and per-row
``sealed: true`` + ``task_response``; default OFF keeps every artifact
byte-identical to the stage-3/4 shape.  In sealed mode the warm receiver
is established through the REAL SAGE lifecycle (issue #22, stage 4): for
each SAGE variant, before its warm exchanges, the shared-context turn
(``content_fn(0)`` -- ``SHARED_CONTEXT`` or the held-out
``ESTABLISHMENT_SHARED_CONTEXT``) is encoded with a pinned packet id and
DECODED with ``acknowledge=True`` (receiver "bob"), which COMMITS receiver
knowledge (known codes / known refs / current_state) into the knowledge
store -- verified before any warm turn is rendered -- and the warm
exchanges then encode with ``use_receiver_knowledge=True``, so the warm
rows' wire bytes ARE the primed lifecycle measurement.  On the CURRENT
fixture the primed warm wire bytes EQUAL the cold re-encode's (receiver
knowledge is decoder-side; the wire whitelist strips
``receiver_known_code_count``), so there is NO wire saving to claim here --
the honest claim is the primed lifecycle, not a wire delta, and the tests
assert that equality rather than hiding it.  Warm rows deliberately carry
no explicit ``primed`` row marker (the internal exchange flag is not
propagated to rows, keeping the sealed row shape additive by exactly
``mechanism_used``); sealed ``receiver_state: "warm"`` rows ARE these
lifecycle-primed re-encodes.  ``receiver_prior`` is never sent in sealed
mode (a leak field); the priming happens ONCE per variant before its warm
exchanges (fresh receiver state per variant/run: per-process scratch DB +
schema reset per variant).

Sealed mode, stage 2 (issue #22 section B mode 1 -- actual packet rendering):
for SAGE variants (v09-v12) in ``direct-symbolic`` mode the
``model_facing_packet`` is NO LONGER the stage-1 canonical-clause proxy: it
is a canonical compact-JSON rendering of the REAL codec packet for that
``(variant, turn)``, deterministically re-encoded through the codec exactly
like the stage-2 benchmark (``_render_sage_variant_packets`` mirrors
``cb._run_sage_variant``: schema reset, spec ``Settings``, codebook
registration from ``spec["codebook"]`` in order, pinned packet ids, the v10
pattern warm-up, per-turn encode+decode).  The re-encoded wire bytes equal
the benchmark's recorded ``wire_bytes`` for the same ``(variant, turn)``
(honesty gate), and the rendering round-trips: parsed back with
``Packet.model_validate`` and decoded by the real codec it yields the
benchmark's recorded reconstruction.  The rendering carries the packet
fields (atom codes/cv + literals, refs, base, delta ops, prov, and meta
FILTERED to the wire whitelist {state, revision, budget_exceeded,
memory_tier} -- the exact subset the wire codec exports, so the rendering
equals the real wire packet + the bindings legend; evaluator-side meta
fields like the strategy/codebook fingerprint/receiver knowledge never
leave the evaluator) plus a ``bindings`` legend mapping each atom's
``code:cv`` to its canonical clause (learned-pattern atoms map to the
pattern's expanded canonical), so a model can answer from codes + bindings
while the FULL codebook/pattern store stays evaluator-side.  Non-sealed
mode and sealed non-direct-symbolic modes keep the stage-1
representation/reconstruction selection byte-identical.

Sealed direct-symbolic RECONSTRUCTION-FIDELITY scope (stage-2 hardening,
stage-4 warm update): in sealed direct-symbolic mode the CHAINED/REFERENCE
variants are a reconstruction-fidelity signal, not a self-contained task
payload.  v11's rendering is ``base`` (a ``sage:sha256:`` state hash) +
``delta`` ops only -- the base state content lives evaluator-side behind
the hash -- and v10 turn 0's single pattern atom covers 1 of 5 clauses, so
a COLD sealed receiver cannot resolve the base-state/reference content: a
perfect echo of the packet is structurally bounded (e.g. ~0.70/0.15
task_success on v11 turns 1-2).  This is the real SAGE cold-receiver
behavior -- NOT a rendering defect (the rendering is faithful to the codec
packet and round-trips) -- and sealed COLD v11 / v10-turn-0 scores must be
read as reconstruction-fidelity signals.  The stage-4 lifecycle-primed
WARM rows are the real primed measurement: the warm receiver ACKed the
establishment through the real lifecycle before the warm exchanges (see
the stage-4 section above), so warm base-state/reference resolution is
anchored exactly as the codec's own primed lifecycle provides it.

Held-out mode (issue #22, stage 3 -- unseen conversations, ``--held-out``,
default OFF)
--------------------------------------------------------------------------------
``--held-out`` (requires ``--sealed``; a clean exit-2 error otherwise)
evaluates the sealed harness against a HELD-OUT scenario
(``scripts/heldout_scenario.py``): the codebook/pattern establishment phase
material is FROZEN before the held-out updates are revealed.  Three phases:

* ESTABLISHMENT -- a NEW project ("Orion": distinct names/facts) is
  transmitted once as the shared context.  This is the ONLY material the
  SAGE variants' FROZEN codebook is compiled from
  (``heldout_scenario.establishment_canonicals`` -- the sorted canonical
  clauses of ``ESTABLISHMENT_SHARED_CONTEXT`` alone).  3 of the 5
  establishment canonicals differ from the default Phoenix scenario; the
  other two are shared ('12' -- the bare number split out of "Python
  3.12." -- and 'database_migrations_must_be_reviewed_by_the_platform_team',
  the generic migration-review sentence kept verbatim for the fidelity
  checker); the held-out UPDATE canonicals are fully disjoint from
  Phoenix.
* FROZEN CODEBOOK -- the SAGE variants' codebook is pinned to the
  establishment canonicals BEFORE any held-out update is revealed.  The
  held-out updates (>= 8, covering every issue section-C content type:
  paraphrased concept / unseen value / new combination of known concepts /
  changed state / contradiction / negation / numeric constraint /
  delayed-relevance) are compiled but their canonicals are deliberately NOT
  in the frozen codebook (proven by the frozen-codebook-proof test).
* HELD-OUT UPDATES -- the updates are revealed and the six-turn sealed
  exchange loop runs exactly as in the standard scenario, but the scenario
  globals of the loaded benchmark module (``SHARED_CONTEXT`` / ``UPDATES`` /
  ``STATE_DICTS`` / ``CHANGE_MARKERS``) are patched from the held-out fixture
  BEFORE the spec builders / benchmark / scoring read them (they resolve the
  globals at call time), so ``run_benchmark``, the plain variants, the SAGE
  variants and the sealed scorer all operate on the held-out material.

SAGE variants run in BOTH explicitly-labeled codebook modes:

* ``oracle_codebook: true`` -- the ORACLE codebook (compiled from the
  establishment material AND all held-out updates, as ``cb._sage_specs()``
  does): the benchmark-recorded upper bound where the codebook was allowed to
  see everything.  Rows are the standard sealed rows against the patched
  scenario; their variant_name carries a `` [oracle]`` suffix.  The
  "allowed to see everything" narrative is exact for the CODEBOOK variants
  v09/v10 (their oracle codebook is the full clause set and the frozen one
  is a pure subset of it).  For v11/v12 it must NOT be read that way:
  oracle v11's codebook is ``[]`` (references + state deltas) and oracle
  v12's is the state-field KEYS, so the frozen-vs-oracle delta on v11/v12
  mixes codebook-kind with frozen-ness (the frozen re-encode gives v11/v12
  a text-clause codebook their oracle design never had).  The data is
  honest and deterministic; the labels keep the two modes from being
  merged.
* ``oracle_codebook: false`` -- the FROZEN establishment-only codebook:
  spec copies of the oracle SAGE specs with the ``codebook`` field replaced
  by the sorted establishment canonicals, deterministically re-encoded
  through the REAL codec (``_render_frozen_variant_packets``, mirroring
  ``_render_sage_variant_packets``: schema reset, codebook registration in
  order, pinned packet ids, v10 pattern warm-up).  Their wire bytes ARE the
  measurement -- no benchmark-recorded counterpart exists for the frozen
  codebook -- and they differ from the oracle rows' (the smaller frozen
  codebook inlines more literals).  Their variant_name carries a
  `` [frozen]`` suffix.

Every held-out row carries ``oracle_codebook: true|false`` (true for the
oracle SAGE rows, false for the frozen SAGE rows and the plain variants --
a plain variant has no codebook mode; the label is false), and the artifact
gains top-level keys ``dataset_split: "held_out"`` and ``oracle_codebook``
(a mapping of each evaluated SAGE variant to its modes,
``{"v09": ["frozen", "oracle"], ...}``).  ``--held-out`` cannot be combined
with ``--record-feedback`` (clean exit-2 error): feedback-loop semantics are
defined against the standard scenario; held-out feedback is a future
refinement.  Default OFF keeps every artifact byte-identical to the
stage-1/2 sealed shape (no ``dataset_split`` / ``oracle_codebook`` keys, no
mode suffixes).

Sealed mechanism attribution (issue #22, stage 4 -- default OFF)
----------------------------------------------------------------
Every sealed row carries a ``mechanism_used`` field naming the PRIMARY
compression mechanism of the turn's encode, derived deterministically from
the real encode, via the same re-encode machinery that renders the sealed
packets: the packet's own strategy/base/refs/atoms, plus the encode's
decisions list ONLY for the receiver-capability attribution
(``fallback_negotiated`` -- the sole decision-level signal consulted;
``"learned_pattern"`` is inferred from the codec's PATTERN-STORE state, an
active learned pattern for the coded atom's concept, not from a decision
record).  The values: ``"state_delta"`` (delta packet with a base),
``"reference"`` (reference packet with refs), ``"learned_pattern"`` (a
coded atom's concept has an active learned pattern), ``"codebook"`` (coded
atoms; codebook definitions used), ``"capability"`` (only when the
decisions record a receiver-capability negotiation --
``fallback_negotiated``), ``"literal"`` (all-literal packet, no compression
mechanism), or ``"none"`` (plain variants, which have no codec lifecycle).
The artifact gains a top-level ``mechanism_summary`` mapping each variant
to its per-mechanism counts across that variant's sealed rows (in held-out
mode the oracle and frozen rows of the same variant share one bucket; the
per-row ``mechanism_used`` values stay distinguishable on the rows).  This
is ADDITIVE JSON: no existing row field changes beyond the new key, and
default-OFF artifacts carry neither ``mechanism_used`` nor
``mechanism_summary``.

RFC field mapping (per result row)
----------------------------------
* receiver model        -> ``receiver_model`` (the config identity)
* model version         -> ``model_version`` (config ``version``)
* codebook version      -> ``codebook_version`` (config, default ``global:1``)
* decoder configuration -> ``decoder_configuration`` (one of
  ``direct symbolic`` / ``decoder-assisted`` / ``full natural-language
  expansion``, from ``--decoder-mode``)
* symbolic-format examples -> ``symbolic_examples`` (bool, from
  ``--with-examples``)
* cold vs warm           -> ``receiver_state``

Cold vs warm
------------
Every selected variant's six exchanges are run twice per adapter: once
``cold`` (``receiver_prior: null``) and once ``warm`` (prior = the ACKed
shared context).  Both rows are reported, plus warm-vs-cold deltas (wire
bytes, input tokens, cost, task accuracy, critical-fact recall).

Decoder modes (RFC "Model-facing evaluation modes")
---------------------------------------------------
* ``direct-symbolic`` (default): the model sees the compact representation;
  ``model_facing_text`` == ``representation``; no expansion tokens.
* ``decoder-assisted``: the harness expands the packet to model-facing text
  BEFORE sending (``model_facing_text`` == the stage-2 deterministic
  reconstruction) and ADDS the expansion tokens to the adapter-reported
  ``input_tokens`` (RFC "Prevent hidden decompression costs": decoding-step
  tokens are always counted; the reported input tokens are a conservative
  upper bound when the adapter already bills the expanded text).
* ``full-expansion``: the packet is reconstructed to ordinary language;
  the adapter reports the tokens it actually consumed.

>=2 model families gate
-----------------------
The config must cover at least 2 DISTINCT ``family`` values; a config with
<2 families is rejected with a clear error (RFC acceptance criterion 4 /
stage-3 "run the receiver task using at least two model families").

Public result format (RFC "Proposed public result format")
----------------------------------------------------------
The printed table and ``--output`` artifact use the RFC's six columns,
one row per (variant, receiver, cold/warm) combination, sorted
deterministically::

    | Variant | Wire bytes | Input tokens | Total cost | Task accuracy | Critical-fact recall |
    | --- | --: | --: | --: | --: | --: |

Raw artifacts (``--output <dir>``) are written OUTSIDE the repository:
``model_eval_harness.json`` (per-exchange rows + table rows + deltas) and
``model_eval_harness.md``.  The scratch codec database lives at a
per-process-unique path ``~/.sage-bench/model_eval_harness-<pid>.db`` (the
pid suffix keeps concurrent harness processes on separate files) -- never
inside the output dir -- and is stable for the lifetime of the process (it is
never deleted while the module-level sqlalchemy engine may hold pooled
connections to it); it is removed at process exit.  The output dir contains
only the two artifacts.

Determinism: two runs produce byte-identical printed tables, ``.md``
artifacts and JSON artifacts except for the measured per-adapter-call
``latency_ms`` row values (real wall-clock measurements, deliberately
excluded from determinism comparisons); ``generated_at`` is pinned to the
benchmark's fixed timestamp.

Feedback loop (issue #16, stage 4 -- RFC "learned semantic shorthand"):
with ``--record-feedback`` (default OFF), after the exchanges the harness
records each selected SAGE variant's measured task success (the mean of the
adapter-reported ``task_success`` for that variant's rows) into the codec's
pattern store via ``PatternStore.record_feedback``, mirroring
``runtime.feedback`` semantics: ``task_success`` must be in ``[0, 1]``
(``ValueError``), an unknown ``packet_id`` raises ``KeyError``, and the
decisions come from the ``MessageAudit`` rows the real encodes created
(pinned packet ids per variant/turn, re-encoded deterministically into the
scratch database).  The feedback summary (patterns updated, ``task_utility``
and ``utility_score`` before/after per pattern) is ADDITIVE JSON -- a new
top-level ``feedback`` key in the artifact -- and never alters existing row
fields or the RFC table; wire bytes are byte-identical with or without the
flag (feedback is post-hoc DB bookkeeping, never touches encode).  Without
the flag the artifacts are byte-identical to the stage-3 shape.

``run_harness`` (the public API) refuses to run unless ``SAGE_DATABASE_URL``
is set to a writable scratch database path -- it never operates on the
ambient default database (``~/sage.db``); ``main()`` sets this up
automatically.  It also refuses when ``sage_plugin.db`` is already imported
with an engine bound to a different database than ``SAGE_DATABASE_URL`` (the
module-level engine cannot be rebound in this process).  ``--timeout`` must
be a positive finite number, an empty ``--variants`` value is an error, and
``family``/``version`` values are whitespace-stripped on load.

Run it (provider configured):

    SAGE_BENCH_LLM_PROVIDER=fake uv run --with '.[dev,mcp]' \\
        python scripts/model_eval_harness.py --adapters adapters.json \\
        --output /opt/data/sage/scratch/stage3-smoke
"""

from __future__ import annotations

import argparse
import atexit
import hashlib
import importlib.util
import json
import math
import os
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

PROVIDER_ENV = "SAGE_BENCH_LLM_PROVIDER"
NO_PROVIDER_NOTE = "not run, no provider"

#: Default codebook release label reported for receivers whose config does
#: not pin one (SAGE codebook releases are signed manifests addressed by
#: namespace/release label -- see ``sage_plugin.codebook_releases``).
DEFAULT_CODEBOOK_VERSION = "global:1"

#: Maximum accepted length (in characters) of a sealed-mode ``task_response``
#: string.  The harness persists the adapter's reply verbatim into the
#: artifact, so an unbounded reply would let a hostile adapter bloat the
#: artifact (or exhaust harness memory) at will -- issue #22 adversary
#: finding F2.  Replies longer than this are rejected with an
#: adapter-naming RuntimeError before any scoring or persistence.  The cap
#: counts CHARACTERS, not bytes (``len()`` on the ``str``) -- strictly
#: bounded either way.
MAX_TASK_RESPONSE_CHARS = 100_000

DECODER_MODES = ("direct-symbolic", "decoder-assisted", "full-expansion")
DECODER_LABELS = {
    "direct-symbolic": "direct symbolic",
    "decoder-assisted": "decoder-assisted",
    "full-expansion": "full natural-language expansion",
}

#: RFC "Proposed public result format" -- exactly these columns/alignment.
RFC_TABLE_HEADER = "| Variant | Wire bytes | Input tokens | Total cost | Task accuracy | Critical-fact recall |"
RFC_TABLE_SEPARATOR = "| --- | --: | --: | --: | --: | --: |"

#: Stage-2 variants whose per-turn content is the state dict, not a message.
_STATE_VARIANTS = frozenset({"v05", "v06", "v11", "v12"})
_ALL_VARIANT_IDS = [f"v{index:02d}" for index in range(1, 13)]


def _scratch_db_path() -> Path:
    """Per-process-unique scratch database path (never deleted mid-process).

    The pid suffix keeps concurrent harness processes on separate files: a
    process's atexit cleanup only ever touches its own file, and per-variant
    schema resets can never race on a shared database.
    """
    # Respect an explicit HOME on every platform. pathlib.Path.home() ignores
    # HOME on Windows, which previously made isolated harness runs write to the
    # real user profile instead of the caller-provided scratch home.
    home = Path(os.environ["HOME"]) if os.environ.get("HOME") else Path.home()
    return home / ".sage-bench" / f"model_eval_harness-{os.getpid()}.db"


def _cleanup_scratch_db() -> None:
    """Best-effort removal of the scratch database at process exit.

    The module-level engine is disposed first when it is bound to the scratch
    file, so the file is never unlinked while a pooled connection may still
    target it.  Only runs at interpreter exit; never mid-process.
    """
    path = _scratch_db_path()
    db_module = sys.modules.get("aifence.bus.db")
    if db_module is not None:
        try:
            url = db_module.engine.url
            if url.drivername == "sqlite" and url.database:
                try:
                    engine_path = Path(url.database)
                except TypeError:
                    engine_path = None
                if engine_path is not None and engine_path == path:
                    db_module.engine.dispose()
        except Exception:
            pass
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


atexit.register(_cleanup_scratch_db)


def _load_compression_benchmark() -> Any:
    """Load the stage-2 benchmark as a module (same pattern the tests use)."""
    spec = importlib.util.spec_from_file_location(
        "compression_benchmark", Path(__file__).resolve().parent / "compression_benchmark.py"
    )
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def provider_available() -> bool:
    """True when ``SAGE_BENCH_LLM_PROVIDER`` is a non-empty environment value."""
    return bool(os.environ.get(PROVIDER_ENV, "").strip())


def validate_adapters(adapters: dict[str, Any]) -> dict[str, Any]:
    """Validate the adapters config and enforce the >=2 families gate."""
    if not isinstance(adapters, dict) or not adapters:
        raise ValueError("adapter configuration must be a non-empty object")
    families: set[str] = set()
    for identity, spec in sorted(adapters.items()):
        if not isinstance(spec, dict):
            raise ValueError(f"adapter {identity}: spec must be an object")
        family = spec.get("family")
        version = spec.get("version")
        command = spec.get("command")
        if not isinstance(family, str) or not family.strip():
            raise ValueError(f"adapter {identity}: 'family' is required")
        if not isinstance(version, str) or not version.strip():
            raise ValueError(f"adapter {identity}: 'version' is required")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
            raise ValueError(f"adapter {identity}: 'command' must be a non-empty list of strings")
        # Normalize: whitespace-padded family/version are accepted but always
        # reported stripped (rows, families gate, artifact).
        spec["family"] = family.strip()
        spec["version"] = version.strip()
        families.add(spec["family"])
    if len(families) < 2:
        raise ValueError(
            "adapter configuration must cover at least 2 distinct model families "
            f"(RFC stage 3); got {sorted(families)}"
        )
    return adapters


def load_adapters(path: str | Path) -> dict[str, Any]:
    """Load and validate an adapters JSON config file."""
    return validate_adapters(json.loads(Path(path).read_text()))


def _invoke(command: list[str], payload: dict[str, Any], timeout: float, identity: str) -> dict[str, Any]:
    """Invoke an adapter command (mirrors ``model_matrix_benchmark._invoke``).

    The child environment is SCRUBBED of every ``SAGE_*`` variable: adapter
    processes are hostile in the sealed threat model and must never be able
    to reach the evaluator's ground-truth codec database through an inherited
    ``SAGE_DATABASE_URL`` (or any other ``SAGE_*`` setting) -- issue #22
    adversary finding F1.  This is an INTERFACE-LEVEL boundary, not a
    security boundary against the same user: a same-user process with
    filesystem access could still read the harness's own source (which
    embeds the benchmark fixture) or guess the scratch database path
    (``~/.sage-bench/model_eval_harness-<pid>.db``); the harness adds no
    channel beyond that ambient reality. ``HOME``/``PATH`` and all non-SAGE
    variables pass through unchanged, except that Windows receives a standard
    ``HOME`` value and ``USERPROFILE`` is aligned with it so child adapters
    resolve one isolated home directory consistently.
    """
    started = time.perf_counter()
    child_env = {k: v for k, v in os.environ.items() if not k.startswith("SAGE_")}
    if os.name == "nt":
        child_env.setdefault("HOME", child_env.get("USERPROFILE", str(Path.home())))
        child_env["USERPROFILE"] = child_env["HOME"]
    try:
        completed = subprocess.run(
            command,
            input=json.dumps(payload, separators=(",", ":")),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            env=child_env,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"adapter {identity} timed out after {timeout}s") from exc
    except OSError as exc:
        raise RuntimeError(f"adapter {identity} could not start: {exc}") from exc
    latency_ms = (time.perf_counter() - started) * 1000
    if completed.returncode != 0:
        raise RuntimeError(
            f"adapter {identity} failed (exit {completed.returncode}): "
            f"{completed.stderr.strip() or 'benchmark adapter failed'}"
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"adapter {identity} returned non-JSON output: {completed.stdout[:200]!r}") from exc
    if not isinstance(result, dict):
        raise RuntimeError(f"adapter {identity} returned a non-object result")
    result.setdefault("latency_ms", latency_ms)
    return result


def _sage_packet(spec: dict[str, Any], turn: int, content: Any, strategy_note: str) -> str:
    """Deterministic symbolic rendering of a SAGE variant's packet."""
    packet_id = "P" + hashlib.sha256(f"{spec['id']}:{turn}".encode()).hexdigest()[:32]
    if isinstance(content, dict):
        return json.dumps(
            {"packet": packet_id, "strategy_note": strategy_note, "state": content},
            sort_keys=True,
            separators=(",", ":"),
        )
    from aifence.bus.compiler import compile_content  # lazy: standalone binds the DB first

    canonicals = [unit.canonical for unit in compile_content(content)]
    return json.dumps(
        {"packet": packet_id, "strategy_note": strategy_note, "canonicals": canonicals},
        sort_keys=True,
        separators=(",", ":"),
    )


# ---------------------------------------------------------------------------
# Sealed direct-symbolic actual-packet rendering (issue #22, stage 2 -- §B
# mode 1).  The stage-1 ``_sage_packet`` proxy above stays byte-identical for
# the UNSEALED path; sealed direct-symbolic SAGE payloads instead carry a
# canonical rendering of the REAL codec packet for the (variant, turn).
# ---------------------------------------------------------------------------

#: The ONLY packet ``meta`` keys the wire codec exports (mirror of the
#: whitelist in ``WireCodec.compact``, src/sage_plugin/wire_codec.py).  The
#: rendering filters ``meta`` to exactly this set so it equals the real wire
#: packet plus the ``bindings`` legend -- evaluator-side meta fields
#: (``strategy``, ``codebook_fingerprint``, ``receiver_known_code_count``)
#: never leave the evaluator.
_WIRE_META_KEYS: frozenset[str] = frozenset(
    {"state", "revision", "budget_exceeded", "memory_tier"}
)


def _render_packet_json(codec: Any, packet: Any) -> str:
    """Canonical compact JSON of a real codec packet plus a ``bindings`` legend.

    The packet fields (``v``/``id``/``cb``/``sender``/``receiver``/``act``,
    ``atoms`` with code/cv + literals, ``refs``, ``base``, ``delta``,
    ``prov``, and ``meta`` filtered to the wire whitelist
    {``state``, ``revision``, ``budget_exceeded``, ``memory_tier``} -- the
    exact subset ``WireCodec.compact`` exports, so the serialized ``meta``
    equals the real wire packet's) are serialized exactly as the codec
    produced them (``model_dump``, ``exclude_none`` for compactness).
    Evaluator-side meta fields (``strategy``, ``codebook_fingerprint``,
    ``receiver_known_code_count``) are deliberately NOT serialized: a real
    wire packet never carries them.  ``bindings`` maps every atom's
    ``code:cv`` to its canonical clause via the codebook's lookup-by-code API
    (``Codebook.get_by_code`` -- the authoritative code -> concept index;
    concept ids follow the registration order of ``spec[\"codebook\"]`` in the
    freshly reset schema, so the mapping is deterministic).  An atom that
    references a learned pattern (``PatternStore.by_concept_id``) maps to the
    pattern's EXPANDED canonical -- exactly what the decoder renders for that
    atom -- so the rendering is self-contained: a model can answer from codes
    + bindings while the full codebook/pattern store stays evaluator-side.
    An unresolvable code maps to ``null`` in the legend -- DEFENSIVE ONLY:
    for the sealed variants (v09-v12) every atom's code is registered in the
    freshly reset schema, so the fallback is unreachable (a miss would
    indicate a codec/schema bug, not a legitimate rendering shape).
    ``Packet.model_validate`` of the result ignores the extra ``bindings``
    key, so the rendering round-trips through the real codec unchanged.
    """
    data = packet.model_dump(mode="json", exclude_none=True)
    # Meta is filtered to the wire whitelist (see ``_WIRE_META_KEYS``) so the
    # rendering carries exactly what a real wire packet carries -- no
    # evaluator-side decoder metadata (strategy / codebook fingerprint /
    # receiver knowledge) leaks through the sealed boundary.
    data["meta"] = {k: v for k, v in data["meta"].items() if k in _WIRE_META_KEYS}
    bindings: dict[str, Any] = {}
    for atom in packet.atoms:
        if not atom.code or atom.cv is None:
            continue
        key = f"{atom.code}:{atom.cv}"
        if key in bindings:
            continue
        concept = codec.codebook.get_by_code(atom.code)
        if concept is None:
            bindings[key] = None
            continue
        pattern = codec.patterns.by_concept_id(concept.id)
        bindings[key] = pattern.canonical if pattern is not None else concept.canonical
    data["bindings"] = bindings
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _render_sage_variant_packets(cb: Any, variant_spec: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Re-encode a SAGE variant through the REAL codec, exactly like the benchmark.

    Mirrors ``cb._run_sage_variant``'s per-variant setup: schema reset,
    ``Settings`` from the spec, codebook registration from ``spec[\"codebook\"]``
    in order, pinned packet ids (per variant/turn), the v10 pattern warm-up
    exchange (learn + activate), and the per-turn encode+decode sequence
    (``use_receiver_knowledge``/``use_patterns``/``base_state``/``inline_limit``
    from the spec; the decode keeps ACKed receiver knowledge and reference
    resolution in the same state the benchmark's run had).  For every turn it
    returns the canonical rendering of the REAL encoded packet plus the
    recorded wire bytes (``context_report`` right after encode) and the
    accumulated reconstruction.  Because the setup is deterministic, the
    re-encoded wire bytes equal the benchmark's recorded ``wire_bytes`` for
    the same ``(variant, turn)`` -- the honesty gate proven in
    ``tests/test_model_eval_packet.py``.
    """
    from sqlalchemy import select

    from aifence.bus import db as db_module
    from aifence.bus.codec import SageCodec
    from aifence.bus.config import Settings
    from aifence.bus.db import SessionLocal
    from aifence.bus.db_models import LearnedPattern

    db_module.init_db()
    cb._reset_schema(db_module)
    settings = Settings(
        auth_required=False,
        database_url=os.environ.get("SAGE_DATABASE_URL", "sqlite://"),
        context_accounting_enabled=True,
        learning_mode="managed",
        **variant_spec.get("settings", {}),
    )
    results: dict[int, dict[str, Any]] = {}
    reconstruction = ""
    with SessionLocal() as db:
        codec = SageCodec(db, settings)
        for canonical in variant_spec["codebook"]:
            codec.codebook.register("global", canonical)
        db.commit()

        warmup = variant_spec.get("warmup")
        if warmup is not None:
            cb._pin_packet_id(codec, variant_spec["id"], "warmup")
            codec.encode(cb._sage_request(warmup, auto_learn=True, record_learning=True))
            pattern = db.scalar(select(LearnedPattern))
            if pattern is not None:
                codec.patterns.set_status(pattern.pattern_id, "active")
                db.commit()

        base_id: str | None = None
        for turn in range(6):
            cb._pin_packet_id(codec, variant_spec["id"], turn)
            content = variant_spec["content_fn"](turn)
            base_state = base_id if (turn > 0 and variant_spec.get("chain_states")) else None
            inline_limit = variant_spec.get("inline_limit") if turn == 0 else None
            request = cb._sage_request(
                content,
                use_receiver_knowledge=variant_spec.get("ack", False),
                use_patterns=variant_spec.get("patterns", True),
                base_state=base_state,
                inline_limit=inline_limit,
            )
            encoded = codec.encode(request)
            encode_report = codec.context_report()
            if encode_report is None:  # pragma: no cover - accounting is enabled above
                raise RuntimeError("codec context report unavailable during sealed packet rendering")
            decisions = _encode_decisions(db, encoded.packet.id)
            decoded = codec.decode(
                encoded.packet,
                resolve_refs=variant_spec.get("resolve_refs", False),
                receiver="bob",
                acknowledge=variant_spec.get("ack", False),
            )
            piece = variant_spec["render_fn"](decoded)
            reconstruction = f"{reconstruction} {piece}".strip()
            if variant_spec.get("chain_states") and encoded.packet.meta.get("state"):
                base_id = str(encoded.packet.meta["state"])
            results[turn] = {
                "rendering": _render_packet_json(codec, encoded.packet),
                "wire_bytes_json": encode_report.wire_bytes_json,
                "wire_bytes_msgpack": encode_report.wire_bytes_msgpack,
                "reconstruction": reconstruction,
                "piece": piece,
                "strategy": encoded.strategy,
                "note": f"sage strategy: {encoded.strategy}",
                "mechanism_used": _mechanism_for_encode(codec, encoded, decisions),
            }
    return results


#: Deterministic re-encode cache: the rendering for a (variant, turn) is fully
#: determined by the variant spec and the freshly reset schema, so re-encodes
#: are cached per key (the wire-bytes honesty gate in the tests proves the
#: cached rendering corresponds to the benchmark's recorded packet).  NOTE:
#: the cache is PER-PROCESS and scenario-tagged -- ``_SCENARIO_TAG`` is set by
#: ``_apply_scenario`` before any rendering happens, and the tag is part of
#: every key, so a process that evaluates more than one scenario (standard and
#: held-out) never serves a rendering compiled against the wrong fixture.
_PACKET_RENDER_CACHE: dict[tuple[str, str, int], str] = {}


#: Current scenario tag for the per-process render/spec caches.  ``"default"``
#: for the standard Phoenix scenario; ``"held_out"`` while the harness is
#: evaluating the frozen-codebook split.
_SCENARIO_TAG: str = "default"

#: Pristine scenario globals of the loaded benchmark module, captured the
#: FIRST time a held-out patch replaces them and restored when the default
#: scenario is applied again.  Keyed by the module object so in-process
#: reuse of ``_apply_scenario`` (tests/dev) always restores the module it
#: patched; ``run_harness`` loads a fresh benchmark module per call, so a
#: default-OFF run never finds a stash entry and stays byte-identical to
#: stage 3.
_ORIGINAL_SCENARIO_GLOBALS: dict[Any, dict[str, Any]] = {}


def _render_actual_packet(cb: Any, variant_spec: dict[str, Any], turn: int) -> str:
    """The sealed direct-symbolic model-facing packet for a SAGE variant turn.

    A canonical compact-JSON rendering of the REAL codec packet for the
    ``(variant, turn)``, deterministically re-encoded exactly like the
    benchmark (see ``_render_sage_variant_packets``) and cached per
    (scenario tag, variant, turn).
    """
    key = (_SCENARIO_TAG, variant_spec["id"], turn)
    cached = _PACKET_RENDER_CACHE.get(key)
    if cached is not None:
        return cached
    for t, entry in _render_sage_variant_packets(cb, variant_spec).items():
        _PACKET_RENDER_CACHE[(_SCENARIO_TAG, variant_spec["id"], t)] = entry["rendering"]
    return _PACKET_RENDER_CACHE[key]


_SAGE_VARIANT_SPECS_CACHE: dict[tuple[str, str], dict[str, Any]] = {}


def _sage_variant_spec(cb: Any, variant_id: str) -> dict[str, Any]:
    """The stage-2 benchmark's spec for a SAGE variant (cached per scenario).

    The cache key carries ``_SCENARIO_TAG`` because the spec is built from
    ``cb._sage_specs()``, which reads the scenario globals at call time -- the
    held-out fixture yields DIFFERENT specs (oracle codebook over the
    held-out material) than the standard fixture.
    """
    key = (_SCENARIO_TAG, variant_id)
    spec = _SAGE_VARIANT_SPECS_CACHE.get(key)
    if spec is None:
        spec = next((s for s in cb._sage_specs() if s["id"] == variant_id), None)
        if spec is None:
            raise RuntimeError(f"unknown SAGE variant {variant_id!r} in sealed packet rendering")
        _SAGE_VARIANT_SPECS_CACHE[key] = spec
    return spec


#: Frozen-codebook re-encode cache: per (scenario tag, variant), the full
#: per-turn rendering dict from ``_render_frozen_variant_packets``.  The
#: frozen codebook is the same sorted establishment-canonical list for every
#: variant of one held-out run, so the (tag, variant) key identifies the
#: re-encode.
_FROZEN_PACKET_RENDER_CACHE: dict[tuple[str, str], dict[int, dict[str, Any]]] = {}


#: Lifecycle-primed warm re-encode cache: per (scenario tag, variant,
#: frozen-flag), the full per-turn rendering dict from
#: ``_render_warm_variant_packets``.  The warm re-encode primes the receiver
#: through the REAL SAGE lifecycle (establishment encode -> ACK -> knowledge
#: commit, verified) ONCE per variant before its warm turns; the
#: (tag, variant, frozen) key identifies the deterministic re-encode (the
#: frozen flag matters because the frozen warm re-encode registers the
#: establishment-only codebook, not the oracle one).
_WARM_PACKET_RENDER_CACHE: dict[tuple[str, str, bool], dict[int, dict[str, Any]]] = {}


# ---------------------------------------------------------------------------
# Sealed mechanism attribution + lifecycle-primed warm receiver (issue #22,
# stage 4).  ``mechanism_used`` is derived deterministically from the real
# encode (packet strategy + the decision list the encode recorded), and the
# warm receiver is established through the REAL SAGE lifecycle instead of a
# simulated receiver_prior.
# ---------------------------------------------------------------------------


def _encode_decisions(db: Any, packet_id: str | None) -> list[dict[str, Any]]:
    """The decision list the real encode recorded for a pinned packet.

    ``codec.encode`` writes a ``MessageAudit`` row (with ``decisions``)
    before returning, so the authoritative decision list for a re-encoded
    packet is read back from the freshly reset schema -- exactly the same
    source ``_record_feedback_for_packets`` uses.
    """
    from sqlalchemy import select

    from aifence.bus.db_models import MessageAudit

    if packet_id is None:  # pragma: no cover - encode always assigns the pinned id
        raise RuntimeError("encoded packet has no id during packet rendering")
    audit = db.scalar(select(MessageAudit).where(MessageAudit.packet_id == packet_id))
    if audit is None:  # pragma: no cover - encode always writes the audit row
        raise RuntimeError(f"no MessageAudit row for packet {packet_id!r} during packet rendering")
    return list(audit.decisions or [])


def _mechanism_for_encode(codec: Any, encoded: Any, decisions: list[dict[str, Any]]) -> str:
    """The PRIMARY compression mechanism of one real encode (deterministic).

    Attribution priority: ``"capability"`` when the decisions record a
    receiver-capability negotiation (``fallback_negotiated`` -- the ONLY
    decision-level signal consulted; the decisions list plays no other role
    here); then the packet's own strategy --
    ``"state_delta"`` for a delta packet with a base, ``"reference"`` for a
    reference packet with refs; then the atom content of a semantic packet
    -- ``"learned_pattern"`` when a coded atom's concept has an active
    learned pattern (inferred from the PATTERN-STORE state via
    ``codec.patterns.by_concept_id`` -- a deterministic proxy for "a
    pattern atom fired", NOT a decision-level pattern-usage record; a
    future fixture whose updates code atoms for the warmup pattern's
    concept would flip turns to ``"learned_pattern"`` without the pattern
    actually being applied), ``"codebook"`` when coded atoms are
    present, ``"literal"`` when the packet is all-literal (no compression
    mechanism); else ``"none"``.  Semantic packets carry atoms and
    reference/delta packets carry refs/base instead, so the mapping is
    unambiguous per packet; ``"capability"`` never fires in the benchmark's
    own runs (no receiver capabilities are configured) but is attributed
    whenever a negotiation did influence an encode.
    """
    if any(decision.get("action") == "fallback_negotiated" for decision in decisions):
        return "capability"
    packet = encoded.packet
    if encoded.strategy == "delta" or (packet.base is not None and packet.delta is not None):
        return "state_delta"
    if encoded.strategy == "reference" or packet.refs:
        return "reference"
    pattern_fired = False
    coded = False
    for atom in packet.atoms:
        if not atom.code:
            continue
        coded = True
        concept = codec.codebook.get_by_code(atom.code)
        if concept is not None and codec.patterns.by_concept_id(concept.id) is not None:
            pattern_fired = True
    if pattern_fired:
        return "learned_pattern"
    if coded:
        return "codebook"
    if packet.atoms:
        return "literal"
    return "none"


def _verify_primed_knowledge(
    codec: Any, variant_spec: dict[str, Any], content: Any, packet: Any
) -> None:
    """HONESTY GATE: the priming decode must have committed receiver knowledge.

    The establishment packet's OWN structure determines what the receiver
    must have learned from ACKing it: coded atoms -> known codes, refs ->
    known refs, dict content -> a committed ``current_state`` (the state
    the packet checkpointed).  If the knowledge store shows none of what
    the packet carried, priming failed and the warm path RAISES instead of
    fabricating a warm benefit.  (Reference packets commit ``known_refs``,
    code packets commit ``known_codes``, and a state packet always commits
    ``current_state`` -- probed behavior of ``KnowledgeStore.acknowledge``.)
    """
    store = codec.knowledge
    known_codes = store.known_codes("bob", "default")
    known_refs = store.known_refs("bob", "default")
    knowledge = store.get("bob", "default")
    expect_codes = any(atom.code for atom in packet.atoms)
    expect_refs = bool(packet.refs)
    problems: list[str] = []
    if expect_codes and not known_codes:
        problems.append(
            "the establishment packet carried coded atoms but the knowledge store "
            "committed no known codes"
        )
    if expect_refs and not known_refs:
        problems.append(
            "the establishment packet carried references but the knowledge store "
            "committed no known refs"
        )
    if isinstance(content, dict) and (knowledge is None or knowledge.current_state is None):
        problems.append(
            "the establishment packet checkpointed state but no current_state was committed"
        )
    if knowledge is None and not expect_codes and not expect_refs:
        problems.append(
            "the establishment packet carried neither codes nor refs and no receiver "
            "knowledge row was created"
        )
    if problems:
        raise RuntimeError(
            "sealed warm lifecycle priming failed to commit receiver knowledge for variant "
            f"{variant_spec['id']}: {'; '.join(problems)} -- refusing to fabricate a warm benefit"
        )


def _prime_receiver(codec: Any, cb: Any, variant_spec: dict[str, Any]) -> Any:
    """Establish the warm receiver through the REAL SAGE lifecycle.

    The shared-context turn (``content_fn(0)`` -- ``SHARED_CONTEXT`` or the
    held-out ``ESTABLISHMENT_SHARED_CONTEXT``) is encoded with a pinned
    packet id exactly like turn 0 of the benchmark loop and DECODED with
    ``acknowledge=True`` (receiver "bob"), which COMMITS receiver knowledge
    (known codes / known refs / current_state) into the knowledge store.
    The commit is verified (``_verify_primed_knowledge``) -- a failed
    priming raises rather than fabricating a warm benefit.  Returns the
    encoded establishment packet (its structure drives the verification).
    """
    cb._pin_packet_id(codec, variant_spec["id"], "prime")
    prime_content = variant_spec["content_fn"](0)
    prime_encoded = codec.encode(
        cb._sage_request(
            prime_content,
            use_receiver_knowledge=False,  # establishment precedes any knowledge
            use_patterns=variant_spec.get("patterns", True),
            base_state=None,
            inline_limit=variant_spec.get("inline_limit"),  # turn-0 semantics
        )
    )
    codec.decode(
        prime_encoded.packet,
        resolve_refs=variant_spec.get("resolve_refs", False),
        receiver="bob",
        acknowledge=True,
    )
    _verify_primed_knowledge(codec, variant_spec, prime_content, prime_encoded.packet)
    return prime_encoded


def _render_warm_variant_packets(
    cb: Any, variant_spec: dict[str, Any], *, frozen: bool = False
) -> dict[int, dict[str, Any]]:
    """Re-encode a SAGE variant with a LIFECYCLE-PRIMED warm receiver.

    Mirrors ``_render_sage_variant_packets`` (schema reset, ``Settings``
    from the spec, codebook registration in order, pinned packet ids, the
    v10 pattern warm-up) and THEN primes the receiver through the REAL SAGE
    lifecycle before the per-turn loop: ``_prime_receiver`` encodes the
    shared-context turn with a pinned packet id and decodes it with
    ``acknowledge=True``, committing receiver knowledge (verified against
    the store -- a failed priming raises, never fabricates).  The per-turn
    loop then encodes with ``use_receiver_knowledge=True`` (the warm path
    always consumes the primed knowledge; ``acknowledge`` on the decode
    stays the variant's own flag), so the resulting wire bytes ARE the
    primed lifecycle measurement.  Deterministic (pinned ids, fixed
    provenance, content-hashed state ids) and cached per
    (scenario tag, variant, frozen flag).
    """
    key = (_SCENARIO_TAG, variant_spec["id"], frozen)
    cached = _WARM_PACKET_RENDER_CACHE.get(key)
    if cached is not None:
        return cached
    from sqlalchemy import select

    from aifence.bus import db as db_module
    from aifence.bus.codec import SageCodec
    from aifence.bus.config import Settings
    from aifence.bus.db import SessionLocal
    from aifence.bus.db_models import LearnedPattern

    db_module.init_db()
    cb._reset_schema(db_module)
    settings = Settings(
        auth_required=False,
        database_url=os.environ.get("SAGE_DATABASE_URL", "sqlite://"),
        context_accounting_enabled=True,
        learning_mode="managed",
        **variant_spec.get("settings", {}),
    )
    results: dict[int, dict[str, Any]] = {}
    reconstruction = ""
    with SessionLocal() as db:
        codec = SageCodec(db, settings)
        for canonical in variant_spec["codebook"]:
            codec.codebook.register("global", canonical)
        db.commit()

        warmup = variant_spec.get("warmup")
        if warmup is not None:
            cb._pin_packet_id(codec, variant_spec["id"], "warmup")
            codec.encode(cb._sage_request(warmup, auto_learn=True, record_learning=True))
            pattern = db.scalar(select(LearnedPattern))
            if pattern is not None:
                codec.patterns.set_status(pattern.pattern_id, "active")
                db.commit()

        # LIFECYCLE PRIMING: happens ONCE per variant, before its warm
        # exchanges (the schema was freshly reset above, so the receiver
        # state is per (variant, run)).
        _prime_receiver(codec, cb, variant_spec)

        base_id: str | None = None
        for turn in range(6):
            cb._pin_packet_id(codec, variant_spec["id"], turn)
            content = variant_spec["content_fn"](turn)
            base_state = base_id if (turn > 0 and variant_spec.get("chain_states")) else None
            inline_limit = variant_spec.get("inline_limit") if turn == 0 else None
            request = cb._sage_request(
                content,
                use_receiver_knowledge=True,  # WARM: consume the primed knowledge
                use_patterns=variant_spec.get("patterns", True),
                base_state=base_state,
                inline_limit=inline_limit,
            )
            encoded = codec.encode(request)
            encode_report = codec.context_report()
            if encode_report is None:  # pragma: no cover - accounting is enabled above
                raise RuntimeError("codec context report unavailable during warm packet rendering")
            decisions = _encode_decisions(db, encoded.packet.id)
            decoded = codec.decode(
                encoded.packet,
                resolve_refs=variant_spec.get("resolve_refs", False),
                receiver="bob",
                acknowledge=variant_spec.get("ack", False),
            )
            piece = variant_spec["render_fn"](decoded)
            reconstruction = f"{reconstruction} {piece}".strip()
            if variant_spec.get("chain_states") and encoded.packet.meta.get("state"):
                base_id = str(encoded.packet.meta["state"])
            results[turn] = {
                "rendering": _render_packet_json(codec, encoded.packet),
                "wire_bytes_json": encode_report.wire_bytes_json,
                "wire_bytes_msgpack": encode_report.wire_bytes_msgpack,
                "reconstruction": reconstruction,
                "piece": piece,
                "strategy": encoded.strategy,
                "note": f"sage strategy: {encoded.strategy}",
                "mechanism_used": _mechanism_for_encode(codec, encoded, decisions),
            }
    _WARM_PACKET_RENDER_CACHE[key] = results
    return results


def _attach_sealed_mechanisms(cb: Any, exchanges: list[dict[str, Any]]) -> None:
    """Attach the deterministic ``mechanism_used`` to every SEALED cold exchange.

    SAGE mechanisms come from the same deterministic re-encode the sealed
    payload rendering uses (``_render_sage_variant_packets`` for oracle
    rows; frozen exchanges already carry their mechanism from
    ``_build_frozen_exchanges``); plain variants (no codec lifecycle) carry
    ``"none"``.  Sealed rows only: unsealed rows never read this key.  The
    re-encode also warms the per-turn rendering cache so the payload loop
    never re-encodes.
    """
    rendered_by_variant: dict[str, dict[int, dict[str, Any]]] = {}
    for exchange in exchanges:
        if not exchange["sage"]:
            exchange["mechanism_used"] = "none"
            continue
        if "mechanism_used" in exchange:
            continue  # frozen exchanges already carry it
        variant_id = exchange["variant"]
        rendered = rendered_by_variant.get(variant_id)
        if rendered is None:
            rendered = _render_sage_variant_packets(cb, _sage_variant_spec(cb, variant_id))
            rendered_by_variant[variant_id] = rendered
            for turn, entry in rendered.items():
                _PACKET_RENDER_CACHE[(_SCENARIO_TAG, variant_id, turn)] = entry["rendering"]
        exchange["mechanism_used"] = rendered[exchange["turn"]]["mechanism_used"]


def _build_warm_exchanges(
    cb: Any,
    cold_exchanges: list[dict[str, Any]],
    *,
    frozen_codebook: list[str] | None,
) -> list[dict[str, Any]]:
    """SEALED-mode warm exchange records: lifecycle-primed SAGE re-encodes.

    For every cold exchange of a SAGE variant the variant is re-encoded
    through the REAL codec with a lifecycle-primed warm receiver
    (``_render_warm_variant_packets``: establishment encode -> ACK ->
    knowledge commit (verified) -> per-turn encode with
    ``use_receiver_knowledge=True``) and the warm wire bytes / rendering /
    reconstruction / mechanism replace the cold ones; plain variants keep
    their turn data unchanged (their warm row differs only by the
    ``receiver_state`` label, exactly like stage 3).  The warm wire bytes
    ARE the primed measurement -- produced by the real primed lifecycle,
    never copied from the cold rows.
    """
    warm: list[dict[str, Any]] = []
    for exchange in cold_exchanges:
        entry = dict(exchange)
        if exchange["sage"]:
            spec = _sage_variant_spec(cb, exchange["variant"])
            if exchange.get("frozen"):
                assert frozen_codebook is not None
                spec = dict(spec)
                spec["codebook"] = list(frozen_codebook)
                rendered = _render_warm_variant_packets(cb, spec, frozen=True)
            else:
                rendered = _render_warm_variant_packets(cb, spec)
            turn_entry = rendered[exchange["turn"]]
            entry["representation"] = turn_entry["rendering"]
            entry["wire_bytes"] = turn_entry["wire_bytes_json"]
            entry["reconstruction"] = turn_entry["reconstruction"]
            entry["mechanism_used"] = turn_entry["mechanism_used"]
            entry["primed"] = True
        else:
            entry["mechanism_used"] = "none"
        warm.append(entry)
    return warm


def _mechanism_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Per-variant mechanism counts across the variant's sealed rows.

    Additive top-level ``mechanism_summary``: ``{variant_id: {mechanism:
    count}}`` counting every sealed row of the variant (all receiver
    states; in held-out mode the oracle and frozen rows of the same variant
    share the bucket -- the per-row ``mechanism_used`` values stay
    distinguishable on the rows themselves).
    """
    counts: dict[str, dict[str, int]] = {}
    for row in rows:
        entry = counts.setdefault(row["variant"], {})
        mechanism = row.get("mechanism_used", "none")
        entry[mechanism] = entry.get(mechanism, 0) + 1
    return counts


def _render_frozen_variant_packets(
    cb: Any, variant_spec: dict[str, Any], frozen_codebook: list[str]
) -> dict[int, dict[str, Any]]:
    """Re-encode a SAGE variant against the FROZEN establishment-only codebook.

    A copy of the ORACLE spec (``cb._sage_specs()`` under the patched
    held-out globals) with the ``codebook`` field REPLACED by the sorted
    establishment canonicals, re-encoded through the REAL codec exactly like
    ``_render_sage_variant_packets`` (schema reset, codebook registration in
    order, pinned packet ids, the v10 pattern warm-up).  The resulting wire
    bytes ARE the frozen-codebook measurement -- no benchmark-recorded
    counterpart exists -- and they differ from the oracle rows' (the smaller
    frozen codebook inlines more literals).  Deterministic: two calls return
    byte-identical renderings (cached per scenario tag + variant).
    """
    key = (_SCENARIO_TAG, variant_spec["id"])
    cached = _FROZEN_PACKET_RENDER_CACHE.get(key)
    if cached is not None:
        return cached
    frozen_spec = dict(variant_spec)
    frozen_spec["codebook"] = list(frozen_codebook)
    rendered = _render_sage_variant_packets(cb, frozen_spec)
    _FROZEN_PACKET_RENDER_CACHE[key] = rendered
    return rendered


def _apply_scenario(cb: Any, *, held_out: bool) -> list[str] | None:
    """Point the loaded benchmark module at the requested scenario.

    The benchmark's spec builders (``_plain_specs`` / ``_sage_specs``), its
    ``run_benchmark`` records, ``ground_truth_answers`` / ``evaluate_turn``
    and the harness's sealed scoring all resolve the scenario globals
    (``SHARED_CONTEXT`` / ``UPDATES`` / ``STATE_DICTS`` / ``CHANGE_MARKERS``)
    AT CALL TIME, so patching them before anything reads them switches the
    whole pipeline to the held-out fixture without touching the frozen
    benchmark file.  Also tags the per-process render/spec caches.

    The ORIGINAL globals are captured on the first held-out patch and
    RESTORED when the default scenario is applied again, so in-process reuse
    of this function (tests/dev mixing ``held_out=True`` and
    ``held_out=False`` in one process) never renders default-tagged packets
    over held-out content.  A default-OFF run that never patched finds no
    stash entry and stays byte-identical to stage 3.

    Returns the FROZEN codebook (the sorted establishment canonicals) when
    ``held_out`` is true -- the SAGE variants' frozen ``codebook`` list -- and
    ``None`` for the standard scenario.
    """
    global _SCENARIO_TAG
    if not held_out:
        _SCENARIO_TAG = "default"
        originals = _ORIGINAL_SCENARIO_GLOBALS.pop(cb, None)
        if originals is not None:
            cb.SHARED_CONTEXT = originals["SHARED_CONTEXT"]
            cb.UPDATES = originals["UPDATES"]
            cb.STATE_DICTS = originals["STATE_DICTS"]
            cb.CHANGE_MARKERS = originals["CHANGE_MARKERS"]
        return None
    spec = importlib.util.spec_from_file_location(
        "heldout_scenario", Path(__file__).resolve().parent / "heldout_scenario.py"
    )
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if cb not in _ORIGINAL_SCENARIO_GLOBALS:
        _ORIGINAL_SCENARIO_GLOBALS[cb] = {
            "SHARED_CONTEXT": cb.SHARED_CONTEXT,
            "UPDATES": cb.UPDATES,
            "STATE_DICTS": cb.STATE_DICTS,
            "CHANGE_MARKERS": cb.CHANGE_MARKERS,
        }
    cb.SHARED_CONTEXT = module.ESTABLISHMENT_SHARED_CONTEXT
    cb.UPDATES = module.HELDOUT_UPDATES
    cb.STATE_DICTS = module.HELDOUT_STATE_DICTS
    cb.CHANGE_MARKERS = module.HELDOUT_CHANGE_MARKERS
    _SCENARIO_TAG = "held_out"
    return module.establishment_canonicals(cb)


def _build_exchanges(
    cb: Any, benchmark: dict[str, Any], selected: list[str], *, held_out: bool = False
) -> list[dict[str, Any]]:
    """Per-variant per-turn exchange records (representation, wire bytes, ...).

    In held-out mode every exchange carries an ``oracle_codebook`` label
    (``True`` for the ORACLE SAGE rows -- the benchmark-recorded upper bound
    against the patched held-out scenario -- ``False`` for the plain
    variants, which have no codebook mode) and the SAGE variant_name gains a
    `` [oracle]`` suffix so rows, payloads, table cells and delta rows
    distinguish the codebook modes.  Default OFF keeps the stage-1/2 shape
    byte-identical (no label, no suffix).
    """
    plain = {spec["id"]: spec for spec in cb._plain_specs()}
    sage = {spec["id"]: spec for spec in cb._sage_specs()}
    by_id = {row["variant_id"]: row for row in benchmark["variants"]}
    exchanges: list[dict[str, Any]] = []
    for variant_id in selected:
        variant_row = by_id[variant_id]
        if variant_row["status"] != "ok":
            continue
        spec = sage.get(variant_id) or plain.get(variant_id)
        if spec is None:
            continue
        is_sage = variant_id in sage
        for turn_record in variant_row["turns"]:
            if turn_record["turn"] < 0:  # pattern warm-up exchange (variant 10)
                continue
            turn = turn_record["turn"]
            if is_sage:
                content = spec["content_fn"](turn)
                representation = _sage_packet(spec, turn, content, turn_record.get("note", ""))
            else:
                if variant_id in _STATE_VARIANTS:
                    content = cb.STATE_DICTS[turn]
                else:
                    content = cb.SHARED_CONTEXT if turn == 0 else cb.UPDATES[turn - 1]
                representation = turn_record["reconstruction"]
            exchange = {
                "variant": variant_id,
                "variant_name": variant_row["name"],
                "turn": turn,
                "phase": turn_record["phase"],
                "content": content,
                "representation": representation,
                "wire_bytes": turn_record["wire_bytes_json"],
                "reconstruction": turn_record["reconstruction"],
                "expected": cb.ground_truth_answers(turn),
                "change_markers": cb.CHANGE_MARKERS.get(turn, []),
                "sage": is_sage,
            }
            if held_out:
                if is_sage:
                    exchange["variant_name"] = f"{exchange['variant_name']} [oracle]"
                    exchange["oracle_codebook"] = True
                else:
                    exchange["oracle_codebook"] = False
            exchanges.append(exchange)
    return exchanges


def _build_frozen_exchanges(
    cb: Any, selected: list[str], frozen_codebook: list[str]
) -> list[dict[str, Any]]:
    """Frozen-codebook exchange records for the held-out SAGE variants.

    For every selected SAGE variant the ORACLE spec (``cb._sage_specs()``
    under the patched held-out globals) is re-encoded through the REAL codec
    with the ``codebook`` field REPLACED by the sorted establishment
    canonicals (``_render_frozen_variant_packets``).  The re-encode's wire
    bytes ARE the frozen measurement -- no benchmark-recorded counterpart
    exists for the frozen codebook -- and its rendering is the sealed
    model-facing packet.  Rows carry ``oracle_codebook: False`` and a
    `` [frozen]`` variant_name suffix.
    """
    sage = {spec["id"]: spec for spec in cb._sage_specs()}
    exchanges: list[dict[str, Any]] = []
    for variant_id in selected:
        spec = sage.get(variant_id)
        if spec is None:
            continue  # plain variants have no codebook mode
        rendered = _render_frozen_variant_packets(cb, spec, frozen_codebook)
        for turn in range(6):
            entry = rendered[turn]
            exchanges.append(
                {
                    "variant": variant_id,
                    "variant_name": f"{spec['name']} [frozen]",
                    "turn": turn,
                    "phase": "shared" if turn == 0 else "update",
                    "content": spec["content_fn"](turn),
                    "representation": entry["rendering"],
                    "wire_bytes": entry["wire_bytes_json"],
                    "reconstruction": entry["reconstruction"],
                    "expected": cb.ground_truth_answers(turn),
                    "change_markers": cb.CHANGE_MARKERS.get(turn, []),
                    "sage": True,
                    "frozen": True,
                    "oracle_codebook": False,
                    "mechanism_used": entry["mechanism_used"],
                }
            )
    return exchanges


def _build_payload(
    cb: Any,
    exchange: dict[str, Any],
    receiver_state: str,
    decoder_mode: str,
    symbolic_examples: bool,
) -> dict[str, Any]:
    """The per-exchange JSON payload sent to the adapter."""
    if exchange["sage"] and decoder_mode == "direct-symbolic":
        model_facing = exchange["representation"]
    else:
        model_facing = exchange["reconstruction"]
    prior: dict[str, Any] | None = None
    if receiver_state == "warm":
        prior = {
            "shared_context": cb.SHARED_CONTEXT,
            "codebook_acked": True,
            "patterns_acked": True,
            "note": "receiver prior established in the shared-context phase (codebook/patterns ACKed)",
        }
    payload: dict[str, Any] = {
        "protocol": "sage/0.2",
        "benchmark": "compression_benchmark:phoenix_rfc",
        "variant": exchange["variant"],
        "variant_name": exchange["variant_name"],
        "turn": exchange["turn"],
        "phase": exchange["phase"],
        "receiver_state": receiver_state,
        "receiver_prior": prior,
        "decoder_configuration": DECODER_LABELS[decoder_mode],
        "symbolic_examples": bool(symbolic_examples),
        "representation": exchange["representation"],
        "wire_bytes": exchange["wire_bytes"],
        "model_facing_text": model_facing,
        "content": exchange["content"],
        "expected": exchange["expected"],
        "change_markers": exchange["change_markers"],
    }
    if symbolic_examples:
        payload["examples"] = [{"packet": exchange["representation"], "meaning": exchange["reconstruction"]}]
    return payload


def _build_sealed_payload(
    cb: Any,
    exchange: dict[str, Any],
    receiver_state: str,
    decoder_mode: str,
    spec: dict[str, Any],
) -> dict[str, Any]:
    """The per-exchange JSON payload for SEALED mode (issue #22, stage 1).

    The model runner receives ONLY the identity fields plus ``task``,
    ``model_facing_packet`` and ``allowed_decoder_metadata`` -- NEVER
    uncompressed source content (``content``), answer keys (``expected``),
    ``change_markers``, ``receiver_prior`` or symbolic ``examples`` (the
    exact key set is pinned by the sealed-payload shape test).  ``task`` is
    deterministic per exchange: state variants (v05/v06/v11/v12) ask for the
    current state (``deployment_allowed``/``failed_tests``/
    ``migration_approved``/``blocker``) plus what changed; text variants ask
    for a summary of the latest update plus what changed.
    ``model_facing_packet`` for SAGE variants in ``direct-symbolic`` mode is
    the stage-2 REAL packet rendering (``_render_actual_packet`` -- the
    canonical compact-JSON rendering of the actual codec packet for the
    ``(variant, turn)``, deterministically re-encoded exactly like the
    benchmark, cached per key); every other path keeps the stage-1
    reconstruction selection byte-identical (sealed non-direct-symbolic
    modes and all non-SAGE variants use ``exchange["reconstruction"]``).
    ``allowed_decoder_metadata`` carries the decoder-side knowledge the
    runner may legitimately use: the config's ``codebook_version`` (or
    ``global:1``), the receiver state and the decoder configuration.
    """
    if exchange["sage"] and decoder_mode == "direct-symbolic":
        if exchange.get("frozen") or exchange.get("primed"):
            # FROZEN-codebook mode (held-out, issue #22 stage 3) and
            # LIFECYCLE-PRIMED WARM exchanges (stage 4) carry the re-encoded
            # packet they were built from (``_render_frozen_variant_packets``
            # / ``_render_warm_variant_packets`` output) -- the model faces
            # that rendering.
            model_facing = exchange["representation"]
        else:
            model_facing = _render_actual_packet(
                cb, _sage_variant_spec(cb, exchange["variant"]), exchange["turn"]
            )
    else:
        model_facing = exchange["reconstruction"]
    if exchange["variant"] in _STATE_VARIANTS:
        task = (
            "Report the current receiver state: deployment_allowed, "
            "failed_tests, migration_approved, blocker -- and what changed "
            "since the previous update."
        )
    else:
        task = (
            "Summarize the latest update you received and state what changed "
            "since the previous update."
        )
    return {
        "protocol": "sage/0.2",
        "benchmark": "compression_benchmark:phoenix_rfc",
        "variant": exchange["variant"],
        "variant_name": exchange["variant_name"],
        "turn": exchange["turn"],
        "phase": exchange["phase"],
        "receiver_state": receiver_state,
        "decoder_configuration": DECODER_LABELS[decoder_mode],
        "wire_bytes": exchange["wire_bytes"],
        "symbolic_examples": False,
        "task": task,
        "model_facing_packet": model_facing,
        "allowed_decoder_metadata": {
            "codebook_version": spec.get("codebook_version", DEFAULT_CODEBOOK_VERSION),
            "receiver_state": receiver_state,
            "decoder_configuration": DECODER_LABELS[decoder_mode],
        },
    }


def _critical_fact_recall(
    cb: Any, result: dict[str, Any], exchange: dict[str, Any], identity: str
) -> float:
    """Adapter-reported recall, else the harness's deterministic score of the
    adapter's reconstruction text (RFC fidelity checker), else 0.0."""
    reported = result.get("critical_fact_recall")
    if reported is not None:
        if isinstance(reported, bool) or not isinstance(reported, (int, float)):
            raise RuntimeError(
                f"adapter {identity}: critical_fact_recall must be a finite number, got {reported!r}"
            )
        try:
            value = float(reported)
        except (TypeError, ValueError, OverflowError) as exc:
            raise RuntimeError(
                f"adapter {identity}: critical_fact_recall must be a finite number, got {reported!r}"
            ) from exc
        if not math.isfinite(value):
            raise RuntimeError(
                f"adapter {identity}: critical_fact_recall must be finite, got {reported!r}"
            )
        return min(1.0, max(0.0, value))
    reconstruction = result.get("reconstruction")
    if isinstance(reconstruction, str) and reconstruction.strip():
        return float(cb.fidelity_critical(reconstruction))
    return 0.0


def _finite_float(
    raw: Any,
    identity: str,
    key: str,
    *,
    minimum: float = -math.inf,
    maximum: float | None = None,
) -> float:
    """Coerce to a finite float within [minimum, maximum]; adapter-naming
    RuntimeError on any violation (never silently promotes garbage)."""
    if isinstance(raw, bool):
        raise RuntimeError(f"adapter {identity}: {key} must be a finite number, got {raw!r}")
    try:
        value = float(raw)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(f"adapter {identity}: {key} must be a finite number, got {raw!r}") from exc
    if not math.isfinite(value):
        raise RuntimeError(f"adapter {identity}: {key} must be finite, got {raw!r}")
    if value < minimum:
        raise RuntimeError(f"adapter {identity}: {key} must be >= {minimum}, got {raw!r}")
    if maximum is not None and value > maximum:
        raise RuntimeError(f"adapter {identity}: {key} must be <= {maximum}, got {raw!r}")
    return value


def _non_negative_int(raw: Any, identity: str, key: str) -> int:
    """Require an integral, non-negative value; strings, bools, fractional
    floats and non-finite numbers are rejected."""
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise RuntimeError(f"adapter {identity}: {key} must be a non-negative integer, got {raw!r}")
    if isinstance(raw, float) and not raw.is_integer():
        raise RuntimeError(f"adapter {identity}: {key} must be a non-negative integer, got {raw!r}")
    value = int(raw)
    if value < 0:
        raise RuntimeError(f"adapter {identity}: {key} must be a non-negative integer, got {raw!r}")
    return value


def _row_from_result(
    cb: Any,
    identity: str,
    spec: dict[str, Any],
    exchange: dict[str, Any],
    result: dict[str, Any],
    *,
    receiver_state: str,
    decoder_mode: str,
    symbolic_examples: bool,
    payload: dict[str, Any],
) -> dict[str, Any]:
    success = result.get("task_success")
    if success is None:
        raise RuntimeError(f"adapter {identity} did not report task_success")
    provider_cost = _finite_float(
        result.get("provider_cost_usd", 0.0), identity, "provider_cost_usd", minimum=0.0
    )
    infrastructure_cost = _finite_float(
        result.get("infrastructure_cost_usd", 0.0), identity, "infrastructure_cost_usd", minimum=0.0
    )
    retrieval_cost = _finite_float(
        result.get("retrieval_cost_usd", 0.0), identity, "retrieval_cost_usd", minimum=0.0
    )
    retry_cost = _finite_float(
        result.get("retry_cost_usd", 0.0), identity, "retry_cost_usd", minimum=0.0
    )
    if "cost_usd" in result:
        total_cost = _finite_float(result["cost_usd"], identity, "cost_usd", minimum=0.0)
    else:
        total_cost = provider_cost + infrastructure_cost + retrieval_cost + retry_cost
    if not math.isfinite(total_cost):
        raise RuntimeError(f"adapter {identity}: cost_usd must be finite, got {total_cost!r}")
    adapter_tokens = _non_negative_int(result.get("input_tokens", 0), identity, "input_tokens")
    expansion_tokens = cb._estimate_tokens(payload["model_facing_text"]) if decoder_mode == "decoder-assisted" else 0
    return {
        "variant": exchange["variant"],
        "variant_name": exchange["variant_name"],
        "turn": exchange["turn"],
        "phase": exchange["phase"],
        "receiver_model": identity,
        "model_family": spec["family"],
        "model_version": spec["version"],
        "codebook_version": spec.get("codebook_version", DEFAULT_CODEBOOK_VERSION),
        "decoder_configuration": DECODER_LABELS[decoder_mode],
        "symbolic_examples": bool(symbolic_examples),
        "receiver_state": receiver_state,
        "receiver_prior": payload["receiver_prior"],
        "wire_bytes": exchange["wire_bytes"],
        "adapter_input_tokens": adapter_tokens,
        "expansion_tokens": expansion_tokens,
        "input_tokens": adapter_tokens + expansion_tokens,
        "output_tokens": _non_negative_int(result.get("output_tokens", 0), identity, "output_tokens"),
        "provider_cost_usd": provider_cost,
        "infrastructure_cost_usd": infrastructure_cost,
        "retrieval_cost_usd": retrieval_cost,
        "retry_cost_usd": retry_cost,
        "cost_usd": total_cost,
        "retrievals": _non_negative_int(result.get("retrievals", 0), identity, "retrievals"),
        "tool_calls": _non_negative_int(result.get("tool_calls", 0), identity, "tool_calls"),
        "retries": _non_negative_int(result.get("retries", 0), identity, "retries"),
        "semantic_loss": _finite_float(result.get("semantic_loss", 0.0), identity, "semantic_loss"),
        "task_success": _finite_float(success, identity, "task_success", minimum=0.0, maximum=1.0),
        "critical_fact_recall": _critical_fact_recall(cb, result, exchange, identity),
        "latency_ms": _finite_float(result.get("latency_ms", 0.0), identity, "latency_ms", minimum=0.0),
    }


def _score_sealed_response(
    cb: Any, exchange: dict[str, Any], task_response: Any, identity: str
) -> tuple[float, float]:
    """Deterministic harness-side scoring of the adapter's sealed answer.

    In sealed mode the adapter reports NO score: ``task_success`` and
    ``critical_fact_recall`` are computed by the harness from the adapter's
    ``task_response`` text alone (the model boundary never sees the answer
    key).  The per-turn ratios come from ``cb.evaluate_turn`` semantics --
    qa fields including the CHANGE_MARKERS ``what_changed`` question,
    state fields, action -- and ``critical_fact_recall`` is
    ``cb.fidelity_critical`` on the text.  A non-empty-string ``task_response``
    is required (adapter-naming RuntimeError otherwise -- never fabricated).

    Turn 0 (the shared-context exchange) has no change markers, so it is
    scored with the same qa computation and ``what_changed: False`` -- a
    deterministic miss against the ground-truth key, never a fabricated
    pass.
    """
    if not isinstance(task_response, str) or not task_response.strip():
        raise RuntimeError(
            f"adapter {identity}: sealed task_response must be a non-empty string"
        )
    if len(task_response) > MAX_TASK_RESPONSE_CHARS:
        raise RuntimeError(
            f"adapter {identity}: sealed task_response exceeds "
            f"{MAX_TASK_RESPONSE_CHARS} characters (got {len(task_response)})"
        )
    turn_index = exchange["turn"]
    predicted = cb.read_state(task_response)
    if turn_index in cb.CHANGE_MARKERS:
        per_turn = cb.evaluate_turn(predicted, task_response, turn_index)
    else:
        ground = cb.ground_truth_answers(turn_index)
        qa = {
            "is_deployment_allowed": cb._yes_no(predicted["deployment_allowed"]),
            "blocker": predicted["blocker"],
            "next_team": cb.next_team(predicted["blocker"]),
            "migration_approved": cb._yes_no(predicted["migration_approved"]),
            "what_changed": False,
        }
        per_turn = {
            "qa_correct": sum(1 for key in ground["qa"] if qa[key] == ground["qa"][key]),
            "qa_total": len(ground["qa"]),
            "state_correct": sum(
                1 for field in cb._STATE_FIELDS if predicted[field] == ground["state"][field]
            ),
            "state_total": len(cb._STATE_FIELDS),
            "action_correct": int(cb.action_for(qa["next_team"]) == ground["action"]),
        }
    task_success = statistics.mean(
        [
            per_turn["qa_correct"] / per_turn["qa_total"],
            per_turn["state_correct"] / per_turn["state_total"],
            per_turn["action_correct"],
        ]
    )
    critical_fact_recall = float(cb.fidelity_critical(task_response))
    return task_success, critical_fact_recall


def _row_from_sealed_result(
    cb: Any,
    identity: str,
    spec: dict[str, Any],
    exchange: dict[str, Any],
    result: dict[str, Any],
    *,
    receiver_state: str,
    decoder_mode: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Sealed-mode result row: harness scores are authoritative.

    Mirrors ``_row_from_result`` (the ``_finite_float``/``_non_negative_int``
    validators are reused) but the adapter-reported ``task_success`` and
    ``critical_fact_recall`` are IGNORED -- the row's scores come from
    ``_score_sealed_response`` on the adapter's ``task_response`` text.
    Adds ``sealed: True``, the raw ``task_response`` and the exchange's
    deterministic ``mechanism_used`` (stage 4: every sealed exchange carries
    it -- ``\"none\"`` only as a defensive fallback for an exchange that
    somehow lacks the key); ``receiver_prior`` is deliberately absent (a leak
    field the sealed payload never carries).
    """
    task_response = result.get("task_response")
    task_success, critical_fact_recall = _score_sealed_response(
        cb, exchange, task_response, identity
    )
    provider_cost = _finite_float(
        result.get("provider_cost_usd", 0.0), identity, "provider_cost_usd", minimum=0.0
    )
    infrastructure_cost = _finite_float(
        result.get("infrastructure_cost_usd", 0.0), identity, "infrastructure_cost_usd", minimum=0.0
    )
    retrieval_cost = _finite_float(
        result.get("retrieval_cost_usd", 0.0), identity, "retrieval_cost_usd", minimum=0.0
    )
    retry_cost = _finite_float(
        result.get("retry_cost_usd", 0.0), identity, "retry_cost_usd", minimum=0.0
    )
    if "cost_usd" in result:
        total_cost = _finite_float(result["cost_usd"], identity, "cost_usd", minimum=0.0)
    else:
        total_cost = provider_cost + infrastructure_cost + retrieval_cost + retry_cost
    if not math.isfinite(total_cost):
        raise RuntimeError(f"adapter {identity}: cost_usd must be finite, got {total_cost!r}")
    adapter_tokens = _non_negative_int(result.get("input_tokens", 0), identity, "input_tokens")
    expansion_tokens = (
        cb._estimate_tokens(payload["model_facing_packet"])
        if decoder_mode == "decoder-assisted"
        else 0
    )
    return {
        "variant": exchange["variant"],
        "variant_name": exchange["variant_name"],
        "turn": exchange["turn"],
        "phase": exchange["phase"],
        "receiver_model": identity,
        "model_family": spec["family"],
        "model_version": spec["version"],
        "codebook_version": spec.get("codebook_version", DEFAULT_CODEBOOK_VERSION),
        "decoder_configuration": DECODER_LABELS[decoder_mode],
        "symbolic_examples": False,
        "receiver_state": receiver_state,
        "sealed": True,
        "mechanism_used": exchange.get("mechanism_used", "none"),
        "task_response": task_response,
        "wire_bytes": exchange["wire_bytes"],
        "adapter_input_tokens": adapter_tokens,
        "expansion_tokens": expansion_tokens,
        "input_tokens": adapter_tokens + expansion_tokens,
        "output_tokens": _non_negative_int(result.get("output_tokens", 0), identity, "output_tokens"),
        "provider_cost_usd": provider_cost,
        "infrastructure_cost_usd": infrastructure_cost,
        "retrieval_cost_usd": retrieval_cost,
        "retry_cost_usd": retry_cost,
        "cost_usd": total_cost,
        "retrievals": _non_negative_int(result.get("retrievals", 0), identity, "retrievals"),
        "tool_calls": _non_negative_int(result.get("tool_calls", 0), identity, "tool_calls"),
        "retries": _non_negative_int(result.get("retries", 0), identity, "retries"),
        "semantic_loss": _finite_float(result.get("semantic_loss", 0.0), identity, "semantic_loss"),
        "task_success": task_success,
        "critical_fact_recall": critical_fact_recall,
        "latency_ms": _finite_float(result.get("latency_ms", 0.0), identity, "latency_ms", minimum=0.0),
    }


def _row_codebook_mode(row: dict[str, Any]) -> str:
    """Grouping discriminator for the two SAGE codebook modes.

    ``"true"`` for oracle-codebook rows, ``"false"`` for frozen-codebook
    (and plain held-out) rows, ``"default"`` when the row carries no
    ``oracle_codebook`` label (standard scenario) -- the mode is uniform per
    run, so the oracle and frozen rows of the same SAGE variant never merge
    and default-OFF grouping stays byte-identical to the stage-1/2 shape.
    """
    if row.get("oracle_codebook") is True:
        return "true"
    if row.get("oracle_codebook") is False:
        return "false"
    return "default"


def _aggregate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One RFC-table row per (variant, codebook mode, receiver, cold/warm)."""
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[
            (row["variant"], _row_codebook_mode(row), row["receiver_model"], row["receiver_state"])
        ].append(row)
    table_rows: list[dict[str, Any]] = []
    for key in sorted(grouped):
        items = sorted(grouped[key], key=lambda item: item["turn"])
        first = items[0]
        table_row = {
            "variant_cell": (
                f"{first['variant']} {first['variant_name']} [{first['receiver_model']}] {first['receiver_state']}"
            ),
            "variant": first["variant"],
            "variant_name": first["variant_name"],
            "receiver_model": first["receiver_model"],
            "model_family": first["model_family"],
            "model_version": first["model_version"],
            "codebook_version": first["codebook_version"],
            "decoder_configuration": first["decoder_configuration"],
            "symbolic_examples": first["symbolic_examples"],
            "receiver_state": first["receiver_state"],
            "wire_bytes": sum(item["wire_bytes"] for item in items),
            "input_tokens": sum(item["input_tokens"] for item in items),
            "output_tokens": sum(item["output_tokens"] for item in items),
            "cost_usd": round(sum(item["cost_usd"] for item in items), 6),
            "task_accuracy": round(statistics.mean(item["task_success"] for item in items), 6),
            "critical_fact_recall": items[-1]["critical_fact_recall"],
        }
        if "oracle_codebook" in first:
            # Held-out mode only: keep the codebook-mode label on the table row
            # so delta grouping (and consumers) can tell the two SAGE modes
            # apart.  Default-OFF table rows carry no such key (byte-identical
            # to the stage-1/2 shape).
            table_row["oracle_codebook"] = first["oracle_codebook"]
        table_rows.append(table_row)
    return table_rows


def _warm_vs_cold_deltas(table_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Warm-minus-cold deltas per (variant, codebook mode, receiver) pair."""
    by_pair: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in table_rows:
        by_pair[(row["variant"], _row_codebook_mode(row), row["receiver_model"])][
            row["receiver_state"]
        ] = row
    deltas: list[dict[str, Any]] = []
    for (variant_id, _mode, receiver) in sorted(by_pair):
        pair = by_pair[(variant_id, _mode, receiver)]
        if "cold" not in pair or "warm" not in pair:
            continue
        cold, warm = pair["cold"], pair["warm"]
        deltas.append(
            {
                "variant": variant_id,
                "variant_name": cold["variant_name"],
                "receiver_model": receiver,
                "wire_bytes_delta": warm["wire_bytes"] - cold["wire_bytes"],
                "input_tokens_delta": warm["input_tokens"] - cold["input_tokens"],
                "cost_usd_delta": round(warm["cost_usd"] - cold["cost_usd"], 6),
                "task_accuracy_delta": round(warm["task_accuracy"] - cold["task_accuracy"], 6),
                "critical_fact_recall_delta": round(
                    warm["critical_fact_recall"] - cold["critical_fact_recall"], 6
                ),
            }
        )
    return deltas


def _format_markdown_table(table_rows: list[dict[str, Any]]) -> str:
    """The RFC's public six-column markdown result table."""
    lines = [RFC_TABLE_HEADER, RFC_TABLE_SEPARATOR]
    for row in table_rows:
        lines.append(
            f"| {row['variant_cell']} | {row['wire_bytes']} | {row['input_tokens']} | "
            f"${row['cost_usd']:.4f} | {round(row['task_accuracy'] * 100)}% | "
            f"{round(row['critical_fact_recall'] * 100)}% |"
        )
    return "\n".join(lines)


def _format_delta_table(deltas: list[dict[str, Any]]) -> str:
    header = "| Variant | Receiver | Wire bytes d | Input tokens d | Cost d | Task accuracy d | Critical recall d |"
    separator = "| --- | --- | --: | --: | --: | --: | --: |"
    lines = [header, separator]
    for delta in deltas:
        lines.append(
            f"| {delta['variant']} {delta['variant_name']} | {delta['receiver_model']} | "
            f"{delta['wire_bytes_delta']:+d} | {delta['input_tokens_delta']:+d} | "
            f"${delta['cost_usd_delta']:+.4f} | {round(delta['task_accuracy_delta'] * 100):+d}% | "
            f"{round(delta['critical_fact_recall_delta'] * 100):+d}% |"
        )
    return "\n".join(lines)


def _urls_point_at_same_database(engine_url: Any, env_url: str) -> bool:
    """True when the two database URLs target the same database.

    SQLite file paths are resolved so equivalent spellings (absolute vs
    relative, symlinked) compare equal; non-sqlite URLs compare by their
    normalized rendering.
    """
    try:
        from sqlalchemy.engine import make_url

        engine_parsed = make_url(str(engine_url))
        env_parsed = make_url(env_url)
    except Exception:
        return str(engine_url) == env_url
    if engine_parsed.drivername != env_parsed.drivername:
        return False
    if engine_parsed.drivername == "sqlite":
        engine_db, env_db = engine_parsed.database, env_parsed.database
        if engine_db is None or env_db is None:
            return engine_db == env_db
        if engine_db == ":memory:" or env_db == ":memory:":
            return engine_db == env_db
        try:
            return Path(engine_db).resolve() == Path(env_db).resolve()
        except OSError:
            return engine_db == env_db
    return str(engine_parsed) == str(env_parsed)


def _prebound_sage_plugin_conflict() -> str | None:
    """Describe a ``sage_plugin.db`` engine that cannot be rebound, else None.

    ``sage_plugin.db`` creates its module-level engine at import time; if it
    is already imported and bound to a database other than the one
    ``SAGE_DATABASE_URL`` names, resetting the schema would hit the pre-bound
    database (data loss), so the harness must refuse instead.
    """
    db_module = sys.modules.get("aifence.bus.db")
    if db_module is None:
        return None
    engine = getattr(db_module, "engine", None)
    if engine is None:
        return None
    engine_url = getattr(engine, "url", None)
    if engine_url is None:
        return None
    env_url = os.environ.get("SAGE_DATABASE_URL", "").strip()
    if _urls_point_at_same_database(engine_url, env_url):
        return None
    return (
        "aifence.bus.db is already imported and its engine is bound to "
        f"{engine_url!r}, which differs from SAGE_DATABASE_URL ({env_url!r}); "
        "the module-level engine cannot be rebound in this process, so the "
        "harness refuses to run (a schema reset would otherwise hit the "
        "pre-bound database). Run in a fresh process or set SAGE_DATABASE_URL "
        "before the first sage_plugin import."
    )


def _record_feedback_for_packets(
    db: Any,
    settings: Any,
    packets: list[tuple[int, str]],
    task_success: float,
) -> dict[str, Any]:
    """Record measured task success against pinned audit rows (issue #16,
    stage 4 -- the RFC "learned semantic shorthand" feedback loop).

    Mirrors ``runtime.feedback`` semantics exactly: ``task_success`` must be
    in ``[0, 1]`` (``ValueError`` otherwise, validated BEFORE any lookup),
    an unknown ``packet_id`` raises ``KeyError``, and the decisions consumed
    by ``PatternStore.record_feedback`` come from the ``MessageAudit`` row
    the real encode created.  Returns a per-packet + merged per-pattern
    before/after summary (status, ``task_utility``, ``utility_score``) --
    additive JSON only, never a change to any existing field.

    ``packets`` is a list of ``(turn, packet_id)`` pairs for one SAGE variant.

    NOTE (cumulative semantics): each packet's ``patterns_updated`` field is
    CUMULATIVE -- ``len(merged)`` across all packets processed so far for
    this variant (``merged`` accumulates outside the packet loop), NOT a
    per-packet count.  The variant-level ``patterns_updated`` list in the
    returned summary is the authoritative merged per-pattern before/after
    view.
    """
    if not 0.0 <= task_success <= 1.0:
        raise ValueError("task_success must be in [0, 1]")
    from sqlalchemy import select

    from aifence.bus.db_models import MessageAudit
    from aifence.bus.patterns import PatternStore

    store = PatternStore(db, settings)
    packets_summary: list[dict[str, Any]] = []
    merged: dict[str, dict[str, Any]] = {}
    for turn, packet_id in packets:
        audit = db.scalar(select(MessageAudit).where(MessageAudit.packet_id == packet_id))
        if audit is None:
            raise KeyError(packet_id)
        touched_ids = sorted(
            {decision.get("pattern_id") for decision in audit.decisions if isinstance(decision.get("pattern_id"), str)}
        )
        before: dict[str, dict[str, Any]] = {}
        for pattern_id in touched_ids:
            pattern = store.get(pattern_id)
            if pattern is not None:
                before[pattern_id] = {
                    "status": pattern.status,
                    "task_utility": pattern.task_utility,
                    "utility_score": store.utility_score(pattern),
                }
        updated = store.record_feedback(audit.decisions, task_success)
        after: dict[str, dict[str, Any]] = {}
        for pattern in updated:
            after[pattern.pattern_id] = {
                "status": pattern.status,
                "task_utility": pattern.task_utility,
                "utility_score": store.utility_score(pattern),
            }
        for pattern_id in sorted(set(before) | set(after)):
            merged[pattern_id] = {
                "pattern_id": pattern_id,
                "status_before": before.get(pattern_id, {}).get("status"),
                "status_after": after.get(pattern_id, {}).get("status"),
                "task_utility_before": before.get(pattern_id, {}).get("task_utility"),
                "task_utility_after": after.get(pattern_id, {}).get("task_utility"),
                "utility_score_before": before.get(pattern_id, {}).get("utility_score"),
                "utility_score_after": after.get(pattern_id, {}).get("utility_score"),
            }
        packets_summary.append(
            {
                "packet_id": packet_id,
                "turn": turn,
                "decisions": len(audit.decisions),
                "patterns_updated": len(merged),
            }
        )
    return {
        "task_success": task_success,
        "packets": packets_summary,
        "patterns_updated": [merged[pattern_id] for pattern_id in sorted(merged)],
    }


def _record_benchmark_feedback(cb: Any, selected: list[str], rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Record each selected SAGE variant's measured task success into the
    codec's pattern store (issue #16, stage 4).

    For every selected SAGE variant (v09-v12) the variant's six exchanges
    are re-encoded into the scratch database through the REAL codec with the
    benchmark's pinned packet ids (deterministic, exactly like the
    benchmark's own ``_run_sage_variant``), so the ``MessageAudit`` rows the
    real encodes created exist; each packet's decisions are then recorded
    with the variant's measured task success -- the mean of the
    adapter-reported ``task_success`` values for that variant's rows -- via
    ``_record_feedback_for_packets`` (``runtime.feedback`` semantics).

    This is post-hoc DB bookkeeping: the wire bytes reported in the artifact
    come from the benchmark's recorded turn data, never from this re-encode,
    so the SAGE variants' wire bytes are byte-identical with or without the
    flag.  The returned summary is additive JSON (a top-level ``feedback``
    key) and never alters existing row fields or the RFC table.
    """
    from aifence.bus import db as db_module
    from aifence.bus.config import Settings
    from aifence.bus.db import SessionLocal

    db_module.init_db()
    sage_specs = {spec["id"]: spec for spec in cb._sage_specs()}
    rows_by_variant: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_variant[row["variant"]].append(row)
    variants: list[dict[str, Any]] = []
    for variant_id in sorted(set(selected) & set(sage_specs)):
        variant_rows = rows_by_variant.get(variant_id)
        if not variant_rows:
            continue
        task_success = statistics.mean(row["task_success"] for row in variant_rows)
        spec = sage_specs[variant_id]
        settings = Settings(
            auth_required=False,
            database_url=os.environ.get("SAGE_DATABASE_URL", "sqlite://"),
            context_accounting_enabled=True,
            learning_mode="managed",
            **spec.get("settings", {}),
        )
        # Real encodes -> MessageAudit rows for this variant (schema reset per
        # variant, exactly like the benchmark's own run loop).
        cb._run_sage_variant(spec)
        packets = [
            (turn, "P" + hashlib.sha256(f"{variant_id}:{turn}".encode()).hexdigest()[:32])
            for turn in range(6)
        ]
        with SessionLocal() as db:
            summary = _record_feedback_for_packets(db, settings, packets, task_success)
            db.commit()
        summary["variant"] = variant_id
        summary["variant_name"] = spec["name"]
        variants.append(summary)
    return {
        "recorded": True,
        "note": (
            "measured downstream task success recorded into the codec's pattern store via "
            "PatternStore.record_feedback (runtime.feedback semantics); post-hoc DB bookkeeping "
            "-- zero wire-byte change"
        ),
        "variants": variants,
    }


def run_harness(
    adapters: dict[str, Any],
    *,
    decoder_mode: str = "direct-symbolic",
    symbolic_examples: bool = False,
    variants: list[str] | None = None,
    timeout: float = 120.0,
    record_feedback: bool = False,
    sealed: bool = False,
    held_out: bool = False,
) -> dict[str, Any]:
    """Run the model evaluation harness end-to-end and return the full results.

    Requires ``SAGE_DATABASE_URL`` to be set to a writable scratch database
    path (the harness refuses to run against the ambient default ``~/sage.db``;
    the CLI ``main()`` sets it up automatically).  If ``sage_plugin.db`` is
    already imported with an engine bound to a different database than
    ``SAGE_DATABASE_URL``, refuses with ``RuntimeError`` (the module-level
    engine cannot be rebound in this process).

    With ``sealed=True`` (issue #22, stage 1) the adapter boundary is split:
    payloads are built by ``_build_sealed_payload`` (identity fields + task /
    model_facing_packet / allowed_decoder_metadata only) and rows by
    ``_row_from_sealed_result`` (harness-scored; ``symbolic_examples`` is
    forced False regardless of the parameter).  The results dict gains a
    top-level ``evaluation_boundary: "sealed"`` key; default OFF keeps every
    artifact byte-identical to the stage-3/4 shape (no such key).

    With ``held_out=True`` (issue #22, stage 3 -- REQUIRES ``sealed=True``;
    a ``ValueError`` otherwise) the scenario globals of the loaded benchmark
    module are patched from ``scripts/heldout_scenario.py`` BEFORE the
    benchmark/specs/scoring read them, the SAGE variants run in BOTH
    explicitly-labeled codebook modes (``oracle_codebook: true`` -- the
    benchmark-recorded upper bound over the held-out material -- and
    ``oracle_codebook: false`` -- the FROZEN establishment-only codebook,
    re-encoded for real; see the module docstring's held-out section), every
    row carries an ``oracle_codebook`` label, and the results dict gains
    top-level ``dataset_split: "held_out"`` + ``oracle_codebook`` keys.
    ``held_out`` cannot be combined with ``record_feedback`` (a
    ``ValueError``): feedback-loop semantics are defined against the standard
    scenario; held-out feedback is a future refinement.  Default OFF keeps
    every artifact byte-identical to the stage-1/2 sealed shape.

    Raises ``ValueError`` for invalid configuration (including configs with
    fewer than 2 distinct model families) and ``RuntimeError`` for adapter
    failures or a missing ``SAGE_DATABASE_URL`` -- results are never
    fabricated.
    """
    if held_out and not sealed:
        raise ValueError(
            "held_out requires sealed=True (--held-out must be combined with --sealed): "
            "the frozen-codebook split is a sealed-boundary evaluation"
        )
    if held_out and record_feedback:
        raise ValueError(
            "held_out cannot be combined with record_feedback: feedback-loop semantics "
            "are defined against the standard scenario; held-out feedback is a future "
            "refinement"
        )
    if not os.environ.get("SAGE_DATABASE_URL", "").strip():
        raise RuntimeError(
            "SAGE_DATABASE_URL is not set; set it to a writable scratch database "
            "path (e.g. sqlite:///<scratch>/sage_bench.db) before running the "
            "harness -- refusing to touch the ambient default database (~/sage.db)"
        )
    conflict = _prebound_sage_plugin_conflict()
    if conflict is not None:
        raise RuntimeError(conflict)
    validate_adapters(adapters)
    if decoder_mode not in DECODER_MODES:
        raise ValueError(f"decoder_mode must be one of {DECODER_MODES}")
    cb = _load_compression_benchmark()
    # Patch the scenario globals BEFORE anything reads them: the spec builders
    # (_plain_specs/_sage_specs), run_benchmark's records, ground_truth_answers
    # / evaluate_turn and the sealed scorer all resolve SHARED_CONTEXT /
    # UPDATES / STATE_DICTS / CHANGE_MARKERS at call time.
    frozen_codebook = _apply_scenario(cb, held_out=held_out)
    benchmark = cb.run_benchmark(out_dir=None)
    selected = variants if variants is not None else list(_ALL_VARIANT_IDS)
    known = {row["variant_id"] for row in benchmark["variants"]}
    for variant_id in selected:
        if variant_id not in known:
            raise ValueError(f"unknown variant id {variant_id!r}; expected one of {sorted(known)}")
    exchanges = _build_exchanges(cb, benchmark, selected, held_out=held_out)
    if held_out:
        # _apply_scenario returns the frozen establishment canonicals exactly
        # when held_out is true (and None otherwise).
        assert frozen_codebook is not None
        exchanges.extend(_build_frozen_exchanges(cb, selected, frozen_codebook))

    # Stage-4 sealed mechanics (ADDITIVE -- issue #22, stage 4): every sealed
    # COLD exchange carries its deterministic mechanism attribution
    # (``_attach_sealed_mechanisms``; the render functions already emit
    # ``mechanism_used`` per turn, the frozen exchanges carry it from
    # ``_build_frozen_exchanges``), and the sealed WARM exchanges are
    # lifecycle-primed re-encodes (``_build_warm_exchanges``: establishment
    # encode -> ACK -> VERIFIED knowledge commit -> per-turn encode with
    # ``use_receiver_knowledge=True`` -- the real primed lifecycle, never a
    # fabricated wire delta; see the module docstring's stage-4 section).
    # Unsealed runs keep the stage-3 shape: the warm loop reuses the cold
    # exchange list and only the ``receiver_state`` label differs.
    warm_exchanges: list[dict[str, Any]] | None = None
    if sealed:
        _attach_sealed_mechanisms(cb, exchanges)
        warm_exchanges = _build_warm_exchanges(cb, exchanges, frozen_codebook=frozen_codebook)

    # In sealed mode examples are evaluator-side decoder knowledge: the
    # payload contract pins symbolic_examples to False (and --with-examples
    # is rejected by main()); run_harness forces it here too.
    examples = False if sealed else bool(symbolic_examples)

    rows: list[dict[str, Any]] = []
    for identity, spec in sorted(adapters.items()):
        for receiver_state in ("cold", "warm"):
            # Sealed warm rows consume the lifecycle-primed warm exchange
            # list (mirror of the cold loop with receiver_state="warm"); every
            # other combination reuses the cold exchange list.
            exchange_list = exchanges
            if sealed and receiver_state == "warm":
                assert warm_exchanges is not None  # built above when sealed
                exchange_list = warm_exchanges
            for exchange in exchange_list:
                if sealed:
                    payload = _build_sealed_payload(
                        cb, exchange, receiver_state, decoder_mode, spec
                    )
                else:
                    payload = _build_payload(cb, exchange, receiver_state, decoder_mode, examples)
                result = _invoke(spec["command"], payload, timeout, identity)
                if sealed:
                    row = _row_from_sealed_result(
                        cb,
                        identity,
                        spec,
                        exchange,
                        result,
                        receiver_state=receiver_state,
                        decoder_mode=decoder_mode,
                        payload=payload,
                    )
                else:
                    row = _row_from_result(
                        cb,
                        identity,
                        spec,
                        exchange,
                        result,
                        receiver_state=receiver_state,
                        decoder_mode=decoder_mode,
                        symbolic_examples=examples,
                        payload=payload,
                    )
                if held_out:
                    # Every held-out row is labeled with its codebook mode:
                    # True for the oracle SAGE rows (upper bound), False for
                    # the frozen SAGE rows and the plain variants (no codebook
                    # mode).  Absent entirely when --held-out is OFF.
                    row["oracle_codebook"] = exchange["oracle_codebook"]
                rows.append(row)
    table_rows = _aggregate_rows(rows)
    deltas = _warm_vs_cold_deltas(table_rows)
    markdown = _format_markdown_table(table_rows)
    markdown_full = markdown + ("\n\n" + _format_delta_table(deltas) if deltas else "")
    feedback = _record_benchmark_feedback(cb, selected, rows) if record_feedback else None
    results = {
        "schema": "sage.model_eval_harness.v1",
        "generated_at": cb.FIXED_TIMESTAMP,
        "scenario": benchmark["scenario"],
        "provider": {"configured": True, "env": PROVIDER_ENV},
        "decoder_mode": decoder_mode,
        "decoder_configuration": DECODER_LABELS[decoder_mode],
        "symbolic_examples": examples,
        "adapters": {
            identity: {
                key: spec[key] for key in ("family", "version", "codebook_version") if key in spec
            }
            for identity, spec in sorted(adapters.items())
        },
        "rows": rows,
        "table_rows": table_rows,
        "deltas": deltas,
        "markdown_table": markdown,
        "markdown": markdown_full,
    }
    if sealed:
        results["evaluation_boundary"] = "sealed"
        results["mechanism_summary"] = _mechanism_summary(rows)
    if held_out:
        sage_ids = {spec["id"] for spec in cb._sage_specs()}
        results["dataset_split"] = "held_out"
        results["oracle_codebook"] = {
            variant_id: ["frozen", "oracle"]
            for variant_id in sorted(set(selected) & sage_ids)
        }
    if feedback is not None:
        results["feedback"] = feedback
    return results


def _write_artifacts(out_dir: str | Path, results: dict[str, Any]) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    # Advisory only (no locking -- this is an opt-in benchmark tool): a
    # pre-existing artifact means a previous run -- possibly a CONCURRENT run
    # pointed at the same --output dir -- is about to be silently overwritten.
    if (out / "model_eval_harness.json").exists():
        print(
            "model evaluation harness: warning: overwriting existing artifacts "
            f"in {out} (concurrent runs with the same --output dir silently lose "
            "one run's results)",
            file=sys.stderr,
        )
    try:
        payload = (
            json.dumps(results, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
        )
    except ValueError as exc:
        raise RuntimeError(
            "adapter results contain non-finite numbers; refusing to write invalid RFC 8259 JSON"
        ) from exc
    (out / "model_eval_harness.json").write_text(payload)
    (out / "model_eval_harness.md").write_text(results["markdown"] + "\n")


def _positive_timeout(value: str) -> float:
    """argparse type: ``--timeout`` must be a positive, finite number of
    seconds (``nan``/``inf`` are rejected -- ``nan <= 0`` is False, so a bare
    ``<= 0`` check would let them through)."""
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError(f"--timeout must be a positive finite number, got {value!r}")
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Opt-in model evaluation harness (issue #16, stage 3): run the compression "
            "benchmark's receivers on >=2 model families via external-runtime adapters, "
            "cold vs warm, RFC public result table."
        )
    )
    parser.add_argument(
        "--adapters",
        type=Path,
        default=None,
        help="path to an adapters JSON config (model_identity -> family/version/command)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="directory for model_eval_harness.json/.md raw artifacts (outside the repo)",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_timeout,
        default=120.0,
        help="per-adapter-call timeout in seconds (must be > 0)",
    )
    parser.add_argument(
        "--decoder-mode",
        choices=DECODER_MODES,
        default="direct-symbolic",
        help="how the packet reaches the receiving model (RFC model-facing evaluation modes)",
    )
    parser.add_argument(
        "--with-examples",
        action="store_true",
        help="give the receivers a symbolic-format example packet + meaning (symbolic_examples=true)",
    )
    parser.add_argument(
        "--sealed",
        action="store_true",
        help=(
            "sealed model boundary (issue #22, stage 1): the adapter receives ONLY identity "
            "fields + task/model_facing_packet/allowed_decoder_metadata -- never uncompressed "
            "source content, answer keys, change markers, receiver prior or examples -- and "
            "reports only a task_response text; task_success/critical_fact_recall are scored "
            "deterministically by the harness"
        ),
    )
    parser.add_argument(
        "--held-out",
        action="store_true",
        help=(
            "held-out split (issue #22, stage 3; REQUIRES --sealed): evaluate the sealed "
            "harness against the unseen scripts/heldout_scenario.py fixture with the SAGE "
            "codebook FROZEN to the establishment material, running every SAGE variant in "
            "BOTH labeled modes -- oracle_codebook true (upper bound) and false (frozen "
            "re-encode); rows carry oracle_codebook labels and the artifact gains "
            "dataset_split/oracle_codebook keys.  Cannot be combined with --record-feedback."
        ),
    )
    parser.add_argument(
        "--variants",
        default=None,
        help="comma-separated variant ids to evaluate (default: all twelve; an empty value is an error)",
    )
    parser.add_argument(
        "--record-feedback",
        action="store_true",
        help=(
            "record each SAGE variant's measured task success into the codec's pattern store "
            "via PatternStore.record_feedback (runtime.feedback semantics; additive 'feedback' "
            "JSON summary key, zero wire-byte change).  Default OFF: artifacts are byte-identical "
            "to a run without the flag."
        ),
    )
    args = parser.parse_args(argv)

    if args.sealed and args.with_examples:
        print(
            "model evaluation harness: error: --sealed cannot be combined with "
            "--with-examples: example meanings are evaluator-side decoder knowledge",
            file=sys.stderr,
        )
        return 2

    if args.held_out and not args.sealed:
        print(
            "model evaluation harness: error: --held-out requires --sealed: the "
            "frozen-codebook split is a sealed-boundary evaluation",
            file=sys.stderr,
        )
        return 2

    if args.held_out and args.record_feedback:
        print(
            "model evaluation harness: error: --held-out cannot be combined with "
            "--record-feedback: feedback-loop semantics are defined against the standard "
            "scenario; held-out feedback is a future refinement",
            file=sys.stderr,
        )
        return 2

    if args.adapters is None or not provider_available():
        print(f"model evaluation harness: {NO_PROVIDER_NOTE}")
        return 0

    # Reject an --output path that exists as a FILE before anything runs (no
    # traceback, no wasted adapter calls).  The directory itself is only
    # created AFTER run_harness has succeeded, immediately before the
    # artifacts are written (see below), so NO validation or error path --
    # missing adapters, empty --variants, unknown variant id, adapter
    # failure -- leaves an empty output dir behind.
    output_dir: Path | None = None
    if args.output is not None:
        out: Path = args.output
        if out.exists() and not out.is_dir():
            print(
                "model evaluation harness: error: --output path exists and is not a directory",
                file=sys.stderr,
            )
            return 2
        output_dir = out

    try:
        adapters = load_adapters(args.adapters)
    except FileNotFoundError:
        print(
            f"model evaluation harness: error: no such adapters file: {args.adapters}",
            file=sys.stderr,
        )
        return 2
    except (ValueError, OSError) as exc:
        print(f"model evaluation harness: error: {exc}", file=sys.stderr)
        return 2

    variants: list[str] | None = None
    if args.variants is not None:
        segments = [item.strip() for item in args.variants.split(",")]
        if not any(segments):
            print(
                "model evaluation harness: error: --variants must name at least one variant id",
                file=sys.stderr,
            )
            return 2
        variants = [item for item in segments if item]

    # Bind a STABLE per-process scratch database BEFORE any sage_plugin import
    # (db.py creates the engine at import time).  The file lives in
    # ~/.sage-bench -- never in the --output dir -- and is never deleted
    # mid-process (the module-level engine may hold pooled connections to it);
    # it is removed at process exit via _cleanup_scratch_db.
    scratch_db = _scratch_db_path()
    scratch_db.parent.mkdir(parents=True, exist_ok=True)
    prior_db_url = os.environ.get("SAGE_DATABASE_URL")
    os.environ["SAGE_DATABASE_URL"] = f"sqlite:///{scratch_db}"
    try:
        results = run_harness(
            adapters,
            decoder_mode=args.decoder_mode,
            symbolic_examples=args.with_examples,
            variants=variants,
            timeout=args.timeout,
            record_feedback=args.record_feedback,
            sealed=args.sealed,
            held_out=args.held_out,
        )
    except ValueError as exc:
        print(f"model evaluation harness: error: {exc}", file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(f"model evaluation harness: error: {exc}", file=sys.stderr)
        return 1
    finally:
        if prior_db_url is None:
            os.environ.pop("SAGE_DATABASE_URL", None)
        else:
            os.environ["SAGE_DATABASE_URL"] = prior_db_url

    boundary = ", sealed boundary: yes" if args.sealed else ""
    split = ", held-out split: yes" if args.held_out else ""
    print(
        f"Model evaluation harness (issue #16, stage 3) -- decoder mode: {args.decoder_mode}, "
        f"symbolic examples: {args.with_examples}{boundary}{split}"
    )
    print(results["markdown_table"])
    if results["deltas"]:
        print()
        print(_format_delta_table(results["deltas"]))
    if output_dir is not None:
        # Create the output dir only now: run_harness has fully succeeded
        # (adapters loaded, --variants validated, every variant id known,
        # adapters ran without error), and this dir is only ever used by
        # _write_artifacts -- so every validation/error path above exits
        # without leaving an empty directory behind.
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            _write_artifacts(output_dir, results)
        except RuntimeError as exc:
            print(f"model evaluation harness: error: {exc}", file=sys.stderr)
            return 1
        print(f"\nArtifacts written to {output_dir}")
    if args.record_feedback:
        feedback = results.get("feedback")
        if feedback is not None:
            variants_note = ", ".join(
                f"{item['variant']} (patterns updated: {len(item['patterns_updated'])})"
                for item in feedback["variants"]
            )
            print(f"Feedback recorded (--record-feedback): {variants_note or 'no SAGE variants selected'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
