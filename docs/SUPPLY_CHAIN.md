# Supply-Chain and Release Integrity

The release gate certifies built artifacts rather than treating a passing source checkout as sufficient evidence.

## Required release path

1. Lint, strict type-check and run Python tests with coverage enforcement.
2. Run red-team, security, architecture, invariant and release consistency gates.
3. Build and test the canonical Quality runtime from source.
4. Build/test Python, TypeScript and Go SDKs and required adapters.
5. Run the Bus protocol TCK across required implementations.
6. Build the Python wheel and source archive.
7. Run package integrity checks and install the built wheel into a clean environment for smoke/conformance checks.
8. Generate dependency vulnerability and SBOM artifacts in CI/release workflows.
9. Publish checksums/provenance alongside release artifacts; sign artifacts/images where the target registry supports it.

## Generated Quality tree

`quality/build/` is generated output and is not source-of-truth. It is ignored by Git and excluded from source release archives. `quality/source/` plus deterministic tooling reconstruct it. The small Quality control registry snapshot shipped in the Python wheel is checked byte-for-byte against the canonical source registry by `scripts/quality_registry_check.py`.

## Dependency policy

Production dependencies should remain explicitly bounded/pinned where reproducibility or signature review requires it. Dependabot/renovation changes should pass the complete release gate rather than being merged solely because an individual package builds.
