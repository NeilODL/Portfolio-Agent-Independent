from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import Field
from app.core.schemas.base import BaseResponseModel

class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"

class VisualizationAgentResponse(BaseResponseModel):
    """
    Schema for the visualization agent response.

    Required fields:
    - chart_type: One of 'bar', 'line', 'scatter'
    - title: Title of the chart
    - x_label: Label for the x-axis
    - y_label: Label for the y-axis
    - data_points: A list of {"x": <value>, "y": <value>}
    
    Optional fields:
    - notes: Additional context or explanation about the data or chart
    - data_source: Information about where the data came from (e.g., "Data after cleaning null values")

    Example:
    {
      "chart_type": "line",
      "title": "Sales Over Q1 2024",
      "x_label": "Month",
      "y_label": "Sales (USD)",
      "data_points": [
        {"x": "January", "y": 50000},
        {"x": "February", "y": 55000},
        {"x": "March", "y": 60000}
      ],
      "notes": "Data after cleaning null values",
      "data_source": "January, February, March 2024 from revenue column"
    }
    """
    chart_type: ChartType = Field(..., description="Type of chart to create")
    title: str = Field(..., description="Title of the chart")
    x_label: str = Field(..., description="Label for the X axis")
    y_label: str = Field(..., description="Label for the Y axis")
    data_points: List[Dict[str, Any]] = Field(..., description="List of data points, each with 'x' and 'y' fields")
    notes: Optional[str] = Field(None, description="Additional notes or context about the chart")
    data_source: Optional[str] = Field(None, description="Information about the data source or selection")
