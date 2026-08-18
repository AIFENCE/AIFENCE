from __future__ import annotations

from fastapi.testclient import TestClient

from aifence.bus.economics import benchmark_representations, score_observed_runs
from aifence.bus.main import app


def test_representation_benchmark_marks_estimates_as_estimates():
    report = benchmark_representations(
        representations={"raw_history": "hello world", "aifence": {"v": 1, "c": "g"}},
        tokenizer={"kind": "estimate", "chars_per_token": 4},
        task_success={"raw_history": 1.0, "aifence": 1.0},
        price={"input_per_million": 10.0, "output_per_million": 0.0},
    )
    assert report["tokenizer"]["exact"] is False
    assert report["warning"]
    assert all(row["cost"] >= 0 for row in report["strategies"])


def test_observed_run_scoring_is_cost_per_success_not_compression_ratio():
    report = score_observed_runs(
        [
            {"strategy": "raw", "input_tokens": 1000, "output_tokens": 100, "task_success": 1.0},
            {"strategy": "aifence", "input_tokens": 100, "output_tokens": 100, "task_success": 1.0},
        ],
        {"input_per_million": 10.0, "output_per_million": 20.0},
    )
    assert report["summary"]["aifence"]["cost_per_success"] < report["summary"]["raw"]["cost_per_success"]


def test_economics_api_compares_required_builtin_strategies():
    with TestClient(app) as client:
        response = client.post(
            "/v1/benchmarks/economics",
            json={
                "content": {"project": "phoenix", "blob": "x" * 5000},
                "summarized_history": "Phoenix project; large blob omitted.",
                "rag": {"project": "phoenix"},
                "budget_tokens": 100,
                "tokenizer": {"kind": "estimate", "chars_per_token": 4},
                "task_success": {"raw_history": 1.0, "aifence": 1.0},
                "price": {"input_per_million": 5.0, "output_per_million": 15.0},
            },
        )
        assert response.status_code == 200, response.text
        body = response.json()
        names = {row["strategy"] for row in body["strategies"]}
        assert {"raw_history", "summarized_history", "rag", "json_state", "state_refs", "aifence", "aifence_bus_learned", "aifence_bus_patterns", "aifence_bus_receiver"} <= names
        assert body["methodology"]["task_success"].startswith("caller-observed")
        assert body["methodology"]["learning_side_effects"] == "disabled for benchmark encodes"


def test_production_http_tokenizer_requires_allowlist():
    from aifence.bus.config import Settings
    from aifence.bus.db import SessionLocal
    from aifence.bus.economics import run_aifence_economics_benchmark
    from aifence.bus.schemas import EconomicsBenchmarkRequest

    req = EconomicsBenchmarkRequest.model_validate({
        "content": {"x": 1},
        "tokenizer": {"kind": "http", "endpoint": "https://tokenizer.invalid/count"},
    })
    with SessionLocal() as db:
        settings = Settings(
            env="production",
            database_url="postgresql+psycopg://aifence:secret@db/aifence",
            auth_required=True,
            api_keys=["s" * 32],
            allowed_hosts=["aifence.invalid"],
            auto_create_schema=False,
            docs_enabled=False,
        )
        try:
            run_aifence_economics_benchmark(db, settings, req)
        except ValueError as exc:
            assert "ALLOWED_HOSTS" in str(exc)
        else:
            raise AssertionError("production HTTP tokenizer should fail closed without an allowlist")
