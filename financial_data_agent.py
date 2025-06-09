# financial_data_agent.py python -m demo.run_financial_data_agent_demo

import logging
from typing import Any, ClassVar, Dict, Type

from app.agents.base.agent import Agent
from app.agents.prompts.financial_data_agent_prompts import (
    SYSTEM_PROMPT,
    generate_financial_prompt
)
from app.agents.schemas.financial_data_agent_schemas import FinancialDataAgentResponse
from app.core.agents.constants import AgentDescription, AgentIcon, AgentType
from app.core.mission.schemas.planner import Task
from app.core.schemas.base import BaseResponseModel
from app.core.types.tool import ToolName

logger = logging.getLogger(__name__)


class FinancialDataAgent(Agent):
    """Agent for analyzing financial data from datasets."""

    agent_type: ClassVar[AgentType] = AgentType.FINANCIAL_ANALYST
    icon: ClassVar[AgentIcon] = AgentIcon.FINANCIAL_ANALYST
    description: ClassVar[AgentDescription] = AgentDescription.FINANCIAL_ANALYST
    system_prompt: ClassVar[str] = SYSTEM_PROMPT
    stream: ClassVar[bool] = True
    default_response_format: ClassVar[Type[BaseResponseModel]] = FinancialDataAgentResponse
    available_tools: ClassVar[list[ToolName]] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the financial data agent."""
        try:
            super().__init__(*args, **kwargs)
        except Exception as err:
            logger.error("Error initializing financial data agent: %s", err)
            raise RuntimeError(f"Failed to initialize financial data agent: {err!s}") from err

    def generate_prompt(self, task: Task, context_variables: Dict[str, Any]) -> str:
        """Generate prompt for the financial data agent."""
        try:
            dataset = context_variables.get("dataset")
        
            if dataset is None:
                raise ValueError("Context variables must include 'dataset'")

            return generate_financial_prompt(
                task=task,
                dataset=dataset
            )
        except Exception as err:
            logger.error("Error generating financial prompt: %s", err)
            raise RuntimeError(f"Failed to generate financial prompt: {err!s}") from err
