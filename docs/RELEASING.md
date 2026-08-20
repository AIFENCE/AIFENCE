# Releasing AIFENCE

AIFENCE uses a tag-driven GitHub Actions release pipeline. Normal pushes are certified by `.github/workflows/ci.yml`; a version tag creates a second, immutable release build from the tagged commit.

## Release candidate build

Run the **Release** workflow manually from GitHub Actions. A manual run performs the release consistency/security gates, rebuilds the source archive and wheel, validates both packages, installs the wheel into a clean virtual environment, runs `aifence doctor` and `aifence demo`, generates a Python SBOM, and uploads the resulting files as a workflow artifact.

A manual run does **not** create a GitHub Release.

## Tagged release

1. Update the platform version in `pyproject.toml` and `src/aifence/versions.py` together.
2. Ensure the normal CI workflow is green on the commit being released.
3. Create and push an exact matching tag. For platform version `0.1.0`, the tag must be `v0.1.0`.

```bash
git tag -s v0.1.0 -m "AIFENCE v0.1.0"
git push origin v0.1.0
```

The Release workflow refuses to publish when the tag and `pyproject.toml` version differ.

## What the workflow publishes

A successful tagged run creates a **draft GitHub Release** containing:

- the reproducible AIFENCE source ZIP;
- the Python wheel;
- SHA-256 checksums covering the package artifacts and SBOM;
- a CycloneDX-compatible Python SBOM;
- automatically generated release notes.

The GitHub Release is intentionally left as a draft so a maintainer can review the notes and assets before making it visible. Pre-release version strings are also marked as GitHub pre-releases.

The workflow does not publish to PyPI, npm, Go module proxies, container registries, or Helm registries. Those distribution channels should be added only when their credentials, signing policy, and rollback process are finalized.

## Re-running a release

Do not move or overwrite an existing release tag. If a released commit is wrong, fix the issue, increment the version, and create a new tag. Manual workflow runs are the supported way to reproduce candidate artifacts without creating a release.
