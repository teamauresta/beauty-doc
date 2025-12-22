"""
Base Agent class for all specialist agents.

All agents use Claude via langchain-anthropic and share common patterns:
- System prompt with role definition
- Tool binding (platform APIs, compliance checks, etc.)
- Structured output parsing
- Error handling and retry logic
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
import structlog

from backend.app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class BaseAgent(ABC):
    """Base class for all specialist agents."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
    ):
        self.name = name
        self.system_prompt = system_prompt

        self.llm = ChatAnthropic(
            model=model,
            temperature=temperature,
            anthropic_api_key=settings.anthropic_api_key,
            max_tokens=4096,
        )

        self.output_parser = JsonOutputParser()

    @abstractmethod
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent's task. Must be implemented by subclasses."""
        pass

    async def invoke(
        self,
        user_message: str,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Invoke the agent with a message and optional context."""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=self._format_user_message(user_message, context)),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            logger.info(
                f"{self.name} response received",
                tokens=response.usage_metadata.get("total_tokens", 0) if response.usage_metadata else 0,
            )

            # Try to parse as JSON, fall back to raw content
            try:
                return self.output_parser.parse(response.content)
            except Exception:
                return {"raw_response": response.content}

        except Exception as e:
            logger.error(f"{self.name} error", error=str(e))
            raise

    def _format_user_message(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        """Format user message with context."""
        if not context:
            return message

        context_str = "\n".join([
            f"## {key}\n{value}"
            for key, value in context.items()
            if value is not None
        ])

        return f"""# Context
{context_str}

# Task
{message}"""


class AgentOutput(BaseModel):
    """Standard output schema for agents."""
    success: bool
    data: dict[str, Any]
    errors: Optional[list[str]] = None
    warnings: Optional[list[str]] = None
    next_steps: Optional[list[str]] = None
