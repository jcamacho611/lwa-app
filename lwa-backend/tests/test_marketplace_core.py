import unittest

from app.services.marketplace_core import (
    MarketplaceProductDraft,
    ProductStatus,
    ProductType,
    calculate_platform_fee,
    create_product_draft,
    public_marketplace_disclosure,
    quote_order,
)


def test_create_product_draft_uses_integer_cents() -> None:
    product = create_product_draft(
        MarketplaceProductDraft(
            seller_id="seller-1",
            product_type=ProductType.HOOK_PACK,
            title="Hook Pack",
            description="Hooks for short-form clips.",
            price_cents=2500,
        )
    )

    assert product.price_cents == 2500
    assert product.status == ProductStatus.DRAFT


def test_marketplace_rejects_float_money() -> None:
    with unittest.TestCase().assertRaises(ValueError):
        calculate_platform_fee(19.99)  # type: ignore[arg-type]


def test_marketplace_rejects_banned_category() -> None:
    with unittest.TestCase().assertRaises(ValueError):
        create_product_draft(
            MarketplaceProductDraft(
                seller_id="seller-1",
                product_type=ProductType.PROMPT_PACK,
                title="Bad Listing",
                description="Not allowed.",
                price_cents=1000,
                category="get rich quick",
            )
        )


def test_clip_commission_forces_disclosure() -> None:
    product = create_product_draft(
        MarketplaceProductDraft(
            seller_id="seller-1",
            product_type=ProductType.CLIP_COMMISSION,
            title="Clip commission",
            description="Manual review and posting package.",
            price_cents=5000,
        )
    )

    assert product.ftc_disclosure_required is True


def test_quote_order_requires_listed_product() -> None:
    product = create_product_draft(
        MarketplaceProductDraft(
            seller_id="seller-1",
            product_type=ProductType.TEMPLATE,
            title="Template",
            description="A template.",
            price_cents=1000,
        )
    )

    with unittest.TestCase().assertRaises(ValueError):
        quote_order(product=product, buyer_id="buyer-1")


def test_quote_order_uses_basis_points_fee() -> None:
    draft_product = create_product_draft(
        MarketplaceProductDraft(
            seller_id="seller-1",
            product_type=ProductType.TEMPLATE,
            title="Template",
            description="A template.",
            price_cents=1000,
        )
    )
    product = draft_product.__class__(**{**draft_product.__dict__, "status": ProductStatus.LISTED})
    quote = quote_order(product=product, buyer_id="buyer-1", fee_bps=1000)

    assert quote.platform_fee_cents == 100
    assert quote.seller_receives_cents == 900


def test_disclosure_never_promises_income() -> None:
    disclosure = public_marketplace_disclosure().lower()

    assert "no guarantee" in disclosure
    assert "income" in disclosure
