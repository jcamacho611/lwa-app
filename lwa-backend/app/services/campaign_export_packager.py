"""
Campaign Export Packager v0

Creates comprehensive campaign packages for multi-platform distribution,
including calendars, asset organization, and platform-specific formatting.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger("uvicorn.error")


class Platform(str, Enum):
    """Target platforms for campaign distribution."""
    
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    YOUTUBE_SHORTS = "youtube_shorts"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"


@dataclass
class CampaignAsset:
    """Individual asset in a campaign."""
    
    id: str
    type: str  # video, image, caption, thumbnail
    file_path: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass
class PlatformPost:
    """Post configuration for a specific platform."""
    
    platform: Platform
    asset_id: str
    caption: str
    hashtags: List[str] = field(default_factory=list)
    scheduled_time: Optional[datetime] = None
    post_settings: Dict[str, any] = field(default_factory=dict)


@dataclass
class CampaignCalendar:
    """Campaign calendar with scheduled posts."""
    
    campaign_id: str
    posts: List[PlatformPost] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: str = "UTC"


@dataclass
class CampaignPackage:
    """Complete campaign package for export."""
    
    campaign_id: str
    name: str
    description: str
    assets: List[CampaignAsset] = field(default_factory=list)
    calendar: Optional[CampaignCalendar] = None
    platform_configs: Dict[Platform, Dict[str, any]] = field(default_factory=dict)
    export_metadata: Dict[str, any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class CampaignExportPackager:
    """
    Campaign export packager for multi-platform distribution.
    
    Creates comprehensive campaign packages with calendars,
    asset organization, and platform-specific formatting.
    """
    
    def __init__(self) -> None:
        self._platform_templates = self._build_platform_templates()
        self._hashtag_libraries = self._build_hashtag_libraries()
    
    def create_campaign_package(
        self,
        clips: List[Dict[str, any]],
        campaign_name: str,
        platforms: List[Platform],
        description: str = ""
    ) -> CampaignPackage:
        """
        Create a campaign package from clips.
        
        Args:
            clips: List of clip data
            campaign_name: Name for the campaign
            platforms: Target platforms
            description: Campaign description
            
        Returns:
            Complete CampaignPackage
        """
        campaign_id = f"campaign_{datetime.utcnow().timestamp()}"
        
        # Convert clips to assets
        assets = []
        for i, clip in enumerate(clips):
            asset = CampaignAsset(
                id=f"asset_{campaign_id}_{i}",
                type="video",
                url=clip.get("url"),
                metadata={
                    "duration": clip.get("duration"),
                    "hook": clip.get("hook"),
                    "score": clip.get("score"),
                }
            )
            assets.append(asset)
        
        # Build platform configurations
        platform_configs = {}
        for platform in platforms:
            platform_configs[platform] = self._platform_templates.get(platform, {})
        
        # Create calendar
        calendar = self._generate_campaign_calendar(assets, platforms)
        
        return CampaignPackage(
            campaign_id=campaign_id,
            name=campaign_name,
            description=description,
            assets=assets,
            calendar=calendar,
            platform_configs=platform_configs,
            export_metadata={
                "total_assets": len(assets),
                "platforms": [p.value for p in platforms],
                "created_by": "lwa_system",
            }
        )
    
    def generate_campaign_calendar(
        self,
        assets: List[CampaignAsset],
        platforms: List[Platform],
        start_date: Optional[datetime] = None,
        posts_per_day: int = 1
    ) -> CampaignCalendar:
        """
        Generate a campaign calendar with scheduled posts.
        
        Args:
            assets: Campaign assets
            platforms: Target platforms
            start_date: Campaign start date
            posts_per_day: Number of posts per day
            
        Returns:
            CampaignCalendar with scheduled posts
        """
        if not start_date:
            start_date = datetime.utcnow()
        
        campaign_id = f"calendar_{datetime.utcnow().timestamp()}"
        posts = []
        current_date = start_date
        asset_index = 0
        
        # Distribute assets across platforms and dates
        while asset_index < len(assets):
            for platform in platforms:
                if asset_index >= len(assets):
                    break
                
                asset = assets[asset_index]
                post = PlatformPost(
                    platform=platform,
                    asset_id=asset.id,
                    caption=self._generate_platform_caption(platform, asset),
                    hashtags=self._get_platform_hashtags(platform),
                    scheduled_time=current_date,
                    post_settings=self._platform_templates.get(platform, {})
                )
                posts.append(post)
                asset_index += 1
            
            current_date += timedelta(days=1)
        
        return CampaignCalendar(
            campaign_id=campaign_id,
            posts=posts,
            start_date=start_date,
            end_date=current_date,
            timezone="UTC"
        )
    
    def organize_assets_by_type(
        self,
        assets: List[CampaignAsset]
    ) -> Dict[str, List[CampaignAsset]]:
        """
        Organize campaign assets by type.
        
        Args:
            assets: List of campaign assets
            
        Returns:
            Dictionary mapping asset types to asset lists
        """
        organized = {}
        
        for asset in assets:
            if asset.type not in organized:
                organized[asset.type] = []
            organized[asset.type].append(asset)
        
        return organized
    
    def optimize_for_platform(
        self,
        asset: CampaignAsset,
        platform: Platform
    ) -> CampaignAsset:
        """
        Optimize asset for specific platform.
        
        Args:
            asset: Asset to optimize
            platform: Target platform
            
        Returns:
            Optimized asset
        """
        platform_config = self._platform_templates.get(platform, {})
        
        # Apply platform-specific optimizations
        optimized_metadata = asset.metadata.copy()
        optimized_metadata.update(platform_config.get("asset_optimizations", {}))
        
        return CampaignAsset(
            id=asset.id,
            type=asset.type,
            file_path=asset.file_path,
            url=asset.url,
            metadata=optimized_metadata
        )
    
    def generate_export_bundle(
        self,
        package: CampaignPackage,
        formats: List[str] = None
    ) -> Dict[str, any]:
        """
        Generate export bundle for campaign package.
        
        Args:
            package: Campaign package to export
            formats: Export formats (json, csv, etc.)
            
        Returns:
            Export bundle with formatted data
        """
        if formats is None:
            formats = ["json"]
        
        bundle = {
            "package": package,
            "formatted": {}
        }
        
        if "json" in formats:
            bundle["formatted"]["json"] = self._format_as_json(package)
        
        if "csv" in formats:
            bundle["formatted"]["csv"] = self._format_as_csv(package)
        
        return bundle
    
    def _generate_platform_caption(
        self,
        platform: Platform,
        asset: CampaignAsset
    ) -> str:
        """Generate platform-specific caption."""
        hook = asset.metadata.get("hook", "")
        
        platform_captions = {
            Platform.TIKTOK: f"{hook} #fyp #viral",
            Platform.INSTAGRAM_REELS: f"{hook} 🎬",
            Platform.YOUTUBE_SHORTS: f"{hook} 🔥",
            Platform.TWITTER: f"{hook}",
            Platform.LINKEDIN: f"{hook}. #professional",
            Platform.FACEBOOK: f"{hook}",
        }
        
        return platform_captions.get(platform, hook)
    
    def _get_platform_hashtags(self, platform: Platform) -> List[str]:
        """Get platform-specific hashtags."""
        return self._hashtag_libraries.get(platform, [])
    
    def _format_as_json(self, package: CampaignPackage) -> str:
        """Format package as JSON."""
        import json
        return json.dumps({
            "campaign_id": package.campaign_id,
            "name": package.name,
            "description": package.description,
            "assets": [
                {
                    "id": a.id,
                    "type": a.type,
                    "url": a.url,
                    "metadata": a.metadata
                }
                for a in package.assets
            ],
            "calendar": {
                "start_date": package.calendar.start_date.isoformat() if package.calendar else None,
                "end_date": package.calendar.end_date.isoformat() if package.calendar else None,
                "posts": [
                    {
                        "platform": p.platform.value,
                        "asset_id": p.asset_id,
                        "caption": p.caption,
                        "scheduled_time": p.scheduled_time.isoformat() if p.scheduled_time else None
                    }
                    for p in package.calendar.posts
                ] if package.calendar else []
            }
        }, indent=2)
    
    def _format_as_csv(self, package: CampaignPackage) -> str:
        """Format package as CSV."""
        lines = ["platform,asset_id,caption,scheduled_time"]
        
        if package.calendar:
            for post in package.calendar.posts:
                scheduled = post.scheduled_time.isoformat() if post.scheduled_time else ""
                lines.append(f"{post.platform.value},{post.asset_id},{post.caption},{scheduled}")
        
        return "\n".join(lines)
    
    def _build_platform_templates(self) -> Dict[Platform, Dict[str, any]]:
        """Build platform configuration templates."""
        return {
            Platform.TIKTOK: {
                "max_duration": 60,
                "aspect_ratio": "9:16",
                "file_format": "mp4",
                "asset_optimizations": {
                    "bitrate": "high",
                    "codec": "h264"
                }
            },
            Platform.INSTAGRAM_REELS: {
                "max_duration": 90,
                "aspect_ratio": "9:16",
                "file_format": "mp4",
                "asset_optimizations": {
                    "bitrate": "high",
                    "codec": "h264"
                }
            },
            Platform.YOUTUBE_SHORTS: {
                "max_duration": 60,
                "aspect_ratio": "9:16",
                "file_format": "mp4",
                "asset_optimizations": {
                    "bitrate": "high",
                    "codec": "h264"
                }
            },
            Platform.TWITTER: {
                "max_duration": 140,
                "aspect_ratio": "1:1",
                "file_format": "mp4",
                "asset_optimizations": {
                    "bitrate": "medium",
                    "codec": "h264"
                }
            },
            Platform.LINKEDIN: {
                "max_duration": 600,
                "aspect_ratio": "1:1",
                "file_format": "mp4",
                "asset_optimizations": {
                    "bitrate": "medium",
                    "codec": "h264"
                }
            },
            Platform.FACEBOOK: {
                "max_duration": 240,
                "aspect_ratio": "1:1",
                "file_format": "mp4",
                "asset_optimizations": {
                    "bitrate": "medium",
                    "codec": "h264"
                }
            },
        }
    
    def _build_hashtag_libraries(self) -> Dict[Platform, List[str]]:
        """Build platform hashtag libraries."""
        return {
            Platform.TIKTOK: ["#fyp", "#viral", "#trending"],
            Platform.INSTAGRAM_REELS: ["#reels", "#explore", "#viral"],
            Platform.YOUTUBE_SHORTS: ["#shorts", "#viral", "#trending"],
            Platform.TWITTER: [],
            Platform.LINKEDIN: ["#professional", "#business"],
            Platform.FACEBOOK: [],
        }


# Singleton instance
campaign_export_packager = CampaignExportPackager()
