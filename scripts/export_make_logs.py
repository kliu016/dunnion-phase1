"""Export execution logs for the Make scenario to data/raw/ (read-only).

Prints only aggregate info: total count, oldest/newest timestamp, count by status.
Never prints log contents, which may contain client PII.
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PAGE_LIMIT = 100


def redact(text, secrets):
    for s in secrets:
        if s:
            text = text.replace(s, "[REDACTED]")
    return text


def extract_entries(payload):
    """Return the list of log entries from a page response."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("scenarioLogs"), list):
            return payload["scenarioLogs"]
        for value in payload.values():
            if isinstance(value, list):
                return value
    return []


def main():
    load_dotenv(ROOT / ".env")
    token = os.getenv("MAKE_TOKEN", "").strip()
    base = os.getenv("MAKE_BASE", "").strip().rstrip("/")
    scenario_id = os.getenv("SCENARIO_ID", "").strip()

    if not token:
        sys.exit("MAKE_TOKEN is empty. Set it in .env before running this export.")
    if not base or not scenario_id:
        sys.exit("MAKE_BASE and SCENARIO_ID must be set in .env.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    url = f"{base}/scenarios/{scenario_id}/logs"
    headers = {"Authorization": f"Token {token}"}

    all_entries = []
    offset = 0
    while True:
        params = {"pg[limit]": PAGE_LIMIT, "pg[offset]": offset}
        resp = requests.get(url, headers=headers, params=params, timeout=60)
        if resp.status_code != 200:
            print(f"HTTP {resp.status_code} at offset {offset}")
            print(redact(resp.text, [token]))
            sys.exit(1)

        payload = resp.json()
        entries = extract_entries(payload)
        if not entries:
            break

        (RAW_DIR / f"make_logs_{offset}.json").write_text(json.dumps(payload, indent=2))
        all_entries.extend(entries)
        offset += PAGE_LIMIT

    (RAW_DIR / "make_logs_all.json").write_text(json.dumps(all_entries, indent=2))

    timestamps = sorted(
        str(e["timestamp"]) for e in all_entries if isinstance(e, dict) and e.get("timestamp")
    )
    statuses = Counter(
        str(e.get("status")) if isinstance(e, dict) else "?" for e in all_entries
    )

    print(f"Total entries: {len(all_entries)}")
    print(f"Oldest: {timestamps[0] if timestamps else 'n/a'}")
    print(f"Newest: {timestamps[-1] if timestamps else 'n/a'}")
    print("By status:")
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()
