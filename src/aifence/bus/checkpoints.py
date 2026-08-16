# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings
from .db_models import SharedState, StateCheckpoint


def _payload_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()
    return hashlib.sha256(raw).hexdigest()


class CheckpointStore:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def create(self, state: SharedState) -> StateCheckpoint:
        existing = self.db.scalar(
            select(StateCheckpoint).where(
                StateCheckpoint.workspace == state.workspace,
                StateCheckpoint.state_id == state.id,
            )
        )
        if existing is not None:
            return existing
        item = StateCheckpoint(
            id="CP" + hashlib.sha256(f"{state.workspace}\0{state.id}".encode()).hexdigest()[:40],
            workspace=state.workspace,
            state_id=state.id,
            revision=state.revision,
            payload_hash=_payload_hash(state.payload),
        )
        self.db.add(item)
        self.db.flush()
        return item

    def maybe_create(self, state: SharedState) -> StateCheckpoint | None:
        if state.revision <= 1 or state.revision % self.settings.checkpoint_interval_revisions != 0:
            return None
        return self.create(state)

    def nearest(self, state: SharedState) -> StateCheckpoint | None:
        current: SharedState | None = state
        while current is not None:
            checkpoint = self.db.scalar(
                select(StateCheckpoint).where(
                    StateCheckpoint.workspace == current.workspace,
                    StateCheckpoint.state_id == current.id,
                )
            )
            if checkpoint is not None:
                return checkpoint
            current = self.db.get(SharedState, current.parent_id) if current.parent_id else None
        return None
