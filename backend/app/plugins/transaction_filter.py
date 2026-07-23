import logging
from app.plugins.base import BasePlugin
from app.models.context import ExecutionContext, LogLevel

logger = logging.getLogger(__name__)


class TransactionFilterPlugin(BasePlugin):
    NAME = "TransactionFilter"
    VERSION = "1.0"
    DESCRIPTION = "Keeps only rows matching allowed transaction types."

    def execute(self, context: ExecutionContext) -> None:
        df = context.current_data
        if df is None or df.empty:
            return

        cfg = context.rules.get(self.NAME, {})
        allowed = cfg.get("allowed", [])
        if not allowed:
            return

        col = "Transaction Type"
        if col not in df.columns:
            context.add_warning(LogLevel.WARNING, f"Column '{col}' not found – skipping TransactionFilter.")
            return

        before = len(df)
        df = df[df[col].astype(str).isin(allowed)]
        removed = before - len(df)
        context.current_data = df

        if removed:
            context.statistics.rows_removed += removed
            context.add_warning(LogLevel.INFO, f"TransactionFilter removed {removed} rows.")
            logger.info("TransactionFilter removed %d rows.", removed)
