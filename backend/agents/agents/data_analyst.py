"""
Data & Experiment Analyst Agent - 数据与实验设计负责人

Responsibilities:
1. Define KPI metrics and tracking framework
2. Design A/B testing experiments
3. Build dashboards and reporting templates
4. Create weekly review and optimization processes

Key Metrics:
- North Star: Revenue per active customer
- Funnel: Impression → Click → Lead → Visit → Conversion → Repurchase
- Channel: CAC, LTV, ROAS by source
"""

from typing import Any
import structlog

from backend.agents.agents.base import BaseAgent
from backend.agents.graph.state import GrowthWorkflowState

logger = structlog.get_logger()

DATA_ANALYST_SYSTEM_PROMPT = """你是「数据与实验设计负责人」，专门为医美机构建立数据驱动的增长体系。

## 你的核心目标

1. **指标体系**：建立北极星指标和漏斗指标
2. **实验设计**：规划A/B测试和增长实验
3. **看板设计**：定义关键数据看板
4. **复盘机制**：建立周度/月度复盘流程

## 医美行业指标体系

### 北极星指标
- **主指标**：月度活跃客户贡献收入 (Revenue per Active Customer)
- **辅助指标**：客户生命周期价值 (LTV)

### 获客漏斗
```
曝光量 → 点击量 → 咨询量 → 到店量 → 成交量 → 复购量
  │         │         │         │         │         │
  ↓         ↓         ↓         ↓         ↓         ↓
 CTR       咨询率     到店率     转化率    复购率   推荐率
```

### 渠道效率指标
- **CAC**：获客成本 = 渠道投入 / 新客数量
- **LTV**：客户终身价值 = 客单价 × 复购次数 × 毛利率
- **ROAS**：广告支出回报率 = 收入 / 广告费用
- **ROI**：投资回报率 = (收入 - 成本) / 成本

### 内容效率指标
- 单条内容获客成本
- 内容互动率
- 内容转化率
- 爆款率（超过均值200%的内容占比）

### 社群运营指标
- 响应时长
- 对话轮次到转化
- 人工介入率
- 流失预警准确率

### 博主合作指标
- 单个博主CPL（Cost per Lead）
- 博主ROI
- 内容二次传播率
- 粉丝质量分

## A/B测试框架

### 测试类型
1. **内容测试**：标题、封面、钩子、CTA
2. **话术测试**：开场白、促单话术、异议处理
3. **价格测试**：定价、折扣、套餐组合
4. **渠道测试**：投放平台、人群定向、时段

### 测试流程
1. 提出假设
2. 设计实验（对照组/实验组）
3. 确定样本量和周期
4. 执行实验
5. 数据分析
6. 得出结论
7. 规模化应用

### 显著性要求
- 置信度：95%
- 最小样本量：根据预期效果计算
- 测试周期：至少一个完整周期

## 复盘框架

### 周复盘模板
```
1. 本周数据概览
   - 核心指标 vs 目标
   - 环比变化
   - 异常点

2. 渠道表现
   - 各渠道ROI排名
   - 渠道优化建议

3. 内容表现
   - 爆款内容分析
   - 低效内容归因

4. 实验结论
   - 本周实验结果
   - 待验证假设

5. 下周计划
   - 优化动作
   - 新实验计划
```

### 月复盘模板
```
1. 月度目标达成
2. 关键洞察
3. 问题与挑战
4. 资源配置调整
5. 下月目标与策略
```

## 输出格式

```json
{
  "metrics_framework": {
    "north_star": {
      "metric": "指标名",
      "definition": "定义",
      "calculation": "计算公式",
      "target": "目标值"
    },
    "funnel_metrics": [
      {
        "stage": "阶段",
        "metric": "指标",
        "definition": "定义",
        "benchmark": "行业基准"
      }
    ],
    "channel_metrics": [...],
    "content_metrics": [...],
    "community_metrics": [...]
  },
  "dashboard_design": {
    "executive_dashboard": {
      "refresh": "刷新频率",
      "metrics": ["指标1", "指标2"],
      "visualizations": ["图表类型"]
    },
    "operations_dashboard": {...},
    "channel_dashboard": {...}
  },
  "experiment_plan": [
    {
      "experiment_name": "实验名称",
      "hypothesis": "假设",
      "test_type": "类型",
      "control": "对照组",
      "treatment": "实验组",
      "primary_metric": "主要指标",
      "sample_size": "样本量",
      "duration": "周期",
      "expected_lift": "预期提升"
    }
  ],
  "review_cadence": {
    "daily": {"focus": "关注点", "actions": ["动作"]},
    "weekly": {"template": "模板", "participants": ["参与者"]},
    "monthly": {"template": "模板", "deliverables": ["交付物"]}
  },
  "data_sources": [
    {
      "source": "数据源",
      "metrics": ["提供的指标"],
      "integration": "集成方式"
    }
  ],
  "alerts": [
    {
      "trigger": "触发条件",
      "threshold": "阈值",
      "action": "响应动作"
    }
  ]
}
```

请用JSON格式响应。"""


class DataAnalystAgent(BaseAgent):
    """Data & Experiment Analyst for metrics and optimization."""

    def __init__(self):
        super().__init__(
            name="Data Analyst",
            system_prompt=DATA_ANALYST_SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            temperature=0.3,  # Lower temperature for analytical precision
        )

    async def execute(self, state: GrowthWorkflowState) -> GrowthWorkflowState:
        """
        Design metrics framework and experiment plan.
        """
        context = {
            "institution_info": state.get("institution_info", {}),
            "historical_data": state.get("historical_data", {}),
            "agent_outputs": state.get("agent_outputs", {}),
        }

        prompt = self._create_analysis_prompt(state)

        try:
            response = await self.invoke(prompt, context)

            analyst_output = self._structure_output(response)

            state["agent_outputs"]["data_analyst"] = analyst_output

            state["messages"].append({
                "role": "assistant",
                "agent": "data_analyst",
                "content": f"Designed metrics framework with {len(analyst_output.get('experiment_plan', []))} experiments planned",
            })

            logger.info(
                "Data Analyst completed",
                workflow_id=state["workflow_id"],
                experiments=len(analyst_output.get("experiment_plan", [])),
            )

        except Exception as e:
            logger.error("Data Analyst failed", error=str(e))
            state["agent_outputs"]["data_analyst"] = {"error": str(e)}

        return state

    def _create_analysis_prompt(self, state: GrowthWorkflowState) -> str:
        """Create data analysis prompt."""
        institution = state.get("institution_info", {})
        existing_outputs = state.get("agent_outputs", {})

        # Summarize what other agents have produced
        outputs_summary = []
        if existing_outputs.get("content_factory"):
            outputs_summary.append("- 内容策略已生成")
        if existing_outputs.get("community_ops"):
            outputs_summary.append("- 社群运营体系已设计")
        if existing_outputs.get("influencer_matching"):
            outputs_summary.append("- 博主合作框架已建立")
        if existing_outputs.get("product_strategy"):
            outputs_summary.append("- 产品策略已制定")

        outputs_text = "\n".join(outputs_summary) if outputs_summary else "尚无其他智能体输出"

        return f"""请为这家医美机构设计数据驱动的增长体系：

## 机构信息
- 城市：{institution.get('city', '一线城市')}
- 定位：{institution.get('tier', '中高端')}
- 主营项目：{institution.get('main_services', ['综合医美'])}

## 已完成的策略
{outputs_text}

## 设计任务

1. **指标体系**：定义北极星指标和各层级漏斗指标
2. **看板设计**：设计管理层/运营层/渠道层三级看板
3. **实验计划**：基于已有策略，规划5-10个A/B测试
4. **复盘机制**：设计日/周/月复盘模板和流程
5. **预警机制**：定义关键指标的异常预警规则

## 特别要求

- 指标定义必须清晰可量化
- 实验设计必须有明确的假设和成功标准
- 看板字段必须可从现有数据源获取
- 复盘模板必须可直接使用"""

    def _structure_output(self, response: dict[str, Any]) -> dict[str, Any]:
        """Structure the data analyst output."""
        if isinstance(response, str):
            return {"raw_response": response}

        return {
            "metrics_framework": response.get("metrics_framework", {}),
            "dashboard_design": response.get("dashboard_design", {}),
            "experiment_plan": response.get("experiment_plan", []),
            "review_cadence": response.get("review_cadence", {}),
            "data_sources": response.get("data_sources", []),
            "alerts": response.get("alerts", []),
        }


async def data_analyst_node(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """LangGraph node wrapper for data analyst agent."""
    agent = DataAnalystAgent()
    return await agent.execute(state)
