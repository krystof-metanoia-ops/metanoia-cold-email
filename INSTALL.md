# Installing the Fundraising Engine skills (for the operator's Mac)

About 30 minutes, done together with the Metanoia consultant the first time. You don't download anything, and you don't type commands yourself: open ChatGPT on your Mac in Work mode with **Mac access**, paste each step, and let it do the work. It asks before anything changes.

## You'll need

- A Mac with the ChatGPT desktop app, signed in to your workspace.
- A GitHub account, for sending feedback on the skills. Setup helps you create one if needed.
- Your logins for SmartLead, MillionVerifier, BounceBan and Notion. ChatGPT walks you through finding each API key.

## Steps

1. **Add the skills.** Paste into ChatGPT:
   > Make sure the Codex command-line tool is installed on my Mac (install it if not). Then run `codex plugin marketplace add krystof-metanoia-ops/metanoia-cold-email` and confirm with `codex plugin marketplace list` that the "metanoia-ops" marketplace is there. Then tell me to restart the ChatGPT app.

   *If that fails,* the Metanoia consultant can send a zip instead: unzip it into `~/metanoia-cold-email` and list it in `~/.agents/plugins/marketplace.json` as a local plugin, path `./metanoia-cold-email/plugins/fundraising-engine`.

2. **Install the plugin.** Restart ChatGPT, open the **Plugins Directory**, choose the source **Metanoia Ops**, and install **fundraising-engine**.

3. **The approval gate (local Codex threads only).** In ChatGPT Work the plugin's hook doesn't run, because Work is run from OpenAI's cloud. Your safety check there is the macOS prompt that appears whenever a script uses one of your keys. In a Codex thread running locally on your Mac, ChatGPT shows the hook for review: read with the Metanoia consultant what `approval_gate.py` does (it blocks spending, sending and posting until you write "approve spend", "approve send" or "approve post"), then trust it.

4. **Set permissions to "Ask for approval".** In Work mode's permission menu choose **Ask for approval** ("Always ask to edit external files and use the internet"), not "Approve for me".

5. **Run setup.** Say: `@setup set up the fundraising engine for <client>`. ChatGPT first runs the checklist (`setup/scripts/check_setup.py`), then works through whatever is MISSING, in this order. You can also follow it yourself:

   **5a. Client config.** Copy `setup/client.example.json` (inside the plugin) to `~/.fundraising-engine/<slug>.json`, where `<slug>` is a short lowercase name for the client, e.g. `acme`. Then fill every `<...>`:

   | Field | Where it comes from |
   |---|---|
   | `client`, `context_page` | The client's name; the title of their Notion context page |
   | `primary_domain`, `cold_domains` | Your real mailbox's domain; the separate cold-sending domains |
   | `notion_workspace_id`, `workers`, `notion` | The context page, or ask the Metanoia consultant. These are IDs, not secrets |

   **5b. API keys.** In each tool, create a **new** key just for this Mac:
   - **SmartLead:** profile, then Settings, then API keys, then Create API Key. It's shown only once, so copy it immediately.
   - **MillionVerifier:** profile, then Account settings, then the API KEYS tab, then Add new API key. The direct page is app.millionverifier.com/api.
   - **BounceBan:** the API section of the dashboard.

   Then, in your own **Terminal** app (not in the chat), run:
   ```
   bash <plugin folder>/skills/setup/scripts/setup_keys.sh <slug>
   ```
   ChatGPT tells you the exact path. Paste each key when asked; nothing shows on screen. Press Enter to skip a tool.

   **5c. Notion command-line tool** (for the dry runs):
   ```
   curl -fsSL https://ntn.dev | bash
   ntn login
   ```
   Sign in and pick the client's workspace.

   **5d. GitHub** (only for sending feedback): create an account at github.com/signup, then:
   ```
   brew install gh        # or the installer from cli.github.com
   gh auth login          # GitHub.com, HTTPS, log in with a web browser
   ```

   macOS asks you to allow access whenever a key is used. Click **Allow**, never "Always Allow".

6. **Check it.**
   - Say `run the health check`. You'll see your SmartLead plan status, your sending mailboxes and whether any sending domain is on a blocklist.
   - Then say `verify <one of your own addresses>`. A macOS "allow access" dialog must appear before anything is spent. If it runs without one, stop and tell the Metanoia consultant.

## Which chats can use it

Installed with the commands above, the plugin lives on your Mac. It's available in chats that run on your computer (the ChatGPT desktop app with access to your Mac), which is also where the SmartLead, verification and other terminal steps work. A cloud chat (chatgpt.com in the browser, the phone app, or Work running in the cloud) can't see it, and will say the plugin is unavailable.

To have it in every chat as well, a workspace owner or admin imports it once in the browser: chatgpt.com → Admin → Plugins → Add → Import marketplace, with this repository's URL. It then updates from GitHub daily (**Sync now** forces it). Cloud chats get the instructions this way, but terminal work still needs a chat on your Mac. Details: `setup` §3d. Not every plan has this import: if Admin → Plugins shows only Apps and Skills, skip it and work in chats on your Mac.

## Updating

Setup offers to switch on **automatic updates**: a small job on your Mac fetches new versions every morning at 07:00 and at login, so you never need to ask. (`setup/scripts/install_autoupdate.sh`; `--remove` turns it off.) You can still update by hand any time: say `update the fundraising engine skills`. If the approval gate changed, ChatGPT asks you to review it again. That's expected. **Start a new chat after an update.** A chat that is already open may keep the skills it started with.

## Feedback

If a skill gets something wrong, is confusing, or should do more, say `send feedback`. ChatGPT asks three short questions (or drafts the answers from your chat), removes anything that identifies you, your investors or the client, shows you the result, and posts it after you reply "approve post". It goes to the public issues page of this repository, where you can also upvote what other users asked for.

## If something looks wrong

Say `report a problem`. It writes a note you can forward to the Metanoia consultant, and changes nothing.
