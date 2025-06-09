from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class SheetInfo(BaseModel):
    name: str
    columns: List[str]
    row_count: int
    column_count: int
    data_types: Dict[str, str] = Field(description="Column name to data type mapping")
    has_headers: bool
    date_columns: List[str] = Field(description="Columns containing date values")
    null_counts: Dict[str, Union[int, str]] = Field(description="Number of null values per column")
    date_formats: List[str] = Field(default_factory=list, description="List of date formats detected in the sheet")


    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            int: str,
            float: str
        }

class SpreadsheetProcessingResponse(BaseModel):
    sheets_metadata: Dict[str, SheetInfo]
    processed_data: Dict[str, Any]
    file_path: str