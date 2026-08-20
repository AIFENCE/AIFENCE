from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "src" / "aifence"
BUS = PKG / "bus"
GUARD = PKG / "guard"
QUALITY = PKG / "quality"
SPEC = BUS / "spec"
MCP_ADAPTERS = {"mcp_server.py", "main.py"}


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            # Resolve enough relative imports to enforce subsystem boundaries.
            if node.level and path.is_relative_to(PKG):
                rel = path.parent.relative_to(PKG).parts
                base = ["aifence", *rel]
                keep = max(1, len(base) - node.level)
                module = ".".join([*base[:keep], node.module])
                found.add(module)
            else:
                found.add(node.module)
    return found


def crosses(module_imports: set[str], forbidden: tuple[str, ...]) -> bool:
    return any(any(name == item or name.startswith(item + ".") for item in forbidden) for name in module_imports)


def main() -> None:
    violations: list[str] = []

    # Subsystems are siblings. They may compose only through the top-level app;
    # no subsystem is allowed to reach into another subsystem's implementation.
    for root, forbidden in (
        (BUS, ("aifence.guard", "aifence.quality")),
        (GUARD, ("aifence.bus", "aifence.quality")),
        (QUALITY, ("aifence.bus", "aifence.guard")),
    ):
        for path in sorted(root.glob("*.py")):
            if crosses(imports(path), forbidden):
                violations.append(
                    f"cross-subsystem dependency: {path.relative_to(ROOT)} imports {', '.join(forbidden)}"
                )

    # MCP remains an adapter-only optional dependency inside Bus.
    for path in sorted(BUS.glob("*.py")):
        if path.name in MCP_ADAPTERS:
            continue
        roots = {name.split(".", 1)[0] for name in imports(path)}
        if "mcp" in roots:
            violations.append(f"MCP dependency leaked into bus core: {path.relative_to(ROOT)}")

    api = BUS / "api.py"
    if not api.is_file():
        violations.append("bus API aggregator missing")
    elif api.stat().st_size > 8_000:
        violations.append("bus API aggregator exceeded decomposition boundary")
    for name in ("api_transport.py", "api_memory.py", "api_learning.py", "api_semantic.py", "api_helpers.py"):
        if not (BUS / name).is_file():
            violations.append(f"missing bus API domain module: {name}")
    if not (BUS / "pattern_structure.py").is_file():
        violations.append("pattern structure module missing")

    spec_path = SPEC / "AIFENCE-0.2.md"
    if not spec_path.is_file():
        violations.append("packaged protocol specification missing")
    else:
        spec = spec_path.read_text(encoding="utf-8").lower()
        if "wire version `2`" not in spec and "wire 2" not in spec:
            violations.append("protocol specification does not state wire 2")

    if violations:
        raise SystemExit("architecture check failed:\n- " + "\n- ".join(violations))
    print(json.dumps({
        "ok": True,
        "subsystem_boundary": "sibling-only",
        "mcp_boundary": "adapter-only",
        "api": "domain-routers",
        "wire": 2,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
