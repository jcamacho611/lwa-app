import unittest

from app.services.social_integrations_core import (
    OAuthStartRequest,
    SocialProvider,
    build_oauth_authorization_url,
    get_provider_capability,
    list_provider_capabilities,
    posting_allowed,
    social_integration_disclosure,
)


def test_provider_capabilities_include_read_only_polymarket() -> None:
    capability = get_provider_capability(SocialProvider.POLYMARKET)

    assert capability is not None
    assert capability.read_supported is True
    assert capability.publish_supported is False
    assert "Read-only" in capability.safety_note or "read-only" in capability.safety_note


def test_posting_is_disabled_by_default_for_all_scaffold_providers() -> None:
    for item in list_provider_capabilities():
        assert posting_allowed(item["provider"]) is False


def test_oauth_authorization_url_requires_state() -> None:
    with unittest.TestCase().assertRaises(ValueError):
        build_oauth_authorization_url(
            OAuthStartRequest(
                provider=SocialProvider.YOUTUBE,
                client_id="client",
                redirect_uri="https://example.com/callback",
                state="",
                auth_base_url="https://provider.example/oauth",
            )
        )


def test_oauth_authorization_url_builds_scopes() -> None:
    url = build_oauth_authorization_url(
        OAuthStartRequest(
            provider=SocialProvider.YOUTUBE,
            client_id="client",
            redirect_uri="https://example.com/callback",
            state="secure-state",
            scopes=("youtube.readonly",),
            auth_base_url="https://provider.example/oauth",
        )
    )

    assert "client_id=client" in url
    assert "state=secure-state" in url
    assert "youtube.readonly" in url


def test_social_disclosure_blocks_fake_posting_claims() -> None:
    disclosure = social_integration_disclosure().lower()

    assert "sandbox" in disclosure
    assert "explicit user actions" in disclosure
