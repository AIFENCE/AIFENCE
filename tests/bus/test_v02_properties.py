from __future__ import annotations

import random

from aifence.bus.protocol_spec import (
    canonical_digest,
    canonical_json_bytes,
    canonical_msgpack_bytes,
    validate_wire_v2,
)
from aifence.bus.state import apply_patch, diff


def _json_value(rng: random.Random, depth: int = 0):
    if depth >= 3:
        return rng.choice([None, True, False, rng.randint(-1000, 1000), round(rng.random() * 100, 4), f"s{rng.randint(0, 9999)}"])
    kind = rng.randrange(5)
    if kind == 0:
        return {f"k{index}": _json_value(rng, depth + 1) for index in range(rng.randrange(5))}
    if kind == 1:
        return [_json_value(rng, depth + 1) for _ in range(rng.randrange(5))]
    return _json_value(rng, 3)


def _reordered(value):
    if isinstance(value, dict):
        return {key: _reordered(value[key]) for key in reversed(list(value.keys()))}
    if isinstance(value, list):
        return [_reordered(item) for item in value]
    return value


def test_canonical_serialization_is_deterministic_for_random_nested_values():
    rng = random.Random(20260731)
    for _ in range(250):
        meta = _json_value(rng)
        if not isinstance(meta, dict):
            meta = {"value": meta}
        wire = {"v": 2, "c": "global", "a": "report", "p": {}, "m": meta}
        reordered = _reordered(wire)
        validate_wire_v2(wire)
        validate_wire_v2(reordered)
        assert canonical_json_bytes(wire) == canonical_json_bytes(reordered)
        assert canonical_msgpack_bytes(wire) == canonical_msgpack_bytes(reordered)
        assert canonical_digest(wire) == canonical_digest(reordered)


def test_state_diff_patch_round_trip_for_random_nested_objects():
    rng = random.Random(20260801)
    for _ in range(250):
        old = _json_value(rng)
        new = _json_value(rng)
        patch = diff(old, new)
        assert apply_patch(old, patch) == new
