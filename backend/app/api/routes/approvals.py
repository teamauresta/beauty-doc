from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
import structlog

from backend.agents.graph.workflow import resume_workflow_with_approval

router = APIRouter()
logger = structlog.get_logger()


class ApprovalDecision(str, Enum):
    """Approval decisions."""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"


class ApprovalRequest(BaseModel):
    """Schema for submitting an approval decision."""
    decision: ApprovalDecision
    feedback: Optional[str] = None  # Reviewer comments
    modifications: Optional[dict[str, Any]] = None  # Requested changes


class PendingApproval(BaseModel):
    """Schema for a pending approval item."""
    workflow_id: UUID
    step_name: str
    agent_name: str
    content_preview: dict[str, Any]
    created_at: datetime


class ApprovalResponse(BaseModel):
    """Response after processing approval."""
    workflow_id: UUID
    decision: ApprovalDecision
    next_step: Optional[str] = None
    message: str


# Track pending approvals (in production, query from LangGraph state)
_pending_approvals: dict[UUID, PendingApproval] = {}


@router.get("/pending", response_model=list[PendingApproval])
async def list_pending_approvals() -> list[PendingApproval]:
    """List all pending approval requests."""
    return list(_pending_approvals.values())


@router.get("/{workflow_id}", response_model=PendingApproval)
async def get_pending_approval(workflow_id: UUID) -> PendingApproval:
    """Get details of a pending approval."""
    if workflow_id not in _pending_approvals:
        raise HTTPException(status_code=404, detail="No pending approval for this workflow")
    return _pending_approvals[workflow_id]


@router.post("/{workflow_id}", response_model=ApprovalResponse)
async def submit_approval(
    workflow_id: UUID,
    approval: ApprovalRequest,
) -> ApprovalResponse:
    """
    Submit approval decision for a workflow step.

    This will:
    1. Record the decision
    2. Resume the LangGraph workflow if approved
    3. Re-run the agent with feedback if changes requested
    4. Stop the workflow if rejected
    """
    if workflow_id not in _pending_approvals:
        raise HTTPException(status_code=404, detail="No pending approval for this workflow")

    logger.info(
        "Approval submitted",
        workflow_id=str(workflow_id),
        decision=approval.decision,
    )

    # Resume workflow with the decision
    result = await resume_workflow_with_approval(
        workflow_id=str(workflow_id),
        decision=approval.decision.value,
        feedback=approval.feedback,
        modifications=approval.modifications,
    )

    # Remove from pending if approved or rejected
    if approval.decision in [ApprovalDecision.APPROVE, ApprovalDecision.REJECT]:
        del _pending_approvals[workflow_id]

    return ApprovalResponse(
        workflow_id=workflow_id,
        decision=approval.decision,
        next_step=result.get("next_step"),
        message=result.get("message", "Approval processed"),
    )


def register_pending_approval(
    workflow_id: UUID,
    step_name: str,
    agent_name: str,
    content_preview: dict[str, Any],
) -> None:
    """Register a new pending approval (called by workflow)."""
    _pending_approvals[workflow_id] = PendingApproval(
        workflow_id=workflow_id,
        step_name=step_name,
        agent_name=agent_name,
        content_preview=content_preview,
        created_at=datetime.utcnow(),
    )
