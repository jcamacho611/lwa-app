from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ...core.config import Settings
from ...models.schemas import GenerationRequest, GenerationResponse


class BaseGenerationProvider(ABC):
    """Base class for all generation providers."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
    
    @abstractmethod
    async def generate_from_text(
        self,
        *,
        text_prompt: str,
        duration: Optional[float] = None,
        style: Optional[str] = None,
        aspect_ratio: str = "9:16",
        **kwargs: Any,
    ) -> GenerationResponse:
        """Generate video from text prompt."""
        pass
    
    @abstractmethod
    async def generate_from_image(
        self,
        *,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        duration: Optional[float] = None,
        motion_strength: str = "medium",
        **kwargs: Any,
    ) -> GenerationResponse:
        """Generate video from image."""
        pass
    
    @abstractmethod
    async def get_generation_status(self, *, generation_id: str) -> Dict[str, Any]:
        """Get status of ongoing generation."""
        pass
    
    @abstractmethod
    async def cancel_generation(self, *, generation_id: str) -> bool:
        """Cancel ongoing generation."""
        pass
