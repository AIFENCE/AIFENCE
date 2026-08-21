from __future__ import annotations

import copy

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from aifence.bus.protocol_spec import (
    canonical_digest,
    canonical_msgpack_bytes,
    validate_wire_v2,
)

json_scalar = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-10_000, max_value=10_000),
    st.text(max_size=32),
)
json_value = st.recursive(
    json_scalar,
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(min_size=1, max_size=12), children, max_size=5),
    ),
    max_leaves=15,
)


KNOWN_WIRE_KEYS = frozenset(
    {"v", "c", "a", "i", "s", "r", "x", "R", "b", "d", "p", "m", "g", "z"}
)


def _wire(payload: object) -> dict[str, object]:
    return {
        "v": 2,
        "c": "core",
        "a": "handoff",
        "i": "HPROP0001",
        # ``d`` is the protocol's arbitrary delta/data surface. ``p`` is reserved
        # for the structured provenance model and therefore cannot hold arbitrary
        # JSON values.
        "d": payload,
    }


@given(json_value)
@settings(max_examples=150, deadline=None)
def test_canonical_wire_is_deterministic_for_arbitrary_payloads(payload: object) -> None:
    wire = _wire(payload)
    validate_wire_v2(wire)
    assert canonical_msgpack_bytes(wire) == canonical_msgpack_bytes(copy.deepcopy(wire))
    assert canonical_digest(wire) == canonical_digest(copy.deepcopy(wire))


@given(
    st.text(min_size=1, max_size=24).filter(lambda value: value not in KNOWN_WIRE_KEYS)
)
@settings(max_examples=75, deadline=None)
def test_unknown_top_level_wire_keys_are_fail_closed(key: str) -> None:
    wire = _wire({"ok": True})
    wire[key] = True
    with pytest.raises((TypeError, ValueError)):
        validate_wire_v2(wire)


@given(st.integers().filter(lambda value: value != 2))
@settings(max_examples=50, deadline=None)
def test_unsupported_wire_versions_are_rejected(version: int) -> None:
    wire = _wire({"ok": True})
    wire["v"] = version
    with pytest.raises((TypeError, ValueError)):
        validate_wire_v2(wire)
