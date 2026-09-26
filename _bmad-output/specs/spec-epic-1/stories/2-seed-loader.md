---
title: 'Seed loader'
type: 'feature'
created: '2026-09-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `mcp/triage_server.py` already reads `app.db`, but nothing loads the seed CSVs into that file yet.

**Approach:** Add `load_seed.py` so `uv run python load_seed.py` loads `seed/tickets.csv` and `seed/customers.csv` into `app.db` tables `tickets` and `customers` with the same columns, without modifying `seed/`. A second run leaves both tables identical to the first.

</frozen-after-approval>

## Implementation Notes

- Added `load_seed.py` with `load_seed()` and a `__main__` entry point.
- DROP + CREATE + INSERT makes reloads idempotent and keeps MCP column names.
- CSV headers are checked against `TICKETS_COLUMNS` / `CUSTOMERS_COLUMNS` before insert.
- `seed/` is read-only; tests assert file bytes are unchanged.
- `pythonpath = ["."]` added under `[tool.pytest.ini_options]` so tests import project modules.
- Verified MCP-shaped queries for `T-1042` / `C-77` against a fresh `app.db`.

## Review Triage Log

- Blind Hunter (self-pass): missing CSV header check would yield a KeyError — **patch**; headers are validated before insert.
- Blind Hunter: DROP TABLE wipes non-seed data in `app.db` — **false** for this workshop story; the success criterion requires the DB to match the seed CSVs after each run.
- Blind Hunter: hard-coded row counts in tests — **low**; rejected (seed files are repo fixtures; counts document the expected load).
