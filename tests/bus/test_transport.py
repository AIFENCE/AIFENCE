# SPDX-License-Identifier: AGPL-3.0-or-later
"""Broker fan-out for committed handoffs."""
from __future__ import annotations

import json

import pytest

from aifence.bus.transport import (
    HandoffEvent,
    MemoryTransport,
    NullTransport,
    build_transport,
    publish_safely,
)
from aifence.core.config import CoreSettings

EVENT = HandoffEvent(
    message_id="M123", receiver="agent-x", sender="fence", workspace="default", wire_bytes=42
)


def test_event_payload_carries_identity_not_content() -> None:
    payload = json.loads(EVENT.to_json())
    assert payload["message_id"] == "M123"
    assert payload["receiver"] == "agent-x"
    # Subscribers resolve content from the durable bus; a broker must not carry it.
    assert "content" not in payload and "artifact" not in payload


# --- selection ---

@pytest.mark.parametrize("backend", ["none", "null", ""])
def test_default_backend_is_no_fanout(backend: str) -> None:
    assert isinstance(build_transport(backend), NullTransport)


def test_memory_backend_records_events() -> None:
    transport = build_transport("memory")
    transport.publish(EVENT)
    assert isinstance(transport, MemoryTransport)
    assert transport.published == [EVENT]


def test_unknown_backend_fails_loudly() -> None:
    # A typo in deployment config must not silently disable fan-out.
    with pytest.raises(ValueError, match="unsupported bus transport"):
        build_transport("kafkaa", url="localhost:9092")


@pytest.mark.parametrize("backend", ["redis", "kafka", "rabbitmq"])
def test_broker_backends_require_a_url(backend: str) -> None:
    with pytest.raises(ValueError, match="requires AIFENCE_BUS_TRANSPORT_URL"):
        build_transport(backend)


# --- failure containment ---

def test_publish_failure_is_reported_not_raised() -> None:
    class _Broken(MemoryTransport):
        def publish(self, event: HandoffEvent) -> None:
            raise RuntimeError("broker down")

    result = publish_safely(_Broken(), EVENT)
    # The handoff is already durable, so the request must not fail...
    assert result["published"] is False
    # ...but the receipt must not claim a fan-out that did not happen.
    assert "broker down" in result["error"]


def test_null_transport_reports_no_publication() -> None:
    assert publish_safely(NullTransport(), EVENT) == {"backend": "null", "published": False}


def test_successful_publish_is_reported() -> None:
    assert publish_safely(MemoryTransport(), EVENT) == {"backend": "memory", "published": True}


# --- configuration validation ---

def test_settings_reject_an_unknown_transport() -> None:
    with pytest.raises(ValueError, match="AIFENCE_BUS_TRANSPORT"):
        CoreSettings(bus_transport="sqs").validate()


def test_settings_require_a_url_for_broker_transports() -> None:
    with pytest.raises(ValueError, match="requires AIFENCE_BUS_TRANSPORT_URL"):
        CoreSettings(bus_transport="redis").validate()


def test_settings_accept_a_configured_broker() -> None:
    CoreSettings(bus_transport="redis", bus_transport_url="redis://localhost:6379/0").validate()
