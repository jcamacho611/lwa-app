# Campaign Mode Foundation

## Purpose
Add campaign-style packaging to the backend without pretending native Whop campaign automation already exists.

## Implemented
- optional campaign request fields:
  - `campaign_brief`
  - `target_audience`
  - `allowed_platforms`
  - `campaign_goal`
  - `required_hashtags`
  - `forbidden_terms`
- optional campaign response fields:
  - `campaign_mode`
  - `campaign_goal`
  - `allowed_platforms`
  - `campaign_readiness`
  - `campaign_notes`
  - `campaign_fit_score`
  - `campaign_fit_reason`
  - `platform_notes`
  - `required_hashtag_suggestions`
  - `compliance_notes`

## Manual Review Boundary
This foundation does not:
- browse Whop campaigns
- submit links to Whop
- automate payouts
- automate direct posting

## Current Safe Notes
- review campaign rules manually before posting
- this package does not submit to any campaign automatically
- use rendered clips only where media assets are available

## Feature Flag Truth
- free: standard packaging only
- pro: richer packaging, but campaign mode still off
- scale: campaign-ready packaging foundation on, still manual workflow

## Future Work
- real campaign imports
- server-side brief validation against campaign requirements
- per-campaign performance feedback
