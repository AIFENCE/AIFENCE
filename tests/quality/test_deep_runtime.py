from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from aifence.quality import deep


def test_runtime_api_path_missing_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(deep, "_repo_root", lambda: None)
    assert deep.runtime_api_path() is None


def test_runtime_api_path_requires_built_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(deep, "_repo_root", lambda: tmp_path)
    assert deep.runtime_api_path() is None
    api = tmp_path / "quality/build/runtime/src/runtime-api.js"
    api.parent.mkdir(parents=True)
    api.write_text("export const status=()=>({ok:true});", encoding="utf-8")
    assert deep.runtime_api_path() == api


def test_deep_runtime_status_reports_availability(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    api = tmp_path / "runtime-api.js"
    api.write_text("", encoding="utf-8")
    monkeypatch.setattr(deep, "runtime_api_path", lambda: api)
    monkeypatch.setattr(deep.shutil, "which", lambda name: "/usr/bin/node" if name == "node" else None)
    status = deep.deep_runtime_status()
    assert status["available"] is True
    assert status["mode"] == "deep"
    assert status["runtime_api"] == str(api)
    assert "synchronous admission" in str(status["semantics"])


def test_plan_deep_evaluation_requires_built_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(deep, "runtime_api_path", lambda: None)
    with pytest.raises(RuntimeError, match="not built"):
        deep.plan_deep_evaluation("evaluate this")


def test_plan_deep_evaluation_requires_node(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    api = tmp_path / "runtime-api.js"
    api.write_text("", encoding="utf-8")
    monkeypatch.setattr(deep, "runtime_api_path", lambda: api)
    monkeypatch.setattr(deep.shutil, "which", lambda _name: None)
    with pytest.raises(RuntimeError, match="Node.js"):
        deep.plan_deep_evaluation("evaluate this")


def test_plan_deep_evaluation_returns_typed_plan(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    api = tmp_path / "quality/build/runtime/src/runtime-api.js"
    api.parent.mkdir(parents=True)
    api.write_text("", encoding="utf-8")
    monkeypatch.setattr(deep, "runtime_api_path", lambda: api)
    monkeypatch.setattr(deep.shutil, "which", lambda _name: "/usr/bin/node")
    captured: dict[str, object] = {}

    def run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout=json.dumps({"status": {"ok": True}, "plan": {"family": "web"}}), stderr="")

    monkeypatch.setattr(deep.subprocess, "run", run)
    result = deep.plan_deep_evaluation("build secure docs", {"artifact": "website"})
    assert result["mode"] == "deep"
    assert result["profile"] == "quality-2.0/evidence-driven"
    assert result["plan"] == {"family": "web"}
    args = captured["args"]
    assert isinstance(args, list)
    assert json.loads(args[-2]) == "build secure docs"
    assert json.loads(args[-1]) == {"artifact": "website"}
    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["timeout"] == 30
    assert kwargs["check"] is False


def test_plan_deep_evaluation_surfaces_runtime_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    api = tmp_path / "runtime-api.js"
    api.write_text("", encoding="utf-8")
    monkeypatch.setattr(deep, "runtime_api_path", lambda: api)
    monkeypatch.setattr(deep.shutil, "which", lambda _name: "/usr/bin/node")
    monkeypatch.setattr(
        deep.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=2, stdout="", stderr="runtime exploded\n"),
    )
    with pytest.raises(RuntimeError, match="runtime exploded"):
        deep.plan_deep_evaluation("intent")


def test_plan_deep_evaluation_rejects_non_object(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    api = tmp_path / "runtime-api.js"
    api.write_text("", encoding="utf-8")
    monkeypatch.setattr(deep, "runtime_api_path", lambda: api)
    monkeypatch.setattr(deep.shutil, "which", lambda _name: "/usr/bin/node")
    monkeypatch.setattr(
        deep.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="[]", stderr=""),
    )
    with pytest.raises(RuntimeError, match="non-object"):
        deep.plan_deep_evaluation("intent")
