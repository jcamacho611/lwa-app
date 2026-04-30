# LWA Social API Future Plan

## Status

Future phase unless repo evidence proves otherwise.

## Provider direction

Potential providers:

- YouTube
- TikTok
- Instagram / Meta
- Twitch
- Reddit
- Google Trends or a trend-data provider
- Polymarket Gamma read-only
- OpenAI
- Anthropic Claude
- Seedance / BytePlus ModelArk
- Apple App Store Connect for app metadata/readiness where appropriate

## Safe first slice

OAuth/status shell only:

- auth URL
- callback
- link status
- revoke
- encrypted tokens if tokens are stored
- provider status docs
- no auto-posting until approved

## Polymarket rule

Polymarket data may only be used as read-only cultural trend metadata.

Do not:

- place trades
- recommend bets
- create betting UI
- reward wagering
- imply financial advice

## Posting rule

Do not implement direct posting until provider app review, scopes, rate limits, and user consent flows are confirmed.

## Token storage rule

Do not store social tokens unless the backend has:

- encryption at rest
- OAuth state verification
- refresh/revocation handling
- clear scope display
- provider status audit trail

## First implementation direction

Start with an integrations dashboard/status shell before real provider actions:

- provider name
- configured/not configured
- connected/disconnected
- scopes requested
- approval status
- last sync
- last error

## Safe customer copy

Use:

Social integrations are planned to help organize source metadata, trend signals, and approved publishing workflows.

Avoid:

Guaranteed posting, guaranteed reach, or platform approval claims.
