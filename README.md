# Portfolio Agent System

A sophisticated multi-agent system for financial data analysis, visualization, and spreadsheet processing. This system combines multiple specialized agents to provide comprehensive financial analysis capabilities.

## Overview

The Portfolio Agent System consists of three main components:

1. **Spreadsheet Agent**: Processes and analyzes spreadsheet data, extracting metadata and preparing it for analysis
2. **Financial Data Agent**: Performs financial analysis and provides structured insights
3. **Visualization Agent**: Creates data visualizations based on financial data

## Features

### Spreadsheet Agent
- Loads and processes Excel spreadsheets
- Extracts metadata including:
  - Sheet information
  - Column names and types
  - Date column identification
  - Data quality metrics (null counts)
- Identifies key columns:
  - Identifier columns
  - Description columns
  - Metric columns
- Generates YAML configuration files for data structure

### Financial Data Agent
- Performs various types of financial analysis:
  - Metric lookups
  - Period comparisons
  - Trend analysis
  - Financial summaries
- Provides structured responses with:
  - Query type identification
  - Detailed analysis
  - Clear insights and recommendations

### Visualization Agent
- Creates data visualizations with:
  - Bar charts
  - Line graphs
  - Scatter plots
- Features:
  - Natural language labels
  - Aesthetic styling
  - Contextual notes
  - Data source attribution

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Spreadsheet Agent Demo
```bash
python run_spreadsheet_agent_demo.py
```

### Running the Financial Data Agent Demo
```bash
python run_financial_data_agent_demo.py
```

### Running the Visualization Agent Demo
```bash
python run_visualization_agent_demo.py
```

## Data Format

The system expects Excel spreadsheets with the following characteristics:
- Clear column headers
- Consistent data types
- Date columns in standard formats
- Financial metrics in numeric format

## Response Formats

### Financial Data Agent Responses
```json
{
  "query_type": "metric_lookup|comparison|trend_analysis|summary",
  "result": {
    // Structure varies based on query_type
  },
  "analysis": "Detailed explanation of findings"
}
```

### Visualization Agent Responses
```json
{
  "chart_type": "bar|line|scatter",
  "title": "Chart Title",
  "x_label": "X Axis Label",
  "y_label": "Y Axis Label",
  "data_points": [
    {"x": value, "y": value}
  ],
  "notes": "Optional context",
  "data_source": "Optional source information"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Contact

[Add your contact information here] 