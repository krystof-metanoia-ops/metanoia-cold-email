---
name: build-campaign
description: Build a campaign or wave from approved contacts, ready to launch - create the campaign and wave rows, build the roster, write the template rows, run the dry run, then hand the Active flip and the Push to the operator. Use for "build the campaign", "new wave", "add a follow-up step", "put these approved investors into a campaign", "set up the cold sequence". Not for finding or verifying contacts (find-leads, verify-emails), not for replies (draft-replies), and never presses Active, Sending, Push or Draft Due Emails itself.
---

# Build a campaign or wave, ready to launch

Goal: end with a wave whose roster, copy and dry run the operator has seen, and then she presses the buttons. You prepare. She launches. Read `fundraising-system` first (sections 2, 5, 6, 7, 8); this skill does not repeat them.

Inputs: the approved contacts (from `review-round`), the client config (`~/.fundraising-engine/<client>.json`), the client's context page, and the campaign's own page. Output: parent campaign row, wave row, roster, template rows at Draft, a dry-run report, and a plain hand-off.

## 1. Read before you build

1. Read the context page, especially "Campaign anatomy", "Manual campaigns vs automated waves" and "Recipes". It wins over this skill.
2. Read the campaign's own page (audience, angle, deck version, what not to say) and the client's **Drafting feedback** page. Apply what it says to the copy.
3. Check that the approved contacts are all Email Status = Valid. Anyone who is not goes back to `verify-emails`. You never set Email Status.

## 2. Agree the plan, one wave at a time

Build one wave per conversation. Never several. Write the plan in the chat and wait for her yes before creating anything:

- **Manual or automated?** If she wants to send by hand, one email at a time, this is a manual campaign: no Active steps, no Push, no wave at Sending (see section 8). Otherwise it is an automated wave.
- Which parent campaign it sits under, and the wave's name.
- **Lane:** warm (her own mailbox, drafted for her approval) or cold (SmartLead). A person she knows personally is warm, never cold.
- The audience: which tier or list, and how many contacts you expect.
- The sequence: how many steps, the wait between them, and where the copy comes from (she supplies it, or you draft it for her to edit in the chat).
- Whether she wants it started now or on a date.

Use the context page's vocabulary: campaign = the whole effort, wave = one audience batch, step = one email. If her word is ambiguous (new step or new wave?), ask one question before creating anything.

## 3. Create the parent campaign and the wave

1. Find the parent campaign row. If none exists, create it (Level = Campaign).
2. Create the wave row: Level = Wave, Campaign = the parent, **Status = Drafting**. Not Sending. A Sending wave with a roster drafts or pushes to everyone on it.
3. Stamp every row you create: the Source property, and a dated provenance line in the field the context page names (for example Background). If a row type has no such field, ask her.

## 4. Build the roster

Work from the approved list. For each contact, apply `fundraising-system` section 6. In practice:

1. **Blockers (all lanes):** the six send blockers on the context page, plus any opt-out or do-not-contact. Blocked contacts are never added, and you never clear a Suppression.
2. **Cold lane only:**
   - A contact currently **in conversation** goes to the warm lane. If a colleague at the same firm is in conversation, hold the contact back and ask her.
   - Anyone already on another wave that is Sending or pushed is held back.
   - **Gateways:** write the cold-lane emails to a temporary file outside the plugin folder, one per line, and run `python3 fundraising-system/scripts/mx_check.py < emails.txt`. Hold back firms behind Mimecast, Proofpoint or IronPort while the cold sending domains are young or blocklisted. The check is free. Delete the file afterwards.
   - A returning contact whose Outreach Channel does not match the lane: do not change it. List the contact for her.
3. **Warm lane:** nothing beyond the blockers and opt-outs.
4. **One contact per firm per wave.** If a firm has several approved contacts, keep the one she ranked highest, or ask.
5. **Sender continuity (cold):** for each returning contact, read the sender of the earlier messages from their Interactions. Group the roster by last sending mailbox. Contacts who replied before matter most. Build one wave per group, and name the group in the wave page. If the context page does not say how a wave is tied to a mailbox, ask her to pass this to the Metanoia consultant through `report-a-problem`; do not guess.
6. Add contacts by the contact's **Campaigns** relation (the roster). Add the first 5, check them, then add the rest.
7. Make a list of everyone you held back, with the one-line reason each. She sees it in the report.

## 5. Write the templates

One template row per step, linked to the wave through Outreach Campaign(s). **Status stays Draft.** Only she flips it to Active.

- **Page body = the exact email the investor receives.** No notes to the writer, no instructions, no brackets.
- The only personalisation is `{{first_name}}`. Any other token disappears silently when sent, so never invent one. `{a|b}` spintax is allowed.
- **Subject Line:** set on step 1. Empty on a follow-up, so it threads as a reply. A set subject starts a new thread.
- **Step Number** in order. **Delay (days)** is the wait after that step before the next one. Never 0.
- **No signature.** The system adds one.
- Show her each email in the chat. She approves or edits the wording there; apply her edits and add the feedback line (`fundraising-system` section 7).

## 6. Dry run

The dry run changes nothing and is free of email risk. Run it yourself in the terminal on her Mac:

- Warm lane: `python3 fundraising-system/scripts/workers.py preview-drafts --client <slug> <wave page id>`
- Cold lane: `python3 fundraising-system/scripts/workers.py preview-feed --client <slug> <wave page id>`

1. Read the answer back to her in plain words: how many would be drafted or pushed, and why the others are skipped. A refusal is also an answer, e.g. "2 steps are not Active and will not be pushed". It tells her what's missing before she presses anything.
2. If it says the Notion CLI isn't logged in, see `setup` §2b. As a fallback, ask her Notion agent to run previewDrafts / previewFeed and paste the result here.
3. Never run the arming tools (pushToSmartLead, draftNow, appendLeads) from the terminal. They are her buttons in Notion, and the approval gate blocks them anyway.

## 7. Report, then hand over

Give her this in plain words:

- Wave name, lane, and the roster count.
- Who was held back and why (the list from section 4).
- The steps: subject, wait, and status of each (all Draft).
- The dry-run numbers, quoted as the tool gave them.
- What is still missing, if anything.

Then tell her what she does and what each press does. You do not press them.

- **Template Status = Active** (each step, by her): approves that exact copy for the whole wave. Until then the machinery treats the sequence as ending before that step.
- **Warm wave: set the wave to Sending.** The drafter writes a Drafted email for every contact on the roster, within the hour. Nothing sends until she approves each draft. Adding contacts to a wave that is already Sending drafts for them automatically.
- **Cold wave: Push to SmartLead.** On a wave that has never sent, this is not a test. It creates the campaign in SmartLead, attaches the sending mailboxes, writes the sequence, uploads the roster, sets the schedule and starts it. Real email begins on SmartLead's schedule. SmartLead then owns cadence and stops a contact on reply or bounce. The undo is `pauseCampaign`. On a wave that is already sending, Push only adds new copy and new contacts; it re-sends nothing to anyone.
- **Draft Due Emails on the parent campaign** drafts for every wave under it, whatever their status. Tell her not to press it while other waves hold rosters.

After she pushes a cold wave, offer to check the next day: SmartLead's lead count should equal the roster. Leads on SmartLead's blocklist are dropped silently, so a lower count means someone did not go in. Report the difference; `campaign-report` has the read-only call.

## 8. Manual campaign, one email at a time

Skip waves and steps. Create the parent campaign. For each email create an Interaction row: Type = Email, E: Direction = Out, Date & Time = now (an empty date never sends), E: Campaign = the campaign, Sending Status = **Drafted**. Show her each email in the chat. When she signs off, say "this will send N email(s) to [names]" and wait for "approve send" or her clear yes to that exact list. Then set Approved. If she rejects a draft or will write it herself, ask whether to delete the row, and delete it only on her yes. Never leave a decided draft sitting at Drafted. Never send from Gmail and log it by hand.

## Never

- Set Active, Sending or Approved without the approval in section 8. Press Push or Draft Due Emails.
- Clear a Suppression, set Email Status, delete rows in bulk, or change the schema.
- Work around a blocker to make a send possible. Name the blocker and ask.
- Build a second wave before the first is launched or dropped.
- Use a client's name, domain or campaign from memory. Take them from the config and the context page.

If anything here contradicts the context page or the machinery, say so and use `report-a-problem`.
