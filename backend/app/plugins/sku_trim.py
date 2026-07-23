import logging
from app.plugins.base import BasePlugin
from app.models.context import ExecutionContext, LogLevel

logger = logging.getLogger(__name__)


class SkuTrimPlugin(BasePlugin):
    NAME = "SkuTrim"
    VERSION = "1.0"
    DESCRIPTION = "Trims the Sku column to a configurable length."

    def execute(self, context: ExecutionContext) -> None:
        df = context.current_data
        if df is None or df.empty:
            return

        cfg = context.rules.get(self.NAME, {})
        trim_length = cfg.get("length", 6)

        col = "Sku"
        if col not in df.columns:
            context.add_warning(LogLevel.WARNING, f"Column '{col}' not found – skipping SkuTrim.")
            return

        df[col] = df[col].astype(str).str[:trim_length]
        context.current_data = df
        context.add_warning(LogLevel.INFO, f"SkuTrim: trimmed Sku to {trim_length} characters.")
        logger.info("SkuTrim: trimmed to %d chars.", trim_length)
