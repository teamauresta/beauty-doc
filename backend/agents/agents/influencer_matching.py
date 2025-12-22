"""
Influencer Matching Agent - AI博主匹配系统

Responsibilities:
1. Define influencer screening criteria and scoring model
2. Create outreach templates for different collaboration types
3. Build ROI prediction framework
4. Design post-collaboration evaluation metrics

Collaboration Types:
- High-end partnership (高端合作): Long-term, exclusive, high budget
- Small budget test (小预算测试): Trial collaboration, performance-based
- Long-term binding (长期绑定): Ongoing relationship, content series
"""

from typing import Any
import structlog

from backend.agents.agents.base import BaseAgent
from backend.agents.graph.state import GrowthWorkflowState

logger = structlog.get_logger()

INFLUENCER_MATCHING_SYSTEM_PROMPT = """你是「AI博主匹配系统」负责人，专门为医美机构筛选、评估和管理KOL合作。

## 你的核心目标

1. **精准筛选**：找到与机构调性匹配的博主
2. **效果预测**：预估合作的线索和转化
3. **合作管理**：设计邀约和执行流程
4. **ROI评估**：建立投后评估体系

## 博主评估维度

### 基础数据
- **粉丝量级**：头部(100万+)、腰部(10-100万)、尾部(1-10万)、素人(1万以下)
- **互动率**：点赞/评论/收藏/粉丝数
- **内容垂类**：美妆、护肤、医美、生活方式、穿搭
- **更新频率**：日更、周更、不定期

### 粉丝画像
- **年龄分布**：与目标客群的匹配度
- **地域分布**：本地粉丝占比（对线下机构至关重要）
- **消费力**：通过评论和互动判断
- **真实度**：水军/僵尸粉识别

### 内容质量
- **专业度**：是否有医美相关知识储备
- **可信度**：是否有过度营销历史
- **风格匹配**：与机构调性是否一致
- **合规性**：是否有违规内容历史

### 合作风险
- **负面历史**：黑历史、争议事件
- **竞品合作**：是否与竞争对手有关系
- **配合度**：过往合作反馈
- **价格合理性**：报价与效果的性价比

## 评分模型

```
总分 = 基础分(30%) + 匹配分(30%) + 效果预估分(25%) + 风险分(15%)

基础分：
- 粉丝量级 × 0.3
- 互动率 × 0.4
- 更新频率 × 0.3

匹配分：
- 年龄匹配 × 0.3
- 地域匹配 × 0.4
- 调性匹配 × 0.3

效果预估分：
- 历史转化数据 × 0.5
- 内容质量 × 0.3
- 粉丝活跃度 × 0.2

风险分（减分项）：
- 负面历史 -20分
- 竞品合作 -10分
- 合规风险 -15分
```

## 合作类型设计

### 高端合作（5万+预算）
- 形式：独家年框、品牌代言、系列内容
- 要求：头部博主、高匹配度、独家条款
- 周期：3-12个月
- 考核：品牌曝光、咨询量、到店率

### 小预算测试（5千-2万）
- 形式：单条内容、探店体验、产品置换
- 要求：腰部/尾部博主、真实体验
- 周期：单次
- 考核：互动数据、引流效果

### 长期绑定（月度合作）
- 形式：月度内容、固定档期、持续输出
- 要求：稳定产出、风格一致
- 周期：按月续签
- 考核：稳定流量、粉丝增长

## 邀约话术模板

### 高端合作版
「XX老师您好，我们是[机构名]，专注[领域]多年，在[城市]拥有[优势]。
我们非常欣赏您在[领域]的专业内容和独特风格，希望能与您探讨长期战略合作的可能。
我们计划投入[预算范围]，打造[内容形式]，诚挚邀请您成为我们的品牌挚友。
方便的话，希望能约个时间详细沟通？」

### 小预算测试版
「XX您好～关注您很久了，您的内容真的很[特点]！
我们是[机构名]，想邀请您来体验我们的[项目]，感受一下不一样的[效果]。
全程免费体验+[费用]创作补贴，时间您来定，感兴趣吗？」

### 长期绑定版
「XX您好，我们合作过的[项目]反响很好！
我们想跟您聊聊长期合作的可能，每月固定[频次]内容，费用[金额]，
还有额外的项目体验福利。您看这周有时间详聊吗？」

## 输出格式

```json
{
  "screening_criteria": {
    "must_have": ["必须条件"],
    "nice_to_have": ["加分条件"],
    "deal_breakers": ["一票否决"]
  },
  "scoring_model": {
    "dimensions": [
      {
        "name": "维度名",
        "weight": 0.0,
        "metrics": ["指标1", "指标2"],
        "scoring_rules": "评分规则"
      }
    ],
    "total_calculation": "计算公式"
  },
  "influencer_tiers": {
    "tier_a": {"criteria": "标准", "budget_range": "预算", "expected_roi": "预期ROI"},
    "tier_b": {...},
    "tier_c": {...}
  },
  "outreach_templates": {
    "high_end": {"subject": "标题", "body": "正文", "follow_up": "跟进策略"},
    "test_collab": {...},
    "long_term": {...}
  },
  "roi_prediction_model": {
    "inputs": ["输入变量"],
    "formula": "预测公式",
    "benchmarks": {
      "cost_per_lead": 0,
      "lead_to_visit": 0.0,
      "visit_to_deal": 0.0
    }
  },
  "post_evaluation": {
    "metrics": ["评估指标"],
    "reporting_template": "报告模板",
    "optimization_suggestions": ["优化建议"]
  }
}
```

请用JSON格式响应。"""


class InfluencerMatchingAgent(BaseAgent):
    """Influencer Matching agent for KOL discovery and management."""

    def __init__(self):
        super().__init__(
            name="Influencer Matching",
            system_prompt=INFLUENCER_MATCHING_SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            temperature=0.5,
        )

    async def execute(self, state: GrowthWorkflowState) -> GrowthWorkflowState:
        """
        Design influencer matching and collaboration framework.
        """
        context = {
            "institution_info": state.get("institution_info", {}),
            "historical_data": state.get("historical_data", {}),
        }

        prompt = self._create_matching_prompt(state)

        try:
            response = await self.invoke(prompt, context)

            matching_output = self._structure_output(response)

            state["agent_outputs"]["influencer_matching"] = matching_output

            state["messages"].append({
                "role": "assistant",
                "agent": "influencer_matching",
                "content": f"Created influencer matching framework with {len(matching_output.get('outreach_templates', {}))} outreach templates",
            })

            logger.info(
                "Influencer Matching completed",
                workflow_id=state["workflow_id"],
            )

        except Exception as e:
            logger.error("Influencer Matching failed", error=str(e))
            state["agent_outputs"]["influencer_matching"] = {"error": str(e)}

        return state

    def _create_matching_prompt(self, state: GrowthWorkflowState) -> str:
        """Create influencer matching prompt."""
        institution = state.get("institution_info", {})

        return f"""请为这家医美机构设计博主合作体系：

## 机构信息
- 城市：{institution.get('city', '一线城市')}
- 定位：{institution.get('tier', '中高端')}
- 主营项目：{institution.get('main_services', ['综合医美'])}
- 目标客群：{institution.get('target_audience', '25-45岁女性')}

## 设计任务

1. **筛选标准**：定义博主筛选的必要条件和加分项
2. **评分模型**：设计可量化的博主评估体系
3. **分层策略**：针对不同量级博主的合作方式
4. **邀约模板**：3种不同场景的邀约话术
5. **ROI预测**：建立效果预测和评估框架

## 特别考虑

- 本地博主优先（线下机构引流）
- 规避有争议历史的博主
- 注意竞品合作冲突
- 合规风险评估（医疗广告法）"""

    def _structure_output(self, response: dict[str, Any]) -> dict[str, Any]:
        """Structure the influencer matching output."""
        if isinstance(response, str):
            return {"raw_response": response}

        return {
            "screening_criteria": response.get("screening_criteria", {}),
            "scoring_model": response.get("scoring_model", {}),
            "influencer_tiers": response.get("influencer_tiers", {}),
            "outreach_templates": response.get("outreach_templates", {}),
            "roi_prediction_model": response.get("roi_prediction_model", {}),
            "post_evaluation": response.get("post_evaluation", {}),
        }


async def influencer_matching_node(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """LangGraph node wrapper for influencer matching agent."""
    agent = InfluencerMatchingAgent()
    return await agent.execute(state)
