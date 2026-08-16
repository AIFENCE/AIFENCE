# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from typing import Any

from .compiler import SemanticUnit, normalize


def _path_shape(path: str) -> str:
    return re.sub(r"\[\d+\]", "[]", path)


def _literal_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return type(value).__name__


def _constant_literal(value: Any, *, allow_strings: bool = False) -> bool:
    if value is None or isinstance(value, bool):
        return True
    if allow_strings and isinstance(value, str):
        text = value.strip()
        return 0 < len(text) <= 64 and len(normalize(text)) <= 64
    return False


def component_for(unit: SemanticUnit, *, allow_string_constants: bool = False) -> dict[str, Any]:
    component: dict[str, Any] = {
        "canonical": unit.canonical,
        "path": _path_shape(unit.path),
        "has_literal": unit.has_literal,
    }
    if unit.has_literal:
        if _constant_literal(unit.literal, allow_strings=allow_string_constants):
            component["literal_mode"] = "constant"
            component["literal"] = unit.literal
        else:
            component["literal_mode"] = "slot"
            component["literal_type"] = _literal_type(unit.literal)
    else:
        component["literal_mode"] = "none"
    return component


def composition_for(units: Iterable[SemanticUnit], *, allow_string_constants: bool = False) -> list[dict[str, Any]]:
    return [component_for(unit, allow_string_constants=allow_string_constants) for unit in units]


def pattern_signature(composition: list[dict[str, Any]]) -> str:
    raw = json.dumps(composition, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def canonical_label(composition: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in composition:
        canonical = str(item["canonical"])
        mode = item.get("literal_mode")
        if mode == "constant":
            parts.append(f"{canonical}={item.get('literal')!s}")
        elif mode == "slot":
            parts.append(f"{canonical}=<{item.get('literal_type', 'value')}>")
        else:
            parts.append(canonical)
    return " + ".join(parts)


def estimated_savings(composition: list[dict[str, Any]]) -> int:
    baseline = len(json.dumps(composition, separators=(",", ":"), ensure_ascii=False).encode())
    slots = sum(1 for item in composition if item.get("literal_mode") == "slot")
    estimated_pattern_wire = 18 + slots * 8
    return max(0, baseline - estimated_pattern_wire)


def slot_fingerprint(units: Iterable[SemanticUnit], composition: list[dict[str, Any]]) -> str | None:
    values = [
        unit.literal
        for unit, component in zip(units, composition, strict=True)
        if component.get("literal_mode") == "slot"
    ]
    if not values:
        return None
    raw = json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()
    return hashlib.sha256(raw).hexdigest()[:24]

