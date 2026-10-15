#!/usr/bin/env python3
"""Run the email workers' DRY RUNS from the operator's Mac.

Usage:
  python3 workers.py preview-drafts --client <slug> <wave_page_id>   # warm lane: what drafting would do
  python3 workers.py preview-feed   --client <slug> <wave_page_id>   # cold lane: what a Push would send

Why this exists (Krystof, 15 Oct 2026: "Why couldn't her ChatGPT call preview draft and preview
feed?"): the dry runs are Notion Worker tools. Until now only the client's Notion agent or
Krystof's `ntn workers exec` could call them. With Notion's CLI (`ntn`) installed on her Mac and
logged in with her own Notion account, her ChatGPT can run them directly and read the answer,
instead of asking her to relay it from the Notion agent.

Only the two previews are exposed here, on purpose. They change nothing. The arming tools
(pushToSmartLead, draftNow, appendLeads) stay buttons she presses in Notion; the approval-gate
hook also blocks them in the terminal without "approve send", and blocks deploy/delete/env
outright (that's build work).

The worker IDs come from the client config: "workers": {"email-drafter": "...", "smartlead-feeder": "..."}.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import fe

TOOLS = {"preview-drafts": ("email-drafter", "previewDrafts"),
         "preview-feed": ("smartlead-feeder", "previewFeed")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=sorted(TOOLS))
    ap.add_argument("wave_page_id")
    ap.add_argument("--client")
    a = ap.parse_args()
    cfg = fe.load_client(a.client)
    worker, tool = TOOLS[a.mode]
    wid = (cfg.get("workers") or {}).get(worker)
    if not wid:
        sys.exit(f"No worker id for '{worker}' in the client config. Run the `setup` skill.")
    ws = cfg.get("notion_workspace_id")
    if not ws:
        sys.exit("No notion_workspace_id in the client config. Run the `setup` skill.")
    # `ntn workers exec --worker-id` alone resolves against the CLI's default workspace and
    # answers 404 WorkerNotFound for a worker in another workspace (seen 15 Oct 2026). A
    # workers.json naming the workspace makes the call land in the right one.
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"version": "1", "environment": "prod", "workspaceId": ws, "workerId": wid}, f)
    r = subprocess.run(["ntn", "workers", "exec", tool, "--workers-config-file", f.name,
                        "-d", json.dumps({"campaignPageId": a.wave_page_id})],
                       capture_output=True, text=True)
    os.unlink(f.name)
    out = (r.stdout + r.stderr).strip()
    # A refusal from the tool IS the dry-run answer (e.g. "2 steps are not Active and will not
    # be pushed"), so print it as the result. Only auth problems point at `ntn login`.
    first = out.split("\n    at ")[0]
    print(first if r.returncode == 0 else f"{tool} answered: {first}")
    if r.returncode != 0 and any(s in out.lower() for s in ("unauthor", "not logged", "login", "401")):
        print("Looks like the Notion CLI isn't logged in to this workspace: run `ntn login` (see `setup`).")


if __name__ == "__main__":
    main()
