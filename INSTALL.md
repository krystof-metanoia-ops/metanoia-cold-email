# Installing the Fundraising Engine skills (for the operator's Mac)

About 30 minutes, done together with Krystof the first time. You don't need a GitHub account or any download, and you don't type commands yourself: open ChatGPT on your Mac in Work mode with **Mac access**, paste each step, and let it do the work. It asks before anything changes.

## You'll need

- A Mac with the ChatGPT desktop app, signed in to your workspace.
- Your logins for SmartLead, MillionVerifier, BounceBan and Notion. ChatGPT walks you through finding each API key.

## Steps

1. **Add the skills.** Paste into ChatGPT:
   > Make sure the Codex command-line tool is installed on my Mac (install it if not). Then run `codex plugin marketplace add krystof-metanoia-ops/metanoia-cold-email` and confirm with `codex plugin marketplace list` that the "metanoia-ops" marketplace is there. Then tell me to restart the ChatGPT app.

   *If that fails,* Krystof can send a zip instead: unzip it into `~/metanoia-cold-email` and list it in `~/.agents/plugins/marketplace.json` as a local plugin, path `./metanoia-cold-email/plugins/fundraising-engine`.

2. **Install the plugin.** Restart ChatGPT, open the **Plugins Directory**, choose the source **Metanoia Ops**, and install **fundraising-engine**.

3. **Trust the approval gate.** ChatGPT shows that the plugin has hooks to review. Read with Krystof what `approval_gate.py` does: it blocks anything that spends credits or sends email until you write "approve spend" or "approve send". Then trust it.

4. **Set permissions to "Ask for approval".** In Work mode's permission menu choose **Ask for approval** ("Always ask to edit external files and use the internet"), not "Approve for me".

5. **Run setup.** Say: `@setup set up the fundraising engine for <client>`. It walks you through everything, one step at a time:
   - finding each API key in SmartLead, MillionVerifier, BounceBan and Notion;
   - storing the keys. You paste each one at a hidden prompt in Terminal, so it never goes into the chat;
   - signing in to Notion's command-line tool, for the dry runs.

   macOS asks you to allow access whenever a key is used. Click **Allow**, never "Always Allow".

6. **Check it.** Say: `run the health check`. You'll see your SmartLead plan status, your sending mailboxes and whether any sending domain is on a blocklist.

## Updating

Updates come from the same place: say `update the fundraising engine skills`, and ChatGPT runs `codex plugin marketplace upgrade`. The morning brief does this once a week by itself. If the approval gate changed, ChatGPT asks you to review it again. That's expected.

## If something looks wrong

Say `report a problem`. It writes a note you can forward to Krystof, and changes nothing.
