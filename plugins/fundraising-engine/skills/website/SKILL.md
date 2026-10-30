---
name: website
description: Change, preview and publish the client's website. Use when the operator says "change the website", "update the site", "edit the homepage", "add a section", "new photo on the site", "show me a preview", "publish the website" or "make it live". Every change goes to a free preview link first; it goes live only when she replies "approve publish". Covers editing the site's text, images and section order, local previews, deploy previews, publishing, and what each step costs on Netlify. Not for new kinds of sections or layouts: that is template work for the Metanoia consultant.
---

# The client's website: edit, preview, publish

The site is two parts:
- **The client's content repository** holds `site.json` (all text, section order, colours), `images/` and `netlify.toml`. This is what you edit.
- **The Metanoia site template** draws the layout. Netlify fetches it at build time from a public repository (named in `netlify.toml`). You never edit it.

Netlify builds the site from the content repository:
- every pull request gets its own **deploy preview** link;
- merging into `main` makes a **production deploy**, which is the live site.

## 0. Where the details are

Read the `website` block of the client config (`~/.fundraising-engine/<client>.json`):

```json
"website": {
  "repo": "<owner/repo of the content repository>",
  "netlify_site": "<Netlify project name>",
  "domain": "<the live domain>"
}
```

If the block is missing, ask the operator for the three values once and add them. Work in a local clone: `gh repo clone <repo> ~/website-<client>` the first time, then `git pull` on `main` before every new change.

## 1. What things cost (Netlify free plan, checked 29 Oct 2026)

- **Deploy previews, branch deploys, draft deploys and local previews: free.** No credits.
- **Each production deploy (each merge to `main`): 15 credits** out of 300 a month, so about 20 publishes a month. Failed deploys are free.
- **Visits** to any deploy, preview or live, cost 2 credits per 10,000 requests. That's negligible for a fund website.
- If the month's credits run out, Netlify pauses the site until next month. That is why publishing is batched and gated.

## 2. Making a change: always a pull request, never `main`

1. **Branch.** Name it after the change: `git switch -c site/<short-name>` from an up-to-date `main`.
2. **Edit.** Change `site.json` and add images to `images/`. Keep the JSON valid (`python3 -m json.tool site.json > /dev/null`). Before inventing a field name, look at how other sections in `site.json` already do it.
3. **Optional quick look, no deploy at all.** Build into a folder and open it from disk:
   - `git clone --depth 1 --branch <template branch from netlify.toml> <template repo> /tmp/site-template`
   - `node /tmp/site-template/build.mjs --content . --out /tmp/site-preview --relative`
   - then `open /tmp/site-preview/index.html`.

   This is good for several small rounds before anything goes to Netlify. The contact form won't send from disk; that's expected.
4. **Pull request.** Commit and push the branch (`git push -u origin site/<short-name>`), then open the pull request: `gh pr create --base main --title "<what changed>" --body "<plain list of changes>"`. Netlify builds a deploy preview for it. It's free.
5. **Get the link.** After a minute or two, run `gh pr checks <number>`, or read the Netlify bot's comment on the pull request (`gh pr view <number> --comments`). The preview address looks like `deploy-preview-<n>--<netlify_site>.netlify.app`.
   - If the preview **failed**, say so and show the error from `gh pr checks`. Don't retry in a loop.
   - On a free plan, Netlify builds a **private** repository only from commits made by the repository owner's account. A commit pushed by anyone else fails. Then the fix is either making the repository public (it holds only the public website) or committing from the owner's account. Ask the operator; don't change repository settings yourself.
6. **Show her.** Send the preview link and a plain list of what changed (old wording → new wording for text). Further edits go on the **same branch**, and the same preview link updates. Keep iterating there.

## 3. Publishing: only on "approve publish"

1. **Batch.** Publish once a set of changes is ready, not after every tweak. Each publish is 15 credits.
2. **Before asking, say:**
   - what goes live (the list from step 2.6);
   - that it is one production deploy, 15 credits;
   - if you can check, how many production deploys already happened this month. Count the merged pull requests this month with `gh pr list --state merged --search "merged:>=<YYYY-MM-01>"`.
3. **Wait** for her latest message to contain **"approve publish"**. The approval gate blocks merging into `main` without it. Don't rephrase the command or split it to get around the gate.
4. **Merge:** `gh pr merge <number> --squash --delete-branch`. Then watch the production deploy once (`gh pr checks`, or the site itself after 2 minutes), and confirm the live domain shows the change.
5. **Undo** if something is wrong on the live site: revert the merge with a new pull request, and publish that the same way. Don't push fixes straight to `main`.

## 4. Content rules

- **No invented facts.** No numbers, fund terms, track-record figures, names, quotes or dates the operator hasn't given you. A fact that's still missing stays a visible placeholder, written `{{Operator: what is missing}}` in `site.json` (it shows as a yellow chip). Remove the chip only when she supplies the fact.
- **Investor names, co-investors and portfolio companies** appear only once she has confirmed they may be shown publicly.
- **Photos** only from the client's own sources (their photo shoot, their Drive). Never stock photos or AI-generated images of real people.
- **Legal notice and eligibility wording:** don't rewrite them. Changes go through her counsel.
- **Search engines:** previews and `*.netlify.app` addresses stay out of search engines. If `static/_headers` sets `X-Robots-Tag: noindex`, leave it until the real domain points to the site. Removing it is part of the domain switch (§6), not an everyday edit.

## 5. What is not hers to change

- **New kinds of sections, layouts, animations or template code.** Describe what she wants and route it to the Metanoia consultant with `send-feedback` or `report-a-problem`. Don't edit the template repository, and don't paste HTML into `site.json` (it's escaped and won't render).
- **Netlify settings:**
  - build settings, domains, form notifications;
  - anything in the Netlify dashboard.

  Walk her through clicks if she asks, but you don't change them from the terminal.
- **Production deploys outside the pull-request flow:** `netlify deploy --prod`, manual deploys, re-running production builds. The approval gate blocks `netlify deploy --prod` outright.

## 6. Domain switch (once, with the Metanoia consultant)

Pointing the real domain at Netlify is a one-time job done together with the Metanoia consultant:
- add the domain in Netlify;
- change only the website records (A `@` and `www`) at the registrar;
- remove the noindex header.

**Never change MX, SPF, DKIM, DMARC or verification TXT records.** They carry her email. If she asks for DNS changes, explain this and offer to set up the session with the consultant.

## Never

- Push to `main`, merge, or publish without "approve publish" in her latest message.
- Run `netlify deploy --prod`, or trigger builds in a loop.
- Invent facts or numbers, or remove a placeholder without the fact.
- Touch email-related DNS records.
- Edit the site template or Netlify settings.
