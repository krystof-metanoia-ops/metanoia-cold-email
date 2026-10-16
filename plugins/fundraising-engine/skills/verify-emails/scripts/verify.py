#!/usr/bin/env python3
"""Email verification ladder: MillionVerifier first, BounceBan for what MV can't resolve.

Usage:
  python3 verify.py preview --client <slug> emails.csv     # free: counts + credit estimate, no API calls
  python3 verify.py run     --client <slug> emails.csv     # SPENDS credits (approval gate applies)
  python3 verify.py writeback --client <slug> results.csv  # Notion writes, needs the notion key
  python3 verify.py preview|run --bb-only ...              # skip MillionVerifier: for contacts it
                                                           # already marked Catch-all / Unknown

emails.csv needs columns `email` and `page_id` (the Notion contact row); extra columns are kept.

The ladder and the label mapping are the ones used on the first client build since Sep 2026:
  MV ok                                   -> Valid
  MV invalid / disposable                 -> Invalid
  MV catch_all / unknown / error          -> ask BounceBan
     BB deliverable                       -> Valid
     BB undeliverable                     -> Invalid
     BB risky / unknown / error           -> Unverifiable
Only Valid is sendable. Never set Valid by hand: it is machine-owned evidence, and a wrong
Valid invites a hard bounce that damages the sending domain.

Credit estimate: MillionVerifier ~1 credit per address; BounceBan ~1 credit per address it
checks. On the Sep 2026 runs roughly 30-40% of addresses went on to BounceBan, so the
preview quotes MV = N and BB = up to N (worst case) with a typical 35%.

Writes results to <input>.results.csv next to the input, resumable: addresses already in the
results file are skipped, so a re-run after an interruption never pays twice.
"""
import argparse
import csv
import os
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "fundraising-system", "scripts"))
import fe  # noqa: E402

LABEL_MV = {"ok": "Valid", "invalid": "Invalid", "disposable": "Invalid"}
LABEL_BB = {"deliverable": "Valid", "undeliverable": "Invalid"}
BB_ONLY = False  # set from --bb-only in __main__


def read_rows(path):
    rows = list(csv.DictReader(open(path)))
    if not rows or "email" not in rows[0]:
        sys.exit("The CSV needs an `email` column (and `page_id` for writeback).")
    seen, out = set(), []
    for r in rows:
        e = (r.get("email") or "").strip().lower()
        if e and e not in seen:
            seen.add(e)
            r["email"] = e
            out.append(r)
    return out


def mv(email, k):
    code, d = fe.http("GET", "https://api.millionverifier.com/api/v3/?api=" + k +
                      "&email=" + urllib.parse.quote(email) + "&timeout=20", timeout=40)
    return (d.get("result") if isinstance(d, dict) else None) or f"error_{code}"


def bb(email, k):
    code, d = fe.http("GET", "https://api.bounceban.com/v1/verify/single?email=" + urllib.parse.quote(email),
                      {"Authorization": "Bearer " + k, "Accept": "application/json"}, timeout=60)
    return (d.get("result") if isinstance(d, dict) else None) or f"error_{code}"


def run(cfg, path):
    rows = read_rows(path)
    out_path = path.rsplit(".", 1)[0] + ".results.csv"
    done = {r["email"] for r in csv.DictReader(open(out_path))} if os.path.exists(out_path) else set()
    todo = [r for r in rows if r["email"] not in done]
    kmv = None if BB_ONLY else fe.key(cfg["slug"], "millionverifier")
    kbb = fe.key(cfg["slug"], "bounceban")
    fields = list(rows[0].keys()) + ["mv_result", "bb_result", "email_status"]
    new = not os.path.exists(out_path)
    fh = open(out_path, "a", newline="")
    w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
    if new:
        w.writeheader()

    def one(r):
        # --bb-only (the Metanoia consultant, 16 Oct 2026): ~490 contacts on the first client carry
        # Catch-all / Unknown from an earlier MillionVerifier-only pass. Re-running MV would pay
        # again for an answer we already have, so those go straight to BounceBan.
        m = "skipped" if BB_ONLY else mv(r["email"], kmv)
        b, label = "", (None if BB_ONLY else LABEL_MV.get(m))
        if label is None:
            b = bb(r["email"], kbb)
            label = LABEL_BB.get(b, "Unverifiable")
        return {**r, "mv_result": m, "bb_result": b, "email_status": label}

    counts = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(one, todo):
            w.writerow(res)
            counts[res["email_status"]] = counts.get(res["email_status"], 0) + 1
    fh.close()
    print(f"Verified {len(todo)} new addresses ({len(done)} were already done). "
          f"Results: {counts}. File: {out_path}")


def preview(path):
    rows = read_rows(path)
    n = len(rows)
    if BB_ONLY:
        print(f"{n} unique addresses. Estimated credits: BounceBan {n}; MillionVerifier 0 "
              f"(--bb-only). No API calls were made.")
        return
    print(f"{n} unique addresses. Estimated credits: MillionVerifier {n}; "
          f"BounceBan about {round(n * 0.35)} (up to {n} if MillionVerifier resolves none). "
          f"No API calls were made.")


def writeback(cfg, path):
    """Set Email Status on each contact. Valid is written only from this verification
    evidence; nothing else in the skills may set it."""
    rows = list(csv.DictReader(open(path)))
    ok = fail = 0
    for r in rows:
        pid, label = r.get("page_id"), r.get("email_status")
        if not pid or not label:
            continue
        code, _ = fe.notion(cfg["slug"], "PATCH", f"/pages/{pid}",
                            {"properties": {"Email Status": {"select": {"name": label}}}})
        ok, fail = (ok + 1, fail) if code == 200 else (ok, fail + 1)
    print(f"Email Status written on {ok} contacts; {fail} failed (re-run is safe).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preview", "run", "writeback"])
    ap.add_argument("csv")
    ap.add_argument("--client")
    ap.add_argument("--bb-only", action="store_true")
    a = ap.parse_args()
    BB_ONLY = a.bb_only  # module-level: this block runs at module scope
    if a.mode == "preview":
        preview(a.csv)
    else:
        cfg = fe.load_client(a.client)
        run(cfg, a.csv) if a.mode == "run" else writeback(cfg, a.csv)
