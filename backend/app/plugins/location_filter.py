import logging
from app.plugins.base import BasePlugin
from app.models.context import ExecutionContext, LogLevel

logger = logging.getLogger(__name__)


class LocationFilterPlugin(BasePlugin):
    NAME = "LocationFilter"
    VERSION = "1.1"
    DESCRIPTION = "Keeps only rows where the configured location column matches allowed values."

    def execute(self, context: ExecutionContext) -> None:
        df = context.current_data
        if df is None or df.empty:
            return

        cfg = context.rules.get(self.NAME, {})
        allowed_states = cfg.get("allowed_states", [])
        filter_column = cfg.get("filter_column", "Bill From State")
        if not allowed_states:
            return

        if filter_column not in df.columns:
            context.add_warning(LogLevel.WARNING, f"Column '{filter_column}' not found – skipping LocationFilter.")
            return

        before = len(df)
        df = df[df[filter_column].astype(str).str.upper().isin([s.upper() for s in allowed_states])]
        removed = before - len(df)
        context.current_data = df

        if removed:
            context.statistics.rows_removed += removed
            context.add_warning(LogLevel.INFO, f"LocationFilter removed {removed} rows (column: {filter_column}).")
            logger.info("LocationFilter removed %d rows on '%s'.", removed, filter_column)
