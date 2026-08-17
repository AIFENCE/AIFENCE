#!/usr/bin/env python
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Regenerate ``docs/api.md`` from the composed application's OpenAPI document.

Run after adding or renaming endpoints so the reference cannot drift from the
code: ``python tooling/generate-api-docs.py``.
"""
from __future__ import annotations

import collections
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

GROUPS = (
    ("Core", lambda p: True),  # fallback, evaluated last
    ("Fence flow", lambda p: p.startswith("/v1/fence")),
    ("Quality", lambda p: p.startswith("/v1/quality")),
    ("Console", lambda p: p.startswith("/v1/console")),
    ("Guard", lambda p: p.startswith("/guard")),
    ("Bus", lambda p: p.startswith("/bus")),
)
ORDER = ["Core", "Fence flow", "Quality", "Console", "Guard", "Bus"]


def _group_for(path: str) -> str:
    for name, matches in GROUPS[1:]:
        if matches(path):
            return name
    return "Core"


def main() -> int:
    os.environ.setdefault("AIFENCE_DATABASE_URL", f"sqlite+pysqlite:///{tempfile.mkdtemp()}/api.db")
    from aifence.app import create_app
    from aifence.core.config import CoreSettings

    app = create_app(CoreSettings(database_url=os.environ["AIFENCE_DATABASE_URL"]))
    paths = app.openapi().get("paths", {})

    grouped: dict[str, list[tuple[str, str, str]]] = collections.defaultdict(list)
    for path, item in sorted(paths.items()):
        for method, operation in item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            summary = (operation.get("summary") or operation.get("operationId") or "").strip()
            grouped[_group_for(path)].append((method.upper(), path, summary))

    total = sum(len(v) for v in grouped.values())
    lines = [
        "---",
        "title: API reference",
        "summary: Every HTTP endpoint the composed application serves, generated from its OpenAPI document.",
        "infobox:",
        "  Source: generated from /openapi.json",
        "  Contract: OpenAPI 3.1",
        f"  Endpoints: {total}",
        "---",
        "",
        "This page is generated from the live OpenAPI document by",
        "`python tooling/generate-api-docs.py`, so it cannot drift from the code.",
        "The authoritative contract is `/openapi.json` when documentation is enabled.",
        "",
        "Authentication for each surface is described in the",
        "[security model](security.md#one-identity-model).",
        "",
    ]
    for group in ORDER:
        if group not in grouped:
            continue
        lines += [f"## {group}", "", "| Method | Path | Purpose |", "| --- | --- | --- |"]
        for method, path, summary in sorted(grouped[group], key=lambda row: (row[1], row[0])):
            lines.append(f"| `{method}` | `{path}` | {summary or '—'} |")
        lines.append("")

    (ROOT / "docs" / "api.md").write_text("\n".join(lines), encoding="utf-8", newline="")
    print(f"docs/api.md: {total} endpoints across {len(grouped)} groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
