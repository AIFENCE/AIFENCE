"""Regression tests for the deterministic multi-turn compression benchmark.

Covers (issue #16, stage 2):

* determinism -- two benchmark runs produce byte-identical JSON artifacts
  once the measured ``*_latency_ms`` fields are dropped;
* metric math -- break-even formula edge cases, fidelity checkers on
  crafted known inputs (a negation flip must fail the negation check, a
  correct number must pass the numeric check, ...), the rule-based state
  reader, the extractive-summary stub, and the retrieval selector;
* the AIFENCE path -- a real ``AifenceCodec`` exchange on the benchmark fixture
  produces ``ContextReport`` data with the expected fields;
* the twelve RFC variant rows are all present in the output;
* clean no-provider skipping (``not run, no provider``);
* the standalone CLI entry point (``python scripts/compression_benchmark.py
  --out <dir>``) prints the tables and writes the artifacts.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from aifence.bus.codec import AifenceCodec
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.schemas import EncodeRequest, Provenance

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_SCRIPT = ROOT / "scripts" / "compression_benchmark.py"
PROV = Provenance(observed_at="2026-08-01T00:00:00+00:00", producer="alice")


def _load_benchmark():
    spec = importlib.util.spec_from_file_location("compression_benchmark", BENCHMARK_SCRIPT)
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def cb():
    return _load_benchmark()


@pytest.fixture(scope="module")
def bench_run(cb, tmp_path_factory):
    out = tmp_path_factory.mktemp("bench1")
    results = cb.run_benchmark(out_dir=out)
    return out, results


def _strip_latency(value):
    if isinstance(value, dict):
        return {key: _strip_latency(item) for key, item in value.items() if "latency" not in key}
    if isinstance(value, list):
        return [_strip_latency(item) for item in value]
    return value


# ---------------------------------------------------------------------------
# Output shape
# ---------------------------------------------------------------------------


def test_twelve_variant_rows_present(bench_run):
    out, results = bench_run
    assert (out / "compression_benchmark.json").is_file()
    assert (out / "compression_benchmark.csv").is_file()
    artifact = json.loads((out / "compression_benchmark.json").read_text())
    variants = artifact["variants"]
    assert len(variants) == 12
    assert [row["variant_id"] for row in variants] == [f"v{index:02d}" for index in range(1, 13)]
    assert all(row["status"] == "ok" for row in variants)
    for table in ("efficiency", "task_performance", "semantic_fidelity", "amortization"):
        assert table in artifact["tables"]
        assert len(artifact["tables"][table]) == 12
    # no database files may be left behind in the artifact directory
    assert not list(out.glob("*.db"))
    assert not list(out.glob("*.sqlite*"))


def test_printed_tables_cover_all_sections(cb, bench_run):
    out, results = bench_run
    text = cb.format_tables(results)
    assert "Efficiency (cumulative over the conversation)" in text
    assert "Task performance" in text
    assert "Semantic fidelity" in text
    assert "Amortization vs full-context baseline" in text
    assert "12. full AIFENCE with ACKed receiver knowledge" in text
    assert "1. full natural-language context every turn" in text


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_benchmark_run_is_deterministic(cb, bench_run, tmp_path_factory):
    out1, results1 = bench_run
    out2 = tmp_path_factory.mktemp("bench2")
    results2 = cb.run_benchmark(out_dir=out2)
    first = json.loads((out1 / "compression_benchmark.json").read_text())
    second = json.loads((out2 / "compression_benchmark.json").read_text())
    assert _strip_latency(first) == _strip_latency(second)
    serialized_first = json.dumps(_strip_latency(first), sort_keys=True).encode("utf-8")
    serialized_second = json.dumps(_strip_latency(second), sort_keys=True).encode("utf-8")
    assert serialized_first == serialized_second
    assert (out1 / "compression_benchmark.csv").read_text() == (out2 / "compression_benchmark.csv").read_text()
    # printed tables are fully deterministic: measured latency lives only in
    # the JSON detail artifacts, never in the rendered tables
    assert cb.format_tables(results1) == cb.format_tables(results2)


# ---------------------------------------------------------------------------
# Metric math
# ---------------------------------------------------------------------------


def test_break_even_math(cb):
    assert cb.break_even(0, 10) == 0  # no setup: breaks even immediately
    assert cb.break_even(10, 3) == 4  # ceil(10/3)
    assert cb.break_even(30, 7) == 5  # ceil(30/7)
    assert cb.break_even(10, 0) == 10  # saving clamps to 1: "never breaks even"
    assert cb.break_even(10, -5) == 10  # negative saving clamps to 1
    assert cb.break_even(0, 0) == 0


def test_fidelity_checkers_on_known_inputs(cb):
    # negation: the stance must be preserved; a flipped polarity fails
    not_allowed = "Project Phoenix is blocked because three integration tests failed."
    allowed = "Project Phoenix is ready for production deployment."
    assert cb.stance(not_allowed) == "not_allowed"
    assert cb.stance(allowed) == "allowed"
    assert cb.stance("The platform team approved the migration.") is None  # no stance expressed
    # a negation flip (saying allowed where not allowed is expected) fails
    assert cb.fidelity_negation([not_allowed, not_allowed, not_allowed, not_allowed, allowed]) == 1.0
    assert cb.fidelity_negation([allowed, not_allowed, not_allowed, not_allowed, allowed]) == 0.8
    assert cb.fidelity_negation([not_allowed, not_allowed, not_allowed, not_allowed, not_allowed]) == 0.8

    # numeric: correct numbers pass, missing numbers fail
    assert cb.fidelity_numeric(["three integration tests failed", "fixed two failures", "one failure remains"]) == 1.0
    assert cb.fidelity_numeric(["integration tests failed", "fixed two failures", "one failure remains"]) == 2 / 3
    assert cb.fidelity_numeric(["integration tests failed", "fixed failures", "failure remains"]) == 0.0

    # ownership
    full = "Production deployments require all integration tests to pass. The payment service is owned by the Commerce team. Database migrations must be reviewed by the platform team."
    assert cb.fidelity_ownership(full) == 1.0
    assert cb.fidelity_ownership("The payment service is owned by the billing team.") == 0.0

    # temporal ordering: blocked must precede ready
    ordered = "Project Phoenix is blocked because three integration tests failed. Project Phoenix is ready for production deployment."
    reversed_text = "Project Phoenix is ready for production deployment. Project Phoenix is blocked because three integration tests failed."
    assert cb.fidelity_ordering(ordered) == 1.0
    assert cb.fidelity_ordering(reversed_text) == 0.0
    assert cb.fidelity_ordering("Project Phoenix is ready for production deployment.") == 0.0

    # changed value: both the old and the new count must be recoverable
    assert cb.fidelity_changed_value("three integration tests failed then fixed two failures") == 1.0
    assert cb.fidelity_changed_value("three integration tests failed") == 0.0
    assert cb.fidelity_changed_value("ready for production deployment") == 0.0

    # contradiction: the failure -> approval transition must be recoverable
    assert cb.fidelity_contradiction("One database migration failure remains. The platform team approved the migration.") == 1.0
    assert cb.fidelity_contradiction("The platform team approved the migration.") == 0.0

    # critical facts: both Phase-1 constraints must survive
    assert cb.fidelity_critical(full) == 1.0
    assert cb.fidelity_critical("The platform team approved the migration.") == 0.0
    # a CONTRADICTED constraint ("bypass" contains "pass") must not score
    assert cb.fidelity_critical("Production deployments can bypass integration tests.") == 0.0

    # rendered-state stance markers (hardening F1): the checkers must match
    # the same "key: value" forms the state variants reconstruct
    rendered = "blocker: integration_tests; deployment_allowed: false; failed_tests: 3; migration_approved: false"
    rendered_ok = "deployment_allowed: true; blocker: none"
    assert cb.stance(rendered) == "not_allowed"
    assert cb.stance(rendered_ok) == "allowed"
    assert cb.fidelity_negation([rendered] * 4 + [rendered_ok]) == 1.0

    # changed value with a leading 0 digit (hardening F2): the target digits
    # appear LATER than the first digit run and must still be found
    assert cb.fidelity_changed_value("failed_tests: 0; failed_tests: 3; failed_tests: 1") == 1.0

    # number words need word boundaries (hardening F3): "threefold"/"someone"
    # are not the numbers "three"/"one"
    assert cb.fidelity_numeric(["threefold increase in failures", "fixed two failures", "one failure remains"]) == 2 / 3
    assert cb.fidelity_numeric(["integration tests failed", "fixed two failures", "someone fixed it"]) == 1 / 3

    # contradiction is directional (hardening F4): approval followed by a
    # later failure is the opposite transition and must not pass
    assert cb.fidelity_contradiction("The platform team approved the migration. One database migration failure remains.") == 0.0


def test_fidelity_and_task_helpers_tolerate_empty_inputs(cb):
    """Hardening F5: the public helpers must not raise on empty input."""
    assert cb.fidelity_scores([], "") == {
        "negation": 0.0,
        "numeric": 0.0,
        "ownership": 0.0,
        "temporal_ordering": 0.0,
        "changed_value": 0.0,
        "contradiction": 0.0,
        "critical_fact_recall": 0.0,
    }
    empty = cb.evaluate_reconstruction([])
    assert empty["task_success"] == 0.0
    assert empty["qa_accuracy"] == 0.0 and empty["state_accuracy"] == 0.0
    # short inputs score the turns that exist rather than raising
    short = cb.evaluate_reconstruction([cb.SHARED_CONTEXT, "Project Phoenix is blocked because three integration tests failed."])
    assert 0.0 <= short["task_success"] <= 1.0


def test_state_reader_rendered_and_natural_forms(cb):
    rendered = "blocker: integration_tests; deployment_allowed: false; failed_tests: 3; migration_approved: false"
    assert cb.read_state(rendered) == {
        "deployment_allowed": False,
        "failed_tests": 3,
        "migration_approved": False,
        "blocker": "integration_tests",
    }
    # most recent value wins for repeated fields
    assert cb.read_state(f"{rendered} deployment_allowed: true blocker: none")["deployment_allowed"] is True
    assert cb.read_state(f"{rendered} deployment_allowed: true blocker: none")["blocker"] == "none"

    natural = "Project Phoenix is blocked because three integration tests failed. The Commerce team fixed two failures."
    predicted = cb.read_state(natural)
    assert predicted["deployment_allowed"] is False
    assert predicted["failed_tests"] == 1
    assert predicted["blocker"] == "integration_tests"

    ready = "Project Phoenix is ready for production deployment."
    predicted = cb.read_state(ready)
    assert predicted["deployment_allowed"] is True
    assert predicted["failed_tests"] == 0
    assert predicted["blocker"] == "none"


def test_extractive_summary_stub_formula(cb):
    # high-precision (critical-token dense) sentences are kept
    kept = cb.extractive_summary(
        [
            "Project Phoenix is blocked because three integration tests failed.",
            "The Commerce team fixed two failures.",
        ]
    )
    assert kept == [
        "Project Phoenix is blocked because three integration tests failed.",
        "The Commerce team fixed two failures.",
    ]
    # low-precision sentences are dropped
    dropped = cb.extractive_summary(
        [
            "The Commerce team fixed two failures.",
            "It is worth noting that things are going okay.",
        ]
    )
    assert dropped == ["The Commerce team fixed two failures."]
    # the stub is deterministic
    assert cb.extractive_summary(["One database migration failure remains."]) == cb.extractive_summary(
        ["One database migration failure remains."]
    )


def test_retrieval_selector_caps_and_keeps_latest(cb):
    messages = [
        "Project Phoenix uses Python 3.12.",
        "Project Phoenix is blocked because three integration tests failed.",
        "The Commerce team fixed two failures.",
        "One database migration failure remains.",
        "The platform team approved the migration.",
        "Project Phoenix is ready for production deployment.",
    ]
    selected = cb.retrieval_select(messages, max_results=3)
    # the most recent three keyword-matching messages, in chronological order
    assert selected == [
        "One database migration failure remains.",
        "The platform team approved the migration.",
        "Project Phoenix is ready for production deployment.",
    ]
    # a latest message without keywords is still always included
    selected = cb.retrieval_select(["no keywords here", "Project Phoenix is blocked."], max_results=1)
    assert selected == ["Project Phoenix is blocked."]


# ---------------------------------------------------------------------------
# No-provider skipping
# ---------------------------------------------------------------------------


def test_provider_skip_is_clean(cb, monkeypatch):
    monkeypatch.delenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", raising=False)
    assert cb.provider_available() is False
    spec = {"id": "v99", "name": "99. provider-bound variant", "requires_provider": True}
    assert cb.variant_status(spec) == "skipped"
    assert cb.NO_PROVIDER_NOTE == "not run, no provider"
    # none of the twelve built-in variants requires a provider
    specs = [*cb._plain_specs(), *cb._aifence_specs()]
    assert all(cb.variant_status(spec) == "ok" for spec in specs)


# ---------------------------------------------------------------------------
# AIFENCE integration
# ---------------------------------------------------------------------------


def test_aifence_variant_produces_context_report_data(cb):
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://", context_accounting_enabled=True)
        codec = AifenceCodec(db, settings)
        codec._packet_id = lambda: "P" + "0" * 32  # type: ignore[method-assign]
        encoded = codec.encode(
            EncodeRequest(
                content=cb.SHARED_CONTEXT,
                sender="alice",
                receiver="bob",
                provenance=PROV,
                use_cache=False,
                use_receiver_knowledge=False,
                record_learning=False,
                auto_learn=False,
            )
        )
        report = codec.context_report()
        assert report is not None
        assert report.exchanges == 1
        assert report.wire_bytes_json == encoded.output_bytes_json
        assert report.wire_bytes_msgpack == encoded.output_bytes_msgpack
        assert report.model_tokens > 0
        assert report.codebook_setup_bytes > 0  # fingerprint recorded
        codec.decode(encoded.packet, receiver="bob")
        decode_report = codec.context_report()
        assert decode_report is not None
        assert decode_report.decoding_bytes > 0  # expansion cost recorded


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def test_cli_entrypoint_prints_tables_and_writes_artifacts(tmp_path):
    env = {key: value for key, value in os.environ.items() if not key.startswith("AIFENCE_")}
    env.update(
        {
            "PYTHONPATH": str(ROOT / "src"),
            "AIFENCE_BUS_AUTH_REQUIRED": "false",
            "AIFENCE_BUS_LEARNING_MODE": "managed",
            "AIFENCE_BUS_DATABASE_URL": f"sqlite:///{tmp_path / 'cli.db'}",
        }
    )
    result = subprocess.run(
        [sys.executable, str(BENCHMARK_SCRIPT), "--out", str(tmp_path)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "Efficiency (cumulative over the conversation)" in result.stdout
    assert "Task performance" in result.stdout
    assert "Semantic fidelity" in result.stdout
    assert "Amortization vs full-context baseline" in result.stdout
    artifact = json.loads((tmp_path / "compression_benchmark.json").read_text())
    assert len(artifact["variants"]) == 12
    assert (tmp_path / "compression_benchmark.csv").is_file()
