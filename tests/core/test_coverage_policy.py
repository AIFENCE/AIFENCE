from __future__ import annotations

from scripts.coverage_policy import _normalize_coverage_path


def test_coverage_paths_are_normalized_across_platforms() -> None:
    assert _normalize_coverage_path(r"src\aifence\guard\crypto.py") == "src/aifence/guard/crypto.py"
    assert _normalize_coverage_path("src/aifence/guard/crypto.py") == "src/aifence/guard/crypto.py"
    assert _normalize_coverage_path("./src/aifence/flow.py") == "src/aifence/flow.py"
