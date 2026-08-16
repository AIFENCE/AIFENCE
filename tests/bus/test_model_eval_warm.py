"""Regression tests for the lifecycle-primed warm receiver + mechanism
attribution (issue #22, stage 4).

Covers (issue #22, stage 4):

* PRIMING COMMITS KNOWLEDGE: before priming, the knowledge store for
  (bob, default) is empty; after the warm path primes a variant through the
  harness's OWN prime machinery (``_prime_receiver``), the store carries the
  probed knowledge per variant (v09 -> 5 known codes; v10 -> 1; v11 -> 1
  known ref + committed ``current_state``; v12 -> 6) -- probed in-process
  against the REAL codec, never assumed;
* WARM LIFECYCLE HONESTY: sealed warm rows exist with ``receiver_state:
  "warm"`` and are produced through the real primed lifecycle
  (``use_receiver_knowledge=True`` on the per-turn encodes after the
  establishment encode -> ACK -> verified knowledge commit); the primed
  re-encode is deterministic (two ``_render_warm_variant_packets`` calls
  return identical wire bytes); and -- the PROBED reality on this fixture,
  documented here so it is pinned, NOT assumed -- the warm wire bytes EQUAL
  the cold wire bytes: receiver knowledge is decoder-side (the wire whitelist
  strips ``receiver_known_code_count``, so primed knowledge changes the
  decoder's meta, not the wire), and on v11 turn 0 the primed
  ``current_state`` triggers the delta branch but ``reject_delta`` wins (a
  delta packet for the 131-144-byte state dict is larger than the reference
  packet).  The honest claim is therefore "the warm row IS the primed
  lifecycle measurement (verified priming, deterministic re-encode)" -- not
  "warm wire bytes differ from cold", which would be fabricated on this
  fixture;
* MECHANISM ATTRIBUTION: v09 rows ``mechanism_used == "codebook"`` (all
  turns); v10 turn 0 == ``"learned_pattern"`` (pattern atom fires), turns
  1-5 == ``"codebook"``; v11 turn 0 == ``"reference"``, turns 1-5 ==
  ``"state_delta"``; v12 == ``"codebook"`` (all turns) -- cross-checked
  against the rendered packet's own strategy/atoms/refs/base where cheap;
  the top-level ``mechanism_summary`` counts match the rows;
* DETERMINISM: two fresh ``--sealed`` CLI runs (cold AND warm rows) produce
  byte-identical printed tables and JSON artifacts modulo ``latency_ms``;
  same for two fresh ``--sealed --held-out`` runs (oracle AND frozen rows,
  both receiver states);
* OFF BYTE-IDENTITY: default-OFF artifacts carry no ``mechanism_used`` /
  ``mechanism_summary`` (identical shape to stage 3); sealed COLD rows are
  unchanged except the ADDITIVE ``mechanism_used`` key;
* VALIDATION: no-provider skip; ``--sealed`` + ``--with-examples`` exits 2
  cleanly; a priming failure raises a clean error through the real honesty
  gate (``_verify_primed_knowledge``) -- the warm path NEVER fabricates a
  warm benefit;
* HELD-OUT + WARM: ``--sealed --held-out`` runs end-to-end with warm rows in
  BOTH codebook modes (frozen AND oracle warm rows, each primed from its own
  codebook), with warm wire == cold wire per mode on this fixture;
* SCENARIO-GLOBAL RESTORE (hardening): in-process reuse of
  ``_apply_scenario`` (``held_out=True`` then ``held_out=False``) restores
  the benchmark module's PRISTINE globals, so a later default render is the
  phoenix shape, not held-out content;
* FROZEN-MODE MECHANISM VALUES (hardening): the frozen establishment-only
  codebook's ``mechanism_used`` per (variant, turn) is pinned (v09 t0
  ``codebook``, v09 t1-5 ``literal``; v11 ``reference``/``state_delta``;
  v12 all ``literal``).

All tests are deterministic (fixed inputs, no network, no real model) and
write their output directories under ``/opt/data/sage/scratch/`` -- never
``/tmp``.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
HARNESS_SCRIPT = ROOT / "scripts" / "model_eval_harness.py"
SCRATCH_ROOT = Path(os.environ.get("SAGE_SCRATCH_ROOT", "/opt/data/sage/scratch")) / "stage22-warm-tests"

#: SAGE variants whose sealed direct-symbolic packets are rendered for real.
SAGE_VARIANTS = ("v09", "v10", "v11", "v12")

#: Sealed fake adapter (mirrors the stage-1/3 tests): replies with a fixed
#: PHOENIX-flavored task_response + the sealed reply shape.  Never sees
#: SAGE_* env (the harness scrubs the child env); the "no-op trap" is the
#: provider env being set BEFORE the child envs in the subprocess runner.
FAKE_ADAPTER_SEALED = (
    "import json,sys; p=json.load(sys.stdin); "
    "print(json.dumps({'task_response': 'Project Phoenix is blocked because three integration tests failed.', "
    "'input_tokens': 7, 'output_tokens': 5, 'provider_cost_usd': 0.0012}))"
)

#: Unsealed fake adapter (mirrors test_model_eval_harness) -- for the
#: default-OFF byte-identity check.
FAKE_ADAPTER_OK = (
    "import json,sys; p=json.load(sys.stdin); "
    "print(json.dumps({'task_success': 1.0 if p.get('receiver_state') == 'warm' else 0.5, "
    "'input_tokens': 7, 'output_tokens': 5, 'provider_cost_usd': 0.0012, 'critical_fact_recall': 0.8}))"
)


def _load_harness() -> Any:
    spec = importlib.util.spec_from_file_location("model_eval_harness", HARNESS_SCRIPT)
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def h() -> Any:
    return _load_harness()


@pytest.fixture()
def scratch_dir() -> Iterator[Path]:
    """A scratch output directory under /opt/data/sage/scratch (never /tmp)."""
    path = SCRATCH_ROOT / uuid.uuid4().hex[:12]
    path.mkdir(parents=True, exist_ok=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def _sealed_adapters_config() -> dict[str, Any]:
    return {
        "acme-gpt-4o": {
            "family": "acme",
            "version": "gpt-4o-2026-05",
            "command": [sys.executable, "-c", FAKE_ADAPTER_SEALED],
        },
        "nebula-sonnet": {
            "family": "nebula",
            "version": "sonnet-2026-07",
            "command": [sys.executable, "-c", FAKE_ADAPTER_SEALED],
        },
    }


def _two_family_config() -> dict[str, Any]:
    return {
        "acme-gpt-4o": {
            "family": "acme",
            "version": "gpt-4o-2026-05",
            "command": [sys.executable, "-c", FAKE_ADAPTER_OK],
        },
        "nebula-sonnet": {
            "family": "nebula",
            "version": "sonnet-2026-07",
            "command": [sys.executable, "-c", FAKE_ADAPTER_OK],
        },
    }


def _run_cli_subprocess(argv: list[str], fake_home: Path) -> subprocess.CompletedProcess:
    """Run the harness CLI in a FRESH subprocess (fake HOME + provider env)."""
    env = {**os.environ, "HOME": str(fake_home), "SAGE_BENCH_LLM_PROVIDER": "fake"}
    env.pop("SAGE_DATABASE_URL", None)
    return subprocess.run(
        [sys.executable, str(HARNESS_SCRIPT), *argv],
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )


def _strip_latency(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_latency(item) for key, item in value.items() if "latency" not in key}
    if isinstance(value, list):
        return [_strip_latency(item) for item in value]
    return value


# ---------------------------------------------------------------------------
# PRIMING COMMITS KNOWLEDGE (probed in-process, real codec)
# ---------------------------------------------------------------------------


def test_priming_commits_knowledge(h, monkeypatch):
    """Before priming the (bob, default) store is EMPTY; after priming the
    warm path via the harness's own ``_prime_receiver``, the store carries the
    probed per-variant knowledge (v09 -> 5 codes; v11 -> 1 ref + current_state)."""
    from sqlalchemy import select

    from aifence.bus import db as db_module
    from aifence.bus.codec import SageCodec
    from aifence.bus.config import Settings
    from aifence.bus.db import SessionLocal
    from aifence.bus.db_models import LearnedPattern

    cb = h._load_compression_benchmark()
    expected = {
        "v09": (5, 0, False),
        "v10": (1, 0, False),
        "v11": (0, 1, True),
        "v12": (6, 0, True),
    }
    for variant_id, (want_codes, want_refs, want_state) in expected.items():
        spec = h._sage_variant_spec(cb, variant_id)
        db_module.init_db()
        cb._reset_schema(db_module)
        settings = Settings(
            auth_required=False,
            database_url=os.environ.get("SAGE_DATABASE_URL", "sqlite://"),
            context_accounting_enabled=True,
            learning_mode="managed",
            **spec.get("settings", {}),
        )
        with SessionLocal() as db:
            codec = SageCodec(db, settings)
            for canonical in spec["codebook"]:
                codec.codebook.register("global", canonical)
            db.commit()
            warmup = spec.get("warmup")
            if warmup is not None:
                cb._pin_packet_id(codec, spec["id"], "warmup")
                codec.encode(cb._sage_request(warmup, auto_learn=True, record_learning=True))
                pattern = db.scalar(select(LearnedPattern))
                if pattern is not None:
                    codec.patterns.set_status(pattern.pattern_id, "active")
                    db.commit()
            store = codec.knowledge
            # BEFORE: the (bob, default) knowledge store is empty
            assert store.get("bob", "default") is None
            assert store.known_codes("bob", "default") == []
            assert store.known_refs("bob", "default") == []
            # PRIME through the harness's own machinery (establ. encode ->
            # ACK -> verified knowledge commit; raises on failure)
            h._prime_receiver(codec, cb, spec)
            # AFTER: probed per-variant knowledge
            assert len(store.known_codes("bob", "default")) == want_codes, variant_id
            assert len(store.known_refs("bob", "default")) == want_refs, variant_id
            knowledge = store.get("bob", "default")
            assert knowledge is not None
            assert (knowledge.current_state is not None) == want_state, variant_id


def test_priming_failure_raises_clean_error(h, monkeypatch):
    """The honesty gate RAISES when priming committed none of what the
    establishment packet carried -- the warm path never fabricates a benefit."""
    from sqlalchemy import select

    from aifence.bus import db as db_module
    from aifence.bus.codec import SageCodec
    from aifence.bus.config import Settings
    from aifence.bus.db import SessionLocal
    from aifence.bus.db_models import LearnedPattern

    cb = h._load_compression_benchmark()
    spec = h._sage_variant_spec(cb, "v09")  # codebook variant: prime carries coded atoms
    db_module.init_db()
    cb._reset_schema(db_module)
    settings = Settings(
        auth_required=False,
        database_url=os.environ.get("SAGE_DATABASE_URL", "sqlite://"),
        context_accounting_enabled=True,
        learning_mode="managed",
        **spec.get("settings", {}),
    )
    with SessionLocal() as db:
        codec = SageCodec(db, settings)
        for canonical in spec["codebook"]:
            codec.codebook.register("global", canonical)
        db.commit()
        warmup = spec.get("warmup")
        if warmup is not None:
            cb._pin_packet_id(codec, spec["id"], "warmup")
            codec.encode(cb._sage_request(warmup, auto_learn=True, record_learning=True))
            pattern = db.scalar(select(LearnedPattern))
            if pattern is not None:
                codec.patterns.set_status(pattern.pattern_id, "active")
                db.commit()
        # Encode the establishment packet but NEVER ACK it: the store stays
        # empty, so the honesty gate must raise instead of fabricating a warm
        # benefit.
        cb._pin_packet_id(codec, spec["id"], "prime")
        prime_content = spec["content_fn"](0)
        prime_encoded = codec.encode(
            cb._sage_request(
                prime_content,
                use_receiver_knowledge=False,
                use_patterns=spec.get("patterns", True),
                base_state=None,
                inline_limit=spec.get("inline_limit"),
            )
        )
        store = codec.knowledge
        assert store.get("bob", "default") is None  # nothing committed
        with pytest.raises(RuntimeError, match="refusing to fabricate a warm benefit") as exc_info:
            h._verify_primed_knowledge(codec, spec, prime_content, prime_encoded.packet)
        assert "v09" in str(exc_info.value)


# ---------------------------------------------------------------------------
# WARM LIFECYCLE HONESTY + MECHANISM ATTRIBUTION (in-process, real lifecycle)
# ---------------------------------------------------------------------------


def test_warm_lifecycle_honesty_and_mechanism_attribution(h, monkeypatch):
    """Sealed warm rows come from the REAL primed lifecycle
    (``use_receiver_knowledge=True`` after the verified prime) and carry the
    probed per-variant mechanism attribution; on THIS fixture the warm wire
    bytes equal the cold ones (receiver knowledge is decoder-side --
    documented, asserted, not hidden)."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    results = h.run_harness(_sealed_adapters_config(), variants=list(SAGE_VARIANTS), sealed=True)
    rows = results["rows"]
    assert rows
    assert results["evaluation_boundary"] == "sealed"
    assert "mechanism_summary" in results

    cold = {(r["variant"], r["turn"], r["receiver_model"]): r for r in rows if r["receiver_state"] == "cold"}
    warm = {(r["variant"], r["turn"], r["receiver_model"]): r for r in rows if r["receiver_state"] == "warm"}
    assert cold and warm
    assert set(cold) == set(warm)  # every cold exchange has a primed warm twin

    # WARM LIFECYCLE HONESTY: the warm rows exist with receiver_state warm and
    # -- the probed reality on this fixture -- their wire bytes EQUAL the cold
    # ones (receiver knowledge is decoder-side; the wire whitelist strips
    # receiver_known_code_count; on v11 turn 0 reject_delta wins).  The honest
    # claim is the PRIMED lifecycle, not a wire delta.
    for key, warm_row in warm.items():
        assert warm_row["receiver_state"] == "warm"
        assert warm_row["sealed"] is True
        assert warm_row["wire_bytes"] == cold[key]["wire_bytes"], key
        assert warm_row["task_response"]  # scored by the harness

    # MECHANISM ATTRIBUTION per variant (probed, cross-checked below).
    expected_mechanisms = {
        "v09": {t: "codebook" for t in range(6)},
        "v10": {0: "learned_pattern", **{t: "codebook" for t in range(1, 6)}},
        "v11": {0: "reference", **{t: "state_delta" for t in range(1, 6)}},
        "v12": {t: "codebook" for t in range(6)},
    }
    cb = h._load_compression_benchmark()
    for variant_id in SAGE_VARIANTS:
        for turn in range(6):
            for receiver_model in ("acme-gpt-4o", "nebula-sonnet"):
                for state in ("cold", "warm"):
                    row = rows_by(rows, variant_id, turn, receiver_model, state)
                    assert row["mechanism_used"] == expected_mechanisms[variant_id][turn], (
                        variant_id, turn, receiver_model, state
                    )

    # top-level mechanism_summary counts the rows
    summary = results["mechanism_summary"]
    for variant_id in SAGE_VARIANTS:
        per_variant = [r for r in rows if r["variant"] == variant_id]
        counts: dict[str, int] = {}
        for r in per_variant:
            counts[r["mechanism_used"]] = counts.get(r["mechanism_used"], 0) + 1
        assert summary[variant_id] == counts, variant_id

    # CROSS-CHECK mechanism_used against the rendered packet's own
    # strategy/atoms/refs/base (cheap: strategy/delta/base/refs/atoms).
    for variant_id in SAGE_VARIANTS:
        spec = h._sage_variant_spec(cb, variant_id)
        for turn in range(6):
            rendered = json.loads(
                h._render_warm_variant_packets(cb, spec)[turn]["rendering"]
            )
            mech = expected_mechanisms[variant_id][turn]
            if mech == "reference":
                assert rendered.get("refs"), (variant_id, turn)
            elif mech == "state_delta":
                assert rendered.get("base"), (variant_id, turn)
            elif mech in ("codebook", "learned_pattern"):
                assert rendered.get("atoms"), (variant_id, turn)

    # PRIMED RE-ENCODE IS DETERMINISTIC: two calls -> identical wire bytes
    for variant_id in SAGE_VARIANTS:
        spec = h._sage_variant_spec(cb, variant_id)
        first = h._render_warm_variant_packets(cb, spec)
        second = h._render_warm_variant_packets(cb, spec)
        for turn in range(6):
            assert first[turn]["wire_bytes_json"] == second[turn]["wire_bytes_json"]
            assert first[turn]["rendering"] == second[turn]["rendering"]


def rows_by(rows: list[dict[str, Any]], variant: str, turn: int, receiver: str, state: str) -> dict[str, Any]:
    matches = [
        r
        for r in rows
        if r["variant"] == variant
        and r["turn"] == turn
        and r["receiver_model"] == receiver
        and r["receiver_state"] == state
    ]
    assert len(matches) == 1, (variant, turn, receiver, state, len(matches))
    return matches[0]


# ---------------------------------------------------------------------------
# CLI determinism (cold AND warm; oracle AND frozen held-out modes)
# ---------------------------------------------------------------------------


def test_sealed_warm_determinism_cli(scratch_dir):
    """Two fresh --sealed CLI runs (which produce BOTH cold and warm rows)
    are byte-identical modulo latency_ms."""
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_a = scratch_dir / "run-a"
    out_b = scratch_dir / "run-b"
    argv = ["--sealed", "--adapters", str(cfg), "--variants", "v09,v11"]
    run_a = _run_cli_subprocess([*argv, "--output", str(out_a)], fake_home)
    assert run_a.returncode == 0, run_a.stderr
    run_b = _run_cli_subprocess([*argv, "--output", str(out_b)], fake_home)
    assert run_b.returncode == 0, run_b.stderr

    def _printed_table(run: subprocess.CompletedProcess, out_dir: Path) -> str:
        return run.stdout.split(f"Artifacts written to {out_dir}")[0]

    assert _printed_table(run_a, out_a) == _printed_table(run_b, out_b)
    art_a = json.loads((out_a / "model_eval_harness.json").read_text())
    art_b = json.loads((out_b / "model_eval_harness.json").read_text())
    assert any("latency_ms" in row for row in art_a["rows"])
    assert _strip_latency(art_a) == _strip_latency(art_b)
    assert json.dumps(_strip_latency(art_a), sort_keys=True).encode() == json.dumps(
        _strip_latency(art_b), sort_keys=True
    ).encode()
    assert (out_a / "model_eval_harness.md").read_bytes() == (out_b / "model_eval_harness.md").read_bytes()
    # both runs carried warm rows with mechanism attribution
    for art in (art_a, art_b):
        assert any(r["receiver_state"] == "warm" for r in art["rows"])
        assert any("mechanism_used" in r for r in art["rows"])
        assert "mechanism_summary" in art


def test_heldout_warm_determinism_cli(scratch_dir):
    """Two fresh --sealed --held-out CLI runs (oracle AND frozen rows, cold AND
    warm) are byte-identical modulo latency_ms, and the warm rows work in BOTH
    codebook modes (frozen AND oracle warm rows primed from their own
    codebooks)."""
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_a = scratch_dir / "run-a"
    out_b = scratch_dir / "run-b"
    argv = ["--sealed", "--held-out", "--adapters", str(cfg), "--variants", "v09,v11"]
    run_a = _run_cli_subprocess([*argv, "--output", str(out_a)], fake_home)
    assert run_a.returncode == 0, run_a.stderr
    run_b = _run_cli_subprocess([*argv, "--output", str(out_b)], fake_home)
    assert run_b.returncode == 0, run_b.stderr

    def _printed_table(run: subprocess.CompletedProcess, out_dir: Path) -> str:
        return run.stdout.split(f"Artifacts written to {out_dir}")[0]

    assert _printed_table(run_a, out_a) == _printed_table(run_b, out_b)
    art_a = json.loads((out_a / "model_eval_harness.json").read_text())
    art_b = json.loads((out_b / "model_eval_harness.json").read_text())
    assert _strip_latency(art_a) == _strip_latency(art_b)
    assert (out_a / "model_eval_harness.md").read_bytes() == (out_b / "model_eval_harness.md").read_bytes()

    # held-out + warm end-to-end: warm rows exist in BOTH codebook modes
    for art in (art_a, art_b):
        assert art["dataset_split"] == "held_out"
        warm = [r for r in art["rows"] if r["receiver_state"] == "warm"]
        assert warm
        oracle_warm = [r for r in warm if r["oracle_codebook"] is True]
        frozen_warm = [r for r in warm if r["oracle_codebook"] is False]
        assert oracle_warm and frozen_warm
        # frozen AND oracle warm rows primed from their own codebooks: every
        # warm row's wire bytes equal its COLD TWIN's (same variant/turn/
        # receiver/mode) -- the probed decoder-side reality on this fixture
        cold_by_twin = {
            (r["oracle_codebook"], r["variant"], r["turn"], r["receiver_model"]): r["wire_bytes"]
            for r in art["rows"]
            if r["receiver_state"] == "cold"
        }
        for r in warm:
            assert r["wire_bytes"] == cold_by_twin[
                (r["oracle_codebook"], r["variant"], r["turn"], r["receiver_model"])
            ]
            assert "mechanism_used" in r


def test_apply_scenario_restores_globals_after_held_out(h):
    """F1 hardening: in-process reuse of _apply_scenario (held_out=True then
    held_out=False) must restore the benchmark module's PRISTINE scenario
    globals -- a subsequent default render is the PHOENIX shape, not held-out
    content (the default call used to leave the held-out patch behind)."""
    cb = h._load_compression_benchmark()
    pristine = {
        "SHARED_CONTEXT": cb.SHARED_CONTEXT,
        "UPDATES": cb.UPDATES,
        "STATE_DICTS": cb.STATE_DICTS,
        "CHANGE_MARKERS": cb.CHANGE_MARKERS,
    }
    # sanity: the freshly loaded module is the pristine phoenix fixture
    assert "Project Phoenix" in cb.SHARED_CONTEXT

    # held-out patch replaces the globals with the Orion fixture
    frozen_codebook = h._apply_scenario(cb, held_out=True)
    assert frozen_codebook is not None
    assert cb.SHARED_CONTEXT != pristine["SHARED_CONTEXT"]
    assert "Project Orion" in cb.SHARED_CONTEXT

    # a default call must restore the pristine globals byte-identically
    assert h._apply_scenario(cb, held_out=False) is None
    for name, expected in pristine.items():
        assert getattr(cb, name) == expected, name

    # a subsequent default render is the phoenix shape, not held-out content.
    # Clear the per-process caches first so the render genuinely re-reads the
    # RESTORED globals instead of serving a cache entry compiled earlier.
    h._SAGE_VARIANT_SPECS_CACHE.clear()
    h._PACKET_RENDER_CACHE.clear()
    h._WARM_PACKET_RENDER_CACHE.clear()
    h._FROZEN_PACKET_RENDER_CACHE.clear()
    spec = h._sage_variant_spec(cb, "v09")
    rendered = json.loads(h._render_sage_variant_packets(cb, spec)[0]["rendering"])
    text = json.dumps(rendered)
    assert "phoenix" in text
    assert "orion" not in text


def test_heldout_frozen_mode_mechanism_values(h, monkeypatch):
    """FROZEN-codebook mechanism_used values are pinned (the standard-scenario
    mapping is fully pinned; this closes the reviewer's coverage note for the
    frozen mode): the establishment-only frozen codebook renders v09 t0 as
    ``codebook`` and the unseen held-out turns as ``literal``, v11 keeps its
    reference/state_delta design, v12 is all-literal (the frozen text-clause
    codebook never codes the held-out state-field updates)."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    results = h.run_harness(
        _sealed_adapters_config(), variants=["v09", "v11", "v12"], sealed=True, held_out=True
    )
    frozen = [r for r in results["rows"] if r["oracle_codebook"] is False]
    assert frozen
    expected = {
        "v09": {0: "codebook", **{t: "literal" for t in range(1, 6)}},
        "v11": {0: "reference", **{t: "state_delta" for t in range(1, 6)}},
        "v12": {t: "literal" for t in range(6)},
    }
    for row in frozen:
        assert row["mechanism_used"] == expected[row["variant"]][row["turn"]], (
            row["variant"], row["turn"], row["receiver_state"], row["mechanism_used"]
        )


# ---------------------------------------------------------------------------
# OFF byte-identity (default-OFF vs stage-3 shape; sealed cold + additive key)
# ---------------------------------------------------------------------------


def test_off_byte_identity_default_off(h, monkeypatch):
    """Default-OFF artifacts carry NO mechanism_used / mechanism_summary keys
    (identical shape to stage 3)."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    results = h.run_harness(_two_family_config(), variants=["v01"])
    assert "mechanism_summary" not in results
    assert results["rows"]
    for row in results["rows"]:
        assert "mechanism_used" not in row
    assert "evaluation_boundary" not in results


def test_off_byte_identity_sealed_cold_rows_additive(h, monkeypatch):
    """Sealed COLD rows are unchanged except the ADDITIVE mechanism_used key:
    every other row field matches the stage-3 sealed shape."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    results = h.run_harness(_sealed_adapters_config(), variants=["v09"], sealed=True)
    cold_rows = [r for r in results["rows"] if r["receiver_state"] == "cold"]
    assert cold_rows
    stage3_keys = {
        "variant", "variant_name", "turn", "phase", "receiver_model", "model_family",
        "model_version", "codebook_version", "decoder_configuration",
        "symbolic_examples", "receiver_state", "sealed", "task_response", "wire_bytes",
        "adapter_input_tokens", "expansion_tokens", "input_tokens", "output_tokens",
        "provider_cost_usd", "infrastructure_cost_usd", "retrieval_cost_usd",
        "retry_cost_usd", "cost_usd", "retrievals", "tool_calls", "retries",
        "semantic_loss", "task_success", "critical_fact_recall", "latency_ms",
    }
    for row in cold_rows:
        assert set(row) == stage3_keys | {"mechanism_used"}
        assert row["mechanism_used"] == "codebook"  # v09: codebook variant
    # warm rows: same shape, receiver_state warm
    warm_rows = [r for r in results["rows"] if r["receiver_state"] == "warm"]
    assert warm_rows
    for row in warm_rows:
        assert set(row) == stage3_keys | {"mechanism_used"}


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------


def test_sealed_warm_no_provider_skip(h, monkeypatch, capsys, scratch_dir):
    monkeypatch.delenv("SAGE_BENCH_LLM_PROVIDER", raising=False)
    assert h.main(["--sealed"]) == 0
    assert "not run, no provider" in capsys.readouterr().out
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config()))
    out_dir = scratch_dir / "out"
    assert h.main(["--sealed", "--adapters", str(cfg), "--output", str(out_dir)]) == 0
    assert "not run, no provider" in capsys.readouterr().out
    assert not out_dir.exists()


def test_sealed_warm_with_examples_rejected(h, monkeypatch, scratch_dir, capsys):
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config()))
    out_dir = scratch_dir / "must-not-exist"
    assert (
        h.main(["--sealed", "--with-examples", "--adapters", str(cfg), "--output", str(out_dir)])
        == 2
    )
    assert "--sealed cannot be combined with --with-examples" in capsys.readouterr().err
    assert not out_dir.exists()
    # static validation: fires even without a provider
    monkeypatch.delenv("SAGE_BENCH_LLM_PROVIDER", raising=False)
    assert h.main(["--sealed", "--with-examples"]) == 2


def test_priming_failure_clean_error_through_harness(h, monkeypatch):
    """A priming failure surfaces as a clean RuntimeError from run_harness --
    no fabricated warm rows are produced."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")

    def _failing_verify(codec, variant_spec, content, packet):
        raise RuntimeError(
            f"sealed warm lifecycle priming failed to commit receiver knowledge for variant "
            f"{variant_spec['id']}: injected failure -- refusing to fabricate a warm benefit"
        )

    # Clear the per-process warm render cache: an earlier test in this module
    # may have already primed v09, which would serve the cached re-encode and
    # never reach the priming gate.  The gate must actually run here.
    h._WARM_PACKET_RENDER_CACHE.clear()
    monkeypatch.setattr(h, "_verify_primed_knowledge", _failing_verify)
    with pytest.raises(RuntimeError, match="refusing to fabricate a warm benefit"):
        h.run_harness(_sealed_adapters_config(), variants=["v09"], sealed=True)
