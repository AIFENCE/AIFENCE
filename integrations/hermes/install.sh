#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET_HOME=${1:-${HERMES_HOME:-$HOME/.hermes}}
TARGET="$TARGET_HOME/plugins/aifence"

mkdir -p "$TARGET"
if [ -f "$TARGET/__init__.py" ]; then
  cp "$TARGET/__init__.py" "$TARGET/__init__.py.bak"
fi
cp "$ROOT/aifence/__init__.py" "$TARGET/__init__.py"
cp "$ROOT/aifence/plugin.yaml" "$TARGET/plugin.yaml"

printf '%s\n' "Installed AIFENCE Hermes plugin to $TARGET"
if command -v hermes >/dev/null 2>&1; then
  if hermes plugins enable aifence >/dev/null 2>&1; then
    printf '%s\n' "Enabled Hermes plugin: aifence"
  else
    printf '%s\n' "Plugin copied. Enable it with: hermes plugins enable aifence"
  fi
  hermes plugins list --plain 2>/dev/null | grep -E '(^|[[:space:]])aifence($|[[:space:]])' || true
else
  printf '%s\n' "Hermes CLI was not found on this machine."
  printf '%s\n' "Enable inside Hermes with: hermes plugins enable aifence"
fi
cat <<'TXT'

Configure Hermes with:
  AIFENCE_BUS_URL=http://127.0.0.1:8080
  AIFENCE_BUS_AGENT_ID=hermes-a
  AIFENCE_BUS_WORKSPACE=default
  AIFENCE_BUS_API_KEY=                 # only when AIFENCE authentication is enabled

For a containerized Hermes instance, use http://host.docker.internal:8080
and add host.docker.internal:host-gateway when required on Linux.
TXT
