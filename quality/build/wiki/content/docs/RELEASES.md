# Releases

Use Git tags and GitHub Releases for distributable ZIPs. Do not commit release archives.

## Local release

```bash
npm run ship
```

Output is written to `dist/` with a `release-manifest.json` containing SHA-256 hashes.

## Release contents

The release generator creates:

- BizIQ canonical source pack
- standalone Runtime with the exact canonical source vendored as `core/`
- portable BizIQ Skill
- Claude plugin
- Gemini extension
- combined platform-adapter package
- generated BizIQ wiki package

All ZIP timestamps are normalized for reproducibility.

## Versioning

The BizIQ Core revision is derived from `source/README.md`.
The Runtime version is the repository `package.json` version.
They can evolve independently while release metadata records both.

## Provenance and compatibility

Every release emits `release-manifest.json` and `release-provenance.json`. Provenance records the canonical source hash, generated build hash, deterministic archive hashes, and the exact Runtime↔Core compatibility policy. CI validates on Linux, Windows, and macOS; external GitHub Actions used by repository workflows are pinned to immutable commit SHAs with version comments.

## Performance evidence

Stable 2.0 performance evidence is documented in [`PERFORMANCE_EVIDENCE.md`](PERFORMANCE_EVIDENCE.md). The current external-value benchmark reports **96.800/100 for BizIQ 2.0**, **85.867/100 for a strong handcrafted production prompt**, and **65.200/100 for brief-only/default generation**, with BizIQ winning 30/30 paired comparisons against both baselines under the locked same-environment engineering protocol.

These are controlled engineering benchmark results, not independent third-party preference ratings. The evidence page records the scoring dimensions, acceptance results, reproducibility hashes, Stable 2.0 qualification evidence, and public reporting boundaries.
