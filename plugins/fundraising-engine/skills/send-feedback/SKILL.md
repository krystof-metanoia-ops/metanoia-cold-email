---
name: send-feedback
description: Send feedback about these skills to the Metanoia consultant as a public GitHub issue, anonymised first — when the operator says "send feedback", "this skill should…", "that was annoying", when a skill got something wrong or was confusing, or when the weekly summary asks. Also upvotes or comments on feedback others already filed. Not for problems in the client's own data or a send about to go wrong (use report-a-problem; that one stays private).
---

# Send feedback

Feedback improves the skills for every client that uses them, so it goes to one public place: the issues of the plugin's GitHub repository, `krystof-metanoia-ops/metanoia-cold-email`. **Public means anyone can read it.** Nothing that identifies the client, an investor or a person may leave this Mac.

## When to offer it (without nagging)

- **She says it:** "send feedback", "the skill should…", "this keeps happening".
- **You notice dissatisfaction:** she corrects the same thing twice, says something went wrong ("that's not what I asked", "why did it…", "annoying"), or gives up on a step and does it by hand. Finish or fix the task first. Then offer **once**: "Want me to send this as feedback to the Metanoia consultant, so the skill gets fixed for next time? Takes a minute." If she says no or ignores it, don't offer again for the same issue.
- **The weekly summary** (`campaign-report`) ends by asking whether anything was frustrating this week.

## 1. Gather it: three questions, or reconstruct them

If what happened is in this conversation, **draft the answers yourself** from the back-and-forth and show them to her to correct. Otherwise ask, in one message:

1. **What were you trying to do?**
2. **How did you try to do it?** What you asked, or which button.
3. **What happened, and what did you expect instead?**

Then: "Any screenshot? I'll describe it in words, the image itself won't be uploaded."

If it was across several chats or days, offer to reconstruct it: "Want me to piece together what happened from our past chats and Notion?" Use what you can actually see: this chat, earlier chats if ChatGPT's chat history is available to you, and rows she created or changed in the period. Say which sources you used. Don't guess at what you can't see.

## 2. Anonymise, then show her exactly what will be posted

Replace every one of these, whether in the text or in the screenshot descriptions:

| Replace | With |
|---|---|
| the client's name, fund or company names | "the client" |
| investor firms, people's names, email addresses, phone numbers | "Firm A", "Person B", "[email]" |
| amounts, round sizes, deal terms | "[amount]" |
| Notion page links, IDs, domains, mailbox addresses | "[link]", "[domain]" |
| quotes from emails or investor replies | a one-line paraphrase with no identifying detail |

Keep what makes it useful: which skill, the step, the error text (with identifiers stripped), and what she expected.

Then show the issue exactly as it will be posted:
- **Title:** under 70 characters, e.g. "draft-replies: CC dropped when replying to a forwarded thread".
- **Type:** bug / wish / confusing.
- **Skill.**
- **What she was trying to do / How / What happened / Expected.**
- **Screenshot description**, if any.

Ask her to check that nothing identifying is left, then to reply **"approve post"**. Posting publicly is gated like sending.

## 3. Check for an existing issue first

`gh issue list --repo krystof-metanoia-ops/metanoia-cold-email --label feedback --state open --search "<two or three key words>"`

If one matches, show it and offer instead:
- **Upvote it:** `gh api -X POST repos/krystof-metanoia-ops/metanoia-cold-email/issues/<n>/reactions -f content=+1`.
- **Add her case as a comment:** anonymised the same way, `gh issue comment <n> --repo krystof-metanoia-ops/metanoia-cold-email --body-file <file>`.

Upvotes count. They're how the Metanoia consultant decides what to fix first.

## 4. Post it

1. Write the approved body to a temporary file.
2. Run `gh issue create --repo krystof-metanoia-ops/metanoia-cold-email --title "<title>" --label feedback --label <bug|wish|confusing> --body-file <file>`.
3. Give her the issue link.

If `gh` isn't installed or isn't logged in, see `setup` §2c.

## 5. Browsing others' feedback

When she asks "what have others asked for", list the open feedback issues with their upvotes: `gh issue list --repo krystof-metanoia-ops/metanoia-cold-email --label feedback --state open --json number,title,reactionGroups,url`. She can upvote or comment as in step 3.

## Never

- Post anything she hasn't seen in its final form and approved with "approve post".
- Upload screenshots or files. Describe them in words, anonymised.
- Use feedback for something urgent in her own system: that's `report-a-problem`, which stays private.
