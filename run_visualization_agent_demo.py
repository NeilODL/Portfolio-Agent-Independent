"""
Visualization Agent Demo Module

This module demonstrates the VisualizationAgent's capabilities by generating a chart specification
and plotting it using seaborn for a more aesthetically pleasing visualization.

Run with: python -m demo.run_visualization_agent_demo
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Type
import json

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from dotenv import load_dotenv
load_dotenv()

from app.agents.schemas.visualization_agent_schemas import VisualizationAgentResponse
from app.core.agents.constants import AgentType
from app.core.mission.schemas.planner import Task
from app.core.registry.agent_initializer import initialize_agents
from app.core.schemas.base import BaseResponseModel
from app.core.agents.types.agent_protocols import AgentProtocol

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def get_visualization_agent() -> AgentProtocol:
    """Get the visualization agent with managed lifecycle."""
    components = await initialize_agents()
    agent_registry = components[2]
    agent = agent_registry.get_agent(AgentType.VISUALIZATION.value)
    if not agent:
        raise RuntimeError("VisualizationAgent not found in registry")
    return agent

async def run_demo() -> None:
    """Run the visualization agent demo."""
    agent = await get_visualization_agent()

    # Load the spreadsheet
    datasets_dir = Path("datasets")
    spreadsheet_path = datasets_dir / "neutroon_data.xlsx"

    if not spreadsheet_path.exists():
        raise FileNotFoundError(f"Spreadsheet not found at {spreadsheet_path}")

    dataset = pd.read_excel(spreadsheet_path)
    # Drop columns with at least 80% null values
    threshold = int(0.2 * len(dataset))
    dataset = dataset.dropna(axis=1, thresh=threshold)

    context_variables = {
        "dataset": dataset
    }

    # Define a task that asks for a chart
    task = Task(
        description="Please create line graph of cash available in Q1 2024",
        instructions="Return a chart specification as per the schema.",
        requires_formatted_output=True
    )

    response_format = VisualizationAgentResponse

    results = []
    async for result in agent.execute(
        task=task,
        context_variables=context_variables,
        stream=False,
        response_format=response_format
    ):
        logger.debug(f"Received chunk: {result}")
        results.append(result)

    if not results:
        print("No results received from agent execution")
        return

    final_result = None
    # Try to find a completed response
    for r in results:
        # If the agent returns directly as a model instance
        if isinstance(r, VisualizationAgentResponse):
            final_result = r.dict()
            break
        # If it returns as a dict with 'status' and 'message' or 'result'
        if isinstance(r, dict):
            if r.get("status") == "completed" and r.get("message"):
                try:
                    final_result = json.loads(r["message"])
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
            elif r.get("status") == "completed" and r.get("result"):
                final_result = r["result"]
                break

    if final_result is None:
        print("No valid visualization specification returned from the agent.")
        return

    # Validate the required fields
    required_fields = ["chart_type", "title", "x_label", "y_label", "data_points"]
    if not all(field in final_result for field in required_fields):
        print(f"Invalid visualization specification. Missing required fields. Got: {final_result.keys()}")
        return

    chart_type = final_result["chart_type"]
    title = final_result["title"]
    x_label = final_result["x_label"]
    y_label = final_result["y_label"]
    data_points = final_result["data_points"]

    # Optional fields
    notes = final_result.get("notes")
    data_source = final_result.get("data_source")

    # Convert data_points into a DataFrame for plotting
    df = pd.DataFrame(data_points)

    # Use seaborn for a nicer style
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(8, 5))
    if chart_type == "line":
        sns.lineplot(x="x", y="y", data=df, marker='o')
    elif chart_type == "bar":
        sns.barplot(x="x", y="y", data=df)
    elif chart_type == "scatter":
        sns.scatterplot(x="x", y="y", data=df)

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # If we have notes or data_source, we could print them out or log them
    if notes:
        logger.info(f"Notes: {notes}")
    if data_source:
        logger.info(f"Data Source: {data_source}")

    plt.tight_layout()

    # Show the plot
    plt.show()

if __name__ == "__main__":
    asyncio.run(run_demo())
