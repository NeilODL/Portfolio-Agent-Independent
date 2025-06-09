# financial_data_agent_demo.py

"""
Financial Data Agent Demo Module

This module demonstrates the FinancialDataAgent's capabilities with both streaming
and formatted outputs. Run with: python -m demo.run_financial_data_agent_demo
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Type

import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from app.agents.schemas.financial_data_agent_schemas import FinancialDataAgentResponse
from app.core.agents.constants import AgentType
from app.core.mission.schemas.planner import Task
from app.core.registry.agent_initializer import initialize_agents
from app.core.schemas.base import BaseResponseModel
from app.core.agents.types.agent_protocols import AgentProtocol

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def get_financial_agent() -> AgentProtocol:
    """Get a financial data agent with managed lifecycle."""
    components = await initialize_agents()
    agent_registry = components[2]  # Assuming the registry is at index 2
    agent = agent_registry.get_agent(AgentType.FINANCIAL_ANALYST.value)
    if not agent:
        raise RuntimeError("FinancialDataAgent not found in registry")
    return agent

async def run_demo() -> None:
    """Run the financial data agent demo with different test cases."""
    agent = await get_financial_agent()

    # Load the spreadsheet
    datasets_dir = Path("datasets")
    spreadsheet_path = datasets_dir / "neutroon_data.xlsx"

    if not spreadsheet_path.exists():
        raise FileNotFoundError(f"Spreadsheet not found at {spreadsheet_path}")

    # Load dataset
    dataset = pd.read_excel(spreadsheet_path)

    # Drop columns with at least 80% null values
    threshold = int(0.2 * len(dataset))  # At least 20% non-null values
    dataset = dataset.dropna(axis=1, thresh=threshold)

    # Prepare context variables
    context_variables = {
        "dataset": dataset
    }

    # Define task
    task = Task(
        description="Give me a financial summary for January 2024?",
        instructions="Provide a summary of the financial data for the specified date.",
        requires_formatted_output=True
    )

    # Test Case 1: Streaming with response format
    print("\n=== Test Case 1: Streaming with response format ===")
    await run_test_case(agent, task, context_variables, stream=True, response_format=FinancialDataAgentResponse)

    # Test Case 2: Streaming without response format
    print("\n=== Test Case 2: Streaming without response format ===")
    await run_test_case(agent, task, context_variables, stream=True, response_format=None)

    # Test Case 3: No streaming with response format
    print("\n=== Test Case 3: No streaming with response format ===")
    await run_test_case(agent, task, context_variables, stream=False, response_format=FinancialDataAgentResponse)

    # Test Case 4: No streaming without response format
    print("\n=== Test Case 4: No streaming without response format ===")
    await run_test_case(agent, task, context_variables, stream=False, response_format=None)

async def run_test_case(
    agent: AgentProtocol,
    task: Task,
    context_variables: Dict[str, Any],
    stream: bool,
    response_format: Type[BaseResponseModel] | None
) -> None:
    """Run a single test case."""
    # For streaming responses, show chunks in the same line
    if stream:
        print("Response: ", end="", flush=True)
        async for result in agent.execute(task, context_variables, stream=stream, response_format=response_format):
            if isinstance(result, dict):
                if result.get("message"):
                    print(result["message"], end="", flush=True)
                elif result.get("status") == "completed":
                    print(f"\nExecution time: {result.get('execution_time', 0):.2f}s")
        print()  # New line at the end
    else:
        # For non-streaming, show each result on a new line
        async for result in agent.execute(task, context_variables, stream=stream, response_format=response_format):
            print(f"Chunk: {result}")

if __name__ == "__main__":
    asyncio.run(run_demo())

