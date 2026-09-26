# Epic 1 Context: triage data and schema

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Later epics cannot run until a triage decision has one accepted shape and the seed data sits in the SQLite file the triage MCP server already reads. This epic delivers that foundation: a validated decision shape and an idempotent seed load into `app.db`. Planning artifacts (PRD, architecture, UX/design, product brief) were missing or empty under `_bmad-output/planning-artifacts`; requirements below are taken only from the epic spec and stories.

## Stories

- Story 1.1: Triage decision schema
- Story 1.2: Seed loader

## Requirements & Constraints

- Accept a triage decision only as a JSON object with `category`, `priority`, `route`, and a one-sentence `rationale`.
- Allowed categories: `billing`, `bug`, `access`, `performance`, `how-to`. Allowed priorities: `P1`–`P4`. Allowed routes: `billing-team`, `bug-team`, `access-team`, `performance-team`, `how-to-team`.
- Reject missing fields, values outside those sets, a non-one-sentence rationale, or any other shape, with an error that states what is wrong.
- `uv run python load_seed.py` loads `seed/tickets.csv` into `app.db` table `tickets` and `seed/customers.csv` into `customers`, preserving the CSV columns; a second run leaves both tables identical.
- Python 3.12+, managed with uv. Do not modify `seed/`. No network calls or API keys.
- Out of scope: triage agent, MCP tools, evals, and any UI.

## Technical Decisions

- Persist seed data in local SQLite `app.db` already consumed by `mcp/triage_server.py`.
- `tickets` columns: `ticket_id`, `customer_id`, `created_at`, `text`. `customers` columns: `customer_id`, `name`, `plan`, `open_tickets`.
- Whether `route` must pair with `category` is unresolved; both sets are independently constrained for now.

## Cross-Story Dependencies

Story 1.2 (seed loader) runs after Story 1.1 (schema).
