# SPDX-License-Identifier: AGPL-3.0-or-later
"""The trace corpus: multi-turn agent behaviour, benign and adversarial."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

Label = Literal["benign", "attack"]


@dataclass(frozen=True)
class Turn:
    """One agent action, carrying whatever each tier needs to judge it."""

    #: What the agent produced — the quality tier's input.
    artifact: str = ""
    content_type: str = "text/plain"
    #: Source material, when the turn makes claims that should be grounded.
    sources: tuple[str, ...] = ()
    #: What the agent wants to do — the guard tier's input.
    operation: str = "read"
    tool: str | None = None
    target: str | None = None
    destructive: bool = False
    external_effect: bool = False
    #: Security context the caller declares.
    data_classes: tuple[str, ...] = ()
    content: str = ""
    network_destination: str | None = None
    environment: str = "production"
    #: Turn-level note for the report, not used in scoring.
    note: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Turn:
        return cls(
            artifact=raw.get("artifact", ""),
            content_type=raw.get("content_type", "text/plain"),
            sources=tuple(raw.get("sources", ())),
            operation=raw.get("operation", "read"),
            tool=raw.get("tool"),
            target=raw.get("target"),
            destructive=bool(raw.get("destructive", False)),
            external_effect=bool(raw.get("external_effect", False)),
            data_classes=tuple(raw.get("data_classes", ())),
            content=raw.get("content", ""),
            network_destination=raw.get("network_destination"),
            environment=raw.get("environment", "production"),
            note=raw.get("note", ""),
        )


@dataclass(frozen=True)
class Trace:
    """A sequence of turns by one agent, with a ground-truth label."""

    id: str
    family: str
    label: Label
    description: str
    turns: tuple[Turn, ...]
    #: Scope the agent was approved for; scope creep is measured against it.
    approved_scope: tuple[str, ...] = ()
    allowed_tools: tuple[str, ...] = ()
    #: For attack traces: the turn (1-indexed) by which a competent system
    #: should have reacted. Detection later than this still counts as detected
    #: but is reported as late.
    detect_by_turn: int | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_attack(self) -> bool:
        return self.label == "attack"

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Trace:
        label = raw.get("label", "attack")
        if label not in ("benign", "attack"):
            raise ValueError(f"trace {raw.get('id')!r}: label must be benign or attack")
        turns = tuple(Turn.from_dict(t) for t in raw.get("turns", ()))
        if not turns:
            raise ValueError(f"trace {raw.get('id')!r}: at least one turn is required")
        return cls(
            id=raw["id"],
            family=raw.get("family", "unspecified"),
            label=label,
            description=raw.get("description", ""),
            turns=turns,
            approved_scope=tuple(raw.get("approved_scope", ())),
            allowed_tools=tuple(raw.get("allowed_tools", ())),
            detect_by_turn=raw.get("detect_by_turn"),
            tags=tuple(raw.get("tags", ())),
        )


def default_corpus_dir() -> Path:
    """Locate ``evals/traces`` from anywhere inside the repository."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "evals" / "traces"
        if candidate.is_dir():
            return candidate
    return here.parents[3] / "evals" / "traces"


def load_corpus(directory: Path | str | None = None) -> list[Trace]:
    """Load every trace file, sorted by id for stable reporting."""
    path = Path(directory) if directory else default_corpus_dir()
    traces: list[Trace] = []
    seen: set[str] = set()
    for file in sorted(path.glob("*.json")):
        document = json.loads(file.read_text(encoding="utf-8"))
        for raw in document.get("traces", []):
            trace = Trace.from_dict(raw)
            if trace.id in seen:
                raise ValueError(f"duplicate trace id {trace.id!r} in {file.name}")
            seen.add(trace.id)
            traces.append(trace)
    return sorted(traces, key=lambda t: t.id)
