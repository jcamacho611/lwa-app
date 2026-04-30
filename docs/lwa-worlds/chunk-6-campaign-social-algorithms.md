# LWA CHUNK 6 — CAMPAIGN MANAGER AND SOCIAL POSTING ALGORITHMS

This chunk defines the real campaign manager and direct social posting architecture. These systems must remain behind feature flags until OAuth, scopes, publishing permissions, and verification are implemented.

## Campaign Mode vs Campaign Manager

```text
Campaign Mode = assign roles to clips in one generation result.
Campaign Manager = workspace, brief, calendar, approvals, scheduling, publishing, performance tracking.
```

## Campaign Manager Objects

```text
campaign_workspace
campaign_brief
campaign_plan
campaign_calendar_item
approval_status
publish_status
performance_snapshot
```

## Campaign planner algorithm

```python
def build_campaign_plan(brief, clips):
    scored = []
    for clip in clips:
        score = (
            clip.score * 0.25 +
            (clip.revenue_intent_score or 0) * 0.20 +
            (clip.offer_fit_score or 0) * 0.15 +
            campaign_role_fit(clip, brief) * 0.20 +
            platform_fit(clip, brief.primary_platforms) * 0.10 +
            render_readiness(clip) * 0.10
        )
        scored.append((clip, score))
    return choose_balanced_campaign_mix(scored)
```

## Campaign mix rules

```text
7-day campaign:
- 2 lead or attention clips
- 2 educational clips
- 1 trust or proof clip
- 1 sales or offer clip
- 1 community or retargeting clip

Launch campaign:
- 1 announcement
- 2 problem clips
- 2 proof clips
- 2 objection clips
- 2 sales clips
- 1 urgency or community clip

Medspa campaign:
- prioritize trust, transformation, safety, consultation, and before/after framing

Whop seller campaign:
- prioritize tactical value, proof, community, offer, and money-angle education
```

## Campaign calendar item statuses

```text
approval_status:
- draft
- needs_review
- approved
- rejected
- revised

publish_status:
- not_scheduled
- scheduled
- publishing
- published
- failed
- cancelled
```

## Direct social posting truth

Direct posting must never happen without:

```text
- user OAuth connection
- required scopes
- platform approval when required
- explicit user publish or schedule action
- real clip asset
- valid caption/title payload
- audit trail
```

## Supported social platforms

```text
youtube
tiktok
instagram
facebook
x
linkedin
twitch
reddit
```

## Social account status values

```text
connected
requires_reauth
revoked
limited_scope
posting_not_approved
disabled
```

## Social post statuses

```text
draft
scheduled
publishing
published
failed
cancelled
requires_reauth
blocked_by_platform
```

## Social publish algorithm

```python
def publish_social_post(post, account, asset):
    if not account or account.status != 'connected':
        return fail('social_account_not_connected')

    if not asset:
        return fail('missing_clip_asset')

    if post.status not in {'draft', 'scheduled'}:
        return fail('post_not_publishable_from_current_status')

    if not scopes_allow_posting(account.scopes, post.platform):
        return fail('missing_required_scope')

    if platform_requires_approval(post.platform) and not account.posting_approved:
        return fail('blocked_by_platform')

    if token_expired(account):
        account = refresh_token(account)

    mark_post_status(post.id, 'publishing')

    result = platform_publish(post, account, asset)

    if result.success:
        mark_post_published(post.id, result.platform_post_id, result.platform_post_url)
    else:
        mark_post_failed(post.id, result.error_code)

    return result
```

## OAuth connection algorithm

```python
def start_social_oauth(user, platform):
    if not feature_enabled('direct_social_posting', user):
        return feature_not_live('Direct posting is planned, not live.')

    state = create_oauth_state(user_id=user.id, platform=platform)
    auth_url = build_authorization_url(platform=platform, state=state.value)

    return {
        'authorization_url': auth_url,
        'state_id': state.id
    }
```

## OAuth callback algorithm

```python
def handle_social_oauth_callback(code, state):
    validated = validate_oauth_state(state)
    tokens = exchange_code_for_tokens(validated.platform, code)
    profile = fetch_platform_account_profile(validated.platform, tokens.access_token)

    return upsert_social_account(
        user_id=validated.user_id,
        platform=validated.platform,
        platform_account_id=profile.id,
        access_token_encrypted=encrypt_token(tokens.access_token),
        refresh_token_encrypted=encrypt_token(tokens.refresh_token),
        scopes=tokens.scopes,
        token_expires_at=tokens.expires_at
    )
```

## Safety rules

```text
- Never ask users for social passwords.
- Never post without explicit action.
- Never claim posting is live until API approval and scope tests pass.
- Encrypt all tokens.
- Store scopes and token expiration.
- Refresh tokens safely.
- Log every publish attempt.
```

## Codex prompt

```text
Implement Chunk 6 only.

Task:
Scaffold campaign manager and social posting services behind feature flags.

Rules:
- Preserve current generation.
- Do not enable direct posting as live.
- Do not create fake publish success.
- Encrypt token fields when real storage exists.
- Do not touch iOS.
- Do not touch unrelated frontend files.

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant tests
```
