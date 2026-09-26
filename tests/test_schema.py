"""Tests for the Epic 1 triage decision schema."""

import pytest

from schema import Category, Priority, Route, TriageDecision, validate_decision


def test_accepts_valid_decision() -> None:
    decision = validate_decision(
        {
            "category": "billing",
            "priority": "P2",
            "route": "billing-team",
            "rationale": "Double charge matches the billing P2 money rule.",
        }
    )
    assert decision.category is Category.billing
    assert decision.priority is Priority.P2
    assert decision.route is Route.billing_team
    assert decision.rationale.endswith(".")


def test_allows_any_allowed_route_with_any_allowed_category() -> None:
    decision = validate_decision(
        {
            "category": "billing",
            "priority": "P3",
            "route": "bug-team",
            "rationale": "Allowed sets are checked independently.",
        }
    )
    assert decision.category is Category.billing
    assert decision.route is Route.bug_team


@pytest.mark.parametrize("category", [item.value for item in Category])
@pytest.mark.parametrize("priority", [item.value for item in Priority])
@pytest.mark.parametrize("route", [item.value for item in Route])
def test_accepts_every_allowed_value(category: str, priority: str, route: str) -> None:
    decision = validate_decision(
        {
            "category": category,
            "priority": priority,
            "route": route,
            "rationale": "Charged $12.50 twice.",
        }
    )
    assert decision.category.value == category
    assert decision.priority.value == priority
    assert decision.route.value == route


@pytest.mark.parametrize(
    "payload,needle",
    [
        (
            {"priority": "P1", "route": "bug-team", "rationale": "Missing category."},
            "category: Field required",
        ),
        (
            {"category": "billing", "route": "billing-team", "rationale": "Missing priority."},
            "priority: Field required",
        ),
        (
            {"category": "billing", "priority": "P1", "rationale": "Missing route."},
            "route: Field required",
        ),
        (
            {"category": "billing", "priority": "P1", "route": "billing-team"},
            "rationale: Field required",
        ),
        (
            {
                "category": "not-a-category",
                "priority": "P1",
                "route": "billing-team",
                "rationale": "Bad category.",
            },
            "category: Input should be",
        ),
        (
            {
                "category": "billing",
                "priority": "P5",
                "route": "billing-team",
                "rationale": "Bad priority.",
            },
            "priority: Input should be",
        ),
        (
            {
                "category": "billing",
                "priority": "P1",
                "route": "nowhere-team",
                "rationale": "Bad route.",
            },
            "route: Input should be",
        ),
        (
            {
                "category": "billing",
                "priority": "P1",
                "route": "billing-team",
                "rationale": "Extra fields are rejected.",
                "extra": "nope",
            },
            "extra: Extra inputs are not permitted",
        ),
        (
            {
                "category": "billing",
                "priority": "P1",
                "route": "billing-team",
                "rationale": "Two sentences. That is invalid.",
            },
            "rationale must be one sentence",
        ),
        (
            {
                "category": "billing",
                "priority": "P1",
                "route": "billing-team",
                "rationale": "No terminator",
            },
            "rationale must be one sentence",
        ),
        ([], "decision: Input should be a valid dictionary"),
        ("not-an-object", "decision: Input should be a valid dictionary"),
    ],
)
def test_rejects_invalid_decisions_with_clear_error(payload: object, needle: str) -> None:
    with pytest.raises(ValueError, match=needle):
        validate_decision(payload)


def test_model_dump_is_json_ready() -> None:
    decision = TriageDecision(
        category=Category.how_to,
        priority=Priority.P4,
        route=Route.how_to_team,
        rationale="How-to questions stay at P4.",
    )
    dumped = decision.model_dump(mode="json")
    assert dumped == {
        "category": "how-to",
        "priority": "P4",
        "route": "how-to-team",
        "rationale": "How-to questions stay at P4.",
    }
