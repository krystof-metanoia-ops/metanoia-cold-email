#!/bin/bash
# Store one client's API keys in the macOS Keychain for the fundraising-engine skills.
# Usage: bash setup_keys.sh <client-slug>      e.g. bash setup_keys.sh acme
#
# Why this shape (the Metanoia consultant, 15 Oct 2026: keys in the macOS Keychain, no new subscription):
# - The operator copies each key from the tool's own dashboard and pastes it at a hidden
#   prompt (read -s): it never appears on screen, in shell history, or in a chat.
# - Items are created with an EMPTY trusted-app list (-T ""), so macOS asks her to allow
#   every read (password or Touch ID). That prompt is a second, physical approval on top of
#   the approval gate. She should click "Allow", never "Always Allow".
# - Re-running replaces a key (-U), e.g. after rotating it.
set -euo pipefail
slug="${1:?usage: setup_keys.sh <client-slug>}"
for tool in smartlead millionverifier bounceban notion; do
  read -r -s -p "Paste the ${tool} API key for '${slug}' (Enter to skip): " k; echo
  [ -z "$k" ] && { echo "  skipped ${tool}"; continue; }
  security add-generic-password -U -a "$USER" -s "fundraising-engine.${slug}.${tool}" \
    -l "Fundraising Engine – ${slug} – ${tool}" -T "" -w "$k"
  unset k
  echo "  stored ${tool}"
done
echo "Done. Keys are in your login Keychain under 'fundraising-engine.${slug}.*'."
