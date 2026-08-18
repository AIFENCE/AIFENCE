#!/usr/bin/env python
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Regenerate the wiki's API reference from the composed application's OpenAPI document.

The reference is derived from this code but published from the documentation
repository, so this writes into a checkout of AIFENCE.github.io. By default it
looks for one beside this repository; pass ``--out`` for anywhere else.

Run after adding or renaming endpoints so the reference cannot drift from the
code: ``python tooling/generate-api-docs.py``.
"""
from __future__ import annotations

import argparse
import collections
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# The documentation lives in its own repository. Point AIFENCE_DOCS_REPO at that
# checkout; otherwise assume it sits beside this one.
DOCS_REPO = Path(os.environ.get("AIFENCE_DOCS_REPO") or ROOT.parent / "AIFENCE.github.io")
DEFAULT_OUT = DOCS_REPO / "docs" / "api.md"

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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"where to write the reference (default: {DEFAULT_OUT})",
    )
    out = parser.parse_args().out
    if not out.parent.is_dir():
        # Better to say which checkout is missing than to create a stray file.
        parser.error(
            f"{out.parent} does not exist. Clone https://github.com/AIFENCE/AIFENCE.github.io "
            "beside this repository, or pass --out."
        )

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

    out.write_text("\n".join(lines), encoding="utf-8", newline="")
    print(f"{out}: {total} endpoints across {len(grouped)} groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
