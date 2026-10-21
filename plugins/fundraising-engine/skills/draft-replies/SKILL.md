---
name: draft-replies
description: Draft replies to investor emails and due follow-ups in the operator's voice, shown in the chat for her to approve, edit or reject. Use for "answer the replies", "draft a reply to X", "who is waiting for an answer", "follow up with the people who went quiet", or an unsubscribe request. Drafts only; a row becomes Approved only after she says yes in the chat. Not for writing campaign templates (build-campaign), not for the automated wave follow-ups (the Draft Due Emails button does those), not for new cold emails to strangers.
---

# Draft replies and follow-ups

You write in the operator's voice. She approves in the chat. Notion holds the record. Read `fundraising-system` first, especially section 5 (asking before sending), 6 (who may be emailed), 7 (feedback) and 8 (never).

## 1. Load context (every time)

1. Pick the client (`~/.fundraising-engine/<client>.json`). Read the client's context page in Notion, in full. It wins over this skill.
2. Read the client's **Drafting feedback** page. Apply every line to the drafts you write.
3. Read the client's voice and style guide, as named on the context page. If none is named, ask her once where it lives.
4. Run `date` and note the current time. You need it for Date & Time.

## 2. Find what needs an answer

1. **Replies.** In Interactions, find rows with `E: Direction = In`, `E: Message Class = Human reply`, no outbound row after it on the thread, and `E: Reply Stance` empty. (The "Inbound" view shows them.) Ignore Auto-reply, Bounce and Other. Do not create rows for these.
2. **Follow-ups.** Only for campaigns the operator runs by hand, one email at a time. A follow-up is due when the campaign page says so and the last outbound is old enough with no reply. Waves with Active steps follow up by themselves: do not draft for them. If she asks for it, explain that the wave's "Draft Due Emails" button drafts for every wave under that campaign, and she presses it.
3. Cold-lane contacts with no reply are followed up by their SmartLead sequence. Do not draft those by hand.
4. Show her the list first: name, firm, what they said in one line, how long ago. Ask which to do, unless she said "all".

## 3. Understand each one before writing

For each reply, read:
- the whole thread (every Interaction on it, both directions) and the campaign page (audience, angle, deck version, what not to say);
- the contact: Outreach Channel (lane), Email Status, Suppression, Paused Until, Campaign Status, and the firm's Pipeline Stage;
- who wrote the last inbound (`Contacts/guests`) and who was copied (`E: CC`).

Work out what the person is doing. Use `Reply Sentiment` if set as a hint, not as truth:
- asks for the deck, data, or more about the company: a buying signal, send it;
- asks who the operator is or why she wrote: hesitant, answer that and nothing more;
- wants a meeting: propose times or her booking link from the context page;
- interested later: acknowledge, and set `Next Touch` to the date they gave;
- declines on mandate or with a flat no: short thanks, no push. A mandate they state goes in the contact's `Background` as one dated line;
- points to a colleague: thank them, ask for the introduction, make sure the colleague exists as a contact;
- hands the conversation to a colleague in the email text: set the original contact's `Campaign Status = Delegated`. A CC or a colleague adding a comment is not delegation. Set `Committed` only if she tells you to.

## 4. Check before drafting

1. **The six send blockers** on the context page. If the contact fails one, say which and why, and stop on that contact. Never clear or work around a blocker.
2. **Unsubscribe or "remove me":** do not draft a reply. If `Suppression` is empty, set it to `Unsubscribed` on that contact and tell her: "I set Suppression = Unsubscribed on [name] because she asked to be removed." If a value is already there, leave it. Never use `Do not contact`; that is her own verdict.
3. **Cold lane:** a reply goes into the SmartLead thread. It may go only to people who wrote on that thread: the lead, or a colleague who answered it. Anyone else makes the row fail with Send failed. To write to someone new, make a warm email instead, and only if their Outreach Channel allows it.
4. **Someone she knows personally** goes warm, never cold.
5. Never log or re-create an email that was already sent. Sent mail logs itself within about 15 minutes.

## 5. Write the draft

Follow the voice guide and the feedback page. Defaults that hold unless the context page says otherwise:
- Short. Plain words. One clear next step. No hype, no invented numbers, traction or co-investors. If you do not know a fact, ask her or leave it out.
- No signature block, no name, no title. The sender adds the sign-off. You may end with a closing word only if the voice guide asks for it.
- Never put internal scoring, notes about the person, or other investors' names in the text.
- Attachments: the row sends only the files on itself, never the template's. If the reply should carry the deck (check the campaign page for the version), attach it on `Email Attachment`, or tell her to. This is how the deck reaches a cold prospect: the first email offers it, and the reply to their "yes" carries it. On a cold-lane reply, warn her to check that the first attachment arrived.

## 6. Create the row (Drafted)

One Interaction row per email:
- `Type = Email`, `E: Direction = Out`, `Sending Status = Drafted`.
- `Date & Time` = now (from step 1), unless she wants it scheduled. An empty date means it never sends.
- `In reply to` = the message being answered. This threads it. Leave `E: Subject` empty on a reply: the sender makes it "Re: <the original subject>" (verified in the sender's code, 15 Oct 2026). A new email that is NOT a reply must have a subject, or the sender marks it Send failed.
- `Contacts/guests` (To) = the author of the last inbound. `E: CC` = everyone in that inbound row's `E: CC`. Only existing contacts can be CC'd. If she names someone with no contact row, ask her.
- To hand a cold conversation to her: CC the contact row of her own primary address, so the investor can reply-all to her. Only when she asks.
- `E: Campaign` = the campaign. Link the firm. The body is the email text.
- Leave `E: Lane`, `E: Message Class` and every `AUX:` property alone.

## 7. Show her, in the chat

For each draft: To, CC, lane, which message it answers (one line), the text, and any flag (blocker, attachment, tone bet). Finish with this sentence: "These are drafts. Nothing has been sent. Each one sends only after you say yes and I set it to Approved."

Then, per draft, she does one of three things:
- **Approve.** Go to step 8.
- **Edit.** Apply her change and show it again. Then add one dated line to the Drafting feedback page: what changed, why if she said, which campaign.
- **Reject** or "I'll write it myself in Gmail". Ask: "Delete this draft row?" Delete only after her yes, one row at a time. Add a feedback line if she gave a reason.

## 8. Approve

1. Re-read each approved row. Its `Review` property says what is still missing. `Date & Time` filled, Direction = Out, Type = Email.
2. Write: "This will send N email(s) to [names]." Wait for her yes. A clear "yes, send it" to that exact list, or "approve send", counts. It must be in her latest message.
3. Set `Sending Status = Approved` yourself. Do not hand the click back to her.
4. Tell her when it goes out (within about 20 minutes, or at the scheduled time) and where to see it.

## 9. Close the loop

Before you finish, query Interactions for Drafted rows (Out, Email) that you made in this chat. Every one must be Approved, deleted, or parked because she said "leave it". List any parked ones by name. The queue must hold no decided rows.

## Never

- Send from Gmail or any other mailbox.
- Set Approved without the echo and her yes.
- Run this as a scheduled task that approves. Scheduled runs may only draft.
- Set `Email Status`, clear a `Suppression`, or set `Committed` on your own.
