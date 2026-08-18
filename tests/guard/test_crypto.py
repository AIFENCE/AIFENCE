# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from aifence.guard.crypto import EnvelopeCipher, SigningKey, canonical_json, hash_object


def test_canonical_hash_is_stable() -> None:
    assert canonical_json({"b": 2, "a": 1}) == b'{"a":1,"b":2}'
    assert hash_object({"a": 1, "b": 2}) == hash_object({"b": 2, "a": 1})


def test_envelope_cipher_authenticates_context() -> None:
    cipher = EnvelopeCipher(bytes.fromhex("11" * 32))
    encrypted = cipher.encrypt(b"secret", context=b"tenant:artifact")
    assert cipher.decrypt(encrypted, context=b"tenant:artifact") == b"secret"
    try:
        cipher.decrypt(encrypted, context=b"other")
        raise AssertionError("context mismatch should fail")
    except Exception:
        pass


def test_signing_receipt_round_trip() -> None:
    key = SigningKey.ephemeral_for_tests()
    token = key.issue_receipt({"aud": "aifence-decision", "sub": "dec_1"})
    claims = key.verify_receipt(token, audience="aifence-decision")
    assert claims["sub"] == "dec_1"


def test_envelope_cipher_supports_key_rotation_and_legacy_reads() -> None:
    old = bytes.fromhex("22" * 32)
    new = bytes.fromhex("33" * 32)
    old_cipher = EnvelopeCipher(old, active_key_id="master-v1")
    old_envelope = old_cipher.encrypt(b"old-secret", context=b"tenant:provider")
    rotated = EnvelopeCipher(active_key_id="master-v2", keyring={"master-v1": old, "master-v2": new})
    assert rotated.decrypt(old_envelope, context=b"tenant:provider") == b"old-secret"
    new_envelope = rotated.encrypt(b"new-secret", context=b"tenant:provider")
    assert b"master-v2" in new_envelope[:32]
    assert rotated.decrypt(new_envelope, context=b"tenant:provider") == b"new-secret"
