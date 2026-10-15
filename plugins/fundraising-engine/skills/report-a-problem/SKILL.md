---
name: report-a-problem
description: Use when something in the fundraising system looks wrong and the operator asks "this looks off", "why did that happen", "it didn't send", "wrong status", "duplicate email", or when you notice a fault yourself. Collects the evidence and writes a short report for Krystof (who built the system) that the operator can forward. Reports only; never repairs, never guesses causes, never changes the rows involved. Not for routine questions about how the system works.
---

# Report a problem

The rule from `fundraising-system` section 8 and 10: report, do not repair. Everything you write in Notion shows as written by the operator, and the workers react to every change. A fix attempt can make the fault worse or send email.

## 1. Stop

1. Make no further writes to the rows involved. Do not create a replacement row, flip a status, retry a send, press a button or clear anything.
2. If the problem is that something may be about to send to the wrong person, tell the operator now, in one sentence, and say what she can do herself (for example set the row back to Drafted, or ask Krystof to pause the wave). Do not do it for her.

## 2. Collect the evidence (read-only)

For each affected row, gather:
1. **The link** to the row (and to its contact, campaign or wave if relevant).
2. **Created by.** Rows made by a worker show the worker's name (for example "SmartLead Sync"). Rows made in the chat or by hand show the operator's name. A hand-made row is not evidence of what the system did: its status was typed, not reported. Say which it is.
3. **What was expected** and **what you see.** Quote the actual property values: Sending Status, Date & Time, E: Direction, Type, Review text, Email Status, Suppression, Campaign Status, Message Class, and any error text such as Send failed reasons or Feeder Result.
4. **When** it happened (dates and times from the rows, not from memory). Run `date` if you need the current time.
5. **What you did NOT change.** State it plainly: "I have not edited or created any row about this."
6. Anything on the context page that covers it: quote the sentence. If the context page and the machinery disagree, say that.

Useful reads: the row's `Review` property, the contact's six send blockers, the other Interactions on the thread, and `fundraising-system/scripts/check_health.py --client <slug>` if mailboxes, domains or SmartLead may be involved (free, read-only).

## 3. Do not guess

- Name a cause only if you can point at the rows that show it. Otherwise write "I don't know why".
- Never join two symptoms into one story unless a row connects them.
- "I don't know how the system will react to this" is a correct sentence. Use it.
- A bounce with a policy or security refusal is not a bad address. Do not call the contact invalid, and do not set Email Status.

## 4. Write the report

Keep it short enough to read on a phone. Use this shape:

> **Problem:** one sentence.
> **Where:** links, with Created by for each.
> **Expected:** ...
> **Seen:** ... (quoted values and dates)
> **Not changed:** I have not edited, created or deleted anything about this.
> **Unknown:** what I could not tell from the rows.
> **Needs:** what you need from Krystof, and whether anything may send in the meantime.

Show it in the chat. Say: "You can forward this to Krystof as it is." Krystof Ekl (Metanoia Ops) built the system and maintains it. Send it by the route the context page names for faults; if none is named, the operator forwards it herself. Do not look for his address elsewhere.

## 5. Record it in Notion (only if there is a place)

If the context page names a place for problem reports (a page, a database or a comment thread), offer to put the report there and wait for her yes. If it names none, do not invent one. Offer a Notion comment on the affected row instead, and write it only if she agrees. Do not paste anything secret: no keys, no tokens.

## 6. After the report

- Say what happens next: Krystof reads it, and nothing in the system has changed until he acts.
- Offer to re-check the rows later (read-only) and report what changed.
- Anything that touches sending, suppression, Email Status, Pipeline Stage past Engaged, or deleting rows needs her explicit yes, even if she asks you to "just fix it". Tell her you are not able to repair it in this skill, and why.
