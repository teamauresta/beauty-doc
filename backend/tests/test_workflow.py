"""
Tests for the Growth Workflow.
"""

import pytest
from uuid import uuid4

from backend.agents.graph.state import (
    GrowthWorkflowState,
    AgentType,
    TaskStatus,
    create_initial_state,
)


class TestWorkflowState:
    """Tests for workflow state management."""

    def test_create_initial_state(self):
        """Test initial state creation."""
        workflow_id = str(uuid4())
        input_data = {
            "tenant_id": str(uuid4()),
            "institution_info": {
                "name": "Test Clinic",
                "city": "Shanghai",
                "tier": "high",
                "main_services": ["botox", "filler"],
            },
        }

        state = create_initial_state(
            workflow_id=workflow_id,
            workflow_type="content_generation",
            input_data=input_data,
        )

        assert state["workflow_id"] == workflow_id
        assert state["workflow_type"] == "content_generation"
        assert state["current_phase"] == "initializing"
        assert state["should_continue"] is True
        assert state["next_agent"] == AgentType.ORCHESTRATOR

    def test_initial_state_with_auto_approve(self):
        """Test initial state with auto_approve enabled."""
        state = create_initial_state(
            workflow_id=str(uuid4()),
            workflow_type="full_growth_plan",
            input_data={},
            auto_approve=True,
        )

        assert state["auto_approve"] is True

    def test_agent_types(self):
        """Test all agent types are defined."""
        expected_agents = [
            "orchestrator",
            "global_benchmark",
            "china_compliance",
            "product_strategy",
            "community_ops",
            "content_factory",
            "influencer_matching",
            "data_analyst",
        ]

        for agent_name in expected_agents:
            assert hasattr(AgentType, agent_name.upper())

    def test_task_status_transitions(self):
        """Test valid task status values."""
        valid_statuses = [
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.AWAITING_APPROVAL,
            TaskStatus.APPROVED,
            TaskStatus.REJECTED,
        ]

        for status in valid_statuses:
            assert isinstance(status.value, str)


class TestWorkflowIntegration:
    """Integration tests for workflow execution."""

    @pytest.mark.asyncio
    async def test_workflow_creation(self):
        """Test workflow can be created via API."""
        # This would test the actual API endpoint
        # For now, just verify the state structure
        state = create_initial_state(
            workflow_id=str(uuid4()),
            workflow_type="content_generation",
            input_data={
                "institution_info": {
                    "name": "Beauty Clinic",
                    "city": "Beijing",
                    "tier": "medium",
                    "main_services": ["skin care", "laser"],
                },
            },
        )

        assert state["institution_info"]["city"] == "Beijing"
        assert "skin care" in state["institution_info"]["main_services"]
