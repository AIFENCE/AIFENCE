from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.2.7"
LATEST_TAGGED_VERSION = "0.2.6"
EXPECTED_RELEASE = "v0.2"
EXPECTED_PROTOCOL = "aifence/0.2"
EXPECTED_WIRE = 2
EXPECTED_REPOSITORY = "https://github.com/NeuralBinary/AIFENCE"
EXPECTED_AUTHOR = "NeuralBinary"
EXPECTED_CREDITS = ["@NeuralBinary", "@ro0ti"]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"release consistency check failed: {message}")


def text_files(root: Path):
    paths = [root] if root.is_file() else root.rglob("*")
    for path in paths:
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix in {".pyc", ".tgz", ".whl", ".zip", ".db"}:
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


def main() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    require(project["version"] == EXPECTED_VERSION, "pyproject version drift")
    require(project["authors"] == [{"name": EXPECTED_AUTHOR}], "pyproject author drift")
    require([item["name"] for item in project["maintainers"]] == ["NeuralBinary", "ro0ti"], "pyproject maintainers drift")
    require(project["urls"]["Repository"] == EXPECTED_REPOSITORY, "pyproject repository drift")
    scripts = project.get("scripts", {})
    require(scripts.get("aifence-doctor") == "aifence.bus.doctor_cli:main", "aifence-doctor entry point drift")
    require(scripts.get("aifence-demo") == "aifence.bus.demo_cli:main", "aifence-demo entry point drift")
    dev_dependencies = project.get("optional-dependencies", {}).get("dev", [])
    require(any(dep.startswith("mypy") for dep in dev_dependencies), "mypy missing from dev dependencies")
    require(any(dep.startswith("pytest-cov") for dep in dev_dependencies), "pytest-cov missing from dev dependencies")
    require((ROOT / "src/aifence/bus/py.typed").is_file(), "PEP 561 py.typed marker missing")
    package_data = pyproject.get("tool", {}).get("setuptools", {}).get("package-data", {}).get("aifence.bus", [])
    require("py.typed" in package_data, "py.typed missing from wheel package data")

    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    require("mypy src/aifence.bus" in ci, "whole-package strict type-check CI gate missing")
    require("--cov=aifence.bus" in ci and "--cov-fail-under=80" in ci, "coverage CI gate missing")
    require("permissions:\n  contents: read" in ci, "least-privilege CI permissions missing")

    scale = (ROOT / ".github/workflows/scale.yml").read_text(encoding="utf-8")
    require("permissions:\n  contents: read" in scale, "least-privilege scale permissions missing")
    for community_file in ("CONTRIBUTING.md", "CONTRIBUTOR_LICENSE_AGREEMENT.md", "SECURITY.md", "SUPPORT.md", "CODE_OF_CONDUCT.md", ".github/PULL_REQUEST_TEMPLATE.md"):
        require((ROOT / community_file).is_file(), f"community policy missing: {community_file}")
    require((ROOT / ".github/dependabot.yml").is_file(), "Dependabot configuration missing")

    plugin = load_json("plugin.json")
    require(plugin["name"] == "AIFENCE", "plugin project name drift")
    require(plugin["version"] == EXPECTED_VERSION, "plugin version drift")
    require(plugin["release"] == EXPECTED_RELEASE, "plugin public release drift")
    require(plugin["protocol"] == EXPECTED_PROTOCOL, "plugin protocol drift")
    require(plugin["author"] == EXPECTED_AUTHOR, "plugin author drift")
    require(plugin["credits"] == EXPECTED_CREDITS, "plugin credits drift")
    require(plugin["repository"] == EXPECTED_REPOSITORY, "plugin repository drift")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for value in ["Project | AIFENCE", "Author | NeuralBinary", EXPECTED_REPOSITORY, "@NeuralBinary, @ro0ti", f"Version | {EXPECTED_RELEASE}"]:
        require(value in readme, f"README metadata missing: {value}")
    require(f"Source package version | {EXPECTED_VERSION}" in readme, "README source package version drift")
    require(f"Latest tagged release | v{LATEST_TAGGED_VERSION}" in readme, "README latest tagged release drift")
    require((ROOT / f"RELEASE-v{EXPECTED_VERSION}.md").is_file(), "current release notes missing")

    # Source identity and latest published release are intentionally distinct while
    # 0.2.7 is being prepared. Build/development docs follow EXPECTED_VERSION;
    # install docs keep pointing at the latest real tag until the new tag exists.
    source_docs = {
        "docs/OPERATIONS.md": [f"source version `{EXPECTED_VERSION}`"],
        "site/Development.md": [
            f"aifence-plugin-v{EXPECTED_VERSION}.zip",
            f"aifence_bus_agent_protocol-{EXPECTED_VERSION}-py3-none-any.whl",
            f"aifence-hermes-plugin-v{EXPECTED_VERSION}.zip",
            f"aifence-agent-openclaw-aifence-{EXPECTED_VERSION}.tgz",
        ],
    }
    for rel, markers in source_docs.items():
        doc = (ROOT / rel).read_text(encoding="utf-8")
        for marker in markers:
            require(marker in doc, f"source-version documentation drift in {rel}: {marker}")

    tagged_docs = ["docs/GETTING_STARTED.md", "site/CLI-Tools.md", "site/Quickstart.md"]
    for rel in tagged_docs:
        doc = (ROOT / rel).read_text(encoding="utf-8")
        require(LATEST_TAGGED_VERSION in doc, f"latest-tag documentation drift in {rel}")

    adapters_doc = (ROOT / "site/Adapters.md").read_text(encoding="utf-8")
    require(f'version: "{EXPECTED_VERSION}"' in adapters_doc, "Adapters source manifest version drift")
    require(f"v{LATEST_TAGGED_VERSION}" in adapters_doc, "Adapters latest-tag install note missing")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    require(project.get("license", {}).get("text") == "AGPL-3.0-or-later", "pyproject license metadata drift")
    require("AIFENCE Dual License" in license_text, "dual-license preamble missing")
    require("SPDX: AGPL-3.0-or-later" in license_text, "AGPL-or-later selection missing")
    require("GNU AFFERO GENERAL PUBLIC LICENSE" in license_text, "AGPL license text missing")
    require("sage@digitalacre.org" in license_text, "commercial license contact missing")
    require((ROOT / "CONTRIBUTOR_LICENSE_AGREEMENT.md").is_file(), "contributor license agreement missing")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    require("CONTRIBUTOR_LICENSE_AGREEMENT.md" in contributing, "CONTRIBUTING does not reference CLA")
    pr_template = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
    require("Contributor License Agreement" in pr_template, "pull-request CLA acknowledgement missing")

    openclaw_pkg = load_json("integrations/openclaw/package.json")
    openclaw_manifest = load_json("integrations/openclaw/openclaw.plugin.json")
    require(openclaw_pkg["version"] == EXPECTED_VERSION, "OpenClaw package version drift")
    require(openclaw_pkg["author"] == EXPECTED_AUTHOR, "OpenClaw author drift")
    require(openclaw_pkg["contributors"] == ["NeuralBinary", "ro0ti"], "OpenClaw credits drift")
    require(openclaw_pkg.get("license") == "AGPL-3.0-or-later", "OpenClaw license metadata drift")
    require(openclaw_pkg["repository"]["url"] == f"git+{EXPECTED_REPOSITORY}.git", "OpenClaw repository drift")
    require(openclaw_manifest["version"] == EXPECTED_VERSION, "OpenClaw manifest version drift")
    require((ROOT / "integrations/openclaw/LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes(), "OpenClaw license payload drift")
    require((ROOT / "integrations/hermes/LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes(), "Hermes license payload drift")

    hermes_yaml = (ROOT / "integrations/hermes/aifence/plugin.yaml").read_text(encoding="utf-8")
    require(re.search(rf'^version:\s*["\']?{re.escape(EXPECTED_VERSION)}["\']?\s*$', hermes_yaml, re.MULTILINE) is not None, "Hermes manifest version drift")
    require((ROOT / "integrations/hermes/aifence/__init__.py").read_bytes() == (ROOT / "src/aifence/bus/hermes_plugin.py").read_bytes(), "standalone Hermes adapter drift")

    init_py = (ROOT / "src/aifence/bus/__init__.py").read_text(encoding="utf-8")
    protocol_py = (ROOT / "src/aifence/bus/protocol_spec.py").read_text(encoding="utf-8")
    require(f'__version__ = "{EXPECTED_VERSION}"' in init_py, "Python package version drift")
    require(f'AIFENCE_PROTOCOL = "{EXPECTED_PROTOCOL}"' in protocol_py, "protocol constant drift")
    require(f"AIFENCE_WIRE_VERSION = {EXPECTED_WIRE}" in protocol_py, "wire constant drift")

    tck = load_json("tck/vectors/core.json")
    require(tck["protocol"] == EXPECTED_PROTOCOL, "TCK protocol drift")
    require(tck["wire_version"] == EXPECTED_WIRE, "TCK wire version drift")
    require(load_json("src/aifence/bus/tck/vectors/core.json") == tck, "packaged TCK differs from repository TCK")
    implementations = load_json("tck/implementations.json")
    require(implementations["suite"] == "aifence-tck/0.2", "TCK implementation matrix drift")
    require(load_json("src/aifence/bus/tck/implementations.json") == implementations, "packaged TCK implementation matrix drift")
    require({item["id"] for item in implementations["implementations"]} == {"python", "javascript", "go"}, "TCK implementation matrix incomplete")

    required = [
        "scripts/conformance_matrix.py",
        "scripts/differential_fuzz.py",
        "scripts/architecture_check.py",
        "scripts/cluster_chaos.py",
        "scripts/soak_cluster.py",
        "scripts/model_matrix_benchmark.py",
        "scripts/invariant_check.py",
        "scripts/generate_protocol_artifacts.py",
        "scripts/generate_specs.py",
        "scripts/package_check.py",
        "scripts/openclaw_adapter_check.mjs",
        "scripts/build_release.py",
        "integrations/go/conformance.go",
        ".env.example",
        "docker-compose.quickstart.yml",
        "quickstart.sh",
        "quickstart.ps1",
        "src/aifence/bus/doctor_cli.py",
        "src/aifence/bus/demo_cli.py",
        "integrations/hermes/README.md",
        "integrations/hermes/LICENSE",
        "integrations/hermes/install.sh",
        "integrations/hermes/install.ps1",
        "integrations/hermes/aifence/__init__.py",
        "integrations/hermes/aifence/plugin.yaml",
        "docs/GETTING_STARTED.md",
        "integrations/openclaw/src/index.ts",
        "integrations/openclaw/src/conformance.ts",
        "integrations/openclaw/tck/core.json",
        "integrations/openclaw/package.json",
        "integrations/openclaw/openclaw.plugin.json",
        "integrations/openclaw/LICENSE",
        "deploy/staging/compose.yml",
        ".github/workflows/scale.yml",
        "deploy/staging/nginx.conf",
        "src/aifence/bus/corpus.py",
        "src/aifence/bus/api_transport.py",
        "src/aifence/bus/api_memory.py",
        "src/aifence/bus/api_learning.py",
        "src/aifence/bus/api_semantic.py",
        "src/aifence/bus/api_helpers.py",
        "src/aifence/bus/pattern_structure.py",
        "src/aifence/bus/telemetry.py",
        "src/aifence/bus/information_flow.py",
        "src/aifence/bus/reachability.py",
        "src/aifence/bus/qualification.py",
        "src/aifence/bus/inspector_ui.py",
        "src/aifence/bus/pattern_policy.py",
        "src/aifence/bus/reliability.py",
        "src/aifence/bus/merkle.py",
        "src/aifence/bus/codebook_releases.py",
        "spec/invariants.json",
        "spec/generated/manifest.json",
        "docs/THREAT_MODEL.md",
        "docs/ARCHITECTURE.md",
        "docs/INVARIANTS.md",
        "spec/AIFENCE-0.2.md",
        "spec/aifence-v0.2.proto",
        "spec/schemas/wire-v2.schema.json",
        "spec/schemas/pattern-v0.2.schema.json",
        "src/aifence/bus/spec/AIFENCE-0.2.md",
        "src/aifence/bus/spec/aifence-v0.2.proto",
        "src/aifence/bus/spec/schemas/wire-v2.schema.json",
        "src/aifence/bus/spec/schemas/pattern-v0.2.schema.json",
    ]
    for rel in required:
        require((ROOT / rel).is_file(), f"missing required v0.2 artifact: {rel}")

    require((ROOT / "spec/AIFENCE-0.2.md").read_bytes() == (ROOT / "src/aifence/bus/spec/AIFENCE-0.2.md").read_bytes(), "packaged protocol specification drift")
    require((ROOT / "spec/aifence-v0.2.proto").read_bytes() == (ROOT / "src/aifence/bus/spec/aifence-v0.2.proto").read_bytes(), "packaged protobuf binding drift")

    repo_schemas = sorted((ROOT / "spec/schemas").glob("*.json"))
    require(repo_schemas, "no normative schemas found")
    for schema_path in repo_schemas:
        packaged = ROOT / "src/aifence/bus/spec/schemas" / schema_path.name
        require(packaged.is_file(), f"missing packaged schema: {schema_path.name}")
        require(schema_path.read_bytes() == packaged.read_bytes(), f"packaged schema drift: {schema_path.name}")

    wire_schema = load_json("spec/schemas/wire-v2.schema.json")
    require("g" in wire_schema.get("properties", {}), "wire signature field missing from schema")
    require("z" in wire_schema.get("properties", {}), "wire trace field missing from schema")
    require("e" in wire_schema.get("$defs", {}).get("WireAtomV2", {}).get("properties", {}), "wire epistemic field missing from schema")
    require("signature" in load_json("spec/schemas/packet-v0.2.schema.json").get("properties", {}), "readable packet signature missing from schema")


    generated = load_json("spec/generated/manifest.json")
    require(generated["protocol"] == EXPECTED_PROTOCOL, "generated protocol manifest drift")
    require(generated["wire"] == EXPECTED_WIRE, "generated wire manifest drift")
    require(set(generated.get("artifacts", {})) >= {
        "spec/generated/wire-v2.ts",
        "spec/generated/wire-v2.go",
        "spec/generated/WIRE-FIELDS.md",
        "spec/aifence-v0.2.proto",
        "src/aifence/bus/spec/aifence-v0.2.proto",
    }, "generated protocol artifact manifest incomplete")

    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    require("alembic upgrade head &&" not in dockerfile, "application container must not race schema migrations")
    root_compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    staging_compose = (ROOT / "deploy/staging/compose.yml").read_text(encoding="utf-8")
    require('command: ["alembic", "upgrade", "head"]' in root_compose, "root Compose migration service missing")
    require('command: ["alembic", "upgrade", "head"]' in staging_compose, "staging migration service missing")

    migration_files = sorted(path.name for path in (ROOT / "alembic/versions").glob("*.py") if path.name != "__init__.py")
    require(
        migration_files == ["05a2a405852d_initial_merged_schema.py"],
        f"unexpected migration history: {migration_files}",
    )

    obsolete_patterns = [
        re.compile(r"aifence/0\.(?:1|[3-9])"),
        re.compile(r"\bv0\.(?:1|[3-9])(?:\.\d+)?\b"),
        re.compile(r"\b0\.(?:1|[3-9])\.0\b"),
        re.compile(r"wire-v(?:1|[3-9])"),
        re.compile(r"AIFENCE-0\.(?:1|[3-9])"),
        re.compile(r"aifence-v0\.(?:1|[3-9])"),
    ]
    prose_forbidden = re.compile(r"\b(?:example|examples|placeholder|placeholders|mock|mocks|scaffold|scaffolding|guess|guessing)\b", re.IGNORECASE)
    obsolete: list[str] = []
    prose_violations: list[str] = []
    for scan_root in [ROOT / "src", ROOT / "spec", ROOT / "tck", ROOT / "docs", ROOT / "integrations", ROOT / "README.md", ROOT / "VERIFICATION.md", ROOT / "plugin.json", ROOT / "pyproject.toml"]:
        for path, text in text_files(scan_root):
            rel = str(path.relative_to(ROOT))
            if any(pattern.search(text) for pattern in obsolete_patterns):
                obsolete.append(rel)
            prose_text = text.replace(".env.example", "")
            if path.suffix in {".md", ".txt"} and prose_forbidden.search(prose_text):
                prose_violations.append(rel)
    require(not obsolete, f"obsolete version markers: {sorted(set(obsolete))}")
    require(not prose_violations, f"development prose found: {sorted(set(prose_violations))}")

    forbidden_artifacts: list[str] = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in {"build", "dist"}:
            forbidden_artifacts.append(str(rel))
            continue
        if any(part in {".pytest_cache", ".ruff_cache", ".mypy_cache", "__pycache__"} for part in rel.parts):
            forbidden_artifacts.append(str(rel))
            continue
        if path.is_file() and (path.name == ".coverage" or path.suffix in {".pyc", ".db", ".sqlite", ".sqlite3"} or path.name.endswith(".egg-info")):
            forbidden_artifacts.append(str(rel))
        if path.is_dir() and path.name.endswith(".egg-info"):
            forbidden_artifacts.append(str(rel))
        if path.is_file() and path.suffix == ".tgz" and "integrations/openclaw" in str(rel):
            forbidden_artifacts.append(str(rel))
    require(not forbidden_artifacts, f"generated/runtime artifacts in source tree: {sorted(set(forbidden_artifacts))[:20]}")

    print(json.dumps({
        "ok": True,
        "project": "AIFENCE",
        "author": EXPECTED_AUTHOR,
        "release": EXPECTED_RELEASE,
        "version": EXPECTED_VERSION,
        "protocol": EXPECTED_PROTOCOL,
        "wire": EXPECTED_WIRE,
        "migration": migration_files[0],
        "tck_vectors": len(tck.get("valid", [])) + len(tck.get("invalid", [])),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
