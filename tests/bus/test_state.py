from aifence.bus.state import apply_patch, diff


def test_json_patch_round_trip():
    old = {"project": "phoenix", "tests": {"failed": 3, "passed": 811}, "blocked": True}
    new = {"project": "phoenix", "tests": {"failed": 1, "passed": 813}, "blocked": True}
    patch = diff(old, new)
    assert patch == [
        {"op": "replace", "path": "/tests/failed", "value": 1},
        {"op": "replace", "path": "/tests/passed", "value": 813},
    ]
    assert apply_patch(old, patch) == new


def test_patch_distinguishes_null_from_delete():
    old = {"a": 1, "b": 2}
    new = {"a": None}
    patch = diff(old, new)
    assert {"op": "replace", "path": "/a", "value": None} in patch
    assert {"op": "remove", "path": "/b"} in patch
    assert apply_patch(old, patch) == new
