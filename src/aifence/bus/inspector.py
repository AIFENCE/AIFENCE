# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db_models import MessageAudit, Reference


class Inspector:
    def __init__(self, db: Session) -> None:
        self.db = db

    def packet(self, packet_id: str, *, workspace: str | None = None, actor: str | None = None) -> dict[str, Any]:
        audit = self.db.scalar(select(MessageAudit).where(MessageAudit.packet_id == packet_id))
        if audit is None or (workspace is not None and audit.workspace != workspace):
            raise KeyError(packet_id)
        if actor is not None and actor not in {audit.sender, audit.receiver}:
            raise KeyError(packet_id)
        patterns = [d for d in audit.decisions if d.get("action") in {"pattern_code", "pattern_shadow_match", "pattern_promoted_to_shadow"}]
        refs: list[dict[str, Any]] = []
        for ref_id in (audit.packet or {}).get("refs", []):
            ref = self.db.get(Reference, ref_id)
            refs.append({"ref": ref_id, "byte_size": ref.byte_size if ref else None})
        omitted = sum(int(d.get("estimated_savings_bytes", 0)) for d in patterns if d.get("action") == "pattern_code")
        known_bytes = int(round(audit.input_bytes * float(audit.receiver_known_ratio or 0.0)))
        total_avoided = max(0, int(audit.input_bytes) - int(audit.output_bytes))
        waterfall = {
            "original_bytes": audit.input_bytes,
            "original_tokens_estimate": audit.original_token_estimate,
            "receiver_already_known_ratio": audit.receiver_known_ratio,
            "receiver_known_bytes_estimate": known_bytes,
            "pattern_bytes_avoided_estimate": omitted,
            "ref_bytes_avoided": audit.ref_bytes_avoided,
            "total_bytes_avoided": total_avoided,
            "sent_bytes": audit.output_bytes,
            "sent_tokens_estimate": audit.estimated_tokens,
            "byte_reduction_ratio": (total_avoided / audit.input_bytes if audit.input_bytes else 0.0),
        }
        return {
            "packet_id": audit.packet_id,
            "workspace": audit.workspace,
            "sender": audit.sender,
            "receiver": audit.receiver,
            "original_bytes": audit.input_bytes,
            "sent_bytes": audit.output_bytes,
            "estimated_original_tokens": audit.original_token_estimate,
            "estimated_sent_tokens": audit.estimated_tokens,
            "receiver_known_ratio": audit.receiver_known_ratio,
            "semantic_loss_score": audit.semantic_loss_score,
            "patterns": patterns,
            "refs": refs,
            "waterfall": waterfall,
            "decisions": audit.decisions,
        }

    def run(self, run_id: str, *, workspace: str | None = None, actor: str | None = None) -> dict[str, Any]:
        stmt = select(MessageAudit).where(MessageAudit.run_id == run_id)
        if workspace is not None:
            stmt = stmt.where(MessageAudit.workspace == workspace)
        if actor is not None:
            stmt = stmt.where((MessageAudit.sender == actor) | (MessageAudit.receiver == actor))
        rows = list(self.db.scalars(stmt.order_by(MessageAudit.created_at)))
        if not rows:
            raise KeyError(run_id)
        return {
            "run_id": run_id,
            "packets": [self.packet(row.packet_id, workspace=workspace, actor=actor) for row in rows],
            "original_bytes": sum(row.input_bytes for row in rows),
            "sent_bytes": sum(row.output_bytes for row in rows),
            "estimated_tokens": sum(row.estimated_tokens for row in rows),
            "semantic_loss_max": max((row.semantic_loss_score for row in rows), default=0.0),
        }
