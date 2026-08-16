from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.db_models import Contradiction
from aifence.bus.main import app
from aifence.bus.runtime import SageRuntime


def test_memory_state_and_concept_rest_workflows() -> None:
    workspace = "public-memory"
    with TestClient(app) as client:
        stored = client.post(
            "/v1/refs",
            json={
                "value": {"secret": "value", "public": 7},
                "workspace": workspace,
                "owner": "owner",
                "acl": ["reader"],
                "tier": "warm",
            },
        )
        assert stored.status_code == 200
        ref_id = stored.json()["ref"]

        resolved = client.post(
            "/v1/refs/resolve",
            json={"ref": ref_id, "actor": "reader", "workspace": workspace},
        )
        assert resolved.status_code == 200
        assert resolved.json()["value"] == {"secret": "value", "public": 7}
        assert client.get(
            f"/v1/refs/{ref_id}",
            params={"actor": "reader", "workspace": workspace},
        ).status_code == 200

        granted = client.post(
            f"/v1/refs/{ref_id}/grant",
            json={"actor": "owner", "grantee": "reviewer", "workspace": workspace},
        )
        assert granted.status_code == 200
        assert "reviewer" in granted.json()["acl"]
        policy = client.post(
            f"/v1/refs/{ref_id}/policy",
            json={"actor": "owner", "workspace": workspace, "tier": "hot"},
        )
        assert policy.status_code == 200
        assert policy.json()["tier"] == "hot"

        created = client.post(
            "/v1/states",
            json={"value": {"count": 1}, "workspace": workspace, "created_by": "owner"},
        )
        assert created.status_code == 200
        state_id = created.json()["state"]
        transitioned = client.post(
            "/v1/states/transition",
            json={
                "base": state_id,
                "value": {"count": 2},
                "mode": "target",
                "workspace": workspace,
                "created_by": "owner",
            },
        )
        assert transitioned.status_code == 200
        next_state_id = transitioned.json()["state"]
        assert transitioned.json()["parent"] == state_id
        assert client.get(
            f"/v1/states/{next_state_id}", params={"workspace": workspace}
        ).json()["value"] == {"count": 2}
        lineage = client.get(
            f"/v1/states/{next_state_id}/lineage", params={"workspace": workspace}
        )
        assert [item["revision"] for item in lineage.json()] == [1, 2]
        checkpoint = client.post(
            f"/v1/states/{next_state_id}/checkpoint", params={"workspace": workspace}
        )
        assert checkpoint.status_code == 200
        assert checkpoint.json()["state_id"] == next_state_id

        original = client.post(
            "/v1/concepts",
            json={
                "canonical": "public_surface_original",
                "codebook": "public.contracts",
                "aliases": ["surface original"],
            },
        ).json()
        replacement = client.post(
            "/v1/concepts",
            json={"canonical": "public_surface_replacement", "codebook": "public.contracts"},
        ).json()
        alias = client.post(
            f"/v1/concepts/{original['code']}/aliases", json={"alias": "legacy surface"}
        )
        assert alias.status_code == 200
        deprecated = client.post(
            f"/v1/concepts/{original['code']}/deprecate",
            json={"replacement_code": replacement["code"]},
        )
        assert deprecated.status_code == 200
        assert deprecated.json()["status"] == "deprecated"
        concepts = client.get(
            "/v1/concepts",
            params={"codebook": "public.contracts", "include_deprecated": True},
        ).json()
        assert {item["code"] for item in concepts} == {original["code"], replacement["code"]}


def test_fact_pubsub_routing_and_operational_rest_workflows() -> None:
    workspace = "public-semantic"
    with TestClient(app) as client:
        left = client.post(
            "/v1/facts",
            json={
                "workspace": workspace,
                "subject": "deploy",
                "predicate": "status",
                "object": "ready",
                "source": "planner",
            },
        )
        right = client.post(
            "/v1/facts",
            json={
                "workspace": workspace,
                "subject": "deploy",
                "predicate": "status",
                "object": "blocked",
                "source": "reviewer",
            },
        )
        assert left.status_code == right.status_code == 200
        left_id = left.json()["id"]
        right_id = right.json()["id"]
        fetched = client.get(f"/v1/facts/{left_id}", params={"workspace": workspace})
        contradiction_id = fetched.json()["contradictions"][0]
        resolved = client.post(
            f"/v1/contradictions/{contradiction_id}/resolve",
            json={"winner_fact_id": right_id, "workspace": workspace, "note": "review wins"},
        )
        assert resolved.status_code == 200
        assert resolved.json()["status"] == "resolved"

        root = client.post(
            "/v1/facts",
            json={
                "workspace": workspace,
                "subject": "release",
                "predicate": "approved",
                "object": True,
            },
        ).json()
        invalidated = client.post(
            f"/v1/facts/{root['id']}/invalidate",
            json={"workspace": workspace, "reason": "superseded"},
        )
        assert invalidated.json()["invalidated"] == [root["id"]]

        subscribed = client.post(
            "/v1/subscriptions",
            json={
                "agent": "worker",
                "workspace": workspace,
                "concepts": ["status"],
                "filters": {"status": "ready"},
                "min_confidence": 0.8,
            },
        )
        assert subscribed.status_code == 200
        published = client.post(
            "/v1/publish",
            json={
                "content": {"status": "ready"},
                "sender": "planner",
                "workspace": workspace,
                "confidence": 0.9,
            },
        )
        assert published.json()["recipients"] == ["worker"]

        registered = client.post(
            "/v1/routing/agents",
            json={
                "agent": "reviewer",
                "workspace": workspace,
                "capabilities": ["review"],
                "authority": ["production"],
                "cost_score": 0.5,
                "latency_ms": 10,
                "metadata": {"concepts": ["change"]},
            },
        )
        assert registered.status_code == 200
        route = {
            "content": {"change": "approve"},
            "workspace": workspace,
            "capability": "review",
            "authority": "production",
            "sender": "planner",
        }
        chosen = client.post("/v1/routing/choose", json=route)
        assert chosen.json()["agent"] == "reviewer"
        sent = client.post("/v1/routing/send", json=route)
        assert sent.status_code == 200
        assert sent.json()["receiver"] == "reviewer"

        identity = client.post(
            "/v1/receivers/model-identity",
            json={
                "receiver": "reviewer",
                "workspace": workspace,
                "provider": "local",
                "model": "contract-model",
                "model_version": "1",
                "runtime": "python",
                "runtime_version": "3.14",
                "configuration": {"temperature": 0},
            },
        )
        assert identity.status_code == 200
        reliability = client.get(
            "/v1/receivers/reviewer/reliability",
            params={
                "workspace": workspace,
                "model_identity_hash": identity.json()["identity_hash"],
            },
        )
        assert reliability.status_code == 200
        assert reliability.json()["status"] in {"unknown", "healthy", "degraded", "blocked"}
        assert client.get("/v1/bus/backpressure", params={"workspace": workspace}).status_code == 200
        assert client.get("/v1/codebooks/public.contracts/merkle").status_code == 200
        sync = client.post(
            "/v1/codebooks/sync", json={"namespace": "public.contracts", "remote": {}}
        )
        assert sync.status_code == 200
        assert client.post("/v1/maintenance/cleanup").status_code == 200
        assert client.get("/v1/ready").json() == {"ready": True}


def test_runtime_facade_covers_transport_memory_bus_and_semantics() -> None:
    workspace = "runtime-contract"
    runtime = SageRuntime(Settings(auth_required=False, database_url="sqlite://"))

    sent = runtime.send(
        sender="planner",
        receiver="reviewer",
        content={"status": "ready", "count": 2},
        workspace=workspace,
        run_id="runtime-run",
        source_ids=["task:1"],
        budget_tokens=1000,
    )
    received = runtime.receive(
        receiver="reviewer", wire=sent["wire"], workspace=workspace, resolve_refs=True
    )
    assert received["act"] == "report"
    assert runtime.explain(sent["packet_id"])["packet_id"] == sent["packet_id"]
    assert runtime.inspect(sent["packet_id"])["packet_id"] == sent["packet_id"]
    assert runtime.feedback(sent["packet_id"], 1.0)["task_success"] == 1.0
    with pytest.raises(ValueError):
        runtime.feedback(sent["packet_id"], 1.1)
    with pytest.raises(KeyError):
        runtime.explain("missing-packet")

    handoff = runtime.handoff(
        sender="planner",
        receiver="reviewer",
        content={"task": "review"},
        workspace=workspace,
        correlation_id="corr-1",
        priority=2,
    )
    pending = runtime.poll(receiver="reviewer", workspace=workspace)
    assert pending[0]["message_id"] == handoff["message_id"]
    runtime.ack(handoff["message_id"], receiver="reviewer", workspace=workspace)

    ref_id = runtime.memory_put(
        {"artifact": "report"},
        workspace=workspace,
        owner="planner",
        acl=["reviewer"],
        tier="warm",
    )
    assert runtime.memory_get(ref_id, actor="reviewer", workspace=workspace) == {
        "artifact": "report"
    }
    grant = runtime.memory_grant(
        ref_id,
        workspace=workspace,
        owner="planner",
        acl=["reviewer", "publisher"],
        tier="hot",
    )
    assert grant["tier"] == "hot"
    forwarded = runtime.forward_refs(
        receiver="publisher", refs=[ref_id], sender="planner", workspace=workspace
    )
    assert forwarded["strategy"] == "zero_copy"

    fact = runtime.fact_put(
        subject="release",
        predicate="status",
        object="ready",
        source="planner",
        workspace=workspace,
    )
    assert runtime.fact_invalidate(fact["id"], workspace=workspace) == [fact["id"]]
    with pytest.raises(KeyError):
        runtime.fact_invalidate("missing-fact", workspace=workspace)

    subscription_id = runtime.subscribe(
        agent="publisher", concepts=["status"], workspace=workspace
    )
    assert subscription_id.startswith("SUB")
    assert runtime.publish(
        {"status": "ready"}, sender="planner", workspace=workspace
    ) == ["publisher"]
    runtime.register_agent(
        agent="reviewer",
        capabilities=["review"],
        authority=["production"],
        workspace=workspace,
        cost_score=0.2,
        latency_ms=5,
    )
    assert runtime.route(
        {"change": "approve"},
        capability="review",
        authority="production",
        workspace=workspace,
        sender="planner",
    )["agent"] == "reviewer"

    assert runtime.patterns(codebook="runtime.contracts") == []
    assert runtime.pattern_candidates(codebook="runtime.contracts") == []
    assert runtime.observe_patterns(
        {"status": "ready", "owner": "planner"},
        codebook="runtime.contracts",
        source_ids=["task:1"],
    ) == []
    assert runtime.pattern_gc("runtime.contracts") == {
        "patterns_cooling": 0,
        "patterns_retired": 0,
    }

    with SessionLocal() as db:
        assert db.query(Contradiction).count() == 0


def test_learning_calibration_latent_and_receiver_rest_workflows() -> None:
    workspace = "public-learning"
    codebook = "public.learning"
    with TestClient(app) as client:
        observed = client.post(
            "/v1/patterns/observe",
            json={
                "content": {"cause": "timeout", "deployment": "blocked"},
                "codebook": codebook,
                "source_ids": ["incident:1"],
                "source_trust": 0.9,
                "trust_scope": "workspace",
            },
        )
        assert observed.status_code == 200
        candidates = client.get(
            "/v1/patterns/candidates", params={"codebook": codebook}
        )
        assert candidates.status_code == 200
        assert candidates.json()[0]["occurrence_count"] == 1
        assert client.get("/v1/patterns/missing-pattern").status_code == 404
        assert client.post(
            "/v1/patterns/missing-pattern/status", json={"status": "active"}
        ).status_code == 404
        assert client.post(
            "/v1/patterns/missing-pattern/counterfactual",
            json={
                "full_success": 1.0,
                "compressed_success": 1.0,
                "semantic_fidelity": 1.0,
                "validation_id": "contract",
            },
        ).status_code == 404
        assert client.post(
            "/v1/patterns/missing-pattern/promote-namespace",
            params={"target": "public.promoted"},
        ).status_code == 404
        assert client.post("/v1/patterns/gc", params={"codebook": codebook}).json() == {
            "patterns_cooling": 0,
            "patterns_retired": 0,
        }

        calibration = client.post(
            "/v1/calibration/record",
            json={
                "predicted": 0.8,
                "observed": 1.0,
                "receiver": "worker",
                "model": "contract-model",
                "task_family": "routing",
                "workspace": workspace,
            },
        )
        assert calibration.status_code == 200
        assert calibration.json()["sample_count"] == 1
        report = client.get(
            "/v1/calibration",
            params={
                "predicted": 0.8,
                "receiver": "worker",
                "model": "contract-model",
                "task_family": "routing",
                "workspace": workspace,
            },
        )
        assert report.status_code == 200
        assert report.json()["sample_count"] == 1

        packed = client.post(
            "/v1/latent/pack",
            json={"vector": [-1.0, 0.25, 2.0], "space": "worker:hidden:v1"},
        )
        assert packed.status_code == 200
        unpacked = client.post("/v1/latent/unpack", json={"packet": packed.json()})
        assert unpacked.status_code == 200
        assert unpacked.json() == pytest.approx([-1.0, 0.25, 2.0], abs=0.02)
        corrupt = packed.json()
        corrupt["checksum"] = "0" * 64
        assert client.post("/v1/latent/unpack", json={"packet": corrupt}).status_code == 422

        negotiated = client.post(
            "/v1/negotiate",
            json={
                "receiver": "worker",
                "workspace": workspace,
                "known_codes": [],
                "capabilities": {
                    "protocol_versions": ["sage/0.2"],
                    "max_packet_bytes": 4096,
                    "supports_patterns": False,
                },
            },
        )
        assert negotiated.status_code == 200
        assert negotiated.json()["negotiated"]["max_packet_bytes"] == 4096
        knowledge = client.get(
            "/v1/receivers/worker", params={"workspace": workspace}
        )
        assert knowledge.status_code == 200
        assert knowledge.json()["capabilities"]["supports_patterns"] is False
        assert client.get(
            "/v1/receivers/missing", params={"workspace": workspace}
        ).status_code == 404


def test_runtime_conformance_facade() -> None:
    report = SageRuntime(Settings(auth_required=False, database_url="sqlite://")).conform(
        fuzz_iterations=3
    )
    assert report["ok"] is True
    assert report["tck"]["ok"] is True
    assert report["wire_fuzz"]["ok"] is True
