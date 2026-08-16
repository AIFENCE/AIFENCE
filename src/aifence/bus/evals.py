# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import gzip
import json
from typing import Any

import msgpack  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from .codec import SageCodec
from .compiler import compile_content, normalize
from .config import Settings
from .schemas import Budget, EncodeRequest, EvalRequest


def _fact_set(value: Any) -> set[str]:
    facts: set[str] = set()
    for unit in compile_content(value):
        facts.add(unit.canonical)
        if unit.literal is not None:
            facts.add(normalize(str(unit.literal)))
    return {f for f in facts if f}


def run_eval(db: Session, settings: Settings, request: EvalRequest) -> dict[str, Any]:
    codec = SageCodec(db, settings)
    rows: list[dict[str, Any]] = []
    total_raw = 0
    total_raw_msgpack = 0
    total_raw_gzip = 0
    total_wire = 0
    fidelity_sum = 0.0
    for index, case in enumerate(request.cases):
        raw = json.dumps(case.content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        result = codec.encode(
            EncodeRequest(
                content=case.content,
                sender="eval-sender",
                receiver=case.receiver,
                workspace=request.workspace,
                run_id=f"eval-{index}",
                budget=Budget(max_tokens=request.budget_tokens),
                use_cache=False,
                auto_learn=False,
            )
        )
        decoded = codec.decode(
            result.packet,
            resolve_refs=True,
            receiver=case.receiver,
            workspace=request.workspace,
        )
        expected = {normalize(x) for x in case.expected_facts if normalize(x)} or _fact_set(case.content)
        observed: set[str] = set()
        if decoded.resolved_state is not None:
            observed |= _fact_set(decoded.resolved_state)
        for ref in decoded.references:
            if ref.get("value") is not None:
                observed |= _fact_set(ref["value"])
        for concept in decoded.concepts:
            if concept.get("canonical"):
                observed.add(normalize(str(concept["canonical"])))
            if concept.get("literal") is not None:
                observed.add(normalize(str(concept["literal"])))
        for literal in decoded.literals:
            if literal.get("literal") is not None:
                observed.add(normalize(str(literal["literal"])))
        fidelity = 1.0 if not expected else len(expected & observed) / len(expected)
        total_raw += len(raw)
        total_raw_msgpack += len(msgpack.packb(case.content, use_bin_type=True))
        total_raw_gzip += len(gzip.compress(raw, compresslevel=6, mtime=0))
        total_wire += result.output_bytes_msgpack
        fidelity_sum += fidelity
        rows.append({
            "case": index,
            "strategy": result.strategy,
            "raw_bytes": len(raw),
            "sage_bytes": result.output_bytes_msgpack,
            "estimated_tokens": result.estimated_tokens,
            "semantic_fidelity": round(fidelity, 6),
            "budget_exceeded": bool(result.packet.meta.get("budget_exceeded")),
        })
    count = len(rows)
    return {
        "cases": rows,
        "summary": {
            "case_count": count,
            "raw_bytes": total_raw,
            "sage_bytes": total_wire,
            "wire_reduction": (total_raw / total_wire) if total_wire else 0.0,
            "semantic_fidelity": fidelity_sum / count if count else 0.0,
            "task_success_per_kilobyte": (fidelity_sum / (total_wire / 1024)) if total_wire else 0.0,
        },
        "baselines": {
            "raw_json_bytes": total_raw,
            "raw_msgpack_bytes": total_raw_msgpack,
            "raw_gzip_json_bytes": total_raw_gzip,
            "sage_msgpack_bytes": total_wire,
            "note": (
                "Built-in transport baselines are lossless raw JSON, raw MessagePack, and gzip JSON. "
                "RAG/summarizer baselines require application-specific retriever/model adapters; "
                "SAGE does not fabricate model-dependent results."
            ),
        },
    }
