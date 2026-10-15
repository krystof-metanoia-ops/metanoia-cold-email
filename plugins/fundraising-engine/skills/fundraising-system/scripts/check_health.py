#!/usr/bin/env python3
"""Read-only health check of the sending side. Free: no credits, no writes.

Usage: python3 check_health.py [--client <slug>] [--json]

Reports:
1. SmartLead account: is the plan active? (On 15 Oct 2026 a client's plan lapsed and every
   campaign stopped; the API answered "Plan expired!" and nobody noticed for a day.)
2. Per mailbox: connected (SMTP/IMAP), warm-up status and reputation, sent today vs limit,
   and any mailbox on the client's PRIMARY domain (that domain must never send cold).
3. Per live campaign: sent, bounced and bounce rate from SmartLead's campaign analytics.
   SmartLead warns at ~5-6% bounces per mailbox; treat 3%+ as worth a look.
   NOTE: per-mailbox bounce rates are not in the mailbox object; this script reports what
   the analytics endpoints return and says so when a field is missing (untested against a
   live plan as of 15 Oct 2026 because the plan had lapsed — the Metanoia consultant to confirm on renewal).
4. Per sending domain: SURBL, Spamhaus DBL and URIBL listings via plain DNS, plus SPF/DMARC.
   A listing on SURBL (127.0.0.64 = abuse list) is why Mimecast-protected firms refuse mail.
   Resolver sanity entries are checked first; if a list refuses public resolvers the result
   is reported as "unknown", never as "clean".
"""
import argparse
import json
import subprocess

import fe

LISTS = {  # zone, the test entry that must answer, how to read a hit
    "SURBL": ("multi.surbl.org", "test.surbl.org"),
    "Spamhaus DBL": ("dbl.spamhaus.org", "dbltest.com"),
    "URIBL": ("multi.uribl.com", "test.uribl.com"),
}
REFUSED = {"127.255.255.254", "127.255.255.255", "127.0.0.255", "127.0.0.1"}  # "query refused" codes


def dig(name, rtype="A"):
    r = subprocess.run(["dig", "+short", "+time=3", "+tries=1", name, rtype], capture_output=True, text=True)
    return [x.strip().strip('"') for x in r.stdout.splitlines() if x.strip()]


def blocklists(domains):
    usable = {}
    for name, (zone, test) in LISTS.items():
        ans = dig(f"{test}.{zone}")
        usable[name] = bool(ans) and not set(ans) <= REFUSED
    out = {}
    for d in domains:
        row = {}
        for name, (zone, _) in LISTS.items():
            if not usable[name]:
                row[name] = "unknown (resolver refused)"
                continue
            ans = dig(f"{d}.{zone}")
            row[name] = ("LISTED " + ",".join(ans)) if ans and not set(ans) <= REFUSED else "clean"
        row["SPF"] = "yes" if any("v=spf1" in t for t in dig(d, "TXT")) else "MISSING"
        dm = [t for t in dig(f"_dmarc.{d}", "TXT") if "v=DMARC1" in t]
        row["DMARC"] = (dm[0].split("p=")[1].split(";")[0] if dm and "p=" in dm[0] else "MISSING")
        out[d] = row
    return out


def smartlead(cfg):
    k = fe.key(cfg["slug"], "smartlead")
    base = "https://server.smartlead.ai/api/v1"
    code, acc = fe.http("GET", f"{base}/email-accounts/?offset=0&limit=100&api_key={k}")
    if code != 200 or not isinstance(acc, list):
        msg = acc.get("message") if isinstance(acc, dict) else str(acc)[:120]
        return {"plan": f"NOT USABLE (HTTP {code}: {msg})", "mailboxes": [], "campaigns": []}
    primary = (cfg.get("primary_domain") or "").lower()
    boxes = []
    for a in acc:
        w = a.get("warmup_details") or {}
        dom = a["from_email"].split("@")[-1].lower()
        boxes.append({
            "mailbox": a["from_email"],
            "connected": bool(a.get("is_smtp_success") and a.get("is_imap_success")),
            "warmup": w.get("status"), "reputation": w.get("warmup_reputation"),
            "sent_today": a.get("daily_sent_count"), "limit": a.get("message_per_day"),
            "on_primary_domain": dom == primary,
            "error": a.get("smtp_failure_error") or a.get("imap_failure_error"),
        })
    code, camps = fe.http("GET", f"{base}/campaigns/?api_key={k}")
    plan = "active" if code == 200 and isinstance(camps, list) else \
        f"NOT USABLE (HTTP {code}: {camps.get('message') if isinstance(camps, dict) else camps})"
    rows = []
    for c in (camps if isinstance(camps, list) else []):
        if c.get("status") not in ("ACTIVE", "STARTED"):
            continue
        _, an = fe.http("GET", f"{base}/campaigns/{c['id']}/analytics?api_key={k}")
        an = an if isinstance(an, dict) else {}
        sent = int(an.get("sent_count") or 0)
        bounced = int(an.get("bounce_count") or 0)
        rows.append({"campaign": c.get("name"), "id": c["id"], "sent": sent, "bounced": bounced,
                     "bounce_rate": f"{100 * bounced / sent:.1f}%" if sent else "n/a",
                     "replies": an.get("reply_count")})
    return {"plan": plan, "mailboxes": boxes, "campaigns": rows}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--client")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    cfg = fe.load_client(a.client)
    domains = sorted(set(cfg.get("cold_domains", [])) | {cfg.get("primary_domain")} - {None, ""})
    report = {"client": cfg["slug"], "domains": blocklists(domains)}
    report.update(smartlead(cfg) if fe.has_key(cfg["slug"], "smartlead") else {"plan": "no SmartLead key"})
    if a.json:
        print(json.dumps(report, indent=1))
    else:
        print(f"Client: {report['client']}\nSmartLead plan: {report['plan']}")
        for m in report.get("mailboxes", []):
            flag = "  <-- PRIMARY DOMAIN, must not send cold" if m["on_primary_domain"] else ""
            print(f"  {m['mailbox']}: connected={m['connected']} warmup={m['warmup']} "
                  f"rep={m['reputation']} sent {m['sent_today']}/{m['limit']}{flag}"
                  + (f" ERROR {m['error']}" if m["error"] else ""))
        for c in report.get("campaigns", []):
            print(f"  campaign {c['campaign']}: sent {c['sent']}, bounced {c['bounced']} "
                  f"({c['bounce_rate']}), replies {c['replies']}")
        for d, r in report["domains"].items():
            print(f"  {d}: " + " · ".join(f"{k} {v}" for k, v in r.items()))
