#!/usr/bin/env python3
"""Check a cold wave's sequence and senders before it is pushed (or edited after a push).

Usage:
  python3 check_sequence.py --client <slug> <wave page id>
  python3 check_sequence.py --client <slug> <wave page id> --smartlead <campaign id>

Read-only: Notion GETs and SmartLead GETs, no writes, no credits. Prints one line per finding:
  FIX    must be fixed before Push, or the operator decides in the chat to keep it as it is
  CHECK  worth a look, not wrong by itself
Exit code 1 if any FIX, else 0.

Why this exists (the Metanoia consultant, 19 Oct 2026): the first wave an operator's ChatGPT
built on its own reached SmartLead with a new thread on every step from 4 to 8, "I've attached
the one-pager" with nothing attachable, a "I'll stop following up" line in step 3 of 8, and three
placeholder mailboxes ("… Partnerships", no signature) among the senders. Each rule was written
down somewhere; none was checked. A skill instruction can be skimmed past; this cannot.
The rules and their reasons: ../references/cold-email-rules.md.

Property names default to the first client's schema and can be overridden in the client config
under "templates" (see DEFAULTS below), so the script stays generic.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "fundraising-system", "scripts"))
import fe  # noqa: E402

DEFAULTS = {
    "wave_steps_relation": "Sequence Steps",   # wave → its template rows
    "step_number": "Step Number",
    "subject": "Subject Line",
    "delay": "Delay (days)",
    "status": "Status",
    "attachments": "Email attachments",      # files property; the cold lane never sends it
    "body_fallback": "Email Body",           # rich_text, used only if the page body is empty
}

# Placeholder-sounding sender names. A real person's mailbox is "First Last". These are the
# patterns that showed up as spare, unsigned mailboxes on the first client.
NON_PERSONAL = re.compile(r"\b(partnerships?|team|info|admin|sales|hello|contact|office|"
                          r"noreply|no-reply|support|outreach|investors?)\b", re.I)

# A promise to stop. Only allowed in the last step (cold-email-rules.md §5).
STOP_PROMISE = re.compile(r"stop (following up|reaching out|emailing)|won'?t (follow up|email|"
                          r"reach out|bother) (you )?again|will not follow up|"
                          r"(my |this is (my|the) )(last|final) (email|note|message)", re.I)

# "I've attached…" and friends. The cold lane uploads no files (rules §7).
# Same phrasings the SmartLead feeder refuses (FIX); apostrophes straight or curly.
ATTACH_PROMISE = re.compile(r"\b(i['’]?ve|i have|we['’]?ve|we have) (also )?attached\b|\bplease find (it |them )?"
                            r"(attached|enclosed)\b|\bsee (the )?attached\b|\battached (is|are|please)\b|"
                            r"\benclosed (is|are|please)\b|\bi['’]?m attaching\b|\bsee the (pdf|deck) below\b", re.I)
# Looser mentions only earn a CHECK ("attachment" also has other meanings).
ATTACH_WORD = re.compile(r"\battach(ed|ing|ment)s?\b|\benclosed\b", re.I)

LINK = re.compile(r"https?://[^\s\"'<>)]+|www\.[^\s\"'<>)]+", re.I)
# File-share and short-link hosts (rules §8). "View the document on OneDrive" from a stranger is the
# credential-phishing pattern, so gateways score these hardest; short links hide the destination.
FILE_SHARE = re.compile(r"(1drv\.ms|onedrive\.|sharepoint\.com|dropbox\.com|drive\.google\.|docs\.google\.|"
                        r"wetransfer\.|we\.tl|box\.com|bit\.ly|tinyurl\.|t\.co/|ow\.ly|rebrand\.ly|cutt\.ly)", re.I)
TOKEN = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")
ALLOWED_TOKENS = {"first_name"}


def prop_value(p):
    if not p:
        return None
    t = p.get("type")
    v = p.get(t)
    if t in ("title", "rich_text"):
        return "".join(x.get("plain_text", "") for x in v)
    if t in ("status", "select"):
        return (v or {}).get("name")
    if t == "number":
        return v
    if t == "files":
        return [f.get("name") for f in v]
    if t == "relation":
        return [r["id"] for r in v]
    return v


def page_text(slug, page_id):
    """Plain text of a page body (the exact email, per build-campaign §5)."""
    out, cursor = [], None
    while True:
        path = f"/blocks/{page_id}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
        code, j = fe.notion(slug, "GET", path)
        if code != 200:
            return None
        for b in j.get("results", []):
            rt = (b.get(b.get("type"), {}) or {}).get("rich_text", [])
            # Keep link targets: plain_text holds only the anchor ("here"), and the URL is what
            # spam filters and the link rules care about.
            out.append("".join(x.get("plain_text", "") + (f" <{x['href']}>" if x.get("href") else "") for x in rt))
        if not j.get("has_more"):
            return "\n".join(out).strip()
        cursor = j.get("next_cursor")


def relation_ids(slug, page_id, prop):
    """All ids of a relation property. Page objects cap relations at 25, so read the
    property endpoint, which paginates."""
    code, page = fe.notion(slug, "GET", f"/pages/{page_id}")
    if code != 200:
        sys.exit(f"Can't read the wave page {page_id} (HTTP {code}).")
    if prop not in page["properties"]:
        sys.exit(f"The wave has no '{prop}' property. Set templates.wave_steps_relation in the config.")
    pid = page["properties"][prop]["id"]
    ids, cursor = [], None
    while True:
        path = f"/pages/{page_id}/properties/{pid}?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
        code, j = fe.notion(slug, "GET", path)
        ids += [r["relation"]["id"] for r in j.get("results", []) if r.get("relation")]
        if not j.get("has_more"):
            return ids
        cursor = j.get("next_cursor")


def load_steps(slug, wave_id, names):
    steps = []
    for sid in relation_ids(slug, wave_id, names["wave_steps_relation"]):
        code, p = fe.notion(slug, "GET", f"/pages/{sid}")
        if code != 200:
            continue
        pr = p["properties"]
        body = page_text(slug, sid) or prop_value(pr.get(names["body_fallback"])) or ""
        steps.append({
            "id": sid,
            "n": prop_value(pr.get(names["step_number"])),
            "subject": (prop_value(pr.get(names["subject"])) or "").strip(),
            "delay": prop_value(pr.get(names["delay"])),
            "status": prop_value(pr.get(names["status"])),
            "files": prop_value(pr.get(names["attachments"])) or [],
            "body": body,
        })
    return sorted(steps, key=lambda s: (s["n"] is None, s["n"] or 0))


def check_steps(steps, check_delays=True):
    """Pure function: list of (level, message). Kept separate from the I/O so it can be tested."""
    f = []
    if not steps:
        return [("FIX", "the wave has no template steps")]
    nums = [s["n"] for s in steps]
    if None in nums or nums != list(range(1, len(steps) + 1)):
        f.append(("FIX", f"step numbers should run 1..{len(steps)} with no gaps or repeats; found {nums}"))
    last = len(steps)
    if last > 5:
        f.append(("CHECK", f"{last} steps. 3–5 is the norm for investors; longer sequences mostly add spam risk"))

    thread_len = 0
    for i, s in enumerate(steps, 1):
        tag = f"step {s['n'] or i}"
        body = s["body"]
        if not body:
            f.append(("FIX", f"{tag}: empty email body"))
        # Threads (rules §2): a subject starts a new thread; about 3 emails per thread.
        if i == 1:
            if not s["subject"]:
                f.append(("FIX", f"{tag}: needs a subject (it opens the first thread)"))
            thread_len = 1
        elif s["subject"]:
            if thread_len < 3:
                f.append(("FIX", f"{tag}: new subject starts a new thread after only {thread_len} "
                                 f"email(s) in the last one. Clear it, or move the new thread to every third step"))
            thread_len = 1
        else:
            thread_len += 1
            if thread_len > 4:
                f.append(("CHECK", f"{tag}: {thread_len} emails in one thread; consider a new subject"))
        # Stop promise anywhere but the last step (rules §5).
        if i < last and STOP_PROMISE.search(body):
            f.append(("FIX", f"{tag}: promises to stop following up, but {last - i} more email(s) follow. "
                             f"Keep that line in step {last} only"))
        # Attachments (rules §7).
        if s["files"]:
            # CHECK, not FIX: the file itself does no harm (the feeder ignores it); the harm is
            # copy that promises it, caught by the FIX below.
            f.append(("CHECK", f"{tag}: has a file attached ({', '.join(s['files'])}). The cold lane sends "
                               f"no attachments, so the recipient won't get it"))
        if ATTACH_PROMISE.search(body):
            f.append(("FIX", f"{tag}: the text says something is attached. Cold emails carry none; "
                             f"offer it instead (\"happy to send the one-pager\")"))
        elif ATTACH_WORD.search(body):
            f.append(("CHECK", f"{tag}: mentions an attachment; make sure it doesn't promise one"))
        links = LINK.findall(body)
        for url in links:
            if FILE_SHARE.search(url):
                f.append(("FIX", f"{tag}: links to a file-sharing or short-link host ({url[:60]}). From a stranger "
                                 f"that reads as phishing; link a page on the client's own site, or offer it on reply"))
        if links and i == 1:
            # Ratified for the first client's scope (June 2026): the deck link "rides a later email
            # touch, never touch 1". Rules §8.
            f.append(("FIX", f"{tag}: has a link. The first email carries none: offer the material and send it "
                             f"on reply, or move the link to step 2 or later"))
        elif any(not FILE_SHARE.search(u) for u in links):
            f.append(("CHECK", f"{tag}: contains a link. Fine after step 1 if it points to the client's own website"))
        for tok in TOKEN.findall(body + " " + s["subject"]):
            if tok == "signature":
                f.append(("CHECK", f"{tag}: {{{{signature}}}} renders as nothing on the cold lane; "
                                   f"the mailbox adds its own signature. Harmless, but remove it"))
            elif tok not in ALLOWED_TOKENS:
                f.append(("FIX", f"{tag}: {{{{{tok}}}}} isn't a field the sender fills; it renders as nothing"))
        if check_delays and i < last and not s["delay"]:
            f.append(("FIX", f"{tag}: wait before the next step is {s['delay']!r}; it must be at least 1 day"))
        if s["status"] and s["status"] != "Active":
            f.append(("CHECK", f"{tag}: status is {s['status']}, so it is not approved yet"))
    return f


def check_senders(accounts, attached):
    """accounts: SmartLead email-account objects. attached: True when these are the campaign's
    actual senders (FIX), False when they are only the pool a push may draw from (CHECK)."""
    f, level = [], ("FIX" if attached else "CHECK")
    where = "is a sender on this campaign" if attached else "is in the mailbox pool a push can use"
    for a in accounts:
        name = (a.get("from_name") or "").strip()
        sig = re.sub(r"<[^>]+>|&nbsp;|\s", "", a.get("signature") or "")
        problems = []
        if not name or NON_PERSONAL.search(name) or len(name.split()) < 2:
            problems.append(f"name \"{name or '(none)'}\" doesn't look like a real person")
        if not sig:
            problems.append("no signature")
        if problems:
            f.append((level, f"mailbox {a.get('from_email')} {where}: {'; '.join(problems)}"))
    return f


def smartlead_steps(slug, campaign_id):
    """The sequence as SmartLead holds it. It can differ from Notion: an edit made directly in
    SmartLead never reaches the templates (seen on the first client, 19 Oct 2026)."""
    k = fe.key(slug, "smartlead")
    code, seq = fe.http("GET", f"https://server.smartlead.ai/api/v1/campaigns/{campaign_id}/sequences?api_key={k}",
                        {"User-Agent": "Mozilla/5.0"})
    if code != 200 or not isinstance(seq, list):
        return []
    out = []
    for q in sorted(seq, key=lambda x: x.get("seq_number") or 0):
        html = q.get("email_body") or ""
        hrefs = " ".join(f"<{h}>" for h in re.findall(r'href="([^"]+)"', html))
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|&nbsp;", " ", html)).strip()
        out.append({"id": q.get("id"), "n": q.get("seq_number"), "subject": (q.get("subject") or "").strip(),
                    "delay": (q.get("seq_delay_details") or {}).get("delay_in_days"), "status": "Active",
                    "files": [], "body": f"{text} {hrefs}".strip()})
    return out


def smartlead_senders(slug, campaign_id):
    k = fe.key(slug, "smartlead")
    base = "https://server.smartlead.ai/api/v1"
    # SmartLead sits behind Cloudflare, which refuses default client user agents (1010).
    ua = {"User-Agent": "Mozilla/5.0"}
    code, allacc = fe.http("GET", f"{base}/email-accounts/?offset=0&limit=100&api_key={k}", ua)
    allacc = allacc if isinstance(allacc, list) else (allacc or {}).get("data", []) if isinstance(allacc, dict) else []
    if not campaign_id:
        return allacc, False
    code, camp = fe.http("GET", f"{base}/campaigns/{campaign_id}/email-accounts?api_key={k}", ua)
    if code != 200 or not isinstance(camp, list):
        sys.exit(f"Can't read the senders of SmartLead campaign {campaign_id} (HTTP {code}).")
    ids = {c.get("id") for c in camp}
    # The campaign list lacks signatures; join to the full account objects.
    return [a for a in allacc if a.get("id") in ids] or camp, True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("wave")
    ap.add_argument("--client")
    ap.add_argument("--smartlead", help="SmartLead campaign id, once the wave has been pushed")
    a = ap.parse_args()
    cfg = fe.load_client(a.client)
    names = {**DEFAULTS, **cfg.get("templates", {})}
    steps = load_steps(cfg["slug"], a.wave.replace("-", ""), names)
    findings = check_steps(steps)
    if fe.has_key(cfg["slug"], "smartlead"):
        accounts, attached = smartlead_senders(cfg["slug"], a.smartlead)
        findings += check_senders(accounts, attached)
        if a.smartlead:
            live = smartlead_steps(cfg["slug"], a.smartlead)
            # SmartLead stores the wait BEFORE a step (step 1 = 0), Notion the wait AFTER it, so the
            # delay rule only applies to the Notion copy.
            # Report only what the live copy adds over the Notion copy, so a fix made in one place
            # but not the other shows up instead of hiding behind a duplicate line.
            have = {m for _, m in findings}
            findings += [(lv, "in SmartLead: " + m) for lv, m in check_steps(live, check_delays=False) if m not in have]
    else:
        findings.append(("CHECK", "no SmartLead key configured, so the senders were not checked"))
    subjects = " | ".join(f"{s['n']}: {s['subject'] or '(reply)'}" for s in steps)
    print(f"{len(steps)} steps. Subjects: {subjects}")
    for level, msg in findings:
        print(f"{level:5}  {msg}")
    fixes = sum(1 for lv, _ in findings if lv == "FIX")
    print(f"{fixes} to fix, {len(findings) - fixes} to check." if findings else "Nothing to fix.")
    sys.exit(1 if fixes else 0)
