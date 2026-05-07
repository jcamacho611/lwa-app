from __future__ import annotations

import os

from app.services import engine_runtime


VALID_ENGINE_IDS = [
    "creator",
    "brain",
    "render",
    "marketplace",
    "wallet_entitlements",
    "proof_history",
    "world_game",
    "safety",
    "social_distribution",
    "operator_admin",
]


def test_missing_engine_env_defaults_to_operator_admin(monkeypatch):
    monkeypatch.delenv(engine_runtime.ENV_VAR_NAME, raising=False)

    selection = engine_runtime.get_runtime_selection()

    assert selection.valid is True
    assert selection.selected_engine_id == "operator_admin"
    assert selection.warning


def test_each_valid_engine_id_selects_engine(monkeypatch):
    for engine_id in VALID_ENGINE_IDS:
        monkeypatch.setenv(engine_runtime.ENV_VAR_NAME, engine_id)

        selection = engine_runtime.get_runtime_selection()
        engine = engine_runtime.get_selected_engine()

        assert selection.valid is True
        assert selection.selected_engine_id == engine_id
        assert engine is not None
        assert engine.engine_id == engine_id


def test_invalid_engine_id_returns_safe_configuration_error(monkeypatch):
    monkeypatch.setenv(engine_runtime.ENV_VAR_NAME, "not_real")

    selection = engine_runtime.get_runtime_selection()
    health = engine_runtime.selected_engine_health()
    demo = engine_runtime.run_selected_engine_demo({"source": "demo"})

    assert selection.valid is False
    assert health["healthy"] is False
    assert health["status"] == "configuration_error"
    assert demo["status"] == "configuration_error"
    assert demo["output"]["external_action_executed"] is False
    assert demo["output"]["payment_or_payout_executed"] is False


def test_demo_response_is_local_safe(monkeypatch):
    monkeypatch.setenv(engine_runtime.ENV_VAR_NAME, "wallet_entitlements")

    demo = engine_runtime.run_selected_engine_demo({"requested_cost": 10})
    output = demo["output"]

    assert demo["engine_id"] == "wallet_entitlements"
    assert output["external_action_executed"] is False
    assert output["paid_provider_called"] is False
    assert output["payment_or_payout_executed"] is False
    assert output["crypto_or_blockchain_action_executed"] is False
    assert output["social_post_executed"] is False
