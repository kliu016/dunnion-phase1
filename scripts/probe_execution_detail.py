"""Fetch the detail log for the newest Make execution and show its structure (read-only).

Saves the raw response to data/raw/probe_detail.json. Prints only the key tree
(no values) and which key paths mention output/bundle/response/data/body.
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

from export_make_logs import redact

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
LOGS_FILE = RAW_DIR / "make_logs_all.json"
OUT_FILE = RAW_DIR / "probe_detail.json"
TERMS = ("output", "bundle", "response", "data", "body")


def key_paths(node, prefix=""):
    """Yield every nested key path. List items are merged under "[]"."""
    if isinstance(node, dict):
        for k, v in node.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            yield path
            yield from key_paths(v, path)
    elif isinstance(node, list):
        path = f"{prefix}[]"
        seen = set()
        for item in node:
            for p in key_paths(item, path):
                if p not in seen:
                    seen.add(p)
                    yield p


def main():
    load_dotenv(ROOT / ".env")
    token = os.getenv("MAKE_TOKEN", "").strip()
    base = os.getenv("MAKE_BASE", "").strip().rstrip("/")
    scenario_id = os.getenv("SCENARIO_ID", "").strip()

    if not token:
        sys.exit("MAKE_TOKEN is empty. Set it in .env before running this probe.")
    if not base or not scenario_id:
        sys.exit("MAKE_BASE and SCENARIO_ID must be set in .env.")
    if not LOGS_FILE.exists():
        sys.exit(f"{LOGS_FILE.relative_to(ROOT)} not found. Run export_make_logs.py first.")

    entries = [e for e in json.loads(LOGS_FILE.read_text()) if isinstance(e, dict)]
    entries = [e for e in entries if e.get("id") and e.get("timestamp")]
    if not entries:
        sys.exit("No entries with both id and timestamp in make_logs_all.json.")
    newest = max(entries, key=lambda e: str(e["timestamp"]))
    execution_id = newest["id"]
    print(f"Newest execution: {execution_id} ({newest['timestamp']})")

    url = f"{base}/scenarios/{scenario_id}/logs/{execution_id}"
    resp = requests.get(url, headers={"Authorization": f"Token {token}"}, timeout=60)
    if resp.status_code != 200:
        print(f"HTTP {resp.status_code}")
        print(redact(resp.text, [token]))
        sys.exit(1)

    payload = resp.json()
    OUT_FILE.write_text(json.dumps(payload, indent=2))

    paths = list(key_paths(payload))
    print("Key tree:")
    for p in paths:
        depth = p.count(".") + p.count("[]")
        print(f"  {'  ' * depth}{p}")

    print("Key paths matching terms:")
    for term in TERMS:
        hits = [p for p in paths if term in p.lower()]
        print(f"  {term}: {'yes' if hits else 'no'}")
        for p in hits:
            print(f"    {p}")


if __name__ == "__main__":
    main()
