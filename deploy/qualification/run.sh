#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
set -euo pipefail
cd "$(dirname "$0")/../.."
./scripts/bootstrap-local-secrets.sh ./secrets
mkdir -p qualification-evidence
docker compose -f deploy/qualification/compose.yaml up -d --build --wait --scale aifence=3 --scale worker=3 --scale lifecycle-worker=2 --scale anchor-worker=2
python -m aifence.cli evaluate \
  --corpus evals/agentic-security-v1.json \
  --output qualification-evidence/agentic-security-evaluation.json \
  --fail-under 1.0
PYTHONPATH=src python scripts/render-postgres-ddl.py > qualification-evidence/postgres-schema.sql
docker compose -f deploy/qualification/compose.yaml ps > qualification-evidence/compose-ps.txt
echo "Qualification stack is running. Evidence is under qualification-evidence/."
