from __future__ import annotations

from fastapi.testclient import TestClient

from app.services.engine_service_app import app
from app.services import engine_runtime


def test_health_endpoint_defaults_safely(monkeypatch):
    monkeypatch.delenv(engine_runtime.ENV_VAR_NAME, raising=False)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "lwa-engine-service"
    assert body["safe_mode"] is True
    assert body["runtime"]["selected_engine_id"] == "operator_admin"


def test_engine_endpoint_returns_selected_engine(monkeypatch):
    monkeypatch.setenv(engine_runtime.ENV_VAR_NAME, "safety")
    client = TestClient(app)

    response = client.get("/engine")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["engine"]["engine_id"] == "safety"


def test_engine_health_endpoint(monkeypatch):
    monkeypatch.setenv(engine_runtime.ENV_VAR_NAME, "proof_history")
    client = TestClient(app)

    response = client.get("/engine/health")

    assert response.status_code == 200
    body = response.json()
    assert body["engine_id"] == "proof_history"
    assert body["runtime"]["selected_engine_id"] == "proof_history"


def test_engine_demo_endpoint_is_safe(monkeypatch):
    monkeypatch.setenv(engine_runtime.ENV_VAR_NAME, "social_distribution")
    client = TestClient(app)

    response = client.post("/engine/demo", json={"payload": {"platform": "tiktok"}})

    assert response.status_code == 200
    body = response.json()
    assert body["engine_id"] == "social_distribution"
    assert body["output"]["external_action_executed"] is False
    assert body["output"]["social_post_executed"] is False


def test_invalid_engine_id_returns_configuration_error(monkeypatch):
    monkeypatch.setenv(engine_runtime.ENV_VAR_NAME, "missing")
    client = TestClient(app)

    health_response = client.get("/health")
    demo_response = client.post("/engine/demo", json={"payload": {}})

    assert health_response.status_code == 200
    assert health_response.json()["status"] == "configuration_error"
    assert demo_response.status_code == 200
    assert demo_response.json()["status"] == "configuration_error"
