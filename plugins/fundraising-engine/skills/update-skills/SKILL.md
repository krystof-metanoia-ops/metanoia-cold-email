---
name: update-skills
description: Update this fundraising-engine plugin to its newest version — when the operator says "update the fundraising engine skills", "update the skills", "update the plugin", "update yourself", "get the latest version", or a reminder asks her to. Runs the plugin update on her Mac and reports the version before and after. Not for editing Notion pages named "Skill: …" or the "AI Skills & Context Docs" database; those are her Notion AI's instructions, a different thing, and this skill never touches them.
---

# Update the fundraising-engine skills

"The skills" here means **this plugin**: the instructions you are reading now, installed on her Mac from the Metanoia consultant's public repository. It does **not** mean the Notion pages called "Skill: …" in her "AI Skills & Context Docs" database. Those belong to her Notion AI. Never edit them as part of an update. If she really means those, she'll say so; ask once if unsure.

## Steps

1. **Version before.** Read `version` from this plugin's `plugin.json` (two folders up from this file) and tell her.
2. **Update.** In the terminal on her Mac, run:

   `codex plugin marketplace upgrade`

   If it says the marketplace isn't known, add it first: `codex plugin marketplace add krystof-metanoia-ops/metanoia-cold-email`, then run the upgrade again. If the terminal isn't available in this chat (a cloud chat), say so and ask her to open a chat that runs on her Mac.
3. **Version after.** Read `plugin.json` again and tell her: "Updated from X to Y" or "Already the newest (X)".
4. **Start fresh.** Tell her to open a **new chat** before carrying on. This chat keeps the instructions it started with until it ends.
5. **Automatic updates.** Check that the daily auto-update job exists: `ls ~/Library/LaunchAgents/com.metanoia-ops.fundraising-engine.update.plist`. If it's missing, offer to switch it on (`setup` §3c). If it exists, show the last 3 lines of `~/.fundraising-engine/update.log` so she can see it ran.

## Never

- Edit Notion pages, context docs or her Notion AI instructions as part of an update.
- Change anything else on her Mac besides running the update and, on her yes, installing the auto-update job.
