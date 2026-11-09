---
name: report-a-problem
description: The report to the Metanoia consultant — use whenever the operator says "report to <her consultant's name>", "tell <him> what happened", "send this to my consultant", "write a report for the consultant", or asks what you or another chat or a scheduled task has been doing; and when something looks wrong anywhere in her AI setup ("this looks off", "why did that happen", "it didn't send", "wrong status", "duplicate email", a scheduled task or connector failing), or when you notice a fault yourself. Covers her whole AI setup, not only email outreach: these skills, scheduled tasks, connectors, Notion, the website, files and anything you built for her. Collects the evidence, writes one short report, and saves it in the session log so the consultant can read it there. Reports only; never repairs, never guesses causes. Not for public feedback about the skills (send-feedback) or routine questions.
---

# Report to the Metanoia consultant

Two kinds of report, one skill:
- **Problem report:** something looks wrong.
- **Activity report:** she wants the consultant to see what was done (for example "report to <his name> what you did with the contacts"), or he asked for one.

Her consultant is the Metanoia consultant (Metanoia Ops), who built and maintains her setup. She may call him by name (the client's context page uses his name). Any request to "report to" or "tell" him starts this skill.

**Scope: her whole AI setup.** Email outreach is only one part of it. A report can cover these skills, scheduled tasks she or you created, connected apps (Notion, Gmail, Clay, Lovable and others), the website, decks and files you made for her, and your own behaviour in past chats. (Widened 9 Nov 2026, the Metanoia consultant's call: her ChatGPT had set up its own hourly sync, outside the plugin, and its failure surfaced only as one line in a morning brief.)

The rule from `fundraising-system` sections 8 and 10: report, do not repair. Everything you write in Notion shows as written by the operator, and the workers react to every change. A fix attempt can make the fault worse or send email.

## 1. Stop

1. Make no further writes to the rows, tasks or settings involved. Do not create a replacement row, flip a status, retry a send, press a button, pause or edit a scheduled task, or clear anything.
2. If something may be about to send to the wrong person, tell the operator now, in one sentence, and say what she can do herself (for example set the row back to Drafted, or ask the Metanoia consultant to pause the wave). Do not do it for her.

## 2. Collect the evidence (read-only)

Use what you can actually see, and name each source: this chat, earlier chats if chat history is available to you, the Agent session logs (section 7b of `fundraising-system`), your scheduled tasks and their run history, and the Notion rows. Never fill a gap from memory.

For each affected row or item, gather:
1. **The link** to the row, page, task or file (and to its contact, campaign or wave if relevant).
2. **Created by.** Rows made by a worker show the worker's name (for example "SmartLead Sync"). Rows made in a chat or by hand show the operator's name. A hand-made row is not evidence of what the system did: its status was typed, not reported. Say which it is.
3. **What was expected** and **what you see.** Quote the actual values: for an email row, Sending Status, Date & Time, E: Direction, Review text, Email Status, Suppression, Campaign Status, Message Class, and any error text; for a scheduled task, its exact name, schedule, instruction text, status, and each run's date, result and error text; for a script, the exact error line.
4. **When** it happened (dates and times from the records, not from memory). Run `date` if you need the current time.
5. **What you did NOT change.** State it plainly: "I have not edited or created anything about this."
6. Anything on the context page that covers it: quote the sentence. If the context page and the machinery disagree, say that.

For an **activity report**, also gather: what she asked for, the method you used and why, the numbers (records in scope, done, skipped, failed, still open), credits spent and the approvals that covered them, and what is still open and for whom.

Useful reads: the row's `Review` property, the contact's send blockers, the other Interactions on the thread, `fundraising-system/scripts/check_health.py --client <slug>` (mailboxes, domains, SmartLead), and `setup/scripts/check_setup.py` (config, keys, Notion CLI). All are free and read-only.

**Before you report a key as missing, run `check_setup.py`.** It shows whether each Keychain item exists. A script error that says the Keychain "could not be read from here" means the key is there but your terminal can't reach it: retry with access to her Mac, and ask her to click Allow on the Keychain prompt. Never ask her to run setup again for a key that exists.

## 3. Do not guess

- Name a cause only if you can point at the records that show it. Otherwise write "I don't know why".
- Never join two symptoms into one story unless a record connects them.
- Say whether you saw a failure in a run history or concluded it from data (for example from the Automations Runs Log). These are different kinds of evidence.
- "I don't know how the system will react to this" is a correct sentence. Use it.
- A bounce with a policy or security refusal is not a bad address. Do not call the contact invalid, and do not set Email Status.

## 4. Write the report

Keep it short enough to read on a phone. Problem report:

> **Problem:** one sentence.
> **Where:** links, with Created by for each.
> **Expected:** ...
> **Seen:** ... (quoted values, dates, error text)
> **Source:** what you read (run history, Notion rows, this chat, session logs).
> **Not changed:** I have not edited, created or deleted anything about this.
> **Unknown:** what I could not tell.
> **Needs:** what you need from the Metanoia consultant, and whether anything may send in the meantime.

Activity report:

> **Asked:** what she asked for, in her words.
> **Done:** the method, then the numbers, with links.
> **Spent:** credits per tool, and the approvals that covered them.
> **Problems:** anything that failed or looked wrong (use the problem shape above for each).
> **Open:** what is still waiting, and for whom.

When she asks about several things at once, write one section per thing, under one report.

## 5. Save it where the consultant can read it

1. **Always** write the report to the session log (`fundraising-system` section 7b), even if this chat changed nothing else. This is the one exception to "a chat that only reads writes nothing": a report is meant to be read later. Title the row `YYYY-MM-DD · Report for <consultant's name>: <topic>`, tick **Problem** if the report contains a problem, put the full report in the page body, and set Status = Done. No keys, no tokens, no full email bodies.
2. Show the same report in the chat, with the link to the session-log row, and say: "<consultant's name> can read it in the session log; you can also forward it as it is." Use the name the context page gives for the consultant; if it gives none, say "the Metanoia consultant".
3. If the session-log database does not exist, say so in one line, show the report in the chat, and ask her to forward it. Do not create a database.

## 6. After the report

- Say what happens next: the Metanoia consultant reads it, and nothing in the system has changed until he acts.
- Offer to re-check later (read-only) and report what changed.
- Anything that touches sending, suppression, Email Status, Pipeline Stage past Engaged, scheduled tasks, or deleting rows needs her explicit yes, even if she asks you to "just fix it". Tell her you are not able to repair it in this skill, and why.
