#!/usr/bin/env python3
"""Segment a roster by the recipient's mail gateway (MX), before a wave is armed.

Why: the cold-outreach playbook says to fingerprint secure email gateways by MX
and hold them back from young or listed sending domains. We did not, and on
2026-09-20 measured the cost: Mimecast recipients bounced 67% while everyone
else bounced 1.8%, and Microsoft 365 recipients replied at 0.9% against 18%
for Google-hosted ones. (Measured on a 2026 client build.)

Usage:
  python3 mx_check.py < emails.txt            # one address per line
  python3 mx_check.py --tsv out.tsv < emails.txt
Free (plain DNS), read-only, no API keys. Needs `dig`.
"""
import sys, subprocess, collections, concurrent.futures as cf, argparse

SEG = {"Mimecast", "Proofpoint", "Cisco IronPort"}  # hold these while cold domains are young or listed

def gateway(mx: str) -> str:
    m = mx.lower()
    if "mimecast" in m: return "Mimecast"
    if "pphosted" in m or "proofpoint" in m: return "Proofpoint"
    if "iphmx" in m: return "Cisco IronPort"
    if "protection.outlook" in m or "outlook.com" in m: return "Microsoft 365"
    if "google" in m: return "Google"
    if "barracuda" in m: return "Barracuda"
    return "other" if m.strip() else "no MX"

def mx_of(domain: str) -> str:
    out = subprocess.run(["dig", "+short", "+time=2", "+tries=1", domain, "MX"],
                         capture_output=True, text=True).stdout
    return " ".join(l.split()[-1] for l in out.splitlines() if l.strip())

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tsv"); a = ap.parse_args()
    emails = [l.strip().lower() for l in sys.stdin if "@" in l]
    domains = sorted({e.split("@")[1] for e in emails})
    with cf.ThreadPoolExecutor(40) as ex:
        gw = dict(zip(domains, (gateway(m) for m in ex.map(mx_of, domains))))
    rows = [(e, e.split("@")[1], gw[e.split("@")[1]]) for e in emails]
    if a.tsv:
        with open(a.tsv, "w") as f:
            f.write("email\tdomain\tgateway\thold\n")
            for e, d, g in rows: f.write(f"{e}\t{d}\t{g}\t{'yes' if g in SEG else ''}\n")
    c = collections.Counter(g for _, _, g in rows); n = len(rows) or 1
    print(f"{len(rows)} addresses, {len(domains)} domains")
    for g, k in c.most_common():
        print(f"  {g:<16}{k:>6}  {100*k/n:5.1f}%{'   <- hold (secure gateway)' if g in SEG else ''}")

if __name__ == "__main__":
    main()
