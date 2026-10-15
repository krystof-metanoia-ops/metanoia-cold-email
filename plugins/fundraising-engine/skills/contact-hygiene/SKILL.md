---
name: contact-hygiene
description: Weekly upkeep of the Contacts database. Use for "clean up the contacts", "tag the new contacts as investors", "find duplicates", "check the auto-created contacts", "fill in the missing firms or channels". Shows counted lists first, writes small batches, never deletes. Does not touch Email Status or Suppression. Not for finding new investors (find-leads), verifying addresses (verify-emails) or adding people to a wave (build-campaign).
---

# Contact hygiene

A weekly pass over Contacts. Read `fundraising-system` first (sections 2, 6 and 8). Read the client's context page too; it names the properties, the views and the workers that react to them.

## Rules for everything below

1. **Look first, write second.** Every task starts read-only and ends with a plan she approves.
2. **Counted dry run before more than 5 rows.** Show: how many rows will change, how many are already fine (skipped), how many are unclear (flagged), how many cannot be done (held, for example no email). Show the first 10 rows as examples. Write the full plan to a file in the working folder. Wait for her yes.
3. **One small batch first.** Write 5 rows, read them back, show her, then do the rest.
4. **Fill, never overwrite.** Set a property only if it is empty. If she wants a value replaced, list those rows and get her yes per row.
5. **Flag, do not guess.** Same name at another firm may be a job-mover or a namesake. Unclear matches go to her.
6. **Stamp provenance.** On every row you change, append one line to `Background`: "Hygiene YYYY-MM-DD: <what changed>". Never replace the existing text. Keep a log (page id, property, old value, new value) so any change can be reverted.
7. **Never touch** `Email Status`, `Suppression`, the `Campaigns` relation, `Paused Until`, `Campaign Status`, `Next Touch`, or any `AUX:` property. The Campaigns relation enrols people in a wave, so a change there can start email. Outreach Channel decides the lane, so see task C.
8. **Never delete or archive.** She does that, one row at a time.
9. **Sizes.** Up to about 20 rows: use the Notion connector. More: write a small script in a scratch folder that imports `fe` from `fundraising-system/scripts/` (`fe.notion(client, method, path, body)`), paginates, waits 0.3 s between writes, retries on HTTP 429, logs errors and carries on, and skips ids already in its log so it can be re-run. If the Notion key is not in the Keychain, tell her to run `setup`; never ask her to paste a key.
10. **Notion reads lag writes.** After you edit a property that a query filters on, re-query until the row shows the new value before you run the next dedupe or count.
11. **A relation property returns only its first 25 links** through the API. For a firm with many contacts, query Contacts filtered on that firm instead.

Run the tasks in this order. She may ask for just one.

## A. Review the auto-created contacts

The machinery creates contacts from the To and Cc lines of emails (Review reason "Auto-created from email"). They wait in the Contacts view "Auto-created – review".

1. List the view. For each contact find the email that created it (Interactions where it is in `Contacts/guests` or `E: CC`) and say in one line who it is likely to be.
2. Propose, from evidence only: the firm (exact match of the email domain to a firm's website domain in Investors; also search by name), `Outreach Channel`, and role. If the person wrote to the operator or she knows them, propose `Personal Email`. If you are not sure, say "not sure".
3. If a contact looks like her own team, a vendor or a non-prospect, tell her. Do not suppress; she decides.
4. She confirms each one. Then fill the blank fields (rules 2 to 6). Do not change `Email Status`: only the person who actually wrote an inbound email is Valid, the rest stay unverified until `verify-emails` runs.
5. A reviewed contact must leave the view. Do what the context page says for that. If it does not say, ask her which property takes a contact out of the view, and do not guess.

## B. Duplicates

1. Find candidate pairs. Strong: same `Email` (ignore case; check `Alternate Emails` too), same LinkedIn URL. Medium: same name and same firm. Weak: same name, different firm (flag only).
2. For each pair show both rows side by side: link, `Created by`, `Source`, Email, Email Status, Outreach Channel, Suppression, Campaign Status, firm, which waves (Campaigns), number of Interactions, any fields that differ.
3. Propose which row to keep and why: the one with the Interactions history, the roster membership and the most filled fields. Never propose to drop a row that carries a `Suppression`; tell her about it instead.
4. She confirms each pair, one by one. Never batch-confirm.
5. After a yes: copy fields that are empty on the kept row from the other row (rule 4), and append to the other row's `Background`: "Duplicate of [link to kept row], confirmed YYYY-MM-DD." Then tell her which row to archive in Notion. You do not delete.
6. Do not move Interactions or roster membership between rows. If the other row is on a live wave roster or has Interactions, say so and use `report-a-problem`: until it is handled, that person could be emailed twice.

## C. Channel and firm gaps

Look for these, and give her counts:
- Investor contacts with no firm in `Investors` (and none in `Companies`). Four safety checks read that relation and stay silent when it is empty.
- Contacts whose firm does not match their email domain.
- Contacts with a blank `Outreach Channel`. A blank channel matches no lane, so the person cannot be emailed. Filling it makes them sendable once the other blockers pass. Say that before you ask.

Propose the fix from evidence only. For firms: exact domain match, otherwise "no match". Do not create firms here; list the unmatched ones for `find-leads` or `review-round`. For channel: `Personal Email` if she knows the person, `Secondary Email` for cold prospects. Never move someone from Personal Email to Secondary Email unless she says so in this chat. She confirms, then write.

## D. Bulk-tag new contacts

Example: "tag the new contacts as investors".
1. Ask what "new" means (added since a date, or from a source) and what tag. Use only values that already exist in the live option list. If the value is missing, ask; never invent an option.
2. Query the contacts, show the counted list with name, firm, source, date added. Exclude rows that already carry a different non-empty value, and show them as skipped.
3. She approves the list. Then run the small batch, read back, then the rest (rules 2 to 6).

## Finish

Re-pull the changed rows and check: planned = written + skipped + flagged + held. Report the numbers, what is left for her (rows to archive, firms to find, flags), and where the log file is. Never say a row was fixed without having read it back.
