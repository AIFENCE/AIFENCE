# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from .checkpoints import CheckpointStore
from .config import Settings
from .db_models import SharedState


def _hash(value: Any, workspace: str = "default") -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "S" + hashlib.sha256(workspace.encode() + b"\0" + raw).hexdigest()[:40]


def _escape(part: str) -> str:
    return part.replace("~", "~0").replace("/", "~1")


def _unescape(part: str) -> str:
    return part.replace("~1", "/").replace("~0", "~")


def diff(old: Any, new: Any, path: str = "") -> list[dict[str, Any]]:
    if old == new:
        return []
    if isinstance(old, dict) and isinstance(new, dict):
        ops: list[dict[str, Any]] = []
        for key in sorted(old.keys() - new.keys(), key=str):
            ops.append({"op": "remove", "path": f"{path}/{_escape(str(key))}"})
        for key in sorted(new.keys(), key=str):
            child = f"{path}/{_escape(str(key))}"
            if key not in old:
                ops.append({"op": "add", "path": child, "value": copy.deepcopy(new[key])})
            else:
                ops.extend(diff(old[key], new[key], child))
        return ops
    return [{"op": "replace", "path": path, "value": copy.deepcopy(new)}]


def _parts(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise ValueError(f"invalid JSON Pointer: {pointer}")
    return [_unescape(p) for p in pointer[1:].split("/")]


def apply_patch(target: Any, patch: Any) -> Any:
    if not isinstance(patch, list):
        raise ValueError("patch must be a list of JSON Patch operations")
    result = copy.deepcopy(target)
    for op in patch:
        if not isinstance(op, dict) or op.get("op") not in {"add", "remove", "replace"}:
            raise ValueError("unsupported JSON Patch operation")
        parts = _parts(str(op.get("path", "")))
        if not parts:
            result = None if op["op"] == "remove" else copy.deepcopy(op.get("value"))
            continue
        parent = result
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        leaf = parts[-1]
        if isinstance(parent, list):
            index = len(parent) if leaf == "-" else int(leaf)
            if op["op"] == "remove":
                parent.pop(index)
            elif op["op"] == "add":
                parent.insert(index, copy.deepcopy(op.get("value")))
            else:
                parent[index] = copy.deepcopy(op.get("value"))
        elif isinstance(parent, dict):
            if op["op"] == "remove":
                if leaf not in parent:
                    raise ValueError(f"remove path not found: {op['path']}")
                del parent[leaf]
            else:
                parent[leaf] = copy.deepcopy(op.get("value"))
        else:
            raise ValueError("patch parent is scalar")
    return result


class StateStore:
    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings
        self.checkpoints = CheckpointStore(db, settings) if settings is not None else None

    def create(
        self,
        value: Any,
        parent_id: str | None = None,
        *,
        workspace: str = "default",
        created_by: str | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> SharedState:
        state_id = _hash(value, workspace)
        existing = self.db.get(SharedState, state_id)
        if existing is not None:
            return existing
        revision = 1
        if parent_id:
            parent = self.get(parent_id, workspace=workspace)
            if parent is None:
                raise KeyError(parent_id)
            revision = parent.revision + 1
        state = SharedState(
            id=state_id,
            revision=revision,
            payload=value,
            parent_id=parent_id,
            workspace=workspace,
            created_by=created_by,
            provenance=provenance or {},
        )
        self.db.add(state)
        self.db.flush()
        if self.checkpoints is not None:
            self.checkpoints.maybe_create(state)
        return state

    def get(self, state_id: str, *, workspace: str | None = None) -> SharedState | None:
        state = self.db.get(SharedState, state_id)
        if state is not None and workspace is not None and state.workspace != workspace:
            return None
        return state

    def transition(
        self,
        base_id: str,
        value: Any,
        *,
        is_patch: bool = False,
        workspace: str = "default",
        created_by: str | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> tuple[SharedState, list[dict[str, Any]]]:
        base = self.get(base_id, workspace=workspace)
        if base is None:
            raise KeyError(base_id)
        target = apply_patch(base.payload, value) if is_patch else value
        patch = value if is_patch else diff(base.payload, target)
        item = self.create(
            target,
            parent_id=base.id,
            workspace=workspace,
            created_by=created_by,
            provenance=provenance,
        )
        return item, patch

    def replay_plan(self, state_id: str, *, workspace: str = "default") -> dict[str, Any]:
        target = self.get(state_id, workspace=workspace)
        if target is None:
            raise KeyError(state_id)
        checkpoint = self.checkpoints.nearest(target) if self.checkpoints is not None else None
        lineage = self.lineage(state_id, workspace=workspace)
        if checkpoint is None:
            return {"checkpoint": None, "states": [item.id for item in lineage]}
        index = next((i for i, item in enumerate(lineage) if item.id == checkpoint.state_id), 0)
        return {"checkpoint": checkpoint.id, "checkpoint_state": checkpoint.state_id, "states": [item.id for item in lineage[index + 1:]]}

    def lineage(self, state_id: str, *, workspace: str = "default") -> list[SharedState]:
        out: list[SharedState] = []
        current = self.get(state_id, workspace=workspace)
        while current is not None:
            out.append(current)
            current = self.get(current.parent_id, workspace=workspace) if current.parent_id else None
        return list(reversed(out))
