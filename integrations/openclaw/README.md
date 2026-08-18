# AIFENCE for OpenClaw

The native OpenClaw plugin exposes structured AIFENCE handoffs, injects claimed
peer context during turn preparation, and ACKs it only after OpenClaw reports a
successful run. AIFENCE runs as a separate service.

## Install from the GitHub release

```bash
openclaw plugins install npm-pack:./aifence-agent-openclaw-aifence-0.2.6.tgz
openclaw plugins enable aifence
openclaw plugins inspect aifence --runtime --json
```

For noninteractive installs, OpenClaw may require `--force` for a reviewed local
archive or npm-pack source.

Configure the plugin with:

```json
{
  "url": "http://127.0.0.1:8080",
  "agentId": "openclaw-a",
  "workspace": "default",
  "apiKey": "",
  "autoInject": true,
  "maxInjectTokens": 1200,
  "contextBudgetFraction": 0.2
}
```

Use a unique `agentId` for every agent that has a separate AIFENCE mailbox. Set
`apiKey` only when the AIFENCE service requires authentication.

Verify the service independently:

```bash
aifence-doctor --url http://127.0.0.1:8080 --agent-id openclaw-a
```

When OpenClaw runs in Docker and AIFENCE runs on the host, use
`http://host.docker.internal:8080`. Linux Compose deployments may also need:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## Install from source

```bash
cd integrations/openclaw
npm install
npm run build
cd ../..
openclaw plugins install --link ./integrations/openclaw
openclaw plugins enable aifence
openclaw plugins inspect aifence --runtime --json
```

`aifence_bus_handoff.content` is raw structured application data. The adapter rejects
AIFENCE semantic envelopes so semantic and wire encoding remain owned by AIFENCE.
