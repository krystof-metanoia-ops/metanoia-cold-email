"""Shared helpers for the fundraising-engine skills: client config, Keychain keys, HTTP.

Design notes (Metanoia Ops, 2026-10-15):
- One operator can serve several clients (e.g. one person runs two clients' raises), so every
  config file and every Keychain item is namespaced by a short client slug.
- Keys live ONLY in the macOS Keychain (Krystof's call, 15 Oct), service name
  "fundraising-engine.<client>.<tool>". Nothing here prints a key; callers must not either.
- HTTP goes through the system `curl`, not urllib: the python.org builds on macOS ship
  without CA certificates, so urllib fails with CERTIFICATE_VERIFY_FAILED on a fresh Mac
  (seen on Krystof's machine). curl uses the system trust store.
- Client config lives in ~/.fundraising-engine/<client>.json, written by the setup skill.
  It holds IDs and domains only — never secrets.
"""
import json
import os
import subprocess
import sys

CONFIG_DIR = os.path.expanduser("~/.fundraising-engine")
TOOLS = ("smartlead", "millionverifier", "bounceban", "notion")


def clients():
    """Slugs of every configured client."""
    if not os.path.isdir(CONFIG_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(CONFIG_DIR) if f.endswith(".json"))


def load_client(slug=None):
    """Return the client's config dict. With one client configured, the slug is optional."""
    have = clients()
    if not have:
        sys.exit("No client is configured yet. Run the `setup` skill first.")
    if slug is None:
        if len(have) > 1:
            sys.exit(f"Several clients are configured ({', '.join(have)}). Pass --client <slug>.")
        slug = have[0]
    path = os.path.join(CONFIG_DIR, slug + ".json")
    if not os.path.exists(path):
        sys.exit(f"No config for client '{slug}'. Configured: {', '.join(have) or 'none'}.")
    cfg = json.load(open(path))
    cfg["slug"] = slug
    return cfg


def key(client_slug, tool):
    """Read one API key from the Keychain. macOS may ask the operator to allow it — that
    prompt is deliberate (setup stores the items so each read needs her confirmation)."""
    service = f"fundraising-engine.{client_slug}.{tool}"
    r = subprocess.run(["security", "find-generic-password", "-s", service, "-w"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit(f"No Keychain item '{service}'. Run the `setup` skill to add the {tool} key.")
    return r.stdout.strip()


def has_key(client_slug, tool):
    r = subprocess.run(["security", "find-generic-password", "-s",
                        f"fundraising-engine.{client_slug}.{tool}"], capture_output=True, text=True)
    return r.returncode == 0


def http(method, url, headers=None, body=None, timeout=60):
    """Return (status_code, parsed_json_or_text). Never raises on HTTP errors: callers
    decide what a 401/429 means. The URL may contain a key, so it is never logged."""
    args = ["curl", "-s", "-X", method, "--max-time", str(timeout), "-w", "\n%{http_code}", url]
    for k, v in (headers or {}).items():
        args += ["-H", f"{k}: {v}"]
    if body is not None:
        args += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = subprocess.run(args, capture_output=True, text=True).stdout
    text, _, code = out.rpartition("\n")
    try:
        return int(code), json.loads(text)
    except (ValueError, json.JSONDecodeError):
        return int(code or 0), text


def notion(client_slug, method, path, body=None):
    """Notion REST call with the client's optional integration key (Notion-Version 2025-09-03,
    the data-sources API the workers use)."""
    tok = key(client_slug, "notion")
    return http(method, "https://api.notion.com/v1" + path,
                {"Authorization": f"Bearer {tok}", "Notion-Version": "2025-09-03"}, body)
