"""Regression tests for the opt-in model evaluation harness (issue #16, stage 3).

Covers (issue #16, stage 3):

* clean no-provider skip -- no ``--adapters`` flag or unset
  ``SAGE_BENCH_LLM_PROVIDER`` -> "not run, no provider", exit code 0,
  nothing fabricated;
* the >=2 model families gate -- configs covering fewer than 2 distinct
  ``family`` values are rejected with a clear error;
* a fake adapter (a tiny ``python -c`` command that echoes a JSON result from
  stdin) proves the end-to-end run produces rows with the RFC's per-model
  fields (receiver model, model version, codebook version, decoder
  configuration, symbolic-example flag), cold AND warm rows, and a markdown
  table matching the RFC's six-column public format;
* decoder-assisted mode counts expansion tokens in ``input_tokens``
  (RFC "Prevent hidden decompression costs");
* adapter failures (non-zero exit / missing ``task_success``) raise a clear
  error -- never silent fabrication;
* hardening regression tests (adversary findings F1-F7): DB isolation and
  repeat in-process ``main()`` calls, numeric reply validation, missing
  executable / ``--output`` file / missing adapters-file error paths,
  determinism modulo ``latency_ms``, and CLI hygiene (``--timeout`` > 0,
  empty ``--variants``, stripped family/version);
* round-2 hardening regression tests (reviewer F8 + adversary Adv-1..Adv-6):
  a per-process-unique scratch DB path with two CONCURRENT CLI runs both
  succeeding, refusal to rebind a pre-imported ``sage_plugin`` engine (no
  drop_all on a pre-bound user DB), ``latency_ms`` validation, bool
  rejection in ``_finite_float``, ``--timeout`` nan/inf rejection, and no
  empty ``--output`` dir left behind on a missing adapters file;
* round-3 hardening regression tests (adversary findings #1..#2): no empty
  ``--output`` dir left behind on an empty ``--variants`` value with a valid
  adapters file, and an advisory stderr overwrite warning when the output
  dir already holds ``model_eval_harness.json``.

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
SCRATCH_ROOT = Path(os.environ.get("SAGE_SCRATCH_ROOT", "/opt/data/sage/scratch")) / "stage3-tests"

#: A deterministic fake adapter: reads the JSON payload from stdin, echoes a
#: fixed result.  Warm receivers succeed at 1.0, cold receivers at 0.5, so the
#: cold/warm split is observable in the rows.
FAKE_ADAPTER_OK = (
    "import json,sys; p=json.load(sys.stdin); "
    "print(json.dumps({'task_success': 1.0 if p.get('receiver_state') == 'warm' else 0.5, "
    "'input_tokens': 7, 'output_tokens': 5, 'provider_cost_usd': 0.0012, 'critical_fact_recall': 0.8}))"
)
FAKE_ADAPTER_EXIT_3 = "import sys; sys.exit(3)"
FAKE_ADAPTER_NO_SUCCESS = (
    "import json,sys; p=json.load(sys.stdin); "
    "print(json.dumps({'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0}))"
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


def _adapters_config() -> dict[str, Any]:
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


def _one_family_config() -> dict[str, Any]:
    """Two adapters of the SAME family -- must be rejected by the gate."""
    return {
        "acme-gpt-4o": {
            "family": "acme",
            "version": "gpt-4o-2026-05",
            "command": [sys.executable, "-c", FAKE_ADAPTER_OK],
        },
        "acme-gpt-4o-mini": {
            "family": "acme",
            "version": "gpt-4o-mini",
            "command": [sys.executable, "-c", FAKE_ADAPTER_OK],
        },
    }


def _run_cli_subprocess(argv: list[str], fake_home: Path) -> subprocess.CompletedProcess:
    """Run the harness CLI in a FRESH subprocess (fake HOME + provider env).

    The Adv-1 fix makes ``main()`` refuse to rebind an already-imported
    ``sage_plugin.db`` engine, so happy-path CLI runs must execute in a
    process where ``sage_plugin`` has not been imported yet -- the same
    isolation ``test_repeated_in_process_main_calls`` uses (the pytest
    session's conftest imports ``sage_plugin.db`` at session start).
    """
    env = {**os.environ, "HOME": str(fake_home), "SAGE_BENCH_LLM_PROVIDER": "fake"}
    env.pop("SAGE_DATABASE_URL", None)
    return subprocess.run(
        [sys.executable, str(HARNESS_SCRIPT), *argv],
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )


# ---------------------------------------------------------------------------
# No-provider skip
# ---------------------------------------------------------------------------


def test_no_provider_skip_is_clean(h, monkeypatch, capsys, scratch_dir):
    monkeypatch.delenv("SAGE_BENCH_LLM_PROVIDER", raising=False)
    assert h.provider_available() is False
    assert h.main([]) == 0
    assert "not run, no provider" in capsys.readouterr().out
    # an adapters config alone is not enough: the provider env gate still skips
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    out_dir = scratch_dir / "out"
    assert h.main(["--adapters", str(cfg), "--output", str(out_dir)]) == 0
    assert "not run, no provider" in capsys.readouterr().out
    assert not out_dir.exists()  # nothing was fabricated or written


# ---------------------------------------------------------------------------
# >=2 model families gate
# ---------------------------------------------------------------------------


def test_less_than_two_families_rejected(h):
    with pytest.raises(ValueError, match="at least 2 distinct model families"):
        h.validate_adapters(_one_family_config())
    # two adapters of DIFFERENT families pass the gate
    h.validate_adapters(_adapters_config())
    # structural validation is still enforced
    with pytest.raises(ValueError, match="command"):
        h.validate_adapters({"x": {"family": "acme", "version": "1", "command": "not-a-list"}})


def test_less_than_two_families_cli_error(h, monkeypatch, scratch_dir, capsys):
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_one_family_config()))
    assert h.main(["--adapters", str(cfg)]) == 2
    assert "at least 2 distinct model families" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Fake-adapter end-to-end
# ---------------------------------------------------------------------------


def test_fake_adapter_end_to_end(h, scratch_dir):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    out_dir = scratch_dir / "out"
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    completed = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_dir), "--variants", "v01,v12", "--with-examples"],
        fake_home,
    )
    assert completed.returncode == 0, completed.stderr
    artifact = json.loads((out_dir / "model_eval_harness.json").read_text())
    markdown = (out_dir / "model_eval_harness.md").read_text()
    rows = artifact["rows"]
    assert rows

    # RFC "Receiver compatibility" per-model fields on every row
    required_fields = {
        "receiver_model",
        "model_version",
        "codebook_version",
        "decoder_configuration",
        "symbolic_examples",
        "receiver_state",
    }
    for row in rows:
        assert required_fields <= row.keys()

    # cold AND warm rows for every (variant, receiver) combination
    pairs = {(row["variant"], row["receiver_model"]) for row in rows}
    assert pairs == {("v01", "acme-gpt-4o"), ("v01", "nebula-sonnet"), ("v12", "acme-gpt-4o"), ("v12", "nebula-sonnet")}
    for variant, receiver in pairs:
        states = {
            row["receiver_state"] for row in rows if row["variant"] == variant and row["receiver_model"] == receiver
        }
        assert states == {"cold", "warm"}

    # the fake adapter's cold/warm split flows through: warm succeeds, cold 0.5
    assert {row["task_success"] for row in rows if row["receiver_state"] == "warm"} == {1.0}
    assert {row["task_success"] for row in rows if row["receiver_state"] == "cold"} == {0.5}

    # per-model fields carry the config values
    config = _adapters_config()
    row = rows[0]
    assert row["receiver_model"] in config
    assert row["model_family"] == config[row["receiver_model"]]["family"]
    assert row["model_version"] == config[row["receiver_model"]]["version"]
    assert row["codebook_version"] == "global:1"  # default when unpinned
    assert row["symbolic_examples"] is True
    assert row["decoder_configuration"] == "direct symbolic"

    # RFC public format: exact header + separator, then one 6-column row each
    lines = artifact["markdown_table"].splitlines()
    assert lines[0] == h.RFC_TABLE_HEADER
    assert lines[1] == h.RFC_TABLE_SEPARATOR
    assert lines[0] == "| Variant | Wire bytes | Input tokens | Total cost | Task accuracy | Critical-fact recall |"
    for line in lines[2:]:
        assert line.startswith("| ")
        assert line.count("|") == 7  # six columns
        assert line.endswith(" |")

    # deterministic sort: variant, then receiver, then cold before warm
    cells = [line.split("|")[1].strip() for line in lines[2:]]
    assert cells == sorted(cells)
    assert any(cell.endswith("] cold") for cell in cells)
    assert any(cell.endswith("] warm") for cell in cells)

    # aggregate rows carry accuracy/recall percentages derived from the adapter
    for table_row in artifact["table_rows"]:
        assert table_row["task_accuracy"] in (0.5, 1.0)
        assert table_row["critical_fact_recall"] == 0.8
    assert "%" in markdown

    # warm-vs-cold deltas exist for every (variant, receiver) pair
    assert len(artifact["deltas"]) == 4
    for delta in artifact["deltas"]:
        assert delta["task_accuracy_delta"] == 0.5  # warm 1.0 - cold 0.5

    # no database files may be left behind in the artifact directory
    assert not list(out_dir.glob("*.db"))
    assert not list(out_dir.glob("*.sqlite*"))


# ---------------------------------------------------------------------------
# Decoder-assisted token accounting
# ---------------------------------------------------------------------------


def test_decoder_assisted_counts_expansion_tokens(h, scratch_dir):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_dir = scratch_dir / "decoder-assisted"
    completed = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_dir), "--variants", "v01", "--decoder-mode", "decoder-assisted"],
        fake_home,
    )
    assert completed.returncode == 0, completed.stderr
    rows = json.loads((out_dir / "model_eval_harness.json").read_text())["rows"]
    assert rows
    for row in rows:
        assert row["decoder_configuration"] == "decoder-assisted"
        assert row["adapter_input_tokens"] == 7
        assert row["expansion_tokens"] > 0
        assert row["input_tokens"] == row["adapter_input_tokens"] + row["expansion_tokens"]

    # the expansion equals the deterministic estimator on the model-facing text
    cb = h._load_compression_benchmark()
    for row in rows:
        if row["variant"] == "v01" and row["turn"] == 0:
            assert row["expansion_tokens"] == cb._estimate_tokens(cb.SHARED_CONTEXT)

    # direct-symbolic (default) adds no expansion tokens
    out_dir_plain = scratch_dir / "direct-symbolic"
    completed_plain = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_dir_plain), "--variants", "v01"], fake_home
    )
    assert completed_plain.returncode == 0, completed_plain.stderr
    rows_plain = json.loads((out_dir_plain / "model_eval_harness.json").read_text())["rows"]
    for row in rows_plain:
        assert row["decoder_configuration"] == "direct symbolic"
        assert row["expansion_tokens"] == 0
        assert row["input_tokens"] == row["adapter_input_tokens"] == 7


# ---------------------------------------------------------------------------
# Adapter failures raise, never fabricate
# ---------------------------------------------------------------------------


def test_adapter_failure_raises_clear_error(h, monkeypatch):
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    exit_config = {
        "acme-bad": {
            "family": "acme",
            "version": "1",
            "command": [sys.executable, "-c", FAKE_ADAPTER_EXIT_3],
        },
        "nebula-ok": {
            "family": "nebula",
            "version": "1",
            "command": [sys.executable, "-c", FAKE_ADAPTER_OK],
        },
    }
    with pytest.raises(RuntimeError, match="acme-bad"):
        h.run_harness(exit_config, variants=["v01"])

    missing_config = {
        "acme-ok": {
            "family": "acme",
            "version": "1",
            "command": [sys.executable, "-c", FAKE_ADAPTER_OK],
        },
        "nebula-missing": {
            "family": "nebula",
            "version": "1",
            "command": [sys.executable, "-c", FAKE_ADAPTER_NO_SUCCESS],
        },
    }
    with pytest.raises(RuntimeError, match="task_success"):
        h.run_harness(missing_config, variants=["v01"])


def test_unknown_variant_rejected(h, monkeypatch):
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    with pytest.raises(ValueError, match="unknown variant id"):
        h.run_harness(_adapters_config(), variants=["v99"])


# ---------------------------------------------------------------------------
# Hardening regression tests (adversary findings F1-F7)
# ---------------------------------------------------------------------------


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
            "command": [sys.executable, "-c", FAKE_ADAPTER_OK],
        },
    }


def test_run_harness_refuses_without_database_url(h, monkeypatch, scratch_dir):
    """F1: run_harness() must never operate on the ambient default database
    (~/sage.db); without SAGE_DATABASE_URL it refuses with a RuntimeError."""
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.delenv("SAGE_DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="SAGE_DATABASE_URL"):
        h.run_harness(_adapters_config(), variants=["v01"])
    assert not (fake_home / "sage.db").exists()  # ambient DB never created


def test_repeated_in_process_main_calls(h, monkeypatch, scratch_dir):
    """F1: two sequential in-process main() calls must both succeed and the
    SAGE_DATABASE_URL env must be restored (no engine left bound to a deleted
    scratch db file)."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    script = scratch_dir / "two_calls.py"
    script.write_text(
        "import importlib.util, os, sys\n"
        "from pathlib import Path\n"
        f"ROOT = Path({str(ROOT)!r})\n"
        "sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'scripts'))\n"
        f"HARNESS = {str(HARNESS_SCRIPT)!r}\n"
        f"CFG = {str(cfg)!r}\n"
        f"OUT_A = {str(scratch_dir / 'outA')!r}\n"
        f"OUT_B = {str(scratch_dir / 'outB')!r}\n"
        "spec = importlib.util.spec_from_file_location('model_eval_harness', HARNESS)\n"
        "h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)\n"
        "rc1 = h.main(['--adapters', CFG, '--output', OUT_A, '--variants', 'v09'])\n"
        "rc2 = h.main(['--adapters', CFG, '--output', OUT_B, '--variants', 'v09'])\n"
        "print('rc1=' + str(rc1) + ' rc2=' + str(rc2) + ' env_after=' + repr(os.environ.get('SAGE_DATABASE_URL')))\n"
    )
    env = {**os.environ, "HOME": str(fake_home)}
    env.pop("SAGE_DATABASE_URL", None)
    completed = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, timeout=300, env=env
    )
    assert completed.returncode == 0, completed.stderr
    assert "rc1=0 rc2=0 env_after=None" in completed.stdout


def test_adapter_garbage_numerics_rejected(h, monkeypatch, scratch_dir):
    """F2: non-finite/out-of-range/negative/string numerics raise an
    adapter-naming RuntimeError; artifacts stay valid RFC 8259 JSON."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    cases = [
        (
            "task_success inf",
            "import json,sys,math; print(json.dumps({'task_success': float('inf'), 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0}))",
            "task_success",
        ),
        (
            "task_success nan",
            "import json,sys,math; print(json.dumps({'task_success': float('nan'), 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0}))",
            "task_success",
        ),
        (
            "task_success out of range",
            "import json,sys; print(json.dumps({'task_success': 2.0, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0}))",
            "task_success",
        ),
        (
            "negative tokens",
            "import json,sys; print(json.dumps({'task_success': 1.0, 'input_tokens': -5, 'output_tokens': 1, 'provider_cost_usd': 0.0}))",
            "input_tokens",
        ),
        (
            "string tokens",
            "import json,sys; print(json.dumps({'task_success': 1.0, 'input_tokens': 'abc', 'output_tokens': 1, 'provider_cost_usd': 0.0}))",
            "input_tokens",
        ),
        (
            "fractional tokens",
            "import json,sys; print(json.dumps({'task_success': 1.0, 'input_tokens': 1.5, 'output_tokens': 1, 'provider_cost_usd': 0.0}))",
            "input_tokens",
        ),
        (
            "nan cost",
            "import json,sys,math; print(json.dumps({'task_success': 1.0, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': float('nan')}))",
            "provider_cost_usd",
        ),
        (
            "negative cost",
            "import json,sys; print(json.dumps({'task_success': 1.0, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': -1.0}))",
            "provider_cost_usd",
        ),
        (
            "string cost",
            "import json,sys; print(json.dumps({'task_success': 1.0, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 'abc'}))",
            "provider_cost_usd",
        ),
    ]
    for name, tail, field in cases:
        with pytest.raises(RuntimeError, match="acme-bad") as exc_info:
            h.run_harness(_two_family_config(tail), variants=["v01"], timeout=30)
        assert field in str(exc_info.value), name
        assert "acme-bad" in str(exc_info.value), name

    # the artifact writer refuses to emit non-finite numbers (RFC 8259 strict)
    out_dir = scratch_dir / "nan-artifact"
    with pytest.raises(RuntimeError, match="non-finite"):
        h._write_artifacts(out_dir, {"rows": [{"latency_ms": float("nan")}], "markdown": ""})


def test_missing_adapter_executable_clean_error(h, monkeypatch):
    """F3: a missing adapter executable surfaces as an adapter-naming
    RuntimeError, never a raw FileNotFoundError traceback."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    cfg = {
        "acme-missing-bin": {"family": "acme", "version": "1", "command": ["/nonexistent/binary-xyz"]},
        "nebula-ok": {"family": "nebula", "version": "1", "command": [sys.executable, "-c", FAKE_ADAPTER_OK]},
    }
    with pytest.raises(RuntimeError, match="acme-missing-bin could not start"):
        h.run_harness(cfg, variants=["v01"])


def test_output_path_existing_file_exit_2(h, monkeypatch, scratch_dir, capsys):
    """F4: --output pointing at an existing FILE exits 2 before any run."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    out_file = scratch_dir / "iamafile.txt"
    out_file.write_text("x")
    assert h.main(["--adapters", str(cfg), "--output", str(out_file), "--variants", "v01"]) == 2
    assert "--output path exists and is not a directory" in capsys.readouterr().err


def test_missing_adapters_file_exit_2(h, monkeypatch, capsys):
    """F5: a nonexistent --adapters file exits 2 with a clean message."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    assert h.main(["--adapters", "/nonexistent/no-such.json", "--variants", "v01"]) == 2
    assert "no such adapters file" in capsys.readouterr().err


def test_artifacts_deterministic_modulo_latency(scratch_dir):
    """F6: two runs produce byte-identical JSON artifacts once the measured
    *_latency_ms row values are dropped, and byte-identical .md artifacts."""
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_a = scratch_dir / "run-a"
    out_b = scratch_dir / "run-b"
    run_a = _run_cli_subprocess(["--adapters", str(cfg), "--output", str(out_a), "--variants", "v01,v09"], fake_home)
    assert run_a.returncode == 0, run_a.stderr
    run_b = _run_cli_subprocess(["--adapters", str(cfg), "--output", str(out_b), "--variants", "v01,v09"], fake_home)
    assert run_b.returncode == 0, run_b.stderr

    def _strip_latency(value: Any) -> Any:
        # mirror the stage-2 convention (test_compression_benchmark): measured
        # latency fields are excluded from determinism comparisons
        if isinstance(value, dict):
            return {key: _strip_latency(item) for key, item in value.items() if "latency" not in key}
        if isinstance(value, list):
            return [_strip_latency(item) for item in value]
        return value

    art_a = json.loads((out_a / "model_eval_harness.json").read_text())
    art_b = json.loads((out_b / "model_eval_harness.json").read_text())
    assert any("latency_ms" in row for row in art_a["rows"])  # latency is kept in rows
    assert _strip_latency(art_a) == _strip_latency(art_b)
    # byte-identical after dropping the latency fields (stage-2 convention)
    serialized_a = json.dumps(_strip_latency(art_a), sort_keys=True).encode("utf-8")
    serialized_b = json.dumps(_strip_latency(art_b), sort_keys=True).encode("utf-8")
    assert serialized_a == serialized_b
    assert (out_a / "model_eval_harness.md").read_bytes() == (out_b / "model_eval_harness.md").read_bytes()


def test_hygiene_timeout_variants_and_stripping(h, monkeypatch, scratch_dir, capsys):
    """F7: --timeout must be > 0; an empty --variants value is an error;
    family/version values are whitespace-stripped on load."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    # --timeout <= 0 is rejected by argparse (exit 2)
    with pytest.raises(SystemExit) as excinfo:
        h.main(["--timeout", "0"])
    assert excinfo.value.code == 2
    # an empty --variants value must not silently mean "all twelve"
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    assert h.main(["--adapters", str(cfg), "--variants", ""]) == 2
    assert "at least one variant" in capsys.readouterr().err
    # family/version are reported stripped after validation
    padded = {name: dict(spec) for name, spec in _adapters_config().items()}
    for spec in padded.values():
        spec["family"] = f"  {spec['family']}  "
        spec["version"] = f"  {spec['version']}  "
    normalized = h.validate_adapters(padded)
    for spec in normalized.values():
        assert spec["family"] == spec["family"].strip()
        assert spec["version"] == spec["version"].strip()


# ---------------------------------------------------------------------------
# Round-2 hardening regression tests (reviewer F8 + adversary Adv-1..Adv-6)
# ---------------------------------------------------------------------------


def test_scratch_db_per_process_unique_and_concurrent_runs(h, scratch_dir):
    """F8/Adv-2: the scratch DB path embeds the pid (per-process unique), so
    two CONCURRENT harness CLI runs (spawned before either finishes, distinct
    --output dirs) both succeed instead of racing on a shared database file."""
    path = h._scratch_db_path()
    assert path.name == f"model_eval_harness-{os.getpid()}.db"
    assert str(os.getpid()) in path.name
    assert path.parent.name == ".sage-bench"

    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    env = {**os.environ, "HOME": str(fake_home), "SAGE_BENCH_LLM_PROVIDER": "fake"}
    env.pop("SAGE_DATABASE_URL", None)
    base = [sys.executable, str(HARNESS_SCRIPT), "--adapters", str(cfg), "--variants", "v01"]
    procs = [
        subprocess.Popen(
            [*base, "--output", str(scratch_dir / "outA")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        ),
        subprocess.Popen(
            [*base, "--output", str(scratch_dir / "outB")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        ),
    ]
    for label, proc in zip(("A", "B"), procs, strict=True):
        _out, err = proc.communicate(timeout=300)
        assert proc.returncode == 0, f"concurrent run {label} failed rc={proc.returncode}: {err}"
        assert "OperationalError" not in err
    assert (scratch_dir / "outA" / "model_eval_harness.json").exists()
    assert (scratch_dir / "outB" / "model_eval_harness.json").exists()


def test_run_harness_refuses_prebound_sage_plugin_db(scratch_dir):
    """Adv-1: when sage_plugin.db is already imported with an engine bound to
    a DIFFERENT database than SAGE_DATABASE_URL, run_harness() must refuse
    with a RuntimeError and must NOT drop_all the pre-bound database (a
    sentinel table must survive)."""
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    sentinel_db = scratch_dir / "sentinel.db"
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    script = scratch_dir / "prebound.py"
    script.write_text(
        "import importlib.util, json, os, sys\n"
        "from pathlib import Path\n"
        "from sqlalchemy import text\n"
        f"ROOT = Path({str(ROOT)!r})\n"
        "sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'scripts'))\n"
        f"HARNESS = {str(HARNESS_SCRIPT)!r}\n"
        f"SENTINEL_DB = {str(sentinel_db)!r}\n"
        f"CFG = {str(cfg)!r}\n"
        "# pre-import aifence.bus bound to a USER database holding a sentinel table\n"
        "os.environ['SAGE_DATABASE_URL'] = 'sqlite:///' + SENTINEL_DB\n"
        "import aifence.bus.db as db\n"
        "import aifence.bus.db_models  # register tables\n"
        "# simulate a pre-existing USER db: only the sentinel table exists (no\n"
        "# sage tables yet) -- any message_audit appearing later is pollution\n"
        "with db.engine.begin() as conn:\n"
        "    conn.execute(text('CREATE TABLE sentinel_marker (id INTEGER PRIMARY KEY)'))\n"
        "    conn.execute(text('INSERT INTO sentinel_marker VALUES (1)'))\n"
        "spec = importlib.util.spec_from_file_location('model_eval_harness', HARNESS)\n"
        "h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)\n"
        "# point SAGE_DATABASE_URL at a DIFFERENT database than the bound engine\n"
        "os.environ['SAGE_DATABASE_URL'] = 'sqlite:///' + SENTINEL_DB + '-other'\n"
        "adapters = json.loads(Path(CFG).read_text())\n"
        "try:\n"
        "    h.run_harness(adapters, variants=['v01'])\n"
        "    print('RESULT: NO_REFUSAL')\n"
        "except RuntimeError as exc:\n"
        "    print('RESULT: REFUSED: ' + str(exc))\n"
        "try:\n"
        "    with db.engine.connect() as conn:\n"
        "        n = conn.execute(text('SELECT COUNT(*) FROM sentinel_marker')).scalar()\n"
        "    print('SENTINEL_COUNT=' + str(n))\n"
        "except Exception as exc:\n"
        "    print('SENTINEL_COUNT=ERROR:' + type(exc).__name__)\n"
        "with db.engine.connect() as conn:\n"
        "    audit = conn.execute(text(\"SELECT name FROM sqlite_master WHERE name='message_audit'\")).scalar()\n"
        "print('MESSAGE_AUDIT=' + str(audit is not None))\n"
    )
    env = {**os.environ, "HOME": str(fake_home)}
    env.pop("SAGE_DATABASE_URL", None)
    completed = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, timeout=300, env=env
    )
    assert completed.returncode == 0, completed.stderr
    assert "RESULT: REFUSED" in completed.stdout, completed.stdout
    assert "aifence.bus" in completed.stdout, completed.stdout
    assert "SENTINEL_COUNT=1" in completed.stdout, completed.stdout
    assert "MESSAGE_AUDIT=False" in completed.stdout, completed.stdout


def test_adapter_latency_ms_validated(h, monkeypatch):
    """Adv-3: adapter-supplied latency_ms is validated like every other
    numeric field -- nan / negative / string values raise an adapter-naming
    RuntimeError instead of silently poisoning rows."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    cases = [
        (
            "latency_ms nan",
            "import json,sys,math; print(json.dumps({'task_success': 1.0, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0, 'latency_ms': float('nan')}))",
        ),
        (
            "latency_ms -5",
            "import json,sys; print(json.dumps({'task_success': 1.0, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0, 'latency_ms': -5.0}))",
        ),
        (
            "latency_ms abc",
            "import json,sys; print(json.dumps({'task_success': 1.0, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0, 'latency_ms': 'abc'}))",
        ),
    ]
    for name, tail in cases:
        with pytest.raises(RuntimeError, match="acme-bad") as exc_info:
            h.run_harness(_two_family_config(tail), variants=["v01"], timeout=30)
        assert "latency_ms" in str(exc_info.value), name
        assert "acme-bad" in str(exc_info.value), name


def test_finite_float_rejects_bools(h, monkeypatch):
    """Adv-4: JSON booleans (task_success: true/false, provider_cost_usd:
    true) must raise an adapter-naming RuntimeError, never silently coerce to
    1.0/0.0 (bool is an int subclass and float(True) == 1.0)."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    cases = [
        (
            "task_success true",
            "import json; print(json.dumps({'task_success': True, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0}))",
        ),
        (
            "task_success false",
            "import json; print(json.dumps({'task_success': False, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': 0.0}))",
        ),
        (
            "provider_cost_usd true",
            "import json; print(json.dumps({'task_success': 1.0, 'input_tokens': 1, 'output_tokens': 1, 'provider_cost_usd': True}))",
        ),
    ]
    for name, tail in cases:
        with pytest.raises(RuntimeError, match="acme-bad") as exc_info:
            h.run_harness(_two_family_config(tail), variants=["v01"], timeout=30)
        assert "acme-bad" in str(exc_info.value), name


def test_timeout_nan_inf_rejected(h, capsys):
    """Adv-5: --timeout nan/inf are rejected by argparse (exit 2) via
    math.isfinite, not accepted and later misinterpreted; a finite positive
    value still parses (no provider -> clean skip)."""
    for bad in ("nan", "inf", "-inf"):
        with pytest.raises(SystemExit) as excinfo:
            h.main(["--timeout", bad])
        assert excinfo.value.code == 2, bad
    assert h.main(["--timeout", "5.0"]) == 0
    assert "not run, no provider" in capsys.readouterr().out


def test_missing_adapters_leaves_no_output_dir(h, monkeypatch, scratch_dir, capsys):
    """Adv-6: when the adapters file is missing, --output must NOT be
    created -- the output dir is only made after the adapters config loads."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    out_dir = scratch_dir / "must-not-exist"
    assert (
        h.main(["--adapters", "/nonexistent/no-such.json", "--output", str(out_dir), "--variants", "v01"])
        == 2
    )
    assert "no such adapters file" in capsys.readouterr().err
    assert not out_dir.exists()


# ---------------------------------------------------------------------------
# Round-3 hardening regression tests (adversary findings #1 and #2)
# ---------------------------------------------------------------------------


def test_empty_variants_leaves_no_output_dir(h, monkeypatch, scratch_dir, capsys):
    """Adversary finding #1: with a VALID adapters file, an empty --variants
    value must exit 2 WITHOUT creating the --output dir -- the mkdir happens
    only after every config path has validated (mirrors
    test_missing_adapters_leaves_no_output_dir)."""
    monkeypatch.setenv("SAGE_BENCH_LLM_PROVIDER", "fake")
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    out_dir = scratch_dir / "must-not-exist"
    assert (
        h.main(["--adapters", str(cfg), "--variants", "", "--output", str(out_dir)]) == 2
    )
    assert "at least one variant" in capsys.readouterr().err
    assert not out_dir.exists()


def test_existing_artifact_warns_on_stderr(scratch_dir):
    """Adversary finding #2: when the --output dir already holds a
    model_eval_harness.json (e.g. a concurrent run pointed at the same dir),
    the harness still succeeds (exit 0) but prints an advisory overwrite
    warning on stderr -- no silent last-wins."""
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    out_dir = scratch_dir / "out"
    out_dir.mkdir()
    (out_dir / "model_eval_harness.json").write_text('{"stale": true}\n')
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    completed = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_dir), "--variants", "v01"],
        fake_home,
    )
    assert completed.returncode == 0, completed.stderr
    assert "warning: overwriting existing artifacts" in completed.stderr
    assert "concurrent runs" in completed.stderr
    # the run still wrote its own artifacts (the overwrite is intentional)
    assert (out_dir / "model_eval_harness.json").exists()
