# Five-Minute AIFENCE Quick Start

## 1. Install

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
```

## 2. Prove the complete fence locally

```bash
aifence demo
```

The demo uses an isolated temporary database, creates a real tenant/API key, submits a real artifact to the composed application, runs **Quality -> Guard -> Bus**, claims the durable handoff as the receiver, and exits non-zero if the lifecycle does not complete.

## 3. Diagnose your configured runtime

```bash
aifence doctor
```

This validates resolved configuration, application/database construction, the packaged Quality registry and Bus protocol resources.

## 4. Run a persistent development server

```bash
aifence serve
```

In another terminal, bootstrap the first administrative identity:

```bash
aifence bootstrap --tenant-name acme
```

Store the returned API key immediately. It is intentionally shown only in the bootstrap output.

Then use it for governed endpoints, for example:

```bash
export AIFENCE_API_KEY='replace-with-bootstrap-token'
curl -sS -X POST http://127.0.0.1:8080/v1/fence/submit \
  -H "Authorization: Bearer $AIFENCE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "artifact":"# Deployment note\\n\\nThe candidate passed the required validation and rollback ownership is documented.",
    "content_type":"text/markdown",
    "receiver":"release-agent",
    "action":{"operation":"read"},
    "risk_score":10
  }'
```

A successful receipt identifies the Quality mode/profile, Guard matched rule/reason codes, tenant-scoped Bus workspace/message and signed audit event.

## Production note

Development defaults intentionally optimize local startup. Production configuration validation rejects SQLite, schema auto-create, interactive docs, wildcard hosts/CORS, unsafe in-memory transport, non-HTTPS public origins and weak private-metrics configuration. Run `aifence doctor` using the intended production environment before deployment.
