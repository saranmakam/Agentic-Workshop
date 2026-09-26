---
title: 'Human-gated escalation'
type: 'feature'
created: '2026-09-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The policy's P1+Enterprise rule is the riskiest action the agent can take. It must never fire on its own.

**Approach:** Add the `escalate_to_human` tool and LangChain human-in-the-loop approval gate (CAP-5): the policy's P1+Enterprise rule pauses the run for a terminal yes/no, and nothing escalates without a yes.

</frozen-after-approval>

## Implementation Notes

- `escalate_to_human` (in `agent.py`, alongside story 1's code — both stories share this one file, same as Epic 1's schema/loader pairing) is a local `@tool`, not part of `mcp/triage_server.py` (which is read-only, per the SPEC's constraint). It takes the agent's proposed `category`/`priority`/`route`/`rationale` and returns a placeholder success string; the actual gate is `HumanInTheLoopMiddleware(interrupt_on={"escalate_to_human": {"allowed_decisions": ["approve", "reject"]}})`, added to `build_agent()`'s middleware list.
- The system prompt instructs the model to call `escalate_to_human` and wait for its result only when the final priority is P1 for an Enterprise customer, and to still return its best decision (without escalating again) if escalation is rejected.
- `run_once()` checks `result["__interrupt__"]` after the first `agent.ainvoke()`; if present, `_ask_human_to_approve_escalation()` prints the interrupt payload and blocks on a terminal `input()` prompt (`y`/`n`), then resumes the same thread with `agent.ainvoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)` (or `{"type": "reject", "feedback": ...}` on "no") — a `MemorySaver` checkpointer keyed by `thread_id` makes the resume possible. No path calls `escalate_to_human`'s underlying logic without going through this interrupt/resume cycle first, so nothing escalates without an explicit "yes".
- Verification:
  - `tests/test_agent.py::test_escalate_to_human_tool_shape` checks the tool's name, description, and argument schema (`category`, `priority`, `route`, `rationale`) so the model has the fields it needs to call it correctly.
  - **Not yet live-verified end to end.** None of the tickets exercised so far (`T-1042`, `T-1099`) reach P1+Enterprise, so the interrupt/resume path itself hasn't been driven by a real run. `app.db` has several candidates that should reach it, e.g. `T-1044` ("Our whole team is locked out after the SSO change this morning." — Globex, Enterprise, 3 open tickets, at the Enterprise-bump threshold) or `T-1048` (Hooli, Enterprise, 4 open tickets, "The API returns 500 on every write request."). Running `uv run python run_agent.py T-1044` should pause at a `y`/`n` terminal prompt; this is deferred because the Gemini free-tier daily quota (20 requests/day) was exhausted by this session's other live checks before this could be tried, and no `GROQ_API_KEY` is available as a fallback (both keys are empty placeholders in `.env`; a real key was only present in the shell environment for this session, already spent).

## Review Triage Log

- Not yet run through `/bmad-code-review`. The CAP-5 interrupt/resume path in particular has only been verified by reading the code and its middleware wiring, not by an actual paused run — flag this for extra scrutiny in that review, and prioritize a live `T-1044`/`T-1048` run once quota or a Groq key is available.
