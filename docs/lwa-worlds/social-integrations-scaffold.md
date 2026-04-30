# Social Integrations Scaffold

## Status

This is a sandbox/read-first foundation for future social and trend integrations.

It does not enable direct posting, does not collect social passwords, and does not claim publishing success.

## Current files

- `lwa-backend/app/services/social_integrations_core.py`
- `lwa-backend/tests/test_social_integrations_core.py`

## Supported scaffold providers

- YouTube
- TikTok
- Instagram
- Twitch
- Reddit
- Polymarket
- Google Trends

## Rules

- OAuth providers require explicit user authorization.
- Posting stays disabled until scopes, approvals, token storage, and tests are verified.
- Polymarket is cultural-attention metadata only.
- No wagering, trading, or betting advice.
- No social password collection.
- No fake posting success.

## Future order

1. Encrypted token storage contract.
2. OAuth start/callback routes.
3. Integration status dashboard.
4. Read-only YouTube/Twitch/Reddit trend reads.
5. Polymarket read-only trend metadata.
6. Direct posting only after provider approvals and explicit user action.

## Claim boundary

Do not describe direct TikTok, Instagram, YouTube, or Twitch publishing as live until the provider-specific implementation, approval, scopes, tests, and user consent flow are complete.
