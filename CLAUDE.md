# Dunnion lead-pipeline remediation — standing rules

- This repo handles a law firm's lead data. Files in `data/` contain client PII: names, phones, emails, injury details.
- Never print, echo, or summarize PII from `data/`. When inspecting real data, show only keys and structure, counts, date ranges, and status values.
- `fixtures/` holds synthetic data only, with fake names and 555 phone numbers. Anything a collaborator sees comes from `fixtures/`, never `data/`.
- Never print or log tokens. Read credentials only from `.env`.
- Everything against Make, CallRail, and Lead Docket is read-only unless I explicitly say otherwise. Never modify the live Make scenario (ID 4844089).
- On any non-200 API response, print the status and body (with secrets redacted) and stop. No silent retries.
