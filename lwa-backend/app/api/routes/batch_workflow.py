from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.core.auth import get_current_user_optional
from app.services.batch_workflow import (
    BatchWorkflowEngine,
    BatchWorkflowItem,
    BatchWorkflowAction,
    BatchWorkflowFilter,
    BatchWorkflowSummary,
    WorkflowItemType,
    WorkflowStatus,
    WorkflowActionType,
    get_batch_workflow_engine,
)


router = APIRouter()


class WorkflowItemCreateRequest(BaseModel):
    item_type: str = Field(..., description="Type of workflow item")
    title: str = Field(..., description="Title of the workflow item")
    description: Optional[str] = Field(None, description="Description of the item")
    external_ref: Optional[str] = Field(None, description="External reference ID")
    external_type: Optional[str] = Field(None, description="Type of external reference")
    platform: Optional[str] = Field(None, description="Target platform")
    goal: Optional[str] = Field(None, description="Goal of the item")
    best_use_case: Optional[str] = Field(None, description="Best use case")
    score_confidence: Optional[float] = Field(None, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class WorkflowItemResponse(BaseModel):
    item_id: str
    user_id: str
    item_type: str
    status: str
    title: str
    description: Optional[str]
    external_ref: Optional[str]
    external_type: Optional[str]
    platform: Optional[str]
    goal: Optional[str]
    best_use_case: Optional[str]
    score_confidence: Optional[float]
    target_platform: Optional[str]
    linked_asset_ids: List[str]
    available_actions: List[str]
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class WorkflowItemListResponse(BaseModel):
    items: List[WorkflowItemResponse]
    total_count: int


class WorkflowActionRequest(BaseModel):
    action_type: str = Field(..., description="Type of action to execute")
    notes: Optional[str] = Field(None, description="Notes about the action")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class BulkActionRequest(BaseModel):
    item_ids: List[str] = Field(..., description="List of item IDs to act on")
    action_type: str = Field(..., description="Type of action to execute")
    notes: Optional[str] = Field(None, description="Notes about the action")


class WorkflowFilterRequest(BaseModel):
    item_types: Optional[List[str]] = Field(None, description="Filter by item types")
    statuses: Optional[List[str]] = Field(None, description="Filter by statuses")
    platforms: Optional[List[str]] = Field(None, description="Filter by platforms")
    goals: Optional[List[str]] = Field(None, description="Filter by goals")
    ready_to_render: Optional[bool] = Field(None, description="Filter by render readiness")
    needs_review: Optional[bool] = Field(None, description="Filter by review need")
    created_after: Optional[str] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[str] = Field(None, description="Filter by creation date (before)")


class WorkflowActionResponse(BaseModel):
    action_id: str
    item_id: str
    user_id: str
    action_type: str
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: str


def get_batch_workflow_engine_instance() -> BatchWorkflowEngine:
    """Get the batch workflow engine instance."""
    return get_batch_workflow_engine()


def _workflow_item_to_response(item: BatchWorkflowItem) -> WorkflowItemResponse:
    """Convert BatchWorkflowItem to response model."""
    return WorkflowItemResponse(
        item_id=item.item_id,
        user_id=item.user_id,
        item_type=item.item_type.value,
        status=item.status.value,
        title=item.title,
        description=item.description,
        external_ref=item.external_ref,
        external_type=item.external_type,
        platform=item.platform,
        goal=item.goal,
        best_use_case=item.best_use_case,
        score_confidence=item.score_confidence,
        target_platform=item.target_platform,
        linked_asset_ids=item.linked_asset_ids,
        available_actions=[action.value for action in item.available_actions],
        metadata=item.metadata,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _workflow_action_to_response(action: BatchWorkflowAction) -> WorkflowActionResponse:
    """Convert BatchWorkflowAction to response model."""
    return WorkflowActionResponse(
        action_id=action.action_id,
        item_id=action.item_id,
        user_id=action.user_id,
        action_type=action.action_type.value,
        notes=action.notes,
        metadata=action.metadata,
        created_at=action.created_at,
    )


@router.post("/batch-workflow/items", response_model=WorkflowItemResponse)
async def create_workflow_item(
    request: WorkflowItemCreateRequest,
    current_user: dict = Depends(get_current_user_optional),
):
    """Create a new workflow item."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Parse item type
    try:
        item_type = WorkflowItemType(request.item_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid item type: {request.item_type}")
    
    # Create workflow item
    engine = get_batch_workflow_engine_instance()
    item = engine.create_workflow_item(
        item_type=item_type,
        title=request.title,
        user_id=user_id,
        external_ref=request.external_ref,
        external_type=request.external_type,
        platform=request.platform,
        goal=request.goal,
        best_use_case=request.best_use_case,
        score_confidence=request.score_confidence,
        metadata=request.metadata
    )
    
    return _workflow_item_to_response(item)


@router.get("/batch-workflow/items", response_model=WorkflowItemListResponse)
async def list_workflow_items(
    item_types: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None,
    platforms: Optional[List[str]] = None,
    goals: Optional[List[str]] = None,
    ready_to_render: Optional[bool] = None,
    needs_review: Optional[bool] = None,
    current_user: dict = Depends(get_current_user_optional),
):
    """List workflow items with optional filtering."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Build filter
    filter_obj = BatchWorkflowFilter()
    
    if item_types:
        try:
            filter_obj.item_types = [WorkflowItemType(t.lower()) for t in item_types]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid item types in filter")
    
    if statuses:
        try:
            filter_obj.statuses = [WorkflowStatus(s.lower()) for s in statuses]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid statuses in filter")
    
    filter_obj.platforms = platforms
    filter_obj.goals = goals
    filter_obj.ready_to_render = ready_to_render
    filter_obj.needs_review = needs_review
    
    # Get items
    engine = get_batch_workflow_engine_instance()
    items = engine.list_workflow_items(user_id, filter_obj)
    
    item_responses = [_workflow_item_to_response(item) for item in items]
    
    return WorkflowItemListResponse(
        items=item_responses,
        total_count=len(item_responses)
    )


@router.get("/batch-workflow/items/{item_id}", response_model=WorkflowItemResponse)
async def get_workflow_item(
    item_id: str,
    current_user: dict = Depends(get_current_user_optional),
):
    """Get a specific workflow item."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    engine = get_batch_workflow_engine_instance()
    item = engine.get_workflow_item(item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Workflow item not found")
    
    # In production, verify user owns this item. For v0, skip strict user checking
    
    return _workflow_item_to_response(item)


@router.post("/batch-workflow/items/{item_id}/action", response_model=WorkflowActionResponse)
async def execute_workflow_action(
    item_id: str,
    request: WorkflowActionRequest,
    current_user: dict = Depends(get_current_user_optional),
):
    """Execute a workflow action on an item."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Parse action type
    try:
        action_type = WorkflowActionType(request.action_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid action type: {request.action_type}")
    
    # Execute action
    engine = get_batch_workflow_engine_instance()
    action = engine.execute_workflow_action(
        item_id=item_id,
        action_type=action_type,
        user_id=user_id,
        notes=request.notes,
        metadata=request.metadata
    )
    
    return _workflow_action_to_response(action)


@router.post("/batch-workflow/bulk-action", response_model=List[WorkflowActionResponse])
async def execute_bulk_workflow_action(
    request: BulkActionRequest,
    current_user: dict = Depends(get_current_user_optional),
):
    """Execute a workflow action on multiple items."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Parse action type
    try:
        action_type = WorkflowActionType(request.action_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid action type: {request.action_type}")
    
    # Execute bulk action
    engine = get_batch_workflow_engine_instance()
    actions = engine.bulk_execute_workflow_action(
        item_ids=request.item_ids,
        action_type=action_type,
        user_id=user_id,
        notes=request.notes
    )
    
    return [_workflow_action_to_response(action) for action in actions]


@router.get("/batch-workflow/summary")
async def get_workflow_summary(
    current_user: dict = Depends(get_current_user_optional),
):
    """Get workflow summary statistics."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    engine = get_batch_workflow_engine_instance()
    summary = engine.get_workflow_summary(user_id)
    
    return {
        "total_items": summary.total_items,
        "by_status": summary.by_status,
        "by_type": summary.by_type,
        "by_platform": summary.by_platform,
        "ready_to_render": summary.ready_to_render,
        "needs_review": summary.needs_review,
        "approved_items": summary.approved_items,
        "rejected_items": summary.rejected_items,
        "avg_score_confidence": summary.avg_score_confidence
    }


@router.get("/batch-workflow/capabilities")
async def get_workflow_capabilities(
    current_user: dict = Depends(get_current_user_optional),
):
    """Get workflow capabilities and options."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "item_types": [item_type.value for item_type in WorkflowItemType],
        "statuses": [status.value for status in WorkflowStatus],
        "action_types": [action_type.value for action in WorkflowActionType],
        "platforms": ["tiktok", "instagram", "youtube", "youtube_shorts", "linkedin", "twitter", "whop"],
        "goals": ["attention", "trust", "sales", "proof", "authority", "community", "launch"],
        "features": {
            "bulk_actions": True,
            "filtering": True,
            "metadata_workflow_only": True,
            "render_engine_integration": False,  # Future gated
            "proof_graph_integration": False,  # Future gated
            "campaign_export_integration": False,  # Future gated
        }
    }


@router.delete("/batch-workflow/items/{item_id}")
async def delete_workflow_item(
    item_id: str,
    current_user: dict = Depends(get_current_user_optional),
):
    """Delete a workflow item."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    engine = get_batch_workflow_engine_instance()
    
    # Verify item exists
    item = engine.get_workflow_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow item not found")
    
    # In production, verify user owns this item. For v0, skip strict user checking
    
    deleted = engine.delete_workflow_item(item_id)
    
    if deleted:
        return {"message": "Workflow item deleted successfully", "item_id": item_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete workflow item")


@router.get("/batch-workflow/items/{item_id}/actions", response_model=List[WorkflowActionResponse])
async def get_item_actions(
    item_id: str,
    current_user: dict = Depends(get_current_user_optional),
):
    """Get all actions for a workflow item."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    engine = get_batch_workflow_engine_instance()
    
    # Verify item exists
    item = engine.get_workflow_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow item not found")
    
    actions = engine.get_item_actions(item_id)
    
    return [_workflow_action_to_response(action) for action in actions]
