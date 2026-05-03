"""
Source Contract Normalizer v0

Normalizes source contracts across all input types to ensure
consistent handling and validation throughout the LWA system.
"""

import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..core.config import Settings
from ..models.schemas import ProcessRequest
from ..services.source_contract import normalize_source_type, classify_upload_source_type
from ..services.source_ingest import infer_source_type

logger = logging.getLogger("uvicorn.error")


class SourceInputType(str, Enum):
    """Types of source inputs."""
    
    UPLOAD_FILE = "upload_file"
    PUBLIC_URL = "public_url"
    PROMPT_ONLY = "prompt_only"
    CAMPAIGN_BRIEF = "campaign_brief"
    TEXT_INPUT = "text_input"
    MIXED_INPUT = "mixed_input"


class SourceValidationStatus(str, Enum):
    """Validation status for source inputs."""
    
    VALID = "valid"
    INVALID = "invalid"
    INCOMPLETE = "incomplete"
    UNSUPPORTED = "unsupported"
    RESTRICTED = "restricted"


@dataclass
class SourceValidationResult:
    """Result of source validation."""
    
    status: SourceValidationStatus
    input_type: SourceInputType
    source_type: str
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedSourceContract:
    """Normalized source contract for consistent processing."""
    
    input_type: SourceInputType
    source_type: str
    primary_source: str
    source_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_mode: str = "standard"
    fallback_strategy: str = "strategy_only"
    validation_result: Optional[SourceValidationResult] = None
    contract_version: str = "1.0"


class SourceContractNormalizer:
    """
    Normalizes source contracts across all input types.
    
    Ensures consistent handling and validation throughout the LWA system
    regardless of input method (upload, URL, prompt, etc.).
    """
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.supported_video_extensions = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
        self.supported_audio_extensions = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".flac"}
        self.supported_image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
        self.supported_text_extensions = {".txt", ".md"}
    
    async def normalize_request(
        self, request: ProcessRequest, upload_info: Optional[Dict[str, Any]] = None
    ) -> NormalizedSourceContract:
        """
        Normalize a ProcessRequest into a standardized source contract.
        
        Args:
            request: The original ProcessRequest
            upload_info: Optional upload metadata if file was uploaded
            
        Returns:
            NormalizedSourceContract with standardized fields
        """
        
        try:
            # Determine input type
            input_type = self._determine_input_type(request, upload_info)
            
            # Validate the input
            validation_result = await self._validate_input(request, upload_info, input_type)
            
            # Normalize source type
            source_type = self._normalize_source_type(request, upload_info, input_type)
            
            # Extract primary source
            primary_source = self._extract_primary_source(request, upload_info, input_type)
            
            # Build source metadata
            source_metadata = self._build_source_metadata(request, upload_info, input_type)
            
            # Determine processing mode
            processing_mode = self._determine_processing_mode(input_type, source_type, validation_result)
            
            # Determine fallback strategy
            fallback_strategy = self._determine_fallback_strategy(input_type, source_type, validation_result)
            
            contract = NormalizedSourceContract(
                input_type=input_type,
                source_type=source_type,
                primary_source=primary_source,
                source_metadata=source_metadata,
                processing_mode=processing_mode,
                fallback_strategy=fallback_strategy,
                validation_result=validation_result,
                contract_version="1.0"
            )
            
            logger.info(
                "source_contract_normalized input_type=%s source_type=%s processing_mode=%s fallback=%s",
                input_type.value,
                source_type,
                processing_mode,
                fallback_strategy
            )
            
            return contract
            
        except Exception as error:
            logger.error(f"source_contract_normalization_failed error={str(error)}")
            
            # Return emergency fallback contract
            return self._emergency_fallback_contract(request, str(error))
    
    def _determine_input_type(
        self, request: ProcessRequest, upload_info: Optional[Dict[str, Any]]
    ) -> SourceInputType:
        """Determine the type of input based on request and upload info."""
        
        # Upload file takes precedence
        if upload_info or request.upload_file_id or request.uploaded_file_ref:
            return SourceInputType.UPLOAD_FILE
        
        # Check for campaign brief
        if request.campaign_brief and len(request.campaign_brief.strip()) > 0:
            return SourceInputType.CAMPAIGN_BRIEF
        
        # Check for URL input
        if request.video_url or request.source_url:
            return SourceInputType.PUBLIC_URL
        
        # Check for prompt input
        if request.prompt or request.text_prompt:
            return SourceInputType.PROMPT_ONLY
        
        # Check for mixed text input
        text_fields = [
            request.content_angle,
            request.selected_trend,
            request.campaign_goal
        ]
        if any(field and len(field.strip()) > 0 for field in text_fields):
            return SourceInputType.TEXT_INPUT
        
        # Default to mixed input (incomplete)
        return SourceInputType.MIXED_INPUT
    
    async def _validate_input(
        self, request: ProcessRequest, upload_info: Optional[Dict[str, Any]], input_type: SourceInputType
    ) -> SourceValidationResult:
        """Validate the input and return validation result."""
        
        errors = []
        warnings = []
        
        if input_type == SourceInputType.UPLOAD_FILE:
            validation_errors, validation_warnings = self._validate_upload_input(request, upload_info)
            errors.extend(validation_errors)
            warnings.extend(validation_warnings)
        
        elif input_type == SourceInputType.PUBLIC_URL:
            validation_errors, validation_warnings = self._validate_url_input(request)
            errors.extend(validation_errors)
            warnings.extend(validation_warnings)
        
        elif input_type == SourceInputType.PROMPT_ONLY:
            validation_errors, validation_warnings = self._validate_prompt_input(request)
            errors.extend(validation_errors)
            warnings.extend(validation_warnings)
        
        elif input_type == SourceInputType.CAMPAIGN_BRIEF:
            validation_errors, validation_warnings = self._validate_campaign_input(request)
            errors.extend(validation_errors)
            warnings.extend(validation_warnings)
        
        elif input_type == SourceInputType.TEXT_INPUT:
            validation_errors, validation_warnings = self._validate_text_input(request)
            errors.extend(validation_errors)
            warnings.extend(validation_warnings)
        
        else:  # MIXED_INPUT or unknown
            errors.append("Incomplete input: please provide a file, URL, prompt, or campaign brief")
        
        # Determine status
        if errors:
            status = SourceValidationStatus.INVALID if "unsupported" in str(errors).lower() else SourceValidationStatus.INCOMPLETE
        elif warnings:
            status = SourceValidationStatus.VALID  # Valid with warnings
        else:
            status = SourceValidationStatus.VALID
        
        # Infer source type for validation
        source_type = self._normalize_source_type(request, upload_info, input_type)
        
        return SourceValidationResult(
            status=status,
            input_type=input_type,
            source_type=source_type,
            validation_errors=errors,
            warnings=warnings,
            metadata={
                "validation_timestamp": "now",
                "input_complexity": self._assess_input_complexity(request, upload_info)
            }
        )
    
    def _validate_upload_input(
        self, request: ProcessRequest, upload_info: Optional[Dict[str, Any]]
    ) -> tuple[List[str], List[str]]:
        """Validate upload file input."""
        
        errors = []
        warnings = []
        
        if not upload_info and not request.upload_file_id and not request.uploaded_file_ref:
            errors.append("Upload file reference is missing")
            return errors, warnings
        
        # Check file extension
        filename = upload_info.get("file_name") if upload_info else ""
        content_type = upload_info.get("content_type") if upload_info else request.upload_content_type
        
        if filename:
            file_ext = Path(filename).suffix.lower()
            if file_ext not in self.supported_video_extensions | self.supported_audio_extensions | self.supported_image_extensions:
                errors.append(f"Unsupported file extension: {file_ext}")
        
        # Check content type
        if content_type:
            content_prefix = content_type.split("/")[0].lower()
            if content_prefix not in ["video", "audio", "image"]:
                warnings.append(f"Unusual content type: {content_type}")
        
        # Check file size
        if upload_info and "file_size" in upload_info:
            file_size = upload_info["file_size"]
            max_size_mb = getattr(self.settings, "max_upload_mb", 500)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                errors.append(f"File too large: {file_size} bytes (max: {max_size_bytes} bytes)")
            elif file_size > max_size_bytes * 0.8:
                warnings.append("Large file may take longer to process")
        
        return errors, warnings
    
    def _validate_url_input(self, request: ProcessRequest) -> tuple[List[str], List[str]]:
        """Validate public URL input."""
        
        errors = []
        warnings = []
        
        url = request.video_url or request.source_url
        
        if not url:
            errors.append("URL is required for public URL input")
            return errors, warnings
        
        # Basic URL validation
        if not url.startswith(("http://", "https://")):
            warnings.append("URL should start with http:// or https://")
        
        # Check for known problematic platforms
        url_lower = url.lower()
        problematic_platforms = ["facebook.com/private", "instagram.com/private", "tiktok.com/private"]
        
        for platform in problematic_platforms:
            if platform in url_lower:
                warnings.append(f"Private/{platform.split('/')[0]} content may not be accessible")
        
        return errors, warnings
    
    def _validate_prompt_input(self, request: ProcessRequest) -> tuple[List[str], List[str]]:
        """Validate prompt-only input."""
        
        errors = []
        warnings = []
        
        prompt = request.prompt or request.text_prompt
        
        if not prompt or len(prompt.strip()) == 0:
            errors.append("Prompt is required for prompt-only input")
            return errors, warnings
        
        # Check prompt length
        prompt_length = len(prompt.strip())
        if prompt_length < 10:
            warnings.append("Very short prompt may produce limited results")
        elif prompt_length > 2000:
            warnings.append("Very long prompt may be truncated")
        
        # Check for potentially problematic content
        prompt_lower = prompt.lower()
        risky_terms = ["guaranteed", "risk free", "passive income", "investment advice"]
        
        for term in risky_terms:
            if term in prompt_lower:
                warnings.append(f"Potentially risky term detected: {term}")
        
        return errors, warnings
    
    def _validate_campaign_input(self, request: ProcessRequest) -> tuple[List[str], List[str]]:
        """Validate campaign brief input."""
        
        errors = []
        warnings = []
        
        brief = request.campaign_brief
        
        if not brief or len(brief.strip()) == 0:
            errors.append("Campaign brief is required for campaign input")
            return errors, warnings
        
        # Check brief length
        brief_length = len(brief.strip())
        if brief_length < 20:
            warnings.append("Brief campaign description may produce limited results")
        
        # Check for campaign goal
        if not request.campaign_goal or len(request.campaign_goal.strip()) == 0:
            warnings.append("Campaign goal not specified, using defaults")
        
        return errors, warnings
    
    def _validate_text_input(self, request: ProcessRequest) -> tuple[List[str], List[str]]:
        """Validate text-only input."""
        
        errors = []
        warnings = []
        
        text_fields = [
            request.content_angle,
            request.selected_trend,
            request.campaign_goal
        ]
        
        has_content = any(field and len(field.strip()) > 0 for field in text_fields)
        
        if not has_content:
            errors.append("At least one text field is required for text input")
        
        return errors, warnings
    
    def _normalize_source_type(
        self, request: ProcessRequest, upload_info: Optional[Dict[str, Any]], input_type: SourceInputType
    ) -> str:
        """Normalize source type based on input and metadata."""
        
        if input_type == SourceInputType.UPLOAD_FILE:
            if upload_info:
                return classify_upload_source_type(
                    filename=upload_info.get("file_name", ""),
                    content_type=upload_info.get("content_type", "")
                )
            elif request.upload_content_type:
                return classify_upload_source_type(
                    filename="",
                    content_type=request.upload_content_type
                )
        
        elif input_type == SourceInputType.PUBLIC_URL:
            return infer_source_type(request)
        
        elif input_type in [SourceInputType.PROMPT_ONLY, SourceInputType.CAMPAIGN_BRIEF]:
            return "prompt"
        
        elif input_type == SourceInputType.TEXT_INPUT:
            return "prompt"
        
        # Fallback to request's source_type or infer
        explicit_type = request.source_type
        if explicit_type:
            return normalize_source_type(explicit_type)
        
        return infer_source_type(request)
    
    def _extract_primary_source(
        self, request: ProcessRequest, upload_info: Optional[Dict[str, Any]], input_type: SourceInputType
    ) -> str:
        """Extract the primary source value from the request."""
        
        if input_type == SourceInputType.UPLOAD_FILE:
            if upload_info and "public_url" in upload_info:
                return upload_info["public_url"]
            return "uploaded_file"
        
        elif input_type == SourceInputType.PUBLIC_URL:
            return request.video_url or request.source_url or ""
        
        elif input_type == SourceInputType.PROMPT_ONLY:
            return request.prompt or request.text_prompt or ""
        
        elif input_type == SourceInputType.CAMPAIGN_BRIEF:
            return request.campaign_brief or ""
        
        elif input_type == SourceInputType.TEXT_INPUT:
            # Combine text fields
            parts = []
            for field in [request.content_angle, request.selected_trend, request.campaign_goal]:
                if field and len(field.strip()) > 0:
                    parts.append(field.strip())
            return " | ".join(parts)
        
        return "unknown_source"
    
    def _build_source_metadata(
        self, request: ProcessRequest, upload_info: Optional[Dict[str, Any]], input_type: SourceInputType
    ) -> Dict[str, Any]:
        """Build comprehensive source metadata."""
        
        metadata = {
            "input_type": input_type.value,
            "original_request": {
                "target_platform": request.target_platform,
                "clip_count": request.clip_count,
                "content_angle": request.content_angle,
                "selected_trend": request.selected_trend,
                "allowed_platforms": request.allowed_platforms,
                "source_metadata": request.source_metadata or {}
            }
        }
        
        if input_type == SourceInputType.UPLOAD_FILE and upload_info:
            metadata.update({
                "upload_info": {
                    "file_name": upload_info.get("file_name"),
                    "file_size": upload_info.get("file_size"),
                    "content_type": upload_info.get("content_type"),
                    "upload_timestamp": upload_info.get("created_at")
                }
            })
        
        elif input_type == SourceInputType.PUBLIC_URL:
            metadata.update({
                "url_info": {
                    "url": request.video_url or request.source_url,
                    "url_type": "video" if request.video_url else "general"
                }
            })
        
        elif input_type == SourceInputType.PROMPT_ONLY:
            metadata.update({
                "prompt_info": {
                    "prompt_length": len(request.prompt or request.text_prompt or ""),
                    "has_content_angle": bool(request.content_angle),
                    "has_trend": bool(request.selected_trend)
                }
            })
        
        elif input_type == SourceInputType.CAMPAIGN_BRIEF:
            metadata.update({
                "campaign_info": {
                    "brief_length": len(request.campaign_brief or ""),
                    "campaign_goal": request.campaign_goal,
                    "allowed_platforms_count": len(request.allowed_platforms or [])
                }
            })
        
        return metadata
    
    def _determine_processing_mode(
        self, input_type: SourceInputType, source_type: str, validation_result: SourceValidationResult
    ) -> str:
        """Determine the optimal processing mode."""
        
        if validation_result.status == SourceValidationStatus.INVALID:
            return "emergency_fallback"
        
        if input_type in [SourceInputType.PROMPT_ONLY, SourceInputType.CAMPAIGN_BRIEF]:
            return "strategy_only"
        
        if source_type in ["video_upload", "audio_upload", "image_upload"]:
            return "media_processing"
        
        if source_type in ["url", "video", "audio"]:
            return "url_ingest"
        
        return "standard"
    
    def _determine_fallback_strategy(
        self, input_type: SourceInputType, source_type: str, validation_result: SourceValidationResult
    ) -> str:
        """Determine the fallback strategy."""
        
        if validation_result.status == SourceValidationStatus.INVALID:
            return "emergency_degraded"
        
        if input_type in [SourceInputType.PROMPT_ONLY, SourceInputType.CAMPAIGN_BRIEF]:
            return "user_provided"
        
        if validation_result.warnings:
            return "enhanced_fallback"
        
        return "standard_processing"
    
    def _assess_input_complexity(
        self, request: ProcessRequest, upload_info: Optional[Dict[str, Any]]
    ) -> str:
        """Assess the complexity of the input."""
        
        complexity_score = 0
        
        # Upload files add complexity
        if upload_info:
            complexity_score += 2
        
        # URLs add complexity
        if request.video_url or request.source_url:
            complexity_score += 2
        
        # Campaign briefs add complexity
        if request.campaign_brief:
            complexity_score += 3
        
        # Multiple text fields add complexity
        text_fields = [request.content_angle, request.selected_trend, request.campaign_goal]
        if sum(1 for field in text_fields if field and len(field.strip()) > 0) > 1:
            complexity_score += 1
        
        # Platform restrictions add complexity
        if request.allowed_platforms and len(request.allowed_platforms) > 0:
            complexity_score += 1
        
        if complexity_score >= 5:
            return "high"
        elif complexity_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _emergency_fallback_contract(self, request: ProcessRequest, error: str) -> NormalizedSourceContract:
        """Create emergency fallback contract when normalization fails."""
        
        logger.error(f"emergency_source_contract_created error={error}")
        
        return NormalizedSourceContract(
            input_type=SourceInputType.MIXED_INPUT,
            source_type="emergency",
            primary_source="emergency_fallback",
            processing_mode="emergency",
            fallback_strategy="emergency_degraded",
            validation_result=SourceValidationResult(
                status=SourceValidationStatus.INVALID,
                input_type=SourceInputType.MIXED_INPUT,
                source_type="emergency",
                validation_errors=[f"Emergency fallback: {error}"],
                warnings=["System experienced errors during source normalization"]
            ),
            source_metadata={"emergency_fallback": True, "original_error": error}
        )


# Singleton instance
source_contract_normalizer = lambda settings: SourceContractNormalizer(settings)
