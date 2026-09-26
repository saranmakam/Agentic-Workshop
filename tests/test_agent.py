"""Tests for the Epic 2 triage agent.

No GEMINI_API_KEY or GROQ_API_KEY is configured for this workshop run, so these
tests cover what does not require a live model call: the provider switch (CAP-2),
the escalate_to_human tool's shape (part of CAP-5), and the real MCP tool chain
the agent depends on (CAP-3). The full triage() flow against a live model is
covered by test_triage_end_to_end_examples, which skips itself without a key.
"""

from __future__ import annotations

import json
import os

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

import agent
import load_seed
from agent import _build_model, _load_mcp_tools, escalate_to_human, triage


def test_build_model_defaults_to_gemini(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PROVIDER", raising=False)
    monkeypatch.delenv("MODEL", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    model = _build_model()
    assert isinstance(model, ChatGoogleGenerativeAI)
    assert model.model.endswith("gemini-3.8-flash")


def test_build_model_honors_model_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PROVIDER", raising=False)
    monkeypatch.setenv("MODEL", "gemini-2.0-flash")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    model = _build_model()
    assert model.model.endswith("gemini-2.0-flash")


def test_build_model_switches_to_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROVIDER", "groq")
    monkeypatch.delenv("MODEL", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")
    model = _build_model()
    assert isinstance(model, ChatGroq)
    assert model.model_name == "openai/gpt-oss-120b"


def test_build_model_groq_honors_model_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROVIDER", "groq")
    monkeypatch.setenv("MODEL", "llama-3.1-70b")
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")
    model = _build_model()
    assert model.model_name == "llama-3.1-70b"


def test_build_model_requires_the_matching_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PROVIDER", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(KeyError):
        _build_model()


def test_escalate_to_human_tool_shape() -> None:
    assert escalate_to_human.name == "escalate_to_human"
    assert "Enterprise" in escalate_to_human.description or "P1" in escalate_to_human.description
    field_names = set(escalate_to_human.args_schema.model_fields)
    assert field_names == {"category", "priority", "route", "rationale"}


@pytest.mark.asyncio
async def test_mcp_tools_expose_get_ticket_and_get_customer_history(tmp_path, monkeypatch) -> None:
    load_seed.load_seed()  # ensure app.db exists for the real MCP server subprocess
    tools = await _load_mcp_tools()
    names = {t.name for t in tools}
    assert names == {"get_ticket", "get_customer_history"}


@pytest.mark.asyncio
async def test_mcp_ticket_then_customer_lookup_matches_billing_example() -> None:
    """Grounds CAP-3's ordering contract: get_ticket's customer_id feeds get_customer_history."""
    load_seed.load_seed()
    tools = await _load_mcp_tools()
    by_name = {t.name: t for t in tools}

    raw_ticket = await by_name["get_ticket"].ainvoke({"ticket_id": "T-1042"})
    ticket = json.loads(raw_ticket[0]["text"])
    assert ticket["customer_id"] == "C-77"

    raw_customer = await by_name["get_customer_history"].ainvoke(
        {"customer_id": ticket["customer_id"]}
    )
    customer = json.loads(raw_customer[0]["text"])
    assert customer["plan"] == "Enterprise"
    assert customer["open_tickets"] < 3  # under the Enterprise-bump threshold


@pytest.mark.skipif(
    not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GROQ_API_KEY")),
    reason="requires a live GEMINI_API_KEY or GROQ_API_KEY to run the agent end to end",
)
@pytest.mark.asyncio
async def test_triage_end_to_end_examples() -> None:
    """Live check for CAP-1, CAP-3, CAP-4, and CAP-6, per SPEC's Success signal."""
    load_seed.load_seed()

    decision = await triage("T-1042")
    assert decision["category"] == "billing"
    assert decision["priority"] == "P2"
    assert decision["route"] == "billing-team"

    injected = await triage("T-1099")
    assert injected["category"] == "bug"
    assert injected["priority"] == "P4"
