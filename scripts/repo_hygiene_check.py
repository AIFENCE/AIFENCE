from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".mutmut-cache",
    ".nox",
    ".tox",
    "node_modules",
    "dist",
    "build",
    "mutants",
}

FORBIDDEN_FILES = {
    ".coverage",
    "coverage.json",
    "coverage.xml",
}

FORBIDDEN_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def repository_paths() -> list[Path]:
    """Return files Git considers repository content.

    Includes:
    - tracked files
    - untracked files that are not ignored

    Excludes:
    - .gitignore-matched local environments
    - caches
    - generated local artifacts
    """
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )

    return [
        Path(value)
        for value in result.stdout.decode("utf-8").split("\0")
        if value
    ]


def is_forbidden(path: Path) -> bool:
    if any(part in FORBIDDEN_DIRS for part in path.parts):
        return True

    if path.name in FORBIDDEN_FILES:
        return True

    return path.suffix in FORBIDDEN_SUFFIXES


def main() -> None:
    failures = sorted(
        path.as_posix()
        for path in repository_paths()
        if is_forbidden(path)
    )

    result = {
        "check": "repository-hygiene",
        "ok": not failures,
        "forbidden": failures,
    }

    print(json.dumps(result, separators=(",", ":")))

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()