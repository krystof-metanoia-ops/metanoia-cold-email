---
name: verify-emails
description: Verify investor email addresses before they can be emailed — runs MillionVerifier, then BounceBan for anything it can't resolve, and writes Email Status (Valid / Invalid / Unverifiable) on the Notion contacts. Use after new leads are loaded, before building a campaign, or when the operator asks "verify these", "are these emails good", "check the new prospects". Not for diagnosing bounces from a live campaign (that's campaign-report: a gateway refusal is not a bad address).
---

# Verify emails

Only contacts with `Email Status = Valid` can be emailed. This skill is the only thing that writes Email Status. Rules for spending and approvals: `fundraising-system` §5.

## Steps

1. **Pick the contacts.** Agree with the operator which ones: usually the batch just loaded by `find-leads`, or a view she names. Skip contacts that are already Valid, have no email, or carry any Suppression value. Report how many you skipped and why.
2. **Make the input file.** Put one row per contact in a CSV with columns `email,page_id` (page_id = the Notion contact row) in a working folder, e.g. `~/fundraising-work/<client>/verify-<date>.csv`.
3. **Preview, free:** `python3 verify-emails/scripts/verify.py preview <file>`. It prints the unique count and the credit estimate: MillionVerifier about 1 credit per address; BounceBan about a third of them typically, all of them in the worst case.
4. **Ask.** Tell her in one message:
   - how many addresses;
   - which contacts, and the rule that selected them;
   - the estimated credits per tool.

   Then ask her to reply **"approve spend"**. Wait.
5. **Run:** `python3 verify-emails/scripts/verify.py run --client <slug> <file>`.
   - If the approval gate blocks it, ask again. Don't rephrase the command.
   - macOS may ask her to allow access to the key. That's expected; she clicks "Allow".
   - The run is resumable: re-running never pays twice for the same address.
6. **Report the results:** how many came out Valid, Invalid and Unverifiable, and the results file path. Name any surprising Invalid on a contact she knows personally. She may have a better address.
7. **Write back:**
   - With a Notion key configured: `python3 verify-emails/scripts/verify.py writeback --client <slug> <file>.results.csv`.
   - Without one: set Email Status through the Notion app in batches of about 25, from the `email_status` column only. Never type a status from memory.
8. **Hand off.** Valid contacts can go to `review-round` or `build-campaign`. List the Unverifiable ones for her: they can't be emailed cold, and she decides whether someone knows them personally (warm lane) or they're dropped.

## Settling old Catch-all / Unknown contacts (BounceBan only)

Contacts already marked **Catch-all** or **Unknown** went through MillionVerifier before, but never through BounceBan. Don't pay MillionVerifier again. Select them (email filled, no Suppression), make the same CSV, then run the verification script with `--bb-only`:
- preview with `--bb-only` first (about 1 BounceBan credit each);
- after "approve spend", run with `--bb-only --client <slug>`;
- then write back as usual. The re-verify-after-3-months rule doesn't apply here: these were never settled.

## How results map (don't change this)

| MillionVerifier | BounceBan | Email Status |
|---|---|---|
| ok | — | Valid |
| invalid, disposable | — | Invalid |
| catch_all, unknown, error | deliverable | Valid |
| catch_all, unknown, error | undeliverable | Invalid |
| catch_all, unknown, error | risky, unknown, error | Unverifiable |

## Never

- Set Valid by hand, or "because they replied before". Valid is evidence from verification or from a real inbound email.
- Turn a **bounce from a live campaign** into Invalid. Many bounces are the recipient's mail gateway refusing our sending domain, not a dead mailbox. See the context page.
- Re-verify the same people every week. Re-verify only addresses older than about 3 months, or after a real bounce ("user unknown").
