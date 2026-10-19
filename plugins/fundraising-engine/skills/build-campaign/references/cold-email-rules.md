# Cold email rules for investor sequences

Read before writing or editing any cold sequence. These are the working rules. `scripts/check_sequence.py` checks the mechanical ones before a push, so a rule you skim past still gets caught. The client's context page and drafting-feedback page win over this file.

Distilled from the Metanoia cold-outreach playbook (deliverability, sequencing) and from what went wrong on real client campaigns. The reasoning lives there; the rules live here.

## Structure

1. **3–5 emails is the norm for investors.** Longer weekly sequences mostly add spam risk and annoyance. If the operator asks for more, say so once in one sentence, then build what she wants.
2. **About 3 emails per thread.** Step 1 sets a subject. The next two have an empty subject and reply inside the thread. A new subject starts a new thread, at most every third step (4, 7, 10). A new subject on every step reads as repeated blasting, to the recipient and to spam filters.
3. **The first email of each thread stands on its own.** It names the company and the ask, because the recipient may never have opened the earlier thread.
4. **A follow-up inside a thread is a reply, not a re-pitch.** Two to four sentences: one new fact or angle, then the ask again. Don't restate the founder's whole biography every week.
5. **The stop line goes in the last email only.** "If this isn't a fit, tell me and I'll stop following up" is a promise. Sending more emails after it breaks the promise.
6. **The wait between steps is never 0 days.** Weekly is common for investors.

## What a cold email can carry

7. **No attachments.** The cold lane (SmartLead) sends none, even if a file sits in the template's attachments field. Never write "I've attached…" in a cold step. Offer the material instead: "I'd be happy to send the one-pager." Attachments on first contact also hurt deliverability.
8. **No links in the first emails of a thread.** A link to a cold domain or a deck host is the most common spam-filter trigger. If a link is needed, put it in a later reply, and only to the client's real site.
9. **The only personalisation token is `{{first_name}}`.** Any other `{{…}}` renders as nothing. `{a|b}` spintax is fine.
10. **No signature in the body.** The sending mailbox adds its own.

## Who it comes from

11. **Every sender is a real, named person with a signature.** A mailbox called "Partnerships" or "Team", or one with no signature, sends a first-person email with no sign-off. If the client has spare mailboxes like that, tell the operator before a wave uses them.
12. **The same mailbox sends every step to the same person.** SmartLead does this by itself; don't swap senders mid-sequence.

## Who it goes to

13. **Grade the audience before the wave, not after.** Tiers decide send order. Only "not an investor", defunct, structurally ineligible or conflicted firms are dropped (`find-leads` §5). A list nobody has graded goes through that grading first.
14. **Tell the operator the real numbers.** Recipients, held back by reason, sending days at mailbox capacity. Never only "the wave is ready".

## Changing a campaign after it is pushed

15. **Copy edits on a pushed cold wave go through `syncSequence`, never a second Push before anything has sent.** Before the first email, Push re-runs the whole launch: it attaches mailboxes again and rewrites the sequence. After the first email, Push reconciles safely. `syncSequence` is safe either way.
