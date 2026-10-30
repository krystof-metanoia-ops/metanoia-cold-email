#!/usr/bin/env python3
"""Approval gate: nothing that spends credits or sends email runs without the operator's
explicit approval in her MOST RECENT message.

Why a hook and not just an instruction (the Metanoia consultant, 14-15 Oct 2026): the skills already say
"always ask before spending", but instructions are text in context and an agent under load
skips them — in October 2026 an operator's ChatGPT sent emails from Gmail and set itself a
sending scheduled task despite being told not to. Codex / ChatGPT Work run PreToolUse hooks on the
desktop, and a hook's "deny" is enforced by the runtime, not by the model's good intentions.

How it works (mirrors the spend guard the Metanoia consultant uses in Claude Code):
- UserPromptSubmit: if the prompt contains "approve spend" or "approve send", record that
  approval with the turn id; ANY other prompt clears it, so approval never outlives the
  message it was given in.
- PreToolUse (Bash): if the command would spend (MillionVerifier, BounceBan, Clay API,
  verify.py run) or send/arm (SmartLead writes, Notion writes that set Approved/Active),
  allow it only when an approval of the matching kind exists for the current turn.

Limits, stated plainly: hooks see the local terminal and local MCP tools, not hosted tools
(OpenAI: "Treat tool hooks as a useful guardrail, not a complete enforcement boundary").
Clay through its ChatGPT app is governed by the app's "Always ask" setting instead.
Read-only calls (SmartLead GETs, MillionVerifier/BounceBan balance checks) always pass.
"""
import json
import os
import re
import sys
import time

DATA = os.environ.get("PLUGIN_DATA") or os.path.expanduser("~/.fundraising-engine")
STATE = os.path.join(DATA, "approval.json")

SPEND = [
    re.compile(r"(bulkapi|api)\.millionverifier\.com(?!/api/v3/credits)"),
    re.compile(r"api\.bounceban\.com/v1/verify"),
    re.compile(r"api\.clay\.com"),
    re.compile(r"verify\.py\s+run\b"),
]
SEND = [
    # Any non-GET SmartLead call: adding leads, changing campaign status, sending replies.
    re.compile(r"server\.smartlead\.ai.*-X\s*(POST|PUT|PATCH|DELETE)", re.I),
    re.compile(r"-X\s*(POST|PUT|PATCH|DELETE).*server\.smartlead\.ai", re.I),
    # A Notion write that arms something: a row to Approved, a template to Active.
    re.compile(r"api\.notion\.com.*\"(Approved|Active)\"", re.S),
    # Worker tools that draft, push or arm (15 Oct 2026: ntn is installed on the operator's Mac
    # for the two dry runs only). previewDrafts / previewFeed / pauseCampaign pass freely.
    re.compile(r"ntn\s+workers\s+exec\s+(pushToSmartLead|draftNow|appendLeads|syncSequence)\b"),
]
# Publishing to the public feedback repo (15 Oct 2026): issues, comments and reactions are
# world-readable, so posting is gated like sending — the operator reads the anonymised text first.
POST = [re.compile(r"gh\s+issue\s+(create|comment|edit)\b"),
        re.compile(r"gh\s+api\b.*-X\s*(POST|PATCH|PUT|DELETE)", re.I),
        re.compile(r"gh\s+api\b.*/(issues|comments|reactions)\b.*-(f|F)\s")]
# Publishing the client's website (29-30 Oct 2026, website skill): a merge into main is a production
# deploy (15 Netlify credits on the free plan, and it changes the live site), so it needs
# "approve publish". Branches, pull requests and deploy previews are free and pass.
PUBLISH = [re.compile(r"gh\s+pr\s+merge\b"),
           re.compile(r"git\s+push\b[^\n]*\s(origin\s+)?(HEAD:)?(main|master)\b"),
           re.compile(r"gh\s+api\b.*/pulls/\d+/merge\b")]
# Never from the operator's machine, approval or not: deploying, deleting or re-configuring the
# workers is the Metanoia consultant's build work (a wrong deploy silently stops sending for everyone).
NEVER = [re.compile(r"ntn\s+workers\s+(deploy|delete|env|create|new|rename)\b"),
         # Production deploys outside the pull-request flow (website skill §5): never from here.
         re.compile(r"netlify\s+deploy\b.*(--prod\b|\s-p\b)")]


def load():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def save(d):
    os.makedirs(DATA, exist_ok=True)
    json.dump(d, open(STATE, "w"))


def main():
    ev = json.load(sys.stdin)
    name = ev.get("hook_event_name")

    if name == "UserPromptSubmit":
        p = (ev.get("prompt") or "").lower()
        kinds = [k for k in ("spend", "send", "post", "publish") if f"approve {k}" in p]
        save({"turn_id": ev.get("turn_id"), "kinds": kinds, "at": time.time()})
        return  # exit 0, no output: the prompt goes through unchanged

    if name != "PreToolUse":
        return
    cmd = (ev.get("tool_input") or {}).get("command") or ""
    if any(r.search(cmd) for r in NEVER):
        why = ("A production deploy outside the pull-request flow is never run from here: publish by "
               "merging the pull request after 'approve publish' (website skill §3)."
               if "netlify" in cmd else
               "Changing the workers (deploy, delete, env, create) is "
               "build work for the Metanoia consultant, never done from here. Use report-a-problem instead.")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
              "permissionDecision": "deny", "permissionDecisionReason": why}}))
        return
    need = None
    if any(r.search(cmd) for r in PUBLISH):
        need = "publish"
    elif any(r.search(cmd) for r in POST):
        need = "post"
    elif any(r.search(cmd) for r in SEND):
        need = "send"
    elif any(r.search(cmd) for r in SPEND):
        need = "spend"
    if not need:
        return

    st = load()
    ok = need in st.get("kinds", []) and st.get("turn_id") == ev.get("turn_id")
    if ok:
        return
    what = {"spend": "spends credits", "send": "sends email or arms a campaign",
            "post": "publishes to the public feedback repository",
            "publish": "publishes the website (a production deploy, 15 Netlify credits)"}[need]
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            f"Blocked by the approval gate: this command {what}. Stop and tell the operator, in "
            f"plain words: what will run, on how many records, the estimated credits or emails, "
            f"and the rule that decides who is included. Then ask her to reply with the words "
            f"'approve {need}'. Approval only counts in her latest message. Do not rephrase or "
            f"split the command to get past this check."),
    }}))


if __name__ == "__main__":
    raw = sys.stdin.read()
    try:
        sys.stdin = __import__("io").StringIO(raw)
        main()
    except Exception as e:
        # A broken gate must not silently allow a paid or sending call: fail closed, but only
        # for PreToolUse (a deny shape is meaningless on UserPromptSubmit).
        if '"PreToolUse"' in raw:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                  "permissionDecision": "deny",
                  "permissionDecisionReason": f"Approval gate error ({e}); tell the Metanoia consultant."}}))
