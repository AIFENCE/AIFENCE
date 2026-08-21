# Releasing AIFENCE

AIFENCE uses a tag-driven GitHub Actions release pipeline. Normal pushes are certified by `.github/workflows/ci.yml`; a version tag creates a second release build from the exact tagged commit.

## Release candidate build

Run the **Release** workflow manually from GitHub Actions. A manual run validates release metadata, runs the release consistency/security gates, rebuilds the source archive and wheel reproducibly, validates both packages, installs the wheel into a clean virtual environment, runs `aifence doctor` and `aifence demo`, generates a Python SBOM, and uploads the resulting files as a workflow artifact.

A manual run does **not** create a GitHub Release or publish a container.

## Tagged release

1. Update the platform version in `pyproject.toml` and `src/aifence/versions.py` together.
2. Ensure the normal CI workflow is green on the commit being released.
3. Create and push an exact matching tag. For platform version `0.1.0`, the tag must be `v0.1.0`.

```bash
git tag -s v0.1.0 -m "AIFENCE v0.1.0"
git push origin v0.1.0
```

The Release workflow refuses to publish when the tag and `pyproject.toml` version differ. For tagged publication it also queries the exact commit's GitHub check runs and requires the Python, Quality, SDK/TCK, and built-artifact certification jobs to have succeeded.

## What the workflow certifies

A successful tagged run:

- runs source/release/security consistency checks and dependency audit;
- builds the source ZIP and Python wheel twice and verifies reproducibility;
- validates the built source and wheel structurally;
- installs the wheel into a fresh virtual environment and runs `aifence doctor --json` plus `aifence demo`;
- generates a CycloneDX-compatible Python SBOM and SHA-256 checksums;
- creates GitHub build-provenance attestations for the release assets;
- builds the final container image;
- scans that exact image with a pinned Trivy release for HIGH/CRITICAL fixed vulnerabilities before publication;
- pushes version, minor-line, and `latest` tags to GHCR;
- records and attests the published container digest;
- creates a **draft GitHub Release** with generated notes and certified artifacts.

The GitHub Release remains a draft so a maintainer can review the notes and assets before making it visible. Pre-release version strings are marked as GitHub pre-releases.

## Release outputs

- `aifence-v<version>-source.zip`
- `aifence-<version>-py3-none-any.whl`
- `AIFENCE-v<version>-SHA256SUMS.txt`
- `aifence-python-sbom.cdx.json`
- `ghcr.io/<repository-owner>/aifence:<version>` plus minor-line and `latest` tags
- GitHub build-provenance attestations for package artifacts and the container digest

PyPI, npm, and Helm-registry publication remain disabled until their signing, credential, rollback, and ownership policies are finalized.

## Re-running a release

Do not move or overwrite an existing release tag. If a released commit is wrong, fix the issue, increment the version, and create a new tag. Manual workflow runs are the supported way to reproduce candidate artifacts without creating a release.
