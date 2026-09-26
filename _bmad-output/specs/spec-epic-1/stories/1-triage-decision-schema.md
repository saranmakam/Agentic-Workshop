---
title: 'Triage decision schema'
type: 'feature'
created: '2026-09-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Later epics need one accepted shape for a triage decision. Without it, agents and evals cannot agree on what a valid decision is.

**Approach:** Add a validation model that accepts only a JSON object with `category`, `priority`, `route`, and a one-sentence `rationale` from the allowed sets, and rejects anything else with an error that states what is wrong. No category–route pairing rule is enforced.

</frozen-after-approval>

## Implementation Notes

- Added `schema.py` with `Category`, `Priority`, `Route`, `TriageDecision`, and `validate_decision()`.
- Pydantic enums enforce allowed values; `extra="forbid"` rejects unknown fields.
- One-sentence check allows decimals (`$12.50`) and common abbreviations; still requires a final `.` `!` or `?`.
- Category and route stay independent — no pairing rule.
- Tests in `tests/test_schema.py` (120 project tests total with loader).

## Review Triage Log

- Blind Hunter (self-pass; nested review subagent not launched): one-sentence rule too strict on decimals — **false**; decimals and abbreviations are masked before the terminator scan.
- Blind Hunter: no category–route pairing — **false** against this story; pairing was left unresolved on purpose and must not be invented.
- Blind Hunter: extra fields silently dropped — **patch** then fixed with `extra="forbid"`.
- Branch also contains the seed loader — **kept** on `story-1/sharan-1.1` as requested.
