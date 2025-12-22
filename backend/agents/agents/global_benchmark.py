"""
Global Benchmark Strategist Agent - 全球打法研究员

Responsibilities:
1. Research US/EU/KR/JP medical aesthetics market strategies
2. Identify transferable tactics and those that don't apply to China
3. Adapt global best practices for Chinese market context
4. Provide comparative analysis with localization recommendations

Markets Covered:
- US: DTC marketing, influencer partnerships, subscription models
- EU: Clinical authority, safety-first messaging, regulatory compliance
- KR: K-beauty integration, idol endorsements, skincare-to-medspa pipeline
- JP: Quality obsession, subtle results, long-term relationship building
"""

from typing import Any
import structlog

from backend.agents.agents.base import BaseAgent
from backend.agents.graph.state import GrowthWorkflowState

logger = structlog.get_logger()

GLOBAL_BENCHMARK_SYSTEM_PROMPT = """你是「全球打法研究员」，专门研究美国、欧洲、韩国、日本的医美增长策略，并为中国市场提供可迁移的经验。

## 你的核心目标

1. **跨市场研究**：深入分析各国医美市场的成功案例
2. **可迁移性评估**：判断哪些策略可以用于中国，哪些不能
3. **本土化改写**：将可用策略改写为适合中国市场的版本
4. **创新启发**：提供中国市场尚未使用的创新思路

## 各市场特征分析

### 美国市场 (US)
**成功模式**：
- DTC品牌直营：Allergan, Galderma的消费者直达策略
- 会员订阅制：Botox俱乐部、积分系统
- 医生IP矩阵：真人秀医生、社交媒体网红医生
- 平台化运营：RealSelf、Zocdoc评价体系

**可迁移**：
✅ 会员积分体系设计
✅ 用户评价机制（需适配）
✅ 项目打包套餐化
❌ 医生个人IP强露出（中国315限制）
❌ 真人手术直播（平台限制）

### 欧洲市场 (EU)
**成功模式**：
- 临床权威背书：学术论文、临床数据
- 安全第一沟通：强调认证、资质、安全记录
- 私密性保护：低调服务、隐私承诺
- 医疗旅游整合：跨境服务、一站式体验

**可迁移**：
✅ 临床数据展示（脱敏处理）
✅ 资质认证强调
✅ 私密服务承诺
❌ 跨境医疗推广（资质限制）

### 韩国市场 (KR)
**成功模式**：
- K-beauty生态：护肤→轻医美→医美的升级路径
- 偶像代言：明星同款、综艺植入
- 价格透明：清晰的价目表、套餐比价
- 术后服务：完善的恢复期服务

**可迁移**：
✅ 护肤到医美的升级链路
✅ 明星同款概念（需合规处理）
✅ 术后服务体系
❌ 明星直接代言医美（广告法限制）

### 日本市场 (JP)
**成功模式**：
- 品质执念：设备先进性、技术精细度
- 自然审美：追求"不像做过"的效果
- 长期关系：客户终身价值经营
- 口碑传播：熟人推荐、圈层渗透

**可迁移**：
✅ 设备技术差异化
✅ 自然审美理念传播
✅ 老客户转介绍体系
✅ 圈层私域运营

## 输出格式

```json
{
  "market_analysis": {
    "us": {"key_insights": [...], "transferable": [...], "not_transferable": [...]},
    "eu": {"key_insights": [...], "transferable": [...], "not_transferable": [...]},
    "kr": {"key_insights": [...], "transferable": [...], "not_transferable": [...]},
    "jp": {"key_insights": [...], "transferable": [...], "not_transferable": [...]}
  },
  "recommended_strategies": [
    {
      "strategy_name": "策略名称",
      "origin_market": "来源市场",
      "original_implementation": "原始做法",
      "china_adaptation": "中国适配版本",
      "implementation_steps": ["步骤1", "步骤2"],
      "expected_impact": "预期效果",
      "risks": ["风险1"],
      "priority": "high|medium|low"
    }
  ],
  "innovation_opportunities": [
    {
      "concept": "创新概念",
      "inspiration_source": "灵感来源",
      "china_application": "中国应用场景",
      "differentiation": "差异化优势"
    }
  ]
}
```

请用JSON格式响应。"""


class GlobalBenchmarkAgent(BaseAgent):
    """Global Benchmark Strategist for cross-market research."""

    def __init__(self):
        super().__init__(
            name="Global Benchmark",
            system_prompt=GLOBAL_BENCHMARK_SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            temperature=0.6,
        )

    async def execute(self, state: GrowthWorkflowState) -> GrowthWorkflowState:
        """
        Research global markets and provide transferable strategies.
        """
        context = {
            "institution_info": state.get("institution_info", {}),
            "workflow_type": state["workflow_type"],
            "existing_strategies": state.get("existing_sops", {}),
        }

        prompt = self._create_research_prompt(state)

        try:
            response = await self.invoke(prompt, context)

            # Structure output
            benchmark_output = self._structure_output(response)

            state["agent_outputs"]["global_benchmark"] = benchmark_output

            state["messages"].append({
                "role": "assistant",
                "agent": "global_benchmark",
                "content": f"Analyzed {len(benchmark_output.get('recommended_strategies', []))} transferable strategies from global markets",
            })

            logger.info(
                "Global Benchmark completed",
                workflow_id=state["workflow_id"],
                strategy_count=len(benchmark_output.get("recommended_strategies", [])),
            )

        except Exception as e:
            logger.error("Global Benchmark failed", error=str(e))
            state["agent_outputs"]["global_benchmark"] = {"error": str(e)}

        return state

    def _create_research_prompt(self, state: GrowthWorkflowState) -> str:
        """Create research prompt based on institution needs."""
        institution = state.get("institution_info", {})
        tier = institution.get("tier", "medium")
        services = institution.get("main_services", [])

        return f"""请为这家医美机构研究全球市场的可借鉴策略：

## 机构特点
- 定位层级：{tier}
- 主营项目：{', '.join(services) if isinstance(services, list) else services}

## 研究任务

1. 分析美国、欧洲、韩国、日本四大市场的医美增长策略
2. 识别可迁移到中国的成功模式
3. 为每个可迁移策略提供中国本土化版本
4. 标注不可迁移的策略及原因（法规、文化、平台差异）
5. 发现中国市场尚未充分利用的创新机会

请特别关注：
- 会员体系设计
- 内容营销策略
- 客户生命周期管理
- 口碑和转介绍机制"""

    def _structure_output(self, response: dict[str, Any]) -> dict[str, Any]:
        """Structure the benchmark output."""
        if isinstance(response, str):
            return {"raw_response": response}

        return {
            "market_analysis": response.get("market_analysis", {}),
            "recommended_strategies": response.get("recommended_strategies", []),
            "innovation_opportunities": response.get("innovation_opportunities", []),
        }


async def global_benchmark_node(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """LangGraph node wrapper for global benchmark agent."""
    agent = GlobalBenchmarkAgent()
    return await agent.execute(state)
