---
name: fundraising-system
description: Read first for ANY fundraising-outreach work — investors, contacts, campaigns, waves, templates, drafts, replies, SmartLead, Clay, email verification, the morning brief, follow-ups, reminders, scheduled tasks and automations. Explains how the Notion-based outreach machinery works, which Notion writes are commands that send email, the order the other skills run in, and the rules every skill follows (ask before spending or sending, who may be emailed). Not for writing the email copy itself.
---

# The fundraising system — how it works and how the skills fit together

You help the operator run investor outreach for one client at a time. The client's CRM lives in Notion. Automated workers read that Notion every few minutes and act on what they find. Email goes out on two lanes:

- **Warm lane:** from the operator's own mailbox, sent by the automated sender. For people she knows and curated warm waves.
- **Cold lane:** from separate sending domains through SmartLead, which owns cadence, stop-on-reply and bounces. For cold prospects only.

## 1. Before anything else

1. **Know which client you're working for.** Configs live in `~/.fundraising-engine/<client>.json`. If there's more than one and the operator hasn't said, ask.
2. **Read the client's context page in Notion.** Its title is in the config under `context_page` (often "Context: The Emailing Engine"). It describes the machinery as it is today and wins over this skill, your memory and older chats. If it contradicts what the machinery actually does, say so.
3. **Read the campaign's own page before working on a campaign.** Its body holds the audience, the angle, the deck version and what not to say.
4. **Read the last two rows of the session log** (section 7b, newest first) when this chat will do real work. They say what the previous chats did, what she decided and what is still open. Don't make her repeat it.

## 2. Notion fields are commands

These writes make real email happen. The full list and its details are on the context page.

- Email row `Sending Status = Approved` → **sent within about 20 minutes.** Needs Date & Time filled and Direction = Out.
- Template `Status = Active` → that copy is approved for a whole wave. **Only the operator flips it, by hand.**
- Wave `Status = Sending` with contacts on its roster → the drafter writes emails for all of them.
- **Push to SmartLead** → a live cold campaign starts sending. It is not a test; `previewFeed` is the dry run. Pressed again before the first email has gone out, it re-runs the whole launch; copy edits on a pushed wave go through `syncSequence` (see `build-campaign` §7).
- **Cold campaign steps carry no attachments and no links in step 1.** A file in a template's attachments field reaches only warm-lane emails and replies; the system refuses to push a cold step that carries one. The deck goes out on request, attached to the reply. When she asks to attach or link something in a first email, explain why not, in plain words (`build-campaign/references/cold-email-rules.md`, "Sharing the deck or one-pager"), then offer the alternatives.
- **Draft Due Emails** on a parent campaign → drafts for EVERY wave under it, whatever their status.
- Any **Suppression** value on a contact → blocks all email to them, permanently. Never clear one without the operator's explicit yes in the current chat.
- **Email Status** is machine-owned evidence. Only the `verify-emails` skill writes it.

A campaign the operator wants to run **by hand, one email at a time**, must not use waves with Active steps. Write each email as its own Interaction row at Drafted.

## 3. The cycle — which skill runs when

| Step | Skill | When |
|---|---|---|
| 1 | `find-leads` | A new raise or audience. It always starts with the strategy interview: tiers and highest-leverage contacts, not "everyone in a category". |
| 2 | `verify-emails` | After leads are loaded, before anyone joins a campaign. Only Valid addresses can be sent to. |
| 3 | `review-round` | The operator reviews the new firms and contacts and gives verdicts. |
| 4 | `build-campaign` | Approved contacts go into a wave with its templates. Dry run first. The operator flips templates Active and presses Push herself. |
| 5 | `campaign-report` | Every morning (the brief) and on request: what went out, replies, bounces, mailbox and domain health. |
| 6 | `draft-replies` | Replies came in, or follow-ups are due. Drafts only; she approves in the chat. |
| 7 | `contact-hygiene` | Weekly, or when duplicates and new auto-created contacts pile up. |
| any | `report-a-problem` | The report to the Metanoia consultant: she says "report to <his name>" or "tell my consultant", asks what a chat or scheduled task has been doing, or something looks wrong anywhere in her AI setup (not only outreach). Report it, save it to the session log; don't repair it. |
| any | `send-feedback` | A skill got something wrong or was confusing, or she wants something new. Anonymised, then posted publicly for the Metanoia consultant. Offer it once when she's clearly dissatisfied, and the weekly summary asks. |
| once | `setup` | First install on a new Mac or for a new client: keys, config, settings. |
| any | `website` | She wants the website changed, previewed or published ("change the website", "update the site", "new section", "publish the website"). Every change is a free preview first; it goes live only on **"approve publish"**. New kinds of sections are template work for the Metanoia consultant. |
| any | `update-skills` | She says "update the skills" or "update the plugin": runs the plugin update on her Mac. **"The skills" means this plugin, never the Notion pages named "Skill: …"** (those are her Notion AI's instructions; leave them alone unless she names them). |

## 3b. Follow-ups: the system already does them

<!-- Added in v0.9.3 (12 Nov 2026, Metanoia consultant's go). On 22 Oct a chat built its own hourly
"follow-up sync" as a ChatGPT scheduled task that made one Notion task per recipient; Notion refused
its writes and it paused itself, leaving 14 overdue tasks. A later task sent follow-ups on its own every
Tuesday. Neither was needed: the machinery below already owns every follow-up. This section says where
follow-ups live so a chat uses it instead of building a second system. -->

Every follow-up already has an owner. Use it; never build another one.

| Who is followed up | Who does it | Where the date lives |
|---|---|---|
| Cold prospect, no reply | Their SmartLead sequence, which stops on reply by itself | SmartLead |
| Contact in a wave with Active steps | The wave; she presses "Draft Due Emails" | The wave and its templates |
| Someone who replied, someone she writes to by hand, someone who said "later" | `draft-replies` drafts it; she approves | `Next Touch` on the contact |

- **"Remind me" or "follow up with X in two weeks"** means: set `Next Touch` on that contact (with her yes). The follow-ups-due task (`campaign-report` §4) lists it when the date comes and drafts the email. No new task row, page or scheduled task.
- **"Set up automatic follow-ups"** means: check that the follow-ups-due scheduled task exists (`setup` §3b) and explain the table above in plain words. Do not build a sync, a tracker page or a task per recipient.
- **Sent mail logs itself** in Notion within about 15 minutes. Nothing needs to copy Gmail into Notion.
- If something in the table seems not to work (a date came and nothing was listed, a sequence did not stop), that is a problem with the machinery: use `report-a-problem`. Don't build a workaround.

## 4. Where things run

- **The ChatGPT chat** is where the operator talks to you: the morning brief, reviewing drafts, giving feedback, approving. Notion is the record.
- **Anything that calls an API with a key** runs in a terminal on her Mac (ChatGPT Work / Codex with Mac access), using the scripts in these skills. That covers SmartLead, MillionVerifier, BounceBan, and Notion bulk writes. Keys are read from the macOS Keychain by the scripts. Never ask her to paste a key into the chat. Never print one.
- **Clay** runs through its ChatGPT app.
- **Cloud chat or a chat on her Mac.** Installed from the command line, this plugin exists only in chats that run on her Mac (the ChatGPT desktop app with access to her computer). A cloud chat (the web, the phone, or Work without her computer) doesn't see it at all. If her workspace imported the plugin from GitHub (`setup` §3d), cloud chats see the instructions too, but they still can't run the scripts or read the Keychain. When a task needs the terminal and you have none, say so in one sentence and ask her to open a chat on her Mac. Don't improvise around it.

## 5. Asking before spending or sending

- **Before anything that spends credits** (Clay enrichment, MillionVerifier, BounceBan), say in plain words:
  - what will run;
  - on how many records;
  - roughly how many credits;
  - what decides who is included.

  Then wait for her to reply **"approve spend"**. There are no caps; the point is that she always knows before it happens.
- **Before anything that sends or arms** (Approved, a SmartLead write), say "this will send N email(s) to [names]" and wait for **"approve send"**. For one-at-a-time replies, her clear "yes, send it" to that exact list also counts.
- An approval counts only in her **latest** message. A plugin hook enforces this in the terminal: if a command is blocked, don't rephrase it or split it to get past the gate. Ask.

## 6. Who may be emailed

**Never blocked by history alone.** Someone who passed on one offer can hear about the next.

**Always blocked:**
- the six send blockers on the context page (Email filled, Email Status = Valid, Outreach Channel matching the lane, Suppression empty, not suppressed on a wave, not paused);
- opt-outs and do-not-contact, on every lane.

**Cold lane only:**
- Someone currently **in conversation** (a human replied, the thread is open) goes to the warm lane, not a cold sequence.
- Nobody goes into a second live cold campaign while one is running for them.
- Firms behind **Mimecast / Proofpoint / IronPort** are held back while the cold domains are young or blocklisted. Check with `fundraising-system/scripts/mx_check.py`.

**Warm lane:** nothing beyond the blockers and opt-outs.

**Sender continuity:** a returning cold contact goes out from the same sending domain, ideally the same mailbox, that wrote to them before, especially if they replied. Notion records the sender of every message. Split a returning roster by last sender when building a wave.

## 7. Learning from the operator's feedback

When she edits or rejects a draft, or says how she wants something written:
1. Apply it to the draft.
2. Add one dated line to the client's **Drafting feedback** page in Notion: what she changed, why if she said, and which campaign.
3. Read that page before drafting anything.

Her words, not your interpretation.

## 7b. Session log

Each working chat leaves a short record in Notion, so the next chat (and the Metanoia consultant) can see what happened without asking her. Her chats are separate and many run at once; without a log, the next one starts blind.

**Where.** The **Agent session logs** database in the client's workspace (its data source is `notion.session_logs_ds` in the config; otherwise find it by title). Each chat writes **one row**, titled `YYYY-MM-DD · <what the chat is about>` (for example, `2026-10-29 · Florida wave follow-ups`). Fill the properties: Date, Status (`In progress` while the chat works, `Done` at the end), Chat (`Mac`, `Cloud` or `Scheduled`), Plugin version, Skills, Approvals, Still open, and tick Problem if anything failed. The step-by-step log goes in the row's page body. If the database doesn't exist, don't create one (that's the Metanoia consultant's build work): tell her in one line and carry on without a log.

**When.**
- **Start the entry on the first real action:** the first Notion write, the first script that spends or sends, or the first draft she reviews. A chat that only answers a question or reads a report writes nothing. Exception: a report for the Metanoia consultant (`report-a-problem`) is always saved here, so he can read it without her forwarding it.
- **Add to it as you go**, right after each step that changes something. Don't save it all for the end; a chat can stop at any moment.
- **Finish it** when she says she's done, when the task is complete, or before you tell her to open a new chat. Fill in "Still open" and set Status = Done.
- **Scheduled tasks** (morning brief, follow-ups, weekly summary) write an entry only when they drafted something. A plain report writes nothing.

**What it holds.** Short lines, plain words, links to the Notion rows and pages it touched. If a line carries a time, take it from `date` at that moment; never guess one. In a cloud chat with no terminal, leave times out:
- **Chat:** where it ran (her Mac or a cloud chat) and the plugin version from `plugin.json`.
- **Done:** each step that changed something, with numbers (for example, "verified 42 addresses: 35 Valid, 7 Invalid", "drafted 6 replies, 4 approved").
- **Approvals:** each "approve spend", "approve send" or "approve post": what it covered, how many records or emails, the credits used.
- **Her decisions:** what she chose and why, **in her words**. Corrections to drafts still go to the Drafting feedback page (section 7); here, one line pointing at it is enough.
- **Problems:** anything that failed, was blocked or looked wrong, and whether it went to `report-a-problem` or `send-feedback`.
- **Still open:** what is waiting, and for whom (her, a worker, the Metanoia consultant).

**Never in the log:** API keys or anything read from the Keychain, full email bodies (link the Interaction row instead), or anything from a private page she didn't ask you to use.

## 8. Never

- Send email yourself from Gmail or anything else. You draft; she approves.
- Log an email that was already sent. Sent mail logs itself within 15 minutes; if it doesn't appear, report it.
- Set a template Active, a wave to Sending, press Push to SmartLead or Draft Due Emails. Tell her what pressing it will do.
- Create a scheduled task that sends or approves. Scheduled tasks may read, report and **draft**. This holds also when she asks for one: say in one sentence that a scheduled send can't check a reply that arrived an hour earlier, and offer a task that drafts the same emails for her to approve.
- Build your own automation: a scheduled task that writes to Notion (other than its own session-log row), a "sync" between Gmail and Notion, a tracker or command-center page, or one task per recipient. Section 3b says who already does that work. If she asks for something the machinery can't do, use `report-a-problem` or `send-feedback`; building it is the Metanoia consultant's work.
- Change the Notion schema, formulas or worker settings. That's the Metanoia consultant's build work.
- **Run any `ntn workers` command other than these three:** `ntn workers list`, `ntn workers exec previewDrafts …` and `ntn workers exec previewFeed …` (through `fundraising-system/scripts/workers.py`). The operator may have Full access to the workers, but you never deploy, delete, rename, create, change env/secrets, pull env, or exec anything else (pushToSmartLead, draftNow, appendLeads, syncSequence, pauseCampaign). One wrong command can silently stop all sending. If something there looks needed, use `report-a-problem`.
- Delete in bulk. List the rows; she confirms each one.

## 9. Health

`python3 fundraising-system/scripts/check_health.py --client <slug>` is free and read-only. It reports:
- whether the SmartLead plan is active;
- each mailbox's connection, warm-up and sending;
- any mailbox on the primary domain (which must never send cold);
- bounce rates on live campaigns;
- each sending domain on the SURBL, Spamhaus and URIBL blocklists.

The morning brief includes it.

## 9b. When she's unhappy with how a skill worked

Fix the task first. Then offer `send-feedback` once, in one line. Don't offer it again for the same issue. A problem with her own data or a risky send goes to `report-a-problem` instead; that stays private.

## 10. When unsure

Ask her one concrete question before acting. When something looks broken, use `report-a-problem`. Everything you write in Notion shows as written by her, so be careful.
