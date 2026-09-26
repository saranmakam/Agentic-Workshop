---
title: 'Triage decision schema'
type: 'feature'
created: '2026-09-26'
status: 'in-progress'
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

