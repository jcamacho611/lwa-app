"""
Base Renderer Interface

Defines the abstract interface for video renderers in the LWA Video OS.
All renderers must implement this interface to be compatible with the video service.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from app.models.video_job import VideoJob


@dataclass
class RenderContext:
    """Context for video rendering operations."""
    
    job: VideoJob
    timeline: Optional[Dict[str, Any]] = None
    render_settings: Optional[Dict[str, Any]] = None
    output_path: Optional[str] = None
    temp_dir: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.render_settings is None:
            self.render_settings = {}


@dataclass
class RenderResult:
    """Result of video rendering operation."""
    
    success: bool
    output_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[float] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    render_time_seconds: Optional[float] = None
    
    @property
    def is_success(self) -> bool:
        """Check if render was successful."""
        return self.success and self.output_path is not None


class BaseRenderer(ABC):
    """
    Abstract base class for video renderers.
    
    All video renderers must inherit from this class and implement
    the required methods to be compatible with the LWA Video OS.
    """
    
    def __init__(self):
        """Initialize renderer."""
        self.name: str = ""
        self.display_name: str = ""
        self.version: str = ""
        self.capabilities: Dict[str, Any] = {}
    
    @abstractmethod
    async def render(self, context: RenderContext) -> RenderResult:
        """
        Render video based on the provided context.
        
        Args:
            context: Render context with job and configuration
            
        Returns:
            RenderResult with output information or error details
        """
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get renderer capabilities and configuration.
        
        Returns:
            Dictionary with renderer capabilities
        """
        pass
    
    @abstractmethod
    async def test_render(self, test_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Test renderer with a simple render operation.
        
        Args:
            test_config: Optional test configuration
            
        Returns:
            True if test render succeeds, False otherwise
        """
        pass
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate renderer configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if configuration is valid
        """
        # Default implementation - subclasses can override
        return True
    
    async def estimate_render_time(self, context: RenderContext) -> float:
        """
        Estimate render time for the given context.
        
        Args:
            context: Render context
            
        Returns:
            Estimated render time in seconds
        """
        # Default estimation based on duration
        if context.job.duration_seconds:
            return context.job.duration_seconds * 2.0  # 2x duration as rough estimate
        return 60.0  # Default 1 minute
    
    async def cleanup(self, context: RenderContext) -> None:
        """
        Clean up temporary files and resources.
        
        Args:
            context: Render context with temp directory info
        """
        # Default implementation - subclasses can override
        pass
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported output formats.
        
        Returns:
            List of supported format strings
        """
        return self.capabilities.get("formats", [])
    
    def get_supported_codecs(self) -> List[str]:
        """
        Get list of supported video codecs.
        
        Returns:
            List of supported codec strings
        """
        return self.capabilities.get("codecs", [])
    
    def supports_resolution(self, resolution: str) -> bool:
        """
        Check if renderer supports the given resolution.
        
        Args:
            resolution: Resolution string (e.g., "1080x1920")
            
        Returns:
            True if resolution is supported
        """
        max_res = self.capabilities.get("max_resolution", "1080x1920")
        # Simple resolution comparison - could be more sophisticated
        return resolution <= max_res
    
    def supports_duration(self, duration_seconds: float) -> bool:
        """
        Check if renderer supports the given duration.
        
        Args:
            duration_seconds: Duration in seconds
            
        Returns:
            True if duration is supported
        """
        max_duration = self.capabilities.get("max_duration", 3600)
        return duration_seconds <= max_duration
    
    async def get_render_progress(self, job_id: str) -> Optional[float]:
        """
        Get current render progress for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Progress percentage (0-100) or None if not available
        """
        # Default implementation - subclasses should override
        return None
    
    async def cancel_render(self, job_id: str) -> bool:
        """
        Cancel an ongoing render operation.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancellation was successful
        """
        # Default implementation - subclasses should override
        return False
    
    def __str__(self) -> str:
        """String representation of renderer."""
        return f"{self.display_name} v{self.version}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"<{self.__class__.__name__}: {self.name} v{self.version}>"
