from fastapi.testclient import TestClient

from aifence.bus.main import app


def test_health_and_round_trip():
    with TestClient(app) as client:
        assert client.get("/health/live").status_code == 200
        register = client.post("/v1/concepts", json={"canonical": "screen_damage"})
        assert register.status_code == 200
        enc = client.post("/v1/encode", json={"content": {"screen_damage": True}})
        assert enc.status_code == 200
        packet = enc.json()["packet"]
        dec = client.post("/v1/decode", json={"packet": packet, "resolve_refs": True})
        assert dec.status_code == 200
        assert dec.json()["concepts"][0]["canonical"] == "screen_damage"


def test_negotiation_returns_fingerprint():
    with TestClient(app) as client:
        client.post("/v1/concepts", json={"canonical": "refund_requested"})
        response = client.post("/v1/negotiate", json={"known_codes": []})
        assert response.status_code == 200
        body = response.json()
        assert body["protocol_version"] == "aifence/0.2"
        assert len(body["fingerprint"]) == 24
        assert body["missing_codes"]


def test_negotiation_rejects_non_v02_peer():
    with TestClient(app) as client:
        response = client.post(
            "/v1/negotiate",
            json={"known_codes": [], "capabilities": {"protocol_versions": ["aifence/9.9"]}},
        )
        assert response.status_code == 409
        assert "aifence/0.2" in response.json()["detail"]


def test_bearer_auth_when_enabled():
    from aifence.bus.config import get_settings

    settings = get_settings()
    old_required, old_keys = settings.auth_required, list(settings.api_keys)
    settings.auth_required = True
    settings.api_keys = ["test-secret-key"]
    try:
        with TestClient(app) as client:
            assert client.get("/v1/concepts").status_code == 401
            ok = client.get("/v1/concepts", headers={"Authorization": "Bearer test-secret-key"})
            assert ok.status_code == 200
    finally:
        settings.auth_required = old_required
        settings.api_keys = old_keys


def test_agent_scoped_key_cannot_impersonate_or_use_control_plane():
    from aifence.bus.config import get_settings

    settings = get_settings()
    old_required = settings.auth_required
    old_service = list(settings.api_keys)
    old_agents = dict(settings.agent_keys)
    settings.auth_required = True
    settings.api_keys = ["s" * 40]
    settings.agent_keys = {"a" * 40: "team:planner"}
    try:
        headers = {"Authorization": f"Bearer {'a' * 40}"}
        with TestClient(app) as client:
            own = client.get("/v1/bus/pull/planner?workspace=team", headers=headers)
            assert own.status_code == 200
            other = client.get("/v1/bus/pull/reviewer?workspace=team", headers=headers)
            assert other.status_code == 403
            wrong_workspace = client.get("/v1/bus/pull/planner?workspace=other", headers=headers)
            assert wrong_workspace.status_code == 403
            control = client.get("/v1/concepts", headers=headers)
            assert control.status_code == 403
    finally:
        settings.auth_required = old_required
        settings.api_keys = old_service
        settings.agent_keys = old_agents


def test_agent_scoped_semantic_memory_and_inspector_are_workspace_bound():
    from aifence.bus.config import get_settings

    settings = get_settings()
    old_required = settings.auth_required
    old_service = list(settings.api_keys)
    old_agents = dict(settings.agent_keys)
    settings.auth_required = True
    settings.api_keys = ["s" * 40]
    settings.agent_keys = {"a" * 40: "team:planner"}
    agent_headers = {"Authorization": f"Bearer {'a' * 40}"}
    service_headers = {"Authorization": f"Bearer {'s' * 40}"}
    try:
        with TestClient(app) as client:
            own = client.post(
                "/v1/facts",
                headers=agent_headers,
                json={"workspace": "team", "subject": "task", "predicate": "status", "object": "ready"},
            )
            assert own.status_code == 200
            assert own.json()["source"] == "planner"
            wrong_workspace = client.post(
                "/v1/facts",
                headers=agent_headers,
                json={"workspace": "other", "subject": "task", "predicate": "status", "object": "ready"},
            )
            assert wrong_workspace.status_code == 403
            impersonate = client.post(
                "/v1/facts",
                headers=agent_headers,
                json={"workspace": "team", "source": "reviewer", "subject": "task", "predicate": "status", "object": "ready"},
            )
            assert impersonate.status_code == 403

            sent = client.post(
                "/v1/send",
                headers=service_headers,
                json={"workspace": "team", "sender": "researcher", "receiver": "planner", "content": {"result": "ok"}, "use_cache": False},
            )
            assert sent.status_code == 200
            packet_id = sent.json()["packet"]["id"]
            allowed = client.get(f"/v1/inspect/{packet_id}", headers=agent_headers)
            assert allowed.status_code == 200

            foreign = client.post(
                "/v1/send",
                headers=service_headers,
                json={"workspace": "team", "sender": "researcher", "receiver": "reviewer", "content": {"result": "private"}, "use_cache": False},
            )
            foreign_id = foreign.json()["packet"]["id"]
            denied = client.get(f"/v1/inspect/{foreign_id}", headers=agent_headers)
            assert denied.status_code == 404
    finally:
        settings.auth_required = old_required
        settings.api_keys = old_service
        settings.agent_keys = old_agents


def test_bus_context_claims_decodes_and_batch_acknowledges():
    with TestClient(app) as client:
        handoff = client.post(
            "/v1/bus/handoff",
            json={
                "sender": "researcher",
                "receiver": "planner",
                "workspace": "team",
                "content": {"status": "ready", "count": 3},
            },
        )
        assert handoff.status_code == 200
        message_id = handoff.json()["message_id"]

        context = client.get("/v1/bus/context/planner?workspace=team&budget_tokens=1200")
        assert context.status_code == 200
        items = context.json()
        assert len(items) == 1
        assert items[0]["message_id"] == message_id
        assert items[0]["receiver"] == "planner"
        assert items[0]["act"] == "handoff"
        assert items[0]["concepts"] or items[0]["literals"] or items[0]["references"]

        ack = client.post(
            "/v1/bus/ack-batch",
            json={"message_ids": [message_id], "receiver": "planner", "workspace": "team"},
        )
        assert ack.status_code == 200
        assert ack.json()[0]["status"] == "acked"
        assert client.get("/v1/bus/context/planner?workspace=team").json() == []


def test_agent_cannot_delegate_unowned_reference_or_negotiate_other_codebook():
    from aifence.bus.config import get_settings

    settings = get_settings()
    old_required = settings.auth_required
    old_service = list(settings.api_keys)
    old_agents = dict(settings.agent_keys)
    settings.auth_required = True
    settings.api_keys = ["s" * 40]
    settings.agent_keys = {"a" * 40: "team:planner"}
    agent_headers = {"Authorization": f"Bearer {'a' * 40}"}
    service_headers = {"Authorization": f"Bearer {'s' * 40}"}
    try:
        with TestClient(app) as client:
            stored = client.post(
                "/v1/refs",
                headers=service_headers,
                json={
                    "workspace": "team",
                    "acl": ["planner"],
                    "value": {"classification": "internal"},
                },
            )
            assert stored.status_code == 200
            ref_id = stored.json()["ref"]

            read = client.get(
                f"/v1/refs/{ref_id}?workspace=team",
                headers=agent_headers,
            )
            assert read.status_code == 200

            delegate = client.post(
                f"/v1/refs/{ref_id}/grant",
                headers=agent_headers,
                json={"workspace": "team", "grantee": "reviewer"},
            )
            assert delegate.status_code == 403

            foreign_codebook = client.post(
                "/v1/negotiate",
                headers=agent_headers,
                json={"workspace": "team", "receiver": "planner", "codebook": "private.other"},
            )
            assert foreign_codebook.status_code == 403
    finally:
        settings.auth_required = old_required
        settings.api_keys = old_service
        settings.agent_keys = old_agents


def test_integration_configuration_requires_concrete_connection_values():
    with TestClient(app) as client:
        response = client.get("/v1/integrations/hermes")
        assert response.status_code == 422


def test_transport_send_imports_valid_trace_headers_and_rejects_invalid_traceparent():
    from aifence.bus.main import app

    traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
    with TestClient(app) as client:
        sent = client.post(
            "/v1/transport/send",
            headers={"traceparent": traceparent, "tracestate": "vendor=value"},
            json={"sender": "researcher", "receiver": "planner", "content": {"status": "ready"}, "use_cache": False},
        )
        assert sent.status_code == 200
        assert sent.json()["wire"]["z"] == {"p": traceparent, "s": "vendor=value"}

        rejected = client.post(
            "/v1/transport/send",
            headers={"traceparent": "invalid"},
            json={"sender": "researcher", "receiver": "planner", "content": {"status": "ready"}, "use_cache": False},
        )
        assert rejected.status_code == 422
