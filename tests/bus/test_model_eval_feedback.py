"""Regression tests for the harness feedback loop (issue #16, stage 4).

Covers (issue #16, stage 4 -- RFC "learned semantic shorthand" feedback
loop, ``--record-feedback``):

1. recording task_success=1.0 raises a pattern's ``task_utility`` and
   ``utility_score``; task_success=0.0 lowers them (asserted via
   ``PatternStore.response`` / direct fields, mirroring test_patterns);
2. a shadow pattern whose measured task success clears the shadow threshold
   advances shadow->validated/active through the harness hook, and retires
   on 2x min-samples failure;
3. default-OFF determinism: two runs without ``--record-feedback`` produce
   byte-identical artifacts (existing contract); with the flag ON, artifacts
   differ ONLY in the new ``feedback`` fields;
4. out-of-range ``task_success`` (1.5, -0.1) raises a clear error; unknown
   ``packet_id`` raises ``KeyError`` (mirror ``runtime.feedback``);
5. ZERO wire-byte change: with ``--record-feedback`` ON, the AIFENCE variants'
   wire bytes are byte-identical to the default run (feedback is post-hoc DB
   bookkeeping, never touches encode).

All tests are deterministic (fixed inputs, no network, no real model).  The
unit-level tests exercise the harness hook (``_record_feedback_for_packets``)
against the session test database exactly like test_patterns.py; the
end-to-end determinism/wire-byte tests run the CLI in subprocesses with a
fake HOME (the prebound-engine guard makes in-process happy-path runs
impossible), mirroring test_model_eval_harness.py's ``_run_cli_subprocess``.
Output directories are written under /opt/data/aifence/scratch/ -- never
/tmp.
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
from sqlalchemy import select

from aifence.bus.codec import AifenceCodec
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.db_models import LearnedPattern, MesaifenceAudit
from aifence.bus.schemas import EncodeRequest

ROOT = Path(__file__).resolve().parents[2]
HARNESS_SCRIPT = ROOT / "scripts" / "model_eval_harness.py"
SCRATCH_ROOT = Path(os.environ.get("AIFENCE_BUS_SCRATCH_ROOT", "/opt/data/aifence/scratch")) / "stage4-tests"

#: A deterministic fake adapter: reads the JSON payload from stdin, echoes a
#: fixed result.  Warm receivers succeed at 1.0, cold receivers at 0.5, so the
#: cold/warm split is observable in the rows.
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


def _pattern_settings(**overrides: Any) -> Settings:
    """Mirror test_patterns.pattern_settings (low thresholds, deterministic)."""
    values = dict(
        auth_required=False,
        max_inline_bytes=100_000,
        default_token_budget=100_000,
        max_packet_bytes=100_000,
        promotion_min_count=999,
        pattern_learning_enabled=True,
        pattern_string_constants_enabled=True,
        pattern_min_components=2,
        pattern_max_components=4,
        pattern_max_observations_per_message=32,
        pattern_candidate_min_count=2,
        pattern_min_savings_bytes=0,
        pattern_shadow_min_samples=2,
        pattern_shadow_min_success=0.9,
        pattern_auto_activate=True,
        pattern_counterfactual_required=True,
        pattern_counterfactual_min_samples=1,
        pattern_holdout_min_samples=1,
        pattern_holdout_min_sources=1,
        pattern_holdout_min_fidelity=0.9,
        pattern_utility_min_score=0.0,
        semantic_cache_enabled=False,
        pattern_min_source_diversity=1,
        pattern_min_trust_score=0.0,
        pattern_max_source_share=1.0,
        pattern_session_min_sources=1,
        pattern_project_min_sources=1,
        pattern_workspace_min_sources=1,
        pattern_domain_min_sources=1,
        pattern_federation_min_sources=1,
    )
    values.update(overrides)
    return Settings(**values)


def _shadow_pattern_and_audit(db: Any, settings: Settings, content: dict[str, Any]) -> tuple[Any, Any]:
    """Create a shadow pattern + a MesaifenceAudit row whose decisions carry a
    ``pattern_shadow_match`` for it (mirror test_patterns), returning
    ``(pattern, audit)``."""
    codec = AifenceCodec(db, settings)
    codec.encode(EncodeRequest(content=content, auto_learn=True, record_learning=True, use_cache=False))
    second = codec.encode(EncodeRequest(content=content, auto_learn=True, record_learning=True, use_cache=False))
    pattern = db.scalar(select(LearnedPattern).where(LearnedPattern.status == "shadow"))
    assert pattern is not None
    audit = db.scalar(select(MesaifenceAudit).where(MesaifenceAudit.packet_id == second.packet.id))
    assert audit is not None
    assert any(
        d.get("action") == "pattern_shadow_match" and d.get("pattern_id") == pattern.pattern_id
        for d in audit.decisions
    )
    return pattern, audit


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


# ---------------------------------------------------------------------------
# 1. task_utility / utility_score rise and fall through the harness hook
# ---------------------------------------------------------------------------


def test_feedback_raises_then_lowers_task_utility_and_score(h, isolated_db):
    """Recording task_success=1.0 raises a pattern's task_utility and
    utility_score; recording task_success=0.0 lowers them -- asserted via
    PatternStore.response and direct fields, through the harness hook."""
    settings = _pattern_settings()
    with SessionLocal() as db:
        pattern, audit = _shadow_pattern_and_audit(db, settings, {"cause": "test_failure", "deployment": "blocked"})
        assert pattern.task_utility is None  # no feedback yet

        # task_success=1.0 -> task_utility rises to 1.0, utility_score rises
        summary = h._record_feedback_for_packets(db, settings, [(0, audit.packet_id)], 1.0)
        db.commit()
        assert summary["patterns_updated"][0]["task_utility_before"] is None
        assert summary["patterns_updated"][0]["task_utility_after"] == 1.0
        assert pattern.task_utility == 1.0
        utility_after_high = pattern.utility_score

        # task_success=0.0 -> task_utility falls to 0.5, utility_score falls
        summary_low = h._record_feedback_for_packets(db, settings, [(0, audit.packet_id)], 0.0)
        db.commit()
        assert summary_low["patterns_updated"][0]["task_utility_after"] == 0.5
        assert pattern.task_utility == 0.5
        assert pattern.utility_score < utility_after_high

        # the same facts surface through PatternStore.response (runtime shape)
        from aifence.bus.patterns import PatternStore

        response = PatternStore(db, settings).response(pattern)
        assert response["task_utility"] == 0.5
        assert response["utility_score"] == pattern.utility_score


# ---------------------------------------------------------------------------
# 2. Shadow promotion / retirement through the harness hook
# ---------------------------------------------------------------------------


def test_feedback_promotes_shadow_to_validated(h, isolated_db):
    """A shadow pattern whose measured task success clears the threshold
    advances shadow->validated/active through the harness hook (mirror
    test_patterns semantics)."""
    settings = _pattern_settings()
    with SessionLocal() as db:
        pattern, audit = _shadow_pattern_and_audit(db, settings, {"cause": "test_failure", "deployment": "blocked"})
        # one sample below the threshold keeps it shadow
        h._record_feedback_for_packets(db, settings, [(0, audit.packet_id)], 1.0)
        db.commit()
        assert pattern.status == "shadow"
        # second sample clears pattern_shadow_min_samples=2 -> validated
        # (counterfactual required, so not auto-activated to active)
        h._record_feedback_for_packets(db, settings, [(0, audit.packet_id)], 1.0)
        db.commit()
        assert pattern.status == "validated"


def test_feedback_auto_activates_without_counterfactual(h, isolated_db):
    """With pattern_counterfactual_required=False and auto_activate on, the
    harness hook advances shadow straight to active once the threshold
    clears."""
    settings = _pattern_settings(pattern_counterfactual_required=False)
    with SessionLocal() as db:
        pattern, audit = _shadow_pattern_and_audit(db, settings, {"cause": "test_failure", "deployment": "blocked"})
        h._record_feedback_for_packets(db, settings, [(0, audit.packet_id)], 1.0)
        db.commit()
        h._record_feedback_for_packets(db, settings, [(0, audit.packet_id)], 1.0)
        db.commit()
        assert pattern.status == "active"


def test_feedback_retires_shadow_on_2x_min_samples_failure(h, isolated_db):
    """A shadow pattern that fails 2x min-samples worth of measured task
    success retires through the harness hook."""
    settings = _pattern_settings()
    with SessionLocal() as db:
        pattern, audit = _shadow_pattern_and_audit(db, settings, {"cause": "test_failure", "deployment": "blocked"})
        for _ in range(4):  # 2 * pattern_shadow_min_samples(2) failures
            h._record_feedback_for_packets(db, settings, [(0, audit.packet_id)], 0.0)
            db.commit()
        assert pattern.status == "retired"


# ---------------------------------------------------------------------------
# 3. Default-OFF determinism; ON differs only in feedback fields
# ---------------------------------------------------------------------------


def _strip_latency(value: Any) -> Any:
    """Mirror the stage-2/3 convention: measured latency fields are excluded
    from determinism comparisons."""
    if isinstance(value, dict):
        return {key: _strip_latency(item) for key, item in value.items() if "latency" not in key}
    if isinstance(value, list):
        return [_strip_latency(item) for item in value]
    return value


def test_record_feedback_default_off_determinism_and_on_differs_only_in_feedback(h, scratch_dir):
    """Two runs WITHOUT --record-feedback produce byte-identical artifacts
    (existing contract); with the flag ON the artifacts differ ONLY in the
    new feedback fields."""
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()

    out_off_a = scratch_dir / "off-a"
    out_off_b = scratch_dir / "off-b"
    out_on = scratch_dir / "on"
    run_off_a = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_off_a), "--variants", "v09,v10"], fake_home
    )
    assert run_off_a.returncode == 0, run_off_a.stderr
    run_off_b = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_off_b), "--variants", "v09,v10"], fake_home
    )
    assert run_off_b.returncode == 0, run_off_b.stderr
    run_on = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_on), "--variants", "v09,v10", "--record-feedback"], fake_home
    )
    assert run_on.returncode == 0, run_on.stderr

    def _load(path: Path) -> dict[str, Any]:
        return json.loads((path / "model_eval_harness.json").read_text())

    off_a, off_b, on = _load(out_off_a), _load(out_off_b), _load(out_on)

    # default OFF: byte-identical modulo measured latency (existing contract)
    assert _strip_latency(off_a) == _strip_latency(off_b)
    assert json.dumps(_strip_latency(off_a), sort_keys=True).encode() == json.dumps(
        _strip_latency(off_b), sort_keys=True
    ).encode()
    assert (out_off_a / "model_eval_harness.md").read_bytes() == (out_off_b / "model_eval_harness.md").read_bytes()

    # ON vs OFF: the ONLY difference is the additive feedback key
    assert "feedback" not in off_a
    assert "feedback" in on
    assert on["feedback"]["recorded"] is True
    on_without_feedback = {key: value for key, value in on.items() if key != "feedback"}
    assert _strip_latency(on_without_feedback) == _strip_latency(off_a)
    # and the .md artifact is byte-identical (feedback is JSON-only)
    assert (out_on / "model_eval_harness.md").read_bytes() == (out_off_a / "model_eval_harness.md").read_bytes()


def test_record_feedback_on_runs_are_deterministic(h, scratch_dir):
    """Two runs WITH --record-feedback produce byte-identical feedback
    summaries (modulo measured latency in the rows)."""
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_a = scratch_dir / "on-a"
    out_b = scratch_dir / "on-b"
    for out in (out_a, out_b):
        completed = _run_cli_subprocess(
            ["--adapters", str(cfg), "--output", str(out), "--variants", "v09,v10", "--record-feedback"], fake_home
        )
        assert completed.returncode == 0, completed.stderr
    art_a = json.loads((out_a / "model_eval_harness.json").read_text())
    art_b = json.loads((out_b / "model_eval_harness.json").read_text())
    assert art_a["feedback"] == art_b["feedback"]
    assert _strip_latency(art_a) == _strip_latency(art_b)


# ---------------------------------------------------------------------------
# 4. Out-of-range task_success and unknown packet ids (mirror runtime.feedback)
# ---------------------------------------------------------------------------


def test_feedback_rejects_out_of_range_task_success(h, isolated_db):
    """task_success outside [0, 1] raises a clear ValueError (mirror
    runtime.feedback), validated BEFORE any packet lookup."""
    settings = _pattern_settings()
    with SessionLocal() as db:
        for bad in (1.5, -0.1):
            with pytest.raises(ValueError, match=r"task_success must be in \[0, 1\]"):
                h._record_feedback_for_packets(db, settings, [(0, "Punknown")], bad)


def test_feedback_unknown_packet_raises_key_error(h, isolated_db):
    """An unknown packet_id raises KeyError (mirror runtime.feedback)."""
    settings = _pattern_settings()
    with SessionLocal() as db:
        with pytest.raises(KeyError):
            h._record_feedback_for_packets(db, settings, [(0, "P" + "0" * 32)], 0.5)


# ---------------------------------------------------------------------------
# 5. ZERO wire-byte change with --record-feedback ON
# ---------------------------------------------------------------------------


def test_record_feedback_zero_wire_byte_change(h, scratch_dir):
    """With --record-feedback ON, the AIFENCE variants' wire bytes are
    byte-identical to the default run (feedback is post-hoc DB bookkeeping,
    never touches encode)."""
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_off = scratch_dir / "wire-off"
    out_on = scratch_dir / "wire-on"
    run_off = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_off), "--variants", "v09,v10,v11,v12"], fake_home
    )
    assert run_off.returncode == 0, run_off.stderr
    run_on = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_on), "--variants", "v09,v10,v11,v12", "--record-feedback"],
        fake_home,
    )
    assert run_on.returncode == 0, run_on.stderr

    rows_off = json.loads((out_off / "model_eval_harness.json").read_text())["rows"]
    rows_on = json.loads((out_on / "model_eval_harness.json").read_text())["rows"]
    assert len(rows_off) == len(rows_on)

    def _wire(row: dict[str, Any]) -> tuple[str, str, str, int]:
        return (row["variant"], row["receiver_model"], row["receiver_state"], row["wire_bytes"])

    wire_off = {_wire(row) for row in rows_off}
    wire_on = {_wire(row) for row in rows_on}
    assert wire_off == wire_on
    # the per-turn wire bytes are individually identical (no aggregate masking)
    for row_off, row_on in zip(rows_off, rows_on, strict=True):
        assert row_off["variant"] == row_on["variant"]
        assert row_off["turn"] == row_on["turn"]
        assert row_off["wire_bytes"] == row_on["wire_bytes"]


def test_unknown_variant_leaves_no_output_dir(scratch_dir):
    """Adversary finding #1: an unknown --variants id (v99) exits 2 via the
    unknown-variant ValueError inside run_harness -- and the --output dir
    must NOT be left behind (the mkdir happens only AFTER run_harness has
    succeeded, just before the artifacts are written, so no validation/error
    path leaves an empty dir). Mirrors
    test_model_eval_harness.py's test_missing_adapters_leaves_no_output_dir
    / test_empty_variants_leaves_no_output_dir, run via a fresh subprocess
    (the prebound-engine guard makes in-process happy-path runs impossible).
    """
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_dir = scratch_dir / "must-not-exist"
    completed = _run_cli_subprocess(
        ["--adapters", str(cfg), "--output", str(out_dir), "--variants", "v99"], fake_home
    )
    assert completed.returncode == 2
    assert "unknown variant id" in completed.stderr
    assert not out_dir.exists()
