"""
Community Ops Bot Agent - AI社群运营机器人

Responsibilities:
1. Design conversation flows for different customer tiers
2. Create trigger-based response scripts
3. Build FAQ knowledge base
4. Define human handoff rules
5. Craft promotion and closing scripts

Customer Tiers:
- 路人 (Stranger): First contact, awareness stage
- 意向 (Interested): Showed interest, considering
- 强意向 (High Intent): Ready to book, comparing options
- 复购 (Returning): Past customer, loyalty focus
"""

from typing import Any
import structlog

from backend.agents.agents.base import BaseAgent
from backend.agents.graph.state import GrowthWorkflowState

logger = structlog.get_logger()

COMMUNITY_OPS_SYSTEM_PROMPT = """你是「AI社群运营机器人」负责人，专门设计医美机构的社群转化体系。

## 你的核心目标

1. **7×24自动应答**：设计智能对话流程
2. **分层运营**：针对不同客户阶段差异化沟通
3. **促单转化**：设计高转化的话术和触发机制
4. **转人工规则**：确保复杂问题无缝交接

## 客户分层体系

### 第一层：路人（Stranger）
- 特征：首次接触，浏览为主，问题泛泛
- 策略：建立信任、提供价值、收集信息
- 话术风格：热情但不急躁，专业但不冷淡
- 目标：留下联系方式，进入下一层

### 第二层：意向（Interested）
- 特征：主动咨询，有具体问题，比较选项
- 策略：解答疑虑、展示优势、创造紧迫感
- 话术风格：专业解答，同理心强
- 目标：预约到店，进入强意向

### 第三层：强意向（High Intent）
- 特征：准备行动，关心价格/时间/医生
- 策略：促单、限时优惠、消除最后顾虑
- 话术风格：果断、稀缺感、价值强调
- 目标：完成预约，到店转化

### 第四层：复购（Returning）
- 特征：已成交客户，体验过服务
- 策略：满意度跟进、复购推荐、转介绍激励
- 话术风格：亲切、VIP感、专属优惠
- 目标：复购、转介绍、提升LTV

## 关键触发器设计

### 咨询类触发器
- 「多少钱」「价格」「费用」→ 报价话术 + 限时优惠
- 「效果」「能保持多久」→ 效果说明 + 案例展示
- 「疼不疼」「恢复期」→ 体验说明 + 术后服务

### 犹豫类触发器
- 「再考虑」「不急」→ 种草内容 + 软性跟进
- 「太贵了」→ 价值重塑 + 分期方案
- 「怕不自然」→ 审美沟通 + 医生专业性

### 竞品类触发器
- 「别家更便宜」→ 差异化价值 + 隐性成本
- 「朋友推荐XX」→ 尊重选择 + 独特优势

### 时间类触发器
- 「什么时候有空」→ 快速锁定时间
- 「月底再说」→ 月底提醒 + 专属名额

## 话术风格库

### 温柔型（适合高端客户、敏感话题）
- 「完全理解您的顾虑，这是很多姐妹最初都会有的想法...」
- 「没关系，变美是一件值得慎重的事情...」

### 专业型（适合理性客户、效果咨询）
- 「从医学角度来说，这个项目的原理是...」
- 「根据您描述的情况，建议先做个面诊评估...」

### 稀缺型（适合促单、限时活动）
- 「这个价格是本月限定，只剩最后3个名额...」
- 「张医生下周的档期很紧张，建议尽快预约...」

## 转人工规则

### 必须转人工
- 投诉类：任何负面情绪、不满表达
- 复杂医疗：具体治疗方案、术后问题
- 大额交易：客单价超过设定阈值
- 要求转人工：客户明确要求

### 转前准备
- 生成对话摘要
- 标注客户意向等级
- 提取关键需求
- 推荐跟进策略

## 输出格式

```json
{
  "conversation_tiers": {
    "stranger": {
      "entry_criteria": "判断标准",
      "greeting_script": "开场白",
      "key_questions": ["信息收集问题"],
      "value_hooks": ["价值点"],
      "next_tier_trigger": "升级条件"
    },
    "interested": {...},
    "high_intent": {...},
    "returning": {...}
  },
  "trigger_responses": [
    {
      "trigger_keywords": ["关键词1", "关键词2"],
      "trigger_type": "inquiry|hesitation|competition|timing",
      "responses": {
        "warm": "温柔版话术",
        "professional": "专业版话术",
        "scarcity": "稀缺版话术"
      },
      "follow_up_action": "后续动作"
    }
  ],
  "faq_knowledge_base": [
    {
      "category": "类别",
      "question": "问题",
      "answer": "标准答案",
      "variations": ["问法变体"],
      "related_upsell": "关联推荐"
    }
  ],
  "handoff_rules": {
    "mandatory_handoff": ["必须转人工场景"],
    "optional_handoff": ["可选转人工场景"],
    "handoff_template": "转人工时的信息模板"
  },
  "closing_scripts": {
    "soft_close": "软性促单话术",
    "urgency_close": "紧迫感促单",
    "value_close": "价值促单",
    "objection_handles": {
      "price": "价格异议处理",
      "timing": "时间异议处理",
      "trust": "信任异议处理"
    }
  }
}
```

请用JSON格式响应。"""


class CommunityOpsAgent(BaseAgent):
    """Community Operations Bot for social conversion design."""

    def __init__(self):
        super().__init__(
            name="Community Ops",
            system_prompt=COMMUNITY_OPS_SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            temperature=0.7,
        )

    async def execute(self, state: GrowthWorkflowState) -> GrowthWorkflowState:
        """
        Design community operations and conversation flows.
        """
        context = {
            "institution_info": state.get("institution_info", {}),
            "existing_sops": state.get("existing_sops", {}),
            "project_catalog": state.get("project_catalog", []),
        }

        prompt = self._create_ops_prompt(state)

        try:
            response = await self.invoke(prompt, context)

            ops_output = self._structure_output(response)

            state["agent_outputs"]["community_ops"] = ops_output

            state["messages"].append({
                "role": "assistant",
                "agent": "community_ops",
                "content": f"Designed {len(ops_output.get('trigger_responses', []))} trigger responses and {len(ops_output.get('faq_knowledge_base', []))} FAQ entries",
            })

            logger.info(
                "Community Ops completed",
                workflow_id=state["workflow_id"],
                triggers=len(ops_output.get("trigger_responses", [])),
            )

        except Exception as e:
            logger.error("Community Ops failed", error=str(e))
            state["agent_outputs"]["community_ops"] = {"error": str(e)}

        return state

    def _create_ops_prompt(self, state: GrowthWorkflowState) -> str:
        """Create community ops prompt."""
        institution = state.get("institution_info", {})
        services = institution.get("main_services", [])

        return f"""请为这家医美机构设计完整的社群运营体系：

## 机构信息
- 定位：{institution.get('tier', '中高端')}
- 主营项目：{', '.join(services) if isinstance(services, list) else services}
- 目标客群：{institution.get('target_audience', '25-45岁女性')}

## 设计任务

1. **客户分层**：设计4层客户分级体系及对应话术
2. **触发器响应**：设计至少10个关键场景的自动回复
3. **FAQ知识库**：整理常见问题及标准答案
4. **转人工规则**：明确何时必须转人工
5. **促单话术**：设计不同风格的成交话术

## 特别要求

- 所有话术必须符合医疗广告法规
- 不能承诺治疗效果
- 价格需标注"面诊后确定"
- 保持专业与亲和的平衡"""

    def _structure_output(self, response: dict[str, Any]) -> dict[str, Any]:
        """Structure the community ops output."""
        if isinstance(response, str):
            return {"raw_response": response}

        return {
            "conversation_tiers": response.get("conversation_tiers", {}),
            "trigger_responses": response.get("trigger_responses", []),
            "faq_knowledge_base": response.get("faq_knowledge_base", []),
            "handoff_rules": response.get("handoff_rules", {}),
            "closing_scripts": response.get("closing_scripts", {}),
        }


async def community_ops_node(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """LangGraph node wrapper for community ops agent."""
    agent = CommunityOpsAgent()
    return await agent.execute(state)
