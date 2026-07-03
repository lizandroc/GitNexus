"""End-to-end API tests using the mock provider — no model runtime needed.

Run:  LAP_PROVIDER=mock pytest tests/ -q   (from local-ai-platform/)
The suite covers: status/privacy, chat + task endpoints, document upload →
indexing → RAG query with citations, all three tools, and usage logging.
"""
from __future__ import annotations

import io

import pytest

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_and_status():
    assert client.get("/health").json() == {"status": "ok"}
    s = client.get("/v1/status").json()
    assert s["server"] == "ok"
    assert s["privacy"]["mode"] == "local-only"
    assert s["providers"]["mock"]["healthy"] is True


def test_privacy_cloud_mode_blocked_by_default():
    r = client.post("/v1/privacy", json={"cloud_mode": True})
    assert r.status_code == 403  # env var LAP_ALLOW_CLOUD not set


def test_models_and_selection():
    m = client.get("/v1/models").json()
    assert any(mod["name"] == "mock-small" for mod in m["providers"]["mock"]["models"])
    r = client.post("/v1/models/select", json={"provider": "mock", "model": "mock-small"})
    assert r.status_code == 200
    assert client.get("/v1/status").json()["active_model"] == "mock-small"


def test_chat_and_task_endpoints():
    r = client.post("/v1/chat", json={"messages": [{"role": "user", "content": "hello platform"}]})
    assert r.status_code == 200
    assert "hello platform" in r.json()["output"]

    r = client.post("/v1/summarize", json={"text": "Quarterly revenue grew 12%."})
    assert r.status_code == 200 and r.json()["output"]

    r = client.post("/v1/classify", json={"text": "I want a refund", "labels": ["sales", "support"]})
    assert r.status_code == 200

    r = client.post("/v1/classify", json={"text": "no labels"})
    assert r.status_code == 400

    r = client.post("/v1/extract", json={"text": "Invoice #42 due June 1",
                                         "fields": {"invoice_number": "the invoice number"}})
    assert r.status_code == 200


def test_document_upload_index_and_rag_query():
    content = (
        "Acme Corp signed the master services agreement on March 3, 2026.\n\n"
        "The renewal term is twelve months with a 30 day termination notice.\n\n"
        "Payment terms are net 45 from invoice date."
    )
    r = client.post(
        "/v1/documents",
        files={"file": ("acme-msa.txt", io.BytesIO(content.encode()), "text/plain")},
        data={"kb": "contracts"},
    )
    assert r.status_code == 200, r.text
    doc = r.json()
    assert doc["status"] == "ready" and doc["num_chunks"] >= 1

    kbs = client.get("/v1/knowledge-bases").json()["knowledge_bases"]
    assert any(kb["name"] == "contracts" for kb in kbs)

    r = client.post("/v1/rag/query", json={"question": "What are the payment terms?", "kb": "contracts"})
    assert r.status_code == 200
    body = r.json()
    assert body["sources"], "RAG must return source citations"
    assert body["sources"][0]["filename"] == "acme-msa.txt"

    # Empty KB answers honestly instead of hallucinating.
    r = client.post("/v1/rag/query", json={"question": "anything?", "kb": "empty-kb"})
    assert r.json()["sources"] == []

    r = client.delete(f"/v1/documents/{doc['id']}")
    assert r.status_code == 200


def test_tools_list_and_run():
    tools = {t["name"] for t in client.get("/v1/tools").json()["tools"]}
    assert {"doc_qa", "email_analyzer", "workflow_runner"} <= tools

    r = client.post("/v1/tools/email_analyzer/run",
                    json={"inputs": {"content": "Hi, following up on the proposal — any update?"}})
    assert r.status_code == 200 and r.json()["output"]

    r = client.post("/v1/tools/workflow_runner/run",
                    json={"inputs": {"input_data": "Meeting with Dana at Acme. She wants pricing by Friday.",
                                     "preset": "crm_note"}})
    assert r.status_code == 200
    assert len(r.json()["steps"]) == 2

    r = client.post("/v1/tools/workflow_runner/run", json={"inputs": {"input_data": "x"}})
    assert r.status_code == 400  # needs preset or steps

    r = client.post("/v1/tools/nope/run", json={"inputs": {}})
    assert r.status_code == 404


def test_usage_tracking():
    runs = client.get("/v1/runs").json()
    assert runs["stats"]["total_runs"] > 0
    kinds = {r["kind"] for r in runs["runs"]}
    assert "chat" in kinds and "tool" in kinds


def test_api_key_auth_when_configured(monkeypatch):
    from app.config import settings as cfg
    monkeypatch.setattr(cfg, "api_key", "secret123")
    assert client.get("/v1/status").status_code == 401
    r = client.get("/v1/status", headers={"Authorization": "Bearer secret123"})
    assert r.status_code == 200
    assert client.get("/health").status_code == 200  # health stays open


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
