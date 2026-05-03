from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import uuid4

# LWA MARKETPLACE FOUNDATION
# INTEGER CENTS ONLY
# NO GUARANTEED INCOME
# NO LIVE PAYOUTS IN SCAFFOLD
# IDEMPOTENT WEBHOOK READY


class ProductType(StrEnum):
    TEMPLATE = "template"
    HOOK_PACK = "hook_pack"
    BROLL = "broll"
    BRAND_KIT = "brand_kit"
    PROMPT_PACK = "prompt_pack"
    CLIP_COMMISSION = "clip_commission"
    CLIP_PACK = "clip_pack"
    CAPTION_STYLE = "caption_style"
    THUMBNAIL_PACK = "thumbnail_pack"
    RENDER_PRESET = "render_preset"
    CREATOR_WORKFLOW = "creator_workflow"
    CHARACTER_SKIN = "character_skin"
    LEE_WUH_MERCH = "lee_wuh_merch"
    BRAND_JOB = "brand_job"
    CAMPAIGN_PACK = "campaign_pack"


class ProductStatus(StrEnum):
    DRAFT = "draft"
    LISTED = "listed"
    PAUSED = "paused"
    TAKEDOWN = "takedown"


class OrderStatus(StrEnum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    REFUNDED = "refunded"
    FAILED = "failed"


BANNED_CATEGORIES = {
    "gambling",
    "securities",
    "get_rich_quick",
    "regulated_firearms",
    "unsafe_health_claims",
}


@dataclass(frozen=True)
class MarketplaceProductDraft:
    seller_id: str
    product_type: ProductType
    title: str
    description: str
    price_cents: int
    category: str | None = None
    tags: list[str] = field(default_factory=list)
    ftc_disclosure_required: bool = False


@dataclass(frozen=True)
class MarketplaceProduct:
    id: str
    seller_id: str
    product_type: ProductType
    title: str
    description: str
    price_cents: int
    status: ProductStatus
    category: str | None = None
    tags: list[str] = field(default_factory=list)
    ftc_disclosure_required: bool = False
    rail: str = "stripe"
    asset_urls: list[str] = field(default_factory=list)
    preview_url: str | None = None
    download_count: int = 0
    rating: float = 0.0
    review_count: int = 0


@dataclass(frozen=True)
class MarketplaceOrderQuote:
    order_id: str
    product_id: str
    buyer_id: str
    seller_id: str
    amount_cents: int
    platform_fee_cents: int
    seller_receives_cents: int
    currency: str = "usd"
    status: OrderStatus = OrderStatus.CREATED


def validate_price_cents(price_cents: int) -> None:
    if not isinstance(price_cents, int):
        raise ValueError("price_cents must be an integer number of cents")
    if price_cents < 0:
        raise ValueError("price_cents cannot be negative")


def validate_category(category: str | None) -> None:
    if not category:
        return
    normalized = category.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in BANNED_CATEGORIES:
        raise ValueError(f"category is not allowed in marketplace scaffold: {normalized}")


def create_product_draft(draft: MarketplaceProductDraft) -> MarketplaceProduct:
    validate_price_cents(draft.price_cents)
    validate_category(draft.category)
    if not draft.title.strip():
        raise ValueError("product title is required")
    if draft.product_type == ProductType.CLIP_COMMISSION:
        ftc_required = True
    else:
        ftc_required = draft.ftc_disclosure_required
    return MarketplaceProduct(
        id=str(uuid4()),
        seller_id=draft.seller_id,
        product_type=draft.product_type,
        title=draft.title.strip(),
        description=draft.description.strip(),
        price_cents=draft.price_cents,
        status=ProductStatus.DRAFT,
        category=draft.category,
        tags=list(draft.tags),
        ftc_disclosure_required=ftc_required,
    )


def calculate_platform_fee(amount_cents: int, fee_bps: int = 1000) -> int:
    """Calculate platform fee using integer basis points.

    Default 1000 bps = 10%. Never use floats for money.
    """
    validate_price_cents(amount_cents)
    if fee_bps < 0 or fee_bps > 10_000:
        raise ValueError("fee_bps must be between 0 and 10000")
    return (amount_cents * fee_bps) // 10_000


def quote_order(*, product: MarketplaceProduct, buyer_id: str, fee_bps: int = 1000) -> MarketplaceOrderQuote:
    if product.status != ProductStatus.LISTED:
        raise ValueError("product must be listed before checkout")
    fee = calculate_platform_fee(product.price_cents, fee_bps=fee_bps)
    return MarketplaceOrderQuote(
        order_id=str(uuid4()),
        product_id=product.id,
        buyer_id=buyer_id,
        seller_id=product.seller_id,
        amount_cents=product.price_cents,
        platform_fee_cents=fee,
        seller_receives_cents=product.price_cents - fee,
    )


def public_marketplace_disclosure() -> str:
    return "Earnings vary. There is no guarantee of income, sales, views, or marketplace results."


def product_to_public_dict(product: MarketplaceProduct) -> dict[str, Any]:
    return {
        "id": product.id,
        "type": product.product_type,
        "title": product.title,
        "description": product.description,
        "price_cents": product.price_cents,
        "currency": "usd",
        "status": product.status,
        "category": product.category,
        "tags": product.tags,
        "ftc_disclosure_required": product.ftc_disclosure_required,
        "disclosure": public_marketplace_disclosure(),
        "preview_url": product.preview_url,
        "download_count": product.download_count,
        "rating": product.rating,
        "review_count": product.review_count,
    }


@dataclass(frozen=True)
class CreatorProfile:
    """Creator profile for marketplace sellers."""
    id: str
    user_id: str
    display_name: str
    bio: str | None = None
    avatar_url: str | None = None
    social_links: dict[str, str] = field(default_factory=dict)
    verified: bool = False
    total_sales: int = 0
    total_products: int = 0
    average_rating: float = 0.0


@dataclass(frozen=True)
class MarketplaceListing:
    """Marketplace listing with search and filter metadata."""
    product: MarketplaceProduct
    seller: CreatorProfile
    featured: bool = False
    trending: bool = False
    category_rank: int | None = None


def search_listings(
    listings: list[MarketplaceListing],
    query: str | None = None,
    product_type: ProductType | None = None,
    category: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    min_rating: float | None = None,
    featured_only: bool = False
) -> list[MarketplaceListing]:
    """Search and filter marketplace listings."""
    filtered = listings
    
    if featured_only:
        filtered = [l for l in filtered if l.featured]
    
    if query:
        query_lower = query.lower()
        filtered = [
            l for l in filtered
            if query_lower in l.product.title.lower()
            or query_lower in l.product.description.lower()
            or any(query_lower in tag.lower() for tag in l.product.tags)
        ]
    
    if product_type:
        filtered = [l for l in filtered if l.product.product_type == product_type]
    
    if category:
        filtered = [l for l in filtered if l.product.category == category]
    
    if min_price is not None:
        filtered = [l for l in filtered if l.product.price_cents >= min_price]
    
    if max_price is not None:
        filtered = [l for l in filtered if l.product.price_cents <= max_price]
    
    if min_rating is not None:
        filtered = [l for l in filtered if l.product.rating >= min_rating]
    
    return filtered
