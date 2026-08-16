# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SemanticUnit:
    path: str
    canonical: str
    literal: Any = None
    has_literal: bool = False
    surface: str | None = None


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9_.:/-]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")[:512]


def compile_content(value: Any, path: str = "$", depth: int = 0) -> list[SemanticUnit]:
    if depth > 16:
        text = json.dumps(value)[:512]
        return [SemanticUnit(path=path, canonical="deep_value", literal=text, has_literal=True)]
    if isinstance(value, dict):
        out: list[SemanticUnit] = []
        for key in sorted(value, key=str):
            key_name = normalize(str(key)) or "field"
            child = value[key]
            child_path = f"{path}.{key_name}"
            if isinstance(child, (dict, list)):
                out.extend(compile_content(child, child_path, depth + 1))
            else:
                out.append(
                    SemanticUnit(
                        path=child_path,
                        canonical=key_name,
                        literal=child,
                        has_literal=True,
                    )
                )
        return out
    if isinstance(value, list):
        list_out: list[SemanticUnit] = []
        for idx, child in enumerate(value):
            list_out.extend(compile_content(child, f"{path}[{idx}]", depth + 1))
        return list_out
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        clauses = [p.strip() for p in re.split(r"[.;\n]+", stripped) if p.strip()]
        if len(clauses) == 1:
            return [SemanticUnit(path=path, canonical=normalize(stripped), surface=stripped)]
        return [
            SemanticUnit(path=f"{path}[{i}]", canonical=normalize(c), surface=c)
            for i, c in enumerate(clauses)
        ]
    return [SemanticUnit(path=path, canonical="value", literal=value, has_literal=True)]
