"""Regression tests for the held-out evaluation split (issue #22, stage 3).

Covers (issue #22, stage 3):

* FROZEN-CODEBOOK PROOF: none of the held-out updates' canonicals appear in
  the frozen codebook (``heldout_scenario.establishment_canonicals`` -- the
  establishment material ONLY), while the ORACLE codebook (``cb._aifence_specs()``
  under the patched held-out globals) DOES contain every held-out canonical;
* CONTENT-TYPE COVERAGE: the fixture contains at least one update per issue
  section-C content type (paraphrased concept / unseen value / new
  combination of known concepts / changed state / contradiction / negation /
  numeric constraint / delayed-relevance), plus the state-machine shape the
  scoring machinery needs (6 state dicts, change markers for turns 1-5);
* FLAG VALIDATION: ``--held-out`` without ``--sealed`` exits 2 cleanly with
  no artifacts; ``--held-out`` + ``--record-feedback`` exits 2 cleanly;
  ``--held-out --sealed`` runs end-to-end with a 2-family fake adapter
  (exit 0, the leak detector never fires -- the sealed boundary holds);
* LABELS: held-out rows carry ``oracle_codebook`` true/false (true for the
  oracle AIFENCE rows, false for the frozen AIFENCE rows and the plain variants),
  table/delta rows distinguish the `` [oracle]`` / `` [frozen]`` modes, the
  artifact gains top-level ``dataset_split: "held_out"`` + an
  ``oracle_codebook`` variant->modes mapping; default-OFF artifacts carry
  NONE of these keys;
* DETERMINISM: two fresh ``--held-out --sealed`` CLI runs produce
  byte-identical printed tables and JSON artifacts modulo ``latency_ms``;
* FROZEN VS ORACLE: the frozen AIFENCE variants' re-encoded wire bytes differ
  from the oracle ones on the update turns (the smaller frozen codebook
  inlines more literals) and are byte-identical across two re-encode calls
  (deterministic); turn 0 (the establishment exchange, present in BOTH
  codebooks) encodes identically -- an honesty signal; the frozen rows'
  wire bytes ARE the frozen re-encode measurement (not a copy of the oracle
  rows), and the oracle re-encode reproduces the benchmark-recorded wire
  bytes under the patched globals;
* the sealed scorer and sealed payload builder keep working under the
  patched held-out globals (orion states score, the rendered packets carry
  orion bindings and no phoenix material, frozen exchanges face the frozen
  rendering).

All tests are deterministic (fixed inputs, no network, no real model) and
write their output directories under ``/opt/data/aifence/scratch/`` -- never
``/tmp``.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
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
HELDOUT_SCRIPT = ROOT / "scripts" / "heldout_scenario.py"
SCRATCH_ROOT = Path(os.environ.get("AIFENCE_BUS_SCRATCH_ROOT", "/opt/data/aifence/scratch")) / "stage22-heldout-tests"

#: AIFENCE variants whose sealed direct-symbolic packets are rendered for real.
AIFENCE_BUS_VARIANTS = ("v09", "v10", "v11", "v12")

#: LEAK-DETECTING sealed fake adapter (mirrors the stage-1 tests): exits 3
#: with {"error": "LEAK"} if any evaluator-only field reaches the adapter, else
#: replies with an ORION-flavored task_response + the sealed reply shape.
FAKE_ADAPTER_SEALED = (
    "import json,sys; p=json.load(sys.stdin); "
    "leak=[k for k in ('content','expected','change_markers','receiver_prior','examples') if k in p]; "
    "print(json.dumps({'error':'LEAK'})) if leak else None; "
    "sys.exit(3) if leak else None; "
    "print(json.dumps({'task_response': 'Project Orion is blocked because three of its integration tests failed.', "
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


def _load_heldout() -> Any:
    spec = importlib.util.spec_from_file_location("heldout_scenario", HELDOUT_SCRIPT)
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def h() -> Any:
    return _load_harness()


@pytest.fixture()
def scratch_dir() -> Iterator[Path]:
    """A scratch output directory under /opt/data/aifence/scratch (never /tmp)."""
    path = SCRATCH_ROOT / uuid.uuid4().hex[:12]
    path.mkdir(parents=True, exist_ok=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def _two_family_config() -> dict[str, Any]:
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


def _run_cli_subprocess(argv: list[str], fake_home: Path) -> subprocess.CompletedProcess:
    """Run the harness CLI in a FRESH subprocess (fake HOME + provider env).

    The provider env is set BEFORE the child env is built (the fake-adapter
    no-op trap: without ``AIFENCE_BUS_BENCH_LLM_PROVIDER`` the CLI prints "not run,
    no provider" and exits 0, exercising nothing); ``AIFENCE_BUS_DATABASE_URL`` is
    popped so the child's ``main()`` binds its own scratch database before
    the first ``aifence.bus`` import.
    """
    env = {**os.environ, "HOME": str(fake_home), "AIFENCE_BUS_BENCH_LLM_PROVIDER": "fake"}
    env.pop("AIFENCE_BUS_DATABASE_URL", None)
    return subprocess.run(
        [sys.executable, str(HARNESS_SCRIPT), *argv],
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )


def _compile(cb: Any, text: str) -> list[str]:
    from aifence.bus.compiler import compile_content

    return [unit.canonical for unit in compile_content(text)]


def _patched_heldout_cb(h: Any) -> tuple[Any, Any, list[str]]:
    """Load cb + the fixture, patch cb onto the held-out scenario, and return
    (cb, fixture module, frozen codebook)."""
    cb = h._load_compression_benchmark()
    ho = _load_heldout()
    frozen = h._apply_scenario(cb, held_out=True)
    assert frozen is not None
    return cb, ho, frozen


# ---------------------------------------------------------------------------
# FROZEN-CODEBOOK PROOF
# ---------------------------------------------------------------------------


def test_frozen_codebook_excludes_every_heldout_update_canonical(h):
    cb, ho, frozen = _patched_heldout_cb(h)
    frozen_set = set(frozen)
    # the frozen list is sorted and deduplicated (deterministic registration)
    assert frozen == sorted(frozen_set)
    assert frozen_set == set(_compile(cb, ho.ESTABLISHMENT_SHARED_CONTEXT))
    for index, update in enumerate(ho.HELDOUT_UPDATES, 1):
        for canonical in _compile(cb, update):
            assert canonical not in frozen_set, (
                f"HELDOUT_UPDATES[{index}] canonical {canonical!r} leaked into the "
                "frozen establishment-only codebook"
            )


def test_oracle_codebook_contains_every_heldout_update_canonical(h):
    cb, ho, frozen = _patched_heldout_cb(h)
    oracle = next(spec for spec in cb._aifence_specs() if spec["id"] == "v09")["codebook"]
    oracle_set = set(oracle)
    assert len(oracle) > len(frozen)  # the oracle saw establishment + updates
    for index, update in enumerate(ho.HELDOUT_UPDATES, 1):
        for canonical in _compile(cb, update):
            assert canonical in oracle_set, (
                f"HELDOUT_UPDATES[{index}] canonical {canonical!r} missing from the oracle codebook"
            )
    # the unseen-value spot check: the new python version's canonical is an
    # oracle-only concept
    assert "13" in oracle_set
    assert "13" not in set(frozen)


# ---------------------------------------------------------------------------
# Content-type coverage of the fixture
# ---------------------------------------------------------------------------


def test_heldout_fixture_content_type_coverage(h):
    cb, ho, _frozen = _patched_heldout_cb(h)
    updates = ho.HELDOUT_UPDATES
    assert len(updates) >= 8
    assert len(ho.HELDOUT_STATE_DICTS) == 6
    assert set(ho.HELDOUT_CHANGE_MARKERS) == {1, 2, 3, 4, 5}
    for state in ho.HELDOUT_STATE_DICTS:
        for field in ("deployment_allowed", "failed_tests", "migration_approved", "blocker"):
            assert field in state
    # (1) paraphrased concept -- U1 restates the deploy-gate failure in new words
    assert "blocked" in updates[0] and "integration tests" in updates[0]
    # (2) unseen value -- the new python version (3.13) was never established
    assert "3.13" in updates[1]
    assert "13" in _compile(cb, updates[1])
    # (3) new combination of known concepts -- U3 composes billing service +
    #     commerce team + platform team + migration review in a NEW relation
    for token in ("billing service", "Commerce team", "platform team", "migration review"):
        assert token in updates[2]
    # (4) changed state -- U4 flips failed_tests 3 -> 1
    assert "fixed two" in updates[3]
    assert ho.HELDOUT_STATE_DICTS[3]["failed_tests"] == 3
    assert ho.HELDOUT_STATE_DICTS[4]["failed_tests"] == 1
    # (5) contradiction -- U5 approves the migration DESPITE the failure
    assert "approved" in updates[4] and "despite" in updates[4] and "failure" in updates[4]
    # (6) negation -- U6 negates a fact
    assert re.search(r"\bno\b", updates[5], flags=re.IGNORECASE) and "failures" in updates[5]
    # (7) numeric constraint -- U7 pins a deploy-gate threshold
    assert "at least" in updates[6] and re.search(r"\d+", updates[6]) is not None
    # (8) delayed-relevance -- U8 plants a fact that only matters later
    assert "later" in updates[7]


# ---------------------------------------------------------------------------
# Flag validation
# ---------------------------------------------------------------------------


def test_heldout_without_sealed_exits_2_cleanly(scratch_dir, h, monkeypatch):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_two_family_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_dir = scratch_dir / "must-not-exist"

    # CLI: --held-out without --sealed -> exit 2, clean error, no artifacts
    completed = _run_cli_subprocess(
        ["--held-out", "--adapters", str(cfg), "--output", str(out_dir), "--variants", "v01"],
        fake_home,
    )
    assert completed.returncode == 2
    assert "--held-out requires --sealed" in completed.stderr
    assert not out_dir.exists()

    # in-process API: run_harness refuses with ValueError (CLI maps to exit 2)
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    with pytest.raises(ValueError, match="requires sealed"):
        h.run_harness(_two_family_config(), variants=["v01"], held_out=True)
    with pytest.raises(ValueError, match="requires sealed"):
        h.run_harness(_two_family_config(), variants=["v01"], held_out=True, sealed=False)

    # the conflict is a static CLI validation error: it fires even with no provider
    monkeypatch.delenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", raising=False)
    assert h.main(["--held-out"]) == 2


def test_heldout_with_record_feedback_exits_2_cleanly(scratch_dir, h, monkeypatch):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_two_family_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_dir = scratch_dir / "must-not-exist"

    completed = _run_cli_subprocess(
        ["--held-out", "--sealed", "--record-feedback", "--adapters", str(cfg), "--output", str(out_dir), "--variants", "v01"],
        fake_home,
    )
    assert completed.returncode == 2
    assert "--held-out cannot be combined with --record-feedback" in completed.stderr
    assert not out_dir.exists()

    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    with pytest.raises(ValueError, match="record_feedback"):
        h.run_harness(_two_family_config(), variants=["v01"], sealed=True, held_out=True, record_feedback=True)


def test_heldout_requires_sealed_no_provider_still_validates(h, monkeypatch, capsys):
    # static validation fires before the provider gate (mirrors --sealed +
    # --with-examples): even with no provider, the flag conflict is exit 2
    monkeypatch.delenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", raising=False)
    assert h.main(["--held-out"]) == 2
    assert "--held-out requires --sealed" in capsys.readouterr().err
    assert h.main(["--held-out", "--sealed", "--record-feedback"]) == 2
    assert "--record-feedback" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# End-to-end held-out sealed run (2-family fake adapter)
# ---------------------------------------------------------------------------


def test_heldout_sealed_end_to_end_two_families(scratch_dir):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_two_family_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_dir = scratch_dir / "out"
    completed = _run_cli_subprocess(
        ["--held-out", "--sealed", "--adapters", str(cfg), "--output", str(out_dir), "--variants", "v01,v05,v09,v12"],
        fake_home,
    )
    assert completed.returncode == 0, completed.stderr
    # the leak detector never fired: the sealed boundary holds in held-out mode
    assert "LEAK" not in completed.stdout + completed.stderr

    artifact = json.loads((out_dir / "model_eval_harness.json").read_text())
    assert artifact["dataset_split"] == "held_out"
    assert artifact["evaluation_boundary"] == "sealed"
    assert artifact["oracle_codebook"] == {
        "v09": ["frozen", "oracle"],
        "v12": ["frozen", "oracle"],
    }
    rows = artifact["rows"]
    assert rows
    pairs = {(row["variant"], row["receiver_model"]) for row in rows}
    assert pairs == {
        ("v01", "acme-gpt-4o"),
        ("v01", "nebula-sonnet"),
        ("v05", "acme-gpt-4o"),
        ("v05", "nebula-sonnet"),
        ("v09", "acme-gpt-4o"),
        ("v09", "nebula-sonnet"),
        ("v12", "acme-gpt-4o"),
        ("v12", "nebula-sonnet"),
    }
    for row in rows:
        assert "oracle_codebook" in row  # EVERY held-out row is labeled
        assert row["sealed"] is True
        assert row["task_response"]
        assert "receiver_prior" not in row
    # oracle AIFENCE rows are labeled true; frozen AIFENCE and plain rows false
    aifence_bus_labels = {(row["variant"], row["oracle_codebook"]) for row in rows if row["variant"] in AIFENCE_BUS_VARIANTS}
    assert aifence_bus_labels == {
        ("v09", True), ("v09", False), ("v12", True), ("v12", False),
    }
    plain_labels = {row["oracle_codebook"] for row in rows if row["variant"] not in AIFENCE_BUS_VARIANTS}
    assert plain_labels == {False}
    # table cells distinguish the two AIFENCE modes (the suffix sits before the
    # "[receiver] state" tail of the variant cell)
    cells = [line.split("|")[1].strip() for line in artifact["markdown_table"].splitlines()[2:]]
    assert any(" [oracle] " in cell for cell in cells)
    assert any(" [frozen] " in cell for cell in cells)
    # plain variants carry no mode suffix
    assert all(" [oracle]" not in cell and " [frozen]" not in cell for cell in cells if cell.startswith(("v01 ", "v05 ")))
    # delta rows distinguish the modes too
    delta_cells = [delta["variant_name"] for delta in artifact["deltas"]]
    assert any(cell.endswith(" [oracle]") for cell in delta_cells)
    assert any(cell.endswith(" [frozen]") for cell in delta_cells)
    # frozen wire bytes are a REAL measurement, not a copy of the oracle rows:
    # the update turns differ (frozen inlines more literals)
    def _wire(variant: str, turn: int, mode: bool, receiver: str = "acme-gpt-4o") -> int:
        return next(
            row["wire_bytes"]
            for row in rows
            if row["variant"] == variant
            and row["turn"] == turn
            and row["oracle_codebook"] is mode
            and row["receiver_model"] == receiver
            and row["receiver_state"] == "cold"
        )

    for turn in range(1, 6):
        assert _wire("v09", turn, False) != _wire("v09", turn, True)
    # turn 0 (the establishment exchange) is present in BOTH codebooks, so it
    # encodes identically -- an honesty signal that the frozen re-encode is
    # the same real codec path
    assert _wire("v09", 0, False) == _wire("v09", 0, True)


# ---------------------------------------------------------------------------
# Labels in-process + default-OFF absence
# ---------------------------------------------------------------------------


def test_heldout_labels_and_default_off_absence(h, monkeypatch):
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    config = _two_family_config()

    held = h.run_harness(config, variants=["v01", "v09"], sealed=True, held_out=True)
    assert held["dataset_split"] == "held_out"
    assert held["evaluation_boundary"] == "sealed"
    assert held["oracle_codebook"] == {"v09": ["frozen", "oracle"]}
    for row in held["rows"]:
        assert "oracle_codebook" in row
    v09_names = {row["variant_name"] for row in held["rows"] if row["variant"] == "v09"}
    assert any(name.endswith(" [oracle]") for name in v09_names)
    assert any(name.endswith(" [frozen]") for name in v09_names)
    v01_names = {row["variant_name"] for row in held["rows"] if row["variant"] == "v01"}
    assert all(not name.endswith((" [oracle]", " [frozen]")) for name in v01_names)
    for table_row in held["table_rows"]:
        assert "oracle_codebook" in table_row
    # the two modes produce distinct table rows for the same variant
    v09_table_modes = {
        table_row["oracle_codebook"]
        for table_row in held["table_rows"]
        if table_row["variant"] == "v09"
    }
    assert v09_table_modes == {True, False}

    off = h.run_harness(config, variants=["v01", "v09"], sealed=True)
    assert "dataset_split" not in off
    assert "oracle_codebook" not in off
    for row in off["rows"]:
        assert "oracle_codebook" not in row
        assert not row["variant_name"].endswith((" [oracle]", " [frozen]"))
    for table_row in off["table_rows"]:
        assert "oracle_codebook" not in table_row
    assert "held_out" not in json.dumps(off)


# ---------------------------------------------------------------------------
# Determinism (two fresh CLI runs)
# ---------------------------------------------------------------------------


def test_heldout_determinism_modulo_latency(scratch_dir):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_two_family_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_a = scratch_dir / "run-a"
    out_b = scratch_dir / "run-b"
    argv = ["--held-out", "--sealed", "--adapters", str(cfg), "--variants", "v01,v05,v09"]
    run_a = _run_cli_subprocess([*argv, "--output", str(out_a)], fake_home)
    assert run_a.returncode == 0, run_a.stderr
    run_b = _run_cli_subprocess([*argv, "--output", str(out_b)], fake_home)
    assert run_b.returncode == 0, run_b.stderr

    def _printed_table(run: subprocess.CompletedProcess, out_dir: Path) -> str:
        return run.stdout.split(f"Artifacts written to {out_dir}")[0]

    assert _printed_table(run_a, out_a) == _printed_table(run_b, out_b)

    def _strip_latency(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: _strip_latency(item) for key, item in value.items() if "latency" not in key}
        if isinstance(value, list):
            return [_strip_latency(item) for item in value]
        return value

    art_a = json.loads((out_a / "model_eval_harness.json").read_text())
    art_b = json.loads((out_b / "model_eval_harness.json").read_text())
    assert any("latency_ms" in row for row in art_a["rows"])
    assert _strip_latency(art_a) == _strip_latency(art_b)
    assert json.dumps(_strip_latency(art_a), sort_keys=True) == json.dumps(_strip_latency(art_b), sort_keys=True)
    assert (out_a / "model_eval_harness.md").read_bytes() == (out_b / "model_eval_harness.md").read_bytes()


# ---------------------------------------------------------------------------
# Frozen vs oracle re-encode (wire bytes are the real measurement)
# ---------------------------------------------------------------------------


def test_frozen_wire_bytes_differ_from_oracle_and_are_deterministic(h):
    cb, _ho, frozen = _patched_heldout_cb(h)
    spec = next(s for s in cb._aifence_specs() if s["id"] == "v09")
    oracle_rendered = h._render_aifence_variant_packets(cb, spec)
    frozen_a = h._render_frozen_variant_packets(cb, spec, frozen)
    frozen_b = h._render_frozen_variant_packets(cb, spec, frozen)

    # the frozen re-encode is deterministic: two calls are byte-identical
    for turn in range(6):
        assert frozen_a[turn]["rendering"] == frozen_b[turn]["rendering"]
        assert frozen_a[turn]["wire_bytes_json"] == frozen_b[turn]["wire_bytes_json"]
        assert frozen_a[turn]["reconstruction"] == frozen_b[turn]["reconstruction"]

    # the frozen measurement is REAL, not a copy of the oracle: the update
    # turns differ (the smaller frozen codebook inlines more literals -> more
    # bytes) ...
    for turn in range(1, 6):
        assert frozen_a[turn]["wire_bytes_json"] != oracle_rendered[turn]["wire_bytes_json"]
        assert frozen_a[turn]["wire_bytes_json"] > oracle_rendered[turn]["wire_bytes_json"]
    # ... while turn 0 (the establishment exchange, registered in BOTH
    # codebooks) encodes identically -- the same real codec path
    assert frozen_a[0]["wire_bytes_json"] == oracle_rendered[0]["wire_bytes_json"]

    # honesty: under the patched held-out globals the ORACLE re-encode
    # reproduces the benchmark-recorded wire bytes for the held-out material
    benchmark = cb.run_benchmark(out_dir=None)
    recorded = next(row for row in benchmark["variants"] if row["variant_id"] == "v09")
    for turn in range(6):
        recorded_turn = next(t for t in recorded["turns"] if t["turn"] == turn)
        assert oracle_rendered[turn]["wire_bytes_json"] == recorded_turn["wire_bytes_json"]


def test_frozen_rows_wire_bytes_are_the_frozen_measurement(h, monkeypatch):
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    results = h.run_harness(_two_family_config(), variants=["v09"], sealed=True, held_out=True)
    cb, _ho, frozen = _patched_heldout_cb(h)
    spec = next(s for s in cb._aifence_specs() if s["id"] == "v09")
    frozen_rendered = h._render_frozen_variant_packets(cb, spec, frozen)

    frozen_rows = [
        row
        for row in results["rows"]
        if row["variant"] == "v09" and row["oracle_codebook"] is False and row["receiver_model"] == "acme-gpt-4o" and row["receiver_state"] == "cold"
    ]
    assert len(frozen_rows) == 6
    for row in frozen_rows:
        turn = row["turn"]
        # the frozen row's wire bytes ARE the frozen re-encode measurement --
        # there is no benchmark-recorded counterpart for the frozen codebook
        assert row["wire_bytes"] == frozen_rendered[turn]["wire_bytes_json"]
        if turn == 0:
            continue  # the establishment exchange is in BOTH codebooks -> identical
        assert row["wire_bytes"] != next(
            r["wire_bytes"]
            for r in results["rows"]
            if r["variant"] == "v09"
            and r["oracle_codebook"] is True
            and r["turn"] == turn
            and r["receiver_model"] == "acme-gpt-4o"
            and r["receiver_state"] == "cold"
        )


# ---------------------------------------------------------------------------
# Sealed scorer + payload builder under the patched held-out globals
# ---------------------------------------------------------------------------


def test_heldout_scoring_and_payload_under_patched_globals(h):
    cb, _ho, frozen = _patched_heldout_cb(h)
    exchange = {"variant": "v05", "variant_name": "x", "turn": 1, "phase": "update", "aifence": False}

    # the exact rendered ORION state scores a perfect turn
    ok = cb.render_state_text(cb.STATE_DICTS[1])
    task_success, _recall = h._score_sealed_response(cb, exchange, ok, "acme")
    assert task_success == 1.0
    # a STALE (turn-0) state scores below perfect (marker + state mismatch)
    stale = cb.render_state_text(cb.STATE_DICTS[0])
    task_success_stale, _recall = h._score_sealed_response(cb, exchange, stale, "acme")
    assert 0.0 < task_success_stale < 1.0

    # oracle payload: the model-facing packet is the REAL held-out rendering
    # (orion bindings, no phoenix material anywhere in the payload)
    aifence_bus_exchange = {"variant": "v09", "variant_name": "x", "turn": 1, "phase": "update", "aifence": True, "wire_bytes": 123}
    payload = h._build_sealed_payload(cb, aifence_bus_exchange, "cold", "direct-symbolic", {"family": "a", "version": "1"})
    rendered = json.loads(payload["model_facing_packet"])
    assert any("orion" in str(value) for value in rendered["bindings"].values())
    assert "phoenix" not in payload["model_facing_packet"]
    for key in ("content", "expected", "change_markers", "receiver_prior", "examples"):
        assert key not in payload

    # frozen payload: the model faces the FROZEN re-encode rendering (the one
    # the frozen exchange carries), not the oracle re-render
    frozen_exchange = {
        **aifence_bus_exchange,
        "frozen": True,
        "representation": "FROZEN-RENDER-MARKER",
    }
    payload = h._build_sealed_payload(cb, frozen_exchange, "cold", "direct-symbolic", {"family": "a", "version": "1"})
    assert payload["model_facing_packet"] == "FROZEN-RENDER-MARKER"

    # the frozen rendering itself is the real codec packet shape
    frozen_rendered = h._render_frozen_variant_packets(cb, next(s for s in cb._aifence_specs() if s["id"] == "v09"), frozen)
    packet = json.loads(frozen_rendered[1]["rendering"])
    for key in ("act", "atoms", "bindings", "cb", "id", "meta", "prov", "receiver", "sender", "v"):
        assert key in packet
    assert packet["atoms"]
    # turn 0 carries ESTABLISHMENT content (registered in the frozen codebook),
    # so its atoms carry codes and the bindings legend is non-empty.
    packet0 = json.loads(frozen_rendered[0]["rendering"])
    assert packet0["bindings"]
