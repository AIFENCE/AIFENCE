from __future__ import annotations

import base64
from types import SimpleNamespace

import httpx
import pytest

from aifence.guard.dispatcher import DispatchResult, DispatchWorker
from aifence.guard.errors import AuthorizationError, ConflictError


def _worker() -> DispatchWorker:
    settings = SimpleNamespace(
        worker_batch_size=10,
        worker_concurrency=5,
        execution_lease_seconds=30,
        worker_retry_base_seconds=2,
        max_broker_response_bytes=8192,
    )
    service = SimpleNamespace(settings=settings)
    return DispatchWorker(session_factory=None, service=service, client=None, worker_id="test-worker")  # type: ignore[arg-type]


def test_dispatch_result_add_is_immutable_and_accumulates() -> None:
    base = DispatchResult(claimed=1)
    updated = base.add(succeeded=1, retried=2, execution_id="exec-1")
    assert base == DispatchResult(claimed=1)
    assert updated.claimed == 1
    assert updated.succeeded == 1
    assert updated.retried == 2
    assert updated.execution_ids == ("exec-1",)


def test_internal_auth_and_close() -> None:
    worker = _worker()
    auth = worker._internal_auth("tenant-x")
    assert auth.tenant_id == "tenant-x"
    assert auth.scopes == frozenset({"*"})
    import asyncio
    asyncio.run(worker.close())
    assert worker._closed is True


class _Session:
    def __init__(self, tool=None) -> None:
        self.tool = tool
    def scalar(self, _statement):
        return self.tool


@pytest.mark.parametrize("method", ["GET", "HEAD", "PUT", "DELETE"])
def test_declared_idempotent_http_methods(method: str) -> None:
    worker = _worker()
    execution = SimpleNamespace(broker_type="provider", upstream_idempotency_key=None, tenant_id="t", broker_id="b")
    assert worker._declared_idempotent(execution, method, None, _Session()) is True


def test_declared_idempotent_mcp_a2a_and_tools() -> None:
    worker = _worker()
    for broker_type in ("mcp", "a2a"):
        yes = SimpleNamespace(broker_type=broker_type, upstream_idempotency_key="stable", tenant_id="t", broker_id="b")
        no = SimpleNamespace(broker_type=broker_type, upstream_idempotency_key=None, tenant_id="t", broker_id="b")
        assert worker._declared_idempotent(yes, "POST", None, _Session()) is True
        assert worker._declared_idempotent(no, "POST", None, _Session()) is False

    tool_exec = SimpleNamespace(broker_type="tool", upstream_idempotency_key=None, tenant_id="t", broker_id="tool-1")
    assert worker._declared_idempotent(tool_exec, "POST", None, _Session()) is False
    assert worker._declared_idempotent(tool_exec, "POST", "read", _Session()) is False
    tool = SimpleNamespace(allowed_operations={"read": {"idempotent": True}, "write": {"idempotent": False}})
    assert worker._declared_idempotent(tool_exec, "POST", "read", _Session(tool)) is True
    assert worker._declared_idempotent(tool_exec, "POST", "write", _Session(tool)) is False


def test_is_retryable_never_retries_auth_or_conflict(monkeypatch: pytest.MonkeyPatch) -> None:
    worker = _worker()
    execution = SimpleNamespace()
    session = _Session()
    monkeypatch.setattr(worker, "_declared_idempotent", lambda *_args, **_kwargs: True)
    assert worker._is_retryable(execution=execution, method="POST", operation=None, exc=AuthorizationError("no"), session=session) is False
    assert worker._is_retryable(execution=execution, method="POST", operation=None, exc=ConflictError("conflict"), session=session) is False
    assert worker._is_retryable(execution=execution, method="POST", operation=None, exc=RuntimeError("network"), session=session) is True


def test_backoff_is_capped_and_jitter_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    worker = _worker()
    monkeypatch.setattr("aifence.guard.dispatcher.random.uniform", lambda _a, b: b)
    assert worker._backoff_seconds(1) == pytest.approx(2.4)
    assert worker._backoff_seconds(100) <= 128.0


def test_response_limit_uses_smallest_applied_limit() -> None:
    worker = _worker()
    controls = [
        {"type": "max_response_bytes", "status": "planned", "parameters": {"value": 1}},
        {"type": "max_response_bytes", "status": "applied", "parameters": {"value": "4096"}},
        {"type": "max_response_bytes", "status": "applied", "parameters": {"value": 2048}},
    ]
    assert worker._response_limit(controls) == 2048
    for value in (0, -1, "nope", None):
        with pytest.raises(AuthorizationError, match="invalid"):
            worker._response_limit([{"type": "max_response_bytes", "status": "applied", "parameters": {"value": value}}])


def test_tool_operation_extracts_bound_operation_or_fails_closed() -> None:
    controls = [
        {"type": "other", "evidence": {"operation": "ignored"}},
        {"type": "capability_binding", "evidence": {"operation": "refund"}},
    ]
    assert DispatchWorker._tool_operation(controls) == "refund"
    assert DispatchWorker._tool_operation([], required=False) is None
    with pytest.raises(AuthorizationError, match="bound operation"):
        DispatchWorker._tool_operation([])


def test_parse_response_json_text_binary_and_malformed_json() -> None:
    json_response = httpx.Response(200, headers={"content-type": "application/json", "x-request-id": "abc", "server": "omit"}, json={"ok": True})
    body, headers = DispatchWorker._parse_response(json_response)
    assert body == {"ok": True}
    assert headers == {"content-type": "application/json", "x-request-id": "abc"}

    text_response = httpx.Response(200, headers={"content-type": "text/plain", "request-id": "r1"}, text="hello")
    assert DispatchWorker._parse_response(text_response) == ("hello", {"content-type": "text/plain", "request-id": "r1"})

    binary = b"\x00\x01"
    binary_response = httpx.Response(200, headers={"content-type": "application/octet-stream"}, content=binary)
    body, _ = DispatchWorker._parse_response(binary_response)
    assert body == {"encoding": "base64", "data": base64.b64encode(binary).decode()}

    bad_json = httpx.Response(200, headers={"content-type": "application/json"}, content=b"not-json")
    body, _ = DispatchWorker._parse_response(bad_json)
    assert body["encoding"] == "base64"
