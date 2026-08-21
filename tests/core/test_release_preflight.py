from __future__ import annotations

import pytest
from scripts.release_preflight import resolve


def test_tag_matching_version_publishes() -> None:
    assert resolve(ref_type="tag", ref_name="v0.1.0", version="0.1.0") == {
        "version": "0.1.0",
        "tag": "v0.1.0",
        "publish": True,
    }


def test_manual_or_branch_build_does_not_publish() -> None:
    assert resolve(ref_type="branch", ref_name="main", version="0.1.0")["publish"] is False
    assert resolve(ref_type="", ref_name="", version="0.1.0")["publish"] is False


def test_tag_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="does not match"):
        resolve(ref_type="tag", ref_name="v0.2.0", version="0.1.0")


def test_unknown_ref_type_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        resolve(ref_type="pull_request", ref_name="17/merge", version="0.1.0")
