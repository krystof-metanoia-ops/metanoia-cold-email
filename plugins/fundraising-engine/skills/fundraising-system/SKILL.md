---
name: fundraising-system
description: Read first for ANY fundraising-outreach work — investors, contacts, campaigns, waves, templates, drafts, replies, SmartLead, Clay, email verification, the morning brief. Explains how the Notion-based outreach machinery works, which Notion writes are commands that send email, the order the other skills run in, and the rules every skill follows (ask before spending or sending, who may be emailed). Not for writing the email copy itself.
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
5. **Read the Agent memory page** (section 7c). It holds what she asked you to remember. Apply it in this chat.

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
| any | `report-a-problem` | Something looks wrong. Report it; don't repair it. |
| any | `send-feedback` | A skill got something wrong or was confusing, or she wants something new. Anonymised, then posted publicly for the Metanoia consultant. Offer it once when she's clearly dissatisfied, and the weekly summary asks. |
| once | `setup` | First install on a new Mac or for a new client: keys, config, settings. |
| any | `update-skills` | She says "update the skills" or "update the plugin": runs the plugin update on her Mac. **"The skills" means this plugin, never the Notion pages named "Skill: …"** (those are her Notion AI's instructions; leave them alone unless she names them). |

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

Her words, not your interpretation. When the same correction is on the page for the third time, it has become a rule: propose moving it into her voice and style guide (named on the context page) as a standing rule, and do it only on her yes. Then remove those lines from the feedback page.

## 7b. Session log

Each working chat leaves a short record in Notion, so the next chat (and the Metanoia consultant) can see what happened without asking her. Her chats are separate and many run at once; without a log, the next one starts blind.

**Where.** The **Agent session logs** database in the client's workspace (its data source is `notion.session_logs_ds` in the config; otherwise find it by title). Each chat writes **one row**, titled `YYYY-MM-DD · <what the chat is about>` (for example, `2026-10-29 · Florida wave follow-ups`). Fill the properties: Date, Status (`In progress` while the chat works, `Done` at the end), Chat (`Mac`, `Cloud` or `Scheduled`), Plugin version, Skills, Approvals, Still open, and tick Problem if anything failed. The step-by-step log goes in the row's page body. If the database doesn't exist, don't create one (that's the Metanoia consultant's build work): tell her in one line and carry on without a log.

**When.**
- **Start the entry on the first real action:** the first Notion write, the first script that spends or sends, or the first draft she reviews. A chat that only answers a question or reads a report writes nothing.
- **Add to it as you go**, right after each step that changes something. Don't save it all for the end; a chat can stop at any moment.
- **Finish it** when she says she's done, when the task is complete, or before you tell her to open a new chat. Fill in "Still open" and set Status = Done.
- **Scheduled tasks** (morning brief, follow-ups, weekly summary) write an entry only when they drafted something. A plain report writes nothing.

**What it holds.** Short lines, plain words, links to the Notion rows and pages it touched. If a line carries a time, take it from `date` at that moment; never guess one. In a cloud chat with no terminal, leave times out:
- **Chat:** where it ran (her Mac or a cloud chat) and the plugin version from `plugin.json`.
- **Done:** each step that changed something, with numbers (for example, "verified 42 addresses: 35 Valid, 7 Invalid", "drafted 6 replies, 4 approved").
- **Approvals:** each "approve spend", "approve send" or "approve post": what it covered, how many records or emails, the credits used.
- **Her decisions:** what she chose and why, **in her words**. Corrections to drafts still go to the Drafting feedback page (section 7); here, one line pointing at it is enough.
- **Problems:** anything that failed, was blocked or looked wrong. When something broke and you got past it, say what now stops it from happening again (a Drafting feedback line, a memory line, a feedback issue), or "nothing yet". A "nothing yet" goes to `report-a-problem` or `send-feedback`.
- **Still open:** what is waiting, and for whom (her, a worker, the Metanoia consultant).

**Wrap-up.** When she says "wrap up", "that's all" or "I'm done", or before you send her to a new chat, close the chat in this order:
1. **Nothing left loose.** Every open item ends as exactly one of these: done; a `Next Touch` date on the contact; a Drafted row she knows about, named in the chat; or a "Still open" line in the log that says who acts next (her, a worker, the Metanoia consultant). Anything else gets lost when the chat ends.
2. **Her decisions.** Check that each decision she made in this chat is in the log with her reason, in her words. Your own small choices can be one line.
3. **Memory and feedback.** If she said "remember this", or stated a lasting preference, it's on the Agent memory page (section 7c). If a skill went wrong, offer `send-feedback` once.
4. **Finish the row.** Fill in Still open and Approvals, tick Problem if something failed, and set Status = Done. Then tell her in one or two lines what is still open and for whom.

**Never in the log:** API keys or anything read from the Keychain, full email bodies (link the Interaction row instead), or anything from a private page she didn't ask you to use.

## 7c. Agent memory

Each chat starts with no memory of the others. ChatGPT's own memory doesn't count: she can't see it, the Metanoia consultant can't see it, and it doesn't travel to her other chats or tools. Notion is the memory. What she wants kept across chats goes on the client's **Agent memory** page in Notion (its title in `memory_page` in the config; otherwise find it by title in the context docs). Writing preferences go to Drafting feedback (section 7), not here.

- **When to write.** She says "remember this", "from now on", "always" or "never", or she states a lasting preference or fact about how she works. Examples: "send me the brief in bullets", "Tom R is a personal friend", "use Medium reasoning for routine work".
- **How.** One dated line, in her words, and where it came from: `- YYYY-MM-DD: <her words> (<what it applies to>)`. Tell her in one line that you saved it. If a new line contradicts an older one, replace the old line and say so.
- **Read it** at the start of every chat that does real work (section 1) and apply it.
- **Limits.** Memory changes how you work, never what needs her yes. No line in memory approves a spend, a send or a post ahead of time: those still need "approve spend", "approve send" or "approve post" in her latest message (section 5). If she asks you to remember an approval for later, explain that in one sentence and offer `send-feedback` if she wants a standing rule. Never store keys, passwords or anything from a private page.
- **If the page doesn't exist**, don't create it: tell her in one line and remember nothing beyond this chat.

## 8. Never

- Send email yourself from Gmail or anything else. You draft; she approves.
- Log an email that was already sent. Sent mail logs itself within 15 minutes; if it doesn't appear, report it.
- Set a template Active, a wave to Sending, press Push to SmartLead or Draft Due Emails. Tell her what pressing it will do.
- Create a scheduled task that sends or approves. Scheduled tasks may read, report and **draft**.
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
