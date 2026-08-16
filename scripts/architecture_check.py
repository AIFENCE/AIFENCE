from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "sage_plugin"
ADAPTERS = {"mcp_server.py", "main.py"}


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module.split(".", 1)[0])
    return out


def main() -> None:
    violations: list[str] = []
    for path in sorted(CORE.glob("*.py")):
        if path.name in ADAPTERS:
            continue
        if "mcp" in imported_roots(path):
            violations.append(f"MCP dependency leaked into core: {path.relative_to(ROOT)}")
    api = CORE / "api.py"
    route_modules = [CORE / name for name in ("api_transport.py", "api_memory.py", "api_learning.py", "api_semantic.py", "api_helpers.py")]
    if api.stat().st_size > 5000:
        violations.append("API aggregator exceeded decomposition boundary")
    for module in route_modules:
        if not module.is_file():
            violations.append(f"missing API domain module: {module.name}")
    if not (CORE / "pattern_structure.py").is_file():
        violations.append("pattern structure module missing")
    spec = (ROOT / "spec" / "SAGE-0.2.md").read_text()
    if "wire version `2`" not in spec.lower() and "wire 2" not in spec.lower():
        violations.append("protocol specification does not state wire 2")
    if violations:
        raise SystemExit("\n".join(violations))
    print(json.dumps({"ok": True, "mcp_boundary": "adapter-only", "api": "domain-routers", "wire": 2}, sort_keys=True))


if __name__ == "__main__":
    main()
