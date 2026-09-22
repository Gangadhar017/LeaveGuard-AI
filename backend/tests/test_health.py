"""Tests for the health and root endpoints."""


def test_root_returns_api_info(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "LeafGuard AI"
    assert body["docs_url"] == "/docs"


def test_health_reports_model_and_database(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["model_name"] == "stub-svm"
    assert body["database"] == "in-memory"
    assert body["version"]
