"""Run spreadsheet demo to test agent functionality."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Type, AsyncGenerator
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

from app.agents.external.spreadsheet_agent import SpreadsheetAgent
from app.core.agents.constants import AgentType, ContentKey, StatusMessage
from app.core.mission.schemas.planner import Task
from app.core.registry.agent_initializer import initialize_agents
from app.core.schemas.base import BaseResponseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("app.core.models.llm").setLevel(logging.INFO)
logging.getLogger("app.agents").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

def format_response(result: dict[str, Any]) -> str:
    """Format the response for display."""
    logger.debug(f"Raw result: {result}")
    output = []

    if "message" in result:
        try:
            message = result["message"]
            if isinstance(message, dict):
                output.append(f"Message: {json.dumps(message, indent=2)}")
            else:
                output.append(f"Message: {message}")
        except Exception as e:
            logger.error(f"Error formatting message: {e}")
            output.append(f"Message: {result['message']} (Error: {str(e)})")

    if "status" in result:
        output.append(f"Status: {result['status']}")

    return "\n".join(output)

@asynccontextmanager
async def get_spreadsheet_agent() -> AsyncGenerator[SpreadsheetAgent, None]:
    """Get a spreadsheet agent with managed lifecycle."""
    components = await initialize_agents()
    agent_registry = components[2]
    agent = agent_registry.get_agent(AgentType.SPREADSHEET.value)
    if not agent:
        raise RuntimeError("Spreadsheet Agent not found in registry")
    try:
        yield agent
    finally:
        await agent.close()

async def run_spreadsheet_demo(stream: bool = False) -> None:
    """Run the spreadsheet agent demo."""
    try:
        # Initialize agent directly since we don't need LLM
        agent = SpreadsheetAgent(model="no-llm")
        
        # Get spreadsheet path
        datasets_dir = Path("datasets")  # Relative to backend directory
        spreadsheet_path = datasets_dir / "neutroon_data.xlsx"
        
        logger.info(f"Looking for spreadsheet at: {spreadsheet_path}")
        
        if not spreadsheet_path.exists():
            raise FileNotFoundError(
                f"Spreadsheet not found at {spreadsheet_path}. "
                "Please ensure neutroon_data.xlsx exists in the backend/datasets directory."
            )
        
        # Create task
        task = Task(
            description="Process spreadsheet",
            instructions="Extract structure and metadata from spreadsheet"
        )
        
        context_variables = {
            "spreadsheet_path": str(spreadsheet_path)
        }
        
        logger.info(f"\nProcessing spreadsheet: {spreadsheet_path}")
        async for result in agent.execute(task, context_variables, stream=stream):
            formatted_output = format_response(result)
            logger.info(formatted_output)
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise
    finally:
        if agent and hasattr(agent, 'close'):
            await agent.close()

if __name__ == "__main__":
    asyncio.run(run_spreadsheet_demo())