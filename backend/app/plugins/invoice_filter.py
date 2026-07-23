import logging
from app.plugins.base import BasePlugin
from app.models.context import ExecutionContext, LogLevel

logger = logging.getLogger(__name__)


class InvoiceFilterPlugin(BasePlugin):
    NAME = "InvoiceFilter"
    VERSION = "1.1"
    DESCRIPTION = "Keeps only rows whose Invoice Number starts with allowed prefixes and optionally strips them."

    def execute(self, context: ExecutionContext) -> None:
        df = context.current_data
        if df is None or df.empty:
            return

        cfg = context.rules.get(self.NAME, {})
        prefixes = cfg.get("prefixes", [])
        strip_prefix = cfg.get("strip_prefix", True)
        
        if not prefixes:
            return

        col = "Invoice Number"
        if col not in df.columns:
            context.add_warning(LogLevel.WARNING, f"Column '{col}' not found – skipping InvoiceFilter.")
            return

        before = len(df)
        
        # Helper to check if string starts with any prefix
        def match_and_strip(val):
            val_str = str(val)
            for p in prefixes:
                if val_str.startswith(p):
                    if strip_prefix:
                        # Strip the prefix, and also strip any leading hyphens
                        return val_str[len(p):].lstrip('-')
                    return val_str
            return None # None means it doesn't match any prefix

        # Apply match and strip
        matched_invoices = df[col].apply(match_and_strip)
        
        # Keep only rows that matched a prefix (where result is not None)
        df = df[matched_invoices.notnull()]
        
        # Update the column with the stripped values
        df.loc[:, col] = matched_invoices[matched_invoices.notnull()]
        
        removed = before - len(df)
        context.current_data = df

        if removed:
            context.statistics.rows_removed += removed
            context.add_warning(LogLevel.INFO, f"InvoiceFilter removed {removed} rows and stripped prefixes.")
            logger.info("InvoiceFilter removed %d rows.", removed)
