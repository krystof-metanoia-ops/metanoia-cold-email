---
name: setup
description: One-time setup of the fundraising-engine skills on a new Mac or for a new client — writes the client config, stores the API keys in the macOS Keychain, checks the approval gate and the ChatGPT settings, and runs a free health check. Use when the operator says "set up", "install", "add a new client", "connect SmartLead / MillionVerifier / BounceBan", or a script says no client or no key is configured. Not for day-to-day work.
---

# Setup

Do this together with the operator, one step at a time. Nothing here spends credits or sends email.

**Start every time with the checklist:** `python3 setup/scripts/check_setup.py [--client <slug>]` (use the full path in the installed plugin). It lists each step as DONE or MISSING. Begin at the first MISSING step, skip what's done, and re-run it at the end. The same order is written out in the plugin's INSTALL.md.

## 1. The client config

Ask for, or read from the client's Notion context page:
- a short **slug** (lowercase, e.g. `acme`);
- the client's name;
- the context page title;
- the **primary domain** (her real mailbox's domain);
- the **cold sending domains**;
- the Notion data source IDs for Contacts, Interactions, Campaigns and Templates. They're on the context page, or the Metanoia consultant has them.

Copy the template `setup/client.example.json` to `~/.fundraising-engine/<slug>.json` and replace every `<...>`. The checklist reports a config with any `<...>` left as MISSING. The fields:

```json
{
  "client": "<name>",
  "context_page": "<title>",
  "primary_domain": "<domain>",
  "cold_domains": ["<domain>", "..."],
  "notion": { "contacts_ds": "...", "interactions_ds": "...", "campaigns_ds": "...", "templates_ds": "..." }
}
```

No secrets go in this file.

## 2. The keys, into the Keychain: walk her through it live

She has never done this, so go one tool at a time. Give her ONE instruction, wait for "done" or a screenshot, then the next. If what she sees doesn't match your description, ask her to describe or screenshot the page, and find the right button together. Menus move; don't insist on these exact names.

**Make a new key for this Mac in each tool; don't reuse an existing one.** The automated workers already use their own keys, and a separate key can be revoked later without breaking them.

1. **SmartLead.** She must be an admin of the account.
   1. Open app.smartlead.ai and sign in.
   2. Click her profile (top right), then **Settings**.
   3. Find the API keys section (called "API Keys" or "API Key Management") and click **Create API Key**. Name it "ChatGPT – <her Mac>".
   4. **Copy it immediately:** SmartLead shows a new key only once.
2. **MillionVerifier.**
   1. Open app.millionverifier.com and sign in.
   2. Click her profile (top right), then **Account settings**, then the **API KEYS** tab. The direct page is app.millionverifier.com/api.
   3. Click **Add new API key** and copy it.
3. **BounceBan.**
   1. Sign in at bounceban.com.
   2. Find the API section of the dashboard. Look in the menu for "API" or "API keys". Create or copy a key.
   3. If she can't find it, ask for a screenshot and look together.
4. **Notion (optional, only for bulk writes such as writing verification results back).**
   1. In Notion: **Settings → Connections → Develop or manage integrations → New integration**.
   2. Choose the client's workspace and name it "ChatGPT – <her Mac>". Copy the "Internal Integration Secret".
   3. Then, on each of the Contacts, Interactions, Campaigns and Templates databases, use **⋯ → Connections** to add the integration.

**Storing them:** after she has copied a key, give her the exact command, with the script's full path in the installed plugin (find it): `bash <full path>/setup/scripts/setup_keys.sh <slug>`. She runs it **in her own Terminal app**, not through your terminal tool: the script asks at hidden, interactive prompts your tool can't answer, and that's what keeps keys out of the chat. It asks for each key at a hidden prompt: she pastes and presses Enter, or just Enter to skip one. She can do one tool at a time and re-run it for the next; re-running replaces nothing she skips.

**Never** ask her to paste a key into the chat, and never print one.

Every time a script reads a key, macOS asks her to allow it. She clicks **Allow**, not "Always Allow". That prompt is a physical second check before anything uses a paid service.

## 2b. The Notion CLI, for the dry runs

The dry runs (what drafting or a Push WOULD do) are Notion Worker tools. Notion's command-line tool runs them from her Mac.

1. Install it in Terminal: `curl -fsSL https://ntn.dev | bash`, then check with `ntn --version`.
2. Run `ntn login`. A browser window opens: she signs in with her own Notion account and picks the client's workspace.
3. Add to the client config the workspace id (`notion_workspace_id`) and the two worker ids (`"workers": {"email-drafter": "...", "smartlead-feeder": "..."}`). The Metanoia consultant has them.
4. Test on any wave: `python3 fundraising-system/scripts/workers.py preview-feed --client <slug> <wave page id>`. It must answer with what it would push, or why not.

The approval gate allows only the dry runs and pausing. Pushing, drafting and appending need "approve send", and deploying or changing workers is blocked outright.

## 2c. GitHub, for sending feedback

Feedback goes to the plugin's public GitHub issues (`send-feedback`).
1. If she has no GitHub account, she creates one at github.com/signup. Free; walk her through it.
2. Install the GitHub command-line tool. With Homebrew: `brew install gh`. Without it, download the macOS installer from cli.github.com.
3. Run `gh auth login`, then choose GitHub.com, HTTPS, and log in with a web browser. She confirms the code in the browser.
4. Check with `gh auth status`.

## 3. Settings in ChatGPT (with her, about 10 minutes)

- **Permissions for Work / Codex: "Ask for approval"** ("Always ask to edit external files and use the internet"). Not "Approve for me".
- **The approval gate hook only runs in local Codex threads.** OpenAI runs ChatGPT Work from its cloud even with Mac access, and there plugin hooks are not supported. In a Codex thread that runs locally, the hook appears for review: read `approval_gate.py` together and trust it. Do paid or sending work in such a thread when possible. Everywhere else the hard check is the Keychain prompt (§2): every key read needs her click on Allow.
- **Gmail app:** sending set to "Always ask", or off. Email goes out through Notion approvals, not from the chat.
- **Clay app:** every credit-spending action set to "Always ask".
- **Credits:** set a monthly limit for her seat.
- **Scheduled tasks:** look through her list together and delete anything that sends or approves. Then create the ones in `campaign-report`.

## 4. Check it works (free)

1. `python3 fundraising-system/scripts/check_health.py --client <slug>`. Expect the SmartLead plan status, the mailboxes and the domain blocklist results.
2. **Test the approval gate.** Ask for a verification preview, then the run, without approving. The run must be blocked. Then she types "approve spend" and runs it on one address of her own.
3. Tell her what passed and what didn't. Anything that failed goes to `report-a-problem`.
