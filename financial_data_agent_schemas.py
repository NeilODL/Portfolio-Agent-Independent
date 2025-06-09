from typing import Dict, Any
from enum import Enum
from pydantic import Field
from app.core.schemas.base import BaseResponseModel

class QueryType(str, Enum):
    METRIC_LOOKUP = "metric_lookup"
    COMPARISON = "comparison"
    TREND_ANALYSIS = "trend_analysis"
    SUMMARY = "summary"
    # Add more types if needed

class FinancialDataAgentResponse(BaseResponseModel):
    """
    Flexible schema with guided sub-schemas based on 'query_type'.

    Required:
    - query_type: "metric_lookup", "comparison", or "trend_analysis"
    - result: Object following the structure defined by query_type
    - analysis: Detailed explanation of findings

    Examples:
    metric_lookup:
    {
      "query_type": "metric_lookup",
      "result": {
        "metric": "Payroll",
        "value": 50000,
        "date": "2024-01-01"
      },
      "analysis": "The payroll for January 2024 is 50,000."
    }

    comparison:
    {
      "query_type": "comparison",
      "result": {
        "comparison": {
          "revenue": {"total": 150000, "breakdown": {"Jan": 50000, "Feb": 50000, "Mar": 50000}},
          "costs": {"total": 120000, "breakdown": {"Jan": 40000, "Feb": 40000, "Mar": 40000}}
        },
        "period": "Q1 2024",
        "difference": 30000
      },
      "analysis": "Revenue exceeded costs by 30,000 in Q1 2024."
    }

    trend_analysis:
    {
      "query_type": "trend_analysis",
      "result": {
        "trend": {
          "monthly_revenue": {
             "2024-01-01": 50000,
             "2024-02-01": 55000,
             "2024-03-01": 60000
          }
        },
        "period": "Q1 2024",
        "insights": "Revenue increased each month."
      },
      "analysis": "The trend shows consistent growth in revenue over the first quarter."
    }

    summary:
    {
      "query_type": "summary",
      "result": {
        "key_metrics": {
          "total_revenue": 500000,
          "total_costs": 400000,
          "net_profit": 100000
        },
        "period": "2024-Q1",
        "highlights": [
          "Strong revenue growth of 15%",
          "Cost optimization improved margins",
          "Healthy cash position"
        ],
        "areas_of_concern": [
          "Rising operational costs",
          "Seasonal revenue fluctuations"
        ]
      },
      "analysis": "The financial performance in Q1 2024 shows robust growth with revenue reaching $500,000. While profitability remains strong, attention should be paid to rising operational costs."
    }
    """

    query_type: QueryType = Field(..., description="Type of the financial query")
    result: Dict[str, Any] = Field(..., description="Result object based on query_type")
    analysis: str = Field(..., description="Detailed explanation of the findings")
