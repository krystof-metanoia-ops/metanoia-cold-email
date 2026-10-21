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

7. **No attachments on any cold step.** The cold lane (SmartLead) cannot send them: a file in the template's attachments field is never sent, and the system refuses to push a cold step that carries one. Never write "I've attached…".
8. **No links in step 1. Later, only to the client's own website.** Never a file-sharing or short link (OneDrive, Dropbox, Google Drive, WeTransfer, bit.ly and the like), on any step.

9. **The only personalisation token is `{{first_name}}`.** Any other `{{…}}` renders as nothing. `{a|b}` spintax is fine.
10. **No signature in the body.** The sending mailbox adds its own.

## Sharing the deck or one-pager

How the material reaches an investor, best first:

- **Offer it, send it on reply (the default).** Step 1 ends with "Would you like the one-pager?" or "Happy to send the one-pager." When they say yes, `draft-replies` puts the file on the reply as a real attachment.
- **A link in a later step**, if the operator wants one: step 2 or later, to a page on the client's own website where the deck lives. Never step 1.
- **Never** a file on a cold step, and never a file-share link.

**Explain why when the operator asks to attach or link something.** Don't just refuse. In plain words:

1. **Spam filters judge a stranger's first email by what it carries.** Links and attachments are how phishing and malware arrive, so a first email from an unknown sender that has either is scored as more suspicious. More of them land in spam or promotions, or are held by company mail gateways (Mimecast, Proofpoint), which quarantine files from new senders.
2. **File-share links look like phishing.** "View the document on OneDrive" from someone you don't know is exactly what credential-phishing emails look like, so gateways treat those links hardest.
3. **Company link scanners click every link.** Microsoft and others open each link to check it, so click numbers turn into scanner traffic and stop telling you who is interested.
4. **Cold domains are young.** Their reputation is fragile, and a link ties every email to the reputation of the site it points to.
5. **Asking works better.** "Would you like the one-pager?" invites a reply. A reply is the strongest good signal to mail providers, and it starts the conversation. A link lets them read it silently and leave, and you never know who looked.
6. **You keep control of the deck.** You know who received it, and you can send the current version.

## Who it comes from

11. **Every sender is a real, named person with a signature.** A mailbox called "Partnerships" or "Team", or one with no signature, sends a first-person email with no sign-off. If the client has spare mailboxes like that, tell the operator before a wave uses them.
12. **The same mailbox sends every step to the same person.** SmartLead does this by itself; don't swap senders mid-sequence.

## Who it goes to

13. **Grade the audience before the wave, not after.** Tiers decide send order. Only "not an investor", defunct, structurally ineligible or conflicted firms are dropped (`find-leads` §5). A list nobody has graded goes through that grading first.
14. **Tell the operator the real numbers.** Recipients, held back by reason, sending days at mailbox capacity. Never only "the wave is ready".

## Changing a campaign after it is pushed

15. **Copy edits on a pushed cold wave go through `syncSequence`, never a second Push before anything has sent.** Before the first email, Push re-runs the whole launch: it attaches mailboxes again and rewrites the sequence. After the first email, Push reconciles safely. `syncSequence` is safe either way.
