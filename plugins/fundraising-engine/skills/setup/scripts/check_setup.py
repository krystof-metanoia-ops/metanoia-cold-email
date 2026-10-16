#!/usr/bin/env python3
"""Setup checklist: what's done on this Mac and what's still missing. Read-only and free.

Usage: python3 check_setup.py [--client <slug>]

Why (the Metanoia consultant, 16 Oct 2026: "the commands and placeholders and steps should be
there, so the agent can just guide any user through the setup"): on the first real install the
operator's ChatGPT had no way to tell which steps were done. This prints one line per step, in
order, so the agent starts at the first MISSING one and never redoes a finished step.
It never prints a key; it only checks that one exists.
"""
import argparse
import json
import os
import shutil
import subprocess

STEPS = []


def step(name, ok, how):
    STEPS.append((name, ok, how))


def run(*a):
    try:
        return subprocess.run(a, capture_output=True, text=True, timeout=20)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client")
    a = ap.parse_args()
    cdir = os.path.expanduser("~/.fundraising-engine")
    have = sorted(f[:-5] for f in os.listdir(cdir) if f.endswith(".json")) if os.path.isdir(cdir) else []
    slug = a.client or (have[0] if len(have) == 1 else None)

    cfg_ok, cfg = False, {}
    if slug and os.path.exists(f"{cdir}/{slug}.json"):
        cfg = json.load(open(f"{cdir}/{slug}.json"))
        placeholders = [k for k, v in cfg.items() if isinstance(v, str) and v.startswith("<")]
        cfg_ok = not placeholders and bool(cfg.get("notion_workspace_id")) and bool(cfg.get("workers"))
    step("1. Client config", cfg_ok,
         f"Copy setup/client.example.json to ~/.fundraising-engine/<slug>.json and fill every <...> "
         f"(values: the client's context page, or the Metanoia consultant). Configured: {have or 'none'}")

    for tool in ("smartlead", "millionverifier", "bounceban"):
        r = run("security", "find-generic-password", "-s", f"fundraising-engine.{slug}.{tool}") if slug else None
        step(f"2. {tool} key in Keychain", bool(r and r.returncode == 0),
             f"Create a new key in {tool}, then run setup/scripts/setup_keys.sh <slug> in the Terminal APP")
    r = run("security", "find-generic-password", "-s", f"fundraising-engine.{slug}.notion") if slug else None
    step("2. notion key (optional, bulk writes)", bool(r and r.returncode == 0), "Optional; see setup §2 step 4")

    ntn = shutil.which("ntn") or os.path.expanduser("~/.local/bin/ntn")
    has_ntn = os.path.exists(ntn)
    step("3. Notion CLI installed", has_ntn, "curl -fsSL https://ntn.dev | bash")
    r = run(ntn, "whoami") if has_ntn else None
    # whoami prints tab-separated fields; the workspace NAME is the 6th. Show it, because the
    # CLI's default workspace must be the client's or the dry runs answer "worker not found".
    ws = (r.stdout.strip().split("\t")[5] if r and r.returncode == 0 and r.stdout.count("\t") >= 5 else "")
    step(f"3. Notion CLI logged in{' (workspace: ' + ws + ' — must be the client' + chr(39) + 's)' if ws else ''}",
         bool(ws), "ntn login  (sign in, pick the client's workspace)")

    # Dry runs from the CLI need the workers to be visible to THIS account. Workers are private
    # to their deployer until shared in the Developer portal (16 Oct 2026). Not a blocker: the
    # Notion agent can run them meanwhile.
    if has_ntn and cfg.get("workers"):
        lst = run(ntn, "workers", "list")
        seen = bool(lst and any(w in (lst.stdout or "") for w in cfg["workers"].values()))
        step("3. Dry runs from this Mac (optional)", seen,
             "The workers aren't shared with this account yet. Ask the Metanoia consultant to share "
             "email-drafter and smartlead-feeder with you (notion.so/developers/workers -> Share -> "
             "Can connect). Until then, dry runs go through the Notion agent.")
    gh = shutil.which("gh")
    r = run(gh, "auth", "status") if gh else None
    step("4. GitHub CLI logged in (for feedback only)", bool(r and r.returncode == 0),
         "brew install gh (or cli.github.com), then gh auth login")

    first = next((s for s in STEPS if not s[1] and "optional" not in s[0]), None)
    for name, ok, how in STEPS:
        print(f"{'DONE   ' if ok else 'MISSING'} {name}" + ("" if ok else f"  ->  {how}"))
    print("\nNext: " + (first[0] if first else "all set — run the health check (fundraising-system/scripts/check_health.py) and the Keychain-prompt test."))


if __name__ == "__main__":
    main()
