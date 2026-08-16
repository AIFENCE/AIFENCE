# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from .config import Settings
from .protocol_spec import (
    SAGE_WIRE_VERSION,
    canonical_json_bytes,
    canonical_msgpack_bytes,
    validate_wire_v2,
)
from .schemas import Atom, EpistemicType, Packet, Provenance, TraceContext
from .signing import verify_wire


class WireCodec:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def compact(self, packet: Packet) -> dict[str, Any]:
        payload: dict[str, Any] = {"v": SAGE_WIRE_VERSION, "c": packet.cb, "a": packet.act}
        if packet.id:
            payload["i"] = packet.id
        if packet.sender:
            payload["s"] = packet.sender
        if packet.receiver:
            payload["r"] = packet.receiver
        if packet.atoms:
            payload["x"] = [
                {k: v for k, v in {
                    "c": atom.code, "v": atom.cv, "l": atom.literal if atom.literal is not None else None,
                    "h": 1 if atom.has_literal else None, "p": atom.path,
                    "q": atom.confidence if atom.confidence != 1.0 else None,
                    "e": atom.epistemic_type if atom.epistemic_type != "fact" else None,
                }.items() if v is not None}
                for atom in packet.atoms
            ]
        if packet.refs:
            payload["R"] = packet.refs
        if packet.base:
            payload["b"] = packet.base
        if packet.delta is not None:
            payload["d"] = packet.delta
        prov = packet.prov
        observed: int | str
        try:
            observed = int(datetime.fromisoformat(prov.observed_at).timestamp())
        except ValueError:
            observed = prov.observed_at
        payload["p"] = {k: v for k, v in {
            "s": prov.source_ids or None, "t": observed, "q": prov.confidence if prov.confidence != 1.0 else None,
            "d": prov.derivation if prov.derivation != "direct" else None, "p": prov.producer,
        }.items() if v is not None}
        meta = {k: v for k, v in packet.meta.items() if k in {"state", "revision", "budget_exceeded", "memory_tier"}}
        if meta:
            payload["m"] = meta
        if packet.signature:
            payload["g"] = packet.signature
        if packet.trace is not None:
            payload["z"] = {k: v for k, v in {"p": packet.trace.traceparent, "s": packet.trace.tracestate}.items() if v is not None}
        return payload

    def wire(self, packet: Packet) -> tuple[str, bytes]:
        compact = self.compact(packet)
        return canonical_json_bytes(compact).decode("utf-8"), canonical_msgpack_bytes(compact)

    def expand(self, payload: dict[str, Any]) -> Packet:
        validate_wire_v2(payload)
        if self.settings.require_packet_signatures and "g" not in payload:
            raise ValueError("packet signature required")
        if "g" in payload and self.settings.packet_signing_public_key is not None:
            if not verify_wire(payload, self.settings.packet_signing_public_key.get_secret_value()):
                raise ValueError("invalid packet signature")
        prov_raw = payload.get("p", {}) or {}
        observed = prov_raw.get("t")
        observed_at = datetime.fromtimestamp(observed, UTC).isoformat() if isinstance(observed, (int, float)) else str(observed) if observed else Provenance().observed_at
        prov = Provenance(
            source_ids=list(prov_raw.get("s") or []), observed_at=observed_at,
            confidence=float(prov_raw.get("q", 1.0)), derivation=str(prov_raw.get("d", "direct")), producer=prov_raw.get("p"),
        )
        atoms = [
            Atom(
                code=atom.get("c"), cv=atom.get("v"), literal=atom.get("l"),
                has_literal=bool(atom.get("h", "l" in atom)), path=atom.get("p"),
                confidence=float(atom.get("q", 1.0)),
                epistemic_type=cast(EpistemicType, str(atom.get("e", "fact"))),
            )
            for atom in payload.get("x", [])
        ]
        return Packet(
            id=payload.get("i"), cb=str(payload.get("c", self.settings.codebook)), sender=payload.get("s"), receiver=payload.get("r"),
            act=str(payload.get("a", "report")), atoms=atoms, refs=list(payload.get("R", [])), base=payload.get("b"),
            delta=payload.get("d"), prov=prov, meta=dict(payload.get("m", {})),
            signature=dict(payload.get("g", {})) if payload.get("g") else None,
            trace=TraceContext(
                traceparent=payload["z"]["p"], tracestate=payload["z"].get("s")
            )
            if payload.get("z")
            else None,
        )
