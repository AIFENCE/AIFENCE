# AIFENCE for Hermes Agent

This release is self-contained and uses only the Python standard library inside Hermes.
AIFENCE itself runs as a separate service.

## Install from the release ZIP

Linux/macOS:

```bash
unzip aifence-hermes-plugin-v0.2.6.zip
cd aifence-hermes-plugin-v0.2.6
./install.sh
```

Windows PowerShell:

```powershell
Expand-Archive .\aifence-hermes-plugin-v0.2.6.zip
cd .\aifence-hermes-plugin-v0.2.6
.\install.ps1
```

The installer copies the plugin to `$HERMES_HOME/plugins/aifence`, or to
`~/.hermes/plugins/aifence` when `HERMES_HOME` is not set. It also enables the
plugin when the `hermes` command is available.

## Configure Hermes

Set these variables in the environment used to start Hermes:

```text
AIFENCE_BUS_URL=http://127.0.0.1:8080
AIFENCE_BUS_AGENT_ID=hermes-a
AIFENCE_BUS_WORKSPACE=default
AIFENCE_BUS_API_KEY=
AIFENCE_BUS_MAX_INJECT_TOKENS=1200
```

`AIFENCE_BUS_API_KEY` is needed only when the AIFENCE service requires authentication.
Use a unique `AIFENCE_BUS_AGENT_ID` for each agent that has a separate mailbox.

Verify the installation:

```bash
hermes plugins list --plain
```

The list should show `aifence` as enabled. Start a new Hermes session after
changing plugin files or environment variables.

## Hermes in Docker

Install into the host directory mounted as Hermes data:

```bash
./install.sh "$HERMES_DATA_DIR"
```

When AIFENCE runs on the Docker host, set:

```text
AIFENCE_BUS_URL=http://host.docker.internal:8080
```

Linux Compose deployments may also need:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

Then recreate Hermes and verify the plugin inside the container:

```bash
docker exec "$HERMES_CONTAINER" hermes plugins enable aifence
docker exec "$HERMES_CONTAINER" hermes plugins list --plain
```

## Verify AIFENCE itself

From a machine with the Python AIFENCE package installed:

```bash
aifence-doctor --url http://127.0.0.1:8080 --agent-id hermes-a
```

For Docker networking, run the same command using the URL that Hermes uses.

The adapter passes raw structured application data to AIFENCE, injects decoded
peer context before a model turn, and acknowledges the claimed batch after the
turn lifecycle completes. Semantic encoding remains owned by AIFENCE.
