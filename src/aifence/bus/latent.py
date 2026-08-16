# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import base64
import hashlib
import struct
from collections.abc import Sequence

from .schemas import LatentPacket


def pack_latent(vector: Sequence[float], space: str) -> LatentPacket:
    """Quantize a latent vector to signed int8 with symmetric scaling."""
    if not vector:
        raise ValueError("latent vector cannot be empty")
    values = [float(v) for v in vector]
    max_abs = max(abs(v) for v in values)
    scale = max_abs / 127.0 if max_abs else 1.0
    quantized = [max(-127, min(127, round(v / scale))) for v in values]
    raw = struct.pack(f"{len(quantized)}b", *quantized)
    return LatentPacket(
        v="sage-latent/0.2",
        space=space,
        dims=len(values),
        scale=scale,
        data_b64=base64.b64encode(raw).decode("ascii"),
        checksum=hashlib.sha256(raw).hexdigest()[:24],
    )


def unpack_latent(packet: LatentPacket) -> list[float]:
    if packet.v != "sage-latent/0.2":
        raise ValueError(f"unsupported latent protocol: {packet.v}")
    raw = base64.b64decode(packet.data_b64, validate=True)
    if hashlib.sha256(raw).hexdigest()[:24] != packet.checksum:
        raise ValueError("latent checksum mismatch")
    if len(raw) != packet.dims:
        raise ValueError("latent dimension mismatch")
    quantized = struct.unpack(f"{packet.dims}b", raw)
    return [q * packet.scale for q in quantized]
