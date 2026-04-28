# LWA Connector Protocol Map

## Purpose
This document defines how external systems connect to LWA without turning the product into random one-off integrations.

Every connector must map to protocol responsibilities, safety rules, and future implementation expectations.

## Connector Families

### Source connectors

- Twitch
- stream/VOD platforms
- public URL ingestion
- upload/file inputs

### Monetization connectors

- Whop
- direct checkout paths
- demo forms
- support links
- referral/partner forms

### Future workflow connectors

- creator tester intake
- guild mission engine
- optional marketplace or agency surfaces
- optional blockchain proof bridge

## Connector Protocol Requirements

Every connector definition should include:

- connector name
- role
- source or output relationship
- event relationship
- user-facing claim-safe label
- fallback behavior
- consent requirements

## Example: Twitch

Role:

- source connector
- metadata provider
- highlight workflow path

Must map to:

- `source_type = twitch` or `stream`
- source metadata
- fallback behavior
- event emissions
- output package path

Must not imply:

- private access bypass
- full live chat ingestion before legal/technical review

## Example: Whop

Role:

- monetization connector
- access or checkout path

Must map to:

- entitlement or purchase flow
- CTA click events
- claim-safe upgrade copy

Must not imply:

- campaign submission automation
- payout automation
- the entire company identity

## Example: Optional Blockchain Bridge

Role:

- future proof-of-contribution connector only

Allowed later:

- badges
- proof of contribution
- cosmetics
- reputation visibility

Not allowed without legal and consent review:

- token appreciation claims
- passive income claims
- hidden mining
- undisclosed compute contributions

## Current Repo Alignment

Current repo alignment already includes:

- Whop as one monetization path
- public-source ingest foundations
- source and packaging directions that can expand toward Twitch/stream and upload

Still needed:

- one canonical typed connector registry
- explicit connector event contracts
- consent-aware reward and guild connector mapping

## Testing Expectations

Each connector should be validated for:

- claim safety
- fallback behavior
- typed field compatibility
- event mapping
- consent requirements where relevant

