"""
LangGraph State Definition for the Multi-Agent Growth System.

The state flows through:
1. Orchestrator receives input and creates task plan
2. Specialist agents execute their tasks in parallel/sequence
3. Results aggregate for human review
4. After approval, execution proceeds
"""

from typing import TypedDict, Annotated, Optional, Any
from enum import Enum
from operator import add


class AgentType(str, Enum):
    """Types of specialist agents in the system."""
    ORCHESTRATOR = "orchestrator"
    GLOBAL_BENCHMARK = "global_benchmark"
    CHINA_COMPLIANCE = "china_compliance"
    PRODUCT_STRATEGY = "product_strategy"
    COMMUNITY_OPS = "community_ops"
    CONTENT_FACTORY = "content_factory"
    INFLUENCER_MATCHING = "influencer_matching"
    DATA_ANALYST = "data_analyst"


class TaskStatus(str, Enum):
    """Status of individual agent tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class AgentTask(TypedDict):
    """A task assigned to a specialist agent."""
    agent: AgentType
    description: str
    status: TaskStatus
    input_data: dict[str, Any]
    output_data: Optional[dict[str, Any]]
    error: Optional[str]


class ApprovalItem(TypedDict):
    """An item awaiting human approval."""
    agent: AgentType
    content_type: str  # e.g., "content_plan", "influencer_list", "community_script"
    preview: dict[str, Any]
    approved: Optional[bool]
    feedback: Optional[str]


def add_messages(left: list, right: list) -> list:
    """Reducer for message accumulation."""
    return left + right


def merge_outputs(left: dict, right: dict) -> dict:
    """Reducer for merging agent outputs."""
    return {**left, **right}


class GrowthWorkflowState(TypedDict):
    """
    Main state for the Growth Workflow.

    This state is passed between all nodes in the LangGraph and persisted
    to PostgreSQL for resume capability.
    """
    # Workflow metadata
    workflow_id: str
    workflow_type: str
    tenant_id: str

    # Input from user/API
    institution_info: dict[str, Any]  # 机构信息
    existing_sops: Optional[dict[str, Any]]  # 现有 SOP
    project_catalog: Optional[list[dict[str, Any]]]  # 项目库
    historical_data: Optional[dict[str, Any]]  # 历史数据
    compliance_rules: Optional[dict[str, Any]]  # 合规红线

    # Orchestrator planning
    task_plan: list[AgentTask]  # Tasks created by orchestrator
    current_phase: str  # e.g., "planning", "research", "generation", "review"

    # Agent outputs (accumulated)
    agent_outputs: Annotated[dict[str, Any], merge_outputs]

    # Messages/conversation history
    messages: Annotated[list[dict[str, Any]], add_messages]

    # Human-in-the-loop
    pending_approvals: list[ApprovalItem]
    approval_decision: Optional[str]  # "approve", "reject", "request_changes"
    approval_feedback: Optional[str]

    # Final deliverables
    final_output: Optional[dict[str, Any]]

    # Control flow
    next_agent: Optional[AgentType]
    should_continue: bool
    auto_approve: bool
    error: Optional[str]


def create_initial_state(
    workflow_id: str,
    workflow_type: str,
    input_data: dict[str, Any],
    auto_approve: bool = False,
) -> GrowthWorkflowState:
    """Create initial state from workflow input."""
    return GrowthWorkflowState(
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        tenant_id=input_data.get("tenant_id", ""),

        # Parse input data
        institution_info=input_data.get("institution_info", {}),
        existing_sops=input_data.get("existing_sops"),
        project_catalog=input_data.get("project_catalog"),
        historical_data=input_data.get("historical_data"),
        compliance_rules=input_data.get("compliance_rules"),

        # Initialize empty
        task_plan=[],
        current_phase="initializing",
        agent_outputs={},
        messages=[],
        pending_approvals=[],
        approval_decision=None,
        approval_feedback=None,
        final_output=None,
        next_agent=AgentType.ORCHESTRATOR,
        should_continue=True,
        auto_approve=auto_approve,
        error=None,
    )
