---
title: 'Seed loader'
type: 'feature'
created: '2026-09-26'
status: 'in-progress'
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

