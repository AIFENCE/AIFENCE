# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import base64
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .protocol_spec import canonical_msgpack_bytes


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64u(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def signing_payload(wire: dict[str, Any]) -> bytes:
    unsigned = dict(wire)
    unsigned.pop("g", None)
    return canonical_msgpack_bytes(unsigned)


def sign_wire(wire: dict[str, Any], private_key_b64: str, *, key_id: str = "default") -> dict[str, str]:
    key = Ed25519PrivateKey.from_private_bytes(_unb64u(private_key_b64))
    signature = key.sign(signing_payload(wire))
    return {"alg": "Ed25519", "kid": key_id, "sig": _b64u(signature)}


def verify_wire(wire: dict[str, Any], public_key_b64: str) -> bool:
    sig = wire.get("g")
    if not isinstance(sig, dict) or sig.get("alg") != "Ed25519" or not isinstance(sig.get("sig"), str):
        return False
    try:
        key = Ed25519PublicKey.from_public_bytes(_unb64u(public_key_b64))
        key.verify(_unb64u(sig["sig"]), signing_payload(wire))
        return True
    except Exception:
        return False


def derive_public_key(private_key_b64: str) -> str:
    from cryptography.hazmat.primitives import serialization

    key = Ed25519PrivateKey.from_private_bytes(_unb64u(private_key_b64))
    raw = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return _b64u(raw)
