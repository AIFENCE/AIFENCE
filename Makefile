# AIFENCE unified developer workflow.
# One toolchain drives all subsystems (bus + guard + quality).
.DEFAULT_GOAL := help
PY ?= python

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Create the local virtual environment
	$(PY) -m venv .venv

.PHONY: install
install: ## Install the package (editable) with dev + optional extras
	$(PY) -m pip install -e ".[dev,postgres,mcp,otel,s3,bench]"

.PHONY: lint
lint: ## Ruff lint
	ruff check src tests scripts

.PHONY: typecheck
typecheck: ## Strict mypy over the package
	mypy src

.PHONY: test
test: ## Run the full Python test suite
	pytest

.PHONY: quality-build
quality-build: ## Build the AIFENCE quality subsystem (Node)
	cd quality && npm ci && npm run build

.PHONY: quality-test
quality-test: ## Validate the AIFENCE quality subsystem
	cd quality && npm test

.PHONY: migrate
migrate: ## Apply database migrations to head
	alembic upgrade head

.PHONY: run
run: ## Run the composed API locally (aifence-api)
	aifence-api

.PHONY: repo-checks
repo-checks: ## Security, architecture, invariant, registry and release consistency gates
	$(PY) scripts/security_check.py
	$(PY) scripts/architecture_check.py
	$(PY) scripts/invariant_check.py
	$(PY) scripts/quality_registry_check.py
	$(PY) scripts/protocol_fixture_check.py
	$(PY) scripts/release_check.py

.PHONY: conformance
conformance: ## Run the composed fence and Bus protocol contracts
	$(PY) -m pytest tests/conformance
	$(PY) -m aifence.bus.conformance --fuzz 100

.PHONY: verify
verify: lint typecheck test repo-checks conformance ## Full local release-oriented gate

.PHONY: build
build: ## Build the Python distribution
	$(PY) -m build

.PHONY: release-build
release-build: ## Build and validate local release artifacts
	rm -rf dist
	$(PY) scripts/build_release.py --output dist
	@VERSION=$$($(PY) -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])'); \
	WHEEL=$$(find dist -maxdepth 1 -name "aifence-$$VERSION-*.whl" -print -quit); \
	$(PY) scripts/package_check.py --source "dist/aifence-v$$VERSION-source.zip" --wheel "$$WHEEL"
