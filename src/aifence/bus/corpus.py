# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CorpusStrategy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    representation: Any
    wire_bytes: int | None = Field(default=None, ge=0)
    estimated_tokens: int | None = Field(default=None, ge=0)


class CorpusRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    task_family: str
    task: Any
    sender_state: Any | None = None
    receiver_prior: Any | None = None
    full_context: Any
    strategies: list[CorpusStrategy]
    expected: Any | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def build(
        cls,
        *,
        task_family: str,
        task: Any,
        full_context: Any,
        strategies: list[CorpusStrategy],
        sender_state: Any | None = None,
        receiver_prior: Any | None = None,
        expected: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CorpusRecord:
        identity = {
            "task_family": task_family,
            "task": task,
            "full_context": full_context,
            "receiver_prior": receiver_prior,
        }
        raw = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()
        return cls(
            record_id="CR" + hashlib.sha256(raw).hexdigest()[:40],
            task_family=task_family,
            task=task,
            sender_state=sender_state,
            receiver_prior=receiver_prior,
            full_context=full_context,
            strategies=strategies,
            expected=expected,
            metadata=metadata or {},
        )


def write_jsonl(path: str | Path, records: list[CorpusRecord]) -> None:
    target = Path(path)
    with target.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(record.model_dump_json(exclude_none=True) + "\n")


def read_jsonl(path: str | Path) -> Iterator[CorpusRecord]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield CorpusRecord.model_validate_json(line)
            except Exception as exc:
                raise ValueError(f"invalid corpus record at line {line_no}") from exc
