# SPDX-License-Identifier: AGPL-3.0-or-later
"""Loader for the canonical BizIQ control registry.

The registry (``quality/source/control_registry.csv``) is BizIQ's authoritative
catalog of production-quality controls. The gate reads it to know which
capabilities exist and at what priority, and to attribute each concrete check
back to a canonical control id.
"""
from __future__ import annotations

import csv
import functools
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QualityControl:
    id: str
    priority: str
    domain: str
    capability: str
    control: str
    target: str
    requirement: str
    capability_id: str
    control_id: str


def registry_path() -> Path:
    """Resolve the vendored BizIQ control registry.

    Honors ``AIFENCE_QUALITY_REGISTRY`` (legacy: the vendored default), then
    searches upward from this file for the ``quality/source`` pack.
    """
    override = os.getenv("AIFENCE_QUALITY_REGISTRY")
    if override:
        return Path(override)
    here = Path(__file__).resolve()
    # src/aifence/quality/controls.py -> repo root is three parents up from src.
    for parent in here.parents:
        candidate = parent / "quality" / "source" / "control_registry.csv"
        if candidate.is_file():
            return candidate
    # Fall back to the conventional location relative to the repo root.
    return here.parents[3] / "quality" / "source" / "control_registry.csv"


@functools.lru_cache(maxsize=1)
def load_controls() -> tuple[QualityControl, ...]:
    path = registry_path()
    if not path.is_file():
        return ()
    controls: list[QualityControl] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            controls.append(
                QualityControl(
                    id=row.get("id", ""),
                    priority=row.get("priority", ""),
                    domain=row.get("domain", ""),
                    capability=row.get("capability", ""),
                    control=row.get("control", ""),
                    target=row.get("target", ""),
                    requirement=row.get("requirement", ""),
                    capability_id=row.get("capability_id", ""),
                    control_id=row.get("control_id", ""),
                )
            )
    return tuple(controls)


def controls_by_capability(capability_id: str) -> tuple[QualityControl, ...]:
    return tuple(c for c in load_controls() if c.capability_id == capability_id)


def registry_summary() -> dict[str, object]:
    controls = load_controls()
    priorities: dict[str, int] = {}
    capabilities: set[str] = set()
    for control in controls:
        priorities[control.priority] = priorities.get(control.priority, 0) + 1
        capabilities.add(control.capability_id)
    return {
        "total_controls": len(controls),
        "capabilities": len(capabilities),
        "by_priority": dict(sorted(priorities.items())),
        "registry_path": str(registry_path()),
        "loaded": bool(controls),
    }
