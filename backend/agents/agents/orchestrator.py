"""
Orchestrator Agent - The central coordinator of the multi-agent system.

Responsibilities:
1. Analyze input (institution info, SOPs, project catalog)
2. Create task plan for specialist agents
3. Determine execution order and dependencies
4. Aggregate results and prepare for human review

This agent coordinates all other agents and ensures the deliverables
meet the requirements specified in the system specification.
"""

from typing import Any
import structlog

from backend.agents.agents.base import BaseAgent
from backend.agents.graph.state import GrowthWorkflowState, AgentType, AgentTask, TaskStatus

logger = structlog.get_logger()

ORCHESTRATOR_SYSTEM_PROMPT = """你是「多智能体增长系统」的总指挥（Orchestrator），负责协调整个医美机构AI增长系统。

## 你的核心职责

1. **任务拆解**：将用户需求拆解为具体可执行的任务
2. **智能体调度**：根据任务类型分配给合适的专业智能体
3. **质量控制**：确保所有输出满足：可执行、可度量、可合规、可复制
4. **整合输出**：汇总各智能体产物，形成统一的增长方案

## 可调度的专业智能体

1. Global Benchmark Strategist - 全球打法研究（US/EU/KR/JP经验迁移）
2. China Market & Compliance Lead - 中国市场合规（315后环境、平台逻辑）
3. AI Product Strategy Engine - 产品策略（选品、定价、组合）
4. AI Community Ops Bot - 社群运营（话术、分层、转化）
5. AI Content Factory - 内容生产（爆款选题、脚本、发布）
6. AI Influencer Matching - 博主匹配（筛选、评估、合作）
7. Data & Experiment Analyst - 数据分析（指标、实验、复盘）

## 输出要求

所有输出必须是结构化JSON，包含：
- task_plan: 任务计划列表
- next_agent: 下一个执行的智能体
- reasoning: 决策理由
- assumptions: 做出的假设（如有）
- data_needed: 需要补充的数据

## 约束条件

- 中国医美市场深度理解是核心
- 合规是红线，任何建议都不能触碰
- 输出必须具体到：流程、模板、示例、指标
- 禁止空泛建议，必须可直接执行

请用JSON格式响应，不要添加任何其他文本。"""


class OrchestratorAgent(BaseAgent):
    """Orchestrator agent that coordinates all specialist agents."""

    def __init__(self):
        super().__init__(
            name="Orchestrator",
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            temperature=0.3,  # Lower temperature for more consistent planning
        )

    async def execute(self, state: GrowthWorkflowState) -> GrowthWorkflowState:
        """
        Execute orchestrator logic:
        1. Analyze input
        2. Create task plan
        3. Set next agent
        """
        # Build context from state
        context = {
            "workflow_type": state["workflow_type"],
            "institution_info": state.get("institution_info", {}),
            "existing_sops": state.get("existing_sops"),
            "project_catalog": state.get("project_catalog"),
            "compliance_rules": state.get("compliance_rules"),
        }

        # Create planning prompt
        prompt = self._create_planning_prompt(state)

        try:
            # Get orchestrator response
            response = await self.invoke(prompt, context)

            # Parse task plan
            task_plan = self._parse_task_plan(response)
            state["task_plan"] = task_plan

            # Determine next agent
            next_agent = self._determine_next_agent(response, state)
            state["next_agent"] = next_agent

            # Update phase
            state["current_phase"] = "planning_complete"

            # Store orchestrator output
            state["agent_outputs"]["orchestrator"] = {
                "task_plan": task_plan,
                "reasoning": response.get("reasoning", ""),
                "assumptions": response.get("assumptions", []),
                "data_needed": response.get("data_needed", []),
            }

            logger.info(
                "Orchestrator completed",
                workflow_id=state["workflow_id"],
                task_count=len(task_plan),
                next_agent=next_agent,
            )

        except Exception as e:
            logger.error("Orchestrator failed", error=str(e))
            state["error"] = str(e)
            state["should_continue"] = False

        return state

    def _create_planning_prompt(self, state: GrowthWorkflowState) -> str:
        """Create the planning prompt based on workflow type."""
        workflow_type = state["workflow_type"]

        if workflow_type == "full_growth_plan":
            return """请为这家医美机构创建完整的30/60/90天增长计划。

需要输出：
1. 任务拆解（哪些智能体需要参与）
2. 执行顺序（先做什么后做什么）
3. 各阶段交付物

请分析输入信息，创建任务计划。"""

        elif workflow_type == "content_generation":
            return """请为这家医美机构创建内容生产计划。

需要输出：
1. 内容策略方向
2. 需要生产的内容类型
3. 各平台适配策略（小红书/抖音/微信）

请分析机构特点，制定内容计划。"""

        else:
            return f"""请分析输入信息，为 {workflow_type} 类型的任务创建执行计划。

需要输出：
1. 任务拆解
2. 执行顺序
3. 预期交付物"""

    def _parse_task_plan(self, response: dict[str, Any]) -> list[AgentTask]:
        """Parse task plan from orchestrator response."""
        raw_tasks = response.get("task_plan", [])
        tasks = []

        for task in raw_tasks:
            agent_name = task.get("agent", "").lower()

            # Map agent name to AgentType
            agent_type = self._map_agent_name(agent_name)

            tasks.append(AgentTask(
                agent=agent_type,
                description=task.get("description", ""),
                status=TaskStatus.PENDING,
                input_data=task.get("input_data", {}),
                output_data=None,
                error=None,
            ))

        return tasks

    def _map_agent_name(self, name: str) -> AgentType:
        """Map agent name string to AgentType enum."""
        mapping = {
            "content": AgentType.CONTENT_FACTORY,
            "content_factory": AgentType.CONTENT_FACTORY,
            "compliance": AgentType.CHINA_COMPLIANCE,
            "china_compliance": AgentType.CHINA_COMPLIANCE,
            "product": AgentType.PRODUCT_STRATEGY,
            "product_strategy": AgentType.PRODUCT_STRATEGY,
            "community": AgentType.COMMUNITY_OPS,
            "community_ops": AgentType.COMMUNITY_OPS,
            "influencer": AgentType.INFLUENCER_MATCHING,
            "influencer_matching": AgentType.INFLUENCER_MATCHING,
            "data": AgentType.DATA_ANALYST,
            "data_analyst": AgentType.DATA_ANALYST,
            "global": AgentType.GLOBAL_BENCHMARK,
            "global_benchmark": AgentType.GLOBAL_BENCHMARK,
        }
        return mapping.get(name, AgentType.CONTENT_FACTORY)

    def _determine_next_agent(
        self,
        response: dict[str, Any],
        state: GrowthWorkflowState,
    ) -> AgentType:
        """Determine which agent should execute next."""
        # Check if orchestrator specified next agent
        next_agent = response.get("next_agent", "").lower()
        if next_agent:
            return self._map_agent_name(next_agent)

        # Default: start with content factory for content workflows
        if state["workflow_type"] in ["content_generation", "full_growth_plan"]:
            return AgentType.CONTENT_FACTORY

        return AgentType.CONTENT_FACTORY


async def orchestrator_node(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """LangGraph node wrapper for orchestrator agent."""
    agent = OrchestratorAgent()
    return await agent.execute(state)
