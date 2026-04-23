from __future__ import annotations

import logging
from pathlib import Path
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
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[height<=720]',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            cookiefile = getattr(self.settings, "yt_dlp_cookiefile", None)
            if cookiefile and Path(cookiefile).exists():
                ydl_opts["cookiefile"] = cookiefile
                logger.info("source_ingest_cookiefile_loaded path=%s", cookiefile)
            else:
                logger.warning("source_ingest_cookiefile_missing youtube_may_block_server_requests=true")
            
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
