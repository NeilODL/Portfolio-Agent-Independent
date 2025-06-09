# app/agents/spreadsheet_agent.py

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, ClassVar, AsyncGenerator
import pandas as pd
import yaml

from app.agents.base.agent import Agent
from app.core.agents.constants import AgentType, AgentDescription, AgentIcon, StatusMessage
from app.core.mission.schemas.planner import Task
from app.core.schemas.base import BaseResponseModel
from app.agents.schemas.spreadsheet_agent_schemas import SpreadsheetProcessingResponse, SheetInfo
from app.agents.prompts.spreadsheet_agent_prompts import SYSTEM_PROMPT, PROCESSING_PROMPT

logger = logging.getLogger(__name__)

class SpreadsheetAgent(Agent):
    """Agent for processing spreadsheet data."""

    agent_type: ClassVar[AgentType] = AgentType.SPREADSHEET
    description: ClassVar[AgentDescription] = AgentDescription.SPREADSHEET
    icon: ClassVar[AgentIcon] = AgentIcon.SPREADSHEET
    system_prompt: ClassVar[str] = SYSTEM_PROMPT
    stream: ClassVar[bool] = False
    default_response_format: ClassVar[type[BaseResponseModel] | None] = SpreadsheetProcessingResponse

    def __init__(self, model: str = "no-llm", tools: List[str] = None, dependencies: List[str] = None):
        super().__init__(model=model, tools=tools or [], dependencies=dependencies or [])
        self.logger = logging.getLogger(__name__)

    def generate_prompt(self, task_input: Dict[str, Any]) -> str:
        """Generate prompt for the spreadsheet processing task."""
        spreadsheet_path = task_input.get('spreadsheet_path', '')
        return PROCESSING_PROMPT.format(spreadsheet_path=spreadsheet_path)
    
    async def execute(self, task: Task, context_variables: Dict[str, Any], stream: bool = False) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the spreadsheet processing task."""
        try:
            spreadsheet_path = context_variables.get('spreadsheet_path')
            if not spreadsheet_path:
                raise ValueError("Spreadsheet path not provided")
            
            if stream:
                yield {
                    "status": StatusMessage.PROCESSING.value,
                    "message": "Loading spreadsheet..."
                }
            
            # Process the spreadsheet
            result = await self.process_spreadsheet(spreadsheet_path)
            
            yield {
                "status": StatusMessage.COMPLETED.value,
                "message": result.model_dump()
            }
            
        except Exception as e:
            self.logger.error(f"Error in SpreadsheetAgent: {str(e)}")
            yield {
                "status": StatusMessage.ERROR.value,
                "message": str(e)
            }
    
    async def process_spreadsheet(self, spreadsheet_path: str) -> SpreadsheetProcessingResponse:
        """Process a spreadsheet file and extract metadata."""
        try:
            # Validate file exists
            path = Path(spreadsheet_path)
            if not path.exists():
                raise FileNotFoundError(f"Spreadsheet not found at {spreadsheet_path}")
            
            # Load all sheets
            sheets = pd.read_excel(spreadsheet_path, sheet_name=None)
            
            # Extract metadata
            sheets_metadata = {}
            global_date_formats = set()
            metrics_mapping = {}
            for sheet_name, df in sheets.items():
                self.logger.info(f"Processing sheet: {sheet_name}")
                
                # Clean column names
                df.columns = df.columns.astype(str).str.strip()
                
                # Filter out unnamed columns
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
                # Extract sheet metadata
                sheet_info, metrics_in_sheet = await self._extract_sheet_metadata(df, sheet_name)
                sheets_metadata[sheet_name] = sheet_info
                
                # Collect date formats from all sheets
                global_date_formats.update(sheet_info.date_formats)
                
                # Collect metrics mapping
                if metrics_in_sheet:
                    metrics_mapping[sheet_name] = metrics_in_sheet
                
            # Generate global settings
            global_settings = {
                'date_formats': list(global_date_formats)
            }
            
            # Build config data
            config_data = {
                'version': '1.0',
                'global': global_settings,
                'sheets': {
                    sheet_name: sheet_info.model_dump(exclude_unset=True) for sheet_name, sheet_info in sheets_metadata.items()
                },
                'metrics_mapping': metrics_mapping  # Added metrics mapping
            }
            
            # Save the metadata to a config file
            config_path = path.with_suffix('.yaml')
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f, sort_keys=False)
            
            self.logger.info(f"Config file saved at: {config_path}")
            
            return SpreadsheetProcessingResponse(
                sheets_metadata=sheets_metadata,
                processed_data={},  # Empty for now; can be filled if needed
                file_path=str(path),
                config_path=str(config_path)
            )
        
        except Exception as e:
            self.logger.error(f"Error in SpreadsheetAgent: {str(e)}")
            raise
    
    async def _extract_sheet_metadata(self, df: pd.DataFrame, sheet_name: str) -> Tuple[SheetInfo, Dict[str, str]]:
        """Extract metadata from a single sheet."""
        # Columns
        columns = df.columns.tolist()
        
        # Date columns and formats
        date_columns, date_formats = self._detect_date_columns(df)
        
        # Update data types based on date detection
        data_types = self._infer_data_types(df, date_columns)
        
        # Null counts
        null_counts = df.isnull().sum().to_dict()
        null_counts = {str(k): int(v) for k, v in null_counts.items()}
        
        # Detect if the sheet has headers
        has_headers = True  # Assuming headers are present
        
        # Identify possible identifier and description columns
        identifier_columns = self._identify_identifier_columns(df)
        description_columns = self._identify_description_columns(df, identifier_columns)
        
        # Identify possible metric columns
        metric_columns = self._identify_metric_columns(df, identifier_columns + description_columns + date_columns)
        
        # Extract metrics mapping
        metrics_mapping = self._extract_metrics(df, identifier_columns, description_columns)
        
        # Create SheetInfo instance
        sheet_info = SheetInfo(
            name=sheet_name,
            columns=columns,
            row_count=int(len(df)),
            column_count=int(len(columns)),
            data_types=data_types,
            has_headers=has_headers,
            date_columns=date_columns,
            null_counts=null_counts,
            date_formats=date_formats,
            identifier_columns=identifier_columns,
            description_columns=description_columns,
            metric_columns=metric_columns
        )
        
        return sheet_info, metrics_mapping
    
    def _detect_date_columns(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Identify columns that contain date values and collect date formats."""
        date_columns = []
        date_formats = set()
        known_formats = [
            "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%B %Y", "%b-%y",
            "%m/%Y", "%Y%m", "%d-%m-%Y", "%m-%d-%Y", "%b-%y", "%b-%Y",
            "%Y-%b", "%b/%y", "%b/%Y"
        ]

        for col in df.columns:
            # Try to parse the column name as a date
            for fmt in known_formats:
                try:
                    pd.to_datetime(col, format=fmt, errors='raise')
                    date_columns.append(col)
                    date_formats.add(fmt)
                    self.logger.debug(f"Column '{col}' matched date format '{fmt}'")
                    break
                except (ValueError, TypeError):
                    continue

            if col.lower() in ['date', 'year', 'month']:
                date_columns.append(col)
                self.logger.debug(f"Column '{col}' identified as a date-related column based on name")
                continue
            else:
                # Try to parse strings in the column as dates
                sample_data = df[col].dropna().astype(str).head(10)
                for fmt in known_formats:
                    try:
                        pd.to_datetime(sample_data, format=fmt, errors='raise')
                        date_columns.append(col)
                        date_formats.add(fmt)
                        self.logger.debug(f"Column '{col}' data matched date format '{fmt}'")
                        break
                    except (ValueError, TypeError):
                        continue

        # Remove duplicates
        date_columns = list(set(date_columns))
        return date_columns, list(date_formats)
    
    def _infer_data_types(self, df: pd.DataFrame, date_columns: List[str]) -> Dict[str, str]:
        """Infer data types for each column, converting date columns."""
        inferred_types = {}
        for col in df.columns:
            if col in date_columns:
                # Attempt to convert column to datetime
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                    inferred_types[col] = "datetime"
                    self.logger.debug(f"Column '{col}' converted to datetime")
                except Exception as e:
                    self.logger.warning(f"Failed to convert column '{col}' to datetime: {e}")
                    inferred_types[col] = "string"
            else:
                series = df[col]
                if pd.api.types.is_datetime64_any_dtype(series):
                    inferred_types[col] = "datetime"
                elif pd.api.types.is_integer_dtype(series):
                    inferred_types[col] = "integer"
                elif pd.api.types.is_float_dtype(series):
                    inferred_types[col] = "float"
                elif pd.api.types.is_bool_dtype(series):
                    inferred_types[col] = "boolean"
                else:
                    inferred_types[col] = "string"
        return inferred_types
    
    def _identify_identifier_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify possible identifier columns based on data patterns."""
        identifier_columns = []
        total_rows = len(df)
        for col in df.columns:
            unique_values = df[col].dropna().unique()
            uniqueness_ratio = len(unique_values) / total_rows if total_rows > 0 else 0
            non_null_ratio = df[col].notnull().mean()
            # Include columns regardless of data type
            if non_null_ratio > 0.4 and uniqueness_ratio < 0.9:
                identifier_columns.append(col)
                self.logger.debug(f"Column '{col}' identified as an identifier column (Uniqueness: {uniqueness_ratio:.2f})")
        return identifier_columns
    
    def _identify_description_columns(self, df: pd.DataFrame, exclude_columns: List[str]) -> List[str]:
        """Identify possible description columns."""
        description_columns = []
        for col in df.columns:
            if col not in exclude_columns:
                non_null_ratio = df[col].notnull().mean()
                if non_null_ratio > 0.4:
                    description_columns.append(col)
                    self.logger.debug(f"Column '{col}' identified as a description column")
        return description_columns
    
    def _identify_metric_columns(self, df: pd.DataFrame, exclude_columns: List[str]) -> List[str]:
        """Identify possible metric columns based on data types."""
        metric_columns = []
        for col in df.columns:
            if col not in exclude_columns and pd.api.types.is_numeric_dtype(df[col]):
                metric_columns.append(col)
                self.logger.debug(f"Column '{col}' identified as a metric column")
        return metric_columns
    
    def _extract_metrics(self, df: pd.DataFrame, identifier_columns: List[str], description_columns: List[str]) -> Dict[str, str]:
        """
        Extract metrics mapping from the sheet dynamically.
        
        Returns:
            Dict[str, str]: Mapping of metric identifiers to descriptions.
        """
        metrics = {}
        columns_to_try = []
        # First, try the first column as identifier and second as description
        if df.columns.size >= 2:
            columns_to_try.append((df.columns[0], df.columns[1]))
            self.logger.debug(f"Trying to map metrics using columns: '{df.columns[0]}' (ID) and '{df.columns[1]}' (Description)")
        # Then, try identified identifier and description columns
        for id_col in identifier_columns:
            for desc_col in description_columns:
                columns_to_try.append((id_col, desc_col))
                self.logger.debug(f"Trying to map metrics using columns: '{id_col}' (ID) and '{desc_col}' (Description)")

        for id_col, desc_col in columns_to_try:
            id_series = df[id_col].astype(str)
            desc_series = df[desc_col].astype(str)
            combined_non_null = id_series.notnull() & desc_series.notnull()
            if combined_non_null.sum() == 0:
                self.logger.debug(f"No overlapping data found between '{id_col}' and '{desc_col}'")
                continue  # No overlapping data
            # Create mapping
            for identifier, description in zip(id_series[combined_non_null], desc_series[combined_non_null]):
                identifier = str(identifier).strip()
                description = str(description).strip()
                if identifier and description and identifier.lower() != 'nan' and description.lower() != 'nan':
                    metrics[identifier] = description
            if metrics:
                self.logger.debug(f"Metrics mapping found using columns '{id_col}' and '{desc_col}': {metrics}")
                return metrics  # Return on first successful mapping
        return metrics
