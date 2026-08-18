# SAGE for OpenClaw

The native OpenClaw plugin exposes structured SAGE handoffs, injects claimed
peer context during turn preparation, and ACKs it only after OpenClaw reports a
successful run. SAGE runs as a separate service.

## Install from the GitHub release

```bash
openclaw plugins install npm-pack:./sage-agent-openclaw-sage-0.2.6.tgz
openclaw plugins enable sage
openclaw plugins inspect sage --runtime --json
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

Use a unique `agentId` for every agent that has a separate SAGE mailbox. Set
`apiKey` only when the SAGE service requires authentication.

Verify the service independently:

```bash
sage-doctor --url http://127.0.0.1:8080 --agent-id openclaw-a
```

When OpenClaw runs in Docker and SAGE runs on the host, use
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
openclaw plugins enable sage
openclaw plugins inspect sage --runtime --json
```

`sage_handoff.content` is raw structured application data. The adapter rejects
SAGE semantic envelopes so semantic and wire encoding remain owned by SAGE.
