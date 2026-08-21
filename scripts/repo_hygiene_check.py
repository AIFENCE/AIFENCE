from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DIRS = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".hypothesis",
    ".mutmut-cache", ".nox", ".tox", "node_modules", "dist", "build", "mutants",
}
FORBIDDEN_FILES = {".coverage", "coverage.json", "coverage.xml"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def main() -> None:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part == ".git" for part in relative.parts):
            continue
        if path.is_dir() and path.name in FORBIDDEN_DIRS:
            # Canonical source paths named build/dist are generated and must not be committed.
            failures.append(relative.as_posix() + "/")
            continue
        if path.is_file() and (path.name in FORBIDDEN_FILES or path.suffix in FORBIDDEN_SUFFIXES):
            failures.append(relative.as_posix())
    result = {"check": "repository-hygiene", "ok": not failures, "forbidden": sorted(failures)}
    print(json.dumps(result, separators=(",", ":")))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
