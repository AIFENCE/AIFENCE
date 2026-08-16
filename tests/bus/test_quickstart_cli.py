from __future__ import annotations

from fastapi.testclient import TestClient

from aifence.bus.demo_cli import run_demo
from aifence.bus.doctor_cli import run_doctor
from aifence.bus.main import app


def test_doctor_checks_full_delivery_flow() -> None:
    with TestClient(app) as client:
        results = run_doctor(client, workspace="doctor-test", check_flow=True)
        agent_results = run_doctor(
            client,
            workspace="doctor-agent-test",
            check_flow=True,
            agent_id="doctor-agent",
        )
    assert results
    assert all(result.ok for result in results), results
    assert all(result.ok for result in agent_results), agent_results
    assert {result.name for result in results} >= {
        "Service reachable",
        "Database ready",
        "Protocol compatible",
        "Test handoff sent",
        "Test context claimed",
        "Test message acknowledged",
        "Delivery lifecycle complete",
    }


def test_demo_supports_two_agents_and_one_agent() -> None:
    with TestClient(app) as client:
        two_agent = run_demo(
            client,
            workspace="demo-test-two",
            content={"status": "ready"},
            single_agent=False,
        )
        one_agent = run_demo(
            client,
            workspace="demo-test-one",
            content={"state": "remember this"},
            single_agent=True,
        )
    assert two_agent["sender"] != two_agent["receiver"]
    assert two_agent["acknowledged"] is True
    assert one_agent["sender"] == one_agent["receiver"]
    assert one_agent["acknowledged"] is True


def test_environment_lists_accept_comma_and_json(monkeypatch) -> None:
    from aifence.bus.config import Settings

    key_a = "a" * 32
    key_b = "b" * 32
    monkeypatch.setenv("SAGE_AUTH_REQUIRED", "true")
    monkeypatch.setenv("SAGE_API_KEYS", f"{key_a},{key_b}")
    monkeypatch.setenv("SAGE_ALLOWED_HOSTS", "LOCALHOST,127.0.0.1")
    comma = Settings(_env_file=None)
    assert comma.api_keys == [key_a, key_b]
    assert comma.allowed_hosts == ["localhost", "127.0.0.1"]

    monkeypatch.setenv("SAGE_API_KEYS", f'["{key_a}", "{key_b}"]')
    monkeypatch.setenv("SAGE_ALLOWED_HOSTS", '["LOCALHOST", "127.0.0.1"]')
    encoded = Settings(_env_file=None)
    assert encoded.api_keys == [key_a, key_b]
    assert encoded.allowed_hosts == ["localhost", "127.0.0.1"]
