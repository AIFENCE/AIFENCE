# Supply-Chain and Release Integrity

The release gate certifies built artifacts rather than treating a passing source checkout as sufficient evidence.

## Required release path

1. Lint, strict type-check and run Python tests with line/branch coverage policy enforcement.
2. Run red-team, security, architecture, invariant, API-compatibility and release consistency gates.
3. Run CodeQL for Python, JavaScript/TypeScript and Go plus repository secret-regression scanning.
4. Build and test the canonical Quality runtime from source.
5. Build/test Python, TypeScript and Go SDKs and required adapters.
6. Run the Bus protocol TCK across required implementations.
7. Build the Python wheel and source archive twice and verify reproducibility.
8. Run package integrity checks and install the built wheel into a clean environment for smoke/conformance checks.
9. Generate dependency vulnerability and SBOM artifacts.
10. Require the exact tagged commit to have successful Python, Quality, SDK/TCK, and built-artifact CI checks before publication.
11. Create build-provenance attestations for certified release assets.
12. Build and scan the exact final container image before publication.
13. Push the certified image digest to GHCR and attest that digest.
14. Create a draft GitHub Release from an exact `v<platform-version>` tag and attach the certified wheel, source ZIP, SBOM, and SHA-256 checksums.

## GitHub Actions integrity

Third-party GitHub Actions used by CI/release/security/compatibility workflows are pinned by full immutable commit SHA. Dependabot is configured to propose updates so pinning does not become permanent version drift.

## Generated Quality tree

`quality/build/` is generated output and is not source-of-truth. It is ignored by Git and excluded from source release archives. `quality/source/` plus deterministic tooling reconstruct it. The small Quality control registry snapshot shipped in the Python wheel is checked byte-for-byte against the canonical source registry by `scripts/quality_registry_check.py`.

## Dependency and secret policy

Production dependencies should remain explicitly bounded/pinned where reproducibility or signature review requires it. Python and npm production dependency audits run in CI/release paths. Repository secret scanning rejects unapproved credential/key patterns while explicit adversarial fixtures are allowlisted narrowly by path/type.

## Container integrity

Tagged releases build the final image before publishing it. The workflow scans that exact image with a pinned Trivy version for HIGH/CRITICAL vulnerabilities, then pushes it to GHCR and creates a provenance attestation bound to the registry digest.

## GitHub release automation

`.github/workflows/release.yml` is the release boundary. Manual runs create certified release-candidate artifacts only. Tag pushes such as `v0.1.0` must match `pyproject.toml`, require the tagged commit's mandatory CI checks to be green, and then create a draft GitHub Release plus the certified GHCR image. See `docs/RELEASING.md` for the operator procedure.
