# Fundraising Engine — skills for ChatGPT / Codex

Skills that let a client's ChatGPT (chat, ChatGPT Work, Codex app) operate the Notion-based fundraising outreach system: Notion CRM + email workers + SmartLead + Clay + MillionVerifier + BounceBan.

- **Generic by design.** No client facts live here. Each skill reads the client's own Notion context page ("Context: The Emailing Engine" or its equivalent) for names, IDs and rules. The same plugin serves several clients.
- **Two surfaces.** ChatGPT chat handles conversation, drafting, Notion and the morning brief. The Codex app, on the operator's Mac, handles anything that calls an API with a key (SmartLead, MillionVerifier, BounceBan). Keys live in the macOS Keychain, never in this repo.
- **Always ask before spending or sending.** Every credit-consuming action states what it will do and the rough credit cost, and waits for an explicit yes.

Status: v0.2 (2026-10-15), untested with a live operator. 10 skills, the approval-gate hook, scripts (health check, verification ladder, mail-gateway check, worker dry runs, key setup). Install: see INSTALL.md.

Built and maintained by [Metanoia Ops](https://metanoia-ops.com). No licence is granted: all rights reserved.
