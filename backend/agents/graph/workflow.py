"""
LangGraph Workflow Definition for the Multi-Agent Growth System.

This defines the state graph that orchestrates all 8 agents with:
- Orchestrator as the central coordinator
- 7 specialist agents for each domain
- Human-in-the-loop approval checkpoints
- Persistent state via PostgreSQL

Workflow Types:
- full_growth_plan: All agents execute in sequence
- content_generation: Content Factory + Compliance only
- influencer_matching: Influencer Matching focus
- community_strategy: Community Ops focus
- product_strategy: Product Strategy focus
"""

from typing import Any, Optional, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import structlog

from backend.agents.graph.state import (
    GrowthWorkflowState,
    AgentType,
    create_initial_state,
)
from backend.agents.agents.orchestrator import orchestrator_node
from backend.agents.agents.global_benchmark import global_benchmark_node
from backend.agents.agents.china_compliance import china_compliance_node
from backend.agents.agents.product_strategy import product_strategy_node
from backend.agents.agents.community_ops import community_ops_node
from backend.agents.agents.content_factory import content_factory_node
from backend.agents.agents.influencer_matching import influencer_matching_node
from backend.agents.agents.data_analyst import data_analyst_node
from backend.app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Global checkpointer (initialized on first use)
_checkpointer: Optional[AsyncPostgresSaver] = None


async def get_checkpointer() -> AsyncPostgresSaver:
    """Get or create PostgreSQL checkpointer for state persistence."""
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = AsyncPostgresSaver.from_conn_string(
            settings.database_url.replace("+asyncpg", "")
        )
        await _checkpointer.setup()
    return _checkpointer


# ============================================================================
# Node Functions - Wrappers for each agent
# ============================================================================

async def orchestrator(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Orchestrator: analyzes input and creates task plan."""
    logger.info("Orchestrator executing", workflow_id=state["workflow_id"])
    return await orchestrator_node(state)


async def global_benchmark(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Global Benchmark: researches US/EU/KR/JP strategies."""
    logger.info("Global Benchmark executing", workflow_id=state["workflow_id"])
    return await global_benchmark_node(state)


async def product_strategy(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Product Strategy: pricing, bundling, seasonal planning."""
    logger.info("Product Strategy executing", workflow_id=state["workflow_id"])
    return await product_strategy_node(state)


async def community_ops(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Community Ops: conversation flows, triggers, scripts."""
    logger.info("Community Ops executing", workflow_id=state["workflow_id"])
    return await community_ops_node(state)


async def content_factory(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Content Factory: viral topics, brand columns, scripts."""
    logger.info("Content Factory executing", workflow_id=state["workflow_id"])
    return await content_factory_node(state)


async def influencer_matching(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Influencer Matching: KOL screening, scoring, outreach."""
    logger.info("Influencer Matching executing", workflow_id=state["workflow_id"])
    return await influencer_matching_node(state)


async def compliance_check(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """China Compliance: regulatory review of all outputs."""
    logger.info("Compliance Check executing", workflow_id=state["workflow_id"])
    return await china_compliance_node(state)


async def data_analyst(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Data Analyst: metrics, experiments, dashboards."""
    logger.info("Data Analyst executing", workflow_id=state["workflow_id"])
    return await data_analyst_node(state)


async def human_review(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Human review checkpoint - pauses for approval."""
    logger.info(
        "Human review checkpoint reached",
        workflow_id=state["workflow_id"],
        pending_count=len(state["pending_approvals"]),
    )

    state["current_phase"] = "awaiting_approval"

    if state["auto_approve"]:
        logger.warning("Auto-approve enabled, skipping human review")
        state["approval_decision"] = "approve"

    return state


async def execute_approved(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Execute approved actions and finalize output."""
    logger.info("Executing approved actions", workflow_id=state["workflow_id"])

    state["current_phase"] = "completed"
    state["final_output"] = {
        "status": "completed",
        "workflow_type": state["workflow_type"],
        "agent_outputs": state["agent_outputs"],
        "message": "Workflow completed successfully",
        "summary": _create_output_summary(state),
    }

    return state


async def aggregate_results(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """Aggregate all agent outputs for human review."""
    logger.info("Aggregating results", workflow_id=state["workflow_id"])

    state["current_phase"] = "review"

    # Create approval items for each agent output
    pending = []
    agent_outputs = state.get("agent_outputs", {})

    if agent_outputs.get("content_factory"):
        pending.append({
            "agent": AgentType.CONTENT_FACTORY,
            "content_type": "content_plan",
            "preview": _create_preview(agent_outputs["content_factory"]),
            "approved": None,
            "feedback": None,
        })

    if agent_outputs.get("community_ops"):
        pending.append({
            "agent": AgentType.COMMUNITY_OPS,
            "content_type": "community_scripts",
            "preview": _create_preview(agent_outputs["community_ops"]),
            "approved": None,
            "feedback": None,
        })

    if agent_outputs.get("influencer_matching"):
        pending.append({
            "agent": AgentType.INFLUENCER_MATCHING,
            "content_type": "influencer_framework",
            "preview": _create_preview(agent_outputs["influencer_matching"]),
            "approved": None,
            "feedback": None,
        })

    if agent_outputs.get("product_strategy"):
        pending.append({
            "agent": AgentType.PRODUCT_STRATEGY,
            "content_type": "product_plan",
            "preview": _create_preview(agent_outputs["product_strategy"]),
            "approved": None,
            "feedback": None,
        })

    state["pending_approvals"] = pending

    return state


def _create_preview(output: dict[str, Any]) -> dict[str, Any]:
    """Create a preview summary of agent output."""
    if output.get("error"):
        return {"status": "error", "error": output["error"]}

    # Return first few items of each key list
    preview = {}
    for key, value in output.items():
        if isinstance(value, list) and len(value) > 0:
            preview[key] = f"{len(value)} items"
        elif isinstance(value, dict) and value:
            preview[key] = f"{len(value)} fields"
        else:
            preview[key] = value

    return preview


def _create_output_summary(state: GrowthWorkflowState) -> dict[str, Any]:
    """Create summary of all outputs for final report."""
    outputs = state.get("agent_outputs", {})
    summary = {}

    if outputs.get("content_factory"):
        cf = outputs["content_factory"]
        summary["content"] = {
            "viral_topics": len(cf.get("viral_topics", [])),
            "brand_columns": len(cf.get("brand_columns", [])),
        }

    if outputs.get("community_ops"):
        co = outputs["community_ops"]
        summary["community"] = {
            "triggers": len(co.get("trigger_responses", [])),
            "faq_entries": len(co.get("faq_knowledge_base", [])),
        }

    if outputs.get("influencer_matching"):
        im = outputs["influencer_matching"]
        summary["influencer"] = {
            "templates": len(im.get("outreach_templates", {})),
        }

    if outputs.get("product_strategy"):
        ps = outputs["product_strategy"]
        summary["product"] = {
            "bundles": len(ps.get("bundle_recommendations", [])),
            "adjustments": len(ps.get("pricing_adjustments", [])),
        }

    if outputs.get("data_analyst"):
        da = outputs["data_analyst"]
        summary["data"] = {
            "experiments": len(da.get("experiment_plan", [])),
        }

    if outputs.get("global_benchmark"):
        gb = outputs["global_benchmark"]
        summary["global"] = {
            "strategies": len(gb.get("recommended_strategies", [])),
        }

    return summary


# ============================================================================
# Routing Functions
# ============================================================================

def route_after_orchestrator(state: GrowthWorkflowState) -> str:
    """Route based on workflow type and orchestrator decision."""
    if state.get("error"):
        return END

    workflow_type = state.get("workflow_type", "full_growth_plan")

    # Route based on workflow type
    if workflow_type == "full_growth_plan":
        return "global_benchmark"  # Start with global research
    elif workflow_type == "content_generation":
        return "content_factory"
    elif workflow_type == "influencer_matching":
        return "influencer_matching"
    elif workflow_type == "community_strategy":
        return "community_ops"
    elif workflow_type == "product_strategy":
        return "product_strategy"
    else:
        return "content_factory"  # Default


def route_after_review(state: GrowthWorkflowState) -> str:
    """Route based on human review decision."""
    decision = state.get("approval_decision")

    if decision == "approve":
        return "execute_approved"
    elif decision == "reject":
        return END
    elif decision == "request_changes":
        return "orchestrator"

    return END


# ============================================================================
# Graph Definitions
# ============================================================================

def create_full_growth_workflow() -> StateGraph:
    """
    Create the full growth workflow with all 8 agents.

    Flow:
    orchestrator → global_benchmark → product_strategy → content_factory
    → community_ops → influencer_matching → compliance_check → data_analyst
    → aggregate_results → human_review → execute_approved → END
    """
    workflow = StateGraph(GrowthWorkflowState)

    # Add all nodes
    workflow.add_node("orchestrator", orchestrator)
    workflow.add_node("global_benchmark", global_benchmark)
    workflow.add_node("product_strategy", product_strategy)
    workflow.add_node("content_factory", content_factory)
    workflow.add_node("community_ops", community_ops)
    workflow.add_node("influencer_matching", influencer_matching)
    workflow.add_node("compliance_check", compliance_check)
    workflow.add_node("data_analyst", data_analyst)
    workflow.add_node("aggregate_results", aggregate_results)
    workflow.add_node("human_review", human_review)
    workflow.add_node("execute_approved", execute_approved)

    # Set entry point
    workflow.set_entry_point("orchestrator")

    # Define the flow
    workflow.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {
            "global_benchmark": "global_benchmark",
            "content_factory": "content_factory",
            "influencer_matching": "influencer_matching",
            "community_ops": "community_ops",
            "product_strategy": "product_strategy",
            END: END,
        }
    )

    # Full workflow chain
    workflow.add_edge("global_benchmark", "product_strategy")
    workflow.add_edge("product_strategy", "content_factory")
    workflow.add_edge("content_factory", "community_ops")
    workflow.add_edge("community_ops", "influencer_matching")
    workflow.add_edge("influencer_matching", "compliance_check")
    workflow.add_edge("compliance_check", "data_analyst")
    workflow.add_edge("data_analyst", "aggregate_results")
    workflow.add_edge("aggregate_results", "human_review")

    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "execute_approved": "execute_approved",
            "orchestrator": "orchestrator",
            END: END,
        }
    )

    workflow.add_edge("execute_approved", END)

    return workflow


def create_content_workflow() -> StateGraph:
    """
    Create content-focused workflow.

    Flow:
    orchestrator → content_factory → compliance_check → aggregate_results
    → human_review → execute_approved → END
    """
    workflow = StateGraph(GrowthWorkflowState)

    workflow.add_node("orchestrator", orchestrator)
    workflow.add_node("content_factory", content_factory)
    workflow.add_node("compliance_check", compliance_check)
    workflow.add_node("aggregate_results", aggregate_results)
    workflow.add_node("human_review", human_review)
    workflow.add_node("execute_approved", execute_approved)

    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "content_factory")
    workflow.add_edge("content_factory", "compliance_check")
    workflow.add_edge("compliance_check", "aggregate_results")
    workflow.add_edge("aggregate_results", "human_review")

    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "execute_approved": "execute_approved",
            "orchestrator": "orchestrator",
            END: END,
        }
    )

    workflow.add_edge("execute_approved", END)

    return workflow


def create_growth_workflow(workflow_type: str = "full_growth_plan") -> StateGraph:
    """
    Factory function to create appropriate workflow based on type.
    """
    if workflow_type == "content_generation":
        return create_content_workflow()
    else:
        return create_full_growth_workflow()


# ============================================================================
# Public API
# ============================================================================

async def run_growth_workflow(
    workflow_id: str,
    workflow_type: str,
    input_data: dict[str, Any],
    auto_approve: bool = False,
) -> dict[str, Any]:
    """
    Run the growth workflow.

    Args:
        workflow_id: Unique workflow identifier
        workflow_type: Type of workflow (full_growth_plan, content_generation, etc.)
        input_data: Input data including institution info, SOPs, etc.
        auto_approve: Whether to skip human review

    Returns:
        Workflow result or status if awaiting approval
    """
    checkpointer = await get_checkpointer()

    # Create initial state
    initial_state = create_initial_state(
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        input_data=input_data,
        auto_approve=auto_approve,
    )

    # Run the graph
    config = {"configurable": {"thread_id": workflow_id}}

    # Create appropriate workflow with interrupt
    graph_with_interrupt = create_growth_workflow(workflow_type).compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"],
    )

    logger.info(
        "Starting workflow",
        workflow_id=workflow_id,
        workflow_type=workflow_type,
    )

    result = await graph_with_interrupt.ainvoke(initial_state, config)

    # Check if we hit the interrupt
    if result.get("current_phase") == "review":
        return {
            "awaiting_approval": True,
            "current_step": "human_review",
            "pending_approvals": result.get("pending_approvals", []),
            "agent_outputs_preview": _create_output_summary(result),
        }

    return result


async def resume_workflow_with_approval(
    workflow_id: str,
    decision: str,
    feedback: Optional[str] = None,
    modifications: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Resume a workflow after human approval.

    Args:
        workflow_id: The workflow to resume
        decision: "approve", "reject", or "request_changes"
        feedback: Optional reviewer feedback
        modifications: Optional content modifications

    Returns:
        Updated workflow state
    """
    checkpointer = await get_checkpointer()
    config = {"configurable": {"thread_id": workflow_id}}

    # Get current state to determine workflow type
    current_state = await get_workflow_state(workflow_id)
    workflow_type = current_state.get("workflow_type", "full_growth_plan")

    graph_with_interrupt = create_growth_workflow(workflow_type).compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"],
    )

    # Update state with approval decision
    update = {
        "approval_decision": decision,
        "approval_feedback": feedback,
    }

    logger.info(
        "Resuming workflow",
        workflow_id=workflow_id,
        decision=decision,
    )

    result = await graph_with_interrupt.ainvoke(update, config)

    return {
        "next_step": result.get("current_phase"),
        "message": f"Workflow {decision}d successfully",
        "final_output": result.get("final_output"),
    }


async def get_workflow_state(workflow_id: str) -> dict[str, Any]:
    """Get the current state of a workflow."""
    checkpointer = await get_checkpointer()
    config = {"configurable": {"thread_id": workflow_id}}

    graph = create_full_growth_workflow().compile(checkpointer=checkpointer)
    state = await graph.aget_state(config)

    return dict(state.values) if state and state.values else {}
