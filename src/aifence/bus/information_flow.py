# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db_models import InformationFlowLabel


class InformationFlowStore:
    def __init__(self, db: Session) -> None:
        self.db = db

    def labels(self, workspace: str, object_kind: str, object_id: str) -> set[str]:
        return set(
            self.db.scalars(
                select(InformationFlowLabel.label).where(
                    InformationFlowLabel.workspace == workspace,
                    InformationFlowLabel.object_kind == object_kind,
                    InformationFlowLabel.object_id == object_id,
                )
            )
        )

    def assign(
        self,
        workspace: str,
        object_kind: str,
        object_id: str,
        labels: list[str] | set[str],
        *,
        source_kind: str | None = None,
        source_id: str | None = None,
    ) -> set[str]:
        normalized = {item.strip().lower() for item in labels if item and item.strip()}
        existing = self.labels(workspace, object_kind, object_id)
        for label in sorted(normalized - existing):
            self.db.add(
                InformationFlowLabel(
                    workspace=workspace,
                    object_kind=object_kind,
                    object_id=object_id,
                    label=label,
                    source_kind=source_kind,
                    source_id=source_id,
                )
            )
        self.db.flush()
        return existing | normalized

    def propagate(
        self,
        workspace: str,
        target_kind: str,
        target_id: str,
        sources: list[tuple[str, str]],
    ) -> set[str]:
        combined: set[str] = set()
        for source_kind, source_id in sources:
            combined |= self.labels(workspace, source_kind, source_id)
        return self.assign(workspace, target_kind, target_id, combined) if combined else set()
