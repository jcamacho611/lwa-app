# Backend Campaign Workflow Foundation

## Current truth

The backend accepts optional campaign-style briefing fields:

- `campaign_brief`
- `campaign_goal`
- `allowed_platforms`
- `required_hashtags`
- `forbidden_terms`

When present, the backend can return:

- `campaign_mode`
- `campaign_readiness`
- `campaign_notes`
- `campaign_fit_score`
- `campaign_fit_reason`
- `platform_notes`
- `required_hashtag_suggestions`
- `compliance_notes`

## Manual-review boundary

Campaign packaging is manual-review foundation only.

Required disclaimers returned in notes:

- Review campaign rules manually before posting.
- LWA does not submit to Whop campaigns automatically.
- Use only rendered clips where a playable asset is available.

## Feature gating

- free: basic packaging only
- pro: richer packaging and exports, but no live campaign automation
- scale: campaign packaging fields can be returned

## What is not implemented

- Whop campaign browsing
- automatic campaign submission
- payout tracking
- platform posting automation

## Safe claims

Say:

- LWA can help package campaign-ready clips for manual review.

Do not say:

- LWA submits to campaigns automatically
- LWA guarantees campaign approval
