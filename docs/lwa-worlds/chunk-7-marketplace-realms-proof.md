# LWA CHUNK 7 — MARKETPLACE, SIGNAL REALMS, AND PROOF ALGORITHMS

This chunk defines marketplace ranking, seller trust, Signal Realms progression, and off-chain proof-of-creation systems. These are future/scaffolded systems until implemented behind feature flags.

## Marketplace rules

```text
- Sell templates, hook packs, caption presets, B-roll packs, brand kits, Director Brain prompt packs, and commission products.
- Use integer cents only.
- Use idempotent webhooks.
- No guaranteed income language.
- Seller payouts require trusted payment state.
- Refunds and disputes must be tracked.
- Products must be reviewable by admin.
```

## Marketplace product types

```text
clip_template
hook_pack
caption_preset
broll_pack
brand_kit
director_brain_prompt_pack
clip_on_commission
campaign_pack
```

## Marketplace ranking formula

```text
MarketplaceRank =
  0.22 * ProductQualityScore +
  0.18 * SellerTrustScore +
  0.16 * BuyerFitScore +
  0.14 * ConversionRateScore +
  0.10 * LowRefundScore +
  0.08 * FreshnessScore +
  0.07 * PriceFitScore +
  0.05 * RatingScore
```

## Seller trust formula

```text
SellerTrustScore =
  0.25 * CompletedOrderScore +
  0.20 * LowRefundRate +
  0.20 * LowDisputeRate +
  0.15 * ProductReviewScore +
  0.10 * AccountAgeScore +
  0.10 * ComplianceScore
```

## Marketplace money split

```python
def calculate_marketplace_split(price_cents, take_rate_bps=2000):
    if price_cents < 0:
        raise ValueError('price_cents cannot be negative')
    platform_fee_cents = price_cents * take_rate_bps // 10000
    seller_net_cents = price_cents - platform_fee_cents
    return {
        'subtotal_cents': price_cents,
        'platform_fee_cents': platform_fee_cents,
        'seller_net_cents': seller_net_cents,
        'total_cents': price_cents,
        'currency': 'usd'
    }
```

## Marketplace ranking pseudocode

```python
def rank_marketplace_products(user, query, filters):
    products = search_marketplace_products(query, filters)
    ranked = []

    for product in products:
        seller = get_seller_profile(product.seller_user_id)
        score = (
            0.22 * score_product_quality(product) +
            0.18 * seller.trust_score +
            0.16 * score_buyer_fit(user, product) +
            0.14 * score_conversion_rate(product) +
            0.10 * score_low_refund(product) +
            0.08 * score_freshness(product) +
            0.07 * score_price_fit(product, filters) +
            0.05 * score_rating(product.average_rating)
        )
        ranked.append((product, score))

    return sort_desc(ranked)
```

## Marketplace safety filters

```text
Reject or review products that include:
- guaranteed income claims
- platform evasion promises
- spam automation
- impersonation
- unsafe scraping instructions
- investment language
- hidden refund terms
```

---

# Signal Realms RPG Layer

## Purpose

Signal Realms is the retention layer. It should reward real usage and identity without creating pay-to-win or legal risk.

## Realms rules

```text
- XP cannot be bought.
- Badges are earned.
- Relics are cosmetic only.
- No pay-to-win.
- No gambling mechanics.
- No investment language.
- No yield or tokenomics.
```

## Classes

```text
clip_smith
hook_hunter
caption_mage
trend_rider
campaign_architect
marketplace_merchant
signal_scout
realm_builder
growth_alchemist
edit_warrior
proof_keeper
community_summoner
```

## Factions

```text
House Velocity
The Hookborn
Order of Proof
Caption Guild
The Signal Scouts
Marketplace Forge
The Retention Circle
House Whopfire
The Local Kings
The Creator Legion
The Algorithm Watch
The Black Gold Order
```

## XP formula

```text
XP required for next level = 100 + ((level - 1) * 35)
```

## XP events

```text
generation_completed: 15
clip_downloaded: 10
hook_copied: 4
caption_copied: 4
campaign_created: 25
social_account_connected: 20
marketplace_purchase: 5
marketplace_product_published: 30
quest_completed: 50
```

Marketplace purchase XP is intentionally tiny and cosmetic. It must not create a paid advantage.

## XP pseudocode

```python
XP_RULES = {
    'generation_completed': 15,
    'clip_downloaded': 10,
    'hook_copied': 4,
    'caption_copied': 4,
    'campaign_created': 25,
    'social_account_connected': 20,
    'marketplace_purchase': 5,
    'marketplace_product_published': 30,
    'quest_completed': 50,
}

def award_xp(user, event_type, source=None):
    if not feature_enabled('rpg_realms', user):
        return None
    xp = XP_RULES.get(event_type, 0)
    if xp <= 0:
        return None
    profile = get_or_create_realms_profile(user.id)
    event = create_xp_event(profile.id, event_type, xp, source)
    update_profile_xp(profile.id, xp)
    return event
```

## Quest algorithm

```python
def update_quests_for_event(user, event_type):
    quests = get_active_quests_for_event(event_type)
    for quest in quests:
        user_quest = get_or_create_user_quest(user.id, quest.id)
        if user_quest.completed:
            continue
        user_quest.progress_count += 1
        if user_quest.progress_count >= quest.required_count:
            user_quest.completed = True
            award_xp(user, 'quest_completed', source={'quest_id': quest.id})
            if quest.badge_reward_key:
                award_badge(user, quest.badge_reward_key)
            if quest.cosmetic_reward_key:
                award_cosmetic(user, quest.cosmetic_reward_key)
        save_user_quest(user_quest)
```

---

# Proof of Creation / Blockchain Provenance

## Purpose

Proof should start off-chain. Blockchain publishing is optional future infrastructure, not MVP.

## Safety rules

```text
- Off-chain proof first.
- Optional Merkle batching later.
- Testnet before mainnet.
- No tokenomics.
- No yield.
- No fractionalization.
- No feature unlocks from NFTs.
- No investment language.
```

## Off-chain proof algorithm

```python
def create_offchain_proof(clip, assets):
    content_hash = sha256(stable_json({
        'clip_id': clip.id,
        'title': clip.title,
        'hook': clip.hook,
        'start_seconds': clip.start_seconds,
        'end_seconds': clip.end_seconds,
        'asset_urls': sorted([asset.asset_url for asset in assets])
    }))

    metadata_hash = sha256(stable_json({
        'algorithm': 'LWA_DIRECTOR_BRAIN_V0',
        'created_by_lwa': True
    }))

    return create_proof_event(
        content_hash=content_hash,
        metadata_hash=metadata_hash,
        proof_status='offchain_recorded'
    )
```

## Merkle batch algorithm

```python
def build_merkle_root(leaves):
    if not leaves:
        return None
    level = leaves
    while len(level) > 1:
        next_level = []
        for index in range(0, len(level), 2):
            left = level[index]
            right = level[index + 1] if index + 1 < len(level) else left
            next_level.append(sha256(''.join(sorted([left, right]))))
        level = next_level
    return level[0]
```

## Badge and relic rules

```text
Soulbound badge:
- earned only
- non-transferable
- no paid advantage
- no income claim

Cosmetic relic:
- profile/identity customization only
- no XP advantage
- no ranking advantage
- no paid feature unlock
- no investment framing
```

## Codex prompt

```text
Implement Chunk 7 only.

Task:
Scaffold marketplace ranking, seller trust, Signal Realms XP/quests/badges, and off-chain proof services behind feature flags.

Rules:
- Do not enable marketplace checkout as live.
- Money uses integer cents.
- Webhooks are idempotent.
- XP cannot be bought.
- Badges are earned.
- Relics are cosmetic only.
- Proof remains off-chain unless a later dedicated blockchain task enables testnet publishing.
- Do not touch iOS.
- Do not touch unrelated frontend files.

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant tests
```
