"""Auto model routing tests — offline, mock provider.

LAP_MODEL_FAST / LAP_MODEL_QUALITY are pointed at mock model names so the
router's tier choices are directly observable in API responses.
"""
from __future__ import annotations

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.routing import pick_model  # noqa: E402

client = TestClient(app)


def test_pick_model_tiers():
    model, reason = pick_model("classify", 50, "billing question")
    assert model == "mock-fast" and "structured" in reason

    model, _ = pick_model("extract", 50000, "huge doc")
    assert model == "mock-fast"  # structured stays fast regardless of size

    model, _ = pick_model("chat", 50, "hello there")
    assert model == "mock-fast"

    model, reason = pick_model("chat", 50, "analyze our churn and explain why it rose")
    assert model == "mock-quality" and "reasoning" in reason

    model, reason = pick_model("chat", 9000, "x" * 9000)
    assert model == "mock-quality" and "long input" in reason

    model, _ = pick_model("summarize", 1000, "short note")
    assert model == "mock-fast"
    model, _ = pick_model("summarize", 20000, "long report")
    assert model == "mock-quality"

    model, _ = pick_model("tool:workflow_runner", 100, "")
    assert model == "mock-quality"

    model, _ = pick_model("rag_query", 40, "what are the payment terms?")
    assert model == "mock-fast"


def test_status_reports_routing_defaults_on():
    s = client.get("/v1/status").json()
    assert s["routing"]["auto"] is True
    assert s["routing"]["fast_model"] == "mock-fast"
    assert s["routing"]["quality_model"] == "mock-quality"


def test_chat_routes_and_reports():
    r = client.post("/v1/chat", json={"messages": [{"role": "user", "content": "hi"}]}).json()
    assert r["model"] == "mock-fast"
    assert r["routing"].startswith("fast tier")

    r = client.post("/v1/chat", json={
        "messages": [{"role": "user", "content": "please analyze this quarter's numbers and explain the trend"}]
    }).json()
    assert r["model"] == "mock-quality"
    assert r["routing"].startswith("quality tier")


def test_explicit_model_wins_over_routing():
    r = client.post("/v1/chat", json={
        "messages": [{"role": "user", "content": "hi"}], "model": "mock-small"
    }).json()
    assert r["model"] == "mock-small"
    assert r["routing"] == "explicit model requested"


def test_toggle_routing_off_uses_active_model():
    assert client.post("/v1/routing", json={"auto": False}).json()["auto"] is False
    client.post("/v1/models/select", json={"provider": "mock", "model": "mock-small"})
    r = client.post("/v1/chat", json={"messages": [{"role": "user", "content": "hi"}]}).json()
    assert r["model"] == "mock-small"
    assert "auto-routing off" in r["routing"]
    # back on: routing resumes
    assert client.post("/v1/routing", json={"auto": True}).json()["auto"] is True
    r = client.post("/v1/chat", json={"messages": [{"role": "user", "content": "hi"}]}).json()
    assert r["model"] == "mock-fast"


def test_tool_run_reports_routing():
    r = client.post("/v1/tools/email_analyzer/run",
                    json={"inputs": {"content": "Quick note: are we still on for Friday?"}}).json()
    assert r["model"] in ("mock-fast", "mock-quality")
    assert "tier" in r["routing"]


def test_workspace_and_ops_pages_served():
    assert "Local AI — Workspace" in client.get("/").text
    assert "Local AI Platform" in client.get("/ops").text
