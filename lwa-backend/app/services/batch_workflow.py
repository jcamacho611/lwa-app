from __future__ import annotations

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class WorkflowItemType(Enum):
    """Types of workflow items."""
    SOURCE_ASSET = "source_asset"
    CLIP = "clip"
    TIMELINE_PLAN = "timeline_plan"
    RENDER_JOB = "render_job"
    CAPTION_TRACK = "caption_track"
    AUDIO_PLAN = "audio_plan"
    EXPORT_PACKAGE = "export_package"
    MASTERPIECE_PLAN = "masterpiece_plan"
    PROOF_ASSET = "proof_asset"


class WorkflowStatus(Enum):
    """Status of workflow items."""
    NEW = "new"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CHANGES = "needs_changes"
    QUEUED_FOR_RENDER = "queued_for_render"
    RENDERING = "rendering"
    RENDERED = "rendered"
    PACKAGED = "packaged"
    SAVED_AS_PROOF = "saved_as_proof"
    POSTED = "posted"
    ARCHIVED = "archived"
    FAILED = "failed"


class WorkflowActionType(Enum):
    """Types of workflow actions."""
    APPROVE = "approve"
    REJECT = "reject"
    MARK_NEEDS_CHANGES = "mark_needs_changes"
    QUEUE_RENDER = "queue_render"
    ADD_CAPTION = "add_caption"
    ADD_AUDIO = "add_audio"
    PACKAGE = "package"
    SAVE_AS_PROOF = "save_as_proof"
    MARK_SALES_ASSET = "mark_sales_asset"
    MARK_TRUST_ASSET = "mark_trust_asset"
    MARK_ATTENTION_ASSET = "mark_attention_asset"
    CREATE_NEXT_ACTION = "create_next_action"
    ARCHIVE = "archive"


@dataclass
class BatchWorkflowItem:
    """A workflow item for batch review."""
    item_id: str
    user_id: str
    item_type: WorkflowItemType
    status: WorkflowStatus
    title: str
    description: Optional[str] = None
    external_ref: Optional[str] = None  # clip_id, source_asset_id, timeline_id, etc.
    external_type: Optional[str] = None
    platform: Optional[str] = None
    goal: Optional[str] = None
    best_use_case: Optional[str] = None
    score_confidence: Optional[float] = None
    target_platform: Optional[str] = None
    linked_asset_ids: List[str] = field(default_factory=list)
    available_actions: List[WorkflowActionType] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class BatchWorkflowAction:
    """A workflow action performed on an item."""
    action_id: str
    item_id: str
    user_id: str
    action_type: WorkflowActionType
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class BatchWorkflowFilter:
    """Filter for workflow items."""
    item_types: Optional[List[WorkflowItemType]] = None
    statuses: Optional[List[WorkflowStatus]] = None
    platforms: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    ready_to_render: Optional[bool] = None
    needs_review: Optional[bool] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None


@dataclass
class BatchWorkflowSummary:
    """Summary of workflow items."""
    total_items: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_platform: Dict[str, int]
    ready_to_render: int
    needs_review: int
    approved_items: int
    rejected_items: int
    avg_score_confidence: Optional[float] = None


class BatchWorkflowEngine:
    """Service for batch workflow management."""
    
    def __init__(self) -> None:
        self._items: Dict[str, BatchWorkflowItem] = {}  # In-memory storage for v0
        self._actions: Dict[str, BatchWorkflowAction] = {}  # In-memory storage for v0
    
    def create_workflow_item(
        self, 
        item_type: WorkflowItemType,
        title: str,
        user_id: str = "guest:unknown",
        external_ref: Optional[str] = None,
        external_type: Optional[str] = None,
        platform: Optional[str] = None,
        goal: Optional[str] = None,
        best_use_case: Optional[str] = None,
        score_confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BatchWorkflowItem:
        """Create a new workflow item."""
        item_id = f"workflow_{uuid4().hex}"
        
        # Determine available actions based on item type and status
        available_actions = self._get_available_actions(item_type, WorkflowStatus.NEW)
        
        item = BatchWorkflowItem(
            item_id=item_id,
            user_id=user_id,
            item_type=item_type,
            status=WorkflowStatus.NEW,
            title=title,
            external_ref=external_ref,
            external_type=external_type,
            platform=platform,
            goal=goal,
            best_use_case=best_use_case,
            score_confidence=score_confidence,
            target_platform=platform,
            available_actions=available_actions,
            metadata=metadata
        )
        
        self._items[item_id] = item
        return item
    
    def get_workflow_item(self, item_id: str) -> Optional[BatchWorkflowItem]:
        """Get a workflow item by ID."""
        return self._items.get(item_id)
    
    def list_workflow_items(
        self, 
        user_id: Optional[str] = None,
        filter_obj: Optional[BatchWorkflowFilter] = None
    ) -> List[BatchWorkflowItem]:
        """List workflow items with optional filtering."""
        items = list(self._items.values())
        
        # Filter by user
        if user_id:
            items = [item for item in items if item.user_id == user_id]
        
        # Apply additional filters
        if filter_obj:
            if filter_obj.item_types:
                items = [item for item in items if item.item_type in filter_obj.item_types]
            if filter_obj.statuses:
                items = [item for item in items if item.status in filter_obj.statuses]
            if filter_obj.platforms:
                items = [item for item in items if item.platform in filter_obj.platforms]
            if filter_obj.goals:
                items = [item for item in items if item.goal in filter_obj.goals]
            if filter_obj.ready_to_render is not None:
                render_ready_statuses = [WorkflowStatus.APPROVED, WorkflowStatus.QUEUED_FOR_RENDER]
                items = [item for item in items if (item.status in render_ready_statuses) == filter_obj.ready_to_render]
            if filter_obj.needs_review is not None:
                review_statuses = [WorkflowStatus.NEW, WorkflowStatus.NEEDS_CHANGES]
                items = [item for item in items if (item.status in review_statuses) == filter_obj.needs_review]
        
        # Sort by created_at descending
        items.sort(key=lambda x: x.created_at, reverse=True)
        return items
    
    def execute_workflow_action(
        self,
        item_id: str,
        action_type: WorkflowActionType,
        user_id: str = "guest:unknown",
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BatchWorkflowAction:
        """Execute a workflow action on an item."""
        item = self.get_workflow_item(item_id)
        if not item:
            raise ValueError(f"Workflow item {item_id} not found")
        
        # Check if action is available
        if action_type not in item.available_actions:
            raise ValueError(f"Action {action_type} not available for item {item_id}")
        
        # Create action record
        action = BatchWorkflowAction(
            action_id=f"action_{uuid4().hex}",
            item_id=item_id,
            user_id=user_id,
            action_type=action_type,
            notes=notes,
            metadata=metadata
        )
        
        self._actions[action.action_id] = action
        
        # Update item status based on action
        new_status = self._get_status_from_action(action_type, item.status)
        if new_status:
            item.status = new_status
            item.updated_at = datetime.utcnow().isoformat()
        
        # Update available actions based on new status
        item.available_actions = self._get_available_actions(item.item_type, item.status)
        
        return action
    
    def bulk_execute_workflow_action(
        self,
        item_ids: List[str],
        action_type: WorkflowActionType,
        user_id: str = "guest:unknown",
        notes: Optional[str] = None
    ) -> List[BatchWorkflowAction]:
        """Execute a workflow action on multiple items."""
        actions = []
        for item_id in item_ids:
            try:
                action = self.execute_workflow_action(item_id, action_type, user_id, notes)
                actions.append(action)
            except ValueError as e:
                # Log error but continue with other items
                print(f"Failed to execute action on {item_id}: {e}")
        
        return actions
    
    def get_workflow_summary(self, user_id: Optional[str] = None) -> BatchWorkflowSummary:
        """Get summary statistics for workflow items."""
        items = self.list_workflow_items(user_id)
        
        # Count by status
        by_status = {}
        for status in WorkflowStatus:
            by_status[status.value] = len([item for item in items if item.status == status])
        
        # Count by type
        by_type = {}
        for item_type in WorkflowItemType:
            by_type[item_type.value] = len([item for item in items if item.item_type == item_type])
        
        # Count by platform
        by_platform = {}
        platforms = set(item.platform for item in items if item.platform)
        for platform in platforms:
            if platform:
                by_platform[platform] = len([item for item in items if item.platform == platform])
        
        # Special counts
        render_ready_statuses = [WorkflowStatus.APPROVED, WorkflowStatus.QUEUED_FOR_RENDER]
        ready_to_render = len([item for item in items if item.status in render_ready_statuses])
        
        review_statuses = [WorkflowStatus.NEW, WorkflowStatus.NEEDS_CHANGES]
        needs_review = len([item for item in items if item.status in review_statuses])
        
        approved_items = len([item for item in items if item.status == WorkflowStatus.APPROVED])
        rejected_items = len([item for item in items if item.status == WorkflowStatus.REJECTED])
        
        # Average confidence score
        scores = [item.score_confidence for item in items if item.score_confidence is not None]
        avg_score_confidence = sum(scores) / len(scores) if scores else None
        
        return BatchWorkflowSummary(
            total_items=len(items),
            by_status=by_status,
            by_type=by_type,
            by_platform=by_platform,
            ready_to_render=ready_to_render,
            needs_review=needs_review,
            approved_items=approved_items,
            rejected_items=rejected_items,
            avg_score_confidence=avg_score_confidence
        )
    
    def delete_workflow_item(self, item_id: str) -> bool:
        """Delete a workflow item."""
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False
    
    def get_item_actions(self, item_id: str) -> List[BatchWorkflowAction]:
        """Get all actions for a workflow item."""
        return [action for action in self._actions.values() if action.item_id == item_id]
    
    def _get_available_actions(self, item_type: WorkflowItemType, status: WorkflowStatus) -> List[WorkflowActionType]:
        """Get available actions based on item type and status."""
        actions = []
        
        # Base actions available for most items
        if status == WorkflowStatus.NEW:
            actions.extend([
                WorkflowActionType.APPROVE,
                WorkflowActionType.REJECT,
                WorkflowActionType.MARK_NEEDS_CHANGES,
                WorkflowActionType.ARCHIVE
            ])
        
        if status == WorkflowStatus.NEEDS_CHANGES:
            actions.extend([
                WorkflowActionType.APPROVE,
                WorkflowActionType.REJECT,
                WorkflowActionType.ARCHIVE
            ])
        
        if status == WorkflowStatus.APPROVED:
            actions.extend([
                WorkflowActionType.QUEUE_RENDER,
                WorkflowActionType.PACKAGE,
                WorkflowActionType.SAVE_AS_PROOF,
                WorkflowActionType.MARK_SALES_ASSET,
                WorkflowActionType.MARK_TRUST_ASSET,
                WorkflowActionType.MARK_ATTENTION_ASSET,
                WorkflowActionType.ARCHIVE
            ])
        
        if status == WorkflowStatus.QUEUED_FOR_RENDER:
            actions.extend([
                WorkflowActionType.ARCHIVE
            ])
        
        if status == WorkflowStatus.RENDERED:
            actions.extend([
                WorkflowActionType.PACKAGE,
                WorkflowActionType.SAVE_AS_PROOF,
                WorkflowActionType.MARK_SALES_ASSET,
                WorkflowActionType.MARK_TRUST_ASSET,
                WorkflowActionType.MARK_ATTENTION_ASSET,
                WorkflowActionType.ARCHIVE
            ])
        
        if status == WorkflowStatus.PACKAGED:
            actions.extend([
                WorkflowActionType.SAVE_AS_PROOF,
                WorkflowActionType.MARK_SALES_ASSET,
                WorkflowActionType.MARK_TRUST_ASSET,
                WorkflowActionType.MARK_ATTENTION_ASSET,
                WorkflowActionType.ARCHIVE
            ])
        
        # Type-specific actions
        if item_type in [WorkflowItemType.CLIP, WorkflowItemType.TIMELINE_PLAN]:
            if status in [WorkflowStatus.NEW, WorkflowStatus.NEEDS_CHANGES]:
                actions.append(WorkflowActionType.ADD_CAPTION)
            if status in [WorkflowStatus.NEW, WorkflowStatus.NEEDS_CHANGES]:
                actions.append(WorkflowActionType.ADD_AUDIO)
        
        # Always allow creating next action
        actions.append(WorkflowActionType.CREATE_NEXT_ACTION)
        
        return actions
    
    def _get_status_from_action(self, action: WorkflowActionType, current_status: WorkflowStatus) -> Optional[WorkflowStatus]:
        """Get new status based on action."""
        status_mapping = {
            WorkflowActionType.APPROVE: WorkflowStatus.APPROVED,
            WorkflowActionType.REJECT: WorkflowStatus.REJECTED,
            WorkflowActionType.MARK_NEEDS_CHANGES: WorkflowStatus.NEEDS_CHANGES,
            WorkflowActionType.QUEUE_RENDER: WorkflowStatus.QUEUED_FOR_RENDER,
            WorkflowActionType.PACKAGE: WorkflowStatus.PACKAGED,
            WorkflowActionType.SAVE_AS_PROOF: WorkflowStatus.SAVED_AS_PROOF,
            WorkflowActionType.ARCHIVE: WorkflowStatus.ARCHIVED,
        }
        
        return status_mapping.get(action)


# Global instance for v0
_batch_workflow_engine_instance = None


def get_batch_workflow_engine() -> BatchWorkflowEngine:
    """Get the global batch workflow engine instance."""
    global _batch_workflow_engine_instance
    if _batch_workflow_engine_instance is None:
        _batch_workflow_engine_instance = BatchWorkflowEngine()
    return _batch_workflow_engine_instance
