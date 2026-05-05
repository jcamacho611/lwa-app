"""
LWA Brain — Proof Events Service

Captures user behavior events for the data moat.
Tracks: generated, fallback_used, copied_hook, copied_caption, 
        saved_clip, exported_bundle, campaign_assigned

This is the foundation for learning from user behavior.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pathlib import Path


class ProofEventType(Enum):
    """Types of events that can be tracked."""
    GENERATE_STARTED = "generate_started"
    GENERATE_COMPLETED = "generate_completed"
    FALLBACK_USED = "fallback_used"
    CLIP_VIEWED = "clip_viewed"
    HOOK_COPIED = "hook_copied"
    CAPTION_COPIED = "caption_copied"
    CLIP_SAVED = "clip_saved"
    BUNDLE_EXPORTED = "bundle_exported"
    CAMPAIGN_OPENED = "campaign_opened"
    CAMPAIGN_ASSIGNED = "campaign_assigned"
    HISTORY_REOPENED = "history_reopened"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    ENHANCEMENT_FAILED = "enhancement_failed"


@dataclass
class ProofEvent:
    """
    A single proof event capturing user behavior.
    
    Each event includes:
    - request_id: ties to a generation run
    - clip_id: specific clip if applicable
    - event_type: what happened
    - timestamp: when it happened
    - source_type: text/url/file/etc
    - strategy_only: whether offline mode was used
    - platform_target: intended platform if known
    - metadata: additional context
    """
    event_type: ProofEventType
    request_id: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Optional clip-specific data
    clip_id: Optional[str] = None
    
    # Source and context
    source_type: Optional[str] = None  # text, url, file, idea
    strategy_only: bool = False
    platform_target: Optional[str] = None  # tiktok, instagram, youtube
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "request_id": self.request_id,
            "clip_id": self.clip_id,
            "timestamp": self.timestamp,
            "source_type": self.source_type,
            "strategy_only": self.strategy_only,
            "platform_target": self.platform_target,
            "metadata": self.metadata,
        }


class ProofEventStore:
    """
    Stores and retrieves proof events.
    
    Current implementation: file-based JSON storage.
    Future: can be upgraded to database backend.
    
    The event store is the foundation for:
    - User style memory
    - Feedback loops
    - Campaign intelligence
    - Future model training
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize event store.
        
        Args:
            storage_path: Directory to store event files.
                         Defaults to ./data/proof_events/
        """
        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "proof_events"
        
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory buffer for recent events
        self._buffer: List[ProofEvent] = []
        self._buffer_size = 100
    
    def _get_event_file(self, request_id: str) -> Path:
        """Get file path for a request's events."""
        # Organize by date for easier management
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        date_dir = self.storage_path / date_str
        date_dir.mkdir(exist_ok=True)
        
        return date_dir / f"{request_id}.jsonl"
    
    def record(self, event: ProofEvent) -> None:
        """
        Record a single proof event.
        
        Args:
            event: The event to record
        """
        # Add to buffer
        self._buffer.append(event)
        if len(self._buffer) > self._buffer_size:
            self._flush_buffer()
        
        # Also write immediately to file
        self._write_event(event)
    
    def _write_event(self, event: ProofEvent) -> None:
        """Write event to file storage."""
        try:
            file_path = self._get_event_file(event.request_id)
            
            with open(file_path, "a") as f:
                f.write(json.dumps(event.to_dict(), default=str) + "\n")
                
        except Exception as e:
            # Fail silently - events are important but not critical
            # In production, this should log to monitoring
            print(f"Failed to write proof event: {e}")
    
    def _flush_buffer(self) -> None:
        """Flush in-memory buffer to storage."""
        for event in self._buffer:
            self._write_event(event)
        self._buffer.clear()
    
    def get_events_for_request(self, request_id: str) -> List[ProofEvent]:
        """
        Get all events for a specific request.
        
        Args:
            request_id: The request to get events for
            
        Returns:
            List of events for the request
        """
        file_path = self._get_event_file(request_id)
        events = []
        
        if not file_path.exists():
            return events
        
        try:
            with open(file_path, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        events.append(ProofEvent(
                            event_type=ProofEventType(data["event_type"]),
                            request_id=data["request_id"],
                            clip_id=data.get("clip_id"),
                            timestamp=data["timestamp"],
                            source_type=data.get("source_type"),
                            strategy_only=data.get("strategy_only", False),
                            platform_target=data.get("platform_target"),
                            metadata=data.get("metadata", {}),
                        ))
        except Exception as e:
            print(f"Failed to read events: {e}")
        
        return events
    
    def get_user_behavior_summary(self, request_id: str) -> Dict[str, Any]:
        """
        Get a summary of user behavior for a request.
        
        Args:
            request_id: The request to summarize
            
        Returns:
            Summary dict with behavior metrics
        """
        events = self.get_events_for_request(request_id)
        
        if not events:
            return {"events_count": 0, "engaged": False}
        
        # Count event types
        event_counts = {}
        for event in events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Determine engagement level
        engagement_signals = [
            event_counts.get("hook_copied", 0),
            event_counts.get("caption_copied", 0),
            event_counts.get("clip_saved", 0),
            event_counts.get("bundle_exported", 0),
        ]
        engaged = sum(engagement_signals) > 0
        
        return {
            "events_count": len(events),
            "engaged": engaged,
            "event_breakdown": event_counts,
            "fallback_used": event_counts.get("fallback_used", 0) > 0,
            "strategy_only": events[0].strategy_only if events else False,
        }


# Convenience functions for common events

def record_generation_started(
    request_id: str,
    source_type: str,
    strategy_only: bool = False,
    platform_target: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record that a generation was started."""
    store = ProofEventStore()
    store.record(ProofEvent(
        event_type=ProofEventType.GENERATE_STARTED,
        request_id=request_id,
        source_type=source_type,
        strategy_only=strategy_only,
        platform_target=platform_target,
        metadata=metadata or {},
    ))


def record_generation_completed(
    request_id: str,
    clips_generated: int,
    fallback_used: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record that a generation was completed."""
    store = ProofEventStore()
    store.record(ProofEvent(
        event_type=ProofEventType.GENERATE_COMPLETED,
        request_id=request_id,
        strategy_only=not fallback_used,  # Strategy-only if no fallback
        metadata={
            "clips_generated": clips_generated,
            "fallback_used": fallback_used,
            **(metadata or {}),
        },
    ))


def record_fallback_used(
    request_id: str,
    reason: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record that fallback mode was used."""
    store = ProofEventStore()
    store.record(ProofEvent(
        event_type=ProofEventType.FALLBACK_USED,
        request_id=request_id,
        strategy_only=True,
        metadata={
            "reason": reason,
            **(metadata or {}),
        },
    ))


def record_hook_copied(
    request_id: str,
    clip_id: str,
    hook_text: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record that a hook was copied."""
    store = ProofEventStore()
    store.record(ProofEvent(
        event_type=ProofEventType.HOOK_COPIED,
        request_id=request_id,
        clip_id=clip_id,
        metadata={
            "hook_text": hook_text,
            **(metadata or {}),
        },
    ))


def record_caption_copied(
    request_id: str,
    clip_id: str,
    caption_text: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record that a caption was copied."""
    store = ProofEventStore()
    store.record(ProofEvent(
        event_type=ProofEventType.CAPTION_COPIED,
        request_id=request_id,
        clip_id=clip_id,
        metadata={
            "caption_text": caption_text,
            **(metadata or {}),
        },
    ))


def record_clip_saved(
    request_id: str,
    clip_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record that a clip was saved."""
    store = ProofEventStore()
    store.record(ProofEvent(
        event_type=ProofEventType.CLIP_SAVED,
        request_id=request_id,
        clip_id=clip_id,
        metadata=metadata or {},
    ))


def record_bundle_exported(
    request_id: str,
    export_format: str,
    clip_count: int,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record that a bundle was exported."""
    store = ProofEventStore()
    store.record(ProofEvent(
        event_type=ProofEventType.BUNDLE_EXPORTED,
        request_id=request_id,
        metadata={
            "export_format": export_format,
            "clip_count": clip_count,
            **(metadata or {}),
        },
    ))


def record_campaign_assigned(
    request_id: str,
    campaign_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record that clips were assigned to a campaign."""
    store = ProofEventStore()
    store.record(ProofEvent(
        event_type=ProofEventType.CAMPAIGN_ASSIGNED,
        request_id=request_id,
        metadata={
            "campaign_id": campaign_id,
            **(metadata or {}),
        },
    ))


# Singleton store for app-wide use
_event_store: Optional[ProofEventStore] = None


def get_event_store() -> ProofEventStore:
    """Get or create the singleton event store."""
    global _event_store
    if _event_store is None:
        _event_store = ProofEventStore()
    return _event_store
