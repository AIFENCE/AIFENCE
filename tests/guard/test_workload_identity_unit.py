from __future__ import annotations

from types import SimpleNamespace

import pytest
from starlette.requests import Request

from aifence.guard import workload_identity as wi
from aifence.guard.errors import AuthenticationError


def _request(headers: dict[str, str] | None = None, host: str = "127.0.0.1") -> Request:
    encoded = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    return Request({"type": "http", "method": "GET", "path": "/", "headers": encoded, "client": (host, 1234)})


def _settings(**overrides):
    values = dict(
        environment="test",
        trusted_proxy_cidrs=("127.0.0.0/8",),
        workload_identity_direct_header="X-Aifence-Workload-Identity",
        workload_identity_header="X-Forwarded-Client-Cert",
        workload_auth_enabled=True,
        workload_trust_domains=("test",),
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_parse_spiffe_id_normalizes_and_rejects_invalid() -> None:
    normalized, domain = wi.parse_spiffe_id(" spiffe://test/agents/refund%2Dworker ")
    assert normalized == "spiffe://test/agents/refund-worker"
    assert domain == "test"
    for value in ("https://test/agent", "spiffe://test", "spiffe://test/../admin", "spiffe://UPPER!/a"):
        with pytest.raises(AuthenticationError):
            wi.parse_spiffe_id(value)


def test_request_from_trusted_proxy_handles_testclient_invalid_ip_and_bad_cidr() -> None:
    assert wi.request_from_trusted_proxy(_request(host="testclient"), _settings()) is True
    assert wi.request_from_trusted_proxy(_request(host="not-an-ip"), _settings()) is False
    with pytest.raises(ValueError, match="invalid trusted proxy CIDR"):
        wi.request_from_trusted_proxy(_request(), _settings(trusted_proxy_cidrs=("bad-cidr",)))


def test_extract_workload_assertion_absent_disabled_and_untrusted() -> None:
    assert wi.extract_workload_assertion(_request(), _settings()) is None
    request = _request({"X-Aifence-Workload-Identity": "spiffe://test/agents/a"})
    with pytest.raises(AuthenticationError, match="disabled"):
        wi.extract_workload_assertion(request, _settings(workload_auth_enabled=False))
    with pytest.raises(AuthenticationError, match="untrusted proxy"):
        wi.extract_workload_assertion(request, _settings(trusted_proxy_cidrs=("10.0.0.0/8",)))


def test_extract_workload_assertion_accepts_single_xfcc_uri_and_instance() -> None:
    request = _request({
        "X-Forwarded-Client-Cert": 'Hash=abc;URI="spiffe://test/agents/a";Subject=worker',
        "X-Aifence-Instance-ID": "pod-7",
    })
    assertion = wi.extract_workload_assertion(request, _settings())
    assert assertion == wi.WorkloadAssertion("spiffe://test/agents/a", "pod-7")

    ambiguous = _request({"X-Forwarded-Client-Cert": "URI=spiffe://test/a,URI=spiffe://test/b"})
    with pytest.raises(AuthenticationError, match="ambiguous"):
        wi.extract_workload_assertion(ambiguous, _settings())


class _FakeSession:
    def __init__(self, *, binding=None, tenant=None, agent=None, dialect="sqlite") -> None:
        self.binding = binding
        self.tenant = tenant
        self.agent = agent
        self.info: dict[str, object] = {}
        self._scalar_calls = 0
        self.executed: list[tuple[object, object]] = []
        self._dialect = dialect

    def get_bind(self):
        return SimpleNamespace(dialect=SimpleNamespace(name=self._dialect))

    def execute(self, statement, params=None):
        self.executed.append((statement, params))

    def scalar(self, _statement):
        self._scalar_calls += 1
        return self.binding if self._scalar_calls == 1 else self.agent

    def get(self, _model, _id):
        return self.tenant


def _binding(**overrides):
    values = dict(
        tenant_id="tenant-1",
        id="binding-1",
        agent_id="agent-1",
        status="active",
        scopes=["tools:execute"],
        instance_pattern="pod-*",
        principal_type="service",
        principal_id="orders",
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_authenticate_workload_success_and_postgres_context(monkeypatch: pytest.MonkeyPatch) -> None:
    binding = _binding()
    tenant = SimpleNamespace(status="active")
    agent = SimpleNamespace(status="active", workload_identity="spiffe://test/agents/a")
    session = _FakeSession(binding=binding, tenant=tenant, agent=agent, dialect="postgresql")
    tenant_context: list[str] = []
    monkeypatch.setattr(wi, "set_tenant_context", lambda _session, tenant_id: tenant_context.append(tenant_id))

    auth = wi.authenticate_workload(session, wi.WorkloadAssertion("spiffe://test/agents/a", "pod-7"), _settings())
    assert auth.tenant_id == "tenant-1"
    assert auth.bound_agent_id == "agent-1"
    assert auth.bound_instance_id == "pod-7"
    assert auth.scopes == frozenset({"tools:execute"})
    assert session.info["spiffe_id"] == "spiffe://test/agents/a"
    assert tenant_context == ["tenant-1"]
    assert session.executed


@pytest.mark.parametrize(
    ("settings_overrides", "binding_overrides", "tenant", "agent", "instance", "message"),
    [
        ({"workload_trust_domains": ("other",)}, {}, SimpleNamespace(status="active"), SimpleNamespace(status="active", workload_identity="spiffe://test/agents/a"), "pod-1", "trust domain"),
        ({}, {"instance_pattern": "pod-*"}, SimpleNamespace(status="active"), SimpleNamespace(status="active", workload_identity="spiffe://test/agents/a"), None, "instance identity is required"),
        ({}, {"instance_pattern": "pod-prod-*"}, SimpleNamespace(status="active"), SimpleNamespace(status="active", workload_identity="spiffe://test/agents/a"), "pod-dev-1", "does not match"),
        ({}, {}, SimpleNamespace(status="suspended"), SimpleNamespace(status="active", workload_identity="spiffe://test/agents/a"), "pod-1", "tenant is inactive"),
        ({}, {}, SimpleNamespace(status="active"), None, "pod-1", "binding no longer matches"),
        ({}, {}, SimpleNamespace(status="active"), SimpleNamespace(status="active", workload_identity="spiffe://test/agents/other"), "pod-1", "binding no longer matches"),
    ],
)
def test_authenticate_workload_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
    settings_overrides: dict[str, object],
    binding_overrides: dict[str, object],
    tenant: object,
    agent: object,
    instance: str | None,
    message: str,
) -> None:
    session = _FakeSession(binding=_binding(**binding_overrides), tenant=tenant, agent=agent)
    monkeypatch.setattr(wi, "set_tenant_context", lambda *_args: None)
    with pytest.raises(AuthenticationError, match=message):
        wi.authenticate_workload(session, wi.WorkloadAssertion("spiffe://test/agents/a", instance), _settings(**settings_overrides))


def test_authenticate_workload_rejects_missing_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    session = _FakeSession(binding=None, tenant=SimpleNamespace(status="active"), agent=None)
    monkeypatch.setattr(wi, "set_tenant_context", lambda *_args: None)
    with pytest.raises(AuthenticationError, match="not registered"):
        wi.authenticate_workload(session, wi.WorkloadAssertion("spiffe://test/agents/a"), _settings())
