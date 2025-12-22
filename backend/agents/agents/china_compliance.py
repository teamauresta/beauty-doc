"""
China Compliance Agent - 中国市场合规负责人

Responsibilities:
1. Review all content for regulatory compliance
2. Ensure 315 regulations adherence
3. Check platform-specific rules
4. Provide compliant alternative expressions

Compliance Areas:
- Medical advertising law (医疗广告法)
- 315 post-regulation environment
- Doctor KOS/IP restrictions
- Platform content policies (Xiaohongshu, Douyin, WeChat)
"""

from typing import Any
import structlog

from backend.agents.agents.base import BaseAgent
from backend.agents.graph.state import GrowthWorkflowState

logger = structlog.get_logger()

COMPLIANCE_SYSTEM_PROMPT = """你是「中国市场合规负责人」，负责确保所有医美营销内容符合中国法规和平台规则。

## 你的核心职责

1. **法规审核**：检查内容是否违反医疗广告法、消费者权益保护法
2. **平台规则**：确保符合小红书、抖音、微信等平台的内容政策
3. **风险预警**：标识高风险表述，提供合规替代方案
4. **315合规**：确保符合315后的新监管环境

## 合规红线清单

### 绝对禁止
1. ❌ 效果保证类：「100%有效」「一次见效」「永久保持」
2. ❌ 医疗承诺类：「治愈」「根治」「安全无副作用」
3. ❌ 虚假对比：伪造before/after、使用PS图片
4. ❌ 医生个人背书：医生以个人名义承诺效果
5. ❌ 手术过程展示：真实手术画面、血腥内容
6. ❌ 患者隐私：未经授权使用患者信息/照片

### 高风险（需谨慎）
1. ⚠️ 案例展示：需模糊处理、标注"个体差异"
2. ⚠️ 价格宣传：不能虚假促销、需标明有效期
3. ⚠️ 成分功效：只能说明成分作用，不能说治疗效果
4. ⚠️ 医生IP：可展示专业背景，不可做效果承诺

### 平台特殊规则

#### 小红书
- 医美内容需标注"广告"
- 不能使用"医生推荐"作为卖点
- 图片不能过度美化

#### 抖音
- 医美类目需资质认证
- 不能挂购买链接
- 直播不能展示治疗过程

#### 微信
- 朋友圈广告需审核
- 公众号医美内容有限制
- 小程序不能直接销售医美服务

## 合规替代话术库

原表述 → 合规表述：
- 「立竿见影」→「即刻看到变化」
- 「永久效果」→「持久美丽」
- 「无副作用」→「临床验证的安全技术」
- 「医生推荐」→「专业团队服务」
- 「治愈」→「改善」「调理」
- 「100%成功」→「众多顾客好评」

## 输出格式

```json
{
  "compliance_status": "pass|warning|fail",
  "reviewed_items": [
    {
      "item_id": "内容ID",
      "original_text": "原文",
      "issues": [
        {
          "type": "violation|warning",
          "rule": "违反的规则",
          "description": "问题说明",
          "suggestion": "合规替代方案"
        }
      ],
      "compliant_version": "合规修改版本"
    }
  ],
  "risk_summary": {
    "high_risk_count": 0,
    "medium_risk_count": 0,
    "low_risk_count": 0
  },
  "recommendations": ["总体建议1", "总体建议2"]
}
```

请用JSON格式响应。"""


class ChinaComplianceAgent(BaseAgent):
    """China Compliance agent for regulatory review."""

    def __init__(self):
        super().__init__(
            name="China Compliance",
            system_prompt=COMPLIANCE_SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            temperature=0.2,  # Low temperature for consistent compliance checks
        )

    async def execute(self, state: GrowthWorkflowState) -> GrowthWorkflowState:
        """
        Review content for compliance:
        1. Check each piece of content
        2. Identify violations and warnings
        3. Provide compliant alternatives
        """
        # Get content to review
        content_output = state.get("agent_outputs", {}).get("content_factory", {})

        if not content_output or content_output.get("error"):
            logger.warning("No content to review", workflow_id=state["workflow_id"])
            state["agent_outputs"]["china_compliance"] = {
                "compliance_status": "skipped",
                "reason": "No content available for review",
            }
            return state

        # Build review context
        context = {
            "content_to_review": content_output,
            "compliance_rules": state.get("compliance_rules", {}),
            "institution_info": state.get("institution_info", {}),
        }

        prompt = self._create_review_prompt(content_output)

        try:
            response = await self.invoke(prompt, context)

            # Structure compliance output
            compliance_output = self._structure_compliance_output(response)

            state["agent_outputs"]["china_compliance"] = compliance_output

            # Add to messages
            status = compliance_output.get("compliance_status", "unknown")
            state["messages"].append({
                "role": "assistant",
                "agent": "china_compliance",
                "content": f"Compliance review complete. Status: {status}",
            })

            logger.info(
                "Compliance review completed",
                workflow_id=state["workflow_id"],
                status=status,
                issues=compliance_output.get("risk_summary", {}).get("high_risk_count", 0),
            )

        except Exception as e:
            logger.error("Compliance review failed", error=str(e))
            state["agent_outputs"]["china_compliance"] = {
                "compliance_status": "error",
                "error": str(e),
            }

        return state

    def _create_review_prompt(self, content: dict[str, Any]) -> str:
        """Create compliance review prompt."""
        # Extract topics for review
        topics = content.get("viral_topics", [])
        columns = content.get("brand_columns", [])

        topics_text = "\n".join([
            f"- [{t.get('platform', 'unknown')}] {t.get('title', 'Untitled')}: {t.get('hook', '')}"
            for t in topics[:10]  # Limit to first 10
        ])

        columns_text = "\n".join([
            f"- {c.get('column_name', 'Unnamed')}: {c.get('positioning', '')}"
            for c in columns[:5]
        ])

        return f"""请审核以下医美营销内容的合规性：

## 爆款选题（待审核）
{topics_text}

## 品牌栏目（待审核）
{columns_text}

请检查：
1. 是否有违反医疗广告法的表述
2. 是否符合315后的监管要求
3. 是否符合各平台内容政策
4. 是否有高风险表述需要修改

对每个问题提供具体的合规修改建议。"""

    def _structure_compliance_output(self, response: dict[str, Any]) -> dict[str, Any]:
        """Structure compliance review output."""
        if isinstance(response, str):
            return {
                "compliance_status": "unknown",
                "raw_response": response,
            }

        # Ensure required fields
        output = {
            "compliance_status": response.get("compliance_status", "unknown"),
            "reviewed_items": response.get("reviewed_items", []),
            "risk_summary": response.get("risk_summary", {
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
            }),
            "recommendations": response.get("recommendations", []),
        }

        # Determine overall status if not provided
        if output["compliance_status"] == "unknown":
            high_risk = output["risk_summary"].get("high_risk_count", 0)
            if high_risk > 0:
                output["compliance_status"] = "fail"
            elif output["risk_summary"].get("medium_risk_count", 0) > 0:
                output["compliance_status"] = "warning"
            else:
                output["compliance_status"] = "pass"

        return output


async def china_compliance_node(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """LangGraph node wrapper for compliance agent."""
    agent = ChinaComplianceAgent()
    return await agent.execute(state)
