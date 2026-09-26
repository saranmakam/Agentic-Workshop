---
id: SPEC-epic-1
companions: []
sources: [../../../INTENT.md]
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Epic 1: triage data and schema

## Why

Later epics cannot run until a triage decision has one accepted shape and the seed data sits in the SQLite file `mcp/triage_server.py` already reads. Epic 1 is that mandate.

## Capabilities

- **CAP-1**
  - **intent:** A triage decision is accepted only when it is a JSON object with a category, a priority, a route, and a one-sentence rationale.
  - **success:** An object is accepted only with category one of `billing`, `bug`, `access`, `performance`, or `how-to`; priority one of `P1`, `P2`, `P3`, or `P4`; route one of `billing-team`, `bug-team`, `access-team`, `performance-team`, or `how-to-team`; and a rationale that is one sentence. A missing field, a value outside those sets, a rationale that is not one sentence, or any other shape is rejected with an error that states what is wrong.

- **CAP-2**
  - **intent:** A person can load the seed tickets and customers into a local database with one command, and loading again does not change the result.
  - **success:** `uv run python load_seed.py` loads `seed/tickets.csv` into `app.db` table `tickets` and `seed/customers.csv` into table `customers`, with the same columns as those files. Running the command a second time leaves both tables identical to the first run.

## Constraints

- Python 3.12 or newer, managed with uv.
- Files in `seed/` are read-only. The loader reads them and does not modify them.
- This epic makes no network calls and uses no API keys.
- `mcp/triage_server.py` already reads `app.db`. Table `tickets` keeps columns `ticket_id`, `customer_id`, `created_at`, `text`. Table `customers` keeps columns `customer_id`, `name`, `plan`, `open_tickets`.

## Non-goals

- The triage agent.
- The MCP tools.
- Evals.
- Any user interface.

## Success signal

A valid decision is accepted, and an invalid one is rejected with an error that states what is wrong. `uv run python load_seed.py` fills `app.db` from the seed CSVs, and a second run leaves that database unchanged.

## Open Questions

- Must `route` match `category` (`billing` with `billing-team`, and the same pairing for the other four), or may any allowed route accompany any allowed category?
