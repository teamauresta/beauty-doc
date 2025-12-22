"""
Product Strategy Engine Agent - AI产品策略引擎

Responsibilities:
1. Analyze market trends and popular treatments
2. Recommend product bundles and pricing strategies
3. Optimize product mix for profitability and demand
4. Plan seasonal promotions and new product launches

Inputs:
- Project catalog (项目库)
- Market hot-selling data
- User search terms
- Seasonal trends
"""

from typing import Any
import structlog

from backend.agents.agents.base import BaseAgent
from backend.agents.graph.state import GrowthWorkflowState

logger = structlog.get_logger()

PRODUCT_STRATEGY_SYSTEM_PROMPT = """你是「AI产品策略引擎」负责人，专门为医美机构优化产品策略和定价。

## 你的核心目标

1. **爆款组合**：设计高需求、高利润的项目组合
2. **定价优化**：根据市场和竞争制定最优价格
3. **上新节奏**：规划新品引入和老品淘汰
4. **季节策略**：针对淡旺季制定差异化策略

## 产品策略框架

### 项目分类
1. **引流款**：低价高频，吸引新客
   - 小气泡、补水针、光子嫩肤基础版
   - 定价策略：低于市场均价10-20%
   - 目标：获客成本控制

2. **利润款**：高客单、高毛利
   - 热玛吉、超声刀、埋线提升
   - 定价策略：保持品质溢价
   - 目标：贡献主要利润

3. **形象款**：塑造专业形象
   - 前沿技术、独家设备
   - 定价策略：高端定位
   - 目标：品牌差异化

4. **复购款**：维持客户粘性
   - 注射类（玻尿酸、肉毒素）
   - 定价策略：会员价、疗程价
   - 目标：提高复购率

### 组合设计原则
- 「引流款 + 利润款」捆绑
- 「新客专享」vs「老客回馈」差异化
- 「单次」vs「疗程」价格锚定
- 「基础版」→「进阶版」→「尊享版」升级路径

### 定价策略
1. **成本加成法**：成本 × (1 + 目标毛利率)
2. **竞争定价法**：参考竞品 ± 差异化溢价
3. **价值定价法**：基于客户感知价值
4. **心理定价法**：9结尾、套餐优惠感

### 季节性策略
- **春季**（3-5月）：焕肤、祛斑、轻医美
- **夏季**（6-8月）：脱毛、控油、防晒后修复
- **秋季**（9-11月）：抗衰、紧致、大项目
- **冬季**（12-2月）：恢复期长的项目、年终促销

## 输出格式

```json
{
  "product_matrix": {
    "traffic_drivers": [
      {
        "name": "项目名",
        "original_price": 0,
        "recommended_price": 0,
        "target_audience": "目标人群",
        "conversion_path": "后续转化路径"
      }
    ],
    "profit_makers": [...],
    "brand_builders": [...],
    "retention_drivers": [...]
  },
  "bundle_recommendations": [
    {
      "bundle_name": "组合名称",
      "included_items": ["项目1", "项目2"],
      "original_total": 0,
      "bundle_price": 0,
      "discount_rate": "折扣率",
      "target_scenario": "适用场景",
      "upsell_opportunity": "升级机会"
    }
  ],
  "pricing_adjustments": [
    {
      "item": "项目名",
      "current_price": 0,
      "recommended_price": 0,
      "reasoning": "调价理由",
      "expected_impact": "预期影响"
    }
  ],
  "seasonal_plan": {
    "current_season": "当前季节",
    "focus_items": ["主推项目"],
    "promotion_theme": "促销主题",
    "marketing_angle": "营销角度"
  },
  "launch_calendar": [
    {
      "month": "月份",
      "action": "上新|促销|淘汰",
      "items": ["项目"],
      "rationale": "理由"
    }
  ]
}
```

请用JSON格式响应。"""


class ProductStrategyAgent(BaseAgent):
    """Product Strategy Engine for pricing and bundling optimization."""

    def __init__(self):
        super().__init__(
            name="Product Strategy",
            system_prompt=PRODUCT_STRATEGY_SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            temperature=0.5,
        )

    async def execute(self, state: GrowthWorkflowState) -> GrowthWorkflowState:
        """
        Analyze products and recommend strategies.
        """
        context = {
            "institution_info": state.get("institution_info", {}),
            "project_catalog": state.get("project_catalog", []),
            "historical_data": state.get("historical_data", {}),
        }

        prompt = self._create_strategy_prompt(state)

        try:
            response = await self.invoke(prompt, context)

            strategy_output = self._structure_output(response)

            state["agent_outputs"]["product_strategy"] = strategy_output

            state["messages"].append({
                "role": "assistant",
                "agent": "product_strategy",
                "content": f"Created {len(strategy_output.get('bundle_recommendations', []))} bundle recommendations and {len(strategy_output.get('pricing_adjustments', []))} pricing adjustments",
            })

            logger.info(
                "Product Strategy completed",
                workflow_id=state["workflow_id"],
                bundles=len(strategy_output.get("bundle_recommendations", [])),
            )

        except Exception as e:
            logger.error("Product Strategy failed", error=str(e))
            state["agent_outputs"]["product_strategy"] = {"error": str(e)}

        return state

    def _create_strategy_prompt(self, state: GrowthWorkflowState) -> str:
        """Create product strategy prompt."""
        catalog = state.get("project_catalog", [])
        institution = state.get("institution_info", {})

        # Format catalog if available
        if catalog:
            catalog_text = "\n".join([
                f"- {item.get('name', 'Unknown')}: ¥{item.get('price', 'N/A')} (毛利: {item.get('margin', 'N/A')})"
                for item in catalog[:20]
            ])
        else:
            catalog_text = "【未提供项目库，请基于行业通用项目进行分析】"

        return f"""请为这家医美机构制定产品策略：

## 机构信息
- 城市：{institution.get('city', '一线城市')}
- 定位：{institution.get('tier', '中高端')}
- 主营：{institution.get('main_services', ['综合医美'])}

## 现有项目库
{catalog_text}

## 策略任务

1. **项目分类**：将项目划分为引流款/利润款/形象款/复购款
2. **组合设计**：设计3-5个高转化的项目组合
3. **定价建议**：识别需要调价的项目
4. **季节规划**：制定当季主推策略
5. **上新节奏**：规划未来3个月的产品动作

请给出具体可执行的产品策略建议。"""

    def _structure_output(self, response: dict[str, Any]) -> dict[str, Any]:
        """Structure the product strategy output."""
        if isinstance(response, str):
            return {"raw_response": response}

        return {
            "product_matrix": response.get("product_matrix", {}),
            "bundle_recommendations": response.get("bundle_recommendations", []),
            "pricing_adjustments": response.get("pricing_adjustments", []),
            "seasonal_plan": response.get("seasonal_plan", {}),
            "launch_calendar": response.get("launch_calendar", []),
        }


async def product_strategy_node(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """LangGraph node wrapper for product strategy agent."""
    agent = ProductStrategyAgent()
    return await agent.execute(state)
