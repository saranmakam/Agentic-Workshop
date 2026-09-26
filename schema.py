"""Validated shape of a support-ticket triage decision."""

from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, ValidationError, field_validator


class Category(str, Enum):
    billing = "billing"
    bug = "bug"
    access = "access"
    performance = "performance"
    how_to = "how-to"


class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Route(str, Enum):
    billing_team = "billing-team"
    bug_team = "bug-team"
    access_team = "access-team"
    performance_team = "performance-team"
    how_to_team = "how-to-team"


_SENTENCE_END = frozenset(".!?")


def _is_one_sentence(text: str) -> bool:
    stripped = text.strip()
    if not stripped or stripped[-1] not in _SENTENCE_END:
        return False
    # Exactly one sentence terminator, at the end.
    return not re.search(r"[.!?](?!$)", stripped)


class TriageDecision(BaseModel):
    """A triage decision accepted by Epic 1 CAP-1."""

    category: Category
    priority: Priority
    route: Route
    rationale: str

    @field_validator("rationale")
    @classmethod
    def rationale_must_be_one_sentence(cls, value: str) -> str:
        if not _is_one_sentence(value):
            raise ValueError("rationale must be one sentence ending with '.', '!', or '?'")
        return value.strip()


def validate_decision(data: Any) -> TriageDecision:
    """Accept a triage decision or raise ValueError stating what is wrong."""
    try:
        return TriageDecision.model_validate(data)
    except ValidationError as exc:
        parts = []
        for err in exc.errors():
            loc = ".".join(str(x) for x in err["loc"]) or "decision"
            parts.append(f"{loc}: {err['msg']}")
        raise ValueError("; ".join(parts)) from exc
