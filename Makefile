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
	ruff check src tests

.PHONY: typecheck
typecheck: ## Strict mypy over the package
	mypy src

.PHONY: test
test: ## Run the full Python test suite
	pytest

.PHONY: quality-build
quality-build: ## Build the BizIQ quality subsystem (Node)
	cd quality && npm ci && npm run build

.PHONY: quality-test
quality-test: ## Validate the BizIQ quality subsystem
	cd quality && npm test

.PHONY: migrate
migrate: ## Apply database migrations to head
	alembic upgrade head

.PHONY: run
run: ## Run the composed API locally (aifence-api)
	aifence-api

.PHONY: verify
verify: lint typecheck test ## Full local gate for the Python tiers

.PHONY: build
build: ## Build the Python distribution
	$(PY) -m build
