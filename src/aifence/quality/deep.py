# SPDX-License-Identifier: AGPL-3.0-or-later
"""Bridge to the repository's full AIFENCE Quality 2.0 runtime.

The deep runtime is evidence-oriented: it routes an intent to family-native
contracts, controls, validators, and evidence requirements.  It is deliberately
separate from the bounded synchronous admission scorer in :mod:`aifence.quality.gate`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _repo_root() -> Path | None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "quality" / "source" / "control_registry.csv").is_file():
            return parent
    return None


def runtime_api_path() -> Path | None:
    root = _repo_root()
    if root is None:
        return None
    path = root / "quality" / "build" / "runtime" / "src" / "runtime-api.js"
    return path if path.is_file() else None


def deep_runtime_status() -> dict[str, object]:
    api = runtime_api_path()
    node = shutil.which("node")
    return {
        "mode": "deep",
        "profile": "quality-2.0/evidence-driven",
        "available": bool(api and node),
        "runtime_api": str(api) if api else None,
        "node": node,
        "semantics": (
            "Routes work into family-native Quality 2.0 controls and evidence requirements; "
            "it is not the synchronous admission score used by /v1/fence/submit."
        ),
    }


def plan_deep_evaluation(intent: str, hints: dict[str, Any] | None = None) -> dict[str, Any]:
    api = runtime_api_path()
    node = shutil.which("node")
    if api is None:
        raise RuntimeError("deep Quality runtime is not built; run `npm --prefix quality run build`")
    if node is None:
        raise RuntimeError("Node.js is required for the deep Quality runtime")
    # Arguments are passed as JSON through argv rather than interpolated into JS,
    # so an untrusted intent cannot become executable source.
    js = (
        "import {pathToFileURL} from 'node:url';"
        "const api=await import(pathToFileURL(process.argv[1]).href);"
        "const intent=JSON.parse(process.argv[2]);"
        "const hints=JSON.parse(process.argv[3]);"
        "console.log(JSON.stringify({status:api.status(),plan:api.plan(intent,hints)}));"
    )
    proc = subprocess.run(
        [node, "--input-type=module", "-e", js, str(api), json.dumps(intent), json.dumps(hints or {})],
        cwd=api.parents[2],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "deep Quality runtime failed").strip())
    result = json.loads(proc.stdout)
    if not isinstance(result, dict):
        raise RuntimeError("deep Quality runtime returned a non-object response")
    result["mode"] = "deep"
    result["profile"] = "quality-2.0/evidence-driven"
    return result
