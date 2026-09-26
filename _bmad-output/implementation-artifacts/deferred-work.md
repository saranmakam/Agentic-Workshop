## Deferred from: code review of 1-triage-decision-schema.md (2026-09-26)

- Epic SPEC still asks whether route must match category. The story intent already says no pairing, and the code does not enforce one. Closing the question means editing `SPEC.md`.
- A failed insert after `DROP TABLE` in `load_seed.py` may wipe `app.db`. Unverified medium: the current seed loads cleanly. Settle it by forcing a failing insert (non-integer `open_tickets`, a duplicate id, or a missing column) and checking whether the previous database is gone.
