from __future__ import annotations

import json
import sys
from contextlib import AbstractContextManager
from pathlib import Path
from types import TracebackType
from typing import Any

import pytest
from pydantic import ValidationError

from aifence.bus import inspect_cli, integrate_cli, learning_cli, simulator
from aifence.bus.config import Settings
from aifence.bus.corpus import CorpusRecord, CorpusStrategy, read_jsonl, write_jsonl
from aifence.bus.spec_models import (
    SPEC_MODELS,
    ProtocolAck,
    ProtocolCapability,
    ProtocolConcept,
    ProtocolDelta,
    ProtocolDeltaOp,
    ProtocolError,
    ProtocolPacket,
    ProtocolPattern,
    ProtocolRef,
    ProtocolState,
)
from aifence.bus.telemetry import Telemetry


def test_protocol_models_cover_every_exported_contract() -> None:
    packet = ProtocolPacket(cb="global", atoms=[{"literal": "ready", "has_literal": True}])
    assert packet.v == "sage/0.2"
    assert ProtocolRef(ref="R1", byte_size=5, digest="abc").tier == "warm"
    assert ProtocolState(state="S1", revision=1, value_digest="digest").revision == 1
    delta = ProtocolDelta(
        base="S1",
        target="S2",
        ops=[ProtocolDeltaOp(op="replace", path="/status", value="ready")],
    )
    assert delta.ops[0].op == "replace"
    assert ProtocolConcept(
        code="C00000001", version=1, codebook="global", canonical="status"
    ).status == "active"
    pattern = ProtocolPattern(
        pattern_id="P1",
        concept_code="C00000001",
        concept_version=1,
        version=1,
        codebook="global",
        signature="sig",
        canonical="status($1)",
        composition=[{"canonical": "status"}],
    )
    assert pattern.status == "shadow"
    assert ProtocolCapability().protocol == "sage/0.2"
    assert ProtocolAck(
        message_id="M1",
        packet_id="P1",
        receiver="worker",
        status="acked",
        observed_at="2026-01-01T00:00:00Z",
    ).status == "acked"
    assert ProtocolError(code="invalid", message="bad input").retryable is False
    assert set(SPEC_MODELS) == {
        "packet",
        "ref",
        "state",
        "delta",
        "concept",
        "pattern",
        "capability",
        "provenance",
        "ack",
        "error",
    }
    with pytest.raises(ValidationError):
        ProtocolPacket(cb="global", unsupported=True)


def test_corpus_jsonl_is_deterministic_and_reports_bad_rows(tmp_path: Path) -> None:
    strategy = CorpusStrategy(
        name="sage", representation={"status": "ready"}, wire_bytes=12, estimated_tokens=3
    )
    record = CorpusRecord.build(
        task_family="routing",
        task={"route": "review"},
        full_context={"status": "ready"},
        receiver_prior={"known": ["status"]},
        strategies=[strategy],
        expected="reviewer",
        metadata={"source": "contract"},
    )
    duplicate = CorpusRecord.build(
        task_family="routing",
        task={"route": "review"},
        full_context={"status": "ready"},
        receiver_prior={"known": ["status"]},
        strategies=[strategy],
    )
    assert record.record_id == duplicate.record_id

    path = tmp_path / "corpus.jsonl"
    write_jsonl(path, [record])
    loaded = list(read_jsonl(path))
    assert loaded == [record]

    bad = tmp_path / "bad.jsonl"
    bad.write_text("\n{not json}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 2"):
        list(read_jsonl(bad))


def test_simulator_loads_json_envelopes_lists_and_jsonl(tmp_path: Path) -> None:
    case = {"content": {"status": "ready"}}
    envelope = tmp_path / "cases.json"
    envelope.write_text(json.dumps({"cases": [case]}), encoding="utf-8")
    assert simulator.load_cases(envelope)[0].content == case["content"]

    rows = tmp_path / "cases.jsonl"
    rows.write_text(json.dumps(case) + "\n\n", encoding="utf-8")
    assert simulator.load_cases(rows)[0].content == case["content"]

    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps({"content": "not-a-list"}), encoding="utf-8")
    with pytest.raises(ValueError, match="eval input"):
        simulator.load_cases(invalid)


class _FakeSpan:
    def __init__(self) -> None:
        self.attributes: dict[str, Any] = {}

    def set_attribute(self, name: str, value: Any) -> None:
        self.attributes[name] = value


class _FakeManager(AbstractContextManager[_FakeSpan]):
    def __init__(self) -> None:
        self.span = _FakeSpan()
        self.exit_args: tuple[Any, ...] | None = None

    def __enter__(self) -> _FakeSpan:
        return self.span

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self.exit_args = (exc_type, exc, traceback)
        return False


class _FakeTrace:
    def __init__(self) -> None:
        self.manager = _FakeManager()

    def start_as_current_span(self, _name: str, *, context: Any = None) -> _FakeManager:
        return self.manager


class _FakeCounter:
    def __init__(self) -> None:
        self.calls: list[tuple[int | float, dict[str, Any]]] = []

    def add(self, value: int | float, attrs: dict[str, Any]) -> None:
        self.calls.append((value, attrs))


class _FakeMeter:
    def __init__(self) -> None:
        self.created: list[str] = []
        self.counter = _FakeCounter()

    def create_counter(self, name: str) -> _FakeCounter:
        self.created.append(name)
        return self.counter


def test_telemetry_noop_and_enabled_paths() -> None:
    disabled = Telemetry(Settings(otel_enabled=False))
    with disabled.span("encode") as span:
        assert span is None
    disabled.add("packets", 1)

    enabled = Telemetry(Settings(otel_enabled=False))
    trace = _FakeTrace()
    meter = _FakeMeter()
    enabled.enabled = True
    enabled._trace = trace
    enabled._meter = meter
    with enabled.span("encode", workspace="team", attempts=2, ignored=None) as span:
        assert span is trace.manager.span
    assert trace.manager.span.attributes == {
        "gen_ai.operation.name": "encode",
        "sage.workspace": "team",
        "sage.attempts": 2,
    }
    enabled.add("packets", 2, workspace="team", ignored=["not-scalar"])
    enabled.add("packets", 3, workspace="team")
    assert meter.created == ["sage.packets"]
    assert meter.counter.calls == [
        (2, {"sage.workspace": "team"}),
        (3, {"sage.workspace": "team"}),
    ]

    with pytest.raises(RuntimeError, match="boom"):
        with enabled.span("decode"):
            raise RuntimeError("boom")
    assert trace.manager.exit_args is not None


def test_cli_output_paths(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["sage-integrate", "--list"])
    integrate_cli.main()
    profiles = json.loads(capsys.readouterr().out)
    assert {item["id"] for item in profiles} >= {"hermes", "openclaw"}

    monkeypatch.setattr(
        sys,
        "argv",
        ["sage-integrate", "hermes", "--agent-id", "planner", "--workspace", "team"],
    )
    integrate_cli.main()
    config = json.loads(capsys.readouterr().out)
    assert config["config"]["workspace"] == "team"

    monkeypatch.setattr(sys, "argv", ["sage-learning", "--codebook", "cli.contracts"])
    learning_cli.main()
    assert json.loads(capsys.readouterr().out) == {"promoted": []}

    packet = {
        "packet_id": "P1",
        "original_bytes": 100,
        "sent_bytes": 40,
        "estimated_original_tokens": 25,
        "estimated_sent_tokens": 10,
        "semantic_loss_score": 0.0,
        "receiver_known_ratio": 0.5,
        "patterns": [],
        "refs": [],
    }
    inspect_cli._print(packet, False)
    assert "Packet P1" in capsys.readouterr().out
    inspect_cli._print(packet, True)
    assert json.loads(capsys.readouterr().out)["packet_id"] == "P1"
