# AIFENCE v7 candidate — local verification

This tree is a **candidate hardening build**, not a published release. The purpose of this guide is to reproduce the repository gates locally before you push/tag it.

## Recommended environment

Use Linux, macOS, or WSL2. GitHub Actions runs the primary gate on Ubuntu.

Required:

- Python 3.12 (3.13 is also exercised by the compatibility workflow)
- Node.js 24 + npm
- Go 1.23+ (1.23 and 1.24 are exercised in compatibility CI)
- Git

Recommended for the full compatibility/container checks:

- Docker + Docker Compose

## 1. Create an isolated Python environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev,hardening,postgres,mcp,otel,s3,bench,quality,redis,kafka,rabbitmq]"
pip install build wheel setuptools pip-audit
```

On PowerShell/Windows use:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev,hardening,postgres,mcp,otel,s3,bench,quality,redis,kafka,rabbitmq]"
pip install build wheel setuptools pip-audit
```

## 2. Fast repository gates

Run these first. They are fast and catch repository drift before the long test suite.

```bash
ruff check src tests scripts
mypy src
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

Expected result: every command exits `0`; the repository checks print PASS/`"ok": true`.

## 3. Full Python suite with independent line + branch gates

This is the main Python CI command:

```bash
pytest \
  --cov=aifence \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=json:coverage.json \
  --cov-fail-under=0

python scripts/coverage_policy.py --profile ci --coverage-json coverage.json
```

The policy in `coverage-policy.toml` currently uses measured **regression floors** rather than pretending the project has already reached its maturity target.

Current CI floors:

- line coverage: 82.0%
- branch coverage: 63.0%

The long-term target is documented in `docs/TESTING.md`: 90%+ line coverage, 80%+ branch coverage, and higher floors for critical security/protocol modules.

## 4. Warning regression check

```bash
pytest -W error \
  tests/bus/test_api.py \
  tests/core/test_cli.py \
  tests/quality/test_deep_runtime.py
```

## 5. Fence/product conformance and Bus TCK

```bash
pytest tests/conformance
python -m aifence.bus.conformance --json --fuzz 500
```

For the deeper/nightly mutation count:

```bash
python -m aifence.bus.conformance --json --fuzz 5000
```

## 6. Adversarial evaluation

```bash
aifence-redteam \
  --behavioral \
  --max-false-positive-rate 0 \
  --min-detection-rate 100
```

## 7. Python dependency audit + SBOM

```bash
pip-audit --strict
python scripts/generate_sbom.py --output dist/aifence-python-sbom.cdx.json
```

## 8. Quality 2.0 deterministic build

```bash
pip install -r quality/source/requirements.txt
cd quality
npm run clean
npm run build
npm run verify
npm test
cd ..
```

## 9. SDKs and adapters

### Python SDK

```bash
cd sdks/python
python -m pip install .
python -m compileall -q aifence_client
python -c "from aifence_client import AifenceClient, AsyncAifenceClient; assert AifenceClient and AsyncAifenceClient"
cd ../..
```

### TypeScript SDK

```bash
cd sdks/typescript
npm ci
npm test
npm audit --omit=dev --audit-level=high
cd ../..
```

### Go SDK

```bash
cd sdks/go
go test ./...
cd ../..
```

### OpenClaw adapter

```bash
cd integrations/openclaw
npm install --ignore-scripts
npm run build
npm audit --omit=dev --audit-level=high
node dist/conformance.js ../../src/aifence/bus/tck/vectors/core.json
cd ../..
```

Then run the cross-implementation matrix:

```bash
python scripts/conformance_matrix.py
```

## 10. Release-artifact certification

```bash
rm -rf dist
python scripts/reproducibility_check.py
python scripts/build_release.py --output dist

VERSION=$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')
WHEEL=$(find dist -maxdepth 1 -name "aifence-${VERSION}-*.whl" -print -quit)
python scripts/package_check.py \
  --source "dist/aifence-v${VERSION}-source.zip" \
  --wheel "$WHEEL"
```

Clean-wheel smoke test:

```bash
python -m venv /tmp/aifence-wheel-smoke
/tmp/aifence-wheel-smoke/bin/pip install "$WHEEL"
/tmp/aifence-wheel-smoke/bin/aifence doctor --json
/tmp/aifence-wheel-smoke/bin/aifence demo
```

## 11. Benchmark the composed fence

Run an initial local sample:

```bash
python scripts/benchmark_fence.py \
  --iterations 200 \
  --warmup 20 \
  --output dist/fence-benchmark.json \
  --max-p95-ms 500
```

Then run the repository performance regression checks:

```bash
python scripts/performance_check.py
```

Keep `dist/fence-benchmark.json`; it records environment metadata plus throughput, mean, p50, p95, p99 and max latency. Do not compare results from unlike hardware as though they were equivalent.

For a more stable local benchmark, run 3–5 repetitions after the machine is idle and compare medians rather than a single run.

## 12. Deep assurance / nightly-equivalent checks

Property + failure injection:

```bash
pytest \
  tests/bus/test_protocol_properties_hypothesis.py \
  tests/conformance/test_failure_injection.py
```

Cross-language differential fuzzing requires the OpenClaw adapter to have been built and Go to be installed:

```bash
python scripts/differential_fuzz.py --iterations 1000
```

Chaos suite:

```bash
python scripts/chaos_suite.py --messages 128
```

Mutation testing can be expensive:

```bash
mutmut run
```

## 13. Database migration compatibility

SQLite/current migration tests are part of the normal suite. For PostgreSQL, start a local PostgreSQL instance and set:

```bash
export AIFENCE_DATABASE_URL='postgresql+psycopg://postgres:postgres@127.0.0.1:5432/aifence'
alembic upgrade head
python -c "from sqlalchemy import create_engine,text; import os; e=create_engine(os.environ['AIFENCE_DATABASE_URL']); c=e.connect(); assert c.execute(text('select 1')).scalar_one()==1; c.close()"
```

The repository also contains a frozen v0.1.0 compatibility fixture for future N→N+1 migration regression testing.

## 14. Optional Redis/Kafka/RabbitMQ transport smoke

The easiest way is to reproduce `.github/workflows/compatibility.yml` with Docker. Once Redis, Kafka, and RabbitMQ are reachable:

```bash
python scripts/broker_smoke.py \
  --redis redis://127.0.0.1:6379/0 \
  --kafka 127.0.0.1:9092 \
  --rabbitmq amqp://guest:guest@127.0.0.1:5672/%2F

pytest tests/bus/test_transport.py -q
```

## 15. Local composed application smoke

```bash
aifence doctor --json
aifence demo
```

To run the API:

```bash
aifence-api
```

Then use the API endpoints documented under `docs/`.

## 16. What to send back if something fails

For a GitHub Actions failure, send:

1. workflow/job name,
2. failing step name,
3. the first traceback/error block,
4. the final ~50 log lines,
5. commit SHA.

For local coverage failures, also send `coverage.json`.

For benchmark review, send `dist/fence-benchmark.json`.

## Useful shortcuts

```bash
make repo-checks
make conformance
make release-build
```

`make verify` runs lint, mypy, the full Python test suite, repository checks and conformance, but the explicit commands above more closely reproduce the current GitHub workflows because they include branch coverage, warning checks, security scans and the extra ecosystem surfaces.

## Windows Command Prompt quick start

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
python --version
python -m pip install --upgrade pip
pip install -e ".[dev,hardening,postgres,mcp,otel,s3,bench,quality,redis,kafka,rabbitmq]"
pip install build wheel setuptools pip-audit
```

The supported CI interpreter is Python 3.12. Use `py -3.12` on Windows even if a newer Python is installed globally.

## Windows Command Prompt (cmd.exe)

Use Python 3.12 explicitly through the Windows launcher:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
python --version
python -m pip install --upgrade pip
pip install -e ".[dev,hardening,postgres,mcp,otel,s3,bench,quality,redis,kafka,rabbitmq]"
pip install build wheel setuptools pip-audit
```

Then run the same Python/Ruff/Mypy commands from the repository root. Replace Unix path separators only where a command contains a literal filesystem path; Python accepts the repository scripts as shown, but native Windows examples may use `scripts\name.py`.
