import pandas as pd
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TransformationWarning(BaseModel):
    level: LogLevel
    message: str
    row_index: Optional[int] = None
    column: Optional[str] = None


class TransformationStats(BaseModel):
    rows_read: int = 0
    rows_processed: int = 0
    rows_removed: int = 0
    rows_failed: int = 0
    duplicate_invoices: int = 0
    missing_gst: int = 0
    missing_account_code: int = 0
    execution_time_ms: float = 0.0


class ExecutionContext:
    """Shared state object passed through every plugin in the pipeline."""

    def __init__(
        self,
        mapping: Dict[str, Any],
        rules: Dict[str, Any],
        lookups: Dict[str, pd.DataFrame],
    ):
        self.mapping = mapping
        self.rules = rules
        self.lookups = lookups
        self.current_data: Optional[pd.DataFrame] = None
        self.statistics = TransformationStats()
        self.warnings: List[TransformationWarning] = []

    def add_warning(
        self,
        level: LogLevel,
        message: str,
        row_index: Optional[int] = None,
        column: Optional[str] = None,
    ):
        self.warnings.append(
            TransformationWarning(
                level=level, message=message, row_index=row_index, column=column
            )
        )
