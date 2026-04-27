from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..core.config import Settings

logger = logging.getLogger("uvicorn.error")


class SourceIngestService:
    """Service for ingesting video sources from URLs."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
    
    async def ingest_from_url(self, video_url: str) -> Dict[str, Any]:
        """Ingest video from URL and return metadata."""
        try:
            import yt_dlp

            if video_url and not video_url.startswith("http"):
                video_url = f"https://{video_url}"
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[height<=720]',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            }
            from ..processor import resolve_yt_cookie_file
            cookie_path = resolve_yt_cookie_file(self.settings)
            if cookie_path:
                ydl_opts["cookiefile"] = cookie_path
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                return {
                    "local_path": None,  # URL sources don't have local files
                    "title": info.get("title"),
                    "duration_seconds": info.get("duration"),
                    "webpage_url": info.get("webpage_url") or video_url,
                    "uploader": info.get("uploader"),
                }
                
        except Exception as error:
            logger.error(f"source_ingest_failed url={video_url} error={str(error)}")
            raise ValueError(f"Failed to ingest video from URL: {str(error)}")
