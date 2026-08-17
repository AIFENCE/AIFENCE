# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pluggable broker transports for fanning out semantic handoffs.

The durable bus is the source of truth: a handoff is committed to the database
before anything is published. A transport is a *fan-out* on top of that record,
so enterprise deployments can carry the semantic state layer over Kafka,
RabbitMQ or Redis without the fence depending on a broker being reachable.

Two invariants follow from that ordering:

* **Publication never invents delivery.** A transport failure is reported, not
  swallowed into a success, and never rolls back the durable record.
* **Publication is not the delivery guarantee.** Receivers may still claim from
  the durable bus; the broker is an accelerator, not a replacement.

Broker clients are imported lazily inside each adapter so the dependency is
required only when that transport is actually configured.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HandoffEvent:
    """The published projection of a durable handoff.

    Deliberately carries the message identity and routing metadata rather than
    the payload: subscribers resolve content from the bus, so a broker outage or
    a misconfigured topic cannot leak semantic content.
    """

    message_id: str
    receiver: str
    sender: str | None
    workspace: str
    correlation_id: str | None = None
    wire_bytes: int = 0
    strategy: str | None = None

    def to_json(self) -> str:
        return json.dumps(
            {
                "message_id": self.message_id,
                "receiver": self.receiver,
                "sender": self.sender,
                "workspace": self.workspace,
                "correlation_id": self.correlation_id,
                "wire_bytes": self.wire_bytes,
                "strategy": self.strategy,
            },
            separators=(",", ":"),
            sort_keys=True,
        )


@runtime_checkable
class Transport(Protocol):
    """A fan-out target for committed handoffs."""

    name: str

    def publish(self, event: HandoffEvent) -> None: ...

    def close(self) -> None: ...


class NullTransport:
    """The default: the durable bus alone, with no broker fan-out."""

    name = "null"

    def publish(self, event: HandoffEvent) -> None:
        return None

    def close(self) -> None:
        return None


@dataclass
class MemoryTransport:
    """An in-process transport, for tests and single-node deployments."""

    name: str = "memory"
    published: list[HandoffEvent] = field(default_factory=list)

    def publish(self, event: HandoffEvent) -> None:
        self.published.append(event)

    def close(self) -> None:
        self.published.clear()


class RedisTransport:
    """Publishes to a Redis Stream (``XADD``), which is replayable and bounded."""

    name = "redis"

    def __init__(self, url: str, stream: str = "aifence.handoffs", maxlen: int = 100_000) -> None:
        try:
            import redis
        except ImportError as exc:  # pragma: no cover - exercised via the extra
            raise RuntimeError("the redis transport requires the 'redis' extra") from exc
        self._client = redis.Redis.from_url(url)
        self._stream = stream
        self._maxlen = maxlen

    def publish(self, event: HandoffEvent) -> None:
        self._client.xadd(
            self._stream,
            {"event": event.to_json()},
            maxlen=self._maxlen,
            approximate=True,
        )

    def close(self) -> None:
        self._client.close()


class KafkaTransport:
    """Publishes to a Kafka topic, keyed by receiver to preserve per-receiver order."""

    name = "kafka"

    def __init__(self, bootstrap_servers: str, topic: str = "aifence.handoffs") -> None:
        try:
            from kafka import KafkaProducer
        except ImportError as exc:  # pragma: no cover - exercised via the extra
            raise RuntimeError("the kafka transport requires the 'kafka' extra") from exc
        self._producer = KafkaProducer(
            bootstrap_servers=[s.strip() for s in bootstrap_servers.split(",") if s.strip()],
            value_serializer=lambda value: value.encode("utf-8"),
            key_serializer=lambda key: key.encode("utf-8"),
            acks="all",
            retries=3,
        )
        self._topic = topic

    def publish(self, event: HandoffEvent) -> None:
        # Keying by receiver keeps a receiver's handoffs in one partition, so
        # ordering is preserved where it is observable.
        self._producer.send(self._topic, key=event.receiver, value=event.to_json())

    def close(self) -> None:
        self._producer.flush(timeout=5)
        self._producer.close(timeout=5)


class RabbitMQTransport:
    """Publishes to a durable RabbitMQ topic exchange."""

    name = "rabbitmq"

    def __init__(self, url: str, exchange: str = "aifence.handoffs") -> None:
        try:
            import pika
        except ImportError as exc:  # pragma: no cover - exercised via the extra
            raise RuntimeError("the rabbitmq transport requires the 'rabbitmq' extra") from exc
        self._pika = pika
        self._connection = pika.BlockingConnection(pika.URLParameters(url))
        self._channel = self._connection.channel()
        self._exchange = exchange
        self._channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)

    def publish(self, event: HandoffEvent) -> None:
        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=f"handoff.{event.workspace}.{event.receiver}",
            body=event.to_json().encode("utf-8"),
            properties=self._pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )

    def close(self) -> None:
        if self._connection.is_open:
            self._connection.close()


def build_transport(backend: str, *, url: str = "", topic: str = "aifence.handoffs") -> Transport:
    """Construct the configured transport.

    Unknown backends raise rather than silently degrading to no fan-out: a
    typo in deployment configuration should fail loudly at startup.
    """
    normalized = (backend or "none").strip().lower()
    if normalized in {"", "none", "null"}:
        return NullTransport()
    if normalized == "memory":
        return MemoryTransport()
    if not url:
        raise ValueError(f"the {normalized} transport requires AIFENCE_BUS_TRANSPORT_URL")
    if normalized == "redis":
        return RedisTransport(url, stream=topic)
    if normalized == "kafka":
        return KafkaTransport(url, topic=topic)
    if normalized == "rabbitmq":
        return RabbitMQTransport(url, exchange=topic)
    raise ValueError(
        f"unsupported bus transport '{backend}'; expected none, memory, redis, kafka or rabbitmq"
    )


def publish_safely(transport: Transport, event: HandoffEvent) -> dict[str, Any]:
    """Publish, reporting failure instead of raising.

    The handoff is already durably committed by the time this runs, so a broker
    outage must not fail the request — but it must be visible in the receipt
    rather than reported as a successful fan-out.
    """
    if isinstance(transport, NullTransport):
        return {"backend": transport.name, "published": False}
    try:
        transport.publish(event)
    except Exception as exc:
        _logger.warning("handoff fan-out failed on %s transport: %s", transport.name, exc)
        return {"backend": transport.name, "published": False, "error": str(exc)}
    return {"backend": transport.name, "published": True}
