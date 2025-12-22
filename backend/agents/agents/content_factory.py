"""
Content Factory Agent - AI内容生成系统

Responsibilities:
1. Generate viral content topics (爆款选题)
2. Create long-term brand columns (资产型栏目)
3. Produce platform-specific content (小红书/抖音/视频号)
4. Script writing with hooks and CTAs

Output Requirements (per specification):
- 10 viral topics per platform
- 5 long-term brand columns
- Each topic includes: title structure, script outline, shot suggestions, comment guidance, conversion hooks
"""

from typing import Any
import structlog

from backend.agents.agents.base import BaseAgent
from backend.agents.graph.state import GrowthWorkflowState

logger = structlog.get_logger()

CONTENT_FACTORY_SYSTEM_PROMPT = """你是「AI内容生成系统」负责人，专门为中国医美机构生产高转化内容。

## 你的核心目标

1. **爆款型内容**：快速获取流量和关注
2. **资产型内容**：建立长期信任和品牌认知
3. **转化型内容**：引导咨询和到店

## 内容生产线

选题 → 脚本 → 拍摄建议 → 剪辑指导 → 发布策略 → 互动引导 → 复盘优化

## 平台特性理解

### 小红书
- 用户画像：25-40岁女性，关注变美、生活品质
- 内容形式：图文笔记为主，真实感强
- 爆款要素：情绪共鸣、干货价值、视觉美感
- 禁忌：硬广、夸张功效、医疗术语

### 抖音
- 用户画像：18-45岁，娱乐为主
- 内容形式：15-60秒短视频
- 爆款要素：前3秒hook、节奏感、反转
- 禁忌：医疗手术画面、功效承诺

### 视频号/微信
- 用户画像：30-50岁，信任关系强
- 内容形式：中长视频、直播
- 爆款要素：专业背书、真实案例、深度科普
- 禁忌：过于年轻化、娱乐化

## 输出格式

必须输出JSON，包含：
```json
{
  "viral_topics": [
    {
      "platform": "xiaohongshu|douyin|weixin",
      "title": "标题",
      "title_structure": "标题公式说明",
      "hook": "开头钩子",
      "script_outline": ["要点1", "要点2", "要点3"],
      "shot_suggestions": ["镜头1", "镜头2"],
      "comment_guide": "评论区引导语",
      "conversion_hook": "转化钩子",
      "best_posting_time": "发布时间建议"
    }
  ],
  "brand_columns": [
    {
      "column_name": "栏目名称",
      "positioning": "定位",
      "target_audience": "目标人群",
      "content_frequency": "更新频率",
      "sample_topics": ["选题1", "选题2", "选题3"]
    }
  ],
  "content_calendar": {
    "week_1": [...],
    "week_2": [...]
  }
}
```

## 合规红线

- 不能出现"效果保证"、"100%有效"等绝对化用语
- 不能出现真人手术过程
- 不能使用患者案例作为效果证明（需模糊处理）
- 不能使用医生个人形象做效果背书（315后限制）
- 产品功效只能说明成分作用，不能说明治疗效果

请用JSON格式响应。"""


class ContentFactoryAgent(BaseAgent):
    """Content Factory agent for generating marketing content."""

    def __init__(self):
        super().__init__(
            name="Content Factory",
            system_prompt=CONTENT_FACTORY_SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            temperature=0.8,  # Higher creativity for content generation
        )

    async def execute(self, state: GrowthWorkflowState) -> GrowthWorkflowState:
        """
        Generate content plan:
        1. Analyze institution characteristics
        2. Generate viral topics for each platform
        3. Create brand column structure
        4. Build content calendar
        """
        # Build context
        context = {
            "institution_info": state.get("institution_info", {}),
            "project_catalog": state.get("project_catalog", []),
            "compliance_rules": state.get("compliance_rules", {}),
            "historical_data": state.get("historical_data", {}),
            "orchestrator_plan": state.get("agent_outputs", {}).get("orchestrator", {}),
        }

        # Generate content prompt
        prompt = self._create_content_prompt(state)

        try:
            response = await self.invoke(prompt, context)

            # Validate and structure response
            content_output = self._structure_content_output(response)

            # Store in state
            state["agent_outputs"]["content_factory"] = content_output

            # Add message for conversation history
            state["messages"].append({
                "role": "assistant",
                "agent": "content_factory",
                "content": f"Generated {len(content_output.get('viral_topics', []))} viral topics and {len(content_output.get('brand_columns', []))} brand columns",
            })

            state["current_phase"] = "content_generated"

            logger.info(
                "Content Factory completed",
                workflow_id=state["workflow_id"],
                topic_count=len(content_output.get("viral_topics", [])),
                column_count=len(content_output.get("brand_columns", [])),
            )

        except Exception as e:
            logger.error("Content Factory failed", error=str(e))
            state["error"] = str(e)
            state["agent_outputs"]["content_factory"] = {"error": str(e)}

        return state

    def _create_content_prompt(self, state: GrowthWorkflowState) -> str:
        """Create content generation prompt."""
        institution = state.get("institution_info", {})

        # Extract key info
        city = institution.get("city", "一线城市")
        tier = institution.get("tier", "中高端")
        main_services = institution.get("main_services", ["玻尿酸", "光子嫩肤"])

        return f"""请为这家医美机构生成内容计划：

## 机构特点
- 城市：{city}
- 定位：{tier}
- 主打项目：{', '.join(main_services) if isinstance(main_services, list) else main_services}

## 任务要求

1. 生成10个爆款选题（分布在小红书、抖音、视频号）
2. 设计5个长期资产栏目
3. 制作2周内容日历

## 选题方向建议

爆款型：
- 变美干货（成分科普、项目对比）
- 避坑指南（如何选医生、识别假货）
- 真实体验（模糊化处理的案例分享）
- 热点蹭流（明星同款、综艺同款）

资产型：
- 医生权威（专业背景、学术成就）
- 审美教育（面部比例、风格分析）
- 科普系列（成分解读、技术原理）
- 生活方式（术后护理、日常保养）

请生成完整的内容计划。"""

    def _structure_content_output(self, response: dict[str, Any]) -> dict[str, Any]:
        """Structure and validate content output."""
        # Handle both raw and structured responses
        if isinstance(response, str):
            return {"raw_content": response, "viral_topics": [], "brand_columns": []}

        # Ensure required fields exist
        output = {
            "viral_topics": response.get("viral_topics", []),
            "brand_columns": response.get("brand_columns", []),
            "content_calendar": response.get("content_calendar", {}),
        }

        # Add metadata
        output["generated_at"] = "now"
        output["platform_distribution"] = self._count_by_platform(output["viral_topics"])

        return output

    def _count_by_platform(self, topics: list[dict]) -> dict[str, int]:
        """Count topics by platform."""
        counts = {"xiaohongshu": 0, "douyin": 0, "weixin": 0}
        for topic in topics:
            platform = topic.get("platform", "").lower()
            if platform in counts:
                counts[platform] += 1
        return counts


async def content_factory_node(state: GrowthWorkflowState) -> GrowthWorkflowState:
    """LangGraph node wrapper for content factory agent."""
    agent = ContentFactoryAgent()
    return await agent.execute(state)
