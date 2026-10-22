---
name: campaign-report
description: The campaign and health report, in one fixed format - use for "morning brief", "how are the campaigns doing", "campaign report", "what's waiting for me", "who replied", "follow-ups due", "weekly summary", "is everything healthy", and as the body of the scheduled morning, follow-up and weekly tasks. Read-only - sent, opens, replies, bounces per live campaign, drafts waiting, unread threads, follow-ups due, mailbox and domain health. Not for writing replies (draft-replies) or fixing problems (report-a-problem).
---

# Campaign report and morning brief

One report, one format, whether the operator asks for it or a scheduled task runs it. It reads and reports. The only thing it may write is a Drafted email through `draft-replies`. It never approves, sends, or changes a campaign.

Read `fundraising-system` first. Read the client's context page; it says where the Interactions, campaigns and Unread views are and how bounces are classed.

## 1. Gather (read only)

1. **Which client.** From the config in `~/.fundraising-engine/`. If several exist and she has not said, ask. A scheduled task names the client in its text.
2. **Live campaigns.** In Notion, the waves whose Status is Sending, plus anything with a SmartLead campaign in progress. For each, read from SmartLead's campaign analytics (read-only, key from the Keychain via `fundraising-system/scripts/fe.py`): sent, opens, replies, bounces. Report opens only if the analytics return them; otherwise write "opens: not available".
3. **Bounces, split.** Read the wave's Interactions with Message Class = Bounce and read the bounce text.
   - **Policy refusal** ("rejected due to security policies", "envelope blocked", "sender address blocked", a named blocklist): the mail gateway refused our domain. The address is almost certainly fine. Report it as a refusal, never as a bad address.
   - **Real bounce** ("user unknown", "no such recipient"): a dead address.
   - Unsure: say "unclear" and leave it.
   Never set Email Status or a Suppression because of a bounce. Refusals at large firms point to the gateway problem on the context page; flag them for the Metanoia consultant through `report-a-problem`.
4. **Drafts waiting.** Interactions with Sending Status = Drafted and Direction = Out. Also rows at Send failed, and rows at Approved with an empty Date & Time (these never send).
5. **Threads needing her.** The Unread view, and inbound human replies with no outbound after them and no "No reply needed" stance. Skip Auto-reply, Bounce, Unsubscribe and Other. Read each reply's Reply Sentiment if present.
6. **Follow-ups due.** Contacts whose Next Touch is today or earlier, and in-conversation threads where the last message is ours and older than 5 days.
7. **Health.** Run `python3 fundraising-system/scripts/check_health.py --client <slug>`. It is free and read-only. Read its docstring for what it covers: SmartLead plan status, each mailbox (connection, warm-up, sent versus limit), any mailbox on the primary domain, bounce rates on live campaigns, and blocklist listings for each sending domain (SURBL, Spamhaus, URIBL). If the terminal or key is not available (for example in a scheduled run), write "health: not run, no terminal access" and say why. Do not guess.

## 2. The report format

Use exactly these headings, in this order. Plain words, short lines, numbers first. Skip nothing; write "none" for an empty section.

```
Campaign report - <client> - <date>

NEEDS YOU
- N drafts waiting for approval
- N replies waiting for a response
- N follow-ups due
- Health: OK / N things to look at

CAMPAIGNS (one block per live campaign)
<campaign / wave> - <lane>, status
  Sent N - Opens N - Replies N - Bounces N (policy refusals N, real N)
  Anything unplanned: a step Active or a wave Sending that she did not set, failed rows

DRAFTS WAITING
<name, firm> - <campaign> - one line of what the email says

REPLIES AND UNREAD
<name, firm> - what they said in one line - suggested next step

FOLLOW-UPS DUE
<name, firm> - Next Touch date or days since our last message

HEALTH
SmartLead plan: ... 
Mailboxes: N connected, N warming, N with errors; any over 3% bounce
Primary domain: no mailbox on it / WARNING
Domains: clean / listed on ... (which)
```

Rules for the content:
- Numbers come from the sources, not from memory. If a source failed, name it.
- Anything that looks wrong goes under NEEDS YOU in one line, then `report-a-problem` if she wants it filed. Do not repair it.
- A bounce rate of 3% or more on a campaign or mailbox gets a line. SmartLead itself warns at about 5 to 6%.
- A refusal count that is high on one gateway is a finding, not a list of bad contacts.

## 3. The morning brief (chat flow)

The scheduled morning task produces this report and, where replies came in, drafts for them. The operator then works in the chat:

1. **Brief.** Show the report.
2. **Drafts in the chat.** Show every waiting draft in full, with the recipient, the thread it answers, and who is on CC. She reads them here, not in Notion.
3. **She decides, in the chat.** For each draft she can approve, edit, or reject.
   - **Edit:** apply her words to the Notion draft. Show the new text.
   - **Reject:** ask whether to delete the row. Delete it only on her yes. Never leave a decided draft at Drafted.
   - **Approve:** collect the approved ones, then say "this will send N email(s) to [names]". Wait for her "approve send" or a clear "yes, send it" to that exact list. Only then set Sending Status = Approved (Date & Time filled, Direction = Out). Say it goes within about 20 minutes.
4. **Feedback loop.** When she edits, rejects, or states a preference, append one dated line to the client's **Drafting feedback** page: what changed, why if she said, which campaign. Use her words (`fundraising-system` section 7).

An approval counts only in her latest message. A scheduled run never approves. Drafting new replies uses `draft-replies`.

## 4. Ready-to-paste scheduled tasks

*Scheduled tasks run in OpenAI's cloud, without access to her Mac's Keychain. Inside a task, skip the HEALTH script and write one line instead: "Health check skipped (runs on your Mac): say 'run the health check'." The same goes for the Monday skill update, which needs her Mac: remind her instead.*

Create these in ChatGPT's Scheduled tasks. Replace `<client>` and `<time zone>`. Each task runs under the same rule: read and report, may draft, never approve or send, never touch a template, wave, Push or Suppression.

**Morning brief, daily at 6:00 operator time** (the campaign and mailbox health check is part of this task)
```
Use $campaign-report for <client>. Produce the full report, including the HEALTH section: run the
health check and report the SmartLead plan, mailboxes, primary domain and domain blocklists. For every
inbound human reply with no response, use $draft-replies to create a Drafted reply only. Do not set
anything to Approved. Do not send, approve, activate, push, or change any campaign. If a source or the
terminal is unavailable, say so in the report. End with: "Reply here to approve, edit or reject the drafts."
```

Skill updates arrive by themselves when automatic updates are switched on (setup §3c). If they aren't, the Monday brief reminds her once to say `update the fundraising engine skills` (the `update-skills` skill runs it).

**Follow-ups due, Monday and Thursday at 6:30 operator time**
```
Use $campaign-report for <client>, FOLLOW-UPS DUE and REPLIES AND UNREAD sections only. List contacts whose
Next Touch has arrived and in-conversation threads where we wrote last and have had no answer for
5 days or more. For each, draft a short follow-up with $draft-replies as Drafted only. Never approve or send.
```

**Weekly summary, Friday at 16:00 operator time**
```
Use $campaign-report for <client>. Write a weekly summary: for each campaign this week's sent, opens, replies
and bounces (policy refusals and real bounces separately), meetings booked, the tiers or lists not yet
contacted, and what to source next. Include the HEALTH section. End with: "Was anything about the skills frustrating or confusing this week? Say 'send feedback' and I'll write it up for the Metanoia consultant." Report only. Do not draft, approve, send or post.
```

If she wants a campaign and mailbox health check on its own schedule, it is the HEALTH section of the first task; do not add a fifth task.

## Never

- Approve, send, or set any status other than Drafted.
- Change Email Status, a Suppression, a template, a wave or a SmartLead campaign.
- Print or paste an API key. Health output has none.
