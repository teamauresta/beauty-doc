from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
import structlog

from backend.agents.graph.workflow import run_growth_workflow, get_workflow_state

router = APIRouter()
logger = structlog.get_logger()


class WorkflowType(str, Enum):
    """Types of growth workflows."""
    FULL_GROWTH_PLAN = "full_growth_plan"  # Complete 30/60/90 day plan
    CONTENT_GENERATION = "content_generation"  # Generate content for platforms
    INFLUENCER_MATCHING = "influencer_matching"  # Find and match KOLs
    COMMUNITY_STRATEGY = "community_strategy"  # Social community ops plan
    PRODUCT_STRATEGY = "product_strategy"  # Product/pricing recommendations


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowCreate(BaseModel):
    """Schema for creating a workflow."""
    tenant_id: UUID
    workflow_type: WorkflowType
    input_data: dict[str, Any]  # 机构信息, SOP, 项目库 etc.
    auto_approve: bool = False  # Skip human review (not recommended)


class WorkflowResponse(BaseModel):
    """Response schema for workflow."""
    id: UUID
    tenant_id: UUID
    workflow_type: WorkflowType
    status: WorkflowStatus
    input_data: dict[str, Any]
    output_data: Optional[dict[str, Any]] = None
    current_step: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# In-memory storage for MVP
_workflows: dict[UUID, WorkflowResponse] = {}


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    background_tasks: BackgroundTasks,
) -> WorkflowResponse:
    """
    Create and start a new growth workflow.

    The workflow will:
    1. Start with the Orchestrator analyzing the input
    2. Delegate to specialist agents (Content Factory, Influencer Matching, etc.)
    3. Pause at approval checkpoints for human review
    4. Execute approved actions (content publishing, outreach, etc.)
    """
    workflow_id = uuid4()
    now = datetime.utcnow()

    response = WorkflowResponse(
        id=workflow_id,
        tenant_id=workflow.tenant_id,
        workflow_type=workflow.workflow_type,
        status=WorkflowStatus.PENDING,
        input_data=workflow.input_data,
        current_step="initializing",
        created_at=now,
        updated_at=now,
    )
    _workflows[workflow_id] = response

    # Start workflow in background
    background_tasks.add_task(
        execute_workflow,
        workflow_id,
        workflow.workflow_type,
        workflow.input_data,
        workflow.auto_approve,
    )

    logger.info(
        "Workflow created",
        workflow_id=str(workflow_id),
        workflow_type=workflow.workflow_type,
        tenant_id=str(workflow.tenant_id),
    )

    return response


async def execute_workflow(
    workflow_id: UUID,
    workflow_type: WorkflowType,
    input_data: dict[str, Any],
    auto_approve: bool,
) -> None:
    """Execute workflow using LangGraph."""
    try:
        _workflows[workflow_id].status = WorkflowStatus.RUNNING
        _workflows[workflow_id].updated_at = datetime.utcnow()

        # Run the LangGraph workflow
        result = await run_growth_workflow(
            workflow_id=str(workflow_id),
            workflow_type=workflow_type.value,
            input_data=input_data,
            auto_approve=auto_approve,
        )

        # Check if workflow is waiting for approval
        if result.get("awaiting_approval"):
            _workflows[workflow_id].status = WorkflowStatus.AWAITING_APPROVAL
            _workflows[workflow_id].current_step = result.get("current_step")
        else:
            _workflows[workflow_id].status = WorkflowStatus.COMPLETED
            _workflows[workflow_id].output_data = result

        _workflows[workflow_id].updated_at = datetime.utcnow()

    except Exception as e:
        logger.error("Workflow failed", workflow_id=str(workflow_id), error=str(e))
        _workflows[workflow_id].status = WorkflowStatus.FAILED
        _workflows[workflow_id].updated_at = datetime.utcnow()


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: UUID) -> WorkflowResponse:
    """Get workflow status and results."""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _workflows[workflow_id]


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows(
    tenant_id: Optional[UUID] = None,
    status: Optional[WorkflowStatus] = None,
) -> list[WorkflowResponse]:
    """List workflows with optional filters."""
    workflows = list(_workflows.values())

    if tenant_id:
        workflows = [w for w in workflows if w.tenant_id == tenant_id]
    if status:
        workflows = [w for w in workflows if w.status == status]

    return sorted(workflows, key=lambda w: w.created_at, reverse=True)


@router.get("/{workflow_id}/state")
async def get_workflow_state_endpoint(workflow_id: UUID) -> dict[str, Any]:
    """Get detailed workflow state from LangGraph."""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    state = await get_workflow_state(str(workflow_id))
    return state
