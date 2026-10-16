#!/bin/bash
# Keep the fundraising-engine skills up to date automatically on this Mac.
# Usage: bash install_autoupdate.sh            # install (daily at 07:00 and at login)
#        bash install_autoupdate.sh --remove   # uninstall
#
# Why (the Metanoia consultant, 16 Oct 2026: automatic updates are "vastly preferable to having
# to ask for updates manually"): a macOS LaunchAgent runs `codex plugin marketplace upgrade`,
# which per OpenAI's plugin docs also refreshes the installed plugin's files. It keeps the local
# install (scripts on this Mac), unlike a workspace/web import, which doesn't deploy scripts.
# Runs only while the Mac is on; a missed run happens at the next login.
set -euo pipefail
label="com.metanoia-ops.fundraising-engine.update"
plist="$HOME/Library/LaunchAgents/$label.plist"
log="$HOME/.fundraising-engine/update.log"

if [ "${1:-}" = "--remove" ]; then
  launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
  rm -f "$plist"; echo "Automatic updates removed."; exit 0
fi

codex_bin="$(command -v codex || true)"
[ -z "$codex_bin" ] && { echo "The codex command isn't installed; install it first (INSTALL.md step 1)." >&2; exit 1; }
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/.fundraising-engine"

# launchd starts jobs with a minimal PATH, so the codex path is written in full, and the PATH
# includes its folder (codex may itself call node).
cat > "$plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key>
  <array><string>$codex_bin</string><string>plugin</string><string>marketplace</string><string>upgrade</string></array>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>$(dirname "$codex_bin"):/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string></dict>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>0</integer></dict>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$log</string>
  <key>StandardErrorPath</key><string>$log</string>
</dict>
</plist>
PLIST
plutil -lint "$plist" >/dev/null
launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$plist"
echo "Automatic updates on: daily at 07:00 and at login. Log: $log"
