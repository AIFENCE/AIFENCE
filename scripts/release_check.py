from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    platform_version = str(project["version"])

    versions_text = (ROOT / "src/aifence/versions.py").read_text(encoding="utf-8")
    require(f'PLATFORM_VERSION = "{platform_version}"' in versions_text, "platform version source drift", failures)

    scripts = project.get("scripts", {})
    for entry in ("aifence", "aifence-api", "aifence-bootstrap", "aifence-doctor", "aifence-demo", "aifence-redteam"):
        require(entry in scripts, f"console entry point missing: {entry}", failures)

    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    require("permissions:\n  contents: read" in ci, "least-privilege CI permissions missing", failures)
    require("--cov=aifence" in ci and "--cov-branch" in ci and "coverage_policy.py --profile ci" in ci, "line/branch coverage policy gate missing", failures)
    for gate in ("security_check.py", "secret_scan.py", "security_regression_check.py", "architecture_check.py", "invariant_check.py", "quality_registry_check.py", "protocol_fixture_check.py", "api_compat_check.py", "release_check.py"):
        require(gate in ci, f"CI does not execute {gate}", failures)
    for ecosystem in ("sdks/python", "sdks/typescript", "sdks/go", "integrations/openclaw"):
        require(ecosystem in ci, f"CI does not cover {ecosystem}", failures)

    release_workflow_path = ROOT / ".github/workflows/release.yml"
    require(release_workflow_path.is_file(), "tag-driven release workflow missing", failures)
    if release_workflow_path.is_file():
        release_workflow = release_workflow_path.read_text(encoding="utf-8")
        for fragment in (
            'tags:',
            'release_preflight.py',
            'reproducibility_check.py',
            'python scripts/build_release.py --output dist',
            'python scripts/package_check.py',
            'aifence doctor --json',
            'aifence demo',
            'aifence-python-sbom.cdx.json',
            'attest-build-provenance@',
            'ghcr.io/',
            'trivy-action@',
            'docker push',
            'gh release create',
            '--verify-tag',
            '--draft',
        ):
            require(fragment in release_workflow, f"release workflow missing required behavior: {fragment}", failures)
        for check_name in (
            "Python release gate",
            "Quality 2.0 deterministic build",
            "SDKs, adapters and Bus TCK",
            "Built-artifact certification",
        ):
            require(check_name in release_workflow, f"release workflow does not require CI check: {check_name}", failures)

    # All third-party/GitHub actions are immutable SHA pins; comments retain human-readable versions.
    import re
    sha_pin = re.compile(r"^[ ]*- uses: [^@\s]+(?:/[^@\s]+)*@([0-9a-f]{40})(?:\s+#.*)?$", re.MULTILINE)
    uses_line = re.compile(r"^[ ]*- uses: (.+)$", re.MULTILINE)
    for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
        text = workflow.read_text(encoding="utf-8")
        for match in uses_line.finditer(text):
            line = match.group(0)
            require(sha_pin.fullmatch(line) is not None, f"workflow action is not SHA-pinned: {workflow.name}: {line.strip()}", failures)

    for workflow_name in ("security.yml", "nightly.yml", "compatibility.yml"):
        require((ROOT / ".github/workflows" / workflow_name).is_file(), f"hardening workflow missing: {workflow_name}", failures)
    require((ROOT / "coverage-policy.toml").is_file(), "coverage policy missing", failures)
    require((ROOT / "compat/openapi-platform-0.1.0.json").is_file(), "OpenAPI compatibility baseline missing", failures)
    require((ROOT / "compat/db/aifence-v0.1.0.sql").is_file(), "database compatibility fixture missing", failures)

    # Public repository identity is singular even though historical authorship is preserved.
    stale = "github.com/NeuralBinary/AIFENCE"
    for root in (ROOT / "integrations", ROOT / "sdks", ROOT / "src"):
        for path in root.rglob("*"):
            if not path.is_file() or "build" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            require(stale not in text, f"stale repository URL: {path.relative_to(ROOT)}", failures)

    # Versioned components remain independent but must be represented in the version inventory.
    require('GUARD_VERSION = "1.0.0rc5"' in versions_text, "guard version missing from inventory", failures)
    require('BUS_VERSION = "0.2.7"' in versions_text, "bus version missing from inventory", failures)
    require('QUALITY_VERSION = "2.0.0"' in versions_text, "quality version missing from inventory", failures)
    require('SDK_VERSION = "1.0.0rc5"' in versions_text, "SDK version missing from inventory", failures)
    require('BUS_PROTOCOL = "aifence/0.2"' in versions_text, "bus protocol missing from inventory", failures)

    # Component metadata must agree with the explicit inventory.
    sdk_python = tomllib.loads((ROOT / "sdks/python/pyproject.toml").read_text(encoding="utf-8"))
    sdk_ts = load_json(ROOT / "sdks/typescript/package.json")
    quality_pkg = load_json(ROOT / "quality/package.json")
    openclaw_pkg = load_json(ROOT / "integrations/openclaw/package.json")
    require(str(sdk_python["project"]["version"]) == "1.0.0rc5", "Python SDK version drift", failures)
    require(str(sdk_ts.get("version")) == "1.0.0-rc.5", "TypeScript SDK version drift", failures)
    require(str(quality_pkg.get("version")) == "2.0.0", "Quality package version drift", failures)
    require(str(openclaw_pkg.get("version")) == "0.2.7", "OpenClaw/Bus adapter version drift", failures)

    required_docs = (
        "docs/VERSIONS.md",
        "docs/FAILURE_SEMANTICS.md",
        "docs/THREAT_MODEL.md",
        "docs/OBSERVABILITY.md",
        "docs/QUALITY_MODES.md",
        "docs/QUICKSTART.md",
        "docs/SUPPLY_CHAIN.md",
        "docs/BUS_PROTOCOL.md",
        "docs/FENCE_FLOW.md",
        "docs/RELEASING.md",
        "docs/TESTING.md",
        "docs/SECURITY_REGRESSIONS.md",
        "docs/BENCHMARKS.md",
    )
    for relative in required_docs:
        require((ROOT / relative).is_file(), f"required release documentation missing: {relative}", failures)

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    require("quality/build/" in gitignore, "generated quality/build is not ignored", failures)

    openclaw = load_json(ROOT / "integrations/openclaw/package.json")
    repo = openclaw.get("repository")
    require(isinstance(repo, dict) and "github.com/AIFENCE/AIFENCE" in str(repo.get("url")), "OpenClaw repository URL drift", failures)

    if failures:
        raise SystemExit("release consistency check failed:\n- " + "\n- ".join(failures))
    print(json.dumps({"ok": True, "platform_version": platform_version, "checks": "release-consistency"}, sort_keys=True))


if __name__ == "__main__":
    main()
