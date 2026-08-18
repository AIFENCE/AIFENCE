# SAGE for Hermes Agent

This release is self-contained and uses only the Python standard library inside Hermes.
SAGE itself runs as a separate service.

## Install from the release ZIP

Linux/macOS:

```bash
unzip sage-hermes-plugin-v0.2.6.zip
cd sage-hermes-plugin-v0.2.6
./install.sh
```

Windows PowerShell:

```powershell
Expand-Archive .\sage-hermes-plugin-v0.2.6.zip
cd .\sage-hermes-plugin-v0.2.6
.\install.ps1
```

The installer copies the plugin to `$HERMES_HOME/plugins/sage`, or to
`~/.hermes/plugins/sage` when `HERMES_HOME` is not set. It also enables the
plugin when the `hermes` command is available.

## Configure Hermes

Set these variables in the environment used to start Hermes:

```text
SAGE_URL=http://127.0.0.1:8080
SAGE_AGENT_ID=hermes-a
SAGE_WORKSPACE=default
SAGE_API_KEY=
SAGE_MAX_INJECT_TOKENS=1200
```

`SAGE_API_KEY` is needed only when the SAGE service requires authentication.
Use a unique `SAGE_AGENT_ID` for each agent that has a separate mailbox.

Verify the installation:

```bash
hermes plugins list --plain
```

The list should show `sage` as enabled. Start a new Hermes session after
changing plugin files or environment variables.

## Hermes in Docker

Install into the host directory mounted as Hermes data:

```bash
./install.sh "$HERMES_DATA_DIR"
```

When SAGE runs on the Docker host, set:

```text
SAGE_URL=http://host.docker.internal:8080
```

Linux Compose deployments may also need:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

Then recreate Hermes and verify the plugin inside the container:

```bash
docker exec "$HERMES_CONTAINER" hermes plugins enable sage
docker exec "$HERMES_CONTAINER" hermes plugins list --plain
```

## Verify SAGE itself

From a machine with the Python SAGE package installed:

```bash
sage-doctor --url http://127.0.0.1:8080 --agent-id hermes-a
```

For Docker networking, run the same command using the URL that Hermes uses.

The adapter passes raw structured application data to SAGE, injects decoded
peer context before a model turn, and acknowledges the claimed batch after the
turn lifecycle completes. Semantic encoding remains owned by SAGE.
