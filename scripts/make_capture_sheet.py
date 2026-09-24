"""Build a blank outcome-capture sheet from the exported Make logs.

Writes data/raw/make_outcomes.csv: one row per execution, oldest first, with
only id and timestamp filled in. Prints only the row count.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
LOGS_FILE = RAW_DIR / "make_logs_all.json"
OUT_FILE = RAW_DIR / "make_outcomes.csv"
COLUMNS = ["id", "timestamp", "route", "success", "opportunityId", "message", "notes"]


def main():
    entries = [e for e in json.loads(LOGS_FILE.read_text()) if isinstance(e, dict)]
    entries.sort(key=lambda e: str(e.get("timestamp", "")))

    with OUT_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for e in entries:
            writer.writerow({"id": e.get("id", ""), "timestamp": e.get("timestamp", "")})

    print(f"Rows: {len(entries)}")


if __name__ == "__main__":
    main()
