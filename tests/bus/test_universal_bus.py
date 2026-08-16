from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from aifence.bus.a2a_adapter import (
    SAGE_EXTENSION_URI,
    SAGE_MEDIA_TYPE,
    pack_data_part,
    unpack_data_part,
)
from aifence.bus.bus import SemanticBus
from aifence.bus.codebook import Codebook
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.integrations import config_for, profile
from aifence.bus.knowledge import KnowledgeStore


def test_handoff_is_not_learned_until_ack():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://")
        registry = Codebook(db, settings)
        concept = registry.register("global", "refund_requested")
        db.commit()

        bus = SemanticBus(db, settings)
        item = bus.handoff(receiver="planner", sender="researcher", content="refund requested")
        db.commit()

        knowledge = KnowledgeStore(db)
        assert concept.code not in knowledge.known_codes("planner")

        pulled = bus.pull(receiver="planner", claim=True)
        assert [message.id for message in pulled] == [item.id]
        db.commit()
        assert concept.code not in knowledge.known_codes("planner")

        bus.ack(item.id, receiver="planner")
        db.commit()
        assert concept.code in knowledge.known_codes("planner")
        assert bus.pending_count(receiver="planner") == 0


def test_stale_claim_is_recoverable():
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False,
            database_url="sqlite://",
            bus_claim_lease_seconds=5,
        )
        bus = SemanticBus(db, settings)
        item = bus.handoff(receiver="worker", content={"task": "review"})
        db.commit()

        first = bus.pull(receiver="worker", claim=True)
        assert len(first) == 1
        first[0].claimed_at = datetime.now(UTC) - timedelta(seconds=10)
        db.commit()

        recovered = bus.pull(receiver="worker", claim=True)
        assert [message.id for message in recovered] == [item.id]


def test_acked_message_cannot_be_nacked():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://")
        bus = SemanticBus(db, settings)
        item = bus.handoff(receiver="worker", content={"task": "review"})
        db.commit()
        bus.ack(item.id, receiver="worker")
        db.commit()
        with pytest.raises(ValueError, match="acknowledged"):
            bus.nack(item.id, receiver="worker")


def test_a2a_data_part_round_trip_and_rejects_non_v02():
    wire = {"v": 2, "c": "global", "a": "handoff", "p": {}}
    part = pack_data_part(wire)
    assert part["mediaType"] == SAGE_MEDIA_TYPE
    assert SAGE_EXTENSION_URI.startswith("urn:uuid:")
    assert part["data"]["sageProtocol"] == "sage/0.2"
    assert unpack_data_part(part) == wire
    invalid_wire = {"v": 99, "a": "handoff", "x": [1, 2]}
    with pytest.raises(ValueError, match="sage/0.2"):
        unpack_data_part({"data": {"sageProtocol": "sage/9.9", "wire": invalid_wire}, "mediaType": "application/json"})
    with pytest.raises(ValidationError):
        pack_data_part(invalid_wire)


def test_cross_vendor_profiles_share_same_core_endpoint():
    for platform in ("hermes", "openclaw", "claude", "openai", "generic"):
        p = profile(platform)
        assert p.id == platform
        cfg = config_for(platform, "https://sage.invalid", agent_id="agent-7")
        assert cfg.config["sage_url"] == "https://sage.invalid"
        assert cfg.config["mcp_url"] == "https://sage.invalid/mcp"


def test_pull_respects_receiver_injection_budget():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://")
        bus = SemanticBus(db, settings)
        first = bus.handoff(receiver="budgeted", content="first")
        second = bus.handoff(receiver="budgeted", content="second")
        first.estimated_tokens = 10
        second.estimated_tokens = 10
        db.commit()
        pulled = bus.pull(receiver="budgeted", claim=False, budget_tokens=10)
        assert len(pulled) == 1
