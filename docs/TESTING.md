# Testing and assurance strategy

AIFENCE uses layered assurance rather than relying on a single coverage percentage.

- **Pull requests / pushes:** line + branch coverage, module-specific security floors, conformance, adversarial regressions, static analysis, dependency/secret checks and package certification.
- **Release:** a stricter release coverage profile, reproducibility verification, clean-wheel smoke testing, API compatibility, container scanning and provenance attestation.
- **Nightly:** a ratcheted coverage profile plus deeper fuzzing, property tests, targeted mutation testing, chaos/failure injection, compatibility services and benchmark regression checks.

## Coverage policy

Coverage policy is declared in `coverage-policy.toml`. `coverage.py`'s single combined percentage is intentionally **not** used as the gate once branch coverage is enabled: that number mixes statement and branch opportunities and can hide which dimension changed. `scripts/coverage_policy.py` instead evaluates line coverage and branch coverage independently and applies per-module floors to critical decision code.

The current floors are regression floors derived from measured coverage. They are not the maturity target. AIFENCE's target remains **90%+ repository line coverage, 80%+ branch coverage, and 95-100% where practical on critical security/protocol paths**. Floors should ratchet upward only after the suite proves them; CI must never be configured to fail by construction.

Critical module floors cover the composed fence flow, Guard authentication/enforcement/crypto/policy, Bus protocol/wire codec, and Quality admission so a high repository average cannot hide weak authorization or protocol coverage.

## Beyond coverage

Mutation testing is intentionally scoped to decision boundaries (`flow`, Guard auth/enforcement/policy, Bus protocol/wire codec and Quality admission). Mutation score is more useful there than mutating generated/model/CLI glue.

Hypothesis/property tests exercise protocol invariants. The Bus TCK and differential fuzzing exercise malformed and cross-language wire behavior. Chaos/failure-injection tests validate documented fail-closed semantics. CodeQL and secret/dependency/container scanning provide independent static and supply-chain evidence.

See `docs/SECURITY_REGRESSIONS.md` for the permanent regression ledger and `docs/BENCHMARKS.md` for performance-regression methodology.


## Local release verification

Before a tag, run the fast repository gates before the long suite:

```bash
ruff check src tests scripts
mypy src
python scripts/repo_hygiene_check.py
python scripts/security_check.py
python scripts/secret_scan.py
python scripts/security_regression_check.py
python scripts/architecture_check.py
python scripts/invariant_check.py
python scripts/quality_registry_check.py
python scripts/protocol_fixture_check.py
python scripts/api_compat_check.py
python scripts/release_check.py
```

Then run the full Python suite and coverage policy, ecosystem/TCK checks, reproducibility check, package certification, and a clean-wheel `aifence doctor --json` / `aifence demo` smoke. See `docs/RELEASING.md` for the tag boundary.

The OpenClaw adapter is pinned in `integrations/openclaw/package.json`. A release checkout should commit its verified `package-lock.json` and use `npm ci --ignore-scripts`; do not regenerate the lock as part of a release workflow.
