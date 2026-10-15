---
name: review-round
description: Run a review round over newly sourced investors ("review the new investors", "go over the new leads", "run the review", "what needs my decision") — brief the operator in the chat on new firms and the few contacts needing a human call, take her verdicts as loose dictation, write them back to Notion as page comments plus the review properties, then hand the approved ones to build-campaign. Not for sourcing (find-leads), not for verifying emails (verify-emails), not for sending anything.
---

# Review round: from a sourced wave to a list of approved firms

Follow `fundraising-system` first (§1 for config and context page, §6 for who may be emailed, §7 for feedback). The conversation happens here in the chat. Notion is the record. Nothing in this skill sends or arms an email.

## The model: review the firm, not every person

A sourcing wave produces firms and one new contact per firm. **The firm is the unit of review.** The contacts ride along: she has never met them, and approving 23 strangers one by one buys nothing.

- The **firm queue** is the real queue: new firms waiting for a verdict.
- The **contact exception queue** is only for people with something specifically wrong: the wrong firm, a bounced address, an email that landed while their firm was mid-conversation, a contact created automatically from an email. Never put a whole wave in it.
- A **review reason** on a row means "something is wrong with this record". Do not stamp it on every new row. That is how a queue of 178 rows nobody worked was made.

## 1. Find the review properties (do not guess them)

Review properties and their exact names differ by client. Before anything else, find them on the context page and in the Investors and Contacts database schemas. You need four things, usually on BOTH databases:

| Purpose | Usual shape | How it is used |
|---|---|---|
| Verdict on a firm (relevance tier, plus options such as conflicted, no campaign fit, excluded) | select | Her verdict. Read each option's own definition in Notion. Never invent a meaning. |
| Exception flag (review reason) | select | Something is wrong with THIS record. Empty means nothing wrong. |
| Latest review comment | text | One line, rewritten each round, so the whole list reads at a glance. |
| Last reviewed | date | The date a human last gave a verdict. Empty means never reviewed. |

If any of the four is missing, or you are unsure which property is which, ask the operator one question before writing anything. Do not create properties. Schema changes belong to the Metanoia consultant (see `report-a-problem`).

**A tier is not a verdict.** Many firms carry a tier that was derived from where the row came from, and nobody looked at it. An empty Last reviewed means no human has judged the row. Never tell her a firm "was graded A" on the strength of a tier on an unreviewed row. Say "the sourcing pass put it at A because <evidence>".

## 2. Prepare the batch

1. Select firms with Last reviewed empty that came from the latest sourcing round (use the strategy section on the campaign page for the date, or ask). Do not edit views or filters to do this; list the rows yourself.
2. Evidence gate. Every firm needs a tier, an evidence sentence and a source link. If a firm lacks them, or the wave never had its shortlist check (`find-leads` §5), tell her so before spending her attention, and offer to run the check first.
3. Contact exceptions: contacts with a review reason set, contacts created automatically from email, contacts whose address bounced, and contacts whose firm is mid-conversation (firm Pipeline Stage advanced, or a recent human reply in Interactions). For each, write one plain sentence on what is wrong.
4. Count: new firms by tier, exceptions, and anything you cannot place.

## 3. Brief her, then stop talking

Open with substantially this, adapted to the batch:

> I have **N new firms** from the [date] sourcing round waiting for your read: [X] tier A, [Y] B, [Z] C. Below, each has the evidence and a source link.
>
> **Just dictate your reaction.** No need to be systematic. "Firm X is a yes", "I know the person at Y, he's warm", "skip anything in [region]", or **"everyone else is fine"** and I'll mark the rest approved.
>
> When you're done I'll add your comment to each firm's page so there's a history, rewrite the Latest review comment so the list reads at a glance, and stamp Last reviewed with today's date.
>
> **What happens next, so you can object now:** everyone you approve becomes eligible for the cold outreach campaign. Tell me who should be **held back**, and who should go to the **warm lane** instead: people you actually know, where a cold sequence would be the wrong first touch. Nothing sends from this step.

Then list the firms grouped by tier (name, one-line evidence, link, the contact and role), then the contact exceptions with their one-sentence problem. Keep every line short. Do not interrogate her firm by firm.

## 4. Read her verdicts

- A blanket ("everyone else is fine") covers every firm not named individually. Say back how many it covered.
- A yes with no tier keeps the tier. A yes that contradicts the tier overrides it: she wins, and you record that she did.
- "I know them" is a warm-lane signal, not only an approval. Flag it.
- A reason to reject maps to the verdict options by their definitions (no campaign fit, excluded, conflicted). A rejection is never a silent deletion.
- A general preference ("skip the Gulf", "family offices only after the funds") is a sourcing rule. Apply it to this batch, then append one dated line to the "Sourcing strategy" section of the campaign page: what she said, why if she said, which campaign.
- Anything ambiguous stays unreviewed. Ask about all of those at the end, in one message.

Before writing, read her the result as one list: approved N, warm-lane N, held back N, rejected N, still unclear N. Write only after she has not objected to the list.

## 5. Write it back

Per firm she gave a verdict on, in this order:
1. Add a **page comment**: her words, dated, marked as her verdict dictated in the chat. This is the permanent history. Never overwrite one. (Everything you write in Notion shows as written by her, so say it is her dictation.)
2. Rewrite **Latest review comment**: one line, the verdict plus the reason.
3. Set **Last reviewed** to today. This is what takes the row out of the queue; nothing else does.
4. Set or confirm the **verdict property**.
5. If she raised something specific and unresolved, set the **review reason**; otherwise leave it empty.

Do all of comment and rewrite. Without the comment you lose history; without the rewrite you lose the overview.

Contacts inherit their firm's outcome. Touch a contact row only if she said something about that person. When you clear a review reason, list what you cleared and why in your report: it is the only trace.

Never write Email Status in this skill. Deliverability says a mailbox exists; it does not say this is the right person, and a Valid never clears an identity doubt.

## 6. Hand the approved ones on

Approval means eligible for outreach, not sent.

1. Quote back: how many contacts, which campaign, which lane. Get her go-ahead unless she already gave it in the dictation.
2. Warm-lane picks: set the contact's Outreach Channel to the value the context page names for the warm lane, and leave them for her own first touch. They do not go on a cold wave.
3. Check each approved contact against `fundraising-system` §6 before it goes to `build-campaign`:
   - the six send blockers are clear (Email filled, Email Status Valid, channel matches the lane, Suppression empty, not suppressed on a wave, not paused). Contacts with no Valid status yet go to `verify-emails` first;
   - someone in an active conversation goes warm, not cold. A firm already in diligence or a booked conversation never gets cold mail: that mistake has been made once and took five pauses to undo;
   - nobody already in another live cold campaign;
   - run `fundraising-system/scripts/mx_check.py` over the addresses, report the split, and hold Mimecast, Proofpoint and IronPort firms off the cold lane while the cold domains are young or listed. Held is not rejected: note them for a later wave;
   - returning cold contacts keep their previous sender (sender continuity, §6).
4. Do NOT enrol anyone, set a wave, or add contacts to a roster here. Hand the checked list to `build-campaign`, which builds the wave and runs the dry run. She flips templates Active and presses Push herself.

## 7. Report

Give her: reviewed N; approved N and handed to `build-campaign`; warm-laned N; held back N (including held for the mail gateway); rejected N with the verdict used; skipped with the reason; still unclear N (the batched questions). Offer the next step: `verify-emails` for contacts not yet Valid, then `build-campaign`.
