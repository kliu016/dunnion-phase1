# Dunnion lead pipeline — Phase 1

Read-only investigation tooling for the Dunnion lead pipeline (Make → CallRail → Lead Docket).
See `CLAUDE.md` for the data-handling rules.

## Layout

- `scripts/` — export and analysis scripts
- `data/raw/` — raw API exports. Contains client PII; git-ignored.
- `fixtures/` — synthetic sample data (fake names, 555 numbers), safe to share
- `out/` — generated reports; git-ignored

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # then fill in MAKE_TOKEN
```

## Export Make scenario logs

```sh
.venv/bin/python scripts/export_make_logs.py
```

Pages through `GET {MAKE_BASE}/scenarios/{SCENARIO_ID}/logs` (read-only), writes each page to
`data/raw/make_logs_{offset}.json` and the merged list to `data/raw/make_logs_all.json`, and prints
only the total count, oldest/newest timestamp, and a count by status.
