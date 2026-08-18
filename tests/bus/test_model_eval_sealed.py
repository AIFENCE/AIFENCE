"""Regression tests for the sealed model boundary (issue #22, stage 1).

Covers (issue #22, stage 1):

* a LEAK-DETECTING fake adapter proves the sealed payload never carries
  evaluator-only fields (``content`` / ``expected`` / ``change_markers`` /
  ``receiver_prior`` / ``examples``) end-to-end through the CLI with a
  2-family config, plus a negative control proving the detector is armed
  (a leaking payload exits 3 with ``{"error": "LEAK"}``);
* the sealed payload shape: the exact key set, no leak keys, and
  ``task`` / ``model_facing_packet`` / ``allowed_decoder_metadata`` present
  (state vs text task instructions, decoder metadata from the adapter spec);
* harness-side scoring correctness: crafted ``task_response`` texts that DO
  and DO NOT satisfy markers/state score the expected ``task_success`` /
  ``critical_fact_recall`` (expectations computed by hand from
  ``cb.evaluate_turn`` semantics; turn i -> ``cb.STATE_DICTS[i]``);
* adapter-reported ``task_success`` / ``critical_fact_recall`` are IGNORED
  in sealed mode -- the harness score is authoritative;
* ``--sealed`` + ``--with-examples`` exits 2 with a clean error and writes
  no artifacts;
* sealed determinism: two fresh CLI subprocess runs produce byte-identical
  printed tables and JSON artifacts modulo ``latency_ms``;
* default-OFF byte identity: non-sealed results carry no
  ``evaluation_boundary`` key and no per-row ``sealed``/``task_response``;
* sealed mode with a missing/empty ``task_response`` raises an
  adapter-naming RuntimeError (exit 1 through the CLI);
* the adapter subprocess environment is scrubbed of every ``AIFENCE_*``
  variable (the scratch ground-truth DB path must never be reachable by a
  hostile adapter -- adversary F1): a unit test spawns a child through
  ``_invoke`` with ``AIFENCE_BUS_DATABASE_URL`` + ``AIFENCE_BUS_BENCH_LLM_PROVIDER`` set
  in the parent env and asserts the child sees none, and an ENV-LEAK-
  DETECTING adapter (checks its own env, exits 3 on any ``AIFENCE_*`` key)
  passes an end-to-end ``--sealed`` CLI run, with a negative control
  proving the detector is armed;
* sealed ``task_response`` is capped at ``MAX_TASK_RESPONSE_CHARS``
  (oversized replies raise an adapter-naming RuntimeError / CLI exit 1 with
  no artifact written -- adversary F2), and the exact-cap boundary is still
  accepted;
* no-provider skip with ``--sealed`` prints "not run, no provider", exit 0.

All tests are deterministic (fixed inputs, no network, no real model) and
write their output directories under ``/opt/data/aifence/scratch/`` -- never
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
SCRATCH_ROOT = Path(os.environ.get("AIFENCE_BUS_SCRATCH_ROOT", "/opt/data/aifence/scratch")) / "stage22-sealed-tests"

#: Evaluator-only fields the sealed payload must NEVER carry.
LEAK_KEYS = ("content", "expected", "change_markers", "receiver_prior", "examples")

#: LEAK-DETECTING fake adapter: reads the payload from stdin; if ANY
#: evaluator-only field is present it prints {"error": "LEAK"} and exits 3
#: (proving the detector is armed), otherwise it echoes a fixed task_response
#: plus token/cost numbers -- the sealed contract's required reply shape.
FAKE_ADAPTER_SEALED = (
    "import json,sys; p=json.load(sys.stdin); "
    "leak=[k for k in ('content','expected','change_markers','receiver_prior','examples') if k in p]; "
    "print(json.dumps({'error':'LEAK'})) if leak else None; "
    "sys.exit(3) if leak else None; "
    "print(json.dumps({'task_response': 'Project Phoenix is blocked because three integration tests failed.', "
    "'input_tokens': 7, 'output_tokens': 5, 'provider_cost_usd': 0.0012}))"
)

#: Echo adapter that ALSO claims a bogus 0.0 task_success / critical_fact_recall
#: -- proves sealed rows are scored by the harness, not the adapter.
FAKE_ADAPTER_ECHO_CLAIM_ZERO = (
    "import json,sys; p=json.load(sys.stdin); "
    "print(json.dumps({'task_success': 0.0, 'critical_fact_recall': 0.0, "
    "'task_response': p.get('model_facing_packet', ''), "
    "'input_tokens': 7, 'output_tokens': 5, 'provider_cost_usd': 0.0012}))"
)

#: Adapter that never reports a task_response (sealed contract violation).
FAKE_ADAPTER_NO_TASK_RESPONSE = (
    "import json,sys; print(json.dumps({'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0}))"
)

#: ENV-LEAK-DETECTING fake adapter: reads the payload from stdin; if the
#: child environment carries ANY ``AIFENCE_*`` variable (e.g. a leaked
#: AIFENCE_BUS_DATABASE_URL pointing at the harness's ground-truth scratch DB) it
#: prints {"error": "ENV_LEAK", "keys": [...]} and exits 3 (proving the
#: detector is armed), otherwise it echoes a valid sealed reply.  Proves
#: ``_invoke`` scrubs AIFENCE_* variables from the adapter subprocess env
#: (issue #22 adversary F1).
FAKE_ADAPTER_ENV_LEAK = (
    "import json,sys,os; p=json.load(sys.stdin); "
    "leak=[k for k in os.environ if k.startswith('AIFENCE_')]; "
    "print(json.dumps({'error':'ENV_LEAK','keys':leak})) if leak else None; "
    "sys.exit(3) if leak else None; "
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
    """A scratch output directory under /opt/data/aifence/scratch (never /tmp)."""
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


def _two_family_config(command_tail: str) -> dict[str, Any]:
    """Two-family config where the FIRST adapter runs the given reply script."""
    return {
        "acme-bad": {
            "family": "acme",
            "version": "1",
            "command": [sys.executable, "-c", command_tail],
        },
        "nebula-ok": {
            "family": "nebula",
            "version": "1",
            "command": [sys.executable, "-c", FAKE_ADAPTER_SEALED],
        },
    }


def _run_cli_subprocess(argv: list[str], fake_home: Path) -> subprocess.CompletedProcess:
    """Run the harness CLI in a FRESH subprocess (fake HOME + provider env)."""
    env = {**os.environ, "HOME": str(fake_home), "AIFENCE_BUS_BENCH_LLM_PROVIDER": "fake"}
    env.pop("AIFENCE_BUS_DATABASE_URL", None)
    return subprocess.run(
        [sys.executable, str(HARNESS_SCRIPT), *argv],
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )


def _exchange(turn: int, variant: str = "v05") -> dict[str, Any]:
    return {"variant": variant, "variant_name": "x", "turn": turn, "phase": "update", "aifence": False}


# ---------------------------------------------------------------------------
# Sealed payload shape (unit)
# ---------------------------------------------------------------------------


def test_sealed_payload_exact_shape_and_no_leaks(h):
    cb = h._load_compression_benchmark()
    exchange = {
        **_exchange(3),
        "variant": "v05",
        "representation": {"blocker": "migration"},
        "reconstruction": "blocker: migration; deployment_allowed: false",
        "wire_bytes": 123,
        "content": "TOP-SECRET source content",
        "expected": {"qa": {"blocker": "migration"}},
        "change_markers": ["migration failure remains"],
    }
    spec = {"family": "acme", "version": "1", "codebook_version": "global:7"}
    payload = h._build_sealed_payload(cb, exchange, "cold", "direct-symbolic", spec)

    assert set(payload) == {
        "protocol",
        "benchmark",
        "variant",
        "variant_name",
        "turn",
        "phase",
        "receiver_state",
        "decoder_configuration",
        "wire_bytes",
        "symbolic_examples",
        "task",
        "model_facing_packet",
        "allowed_decoder_metadata",
    }
    for key in LEAK_KEYS + ("representation", "model_facing_text", "receiver_prior"):
        assert key not in payload
    assert payload["symbolic_examples"] is False
    assert payload["protocol"] == "aifence/0.2"
    assert payload["decoder_configuration"] == "direct symbolic"
    assert payload["model_facing_packet"] == exchange["reconstruction"]  # plain variant
    assert payload["allowed_decoder_metadata"] == {
        "codebook_version": "global:7",
        "receiver_state": "cold",
        "decoder_configuration": "direct symbolic",
    }
    # state variants get the state-report task
    assert "deployment_allowed" in payload["task"]
    assert "what changed" in payload["task"]


def test_sealed_payload_task_and_packet_selection(h):
    cb = h._load_compression_benchmark()
    text_exchange = {
        **_exchange(1, variant="v01"),
        "variant": "v01",
        "representation": "REPR",
        "reconstruction": "RECON",
        "wire_bytes": 10,
    }
    # text variant -> summarize task
    payload = h._build_sealed_payload(cb, text_exchange, "warm", "direct-symbolic", {"family": "a", "version": "1"})
    assert "Summarize the latest update" in payload["task"]
    assert payload["model_facing_packet"] == "RECON"  # plain variant: reconstruction
    # default codebook_version when the spec pins none
    assert payload["allowed_decoder_metadata"]["codebook_version"] == "global:1"
    assert payload["allowed_decoder_metadata"]["receiver_state"] == "warm"
    # aifence variant in direct-symbolic -> the RENDERED ACTUAL codec packet
    # (stage 2): a canonical compact-JSON rendering of the real v12 packet
    # for (v12, turn 1), not the stage-1 canonical-clause proxy.
    aifence_bus_exchange = {**text_exchange, "variant": "v12", "aifence": True}
    payload = h._build_sealed_payload(cb, aifence_bus_exchange, "cold", "direct-symbolic", {"family": "a", "version": "1"})
    rendered = json.loads(payload["model_facing_packet"])
    assert payload["model_facing_packet"] != "REPR"
    for key in ("act", "atoms", "bindings", "cb", "id", "meta", "prov", "receiver", "sender", "v"):
        assert key in rendered
    assert rendered["atoms"]  # ACKed full-AIFENCE packets carry code/cv atoms
    assert rendered["bindings"]
    for key in ("strategy_note", "canonicals"):
        assert key not in rendered
    assert "Report the current receiver state" in payload["task"]  # v12 is a state variant
    # aifence variant in full-expansion -> reconstruction again
    payload = h._build_sealed_payload(cb, aifence_bus_exchange, "cold", "full-expansion", {"family": "a", "version": "1"})
    assert payload["model_facing_packet"] == "RECON"
    assert payload["decoder_configuration"] == "full natural-language expansion"


# ---------------------------------------------------------------------------
# Harness-side scoring correctness
# ---------------------------------------------------------------------------


def test_sealed_scoring_correct_and_wrong_responses(h):
    cb = h._load_compression_benchmark()

    # turn 1: exact rendered state -> every qa/state/action field correct
    ok1 = cb.render_state_text(cb.STATE_DICTS[1])
    task_success, recall = h._score_sealed_response(cb, _exchange(1), ok1, "acme")
    assert task_success == 1.0
    assert recall == 0.0  # rendered state carries none of the critical phrases

    # turn 1: a response that mentions none of the markers/state -> 0.3
    task_success, recall = h._score_sealed_response(cb, _exchange(1), "I don't know what changed.", "acme")
    assert task_success == pytest.approx(0.3)
    assert recall == 0.0

    # turn 2: STALE state (turn-1 rendered) -> state mismatch + missing marker
    task_success, recall = h._score_sealed_response(cb, _exchange(2), cb.render_state_text(cb.STATE_DICTS[1]), "acme")
    assert task_success == pytest.approx(0.85)
    assert recall == 0.0

    # turn 5: full natural-language answer satisfying BOTH critical constraints
    t5 = (
        "Project Phoenix is ready for production deployment. All integration tests pass. "
        "The migration was reviewed by the platform team and approved."
    )
    task_success, recall = h._score_sealed_response(cb, _exchange(5), t5, "acme")
    assert task_success == 1.0
    assert recall == 1.0

    # turn 5: same answer WITHOUT the platform-team review -> recall 0.5
    t5b = (
        "Project Phoenix is ready for production deployment. All integration tests pass. "
        "The migration was approved."
    )
    task_success, recall = h._score_sealed_response(cb, _exchange(5), t5b, "acme")
    assert task_success == 1.0
    assert recall == 0.5


def test_sealed_scoring_rejects_empty_or_non_string(h):
    cb = h._load_compression_benchmark()
    for bad in ("", "   ", None, {"text": "x"}, 42):
        with pytest.raises(RuntimeError, match="acme") as exc_info:
            h._score_sealed_response(cb, _exchange(1), bad, "acme")
        assert "task_response" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Adapter-reported scores ignored in sealed mode
# ---------------------------------------------------------------------------


def test_sealed_adapter_reported_scores_ignored(h, monkeypatch):
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    config = {
        "acme-echo": {
            "family": "acme",
            "version": "1",
            "command": [sys.executable, "-c", FAKE_ADAPTER_ECHO_CLAIM_ZERO],
        },
        "nebula-echo": {
            "family": "nebula",
            "version": "1",
            "command": [sys.executable, "-c", FAKE_ADAPTER_ECHO_CLAIM_ZERO],
        },
    }
    results = h.run_harness(config, variants=["v05"], sealed=True)
    rows = results["rows"]
    assert rows
    assert results["evaluation_boundary"] == "sealed"
    for row in rows:
        assert row["sealed"] is True
        assert row["task_response"]  # the echoed model-facing packet
        assert "receiver_prior" not in row
        # the adapter claimed 0.0 -- the harness score must win
        assert row["task_success"] != 0.0
    # turns 1..5 were answered with the exact rendered current state
    for row in rows:
        if row["turn"] >= 1:
            assert row["task_success"] == 1.0
            assert row["critical_fact_recall"] == 0.0


# ---------------------------------------------------------------------------
# LEAK-DETECTING adapter end-to-end (2-family CLI run)
# ---------------------------------------------------------------------------


def test_sealed_leak_detecting_adapter_end_to_end(scratch_dir):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_dir = scratch_dir / "out"
    completed = _run_cli_subprocess(
        ["--sealed", "--adapters", str(cfg), "--output", str(out_dir), "--variants", "v01,v05"],
        fake_home,
    )
    assert completed.returncode == 0, completed.stderr
    # the leak detector never fired
    assert "LEAK" not in completed.stdout + completed.stderr

    artifact = json.loads((out_dir / "model_eval_harness.json").read_text())
    assert artifact["evaluation_boundary"] == "sealed"
    assert artifact["symbolic_examples"] is False
    rows = artifact["rows"]
    assert rows
    pairs = {(row["variant"], row["receiver_model"]) for row in rows}
    assert pairs == {
        ("v01", "acme-gpt-4o"),
        ("v01", "nebula-sonnet"),
        ("v05", "acme-gpt-4o"),
        ("v05", "nebula-sonnet"),
    }
    for row in rows:
        assert row["sealed"] is True
        assert row["task_response"]
        assert "receiver_prior" not in row
        assert 0.0 <= row["task_success"] <= 1.0
    cells = [line.split("|")[1].strip() for line in artifact["markdown_table"].splitlines()[2:]]
    assert any(cell.endswith("] cold") for cell in cells)
    assert any(cell.endswith("] warm") for cell in cells)

    # negative control: the detector is ARMED -- a leaking payload exits 3
    proc = subprocess.run(
        [sys.executable, "-c", FAKE_ADAPTER_SEALED],
        input=json.dumps({"content": "SECRET", "turn": 1}),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 3
    assert "LEAK" in proc.stdout


# ---------------------------------------------------------------------------
# CLI flag conflicts and skip behavior
# ---------------------------------------------------------------------------


def test_sealed_with_examples_rejected_cleanly(h, monkeypatch, scratch_dir, capsys):
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config()))
    out_dir = scratch_dir / "must-not-exist"
    assert (
        h.main(["--sealed", "--with-examples", "--adapters", str(cfg), "--output", str(out_dir)])
        == 2
    )
    err = capsys.readouterr().err
    assert "--sealed cannot be combined with --with-examples" in err
    assert "decoder knowledge" in err
    assert not out_dir.exists()  # no artifacts on the flag-conflict path

    # the conflict is a static CLI validation error: it fires even with no provider
    monkeypatch.delenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", raising=False)
    assert h.main(["--sealed", "--with-examples"]) == 2
    assert "--sealed cannot be combined with --with-examples" in capsys.readouterr().err


def test_sealed_no_provider_skip(h, monkeypatch, capsys, scratch_dir):
    monkeypatch.delenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", raising=False)
    assert h.main(["--sealed"]) == 0
    assert "not run, no provider" in capsys.readouterr().out
    # an adapters config alone is not enough: the provider gate still skips
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config()))
    out_dir = scratch_dir / "out"
    assert h.main(["--sealed", "--adapters", str(cfg), "--output", str(out_dir)]) == 0
    assert "not run, no provider" in capsys.readouterr().out
    assert not out_dir.exists()


# ---------------------------------------------------------------------------
# Missing / empty task_response -> adapter-naming RuntimeError, exit 1
# ---------------------------------------------------------------------------


def test_sealed_missing_task_response_raises(h, monkeypatch):
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    with pytest.raises(RuntimeError, match="acme-bad") as exc_info:
        h.run_harness(_two_family_config(FAKE_ADAPTER_NO_TASK_RESPONSE), variants=["v01"], sealed=True)
    assert "task_response" in str(exc_info.value)

    # an empty-string task_response is equally rejected
    empty = "import json,sys; print(json.dumps({'task_response': '', 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0}))"
    with pytest.raises(RuntimeError, match="acme-bad") as exc_info:
        h.run_harness(_two_family_config(empty), variants=["v01"], sealed=True)
    assert "task_response" in str(exc_info.value)


def test_sealed_missing_task_response_cli_exit_1(scratch_dir):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_two_family_config(FAKE_ADAPTER_NO_TASK_RESPONSE)))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    completed = _run_cli_subprocess(
        ["--sealed", "--adapters", str(cfg), "--variants", "v01"],
        fake_home,
    )
    assert completed.returncode == 1
    assert "task_response" in completed.stderr
    assert "acme-bad" in completed.stderr


# ---------------------------------------------------------------------------
# Sealed determinism (two fresh CLI runs)
# ---------------------------------------------------------------------------


def test_sealed_determinism_modulo_latency(scratch_dir):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_a = scratch_dir / "run-a"
    out_b = scratch_dir / "run-b"
    run_a = _run_cli_subprocess(
        ["--sealed", "--adapters", str(cfg), "--output", str(out_a), "--variants", "v01,v05"],
        fake_home,
    )
    assert run_a.returncode == 0, run_a.stderr
    run_b = _run_cli_subprocess(
        ["--sealed", "--adapters", str(cfg), "--output", str(out_b), "--variants", "v01,v05"],
        fake_home,
    )
    assert run_b.returncode == 0, run_b.stderr

    # printed tables (and status lines) byte-identical -- the run-specific
    # "Artifacts written to <dir>" footer is excluded
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
    serialized_a = json.dumps(_strip_latency(art_a), sort_keys=True).encode("utf-8")
    serialized_b = json.dumps(_strip_latency(art_b), sort_keys=True).encode("utf-8")
    assert serialized_a == serialized_b
    assert (out_a / "model_eval_harness.md").read_bytes() == (out_b / "model_eval_harness.md").read_bytes()


# ---------------------------------------------------------------------------
# Default-OFF byte identity
# ---------------------------------------------------------------------------


def test_non_sealed_results_have_no_evaluation_boundary(h, monkeypatch):
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    config = {
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
    results = h.run_harness(config, variants=["v01"])
    assert "evaluation_boundary" not in results
    assert results["symbolic_examples"] is False
    for row in results["rows"]:
        assert "sealed" not in row
        assert "task_response" not in row
        assert "receiver_prior" in row  # unsealed rows keep the prior field


# ---------------------------------------------------------------------------
# Adapter subprocess env scrubbing (issue #22 adversary F1)
# ---------------------------------------------------------------------------


def test_sealed_adapter_env_scrubbed_in_invoke(h, monkeypatch):
    """A child spawned by ``_invoke`` must see NO ``AIFENCE_*`` env vars.

    With ``AIFENCE_BUS_DATABASE_URL`` and ``AIFENCE_BUS_BENCH_LLM_PROVIDER`` set in the
    PARENT env, a ``python -c`` child that prints the ``AIFENCE_*`` keys it
    observes must see an empty list -- and non-AIFENCE vars (HOME/PATH) must
    still pass through.
    """
    monkeypatch.setenv("AIFENCE_BUS_DATABASE_URL", "sqlite:///should-never-leak.db")
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    child = (
        "import json,os; "
        "print(json.dumps({'aifence_bus_env_keys': sorted(k for k in os.environ if k.startswith('AIFENCE_')), "
        "'has_home': 'HOME' in os.environ, 'has_path': 'PATH' in os.environ}))"
    )
    result = h._invoke([sys.executable, "-c", child], {"turn": 1}, 60, "acme")
    assert result["aifence_bus_env_keys"] == []
    assert result["has_home"] is True
    assert result["has_path"] is True


def test_sealed_env_leak_detecting_adapter_end_to_end(scratch_dir):
    """A --sealed CLI run whose adapter checks its own env for AIFENCE_* vars
    must exit 0: the child env carries no AIFENCE_* variables (F1)."""
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_two_family_config(FAKE_ADAPTER_ENV_LEAK)))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_dir = scratch_dir / "out"
    completed = _run_cli_subprocess(
        ["--sealed", "--adapters", str(cfg), "--output", str(out_dir), "--variants", "v01,v05"],
        fake_home,
    )
    assert completed.returncode == 0, completed.stderr
    assert "ENV_LEAK" not in completed.stdout + completed.stderr

    artifact = json.loads((out_dir / "model_eval_harness.json").read_text())
    assert artifact["evaluation_boundary"] == "sealed"
    assert artifact["rows"]

    # negative control: the detector is ARMED -- with a AIFENCE_* var in ITS env
    # it must fire (exit 3, ENV_LEAK), proving a leaked env would be caught.
    leaked_env = {**os.environ, "AIFENCE_BUS_DATABASE_URL": "sqlite:///leak.db"}
    proc = subprocess.run(
        [sys.executable, "-c", FAKE_ADAPTER_ENV_LEAK],
        input=json.dumps({"turn": 1}),
        capture_output=True,
        text=True,
        timeout=60,
        env=leaked_env,
    )
    assert proc.returncode == 3
    assert "ENV_LEAK" in proc.stdout


# ---------------------------------------------------------------------------
# Oversized task_response cap (issue #22 adversary F2)
# ---------------------------------------------------------------------------


def _oversized_task_response_script(h: Any) -> str:
    """Adapter script replying with a task_response one char over the cap."""
    return (
        "import json,sys; print(json.dumps("
        f"{{'task_response': 'x' * {h.MAX_TASK_RESPONSE_CHARS + 1}, 'input_tokens': 1, 'output_tokens': 1, "
        "'provider_cost_usd': 0.0}))"
    )


def test_sealed_oversized_task_response_raises(h, monkeypatch):
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")
    with pytest.raises(RuntimeError, match="acme-bad") as exc_info:
        h.run_harness(
            _two_family_config(_oversized_task_response_script(h)),
            variants=["v01"],
            sealed=True,
        )
    assert "task_response" in str(exc_info.value)
    assert "characters" in str(exc_info.value)

    # boundary: exactly MAX_TASK_RESPONSE_CHARS chars is still accepted
    cb = h._load_compression_benchmark()
    h._score_sealed_response(cb, _exchange(1), "x" * h.MAX_TASK_RESPONSE_CHARS, "acme")


def test_sealed_oversized_task_response_cli_exit_1(scratch_dir, h):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_two_family_config(_oversized_task_response_script(h))))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_dir = scratch_dir / "out"
    completed = _run_cli_subprocess(
        ["--sealed", "--adapters", str(cfg), "--output", str(out_dir), "--variants", "v01"],
        fake_home,
    )
    assert completed.returncode == 1
    assert "task_response" in completed.stderr
    assert "acme-bad" in completed.stderr
    assert not out_dir.exists()  # no artifact written on the rejection path
