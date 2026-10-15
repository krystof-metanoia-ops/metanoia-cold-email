#!/bin/bash
# Build the download for operators without GitHub access (Krystof, 15 Oct 2026: "set this up
# so that she doesn't need to create a GitHub account").
# Output: dist/metanoia-cold-email-<version>.zip, unzipped by the operator into
# ~/metanoia-cold-email (see INSTALL.md). Refuses to package if a client name slipped in:
# the same zip goes to every client, and no client may see another's name.
set -euo pipefail
cd "$(dirname "$0")"
v=$(python3 -c "import json;print(json.load(open('plugins/fundraising-engine/plugin.json'))['version'])")
# The client names to refuse live in .denylist (one regex alternative per line), which is
# gitignored: this repo is public, so the list of who the clients are must never be committed.
if [ -s .denylist ]; then
  pat=$(grep -v '^#' .denylist | paste -sd'|' -)
  if grep -rniE "$pat" plugins README.md INSTALL.md; then
    echo "Client name found above — remove it before packaging." >&2; exit 1
  fi
else
  echo "Warning: no .denylist, so the client-name check was skipped." >&2
fi
find . -name __pycache__ -type d -prune -exec rm -rf {} +
mkdir -p dist; out="dist/metanoia-cold-email-$v.zip"; rm -f "$out"
zip -qr "$out" README.md INSTALL.md .agents plugins -x '*.DS_Store'
echo "$out ($(du -h "$out" | cut -f1))"
