"""
Marketplace API Routes

Provides endpoints for marketplace functionality:
- Product listings
- Creator profiles
- Jobs and campaigns
- Orders and transactions
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ...services.marketplace_core import marketplace_core
from ...services.marketplace_core import ProductType, ProductStatus, OrderStatus

router = APIRouter(prefix="/v1/marketplace", tags=["marketplace"])

# Request/Response Models
class ProductListingRequest(BaseModel):
    name: str
    description: str
    product_type: str
    price: float
    preview_url: Optional[str] = None
    asset_urls: List[str] = []

class JobPostingRequest(BaseModel):
    title: str
    description: str
    campaign_type: str
    budget: float
    requirements: List[str] = []
    deadline: Optional[str] = None

class CreatorProfileRequest(BaseModel):
    display_name: str
    bio: str
    specialties: List[str] = []

# Products
@router.get("/products")
async def get_products(limit: int = 50, offset: int = 0, category: Optional[str] = None) -> Dict[str, Any]:
    """Get marketplace product listings."""
    try:
        products = marketplace_core.search_listings(
            query=category or "",
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "product_type": product.product_type.value,
                    "price": product.price,
                    "creator_name": product.creator_name,
                    "status": product.status.value,
                    "created_at": product.created_at.isoformat(),
                    "download_count": product.download_count,
                    "rating": product.rating,
                    "review_count": product.review_count,
                    "preview_url": product.preview_url,
                    "asset_urls": product.asset_urls
                }
                for product in products
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products")
async def create_product(request: ProductListingRequest) -> Dict[str, Any]:
    """Create a new product listing."""
    try:
        product_type = ProductType(request.product_type)
        
        product = marketplace_core.create_product_draft(
            name=request.name,
            description=request.description,
            product_type=product_type,
            price=request.price,
            creator_name="demo_creator",  # Would come from auth
            preview_url=request.preview_url,
            asset_urls=request.asset_urls
        )
        
        return {
            "success": True,
            "product_id": product.id,
            "status": product.status.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Jobs
@router.get("/jobs")
async def get_jobs(limit: int = 50, offset: int = 0, status: Optional[str] = None) -> Dict[str, Any]:
    """Get marketplace job postings."""
    try:
        # Mock job data for now
        jobs = [
            {
                "id": "job_1",
                "title": "TikTok Clip Creator Needed",
                "description": "Looking for experienced TikTok clip creator for gaming content",
                "campaign_type": "gaming",
                "budget": 500.0,
                "status": "active",
                "created_at": "2026-05-03T00:00:00Z",
                "deadline": "2026-05-10T00:00:00Z",
                "requirements": ["TikTok experience", "Gaming knowledge", "Fast turnaround"],
                "applicant_count": 12,
                "creator_profile": {
                    "display_name": "GameStudio",
                    "rating": 4.8
                }
            },
            {
                "id": "job_2", 
                "title": "YouTube Shorts Editor",
                "description": "Need editor for YouTube Shorts content creation",
                "campaign_type": "youtube",
                "budget": 300.0,
                "status": "active",
                "created_at": "2026-05-02T00:00:00Z",
                "deadline": "2026-05-08T00:00:00Z",
                "requirements": ["YouTube Shorts experience", "Quick editing"],
                "applicant_count": 8,
                "creator_profile": {
                    "display_name": "ContentCo",
                    "rating": 4.5
                }
            }
        ]
        
        return {
            "success": True,
            "jobs": jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs")
async def create_job(request: JobPostingRequest) -> Dict[str, Any]:
    """Create a new job posting."""
    try:
        # Mock job creation
        job_id = f"job_{hash(request.title)}"
        
        return {
            "success": True,
            "job_id": job_id,
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Creator Profiles
@router.get("/profiles")
async def get_creator_profiles(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Get creator profiles."""
    try:
        # Mock creator profile data
        profiles = [
            {
                "id": "creator_1",
                "display_name": "ClipMaster",
                "bio": "Expert video clip creator with 5+ years experience",
                "specialties": ["gaming", "tiktok", "youtube"],
                "rating": 4.9,
                "completed_jobs": 127,
                "earnings": {
                    "approved": 15420.0,
                    "pending": 2300.0
                },
                "status": "active"
            },
            {
                "id": "creator_2",
                "display_name": "EditPro",
                "bio": "Professional video editor specializing in short-form content",
                "specialties": ["editing", "youtube", "instagram"],
                "rating": 4.7,
                "completed_jobs": 89,
                "earnings": {
                    "approved": 11200.0,
                    "pending": 1800.0
                },
                "status": "active"
            }
        ]
        
        return {
            "success": True,
            "profiles": profiles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/profiles")
async def update_creator_profile(request: CreatorProfileRequest) -> Dict[str, Any]:
    """Update creator profile."""
    try:
        # Mock profile update
        return {
            "success": True,
            "message": "Profile updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Orders
@router.get("/orders")
async def get_orders(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Get user orders."""
    try:
        # Mock order data
        orders = [
            {
                "id": "order_1",
                "product_id": "product_1",
                "product_name": "Gaming Clip Pack",
                "amount": 29.99,
                "status": "completed",
                "created_at": "2026-05-01T00:00:00Z",
                "completed_at": "2026-05-01T01:00:00Z"
            }
        ]
        
        return {
            "success": True,
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Categories and Types
@router.get("/categories")
async def get_categories() -> Dict[str, List[str]]:
    """Get available product categories."""
    return {
        "categories": ["clip_packs", "caption_styles", "thumbnail_packs", "render_presets", "creator_workflows", "character_skins", "lee_wuh_merch", "brand_jobs", "campaign_packs"]
    }

@router.get("/product-types")
async def get_product_types() -> Dict[str, List[str]]:
    """Get available product types."""
    return {
        "types": [product_type.value for product_type in ProductType]
    }

# Health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Check health of marketplace system."""
    return {
        "status": "healthy",
        "services": "products, jobs, profiles, orders"
    }
