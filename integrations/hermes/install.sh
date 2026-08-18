#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET_HOME=${1:-${HERMES_HOME:-$HOME/.hermes}}
TARGET="$TARGET_HOME/plugins/sage"

mkdir -p "$TARGET"
if [ -f "$TARGET/__init__.py" ]; then
  cp "$TARGET/__init__.py" "$TARGET/__init__.py.bak"
fi
cp "$ROOT/sage/__init__.py" "$TARGET/__init__.py"
cp "$ROOT/sage/plugin.yaml" "$TARGET/plugin.yaml"

printf '%s\n' "Installed SAGE Hermes plugin to $TARGET"
if command -v hermes >/dev/null 2>&1; then
  if hermes plugins enable sage >/dev/null 2>&1; then
    printf '%s\n' "Enabled Hermes plugin: sage"
  else
    printf '%s\n' "Plugin copied. Enable it with: hermes plugins enable sage"
  fi
  hermes plugins list --plain 2>/dev/null | grep -E '(^|[[:space:]])sage($|[[:space:]])' || true
else
  printf '%s\n' "Hermes CLI was not found on this machine."
  printf '%s\n' "Enable inside Hermes with: hermes plugins enable sage"
fi
cat <<'TXT'

Configure Hermes with:
  SAGE_URL=http://127.0.0.1:8080
  SAGE_AGENT_ID=hermes-a
  SAGE_WORKSPACE=default
  SAGE_API_KEY=                 # only when SAGE authentication is enabled

For a containerized Hermes instance, use http://host.docker.internal:8080
and add host.docker.internal:host-gateway when required on Linux.
TXT
